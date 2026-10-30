"""Ghép nội suy ngược vào Report hiện có; giữ nguyên lựa chọn mỗi lượt chạy."""
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction
import math

import numpy as np

from .common import Report, numbers
from .inverse_model import (InverseMap, rational, decimal, evaluate, difference_table,
                            expand_newton, certify, derivative)


class InverseFailure(ValueError):
    """API cũ vẫn báo ValueError; GUI có thể giữ cả lời giải đã tính."""
    def __init__(self,report):
        self.report=report
        super().__init__(report.presentation['inverse_solution']['failure']['message'])


class _Invalid(ValueError):
    def __init__(self,status,message):self.status=status;super().__init__(message)


def _fail(status,message):raise _Invalid(status,message)


def _check(data,title,state,observed=None,expected=None,explanation=''):
    """Ghi căn cứ tiền kiểm để bộ trình bày không phải kiểm tra lại bài toán."""
    data.setdefault('validation_checks',[]).append({
        'title':title,'state':state,'observed_value':observed,
        'expected_condition':expected,'explanation':explanation})


def _nonnegative(value,label):
    try:result=rational(value)
    except (ValueError,TypeError,OverflowError):_fail('invalid_input',f'{label} phải hữu hạn và không âm.')
    if result<0:_fail('invalid_input',f'{label} phải không âm; đã nhận {value!r}.')
    return result


def _near_levels(data,rows,atol,rtol):
    """Chỉ cảnh báo nhạy số, không biến gần bằng thành mốc trùng."""
    a=_nonnegative(atol,'Ngưỡng tung độ gần trùng tuyệt đối')
    r=_nonnegative(rtol,'Ngưỡng tung độ gần trùng tương đối')
    ordered=sorted(rows,key=lambda row:row['y']);near=[]
    for left,right in zip(ordered,ordered[1:]):
        gap=right['y']-left['y'];threshold=a+r*max(abs(left['y']),abs(right['y']))
        if gap and gap<=threshold:
            near.append({'left':left['index'],'right':right['index'],'gap':gap,'threshold':threshold})
            data['warnings'].append(
                f'Tung độ ở hàng {left["index"]} và {right["index"]} gần nhau: |Δy|={float(gap):.12g} '
                f'≤ {float(threshold):.12g} (atol={float(a):.12g}, rtol={float(r):.12g}). '
                'Giữ nguyên hai mốc; bài toán có thể nhạy với sai số tung độ.')
    data['near_y_checks']=near
    _check(data,'Độ tách biệt của tung độ','warning' if near else 'passed',near,
           {'atol':a,'rtol':r},'Ngưỡng chỉ phát cảnh báo; không gộp hoặc thay đổi mốc.')


def _integer(value,label,minimum=1):
    if isinstance(value,(bool,np.bool_)) or not isinstance(value,(int,np.integer)) or value<minimum:
        _fail('invalid_input',f'{label} phải là số nguyên từ {minimum} trở lên; đã nhận {value!r}.')
    return int(value)


def _positive(value,label):
    try:result=rational(value)
    except (ValueError,TypeError,OverflowError):_fail('invalid_input',f'{label} phải dương và hữu hạn; đã nhận {value!r}.')
    if result<=0:_fail('invalid_input',f'{label} phải dương; đã nhận {value!r}.')
    return result


def _indices(value,size,label):
    result=[_integer(v,label,0) for v in value]
    if len(set(result))!=len(result) or any(v>=size for v in result):
        _fail('invalid_selection',f'{label} bị trùng hoặc nằm ngoài chỉ số 0…{size-1}: {result}.')
    return result


def sample_scan(rows,target):
    exact=[row['index'] for row in rows if row['y']==target]
    brackets=[];flats=[];branches=[];start=0;direction=0
    for i in range(len(rows)-1):
        left,right=rows[i],rows[i+1]
        a,b=left['y']-target,right['y']-target
        if (a<0<b) or (b<0<a):brackets.append((left['index'],right['index']))
        if a==b==0:flats.append((left['index'],right['index']))
        sign=(right['y']>left['y'])-(right['y']<left['y'])
        if not sign:
            if start<i:branches.append([r['index'] for r in rows[start:i+1]])
            start=i+1;direction=0
        elif not direction:direction=sign
        elif sign!=direction:
            branches.append([r['index'] for r in rows[start:i+1]]);start=i;direction=sign
    if start<len(rows)-1:branches.append([r['index'] for r in rows[start:]])
    return {'sample_roots':exact,'brackets':brackets,'flat_intervals':flats,'branches':branches}


def _prepare(data,x,y,target,selected_indices,branch_indices,count,degree):
    data['phase']='Kiểm tra và ghép cặp dữ liệu'
    try:xx=np.asarray(x,dtype=float);yy=np.asarray(y,dtype=float)
    except (TypeError,ValueError) as exc:_fail('invalid_input',f'Chưa đọc được hai dãy số thực: {exc}')
    if xx.ndim!=1 or yy.ndim!=1:_fail('invalid_input','Hai dãy x,y phải là danh sách một chiều.')
    if len(xx)!=len(yy):_fail('invalid_input',f'Có {len(xx)} hoành độ nhưng {len(yy)} tung độ; chưa ghép được các cặp.')
    if len(xx)<2:_fail('insufficient_nodes',f'Nội suy ngược cần ít nhất 2 cặp; hiện có {len(xx)}.')
    for label,values in (('x',xx),('y',yy)):
        for i,value in enumerate(values):
            if not np.isfinite(value):_fail('invalid_input',f'Hàng {i}, cột {label}: {value!r} không hữu hạn; không thay bằng 0.')
    try:level=rational(target)
    except (ValueError,TypeError,OverflowError):_fail('invalid_input',f'Mức cần tìm không hữu hạn: {target!r}.')
    _check(data,'Ghép cặp và giá trị hữu hạn','passed',len(xx),'Hai dãy cùng độ dài, có ít nhất 2 cặp; mọi số hữu hạn.')
    # Giữ chữ số thập phân/Fraction gốc. Kiểm tra float ở trên chỉ phát
    # hiện đầu vào không hữu hạn, không dùng nó để dựng lại dữ liệu.
    rows=[{'index':i,'x':rational(a),'y':rational(b)} for i,(a,b) in enumerate(zip(x,y))]
    data['original_rows']=deepcopy(rows)
    rows=sorted(rows,key=lambda row:row['x']);data['sorted_rows']=rows
    data['sort_order']=[row['index'] for row in rows]
    for left,right in zip(rows,rows[1:]):
        if left['x']==right['x']:
            kind='cùng cặp dữ liệu' if left['y']==right['y'] else 'tung độ khác nhau'
            _fail('duplicate_abscissa',f'Hàng {left["index"]} và {right["index"]} có cùng x={float(left["x"]):.17g}, {kind}. Chính sách giữ cặp: không tự loại hoặc gộp mốc; hãy xử lý bản sao ở dữ liệu nguồn.')
        ulp=max(math.ulp(float(left['x'])),math.ulp(float(right['x'])))
        if right['x']-left['x']<=32*rational(ulp):
            data['warnings'].append(f'Hàng {left["index"]} và {right["index"]}: hiệu x={float(right["x"]-left["x"]):.12g} gần độ phân giải float theo thang x. Không gộp hoặc làm tròn mốc; kết quả có thể nhạy với dữ liệu.')
    _check(data,'Hoành độ phân biệt','passed',data['sort_order'],'Không có hai mốc x trùng nhau.',
           'Sắp theo x tăng và giữ nguyên cặp cùng chỉ số hàng gốc.')
    data['target']=level;data['sample_scan']=sample_scan(rows,level)
    chosen=set(range(len(rows))) if selected_indices is None else set(_indices(selected_indices,len(rows),'Chỉ số mốc đã chọn'))
    used=[row for row in rows if row['index'] in chosen]
    data['used_rows']=used
    if len(used)<2:_fail('insufficient_nodes',f'Tập đã chọn chỉ có {len(used)} mốc; cần ít nhất 2.')
    if count is not None:
        count=_integer(count,'Số mốc')
        if count!=len(used):_fail('selection_required',f'Yêu cầu {count} mốc nhưng tập đưa vào có {len(used)}. Hãy chọn đúng các cặp cần dùng trong bảng hiện có; chương trình không tự lấy những mốc gần mức hơn.')
    degree=len(used)-1 if degree is None else _integer(degree,'Bậc đa thức')
    data['degree']=degree
    if degree+1>len(used):_fail('insufficient_nodes',f'Bậc {degree} cần {degree+1} mốc, tập đã chọn chỉ có {len(used)}.')
    if degree+1!=len(used):_fail('selection_required',f'Bậc {degree} cần đúng {degree+1} mốc; đang chọn {len(used)}. Giữ nguyên lựa chọn và chọn lại tập mốc trước khi chạy.')
    _check(data,'Số mốc và bậc đã chọn','passed',{'nodes':len(used),'degree':degree},'Số mốc = bậc + 1; không tự chọn lại mốc.')
    if branch_indices is not None:
        branch=set(_indices(branch_indices,len(rows),'Chỉ số nhánh'))
        if data['method']=='inverse_function' and not chosen<=branch:_fail('invalid_selection','Có mốc đã chọn nằm ngoài nhánh được chỉ định; không mở rộng nhánh tự động.')
        data['branch_rows']=[row for row in rows if row['index'] in branch]
        positions=[i for i,row in enumerate(rows) if row['index'] in branch]
        if any(b-a!=1 for a,b in zip(positions,positions[1:])):
            _fail('invalid_branch','Nhánh được chỉ định bỏ qua mốc nằm giữa trên bảng đã nhập; không bỏ mốc để che việc đổi chiều.')
        branch_dy=[right['y']-left['y'] for left,right in zip(data['branch_rows'],data['branch_rows'][1:])]
        monotone=bool(branch_dy) and (all(v>0 for v in branch_dy) or all(v<0 for v in branch_dy))
        if data['method'] in ('forward_iteration','backward_iteration') and not monotone:
            data['warnings'].append('Nhánh mục tiêu được chỉ định chưa đơn điệu trên mẫu. Đa thức thuận vẫn được lập từ nguyên tập mốc; cần đối chiếu đúng khoảng và theo dõi hội tụ.')
        _check(data,'Nhánh mục tiêu trên các mốc','passed' if monotone else 'warning',[row['index'] for row in data['branch_rows']],
               'Nhánh mục tiêu là lựa chọn độc lập với tập mốc lập đa thức thuận.',
               'Hàm ngược cần nhánh một-một; lặp thuận được phép giữ nguyên toàn bảng qua nhiều nhánh.')
    else:data['branch_rows']=[row for row in rows if used[0]['x']<=row['x']<=used[-1]['x']]
    data['selection']={'indices':[r['index'] for r in used],'degree':degree,'policy':'provided_stencil'}
    return used,level


