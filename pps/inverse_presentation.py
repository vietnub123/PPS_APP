"""Lời giải nội suy ngược theo PDF; chỉ đọc kết quả, không giải lại mô hình."""
from decimal import Decimal, localcontext
from fractions import Fraction
import math
from contextvars import ContextVar

from .common import Report
from .inverse_model import decimal, rational


NAMES={'inverse_function':'Nội suy hàm ngược','forward_iteration':'Nội suy ngược — Newton tiến',
       'backward_iteration':'Nội suy ngược — Newton lùi','bisection':'Chia đôi đa thức thuận'}
_DIGITS=ContextVar('inverse_report_digits',default=12)


def number(value,digits=None,exact=False):
    if digits is None:digits=_DIGITS.get()
    if value is None:return '—'
    if isinstance(value,bool):return 'Đạt' if value else 'Chưa đạt'
    if isinstance(value,str):return value
    if exact and isinstance(value,Fraction):
        denominator=value.denominator
        for base in (2,5):
            while denominator%base==0:denominator//=base
        if denominator!=1 and value.numerator.bit_length()+value.denominator.bit_length()<=100 and len(str(value.numerator))+len(str(value.denominator))<=28:
            return str(value)
    with localcontext() as context:
        context.prec=max(80,digits+30)
        v=decimal(value)
        if not v:return '0'
        if v.adjusted()>=12 or v.adjusted()<-4:
            return f'{v:.{digits}e}'
        text=f'{v:.{digits}f}'.rstrip('0').rstrip('.') if digits else f'{v:.0f}'
        return f'{v:.{max(1,digits)}e}' if text in ('0','-0','') else text


def tex_number(value,exact=False,digits=None):
    text=number(value,digits=digits,exact=exact)
    if '/' in text:
        a,b=text.split('/');return rf'\frac{{{a}}}{{{b}}}'
    if 'e' in text.lower():
        a,b=text.lower().split('e');return rf'{a}\cdot 10^{{{int(b)}}}'
    return text


def factor(variable,value,latex=False):
    n=tex_number(value,True) if latex else number(value,exact=True)
    return f'({variable}-({n}))'


def basis(order,backward=False,latex=False,variable='t'):
    if order==0:return '1'
    if order>8:
        return (rf'\prod_{{j=0}}^{{{order-1}}}(t+ j)' if backward else rf'\prod_{{j=0}}^{{{order-1}}}(t-j)') if latex else f'prod({variable}{"+" if backward else "-"}j; j=0..{order-1})'
    factors=[variable if k==0 else f'({variable}{"+" if backward else "-"}{k})' for k in range(order)]
    return (r'\,' if latex else '*').join(factors)


def _newton_terms(model,latex=False):
    variable=model['variable'];result=[]
    for k,c in enumerate(model['coefficients']):
        if k and not c:continue
        if model['basis']=='power':
            term=tex_number(c,True) if latex else number(c,exact=True)
            if k:
                power=variable if k==1 else (rf'{variable}^{{{k}}}' if latex else f'{variable}^{k}')
                term=('' if c==1 else term+(r'\,' if latex else '*'))+power
        elif variable=='t':
            scaled=c/math.factorial(k)
            term=tex_number(scaled,True) if latex else number(scaled,exact=True)
            if k:term='('+term+')'+(r'\,' if latex else '*')+basis(k,model['basis']=='backward',latex)
        else:
            term=tex_number(c,True) if latex else number(c,exact=True)
            if k:
                if k>8:product=rf'\prod_{{j=0}}^{{{k-1}}}({variable}-{variable}_j)' if latex else f'prod({variable}-{variable}_j; j=0..{k-1})'
                else:product=(r'\,' if latex else '*').join(factor(variable,v,latex) for v in model['nodes'][:k])
                term='('+term+')'+(r'\,' if latex else '*')+product
        result.append((k,term))
    return result


def _report_precision(function):
    def build(data):
        try:digits=int(data['input'].get('display_digits',12))
        except (TypeError,ValueError):digits=12
        token=_DIGITS.set(max(0,digits))
        try:return function(data)
        finally:_DIGITS.reset(token)
    return build



from contextlib import contextmanager