def _interval(data,rows,interval,bracket_indices,method):
    if bracket_indices is not None:
        indices=_indices(bracket_indices,len(data['original_rows']),'Chỉ số khoảng')
        if len(indices)!=2:_fail('invalid_selection','Khoảng mốc cần đúng hai chỉ số đầu mút phân biệt.')
        bracket=sorted((data['original_rows'][i] for i in indices),key=lambda row:row['x'])
        interval=tuple(row['x'] for row in bracket)
        data['bracket_rows']=deepcopy(bracket)
        data['interval_source']='Hai mốc đầu mút do người dùng chọn; giữ nguyên tập mốc tính và gốc.'
    if interval is None:
        if method in ('forward_iteration','backward_iteration'):
            scan=sample_scan(rows,data['target'])
            if len(scan['brackets'])==1 and not scan['sample_roots']:
                ids=set(scan['brackets'][0]);bracket=[row for row in rows if row['index'] in ids]
                interval=tuple(row['x'] for row in bracket)
                data['bracket_rows']=deepcopy(bracket)
                data['interval_source']='Khoảng đổi dấu duy nhất trên tập đã nhập, được xác định từ mức cần tìm; không đổi mốc hoặc gốc.'
            elif len(scan['sample_roots'])==1 and not scan['brackets']:
                interval=(rows[0]['x'],rows[-1]['x'])
                data['interval_source']='Miền của tập mốc; đã nhận dạng duy nhất một mốc đạt mức.'
            else:
                _fail('selection_required','Chưa có một khoảng mục tiêu duy nhất. Hãy nhập a,b hoặc chọn hai mốc đầu mút; không lấy hai mốc đầu/cuối chỉ vì đã chọn tiến/lùi.')
        else:
            interval=(rows[0]['x'],rows[-1]['x'])
            data['interval_source']='Miền x của tập mốc đã chọn.'
    elif 'interval_source' not in data:data['interval_source']='Khoảng mục tiêu do người dùng cung cấp, độc lập với gốc và tập mốc tính.'
    try:
        if len(interval)!=2:raise ValueError()
        lo,hi=map(rational,interval)
    except (ValueError,TypeError,OverflowError):_fail('invalid_selection','Khoảng đang xét phải gồm hai số hữu hạn a<b.')
    data['interval']=(lo,hi)
    if not rows[0]['x']<=lo<hi<=rows[-1]['x']:_fail('invalid_selection','Khoảng đang xét phải nằm trong dải mốc đã chọn và có a<b.')
    if method in ('forward_iteration','backward_iteration'):
        data['selection']['policy']='all_imported' if len(rows)==len(data['original_rows']) else 'explicit_subset'
        data['selection']['interval_independent']=True
        _check(data,'Giữ nguyên tập mốc và gốc khai triển','passed',data['selection']['indices'],
               'Tiến lấy gốc đầu tập tính; lùi lấy gốc cuối; tập được chọn chỉ cần có lưới đều.',
               'Khoảng nghiệm ở giữa bảng không làm thiếu mốc; số vòng không làm tăng số mốc cần dùng.')
    _check(data,'Khoảng đang giải','passed',(lo,hi),'a < b và khoảng nằm trong dải mốc đã chọn.',
           data['interval_source'])
    endpoints=[row for row in data['sorted_rows'] if row['x'] in (lo,hi)]
    if len(endpoints)==2:
        left,right=endpoints;target=data['target'];a0,b0=left['y']-target,right['y']-target
        if not a0 or not b0:state='passed';reason='Một đầu là mốc đúng mức trên dữ liệu.'
        elif (a0<0)!=(b0<0):state='passed';reason='Hai đầu đổi dấu. Nếu hàm thật liên tục thì có ít nhất một nghiệm.'
        else:state='not_verified';reason='Hai đầu cùng dấu; phép đổi dấu chưa xác nhận khoảng, không suy ra hàm thật vô nghiệm.'
        _check(data,'Đối chiếu mức tại hai đầu khoảng',state,{'left':a0,'right':b0},'Đổi dấu hoặc mốc đúng mức.',reason)
    else:_check(data,'Đối chiếu mức tại hai đầu khoảng','not_verified',None,'Cần giá trị của hai đầu.',
                'Có đầu khoảng không trùng mốc bảng; không tự suy giá trị hàm thật tại đầu đó.')
    return lo,hi


def _uniform(data,rows,rtol,atol):
    gaps=[b['x']-a['x'] for a,b in zip(rows,rows[1:])];h=gaps[0]
    data['grid']={'steps':gaps,'h':h,'rtol':rational(rtol),'atol':rational(atol),
                  'max_deviation':max(abs(v-h) for v in gaps),'classification':'nonuniform'}
    a=_nonnegative(atol,'Dung sai lưới tuyệt đối');r=_nonnegative(rtol,'Dung sai lưới tương đối')
    data['grid']['thresholds']=[a+r*max(abs(v),abs(h)) for v in gaps]
    if any(abs(v-h)>threshold for v,threshold in zip(gaps,data['grid']['thresholds'])):
        _fail('nonuniform_grid','Các h_i không đều theo dung sai đã công bố; không áp dụng Newton tiến/lùi đều và không tự sửa các mốc.')
    data['grid']['classification']='exactly_uniform' if all(v==h for v in gaps) else 'approximately_uniform'
    if data['grid']['classification']=='approximately_uniform':
        data['warnings'].append('Lưới gần đều: chứng nhận chỉ xét mô hình x_i = gốc + i·h đang công bố, không chứng nhận thay đổi sai số do độ lệch các mốc thực nhập.')
    _check(data,'Lưới x đều','passed' if data['grid']['classification']=='exactly_uniform' else 'warning',
           data['grid'],'|h_i−h| ≤ atol + rtol·max(|h_i|,|h|).',
           'Dung sai nhận dạng lưới độc lập với hai ngưỡng sai số nghiệm.')


def _errors(data,result,inverse=False):
    given=data['input'].get('error_data') or {}
    result['true_function_error_bound_x']=None
    if not given:return
    domain=given.get('domain');source=given.get('source')
    if not domain or len(domain)!=2 or not source:
        data['warnings'].append('Chưa có đủ miền áp dụng và nguồn của cận sai số hàm thật; không xuất cận bảo đảm.')
        return
    a,b=map(rational,domain)
    if a>b:_fail('invalid_input','Miền của cận sai số có đầu trái lớn hơn đầu phải.')
    if inverse and 'M' in given:
        nodes=[r['y'] for r in data['used_rows']];target=data['target']
        if not a<=min(*nodes,target)<=max(*nodes,target)<=b:
            data['warnings'].append('Miền cận M không chứa đủ các tung độ và mức; chưa xuất cận hàm thật.');return
        bound=rational(given['M'])
        if bound<0:_fail('invalid_input','Cận đạo hàm hàm ngược M phải không âm.')
        for node in nodes:bound*=abs(target-node)
        result['true_function_error_bound_x']=bound/math.factorial(len(nodes))
    elif not inverse and all(k in given for k in ('E','mu')):
        e,mu=map(rational,(given['E'],given['mu']))
        if e<0 or mu<=0:_fail('invalid_input','Cần E không âm và mu dương.')
        if not a<=min(data['interval'][0],rational(result['x_hat']))<=max(data['interval'][1],rational(result['x_hat']))<=b:
            data['warnings'].append('Miền của E,mu không chứa khoảng đã chọn và điểm tính; chưa xuất cận hàm thật.');return
        result['true_function_error_bound_x']=(decimal(e)+result['residual_y'])/decimal(mu)
    else:data['warnings'].append('Thiếu M của hàm ngược hoặc E,mu của hàm thuận; chưa có cận sai số hàm thật.')
    result['error_source']=deepcopy(given)


def _finish(data,exact,status,bound=None,residual=None):
    value=float(exact)
    if not np.isfinite(value):_fail('nonfinite_result','Hoành độ vượt miền float; không trả kết quả không hữu hạn.')
    rounding=abs(Decimal.from_float(value)-decimal(exact))
    data['status']=status
    data['result']={'x_hat':value,'x_internal':exact,'residual_y':residual,'iteration_error_bound_x':bound,
                    'rounding_error_bound_x':rounding,'true_function_error_bound_x':None,
                    'scope':'sample_value' if status=='exact_sample_match' else 'inverse_interpolant_value' if data['method']=='inverse_function' else 'forward_interpolant_root'}
    data['value']=value
    if data['method']!='inverse_function' and status!='exact_sample_match' and rounding>decimal(rational(data['input']['eps_x'])):
        _fail('numerical_resolution_limit',
              f'Phần chuyển nghiệm nội bộ sang float là {rounding:.12e}, lớn hơn ε_x={data["input"]["eps_x"]}. '
              'Giữ phép tính và kết quả nội bộ để xem; chưa thể trả một số float đạt ngưỡng. Hãy đổi đơn vị/gốc hoặc chọn dung sai phù hợp trong lượt khác.')
    lo,hi=data['interval']
    if not lo<=rational(exact)<=hi:
        data['warnings'].append('Kết quả mô hình nằm ngoài khoảng đang xét; giữ giá trị thô, không cắt về đầu mút.')
        if data['method'] in ('forward_iteration','backward_iteration'):
            data['last_approximation']=exact
            _fail('converged_outside_requested_bracket',
                  f'Phép lặp đạt ngưỡng tại x={value:.12g}, ngoài khoảng mục tiêu [{float(lo):.12g},{float(hi):.12g}]. '
                  'Đây chưa phải nghiệm được yêu cầu trong khoảng; giữ giá trị cuối để xem lại lựa chọn khởi tạo/khoảng.')
        data['status']='outside_bracket'
    try:_errors(data,data['result'],data['method']=='inverse_function')
    except (ValueError,TypeError,AttributeError,ArithmeticError) as exc:
        data['result']['true_function_error_bound_x']=None
        data['warnings'].append(f'Dữ kiện cận hàm thật chưa hợp lệ ({exc}); giữ kết quả mô hình nhưng không xuất cận hàm thật.')


def _inverse_function(data,rows,level,form,allow_extrapolation):
    data['phase']='Kiểm tra nhánh và đảo bảng'
    branch=data['branch_rows'];dy=[b['y']-a['y'] for a,b in zip(branch,branch[1:])]
    duplicates={}
    for row in branch:
        if row['y'] in duplicates:_fail('duplicate_inverse_node',f'Hàng {duplicates[row["y"]]} và {row["index"]} có cùng tung độ {float(row["y"]):.17g}, khác hoành độ; không chia cho hiệu bằng 0 trong bảng đảo.')
        duplicates[row['y']]=row['index']
    for left,right in zip(branch,branch[1:]):
        ulp=max(math.ulp(float(left['y'])),math.ulp(float(right['y'])))
        if abs(right['y']-left['y'])<=32*rational(ulp):
            data['warnings'].append(f'Hiệu tung độ ở hàng {left["index"]} và {right["index"]} gần độ phân giải float; bảng đảo nhạy với nhiễu. Không coi gần bằng là bằng đúng.')
    if not dy or not (all(v>0 for v in dy) or all(v<0 for v in dy)):
        _fail('invalid_branch','Dãy tung độ trên nhánh đã chọn không đơn điệu nghiêm ngặt. Hãy khảo sát/tách nhánh, không sắp toàn bảng theo y để che điểm đổi chiều.')
    in_branch=min(r['y'] for r in branch)<=level<=max(r['y'] for r in branch)
    in_nodes=min(r['y'] for r in rows)<=level<=max(r['y'] for r in rows)
    data['extrapolation']={'in_branch':in_branch,'in_selected_nodes':in_nodes,'allowed':bool(allow_extrapolation)}
    if not in_branch or not in_nodes:
        where='nhánh' if not in_branch else 'tập mốc đã chọn'
        if not allow_extrapolation:_fail('inverse_extrapolation',f'Mức {float(level):.12g} nằm ngoài miền tung độ {where}; ngoại suy ngược chưa được bật rõ. Không lấy miền của nhánh lớn thay cho miền của các mốc thực sự dùng.')
        data['warnings'].append('Đang ngoại suy ngược theo lựa chọn tường minh; kết quả không mang nghĩa nội suy thường.')
    _check(data,'Mức nằm trong miền tung độ nhánh và tập mốc','passed' if in_branch and in_nodes else 'warning',
           data['extrapolation'],'Mức được bao bởi cả nhánh và tập mốc, hoặc đã bật ngoại suy tường minh.')
    _check(data,'Nhánh khả nghịch trên mẫu','passed',[row['index'] for row in branch],
           'Tung độ phân biệt và tăng/giảm nghiêm ngặt trên các mốc đã cho.',
           'Muốn khẳng định hàm thật có nghịch đảo trên toàn nhánh cần thêm giả thiết của đề.')
    if form not in ('divided_difference','lagrange'):_fail('invalid_input','Dạng hàm ngược phải là divided_difference hoặc lagrange.')
    u=[r['y'] for r in rows];v=[r['x'] for r in rows]
    columns,steps=difference_table(u,v,True);coefficients=[column[0] for column in columns]
    data['model']={'variable':'y','basis':form,'nodes':u,'values':v,'columns':columns,
                   'coefficient_steps':steps,'coefficients':coefficients,'used_cells':[(0,k) for k in range(len(u))]}
    data['inverse_gaps']=[b-a for a,b in zip(u,u[1:])]
    data['phase']='Đánh giá đa thức hàm ngược'
    if form=='lagrange':
        terms=[]
        for i in range(len(u)):
            numerator=denominator=Fraction(1)
            factors=[]
            for j in range(len(u)):
                if i!=j:
                    numerator*=level-u[j];denominator*=u[i]-u[j]
                    factors.append({'node':u[j],'numerator':level-u[j],'denominator':u[i]-u[j]})
            weight=numerator/denominator
            terms.append({'i':i,'factors':factors,'denominator':denominator,'basis_value':weight,'contribution':v[i]*weight})
        data['model']['lagrange_terms']=terms
        value=sum((term['contribution'] for term in terms),Fraction(0))
    else:
        value=coefficients[-1];nested=[]
        for k in range(len(u)-2,-1,-1):
            previous=value;value=coefficients[k]+(level-u[k])*previous
            nested.append({'k':k,'coefficient':coefficients[k],'factor':level-u[k],'previous':previous,'value':value})
        data['model']['nested_steps']=nested
    pc,ps=difference_table([r['x'] for r in rows],[r['y'] for r in rows],True)
    forward=expand_newton([r['x'] for r in rows],[c[0] for c in pc])
    data['model']['forward_residual']=evaluate(forward,value)-level
    data['model']['forward_polynomial']=forward
    _finish(data,value,'inverse_value_computed')