class _Writer:
    """Cây bố cục; bản phẳng chỉ dùng cho text và tương thích Report cũ."""
    def __init__(self, report, detail_level):
        self.report=report; self.layout=[]; self.stack=[self.layout]
        self.detailed=detail_level in ('detailed','detail','chi_tiet')
        report.presentation.update(inverse_layout=self.layout,blocks=[],plain_formulas={},
                                   formulas=[],inverse_tables={},difference_tables={})

    @contextmanager
    def group(self,kind,title=None,**extra):
        node={'kind':kind,'children':[],**extra}
        if title:node['title']=title
        self.stack[-1].append(node);self.stack.append(node['children'])
        try:yield node
        finally:self.stack.pop()

    def details(self,title):return self.group('details',title,open=self.detailed)

    def text(self,text,tone=None):
        node={'kind':'text','text':str(text)}
        if tone:node['tone']=tone
        self.stack[-1].append(node)

    def formula(self,latex,plain):
        self.stack[-1].append({'kind':'formula','latex':latex})
        self.report.presentation['plain_formulas'][latex]=plain
        self.report.presentation['formulas'].append(('Công thức',[latex]))

    def expression(self,lhs,model,minimum=0):
        absolute={**model,'coefficients':[abs(c) for c in model['coefficients']]}
        tex=[(k,t) for k,t in _newton_terms(absolute,True) if k>=minimum]
        plain=dict(_newton_terms(absolute))
        if not tex:self.formula(lhs+'=0',lhs+' = 0');return
        chunks=[];a=b=''
        for k,term in tex:
            sign='-' if model['coefficients'][k]<0 else '+'
            pa=plain[k]
            # Giữ vài số hạng trên một dòng, vừa ô công thức cạnh bảng.
            # Không trải một đa thức ngắn ra mỗi dòng một số hạng.
            too_wide=False
            if a and len(tex)<=12:
                from .math_view import math_image
                too_wide=math_image((lhs+'=' if not chunks else r'\qquad ')+a+sign+term).width>455
            if a and (len(b)+len(pa)>65 or too_wide):
                chunks.append((a,b));a=b=''
            prefix=sign if a or chunks or sign=='-' else ''
            a+=prefix+term;b+=prefix+pa
        if a:chunks.append((a,b))
        for i,(a,b) in enumerate(chunks):
            self.formula((lhs+'=' if not i else r'\qquad ')+a,(lhs+' = ' if not i else '    ')+b)

    def table(self,title,headers,rows,exact=False,kind='plain',used_cells=(),text_columns=(),fixed_columns=()):
        index=len(self.report.tables);result=[]
        for row in rows:
            rr=[]
            for j,value in enumerate(row):
                if value is not None and not isinstance(value,(str,bool)) and j in fixed_columns:
                    with localcontext() as context:
                        context.prec=max(80,_DIGITS.get()+30);v=decimal(value)
                        text=(f'{v:.{_DIGITS.get()}e}' if v and (v.adjusted()>=12 or v.adjusted()<-4)
                              else f'{v:.{_DIGITS.get()}f}')
                else:text=number(value,exact=exact)
                rr.append(text)
            result.append(rr)
        self.report.table(title,headers,result)
        self.stack[-1].append({'kind':'table','index':index})
        self.report.presentation['inverse_tables'][index]={'kind':kind,'used_cells':list(used_cells),'text_columns':list(text_columns)}
        return index

    def finish(self):
        flat=self.report.presentation['blocks']
        def visit(nodes):
            for node in nodes:
                kind=node['kind']
                if kind in ('section','panel','details') and node.get('title'):flat.append(('heading',node['title']))
                if kind=='text':flat.append(('text',node['text']))
                elif kind=='formula':flat.append(('formula',node['latex']))
                elif kind=='table':flat.append(('table',node['index']))
                else:visit(node.get('children',[]))
        visit(self.layout)


def _decision(row):
    decision={'initial':'Khởi tạo','accepted':'Đạt cả hai','continue':'Tiếp tục',
              'accepted_outside_target':'Đạt ngưỡng ngoài khoảng',
              'certificate_violation':'Lỗi: vi phạm chứng nhận',
              'nonfinite_iteration':'Lỗi: tràn/không hữu hạn'}.get(row.get('status'),'Chưa đạt / lỗi')
    if row.get('in_target_t_interval') is False and row.get('status') in ('initial','continue'):
        decision+=' — ngoài T'
    return decision


def _sum_numbers(values,latex=False):
    parts=[]
    for value in values:
        sign='-' if value<0 else '+' if parts else ''
        parts.append(sign+(tex_number(abs(value),True) if latex else number(abs(value),exact=True)))
    return ''.join(parts) or '0'


def _power_model(coefficients,variable='t'):
    # Cơ sở Newton tại các nút 0 biểu diễn đúng lũy thừa; chỉ đổi cách viết.
    return {'variable':variable,'basis':'power','nodes':[Fraction(0)]*len(coefficients),'coefficients':coefficients}


def _inputs(w,data):
    config=data['input'];rows=data.get('used_rows',data.get('original_rows',[]))
    with w.group('section','1. Bài toán và lựa chọn'):
        with w.group('columns'):
            with w.group('panel','Thông số của lượt chạy'):
                degree=data.get('degree',config.get('degree'))
                w.text(f'Phương pháp: {w.report.title}. Mức cần tìm: {number(data.get("target",config.get("target_y")))}. Bậc tối đa: {degree if degree is not None else "chưa xác định"}.')
                if data.get('interval'):
                    a,b=data['interval'];w.text(f'Khoảng x: [{number(a)}, {number(b)}]. '+data.get('interval_source',''))
                if data['method']!='inverse_function':
                    w.text(f'ε_x={number(config.get("eps_x"))}; ε_y={number(config.get("eps_y"))}; tối đa {config.get("max_iter")} vòng.')
                if data['method'] in ('forward_iteration','backward_iteration'):
                    rules={'origin_linear':'Theo phần tuyến tính tại gốc','bracket_linear':'Tuyến tính giữa hai đầu khoảng','manual':'Thủ công'}
                    w.text('Khởi tạo: '+rules.get(config.get('initial_rule'),'Theo phần tuyến tính tại gốc')+'. Chế độ: '+('chỉ nhận kết quả có chứng nhận' if config.get('stop_mode')=='certified' else 'lặp thực hành, chưa bảo đảm sai số')+'.')
                if data.get('selection'):w.text('Chỉ số mốc dùng: '+str(data['selection']['indices'])+' (bắt đầu từ 0).')
                w.text(f'Giữ số đầy đủ khi tính; bảng trung gian hiển thị {_DIGITS.get()} chữ số hoặc dạng khoa học.','muted')
            with w.group('panel','Các mốc đã chọn'):
                if rows:w.table('Các cặp dùng trong mô hình',['dòng gốc','x_i','y_i'],((r['index'],r['x'],r['y']) for r in rows))
                elif data['method']=='bisection':w.text('Dùng trực tiếp mô hình được cung cấp; không nội suy bảng khác.')
                else:w.text('X đã nhận: '+str(config.get('X')));w.text('Y đã nhận: '+str(config.get('Y')))
        original=data.get('original_rows',[])
        if original and original!=rows:
            with w.details('Bảng nguồn và ánh xạ dòng'):
                w.table('Toàn bộ dữ liệu đã nhập',['dòng gốc','x','y'],((r['index'],r['x'],r['y']) for r in original))
                w.text('Thứ tự dòng sau sắp tăng x: '+str(data.get('sort_order'))+'.')
        scan=data.get('sample_scan')
        if scan:
            with w.details('Khảo sát mức và các nhánh trên mẫu'):
                w.text(f'Mốc đúng mức: {scan["sample_roots"]}; khoảng đổi dấu: {scan["brackets"]}; nhánh trên mẫu: {scan["branches"]}; hai đầu cùng mức: {scan["flat_intervals"]}.')
                w.text('Nếu hàm thật liên tục, mỗi khoảng đổi dấu có ít nhất một nghiệm. Phép quét có thể bỏ sót nghiệm tiếp xúc; đơn điệu trên mẫu không chứng minh đơn điệu giữa các mốc.')
                if scan.get('near_level_samples'):w.table('Mốc gần mức — không gọi là nghiệm chính xác',['dòng gốc','phần dư'],((r['index'],r['residual']) for r in scan['near_level_samples']))
        for assumption in config.get('assumptions',[]):w.text('Giả thiết người dùng cung cấp: '+str(assumption))