def _convergence(data,model,lo,hi,t0,mode):
    """Phân loại căn cứ trước khi dùng q; nguồn do người dùng đưa luôn có điều kiện."""
    supplied=data['input'].get('convergence_certificate')
    automatic=certify(model,lo,hi,t0) if mode=='certified' else None
    if automatic is not None:
        automatic['kind']='not_applicable_to_seed' if not lo<=t0<=hi else 'analytic_verified' if automatic['verified'] else (
            'condition_failed' if 'disproved' in (automatic['image_state'],automatic['derivative_state']) else 'unavailable')
        automatic['interval']=(lo,hi)
        automatic['source']='Chặn hữu tỷ trên toàn đoạn của chính mô hình đã chọn.'
    if supplied is None:
        convergence=automatic or {'kind':'unavailable','interval':(lo,hi),'q':None,'verified':False,
                                  'source':'Người dùng chọn dừng thực hành; không dùng cận co để dừng.'}
        data['iteration']['convergence']=convergence
        return automatic
    if not isinstance(supplied,dict):_fail('invalid_convergence_certificate','Căn cứ hội tụ phải có loại, J, q, căn cứ giữ đoạn và nguồn; không nhận một số q trần.')
    kind=supplied.get('kind','user_supplied_bound')
    if kind in ('sampled_diagnostic','unavailable','condition_failed'):
        diagnostic=deepcopy(supplied);diagnostic.update(interval=(lo,hi),q=None,verified=False)
        data['iteration']['convergence']=diagnostic
        _check(data,'Căn cứ hội tụ được cung cấp','not_verified',kind,'Cần chứng nhận toàn đoạn, không chỉ khảo sát mẫu.',
               'Nguồn này không được dùng làm cận bảo đảm hoặc tự chuyển chế độ dừng.')
        if mode=='certified':_fail('certification_unavailable','Nguồn được chọn chưa chứng nhận co trên cả J; không tự đổi sang dừng thực hành.')
        return None
    if kind!='user_supplied_bound':
        _fail('invalid_convergence_certificate','Căn cứ gửi từ ngoài phải gắn user_supplied_bound; phần mềm không tự nhận là đã chứng minh analytic_verified/interval_verified chỉ từ một nhãn.')
    try:
        if len(supplied.get('J',[]))!=2 or len(supplied.get('invariant_image_bound',[]))!=2:raise ValueError()
        chosen_interval=tuple(map(rational,supplied['J']));image=tuple(map(rational,supplied['invariant_image_bound']))
        q=rational(supplied['q'])
    except (KeyError,ValueError,TypeError,OverflowError):
        _fail('invalid_convergence_certificate','Cận người dùng cần J=[lo,hi], q hữu hạn, invariant_image_bound=[cận dưới,cận trên] và nguồn source.')
    if chosen_interval!=(lo,hi):_fail('invalid_convergence_certificate','Đoạn J trong cận được cung cấp không khớp đoạn chứng nhận J đã chọn. Không dùng cận trên một J cho J khác; đoạn mục tiêu T được phép khác J.')
    if not 0<=q<1:_fail('invalid_convergence_certificate','Cận q do người dùng cung cấp phải thỏa 0 ≤ q < 1.')
    if not lo<=image[0]<=image[1]<=hi:_fail('invalid_convergence_certificate','Bao ảnh được cung cấp không nằm trong J hoặc bị đảo đầu; chưa đủ căn cứ giữ đoạn.')
    source=supplied.get('source')
    if not isinstance(source,str) or not source.strip():_fail('invalid_convergence_certificate','Thiếu nguồn/lập luận cho cận q và bao ảnh do người dùng cung cấp.')
    if not lo<=t0<=hi:
        data['iteration']['convergence']={'kind':'not_applicable_to_seed','interval':(lo,hi),'q':None,
                                         'verified':False,'source':source,'supplied_q':q,'image':image}
        _check(data,'Chứng nhận có chứa khởi tạo','not_verified',t0,(lo,hi),
               'Khởi tạo ngoài J nên chứng nhận này chưa áp dụng; không phải lỗi thiếu mốc.')
        if mode=='certified':_fail('certification_unavailable','Khởi tạo nằm ngoài đoạn J của chứng nhận đã cung cấp. Chọn lại J/khởi tạo hoặc chọn rõ chế độ thực hành; không phải thiếu mốc.')
        return None
    # Bác bỏ các khẳng định bị phản ví dụ chính xác tại đầu mút/điểm tới hạn;
    # vượt qua kiểm tra này vẫn không thay thế chứng minh toàn đoạn của nguồn.
    derivative_phi=derivative(model.phi_exact)
    points={lo,(lo+hi)/2,hi}
    if automatic:
        points.update(point for point,_ in automatic['derivative_candidates'])
    if any(abs(evaluate(derivative_phi,point))>q for point in points):
        _fail('invalid_convergence_certificate','Có giá trị đạo hàm tính chính xác vượt q được cung cấp; cận này mâu thuẫn với mô hình đang xét.')
    if any(not image[0]<=evaluate(model.phi_exact,point)<=image[1] for point in (lo,(lo+hi)/2,hi)):
        _fail('invalid_convergence_certificate','Bao ảnh được cung cấp bỏ sót một giá trị Phi(t) tính chính xác; cận này mâu thuẫn với mô hình đang xét.')
    accepted={'kind':'user_supplied_bound','interval':(lo,hi),'q':q,'image':image,
              'verified':True,'independently_verified':False,'source':source.strip(),
              'initial_state':'verified','image_state':'verified','derivative_state':'verified',
              'estimated_q':q,'image_numerators':tuple(v*model.d1_exact for v in image),
              'term_ranges':automatic['term_ranges'] if automatic else [],
              'phi_derivative':derivative_phi,'derivative_candidates':automatic['derivative_candidates'] if automatic else [],
              'derivative_image':(-q,q),'arithmetic':'user_supplied_assumption','machine_rounding_certified':False}
    data['iteration']['convergence']=accepted
    _check(data,'Cận và bao ảnh do người dùng cung cấp','warning',{'J':(lo,hi),'q':q,'image':image},
           'Có nguồn, đúng J, 0≤q<1 và bao ảnh nằm trong J.',
           'Chỉ kết luận theo cận/giả thiết được cung cấp; kiểm tra phản ví dụ không phải chứng minh độc lập.')
    if mode=='practical':
        accepted['used_for_stopping']=False
        data['warnings'].append('Đã giữ căn cứ hội tụ được cung cấp để đối chiếu; chế độ thực hành vẫn dừng theo độ thay đổi bước và phần dư, không dùng cận đó để thay tiêu chuẩn.')
        return None
    accepted['used_for_stopping']=True
    return accepted