def _checks(w,data):
    labels={'passed':'✓ Đạt','failed':'Chưa đạt','warning':'Cảnh báo','not_verified':'Chưa xác minh','not_applicable':'Không áp dụng'}
    with w.group('section','2. Kiểm tra điều kiện'):
        checks=data.get('validation_checks',[])
        if not checks:
            if data.get('original_rows'):w.text(f'✓ Đã đọc {len(data["original_rows"])} dòng hữu hạn và giữ ghép cặp.','success')
            if data.get('selection'):w.text(f'✓ {len(data["used_rows"])} mốc cho bậc {data["degree"]}.','success')
            if data.get('failure'):w.text(data['failure']['step']+': '+data['failure']['message'],'failed')
        for check in checks:
            state=check.get('state','not_verified')
            reason=check.get('explanation') or check.get('expected_condition') or ''
            w.text(f'{labels.get(state,state)} — {check.get("title","Kiểm tra")}: {reason}',
                   'success' if state=='passed' else 'failed' if state=='failed' else 'muted' if state=='not_applicable' else 'warning')
            observed=check.get('observed_value')
            if state in ('failed','warning') and observed is not None:
                if isinstance(observed,(int,float,Fraction,Decimal)):observed=number(observed)
                w.text('Giá trị quan sát: '+str(observed)+'.','muted')
        grid=data.get('grid')
        if grid:
            w.text(f'Lưới x: h={number(grid["h"])}; độ lệch lớn nhất={number(grid["max_deviation"])}; atol={number(grid["atol"])}; rtol={number(grid["rtol"])}.','muted')
            with w.details('Các bước lưới thực nhập'):w.table('Kiểm tra lưới x',['i','h_i'],enumerate(grid['steps']))
        for warning in data.get('warnings',[]):w.text(warning,'warning')


def _coefficients(w,data):
    with w.group('section','3. Bảng tính trung gian'):
        model=data.get('model')
        if not model:
            w.text('Mức đã đạt đúng tại mốc dữ liệu; không cần lập bảng nội suy.' if data.get('status')=='exact_sample_match' else 'Chưa lập bảng hệ số: xem điều kiện chưa đạt.','muted');return
        rows=data['used_rows'];columns=model['columns'];n=len(rows)
        inverse=data['method']=='inverse_function';backward=model['basis']=='backward'
        divided=inverse or model['basis']=='divided_difference'
        headers=['i','y_i' if inverse else 'x_i','x_i' if inverse else 'y_i']
        sup=str.maketrans('0123456789','⁰¹²³⁴⁵⁶⁷⁸⁹')
        headers+=[f'T_{k}' if divided else ('∇' if backward else 'Δ')+(str(k).translate(sup) if k>1 else '')+'y' for k in range(1,n)]
        values=[]
        for i,row in enumerate(rows):
            rr=[i,row['y'] if inverse else row['x'],row['x'] if inverse else row['y']]
            rr+=([columns[k][i-k] if i>=k else None for k in range(1,n)] if backward else
                 [columns[k][i] if i<len(columns[k]) else None for k in range(1,n)])
            values.append(rr)
        title='Tỉ sai phân trên bảng đảo' if inverse else 'Bảng sai phân lùi' if backward else 'Tỉ sai phân đa thức thuận' if divided else 'Bảng sai phân tiến'
        w.table(title,headers,values,exact=True,kind='divided' if divided else 'backward' if backward else 'forward',
                used_cells=[(n-1 if backward else 0,2+k) for k in range(n)])
        w.text('Hệ số c = ['+', '.join(number(c,exact=True) for c in model['coefficients'])+'].')
        if model.get('actual_degree') is not None:
            w.text(f'Bậc tối đa {data["degree"]}; bậc thực tế của đa thức từ hệ số đang giữ: {model["actual_degree"]}. Không tự cắt các hệ số nhỏ về 0.','muted')
        w.text('Bảng ∇ đặt ô tại hàng kết thúc; lấy các hệ số cùng hàng gốc phải.' if backward else 'Các ô đánh dấu là hệ số được lấy, giữ đúng thứ tự mốc.')
        with w.details('Phép tính từng ô và cách lấy hệ số'):
            w.table('Các phép tính đã lưu',['i','cấp','phải','trái','tử','mẫu','kết quả'],
                    ((s['i'],s['order'],s['right'],s['left'],s['numerator'],s['denominator'],s['value']) for s in model.get('coefficient_steps',[])),exact=True)
            if not divided:w.table('Hệ số và mẫu giai thừa',['r','dòng dùng','c_r','r!','c_r/r!'],
                    ((k,model['used_cells'][k][0],c,math.factorial(k),c/math.factorial(k)) for k,c in enumerate(model['coefficients'])),exact=True)
            if data.get('inverse_gaps'):
                gaps=data['inverse_gaps'];w.text('Các khoảng tung độ: ['+', '.join(number(v,exact=True) for v in gaps)+']. '+('Tung độ cách đều.' if len(set(gaps))==1 else 'Tung độ không cách đều; dùng tỉ sai phân trên bảng đảo.'))