def _initial_value(data,model,rows,target_interval):
    """Khởi tạo công bố trước; không tự đổi sau khi quỹ đạo gặp khó khăn."""
    rule=data['input'].get('initial_rule','origin_linear')
    record={'rule':rule}
    if rule=='origin_linear':
        value=(model.target_exact-model.y0_exact)/model.d1_exact
        record.update(numerator=model.target_exact-model.y0_exact,denominator=model.d1_exact)
    elif rule=='bracket_linear':
        a,b=data['interval'];ta,tb=target_interval
        def endpoint(x,t):
            match=next((row for row in rows if row['x']==x),None)
            return (match['y'],'mốc trong tập tính') if match else (evaluate(model.polynomial_exact,t),'đa thức thuận tại đầu khoảng')
        ya,source_a=endpoint(a,ta);yb,source_b=endpoint(b,tb)
        if ya==yb:_fail('zero_bracket_difference','Không lập được khởi tạo tuyến tính giữa hai đầu vì y_b−y_a=0. Chọn quy tắc khởi tạo khác ở lượt riêng.')
        x0=a+(b-a)*(model.target_exact-ya)/(yb-ya)
        value=(x0-model.origin_exact)/model.h_exact
        record.update(a=a,b=b,ya=ya,yb=yb,source_a=source_a,source_b=source_b,x0=x0)
    else:
        given_t=data['input'].get('initial_t');given_x=data['input'].get('initial_x')
        if given_t is None and given_x is None:_fail('invalid_initial_value','Quy tắc thủ công cần initial_t hoặc initial_x hữu hạn.')
        try:
            value=rational(given_t) if given_t is not None else (rational(given_x)-model.origin_exact)/model.h_exact
            if given_t is not None and given_x is not None and model.origin_exact+model.h_exact*value!=rational(given_x):
                _fail('invalid_initial_value','Hai giá trị initial_t và initial_x không khớp phép đổi biến của mô hình.')
        except (TypeError,ValueError,OverflowError):_fail('invalid_initial_value','Giá trị khởi tạo thủ công phải hữu hạn.')
        record.update(given_t=given_t,given_x=given_x)
    record.update(t0=value,x0=model.origin_exact+model.h_exact*value)
    return value,record


def _evaluate_iteration(model,t):
    """Cơ sở và đạo hàm cùng truy hồi; dùng cơ sở cũ khi cập nhật đạo hàm."""
    basis=Decimal(1);slope=Decimal(0);high=Decimal(0);high_prime=Decimal(0);terms=[]
    for order in range(1,len(model.differences)):
        factor=t+(order-1) if model.backward else t-(order-1)
        old=basis;old_prime=slope
        basis=old*factor/order;slope=(old_prime*factor+old)/order
        coefficient=decimal(model.differences[order]);value=coefficient*basis
        if order>=2:
            high+=value;high_prime+=coefficient*slope
            terms.append({'order':order,'basis':basis,'basis_derivative':slope,
                          'coefficient':model.differences[order],
                          'factors':[t+k if model.backward else t-k for k in range(order)],'value':value})
    return model.y0+model.d1*t+high,high,high_prime,terms