def _formulas(w,data):
    with w.group('section','4. Thiết lập công thức'):
        model=data.get('model');iteration=data.get('iteration');target=data.get('target')
        if data.get('status')=='exact_sample_match':
            value=data['result']['x_internal']
            w.formula(rf'\widehat{{x}}={tex_number(value)},\quad y_i={tex_number(target)}',
                      f'Nhận mốc x={number(value)} vì tung độ tại mốc bằng đúng {number(target)}.');return
        if data['method']=='inverse_function' and model:
            w.text('Đặt g=f⁻¹ trên nhánh đã chọn; nội suy Q(y) rồi tính Q(Y*). Không có vòng hội tụ tìm nghiệm.')
            if model['basis']=='lagrange':
                w.formula(r'Q_m(y)=\sum_{i=0}^m x_iL_i(y),\quad L_i(y)=\prod_{r\ne i}\frac{y-y_r}{y_i-y_r}',
                          'Q_m(y)=sum_i x_i*L_i(y); L_i(y)=prod_{r≠i}(y-y_r)/(y_i-y_r).')
            else:
                w.expression('Q_m(y)',model)
                with w.details('Công thức Newton tổng quát'):w.formula(r'Q_m(y)=c_0+\sum_{r=1}^m c_r\prod_{s=0}^{r-1}(y-y_s)',
                                      'Q_m(y)=c_0+sum_{r=1}^m c_r*prod_{s=0}^{r-1}(y-y_s).')
            w.formula(rf'\widehat{{x}}=Q_m({tex_number(target)})',f'x gần đúng = Q_m({number(target)}).');return
        if data['method']=='bisection':
            if model:w.expression('P_m(x)',model)
            elif data.get('provided_polynomial') is not None:w.expression('P(x)',_power_model(data['provided_polynomial'],'x'))
            if target is not None:w.formula(rf'F(x)=P_m(x)-({tex_number(target)})',f'F(x)=P_m(x)-({number(target)}).')
            w.text('Giữ đúng đa thức đã chọn, không dựng một mô hình khác khi chia đôi.');return
        if not model:w.text('Chưa lập được công thức từ dữ liệu hiện tại.','muted');return
        backward=model['basis']=='backward';symbol=r'\psi' if backward else r'\varphi'
        origin,h=model['anchor'],model['h'];c=model['coefficients']
        w.text('Đổi biến và đa thức thuận')
        w.formula(rf't=\frac{{x-({tex_number(origin)})}}{{{tex_number(h)}}},\quad x={tex_number(origin)}+({tex_number(h)})t',
                  f't=(x-({number(origin)}))/({number(h)}); x={number(origin)}+({number(h)})*t.')
        if iteration:
            ta,tb=iteration.get('T',iteration['J'])
            w.formula(rf'T=[{tex_number(ta,True)},{tex_number(tb,True)}]',
                      f'Ảnh T của khoảng mục tiêu theo đúng gốc đang dùng: [{number(ta,exact=True)},{number(tb,exact=True)}].')
        w.expression('p(t)',model);w.text('Phần hiệu chỉnh từ cấp 2 đến bậc đã chọn');w.expression('H(t)',model,minimum=2)
        w.formula(rf'p(t)={tex_number(target)}',f'Phương trình cần giải: p(t)={number(target)}.')
        if c[1]:w.formula(rf'{symbol}(t)=\frac{{{tex_number(target-c[0])}-H(t)}}{{{tex_number(c[1])}}}',
                             f'Hàm lặp Phi(t)=({number(target-c[0])}-H(t))/({number(c[1])}).')
        else:w.text('Sai phân cấp một bằng 0; không lập phép chia cho c₁.','failed')
        if iteration:
            t0=iteration['t0'];x0=origin+h*t0
            initial=iteration.get('initial_rule',{'rule':'origin_linear'})
            if initial['rule']=='origin_linear':
                w.formula(rf't_0=\frac{{{tex_number(target)}-({tex_number(c[0])})}}{{{tex_number(c[1])}}}={tex_number(t0)}',
                          f't_0=({number(target)}-({number(c[0])}))/({number(c[1])})={number(t0)}.')
            elif initial['rule']=='bracket_linear':
                w.formula(rf'x_0={tex_number(initial["a"])}+({tex_number(initial["b"]-initial["a"])})\frac{{{tex_number(target)}-({tex_number(initial["ya"])})}}{{{tex_number(initial["yb"])}-({tex_number(initial["ya"])})}}={tex_number(x0)}',
                          f'x_0=a+(b-a)*(Y*−y_a)/(y_b−y_a)={number(x0)}; t_0=(x_0−gốc)/h={number(t0)}.')
                w.text('Đầu trái dùng '+initial['source_a']+'; đầu phải dùng '+initial['source_b']+'.')
                w.formula(rf't_0=\frac{{{tex_number(x0)}-({tex_number(origin)})}}{{{tex_number(h)}}}={tex_number(t0)}',
                          f't_0=({number(x0)}-({number(origin)}))/({number(h)})={number(t0)}.')
            else:
                w.formula(rf't_0={tex_number(t0)}',f'Khởi tạo thủ công đã chọn: t_0={number(t0)}.')
            w.formula(rf'x_0={tex_number(origin)}+({tex_number(h)})t_0\approx {tex_number(x0)}',
                      f'x_0={number(origin)}+({number(h)})*({number(t0)})={number(x0)}.')
        with w.details('Cơ sở và hàm lặp tổng quát'):
            sign='+' if backward else '-'
            w.formula(rf'B_r(t)=\frac{{\prod_{{s=0}}^{{r-1}}(t{sign}s)}}{{r!}},\quad p(t)=\sum_{{r=0}}^m c_rB_r(t)',
                      f'B_r(t)=prod(t{sign}s,s=0..r-1)/r!; p(t)=sum(c_r*B_r(t),r=0..m).')
            w.formula(r'\Phi(t)=\frac{Y^*-c_0-H(t)}{c_1}','Phi(t)=(Y*−c_0−H(t))/c_1.')


def _convergence(w,data):
    with w.group('section','5. Hội tụ và tiêu chuẩn dừng'):
        iteration=data.get('iteration')
        if not iteration:
            if data['method']=='inverse_function':w.text('Hàm ngược tính trực tiếp Q(Y*); không áp dụng kiểm tra hội tụ lặp. Cận sai số hàm thật cần dữ kiện đạo hàm hợp lệ riêng.')
            elif data['method']=='bisection':
                w.text('Chia đôi cần hai đầu trái dấu hoặc một đầu đạt mức. Phần dư chỉ để đối chiếu, không tự thêm làm điều kiện dừng.')
                w.formula(r'B_x=\frac{b-a}{2}\leq\varepsilon_x','Cận vị trí nghiệm mô hình: B_x=(b-a)/2 ≤ eps_x.')
            else:w.text('Chưa kiểm tra được hội tụ của phép lặp hiện tại; xem nguyên nhân ở bước lập công thức hoặc cấu hình, không đồng nhất với thiếu mốc.','muted')
            return
        lo,hi=iteration['J'];ta,tb=iteration.get('T',iteration['J']);t0=iteration['t0'];cert=iteration.get('certificate')
        with w.group('columns'):
            with w.group('panel','Căn cứ hội tụ trên đoạn đang chạy'):
                w.text(f'T=[{number(ta)}, {number(tb)}] là ảnh của khoảng mục tiêu theo gốc thật; t₀={number(t0)} '+('thuộc T.' if ta<=t0<=tb else 'ngoài T — cảnh báo, không phải thiếu mốc.'))
                if data['input'].get('stop_mode')=='certified' or data['input'].get('certificate_interval') is not None or data['input'].get('convergence_certificate'):
                    w.text(f'J=[{number(lo)}, {number(hi)}] dùng để kiểm tra chứng nhận, phân biệt với T; t₀ '+('thuộc J.' if lo<=t0<=hi else 'ngoài J nên chứng nhận chưa áp dụng.'))
                evidence=cert or iteration.get('convergence',{})
                kind=evidence.get('kind','unavailable')
                labels={'analytic_verified':'Đã chặn hữu tỷ trên toàn đoạn','interval_verified':'Đã kiểm tra bằng tính khoảng có bao ngoài',
                        'user_supplied_bound':'Theo cận/giả thiết do người dùng cung cấp','sampled_diagnostic':'Khảo sát số, chưa có cận bảo đảm',
                        'unavailable':'Chưa có chứng nhận hội tụ','condition_failed':'Chưa đủ điều kiện co trên đoạn đã chọn',
                        'not_applicable_to_seed':'Chứng nhận không chứa khởi tạo đang dùng; không áp dụng cận q cho quỹ đạo này'}
                w.text(labels.get(kind,'Chưa phân loại chứng cứ'),'success' if kind in ('analytic_verified','interval_verified') else 'warning')
                if cert:
                    image=cert.get('image') or cert.get('invariant_image_bound')
                    if image:
                        a,b=image;w.formula(rf'\Phi(J)\subseteq[{tex_number(a,True)},{tex_number(b,True)}]',
                                          f'Bao ảnh Phi(J) nằm trong [{number(a,exact=True)}, {number(b,exact=True)}].')
                    q=cert.get('q') if cert.get('q') is not None else cert.get('estimated_q')
                    if q is not None:w.formula(rf'q={tex_number(q,True)}\quad {"<" if q<1 else r"\geq"}\quad1',
                                                f'Cận |Phi′| = {number(q,exact=True)}; '+('nhỏ hơn 1.' if q<1 else 'chưa đạt q<1.'))
                    if cert.get('source'):w.text('Nguồn cận: '+str(cert['source']))
                w.text('Thiếu chứng nhận không tự chứng minh phân kỳ; không tự đổi t₀, khoảng hay phương pháp.','muted')
            with w.group('panel','Hai điều kiện dừng độc lập'):
                if cert and cert.get('verified'):w.formula(r'B_j=|h|\frac{q}{1-q}|t_j-t_{j-1}|\leq\varepsilon_x',
                                                       'Cận vị trí nghiệm mô hình: B_j=|h|*q/(1-q)*|t_j-t_(j-1)| ≤ eps_x.')
                elif data['input'].get('stop_mode')=='certified':
                    w.text('Lượt này yêu cầu cận sai số có chứng nhận nhưng chưa đủ căn cứ áp dụng. Giữ nguyên chế độ đã chọn; không tự chuyển sang dừng thực hành.','warning')
                else:w.formula(r's_j=|h||t_j-t_{j-1}|\leq\varepsilon_x','Độ thay đổi theo x: s_j=|h|*|t_j-t_(j-1)| ≤ eps_x; chưa phải cận sai số.')
                w.formula(r'r_j=|p(t_j)-Y^*|\leq\varepsilon_y','Độ lệch tại giá trị mới: r_j=|p(t_j)−Y*| ≤ eps_y.')
                w.text(f'ε_x={number(data["input"].get("eps_x"))}; ε_y={number(data["input"].get("eps_y"))}. Chỉ dừng đạt yêu cầu khi cả hai cùng đạt.')
        if cert:
            with w.details('Chi tiết phép chặn ảnh và đạo hàm'):
                if cert.get('term_ranges'):w.table('Cận số hạng cấp cao trên J',['r','cận dưới','cận trên'],
                     ((t['order'],t['lower'],t['upper']) for t in cert['term_ranges']),exact=True)
                if cert.get('phi_derivative'):w.expression(r'\Phi^\prime(t)',_power_model(cert['phi_derivative']))
                if cert.get('derivative_image'):
                    a,b=cert['derivative_image'];w.formula(rf'\Phi^\prime(t)\in[{tex_number(a,True)},{tex_number(b,True)}]',
                                                          f'Trên cả J, Phi′(t) thuộc [{number(a,exact=True)}, {number(b,exact=True)}].')
                if cert.get('derivative_candidates'):w.table('Các điểm dùng để chặn đạo hàm',['t','Phi′(t)'],cert['derivative_candidates'],exact=True)
                w.text('Bậc thấp xét đầu mút và cực trị; bậc cao dùng cận hệ số/đơn điệu đã chứng minh. Không lấy max từ một lưới mẫu float.')
                w.text('Chứng nhận toán học xét mô hình đã công bố, chưa chứng nhận toàn bộ sai số máy bằng số học khoảng.')