def _iterate(data,rows,level,eps_x,eps_y,max_iter,mode,rtol,atol):
    data['phase']='Kiểm tra lưới và dựng bảng sai phân'
    if 'grid' not in data:_uniform(data,rows,rtol,atol)
    signs=[(b['y']>a['y'])-(b['y']<a['y']) for a,b in zip(rows,rows[1:])]
    if 1 in signs and -1 in signs:
        data['warnings'].append('Tập mốc khai triển đi qua chỗ mẫu đổi chiều; đang giải đa thức thuận trên khoảng đã chọn, không gọi toàn tập mốc là một nhánh khả nghịch của hàm thật.')
        _check(data,'Đơn điệu của tập mốc lặp','warning',signs,'Nhánh chuẩn tăng hoặc giảm trên mẫu.',
               'Khoảng tường minh đang xác định bài toán đa thức thuận; chưa có một nhánh hàm ngược thật trên toàn tập.')
    else:_check(data,'Đơn điệu của tập mốc lặp','passed',signs,'Dãy tăng hoặc giảm trên các mốc đã cho.',
                'Không suy từ thứ tự mẫu ra tính đơn điệu của hàm thật giữa mọi mốc.')
    backward=data['method']=='backward_iteration'
    precision=max(50,-decimal(eps_x).adjusted()+40,-decimal(eps_y).adjusted()+40)
    xx=[r['x'] for r in rows];yy=[r['y'] for r in rows]
    columns,steps=difference_table(xx,yy)
    cells=[(len(rows)-k-1 if backward else 0,k) for k in range(len(rows))]
    coefficients=[columns[k][i] for i,k in cells]
    data['model']={'variable':'t','basis':'backward' if backward else 'forward','anchor':xx[-1] if backward else xx[0],
                   'h':xx[1]-xx[0],'columns':columns,'coefficients':coefficients,
                   'coefficient_steps':steps,'used_cells':cells}
    if not coefficients[1]:
        a,b=rows[-2:] if backward else rows[:2]
        _fail('zero_first_difference',f'Sai phân cấp một tại gốc = {float(b["y"]):.12g} − ({float(a["y"]):.12g}) = 0. Dừng trước phép chia.')
    scale=max(map(abs,yy));warning_atol=rational(data['input'].get('linear_warning_atol',0))
    warning_rtol=rational(data['input'].get('linear_warning_rtol','1e-12'))
    warning_threshold=warning_atol+warning_rtol*scale
    small=abs(coefficients[1])<=warning_threshold
    data['linear_difference_check']={'value':coefficients[1],'scale_y':scale,'threshold':warning_threshold,
                                     'atol':warning_atol,'rtol':warning_rtol,'small':small}
    if small:
        data['warnings'].append(f'Sai phân cấp một d={float(coefficients[1]):.12g} nhỏ so với thang tung độ {float(scale):.12g}: '
                                f'|d| ≤ {float(warning_threshold):.12g} (atol={float(warning_atol):.12g}, rtol={float(warning_rtol):.12g}). '
                                'Giữ nguyên mẫu số; phép lặp có thể nhạy với sai số số liệu.')
    _check(data,'Sai phân tuyến tính tại gốc','warning' if small else 'passed',data['linear_difference_check'],
           'd khác 0; cảnh báo khi |d| ≤ atol + rtol·max|y_i|.',
           'Không thay d bằng một số nhỏ tùy ý và không dùng ngưỡng cảnh báo làm ngưỡng sai số nghiệm.')
    model=InverseMap(xx,yy,level,backward,precision,table=(columns,steps))
    target_interval=tuple((v-model.origin_exact)/model.h_exact for v in data['interval'])
    t0,initial_record=_initial_value(data,model,rows,target_interval)
    chosen_j=data['input'].get('certificate_interval')
    if chosen_j is None and isinstance(data['input'].get('convergence_certificate'),dict):
        chosen_j=data['input']['convergence_certificate'].get('J')
    if chosen_j is None:chosen_j=target_interval
    try:
        if len(chosen_j)!=2:raise ValueError()
        lo,hi=map(rational,chosen_j)
        if lo>=hi:raise ValueError()
    except (ValueError,TypeError,OverflowError):_fail('invalid_certificate_interval','Đoạn chứng nhận J phải gồm hai số hữu hạn tăng dần trong biến t.')
    data['model']={'variable':'t','basis':'backward' if backward else 'forward','anchor':model.origin_exact,
                   'h':model.h_exact,'columns':model.columns,'coefficients':model.differences,
                   'coefficient_steps':model.difference_steps,'used_cells':model.coefficient_indices,
                   'polynomial':model.polynomial_exact,'phi':model.phi_exact,
                   'actual_degree':len(model.polynomial_exact)-1}
    data['iteration']={'T':target_interval,'J':(lo,hi),'t0':t0,'history':[],'stop_mode':mode,'certificate':None,
                       'initial_rule':initial_record,'target_exit_iterations':[],
                       'initial':{'iteration':0,'t_new':t0,'x_new':model.origin_exact+model.h_exact*t0,
                                  'status':'initial','error_bound_x':None,'residual_y':None,
                                  'in_target_t_interval':target_interval[0]<=t0<=target_interval[1],
                                  'in_certificate_interval':lo<=t0<=hi}}
    data['iterations_done']=0
    data['phase']='Kiểm tra giá trị đầu và hội tụ'
    in_target=target_interval[0]<=t0<=target_interval[1]
    if not in_target:
        data['warnings'].append(f't₀={float(t0):.12g} ngoài đoạn mục tiêu T=[{float(target_interval[0]):.12g},{float(target_interval[1]):.12g}]. Đây không phải lỗi thiếu mốc; giữ nguyên khởi tạo đã chọn và theo dõi quỹ đạo.')
    _check(data,'Khởi tạo so với khoảng mục tiêu','passed' if in_target else 'warning',t0,target_interval,
           'T được tính từ khoảng nghiệm và gốc thật. Khởi tạo ngoài T không chặn phép lặp thực hành.')
    certificate=_convergence(data,model,lo,hi,t0,mode)
    data['iteration']['certificate']=certificate
    if mode=='certified' and (not certificate or not certificate['verified']):
        _fail('certification_unavailable','Chưa đủ chứng nhận trên J: cần t₀ thuộc J, ánh xạ giữ J và cận co q<1. Xem từng điều kiện; đây không phải thiếu mốc và không tự đồng nghĩa phân kỳ. Không tự đổi sang thực hành hoặc chia đôi.')
    if certificate:
        _check(data,'Điều kiện co trên toàn J','passed' if certificate['kind']=='analytic_verified' else 'warning',
               {'q':certificate['q'],'image':certificate['image'],'J':(lo,hi),'kind':certificate['kind']},
               't0 thuộc J; Phi(J) nằm trong J; |Phi′| ≤ q < 1.',certificate['source'])
    elif mode=='practical':_check(data,'Điều kiện co trên toàn J','not_verified',None,
                                'Cần cận hợp lệ trên cả đoạn.','Dừng thực hành không được gọi là cận sai số bảo đảm.')
    with localcontext() as context:
        context.prec=model.precision
        q=decimal(certificate['q']) if certificate else None
        t=decimal(t0);left,right=map(decimal,(lo,hi));ta,tb=map(decimal,target_interval)
        dx,dy=decimal(eps_x),decimal(eps_y)
        if all(v==0 for v in model.differences[2:]):
            exact_t=(level-model.y0_exact)/model.d1_exact
            exact_x=model.origin_exact+model.h_exact*exact_t
            data['last_approximation']=exact_x
            _finish(data,exact_x,'linear_model_value',Decimal(0) if q is not None else None,Decimal(0))
            return
        for k in range(1,max_iter+1):
            data['phase']=f'Vòng lặp {k}'
            row={'iteration':k,'t_old':t,'term_contributions':[],'high_sum':None,'high_prime_old':None,
                 'numerator':None,'denominator':model.d1,'t_new':None,'x_new':None,'status':'pending',
                 'delta_t':None,'step_x':None,'q_used':q,'error_bound_x':None,'position_ok':False,'residual_ok':False,
                 'in_target_t_interval':None,'in_certificate_interval':None}
            data['iteration']['history'].append(row)
            data['iterations_done']=k
            try:
                p_old,high_sum,high_prime,terms=_evaluate_iteration(model,t)
                row.update(p_at_old=p_old,high_sum=high_sum,high_prime_old=high_prime,term_contributions=terms)
                numerator=model.target-model.y0-high_sum;row['numerator']=numerator
                new=numerator/model.d1
                row.update(t_new=new,x_new=model.location(new),delta_t=abs(new-t),step_x=model.h*abs(new-t))
                data['last_approximation']=row['x_new']
                if not all(v.is_finite() for v in (new,row['x_new'],row['step_x'])):raise ArithmeticError('t, x hoặc bước cập nhật không hữu hạn')
                row['in_target_t_interval']=ta<=new<=tb
                row['in_certificate_interval']=left<=new<=right if certificate else None
                if certificate and not left<=new<=right:
                    row['status']='certificate_violation'
                    _fail('certificate_violation',f'Vòng {k}: t mới={new:.12g} rời đoạn J đã chứng nhận [{left:.12g},{right:.12g}]. Dừng kiểm tra chứng nhận/số học; không kẹp biên và không đổi phương pháp.')
                if not row['in_target_t_interval']:
                    row['warnings']=['iterate_outside_target']
                    exits=data['iteration']['target_exit_iterations'];exits.append(k)
                    if len(exits)==1:data['warnings'].append(f'Vòng {k} rời khoảng mục tiêu T. Công thức đa thức vẫn xác định: giữ giá trị và tiếp tục; kết quả cuối phải được đối chiếu lại với khoảng x đã yêu cầu.')
                p,new_high,new_high_prime,new_terms=_evaluate_iteration(model,new)
                residual=abs(p-model.target);bound=model.h*q/(1-q)*abs(new-t) if q is not None else None
                if not p.is_finite() or not residual.is_finite() or (bound is not None and not bound.is_finite()):raise ArithmeticError('giá trị đa thức, phần dư hoặc cận không hữu hạn')
                row.update(p_at_new=p,high_sum_new=new_high,high_prime_new=new_high_prime,
                           residual_y=residual,error_bound_x=bound,
                           position_ok=(bound if bound is not None else row['step_x'])<=dx,residual_ok=residual<=dy)
            except _Invalid:raise
            except (ArithmeticError,ValueError,OverflowError) as exc:
                row['status']='nonfinite_iteration';row['failure_message']=str(exc)
                _fail('nonfinite_iteration',f'Vòng {k}: phép tính không hữu hạn hoặc tràn số khi đánh giá/cập nhật: {exc}. Giữ quỹ đạo đã tính; đây không phải lỗi thiếu mốc.')
            if row['position_ok'] and row['residual_ok']:
                row['status']='accepted' if row['in_target_t_interval'] else 'accepted_outside_target'
                success=('conditional_model_tolerance' if certificate and certificate['kind']=='user_supplied_bound'
                         else 'certified_model_tolerance') if q is not None else 'practical_stop'
                _finish(data,row['x_new'],success,bound,residual)
                return
            row['status']='continue'
            if new==t:_fail('numerical_stagnation',f'Vòng {k}: t mới bằng t cũ nhưng chưa đạt đủ hai tiêu chuẩn; không báo hội tụ.')
            t=new
    _fail('max_iter_reached',f'Đã thực hiện {max_iter} vòng; chưa đồng thời đạt ngưỡng vị trí và phần dư. Giữ lịch sử để người dùng quyết định lượt chạy tiếp theo.')