def _iteration_detail(w,data,row):
    model=data['model'];c=model['coefficients'];j=row['iteration']
    with w.details(f'Vòng {j} — {_decision(row)}'):
        w.text(f'✓ Dùng giá trị cũ t_{j-1}={number(row["t_old"])}.')
        w.text(f'd={number(row.get("denominator"))}; P(t cũ)={number(row.get("p_at_old"))}; H′(t cũ)={number(row.get("high_prime_old"))}; q dùng để dừng={number(row.get("q_used"))}.','muted')
        if row.get('t_new') is None or row.get('status')=='nonfinite_iteration':
            w.text('Phép đánh giá/cập nhật không hoàn tất: '+str(row.get('failure_message','giá trị không hữu hạn'))+'. Giữ nguyên các bước trước, không coi là thiếu mốc.','failed')
            return
        for term in row.get('term_contributions',[]):
            k=term['order'];factors=term.get('factors',[])
            if k<=8:
                product=r'\,'.join('('+tex_number(v)+')' for v in factors)
                w.formula(rf'T_{{{k}}}=\frac{{({tex_number(term["coefficient"])}){product}}}{{{k}!}}={tex_number(term["value"])}',
                          f'T_{k}=({number(term["coefficient"])})*'+'*'.join('('+number(v)+')' for v in factors)+f'/{k}! = {number(term["value"])}.')
            else:w.text(f'Cấp {k}: hệ số={number(term["coefficient"])}; cơ sở={number(term["basis"])}; đóng góp={number(term["value"])}.')
        w.formula(rf'H(t_{{{j-1}}})={tex_number(row["high_sum"])}',f'✓ Cộng H(t_{j-1})={number(row["high_sum"])}.')
        w.formula(rf't_{{{j}}}=\frac{{{tex_number(data["target"]-c[0])}-({tex_number(row["high_sum"])})}}{{{tex_number(row["denominator"])}}}={tex_number(row["t_new"])}',
                  f'✓ t_{j}=({number(data["target"]-c[0])}-({number(row["high_sum"])}))/({number(row["denominator"])})={number(row["t_new"])}.')
        w.formula(rf'x_{{{j}}}={tex_number(model["anchor"])}+({tex_number(model["h"])})({tex_number(row["t_new"])})={tex_number(row["x_new"])}',
                  f'✓ x_{j}={number(model["anchor"])}+({number(model["h"])})*({number(row["t_new"])})={number(row["x_new"])}.')
        w.text('So với khoảng mục tiêu T: '+('ở trong.' if row.get('in_target_t_interval',True) else 'đang ở ngoài; giữ nguyên giá trị để theo dõi quỹ đạo.')+
               (' So với đoạn chứng nhận J: '+('ở trong.' if row.get('in_certificate_interval') else 'vi phạm J.') if row.get('in_certificate_interval') is not None else ''),
               'warning' if row.get('in_target_t_interval') is False else 'muted')
        if row.get('p_at_new') is not None:w.formula(rf'r_{{{j}}}=|{tex_number(row["p_at_new"])}-({tex_number(data["target"])})|={tex_number(row["residual_y"])}',
                                                f'Độ lệch tại giá trị mới: |{number(row["p_at_new"])}-({number(data["target"])})|={number(row["residual_y"])}.')
        bound=row.get('error_bound_x')
        if bound is not None:
            q=row['q_used'];w.formula(rf'B_{{{j}}}=({tex_number(model["h"])})\frac{{{tex_number(q)}}}{{1-({tex_number(q)})}}|{tex_number(row["t_new"])}-({tex_number(row["t_old"])})|={tex_number(bound)}',
                                     f'B_{j}=h*q/(1-q)*|t mới-t cũ|={number(bound)}.')
        else:w.formula(rf's_{{{j}}}=|h||t_{{{j}}}-t_{{{j-1}}}|={tex_number(row["step_x"])}',f'Độ thay đổi theo x s_{j}={number(row["step_x"])}; chưa phải cận sai số.')
        criterion=bound if bound is not None else row['step_x']
        with w.group('panel',keep_together=True):
            w.text(f'Vị trí: {number(criterion)} ≤ ε_x={number(data["input"].get("eps_x"))} — {number(row.get("position_ok",False))}.','success' if row.get('position_ok') else 'warning')
            w.text(f'Độ lệch: {number(row.get("residual_y"))} ≤ ε_y={number(data["input"].get("eps_y"))} — {number(row.get("residual_ok",False))}.','success' if row.get('residual_ok') else 'warning')
            w.text('Quyết định: '+_decision(row)+'.','success' if row.get('status')=='accepted' else 'warning')


def _process(w,data):
    with w.group('section','6. Quá trình tính'):
        model=data.get('model');iteration=data.get('iteration')
        if data['method']=='inverse_function' and model:
            if model['basis']=='lagrange':
                terms=model['lagrange_terms']
                w.table('Cơ sở và đóng góp Lagrange',['i','x_i','L_i(Y*)','x_i L_i(Y*)'],
                        ((t['i'],data['used_rows'][t['i']]['x'],t['basis_value'],t['contribution']) for t in terms),exact=True)
                total=data.get('result',{}).get('x_internal') if data.get('result') else None
                if total is not None:w.formula(rf'Q_m({tex_number(data["target"])})='+_sum_numbers([t['contribution'] for t in terms],True)+'='+tex_number(total,True),
                                              'Tổng đóng góp: '+_sum_numbers([t['contribution'] for t in terms])+' = '+number(total,exact=True)+'.')
                for term in terms:
                    with w.details(f'Cơ sở L_{term["i"]} và phép thay mức'):
                        factors=term['factors']
                        if len(factors)<=8:
                            numerator=r'\,'.join(factor('y',v['node'],True) for v in factors) or '1'
                            w.formula(rf'L_{{{term["i"]}}}(y)=\frac{{{numerator}}}{{{tex_number(term["denominator"],True)}}}',
                                      f'L_{term["i"]}(y)='+'*'.join(factor('y',v['node']) for v in factors)+f'/({number(term["denominator"],exact=True)}).')
                        w.formula(rf'L_{{{term["i"]}}}({tex_number(data["target"])})={tex_number(term["basis_value"],True)}',
                                  f'L_{term["i"]}({number(data["target"])})={number(term["basis_value"],exact=True)}.')
                        w.text('Đóng góp x_i L_i = '+number(term['contribution'],exact=True)+'.')
            else:
                w.text('Tính Q(Y*) bằng nhân lồng, dùng đúng hệ số trong bảng tỉ sai phân.')
                for step in model.get('nested_steps',[]):w.formula(rf'v_{{{step["k"]}}}={tex_number(step["coefficient"],True)}+({tex_number(step["factor"],True)})({tex_number(step["previous"],True)})={tex_number(step["value"],True)}',
                    f'v_{step["k"]}={number(step["coefficient"],exact=True)}+({number(step["factor"],exact=True)})*({number(step["previous"],exact=True)})={number(step["value"],exact=True)}.')
            return
        if iteration:
            cert=iteration.get('certificate');bounded=bool(cert and cert.get('verified'))
            initial=iteration.get('initial') or {'t_new':iteration['t0'],'x_new':model['anchor']+model['h']*iteration['t0']}
            summary=[[0,initial['t_new'],initial['x_new'],None,None,_decision(initial)]]
            summary.extend([row['iteration'],row['t_new'],row['x_new'],row.get('error_bound_x') if bounded else row['step_x'],row.get('residual_y'),_decision(row)] for row in iteration['history'])
            w.table('Bảng tổng hợp vòng lặp',['vòng','t_j','x_j','Cận sai số B_j' if bounded else 'Độ thay đổi theo x','Độ lệch r_j','Trạng thái'],
                    summary,kind='summary',fixed_columns=(1,2,3,4),text_columns=(5,))
            for row in iteration['history']:_iteration_detail(w,data,row)
            if not iteration['history']:w.text('Chưa có vòng cập nhật; giữ nguyên giá trị khởi tạo. Mô hình tuyến tính được giải trực tiếp nếu đủ điều kiện.')
            return
        if data.get('bisection_history') is not None:
            endpoints=data.get('bisection_endpoints')
            if endpoints:w.text(f'F({number(endpoints["a"])})={number(endpoints["fa"])}; F({number(endpoints["b"])})={number(endpoints["fb"])}.')
            history=data['bisection_history']
            w.table('Tổng hợp chia đôi',['lần','trung điểm c','F(c)','a mới','b mới','nửa độ rộng'],
                    ((r['iteration'],r['c'],r['fc'],r['new_a'],r['new_b'],r['half_width']) for r in history),kind='summary')
            with w.details('Hai đầu trước mỗi lần chia'):w.table('Dấu trước cập nhật',['lần','a cũ','b cũ','F(a)','F(b)'],
                    ((r['iteration'],r['a'],r['b'],r['fa'],r['fb']) for r in history))
            if data.get('final_interval'):
                a,b=data['final_interval'];w.text(f'Khoảng cuối [{number(a)}, {number(b)}]; lấy trung điểm của chính khoảng này.')
            return
        w.text('Mức bằng đúng dữ liệu tại một mốc; nhận hoành độ tại mốc, không tạo vòng lặp giả.' if data.get('status')=='exact_sample_match' else 'Chưa có bước tính sau tiền kiểm.','muted')