def solve_inverse(x,y,target,method='inverse_function',*,degree=None,count=None,interval=None,
                  selected_indices=None,branch_indices=None,bracket_indices=None,
                  eps_x=1e-10,eps_y=1e-6,max_iter=100,stop_mode='practical',inverse_form='divided_difference',
                  grid_rtol=1e-10,grid_atol=0,assumptions=None,error_data=None,
                  allow_extrapolation=False,display_digits=12,equality_atol_y=0,config_snapshot=None,
                  detail_level='summary',near_y_atol=0,near_y_rtol=1e-12,
                  linear_warning_atol=0,linear_warning_rtol=1e-12,convergence_certificate=None,
                  initial_rule='origin_linear',initial_t=None,initial_x=None,
                  certificate_interval=None,run_mode=None):
    """Luôn trả Report có trạng thái; các wrapper API cũ quyết định phát ValueError."""
    requested_method=method
    aliases={'inverse_lagrange':('inverse_function','lagrange'),'inverse_newton':('inverse_function','divided_difference'),
             'iterate_forward':('forward_iteration',None),'iterate_backward':('backward_iteration',None)}
    if isinstance(method,str) and method in aliases:
        method,chosen_form=aliases[method]
        if chosen_form is not None:inverse_form=chosen_form
    if run_mode is not None:
        stop_mode={'certified_only':'certified','practical':'practical'}.get(run_mode,run_mode)
    snapshot={'X':deepcopy(x),'Y':deepcopy(y),'target_y':target,'method':method,'degree':degree,
              'count':count,'interval':deepcopy(interval),'selected_indices':deepcopy(selected_indices),
              'branch_indices':deepcopy(branch_indices),'bracket_indices':deepcopy(bracket_indices),
              'eps_x':eps_x,'eps_y':eps_y,'max_iter':max_iter,'stop_mode':stop_mode,'inverse_form':inverse_form,
              'grid_rtol':grid_rtol,'grid_atol':grid_atol,'assumptions':deepcopy([assumptions] if isinstance(assumptions,str) else assumptions or []),
              'error_data':deepcopy(error_data or {}),'allow_extrapolation':allow_extrapolation,
              'display_digits':display_digits,'equality_atol_y':equality_atol_y,'ui':deepcopy(config_snapshot),
              'detail_level':detail_level,'near_y_atol':near_y_atol,'near_y_rtol':near_y_rtol,
              'linear_warning_atol':linear_warning_atol,'linear_warning_rtol':linear_warning_rtol,
              'convergence_certificate':deepcopy(convergence_certificate),'requested_method':requested_method,
              'initial_rule':initial_rule,'initial_t':initial_t,'initial_x':initial_x,
              'certificate_interval':deepcopy(certificate_interval),
              'run_mode':'certified_only' if stop_mode=='certified' else stop_mode}
    data={'input':snapshot,'method':method,'phase':'Đọc cấu hình','warnings':[],'status':'pending',
          'result':None,'value':None,'failure':None,'validation_checks':[],'iterations_done':0,'last_approximation':None}
    try:
        if method not in ('inverse_function','forward_iteration','backward_iteration','bisection'):_fail('selection_required','Chọn đúng phương pháp hàm ngược, lặp tiến, lặp lùi hoặc chia đôi trước khi chạy.')
        if stop_mode not in ('certified','practical'):_fail('invalid_input','Chế độ dừng phải là certified hoặc practical; không tự đổi chế độ.')
        if initial_rule not in ('origin_linear','bracket_linear','manual'):
            _fail('invalid_input','Quy tắc khởi tạo phải là origin_linear, bracket_linear hoặc manual.')
        if detail_level not in ('summary','detailed'):_fail('invalid_input','Mức chi tiết phải là summary hoặc detailed; không tác động đến phép tính.')
        _integer(display_digits,'Số chữ số bảng',0)
        for value,label in ((near_y_atol,'Ngưỡng tung độ gần trùng tuyệt đối'),(near_y_rtol,'Ngưỡng tung độ gần trùng tương đối'),
                            (linear_warning_atol,'Ngưỡng cảnh báo d tuyệt đối'),(linear_warning_rtol,'Ngưỡng cảnh báo d tương đối'),
                            (grid_atol,'Dung sai lưới tuyệt đối'),(grid_rtol,'Dung sai lưới tương đối')):
            _nonnegative(value,label)
        if method=='inverse_function':ex=Fraction(1,10**10);ey=Fraction(1,10**6);limit=100
        else:ex=_positive(eps_x,'Ngưỡng vị trí eps_x');ey=_positive(eps_y,'Ngưỡng phần dư eps_y');limit=_integer(max_iter,'Số vòng tối đa')
        rows,level=_prepare(data,x,y,target,selected_indices,branch_indices,count,degree)
        _near_levels(data,rows,near_y_atol,near_y_rtol)
        equality=rational(equality_atol_y)
        if equality<0:_fail('invalid_input','Dung sai gần mức phải không âm; 0 nghĩa chỉ nhận bằng đúng.')
        data['sample_scan']['near_level_samples']=[{'index':r['index'],'residual':abs(r['y']-level),'status':'near_level_sample'}
                                                for r in data['sorted_rows'] if 0<abs(r['y']-level)<=equality]
        data['phase']='Kiểm tra khoảng và tập mốc'
        if method in ('forward_iteration','backward_iteration'):_uniform(data,rows,grid_rtol,grid_atol)
        scan=sample_scan(rows,level)
        if interval is None and bracket_indices is None and len(scan['brackets'])+len(scan['sample_roots'])>1:
            _fail('selection_required','Có nhiều khoảng hoặc mốc ứng viên trong tập đã nhập. Hãy chọn khoảng/nhánh cần giải; không tự lấy khoảng đầu tiên hoặc tự giải tất cả.')
        if method=='bisection' and interval is None and bracket_indices is None:
            _fail('selection_required','Chia đôi cần khoảng do người dùng chọn; không tự lấy khoảng đổi dấu đầu tiên.')
        _interval(data,rows,interval,bracket_indices,method)
        if method=='bisection':
            xx=[r['x'] for r in rows];yy=[r['y'] for r in rows]
            columns,steps=difference_table(xx,yy,True);coefficients=[column[0] for column in columns]
            polynomial=expand_newton(xx,coefficients)
            data['model']={'variable':'x','basis':'divided_difference','nodes':xx,'values':yy,'columns':columns,
                           'coefficient_steps':steps,'coefficients':coefficients,'used_cells':[(0,k) for k in range(len(xx))]}
            _bisect(data,lambda value:evaluate(polynomial,value),level,ex,limit)
            from .inverse_presentation import build_report
            return build_report(data)
        matches=[row for row in rows if row['y']==level and data['interval'][0]<=row['x']<=data['interval'][1]]
        if len(matches)>1:_fail('selection_required','Có nhiều mốc bằng mức trong khoảng đang xét; cần chỉ định nhánh/khoảng, không tự trả mốc đầu tiên.')
        if matches:
            _finish(data,matches[0]['x'],'exact_sample_match',Fraction(0),Fraction(0))
        elif method=='inverse_function':_inverse_function(data,rows,level,inverse_form,allow_extrapolation)
        else:_iterate(data,rows,level,ex,ey,limit,stop_mode,grid_rtol,grid_atol)
    except _Invalid as exc:
        data['status']=exc.status;data['value']=None;data['failure']={'step':data['phase'],'message':str(exc)}
        _check(data,data['phase'],'failed',data['status'],None,str(exc))
    except (ArithmeticError,ValueError) as exc:
        data['status']='invalid_input' if data['phase']=='Đọc cấu hình' else 'nonfinite_operation'
        data['value']=None;data['failure']={'step':data['phase'],'message':f'{exc}. Không có kết quả đạt yêu cầu; giữ các bước đã tính.'}
        _check(data,data['phase'],'failed',data['status'],None,str(exc))
    from .inverse_presentation import build_report
    return build_report(data)


def require_success(report):
    if report.presentation['inverse_solution'].get('failure'):raise InverseFailure(report)
    return report


def _bisect(data,model,target,tolerance,max_steps):
    data['phase']='Kiểm tra hai đầu của mô hình đã chọn'
    a,b=data['interval'];history=[];data['bisection_history']=history
    def residual(value):
        result=model(value)
        try:return rational(result)-target
        except (ValueError,OverflowError,TypeError):_fail('nonfinite_operation',f'Mô hình không hữu hạn tại x={float(value):.12g}.')
    fa,fb=residual(a),residual(b)
    data['bisection_endpoints']={'a':a,'b':b,'fa':fa,'fb':fb}
    if not fa:root=a;b=a
    elif not fb:root=b;a=b
    else:
        if (fa<0)==(fb<0):_fail('no_model_sign_change',f'Hai đầu không trái dấu: F(a)={float(fa):.12g}, F(b)={float(fb):.12g}. Chưa đủ điều kiện chia đôi trên khoảng này; không suy vô nghiệm ở mọi nơi.')
        while (b-a)/2>tolerance:
            k=len(history)+1;data['phase']=f'Lần chia đôi {k}'
            if k>max_steps:_fail('max_iter_reached',f'Đã chia {max_steps} lần; nửa độ rộng chưa đạt ε_x.')
            c=(a+b)/2
            if float(c) in (float(a),float(b)):
                _fail('numerical_stagnation','Khoảng không còn phân biệt được trung điểm bằng float; dung sai nhỏ hơn độ phân giải float. Giữ khoảng cuối, không báo đã đạt.')
            fc=residual(c);row={'iteration':k,'a':a,'b':b,'c':c,'fa':fa,'fb':fb,'fc':fc}
            if not fc:a=b=c
            elif (fa<0)!=(fc<0):b,fb=c,fc
            else:a,fa=c,fc
            row.update(new_a=a,new_b=b,half_width=(b-a)/2);history.append(row)
        root=(a+b)/2
    data['final_interval']=(a,b)
    _finish(data,root,'bisection_model_tolerance',(b-a)/2,abs(residual(root)))
    data['result']['bracket']=(a,b)
    data['value']=(float(root),(float(a),float(b)))