def _result(w,data):
    with w.group('section','7. Kết luận đúng phạm vi',keep_together=True):
        failure=data.get('failure')
        if failure:
            w.text(f'Chưa có kết quả đạt yêu cầu. {failure["step"]}: {failure["message"]}','failed');w.report.lines.append('Chưa đạt: '+failure['message'])
            history=data.get('iteration',{}).get('history',[])
            if history:
                last=history[-1];w.text(f'Giá trị cuối để xem: t={number(last["t_new"])}; x={number(last["x_new"])}. Đây chưa phải nghiệm đạt yêu cầu.')
            elif data.get('last_approximation') is not None:
                w.text('Giá trị mô hình để xem: x='+number(data['last_approximation'])+'. Đây chưa phải nghiệm đạt yêu cầu trong khoảng đã chọn.')
            w.text('Giữ nguyên cấu hình và các bước đã tính. Chọn lại khoảng/mốc/bậc/phương pháp và chạy lượt riêng; không có kết quả thay thế ngầm.');return
        result=data.get('result')
        if not result:w.text('Chưa có kết quả hợp lệ.','warning');return
        labels={'exact_sample_match':'Mốc dữ liệu đạt đúng mức; không cần lặp.',
                'linear_model_value':'Đã giải trực tiếp mô hình tuyến tính; không tạo vòng lặp giả.',
                'inverse_value_computed':'Đã tính Q(Y*) theo mô hình hàm ngược; không có vòng hội tụ.',
                'practical_stop':'Đạt dừng thực hành; chưa có cận bảo đảm vị trí từ tính co.',
                'certified_model_tolerance':'Đã đạt hai ngưỡng theo chứng nhận của mô hình.',
                'conditional_model_tolerance':'Đã đạt hai ngưỡng theo cận/giả thiết do người dùng cung cấp.',
                'bisection_model_tolerance':'Đạt ngưỡng vị trí của nghiệm mô hình được giữ trong khoảng chia đôi.',
                'outside_bracket':'Đã tính mô hình nhưng kết quả ngoài khoảng đang xét; giữ giá trị thô để xem lại.'}
        w.text(labels.get(data['status'],'Đã tính kết quả mô hình.'),'warning' if data['status'] in ('outside_bracket','practical_stop','conditional_model_tolerance') else 'success')
        x=result['x_hat'];bound=result.get('iteration_error_bound_x')
        eps=rational(data['input'].get('eps_x',1e-10)) if data['method']!='inverse_function' else Fraction(1,10**10)
        digits=max(9,-decimal(eps).adjusted()+2);value=Decimal(str(x))
        def shown_value():return f'{value:.{digits}f}' if -4<=value.adjusted()<12 else number(value,digits)
        shown=shown_value()
        if bound is not None:
            base=decimal(bound)+result['rounding_error_bound_x']
            while base<decimal(eps) and base+abs(Decimal(shown)-value)>decimal(eps):digits+=1;shown=shown_value()
        shown_tex=shown if 'e' not in shown.lower() else tex_number(Decimal(shown),digits=digits)
        w.formula(rf'\widehat{{x}}\approx {shown_tex}','x gần đúng ≈ '+shown+'.')
        history=data.get('iteration',{}).get('history',[])
        if history:
            last=history[-1];criterion=last.get('error_bound_x') if last.get('error_bound_x') is not None else last['step_x']
            w.text(f'Sau {len(history)} vòng. Vị trí: {number(criterion)} ≤ {number(data["input"]["eps_x"])} — {number(last["position_ok"])}. Độ lệch: {number(last.get("residual_y"))} ≤ {number(data["input"]["eps_y"])} — {number(last["residual_ok"])}.')
        if bound is not None:
            w.text('Cận sai số lặp đối với nghiệm mô hình: '+number(bound)+'.')
            printed=decimal(bound)+result['rounding_error_bound_x']+abs(Decimal(shown)-value);result['printed_error_bound_x']=printed
            w.text('Cận gồm chuyển sang float và làm tròn số đang in: '+number(printed)+'; chưa gồm sai số nội suy hàm thật hoặc toàn bộ sai số số học máy.','muted')
            w.report.lines.append('cận nghiệm mô hình: '+number(bound))
        model=data.get('model')
        if model and 'forward_residual' in model:
            with w.details('Đối chiếu riêng với đa thức thuận'):
                w.formula(rf'P_m(Q_m(Y^*))-Y^*={tex_number(model["forward_residual"],True)}','P_m(Q_m(Y*))−Y*='+number(model['forward_residual'],exact=True)+'.')
                w.text('Đây không phải lỗi hội tụ của phương pháp hàm ngược. Q nội suy hàm ngược, không phải nghịch đảo chính xác của P.')
        if result.get('true_function_error_bound_x') is not None:
            w.text('Cận hàm thật theo dữ kiện/giả thiết cung cấp: '+number(result['true_function_error_bound_x'])+'.')
            source=result.get('error_source',{});w.text('Nguồn: '+str(source.get('source','chưa có'))+'; miền ['+', '.join(number(v) for v in source.get('domain',[]))+'].')
            w.text('Dữ kiện đã dùng: '+'; '.join(f'{key}={number(rational(source[key]),exact=True)}' for key in ('M','E','mu') if key in source)+'.')
        else:w.text('Chưa đủ dữ kiện chặn sai số so với nghiệm hàm thật. Sai số nội suy, sai số dữ liệu và sai số giải mô hình là các thành phần khác nhau.','muted')


@_report_precision
def build_report(data):
    title=NAMES.get(data['method'],'Nội suy ngược')
    if data['method']=='inverse_function':
        model=data.get('model') or {};form=model.get('basis',data['input'].get('inverse_form'))
        title+=' — Lagrange' if form=='lagrange' else ' — Newton tỉ sai phân'
    report=Report(title,value=data.get('value'));report.presentation['inverse_solution']=data
    w=_Writer(report,data['input'].get('detail_level','summary'))
    _inputs(w,data);_checks(w,data)
    if data.get('failure') and not data.get('model'):
        # Giữ các bước đã thực hiện, không đẩy lỗi tiền kiểm sang trang sau
        # bằng bốn mục tính toán chưa hề được chạy.
        _result(w,data);w.finish();data['report_steps']=list(report.presentation['blocks'])
        return report
    with w.group('columns'):_coefficients(w,data);_formulas(w,data)
    _convergence(w,data);_process(w,data);_result(w,data);w.finish()
    data['report_steps']=list(report.presentation['blocks'])
    return report