def bisect_solution(model,target,a,b,tolerance=1e-10,max_steps=1000):
    """Dùng đúng callable được đưa vào; không đổi hoặc dựng lại đa thức."""
    snapshot={'X':[],'Y':[],'target_y':target,'interval':(a,b),'eps_x':tolerance,'eps_y':None,
              'max_iter':max_steps,'stop_mode':'certified','assumptions':['Mô hình được cung cấp liên tục trên khoảng đang xét.'],
              'error_data':{},'display_digits':12}
    data={'input':snapshot,'method':'bisection','phase':'Đọc cấu hình','warnings':[],
          'status':'pending','value':None,'result':None,'failure':None,'validation_checks':[]}
    if isinstance(model,np.polynomial.Polynomial):
        data['provided_polynomial']=[rational(str(float(v))) for v in model.coef]
        data['degree']=model.degree()
    try:
        lo,hi=map(rational,(a,b));level=rational(target)
        if lo>=hi:_fail('invalid_input','Chia đôi cần a<b; không tự đổi khoảng.')
        ex=_positive(tolerance,'Ngưỡng vị trí');limit=_integer(max_steps,'Số lần chia tối đa')
        data['interval']=(lo,hi);data['target']=level
        _bisect(data,lambda value:model(float(value)),level,ex,limit)
    except _Invalid as exc:
        data['status']=exc.status;data['failure']={'step':data['phase'],'message':str(exc)};data['value']=None
        _check(data,data['phase'],'failed',data['status'],None,str(exc))
    except (ArithmeticError,ValueError,TypeError) as exc:
        data['status']='invalid_input';data['failure']={'step':data['phase'],'message':str(exc)};data['value']=None
        _check(data,data['phase'],'failed',data['status'],None,str(exc))
    from .inverse_presentation import build_report
    return build_report(data)


def from_gui(method,values,xtext,ytext):
    """Bộ chuyển đổi mỏng, dùng parser/biểu mẫu cũ; cấu hình kỹ thuật hiện trong báo cáo."""
    mapping={'Hàm ngược':'inverse_function','Hàm ngược — Newton':'inverse_newton','Hàm ngược — Lagrange':'inverse_lagrange',
             'Lặp tiến':'forward_iteration','Lặp lùi':'backward_iteration',
             'Lặp có cận co':'backward_iteration' if values.get('direction','Tiến')=='Lùi' else 'forward_iteration',
             'Chia đôi đa thức':'bisection'}
    snapshot={'method':method,'values':deepcopy(values),'x':xtext,'y':ytext}
    try:
        # Dùng đúng cú pháp parser chung nhưng giữ các token thập phân để
        # bảng sai phân bậc cao không nhận nhiễu chỉ do bước parse sang float.
        numbers(xtext);numbers(ytext)
        def exact_numbers(value):
            return value.replace('−','-').replace(',', ' ').replace(';', ' ').split() if isinstance(value,str) else list(value)
        x,y=exact_numbers(xtext),exact_numbers(ytext)
        if not values.get('target','').strip():raise ValueError('Thiếu mức tung độ cần tìm trước khi chạy.')
        if method in ('Lặp có cận co','Chia đôi đa thức') and any(not values.get(key,'').strip() for key in ('a','b')):
            raise ValueError('Thiếu cận x của khoảng đã chọn; không tự lấy một khoảng ứng viên để giải.')
        if method=='Lặp có cận co' and values.get('direction','Tiến') not in ('Tiến','Lùi'):
            raise ValueError('Hướng nội suy phải là Tiến hoặc Lùi.')
        def optional_int(key):
            if values.get(key,'')=='':return None
            value=float(values[key])
            if not np.isfinite(value) or value!=int(value):raise ValueError(f'{key} phải là số nguyên.')
            return int(value)
        def structured(key):
            import json
            value=values.get(key,'')
            return json.loads(value) if isinstance(value,str) and value else value or None
        has_a=bool(values.get('a','').strip());has_b=bool(values.get('b','').strip())
        if has_a!=has_b:raise ValueError('Khoảng mục tiêu cần cả hai đầu a và b; không tự điền đầu còn thiếu.')
        interval=(values['a'],values['b']) if has_a and has_b else structured('interval')
        detail={'Tổng hợp':'summary','Chi tiết':'detailed'}.get(values.get('detail_level','summary'),values.get('detail_level','summary'))
        digits=optional_int('display_digits') if values.get('display_digits','')!='' else (
            optional_int('digits') if values.get('digits','')!='' else 12)
        initial_rule={'Theo gốc':'origin_linear','Tuyến tính tại gốc':'origin_linear',
                      'Theo hai đầu khoảng':'bracket_linear','Tuyến tính hai đầu khoảng':'bracket_linear',
                      'Thủ công':'manual'}.get(values.get('initial_rule','origin_linear'),values.get('initial_rule','origin_linear'))
        return solve_inverse(x,y,values['target'],mapping.get(method,method),
                             degree=optional_int('degree'),count=optional_int('count'),interval=interval,
                             selected_indices=structured('selected_indices'),branch_indices=structured('branch_indices'),
                             bracket_indices=structured('bracket_indices'),eps_x=float(values.get('tol',1e-10)),
                             eps_y=float(values.get('residual_tol',1e-6)),max_iter=optional_int('max_iter') if values.get('max_iter','')!='' else 100,
                             stop_mode=values.get('stop_mode','certified' if method=='Lặp có cận co' else 'practical'),
                             inverse_form=values.get('inverse_form','divided_difference'),
                             grid_rtol=float(values.get('grid_rtol',1e-10)),grid_atol=float(values.get('grid_atol',0)),
                             equality_atol_y=float(values.get('equality_atol_y',0)),
                             allow_extrapolation=values.get('allow_extrapolation','false').casefold()=='true',
                             assumptions=structured('assumptions'),error_data=structured('error_data'),
                             display_digits=digits,detail_level=detail,
                             near_y_atol=float(values.get('near_y_atol',0)),near_y_rtol=float(values.get('near_y_rtol',1e-12)),
                             linear_warning_atol=float(values.get('linear_warning_atol',0)),
                             linear_warning_rtol=float(values.get('linear_warning_rtol',1e-12)),
                             convergence_certificate=structured('convergence_certificate'),
                             initial_rule=initial_rule,
                             initial_t=values.get('initial_t') if values.get('initial_t','').strip() else None,
                             initial_x=values.get('initial_x') if values.get('initial_x','').strip() else None,
                             certificate_interval=structured('certificate_interval'),
                             run_mode=values.get('run_mode') or None,
                             config_snapshot=snapshot)
    except (ValueError,TypeError,KeyError,OverflowError) as exc:
        data={'input':{'X':xtext,'Y':ytext,'target_y':values.get('target'),'degree':values.get('degree'),
                       'eps_x':values.get('tol'),'eps_y':values.get('residual_tol',1e-6),'max_iter':values.get('max_iter',100),
                       'stop_mode':'practical','assumptions':[],'ui':snapshot},
              'method':'inverse_function' if method in ('Hàm ngược — Newton','Hàm ngược — Lagrange') else mapping.get(method,method),
              'status':'invalid_input','phase':'Đọc dữ liệu từ biểu mẫu hiện có','validation_checks':[],
              'value':None,'result':None,'warnings':[],'failure':{'step':'Đọc dữ liệu từ biểu mẫu hiện có','message':str(exc)}}
        _check(data,'Đọc dữ liệu từ biểu mẫu hiện có','failed',None,None,str(exc))
        from .inverse_presentation import build_report
        return build_report(data)
