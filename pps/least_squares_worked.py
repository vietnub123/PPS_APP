"""Bình phương tối thiểu có lời giải và trace đúng bộ giải đã lựa chọn.

Các tổng và phép khử dùng Decimal. QR/SVD không bị trình bày giả thành
khử Gauss; mỗi thuật toán lưu đúng dữ liệu mà nó thực sự dùng để giải.
"""
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction
import math

import numpy as np
import sympy as sp

from .common import Report, expression, function
from .linear_algebra import exp_parameter
from .worked_report import ReportBuilder


LINEAR='Tuyến tính theo cơ sở'
LOG_MODEL='Log của tổ hợp cơ sở'
TRANSFORMS=('1/(a+b*x)','x/(a+b*x)','a+b*ln(x)','A*b^x')


class _FitFailure(ValueError):
    def __init__(self,status,message):self.status=status;super().__init__(message)


def _fail(status,message):raise _FitFailure(status,message)


def _dec(value):return value if isinstance(value,Decimal) else Decimal(str(float(value)))


def _dot(a,b):return sum((x*y for x,y in zip(a,b)),Decimal(0))


def _finite_float(value,label):
    result=float(value)
    if not np.isfinite(result):_fail('numerical_failure',label+' vượt miền số float; giữ các bước đã tính.')
    return result


def _check(data,title,state,detail):
    data['checks'].append({'title':title,'state':state,'detail':str(detail)})


def _basis_values(labels,x):
    funcs=[];columns=[]
    for j,label in enumerate(labels):
        try:
            f=function(str(label));column=np.asarray(f(x),float)
        except (ValueError,ArithmeticError) as exc:
            _fail('basis_domain_error',f'Cơ sở {j} ({label}) không hữu hạn/đúng miền trên dữ liệu: {exc}')
        funcs.append(f);columns.append(column)
    return funcs,np.column_stack(columns)


def _prepare(data,x,y,kind,basis,weights):
    data['phase']='Đọc quan sát và kiểm tra miền mô hình'
    try:x=np.asarray(x,float);y=np.asarray(y,float)
    except (ValueError,TypeError):_fail('invalid_input','Hai dãy phải gồm các số thực hữu hạn.')
    if x.ndim!=1 or y.shape!=x.shape or not len(x):_fail('invalid_input','Cần hai dãy một chiều cùng số phần tử, có ít nhất một quan sát.')
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):_fail('invalid_input','Mọi x,y phải hữu hạn; không tự loại dòng lỗi.')
    try:w=np.ones(len(x)) if weights is None else np.asarray(weights,float)
    except (ValueError,TypeError):_fail('invalid_input','Trọng số phải là dãy số thực.')
    if w.shape!=x.shape or not np.all(np.isfinite(w)) or np.any(w<0) or not np.any(w>0):
        _fail('invalid_weights','Cần w_i≥0, hữu hạn, cùng số quan sát và ít nhất một trọng số dương.')
    data.update(x=x,y=y,weights=w,effective_observations=int(np.count_nonzero(w)))
    _check(data,'Quan sát hữu hạn, giữ nguyên dòng','passed',f'{len(x)} quan sát; x trùng và lưới không đều đều được giữ.')
    _check(data,'Trọng số','passed',f'{np.count_nonzero(w)} dòng có trọng số dương; {np.count_nonzero(w==0)} dòng trọng số 0 vẫn hiện trong báo cáo.')
    labels=[str(v).strip() for v in basis if str(v).strip()]
    z=y.copy();sign=1.;transform='y';basekind=kind
    nonlinear=kind in ('Hàm mũ — SSE thang y','Lũy thừa — SSE thang y')
    if nonlinear:basekind=kind.split(' — ')[0]
    if basekind in ('Hàm mũ','Lũy thừa') and not nonlinear:
        if np.any(y==0) or not (np.all(y>0) or np.all(y<0)):
            _fail('transform_domain_error','Khớp log cần y khác 0 và cùng dấu. Phép biến đổi này không dùng được; không kết luận mọi cách khớp đều vô nghiệm.')
        sign=float(np.sign(y[0]));z=np.log(abs(y));transform='ln|y|'
    if basekind=='Lũy thừa':
        if np.any(x<=0):_fail('transform_domain_error','Lũy thừa với số mũ thực cần x>0; không xóa điểm có x≤0.')
        labels=['1','ln(x)']
    elif basekind=='Hàm mũ':
        # Cột hằng biểu diễn ln|A|, không phải tự thêm hệ số chặn vào một
        # mô hình tuyến tính đã yêu cầu đi qua gốc.
        labels=['1']+labels
    elif kind==LOG_MODEL:
        with np.errstate(over='ignore'):z=np.exp(y)
        if not np.all(np.isfinite(z)) or np.any(z==0):_fail('transform_domain_error','Biến đổi V=exp(y) tràn/hụt số; không thể dùng thang mũ với đơn vị hiện tại.')
        transform='exp(y)'
    elif kind in TRANSFORMS:
        if kind=='1/(a+b*x)':
            if np.any(y==0):_fail('transform_domain_error','Biến đổi 1/y cần mọi y khác 0.')
            labels=['1','x'];z=1/y;transform='1/y'
        elif kind=='x/(a+b*x)':
            if np.any(x==0) or np.any(y==0):_fail('transform_domain_error','Biến đổi 1/x,1/y cần mọi x,y khác 0; không tự bỏ dòng.')
            labels=['1','1/x'];z=1/y;transform='1/y'
        elif kind=='a+b*ln(x)':
            if np.any(x<=0):_fail('transform_domain_error','Cơ sở ln(x) cần x>0; y có thể âm hoặc bằng 0.')
            labels=['1','ln(x)']
        else:
            if np.any(y==0) or not (np.all(y>0) or np.all(y<0)):_fail('transform_domain_error','Khớp A*B^x bằng log cần y cùng dấu, khác 0.')
            labels=['1','x'];sign=float(np.sign(y[0]));z=np.log(abs(y));transform='ln|y|'
    elif basekind not in (LINEAR,'Hàm mũ','Lũy thừa'):
        _fail('invalid_model','Mô hình chưa được hỗ trợ; không tự thay bằng một mô hình khác.')
    if not labels:_fail('invalid_basis','Cần ít nhất một hàm cơ sở theo đúng mô hình đề bài.')
    funcs,theta=_basis_values(labels,x)
    if not np.all(np.isfinite(z)):_fail('transform_domain_error','Giá trị sau biến đổi không hữu hạn; không tự sửa dữ liệu.')
    data.update(labels=labels,theta=theta,z=z,transform=transform,sign=sign,basekind=basekind,nonlinear=nonlinear)
    _check(data,'Miền của cơ sở và phép biến đổi','passed','Mọi cột được đánh giá hữu hạn trên các quan sát; thứ tự cơ sở được giữ.')
    return x,y,w,funcs


def _weighted_design(data):
    theta,z,w=data['theta'],data['z'],data['weights']
    max_weight=_dec(max(w));roots=[(_dec(v)/max_weight).sqrt() for v in w]
    columns=[[_dec(v)*root for v,root in zip(column,roots)] for column in theta.T]
    target=[_dec(v)*root for v,root in zip(z,roots)]
    p=theta.shape[1]
    gram=[[_dot([_dec(v) for v in theta[:,i]],[_dec(a)*_dec(b) for a,b in zip(w,theta[:,j])]) for j in range(p)] for i in range(p)]
    rhs=[sum((_dec(a)*_dec(b)*_dec(c) for a,b,c in zip(w,theta[:,j],z)),Decimal(0)) for j in range(p)]
    data.update(gram=gram,rhs=rhs,weight_scale=max_weight,weighted_columns=columns,weighted_target=target)
    scales=[max(map(abs,c),default=Decimal(0)) for c in columns]
    normalized=np.column_stack([[float(v/s) if s else 0. for v in c] for c,s in zip(columns,scales)])
    singular=np.linalg.svd(normalized,compute_uv=False)
    threshold=(max(normalized.shape)*np.finfo(float).eps*singular[0]) if len(singular) else 0.
    rank=int(np.count_nonzero(singular>threshold))
    condition=float(singular[0]/singular[-1]) if len(singular) and singular[-1]>0 else math.inf
    data['rank']={'numeric_rank':rank,'parameters':p,'singular_values':singular,'threshold':threshold,
                  'condition_scaled':condition,'diagnostic':'SVD của ma trận có trọng số đã đổi thang cột; không gọi là chứng minh hạng đại số.'}
    if condition>1e8:data['warnings'].append('Ma trận thiết kế có độ nhạy lớn theo SVD đổi thang; nhiều chữ số tính toán không tự khôi phục sai số của số liệu hoặc lựa chọn mô hình.')
    return columns,target


def _back_substitution(r,z,trace):
    count=len(z);answer=[Decimal(0)]*count
    for i in range(count-1,-1,-1):
        tail=sum((r[i][j]*answer[j] for j in range(i+1,count)),Decimal(0))
        if not r[i][i]:_fail('rank_deficient','Pivot bằng 0: tham số chưa xác định duy nhất, không phải bài toán không có cực tiểu.')
        answer[i]=(z[i]-tail)/r[i][i]
        trace.append({'row':i,'rhs':z[i],'tail':tail,'pivot':r[i][i],'value':answer[i]})
    return answer


def _qr(data,columns,target):
    p=len(columns);q=[];r=[[Decimal(0)]*p for _ in range(p)];steps=[]
    data['solver_trace']={'kind':'qr','steps':steps,'back_substitution':[]}
    precision=data['precision'];small=Decimal(10)**(-precision+25)
    for j,column in enumerate(columns):
        v=column.copy();original_norm=_dot(v,v).sqrt();projections=[]
        for turn in range(2):
            for i,qi in enumerate(q):
                projection=_dot(qi,v);r[i][j]+=projection
                v=[a-projection*b for a,b in zip(v,qi)]
                projections.append({'pass':turn+1,'onto':i,'projection':projection})
        norm=_dot(v,v).sqrt()
        step={'column':j,'original_norm':original_norm,'projections':projections,'remaining_norm':norm,
              'threshold':original_norm*small,'q_column':None}
        steps.append(step)
        if not original_norm or norm<=original_norm*small:
            data['rank']['resolved_rank']=len(q)
            _fail('rank_deficient','Các cột cơ sở phụ thuộc trên tập quan sát có trọng số; tham số không duy nhất. Có thể chọn SVD chuẩn nhỏ nhất ở lượt khác.')
        r[j][j]=norm;qi=[a/norm for a in v];q.append(qi);step['q_column']=qi
    z=[_dot(qi,target) for qi in q]
    data['solver_trace'].update(Q=q,R=r,qt_target=z)
    answer=_back_substitution(r,z,data['solver_trace']['back_substitution'])
    data['rank']['resolved_rank']=p
    if data['rank']['numeric_rank']<p:
        data['warnings'].append('SVD float coi ma trận gần thiếu hạng; QR Decimal vẫn tách được các cột ở độ chính xác đang dùng. Kết quả nhạy với sai số dữ liệu.')
    return answer


def _gauss(data):
    a=[row.copy() for row in data['gram']];b=data['rhs'].copy();p=len(b);steps=[]
    trace={'kind':'normal_gauss','steps':steps,'back_substitution':[]};data['solver_trace']=trace
    small=Decimal(10)**(-data['precision']+25)
    for k in range(p):
        pivot=max(range(k,p),key=lambda i:abs(a[i][k]));scale=max(abs(a[i][k]) for i in range(k,p))
        record={'column':k,'pivot_row':pivot,'pivot':a[pivot][k],'threshold':scale*small,
                'swapped':pivot!=k,'eliminations':[]};steps.append(record)
        if not scale or abs(a[pivot][k])<=scale*small:
            _fail('rank_deficient','Hệ chuẩn có pivot không phân biệt được với 0; tham số chưa được xác định duy nhất trong độ chính xác đang dùng. Không gọi là vô nghiệm.')
        if pivot!=k:a[k],a[pivot]=a[pivot],a[k];b[k],b[pivot]=b[pivot],b[k]
        for i in range(k+1,p):
            multiplier=a[i][k]/a[k][k];before=a[i].copy()+[b[i]]
            for j in range(k,p):a[i][j]-=multiplier*a[k][j]
            b[i]-=multiplier*b[k]
            record['eliminations'].append({'row':i,'multiplier':multiplier,'before':before,'after':a[i].copy()+[b[i]]})
        record['matrix_after']=[row.copy()+[rhs] for row,rhs in zip(a,b)]
    trace.update(R=a,triangular_rhs=b)
    data['rank']['resolved_rank']=p
    if data['rank']['condition_scaled']>1e8:
        data['warnings'].append('Ma trận thiết kế nhạy số; hệ chuẩn làm bình phương số điều kiện. Đã giữ đúng bộ giải Gauss được chọn, có thể chọn QR ở lượt khác.')
    return _back_substitution(a,b,trace['back_substitution'])


def _svd(data,columns,target,minimum_norm):
    p=len(columns);scale=max((abs(v) for column in columns for v in column),default=Decimal(0))
    if not scale:scale=Decimal(1)
    tscale=max(map(abs,target),default=Decimal(0)) or Decimal(1)
    design=np.column_stack([[float(v/scale) for v in column] for column in columns])
    z=np.array([float(v/tscale) for v in target])
    u,s,vt=np.linalg.svd(design,full_matrices=False)
    threshold=max(design.shape)*np.finfo(float).eps*(s[0] if len(s) else 0.)
    active=s>threshold;rank=int(np.count_nonzero(active))
    trace={'kind':'svd','singular_values':s,'threshold':threshold,'rank':rank,'Vt':vt,
           'u_target':u.T@z,'minimum_norm':bool(minimum_norm)};data['solver_trace']=trace
    data['rank'].update(numeric_rank=rank,resolved_rank=rank,threshold=threshold,singular_values=s)
    data['rank']['diagnostic']='SVD của thiết kế có trọng số sau một đổi thang chung; giữ chuẩn Euclid của hệ số gốc khi chọn chuẩn nhỏ nhất.'
    if rank<p and not minimum_norm:
        _fail('rank_deficient','SVD xác nhận thiếu hạng theo ngưỡng đã công bố. Có cực tiểu nhưng không có bộ tham số duy nhất; chưa chọn nghiệm chuẩn nhỏ nhất.')
    factors=np.zeros(len(s));factors[active]=(u.T@z)[active]/s[active]
    answer=vt.T@factors
    if rank<p:data['warnings'].append('Đã chọn nghiệm chuẩn nhỏ nhất theo ngưỡng SVD; các tham số không được dữ liệu xác định duy nhất.')
    return [_dec(v)*tscale/scale for v in answer]


def _linear_predictor(data,coefficients,funcs):
    kind=data['kind'];sign=data['sign'];precision=data['precision']
    def predict(values,return_decimal=False):
        arr=np.asarray(values,float)
        if not np.all(np.isfinite(arr)):raise ValueError('Điểm dự đoán phải hữu hạn.')
        if kind=='x/(a+b*x)':
            # Chỉ phép biến đổi khi khớp cần x≠0. Mô hình gốc tại điểm mới
            # x=0 vẫn có thể xác định, không đánh giá lại cơ sở 1/x ở đó.
            result=[]
            with localcontext() as ctx:
                ctx.prec=precision
                for argument in arr.ravel():
                    argument=_dec(argument);denominator=coefficients[1]+coefficients[0]*argument
                    if not denominator:raise ValueError('Mẫu a+b*x của mô hình bằng 0 tại điểm dự đoán.')
                    result.append(argument/denominator)
            if return_decimal:return result
            ans=np.asarray([float(v) for v in result])
            if not np.all(np.isfinite(ans)):raise ValueError('Dự đoán vượt miền float.')
            return float(ans[0]) if arr.ndim==0 else ans.reshape(arr.shape)
        features=np.column_stack([f(arr.ravel()) for f in funcs])
        result=[]
        with localcontext() as ctx:
            ctx.prec=precision
            for row in features:
                value=sum((c*_dec(v) for c,v in zip(coefficients,row)),Decimal(0))
                if kind in ('Hàm mũ','Lũy thừa','A*b^x'):value=Decimal(str(sign))*value.exp()
                elif kind==LOG_MODEL:
                    if value<=0:raise ValueError('Đối số log của mô hình sau khôi phục không dương tại điểm dự đoán.')
                    value=value.ln()
                elif kind=='1/(a+b*x)':
                    if not value:raise ValueError('Mẫu mô hình sau khôi phục bằng 0 tại điểm dự đoán.')
                    value=1/value
                elif kind=='x/(a+b*x)':
                    if not value:raise ValueError('Mẫu biến đổi bằng 0 tại điểm dự đoán.')
                    value=1/value
                result.append(value)
        if return_decimal:return result
        ans=np.array([float(v) for v in result])
        if not np.all(np.isfinite(ans)):raise ValueError('Dự đoán vượt miền float; mô hình và các hệ số vẫn được giữ.')
        return float(ans[0]) if arr.ndim==0 else ans.reshape(arr.shape)
    return predict


def _nonlinear(data,funcs,initial,max_iter,tolerance):
    # Thang nội bộ thay đơn vị A và nhân mục tiêu với cùng hằng số dương;
    # mọi tham số/phần dư hiển thị được đổi lại đơn vị ban đầu.
    theta=data['theta'][:,1:];x,y,w=data['x'],data['y'],data['weights']
    # Dòng w=0 không được đổi độ lớn mục tiêu hay làm tiêu chuẩn dừng
    # ngừng quá sớm chỉ vì một giá trị y ngoại lệ không có trọng số.
    yscale=max(abs(y[w>0])) or 1.
    root_w=np.array([float((_dec(a)/_dec(max(w))).sqrt()) for a in w])
    scaled_y=np.zeros(len(y));scaled_y[w>0]=y[w>0]/yscale
    data['nonlinear_scale']=yscale
    if initial is None:
        if np.all(y>0) or np.all(y<0):
            from .linear_algebra import fit_basis
            start,_=fit_basis(data['theta'][w>0],np.log(abs(y[w>0]))-math.log(yscale),w[w>0])
            parameters=np.r_[np.sign(y[0])*np.exp(start[0]),start[1:]]
            initial_rule='Khởi tạo công bố từ khớp log trên các dòng có trọng số dương.'
        else:
            mean=np.average(scaled_y,weights=w);parameters=np.r_[mean if mean else 1.,np.zeros(theta.shape[1])]
            initial_rule='Khởi tạo A bằng trung bình có trọng số, các hệ số mũ bằng 0.'
    else:
        parameters=np.asarray(initial,float).copy()
        if parameters.shape!=(theta.shape[1]+1,) or not np.all(np.isfinite(parameters)):_fail('invalid_initial','Khởi tạo phải gồm A và đủ hệ số số mũ hữu hạn theo đúng thứ tự.')
        parameters[0]/=yscale;initial_rule='Tham số đầu do người dùng cung cấp.'
    if not np.all(np.isfinite(parameters)):_fail('invalid_initial','Đổi tham số đầu sang thang nội bộ vượt miền float; chọn lại đơn vị hoặc tham số đầu.')
    if np.all(y[w>0]==0):data['warnings'].append('Các quan sát hiệu lực đều có y=0: A=0 khớp đúng nhưng các hệ số trong số mũ không được xác định duy nhất.')
    trace={'kind':'levenberg_marquardt','initial_rule':initial_rule,'iterations':[],'yscale':yscale,
           'weight_scale':max(w),'tolerance':tolerance,'max_iterations':max_iter}
    data['solver_trace']=trace
    def evaluate(par):
        with np.errstate(over='ignore',invalid='ignore'):
            exponent=np.exp(theta@par[1:]);pred=par[0]*exponent
            jac=np.column_stack([exponent,pred[:,None]*theta])
        if not np.all(np.isfinite(pred)) or not np.all(np.isfinite(jac)):raise ValueError('Mô hình/Jacobian không hữu hạn với tham số đề xuất.')
        residual=(pred-scaled_y)*root_w
        if not np.all(np.isfinite(residual)):raise ValueError('Phần dư nội bộ không hữu hạn.')
        return residual,jac*root_w[:,None]
    def physical(par):return np.r_[par[0]*yscale,par[1:]]
    try:res,jac=evaluate(parameters)
    except ValueError as exc:_fail('invalid_initial',str(exc))
    damping=1e-3;cost=float(res@res);trace['initial_parameters']=physical(parameters).copy()
    converged=False
    for k in range(1,max_iter+1):
        gradient=jac.T@res;gnorm=float(np.linalg.norm(gradient,np.inf))
        if gnorm<=tolerance:
            converged=True;trace['termination']='Chuẩn vô cùng của gradient mục tiêu nội bộ đạt ngưỡng.';break
        norms=np.linalg.norm(jac,axis=0);norms=np.where(norms>0,norms,1.)
        augmented=np.vstack([jac,np.sqrt(damping)*np.diag(norms)])
        delta=np.linalg.lstsq(augmented,np.r_[-res,np.zeros(len(parameters))],rcond=None)[0]
        proposal=parameters+delta;valid=True
        try:
            new_res,new_jac=evaluate(proposal);new_cost=float(new_res@new_res)
            if not np.isfinite(new_cost):raise ValueError('Mục tiêu của bước thử không hữu hạn.')
        except ValueError:valid=False;new_cost=math.inf
        accepted=valid and new_cost<cost
        row={'iteration':k,'old_parameters':physical(parameters).copy(),'proposed_parameters':physical(proposal).copy(),
             'sse_before':_dec(cost)*_dec(yscale)**2*_dec(max(w)),
             'sse_proposed':_dec(new_cost)*_dec(yscale)**2*_dec(max(w)) if valid else None,
             'damping':damping,'step_norm':float(np.linalg.norm(delta)),'gradient_norm':gnorm,
             'accepted':accepted,'jacobian':jac.copy(),'residual_scaled':res.copy(),
             'step_internal':delta.copy(),'jacobian_column_norms':norms.copy()}
        trace['iterations'].append(row)
        if accepted:
            old_cost=cost;parameters=proposal;res,jac=new_res,new_jac;cost=new_cost;damping=max(damping/3,1e-15)
            relative_step=np.linalg.norm(delta)/(1+np.linalg.norm(parameters))
            if relative_step<=tolerance and abs(old_cost-cost)<=tolerance*(1+old_cost):
                converged=True;trace['termination']='Bước tham số tương đối và thay đổi mục tiêu cùng đạt ngưỡng.';break
        else:damping*=10
        if not np.isfinite(damping):break
    trace['last_parameters']=physical(parameters).copy();trace['objective_scaled']=cost
    data['coefficients']=[_dec(v) for v in physical(parameters)]
    if not converged:
        trace['termination']='Hết số vòng mà chưa đạt tiêu chuẩn tối ưu đã chọn.'
        _fail('max_iterations','Lặp phi tuyến chưa đạt điều kiện dừng; giữ tham số cuối và toàn bộ các bước thử. Không báo cực tiểu thành công.')
    def predict(values,return_decimal=False):
        arr=np.asarray(values,float)
        if not np.all(np.isfinite(arr)):raise ValueError('Điểm dự đoán phải hữu hạn.')
        columns=np.column_stack([f(arr.ravel()) for f in funcs[1:]]) if len(funcs)>1 else np.empty((arr.size,0))
        with np.errstate(over='ignore',invalid='ignore'):
            ans=np.zeros(len(columns)) if parameters[0]==0 else np.sign(parameters[0])*np.exp(math.log(abs(parameters[0]))+math.log(yscale)+columns@parameters[1:])
        if not np.all(np.isfinite(ans)):raise ValueError('Mô hình phi tuyến không hữu hạn tại điểm dự đoán.')
        if return_decimal:return [_dec(v) for v in ans]
        return float(ans[0]) if arr.ndim==0 else ans.reshape(arr.shape)
    return predict


def _metrics(data,predict):
    y,w=data['y'],data['weights'];prediction=predict(data['x'],True)
    residual=[_dec(v)-pred for v,pred in zip(y,prediction)]
    squares=[v*v for v in residual];sse=sum(squares,Decimal(0));weighted=sum((_dec(a)*b for a,b in zip(w,squares)),Decimal(0))
    n=len(y);mean=sum(map(_dec,y),Decimal(0))/n;tss=sum(((_dec(v)-mean)**2 for v in y),Decimal(0))
    metrics={'SSE_y':sse,'MSE_y':sse/n,'RMSE_y':(sse/n).sqrt(),'weighted_objective_y':weighted,
             'weighted_RMSE':(weighted/sum(map(_dec,w),Decimal(0))).sqrt(),
             'R_squared':None if not tss else 1-sse/tss,'TSS':tss,'statistical_sigma':None}
    p=len(data['coefficients'])
    if n>p and np.all(w==w[0]) and w[0]>0 and data['transform']=='y':
        metrics['statistical_sigma']=(sse/(n-p)).sqrt()
    if not data['nonlinear']:
        c=data['coefficients'];trans=[_dec(v)-sum((cj*_dec(a) for cj,a in zip(c,row)),Decimal(0)) for v,row in zip(data['z'],data['theta'])]
        metrics['SSE_transformed']=sum((v*v for v in trans),Decimal(0))
        metrics['weighted_objective_transformed']=sum((_dec(a)*b*b for a,b in zip(w,trans)),Decimal(0))
        data['optimality']=[sum((_dec(a)*_dec(b)*c for a,b,c in zip(w,column,trans)),Decimal(0)) for column in data['theta'].T]
        data['transformed_residuals']=trans
        data['system_residual']=[sum((g*cj for g,cj in zip(row,c)),Decimal(0))-b for row,b in zip(data['gram'],data['rhs'])]
    data.update(prediction=prediction,residuals=residual,residual_squares=squares,metrics=metrics)


def _coefficient_display(value):
    fraction=Fraction(value).limit_denominator(10**6)
    with localcontext() as context:
        context.prec=max(80,len(value.as_tuple().digits)+20)
        if abs(value-Decimal(fraction.numerator)/Decimal(fraction.denominator))<Decimal('1e-40'):return fraction
    return value


def _model_tex(data,w):
    coeffs=data.get('coefficients',[]);labels=data.get('labels',[])
    if data.get('nonlinear'):
        a=coeffs[0];tail=[]
        for c,label in zip(coeffs[1:],labels[1:]):
            expr,_=expression(label);tail.append(('+' if c>=0 and tail else '')+w.tex(_coefficient_display(c),True)+r'\,'+sp.latex(expr))
        return rf'g(x)={w.tex(a)}' if not tail else rf'g(x)=({w.tex(a)})\exp\left('+''.join(tail)+r'\right)'
    terms=[]
    for c,label in zip(coeffs,labels):
        if not c:continue
        expr,_=expression(label);body=w.tex(_coefficient_display(abs(c)),True)
        if expr!=1:body+=r'\,\left('+sp.latex(expr)+r'\right)'
        terms.append(('-' if c<0 else '+' if terms else '')+body)
    body=''.join(terms) or '0'
    if data['kind'] in ('Hàm mũ','Lũy thừa','A*b^x'):body=('-' if data.get('sign',1)<0 else '')+r'\exp\left('+body+r'\right)'
    elif data['kind']==LOG_MODEL:body=r'\ln\left('+body+r'\right)'
    elif data['kind'] in ('1/(a+b*x)','x/(a+b*x)'):body=r'\frac{1}{'+body+'}'
    return 'g(x)='+body


def _render(data):
    report=Report('Bình phương tối thiểu — '+str(data['kind']),value=data.get('predict'))
    report.presentation['worked_solution']=data
    builder=ReportBuilder(report,data['input'].get('detail_level','summary'),data['input'].get('display_digits',12));w=builder
    solver_name={'qr':'QR Decimal, trực giao hóa hai lượt','normal_gauss':'Hệ chuẩn — Gauss chọn trụ','svd':'SVD','lm':'Levenberg–Marquardt','levenberg_marquardt':'Levenberg–Marquardt'}
    x=data.get('x');coeffs=data.get('coefficients');failure=data.get('failure')
    with w.group('section','1. Bài toán và lựa chọn'):
        with w.group('columns'):
            with w.group('panel','Mô hình, mục tiêu và bộ giải'):
                w.text('Mô hình: '+data['kind']+'. Thứ tự cơ sở: '+', '.join(data.get('labels',data['input'].get('basis',[])))+'.')
                w.text('Mục tiêu: '+('SSE có trọng số trên thang y, lặp phi tuyến.' if data.get('nonlinear') else 'Tổng bình phương có trọng số trên thang '+data.get('transform','y')+'.'))
                w.text('Bộ giải đã chọn: '+solver_name.get(data.get('solver'),str(data.get('solver')))+'.')
                w.text('Mô hình và thang mục tiêu là lựa chọn của bài; không tự thêm hệ số chặn, giảm bậc hoặc bỏ quan sát.')
            if x is not None:
                with w.group('panel','Quan sát gốc'):
                    with w.details('Dữ liệu, trọng số và dòng gốc'):
                        w.table('Quan sát được giữ nguyên',['i','x_i','y_i','w_i'],((i,a,b,c) for i,(a,b,c) in enumerate(zip(x,data['y'],data['weights']))))
                    w.text(f'{len(x)} quan sát; {data["effective_observations"]} dòng hiệu lực. Các dòng cùng x vẫn là những phép đo riêng.')
    with w.group('section','2. Tiền kiểm và hạng'):
        for check in data['checks']:
            state=check['state'];w.text(('✓ ' if state=='passed' else 'Cảnh báo — ' if state=='warning' else 'Chưa đạt — ')+check['title']+': '+check['detail'],
                                      'success' if state=='passed' else 'warning' if state=='warning' else 'failed')
        rank=data.get('rank')
        if rank:
            w.text(f'Hạng số SVD: {rank["numeric_rank"]}/{rank["parameters"]}; ngưỡng τ={w.number(rank["threshold"])}. '+rank['diagnostic'])
            if data.get('nonlinear'):w.text('Đây là hạng của các cơ sở trong số mũ (kèm cột hằng), không phải chứng nhận hạng Jacobian tại mọi tham số hoặc tính duy nhất của cực tiểu phi tuyến.')
            if rank.get('resolved_rank')==rank['parameters']:w.text('✓ Bộ giải đã tìm được đủ các cột độc lập trong độ chính xác làm việc.','success')
            with w.details('Giá trị kỳ dị và độ nhạy'):
                w.table('Chẩn đoán SVD',['j','σ_j'],enumerate(rank['singular_values']))
                w.text('Số điều kiện của thiết kế đổi thang: '+str(rank['condition_scaled'])+'. Đổi thang chỉ hỗ trợ số học, không phải cận sai số dữ liệu.')
        for warning in data['warnings']:w.text(warning,'warning')
    if data.get('theta') is not None:
        with w.group('columns'):
            with w.group('section','3. Bảng cơ sở, biến đổi và các tổng'):
                w.text('Các cơ sở tạo số mũ; y là quan sát gốc, không giải hệ tuyến tính Φc=y.' if data['nonlinear'] else 'Biến mục tiêu dùng để giải: z = '+data['transform']+'.')
                with w.details('Bảng cơ sở đầy đủ' if data['nonlinear'] else 'Ma trận thiết kế đầy đủ Φ'):
                    w.table('Giá trị cơ sở trong số mũ' if data['nonlinear'] else 'Φ_ij = φ_j(x_i)',
                            ['i','x_i','y_i' if data['nonlinear'] else 'z_i']+data['labels'],
                            ([i,a,z,*row] for i,(a,z,row) in enumerate(zip(data['x'],data['z'],data['theta']))))
                if data['nonlinear']:
                    w.text('Cột 1 dùng mô tả biên độ/log của biên độ khi khởi tạo phù hợp. Các cột còn lại nhân các hệ số b_j trong số mũ. Tham số được cập nhật bằng LM, không giải hệ chuẩn của bảng cơ sở này.')
                elif data['labels']==['1','x']:
                    weighted=any(v!=1 for v in data['weights'])
                    if weighted:
                        rows=[[i,_dec(v),_dec(v)*_dec(a),_dec(v)*_dec(b),_dec(v)*_dec(a)**2,_dec(v)*_dec(a)*_dec(b)]
                              for i,(a,b,v) in enumerate(zip(data['x'],data['z'],data['weights']))]
                        rows.append(['Tổng']+[sum((r[j] for r in rows),Decimal(0)) for j in range(1,6)])
                        w.table('Bảng tổng có trọng số trên thang đang khớp',['i','w_i','w_i x_i','w_i z_i','w_i x_i²','w_i x_i z_i'],rows)
                    else:
                        rows=[[i,a,b,_dec(a)**2,_dec(a)*_dec(b)] for i,(a,b) in enumerate(zip(data['x'],data['z']))]
                        rows.append(['Tổng',sum(map(_dec,data['x']),Decimal(0)),sum(map(_dec,data['z']),Decimal(0)),sum((_dec(a)**2 for a in data['x']),Decimal(0)),sum((_dec(a)*_dec(b) for a,b in zip(data['x'],data['z'])),Decimal(0))])
                        w.table('Bảng tổng đường thẳng trên thang đang khớp',['i','x_i','z_i','x_i²','x_i z_i'],rows)
                else:w.text('Các tổng G_jk và b_j lấy đúng các cột cơ sở đã công bố, có trọng số.')
            with w.group('section','4. Mô hình và mục tiêu phi tuyến' if data['nonlinear'] else '4. Hệ chuẩn và hệ thực sự được giải'):
                if data['nonlinear']:
                    w.formula(r'g_i(p)=A\exp\left(\sum_{j=1}^{m}b_j\varphi_j(x_i)\right)',
                              'g_i(p)=A*exp(sum_j b_j*phi_j(x_i)); các phi_j theo thứ tự đã công bố.')
                    w.formula(r'F(p)=\sum_i w_i\left(g_i(p)-y_i\right)^2',
                              'Mục tiêu F(p)=sum_i w_i*(g_i(p)−y_i)^2 trên thang y gốc.')
                    w.text('Bài này phi tuyến theo tham số. Mỗi bước LM lập lại Jacobian và giải hệ bình phương tối thiểu tăng cường bên dưới; không dùng hệ chuẩn Gc=b của mô hình tuyến tính theo cơ sở.')
                else:
                    w.formula(r'\Phi c\approx z,\qquad \min_c\|\sqrt{W}(\Phi c-z)\|_2^2',
                              'Mô hình Φc≈z; cực tiểu hóa ||sqrt(W)(Φc−z)||², không ép khớp đúng mọi quan sát.')
                    w.formula(r'G=\Phi^TW\Phi,\quad b=\Phi^TWz,\quad Gc=b','G=Phi^T W Phi; b=Phi^T W z; hệ chuẩn Gc=b.')
                    if data.get('gram') is not None:
                        w.table('Hệ chuẩn và vế phải',['j']+[f'c_{j}' for j in range(len(data['labels']))]+['b_j'],([i,*row,b] for i,(row,b) in enumerate(zip(data['gram'],data['rhs']))))
                        for j,(row,b) in enumerate(zip(data['gram'],data['rhs'])):
                            if len(row)<=5:
                                eq=''.join(('+' if k else '')+'('+w.tex(v)+')'+rf'c_{{{k}}}' for k,v in enumerate(row))+'='+w.tex(b)
                                w.formula(eq,'Phương trình '+str(j)+': '+' + '.join('('+w.number(v)+')*c_'+str(k) for k,v in enumerate(row))+' = '+w.number(b))
                    w.text('Hệ chuẩn chỉ là đối chiếu lý thuyết khi bộ giải được chọn là QR/SVD. Trace phía dưới ghi đúng thuật toán tạo ra nghiệm.')
    trace=data.get('solver_trace')
    if trace:
        with w.group('section','5. Trace bộ giải thực tế'):
            kind=trace['kind'];w.text(solver_name.get(kind,kind)+'.')
            if kind=='qr':
                w.formula(r'B=\sqrt{W/w_{\max}}\,\Phi,\quad \widetilde z=\sqrt{W/w_{\max}}\,z',
                          'B=sqrt(W/max(w))·Φ; z̃=sqrt(W/max(w))·z. Cả ma trận và vế phải đều nhân cùng căn trọng số.')
                w.formula(r'B=QR,\qquad Rc=Q^T\widetilde z',
                          'Trực giao hóa QR hai lượt trên B, rồi thế ngược R c = Qᵀ z̃; z̃ là mục tiêu đã nhân trọng số.')
                for step in trace['steps']:
                    with w.details(f'Cột QR {step["column"]}'):
                        w.text('Chuẩn cột ban đầu '+w.number(step['original_norm'])+'; chuẩn còn lại '+w.number(step['remaining_norm'])+'; ngưỡng '+w.number(step['threshold'])+'.')
                        w.table('Các lần chiếu đã thực hiện',['lượt','cột chiếu','hệ số chiếu'],((a['pass'],a['onto'],a['projection']) for a in step['projections']))
                if 'R' in trace:
                    w.table('Hệ tam giác R c = Qᵀ z̃',[f'c_{i}' for i in range(len(coeffs))]+['Qᵀ z̃'],([*row,z] for row,z in zip(trace['R'],trace['qt_target'])))
                    with w.details('Các cột Q thực sự dùng'):w.table('Q',['i']+[f'q_{j}' for j in range(len(trace['Q']))],([i]+[c[i] for c in trace['Q']] for i in range(len(data['x']))))
            elif kind=='normal_gauss':
                for step in trace['steps']:
                    with w.details(f'Cột khử {step["column"]} — pivot hàng {step["pivot_row"]}'):
                        w.text('Pivot='+w.number(step['pivot'])+'; ngưỡng='+w.number(step['threshold'])+'; '+('đã đổi hàng.' if step['swapped'] else 'giữ hàng.'))
                        for elimination in step['eliminations']:
                            w.text(f'R_{elimination["row"]} ← R_{elimination["row"]} − ({w.number(elimination["multiplier"])})R_{step["column"]}.')
                        if step.get('matrix_after'):w.table('Hệ sau bước khử',[f'c_{i}' for i in range(len(data['labels']))]+['b'],step['matrix_after'])
            elif kind=='svd':
                w.table('Giá trị kỳ dị thực sự dùng',['j','σ_j'],enumerate(trace['singular_values']))
                w.text(f'Hạng số {trace["rank"]}; τ={w.number(trace["threshold"])}; '+('đã chọn nghiệm chuẩn nhỏ nhất.' if trace['minimum_norm'] else 'yêu cầu nghiệm tham số duy nhất.'))
            elif kind=='levenberg_marquardt':
                w.text(trace['initial_rule']+' Thang nội bộ y_scale='+w.number(trace['yscale'])+'. Ngưỡng='+w.number(trace['tolerance'])+'.')
                w.text('Quy ước nội bộ ρ_i=sqrt(w_i/max(w))*(g_i−y_i)/y_scale, J là đạo hàm của ρ theo tham số nội bộ a=A/y_scale và các b_j. Vì vậy ρ khác dấu và đơn vị với phần dư y_i−g_i ở bảng đánh giá.')
                w.formula(r'\min_\delta\left\{\left\|J\delta+\rho\right\|_2^2+\lambda\left\|D\delta\right\|_2^2\right\}',
                          'Bước LM giải min ||[J; sqrt(lambda)D] delta − [−rho; 0]||² bằng SVD của hệ tăng cường; D là chuẩn từng cột Jacobian (thay chuẩn 0 bằng 1).')
                w.formula(r'p_{\rm thu}=p_{\rm cu}+\delta',
                          'p_thử=p_cũ+delta trong thang nội bộ a=A/y_scale; b_j giữ nguyên. Nhận bước chỉ khi mục tiêu giảm.')
                headers=['vòng']+['A']+[f'b_{j+1}' for j in range(len(data['labels'])-1)]+['F thử','λ','||bước||','quyết định']
                rows=[[0,*trace['initial_parameters'],None,None,None,'Khởi tạo']]
                rows.extend([a['iteration'],*a['proposed_parameters'],a['sse_proposed'],a['damping'],a['step_norm'],'Nhận' if a['accepted'] else 'Từ chối'] for a in trace['iterations'])
                w.table('Tham số và mục tiêu qua từng bước thử',headers,rows,text_columns=(len(headers)-1,))
                for row in trace['iterations']:
                    with w.details(f'Bước thử {row["iteration"]} — '+('nhận' if row['accepted'] else 'tăng damping, thử tiếp')):
                        w.text('Tham số cũ: '+str(row['old_parameters'].tolist())+'; đề xuất: '+str(row['proposed_parameters'].tolist())+'.')
                        w.text('F cũ='+w.number(row['sse_before'])+'; F thử='+w.number(row['sse_proposed'])+'; ||gradient||∞ nội bộ='+w.number(row['gradient_norm'])+'.')
                        w.table('Bước tham số trong thang nội bộ',['j','D_jj','delta_j'],((j,a,b) for j,(a,b) in enumerate(zip(row['jacobian_column_norms'],row['step_internal']))))
                        w.table('Jacobian nội bộ đã dùng',[f'p_{j}' for j in range(row['jacobian'].shape[1])],row['jacobian'])
                w.text('Lý do dừng: '+trace.get('termination','chưa có kết luận')+'.')
            if trace.get('back_substitution'):
                with w.details('Thế ngược từng tham số'):
                    w.table('Các phép chia trong thế ngược',['j','vế phải','tổng đã biết','pivot','c_j'],((s['row'],s['rhs'],s['tail'],s['pivot'],s['value']) for s in trace['back_substitution']))
    if data.get('metrics'):
        with w.group('section','6. Dự đoán, phần dư và kiểm tra'):
            w.text('Quy ước thống nhất r_i = y_i − g(x_i), giữ đúng đơn vị dữ liệu gốc.')
            with w.details('Đối chiếu từng quan sát'):
                w.table('Dự đoán và sai lệch',['i','x_i','y_i','w_i','g(x_i)','r_i','r_i²'],((i,x,y,z,p,r,s) for i,(x,y,z,p,r,s) in enumerate(zip(data['x'],data['y'],data['weights'],data['prediction'],data['residuals'],data['residual_squares']))))
            metrics=data['metrics']
            w.table('Các chỉ số có định nghĩa rõ',['đại lượng','giá trị','ý nghĩa'],
                    [('SSE_y',metrics['SSE_y'],'sum(r_i²)'),('MSE_y',metrics['MSE_y'],'SSE_y/N'),('RMSE_y',metrics['RMSE_y'],'sqrt(SSE_y/N)'),
                     ('J_y có trọng số',metrics['weighted_objective_y'],'sum(w_i*r_i²)'),('RMSE có trọng số',metrics['weighted_RMSE'],'sqrt(J_y/sum(w_i))'),
                     ('R² không trọng số',metrics['R_squared'],'1−SSE_y/TSS; không áp dụng nếu y hằng'),
                     ('sigma thống kê',metrics['statistical_sigma'],'sqrt(SSE_y/(N−p)); chỉ diễn giải theo giả thiết thống kê')],text_columns=(0,2))
            if data['transform']!='y' and not data['nonlinear']:
                w.text('Mục tiêu đã tối thiểu hóa ở thang '+data['transform']+': J='+w.number(metrics['weighted_objective_transformed'])+'; SSE không trọng số trên thang đó='+w.number(metrics['SSE_transformed'])+'. Không đồng nhất với SSE_y.','warning')
            if data.get('optimality') is not None:
                with w.details('Thế lại hệ và trực giao phần dư'):
                    w.table('Kiểm tra hệ và tối ưu',['j','(G c−b)_j','(Φᵀ W r_thang_khớp)_j'],((i,a,b) for i,(a,b) in enumerate(zip(data['system_residual'],data['optimality']))))
                w.text('Các phần dư hệ/điều kiện tối ưu được tính trên đúng ma trận và thang đã giải, không phải cận sai số dự đoán.')
    with w.group('section','7. Kết luận',keep_together=True):
        if failure:
            w.text(f'Chưa có mô hình đạt yêu cầu của lượt chạy. {failure["phase"]}: {failure["message"]}','failed')
            w.text('Giữ các bước đã tính; người dùng chọn lại mô hình, miền, bộ giải hoặc cách xử lý thiếu hạng. Không tự đổi bài toán.')
        else:
            w.formula(_model_tex(data,w),'Mô hình với thứ tự hệ số đã công bố: ['+', '.join(w.number(_coefficient_display(v),True) for v in data['coefficients'])+'].')
            w.table('Tham số theo đúng cơ sở',['tên/cơ sở','hệ số'],zip(['A']+data['labels'][1:] if data['nonlinear'] else data['labels'],[_coefficient_display(v) for v in coeffs]),exact=True,text_columns=(0,))
            if data['kind'] in ('Hàm mũ','Lũy thừa','A*b^x'):
                amplitude=exp_parameter(float(coeffs[0]),data['sign']);w.text('Khôi phục A = '+str(amplitude)+'; các hệ số mũ theo thứ tự cơ sở ở trên.')
                if data['kind']=='A*b^x':w.text('Cơ số B = exp(c₁) = '+str(exp_parameter(float(coeffs[1])))+' > 0.')
            if data['kind']=='x/(a+b*x)':w.text('Ánh xạ về đề: a=c₁, b=c₀; c₀ là hệ số chặn của biến 1/x.')
            if data['nonlinear']:w.text('Đạt điều kiện dừng của phép tối ưu đã chạy; kết quả phụ thuộc tham số đầu, không có chứng nhận cực tiểu toàn cục.','warning')
            else:w.text('Đã giải bài toán bình phương tối thiểu tuyến tính trên thang '+data['transform']+' bằng bộ giải công bố; tham số không thay đổi chỉ để ép qua mọi điểm.')
            if data.get('target') is not None:w.text('Dự đoán tại x='+w.number(data['target'])+': '+w.number(data.get('target_prediction'))+'.')
            w.text('RMSE/R² đánh giá độ khớp trên mẫu; không phải cận sai số tại từng điểm hay bảo đảm cho dữ liệu mới.','muted')
    if not failure:
        report.scatter=(data['x'],data['y']);grid=np.linspace(min(data['x']),max(data['x']),400)
        try:report.curves=[(grid,data['predict'](grid),'Mô hình đã khớp')]
        except (ValueError,ArithmeticError):report.lines.append('Không vẽ được toàn miền giữa các quan sát; giữ mô hình và kết quả tại dữ liệu.')
    w.finish();return report


def solve_least_squares(x,y,kind=LINEAR,basis=None,weights=None,*,solver=None,rank_policy='unique',
                        initial=None,max_iter=100,tolerance=1e-10,target=None,detail_level='summary',display_digits=12):
    """Luôn trả Report kể cả lỗi; giữ callable g(x) khi bài khớp thành công."""
    if solver is None:solver='lm' if kind in ('Hàm mũ — SSE thang y','Lũy thừa — SSE thang y') else 'qr'
    solver_alias={'QR':'qr','Hệ chuẩn — Gauss':'normal_gauss','Gauss':'normal_gauss','SVD':'svd','Levenberg–Marquardt':'lm'}
    solver=solver_alias.get(solver,solver)
    rank_policy={'Nghiệm duy nhất':'unique','Chuẩn nhỏ nhất':'minimum_norm'}.get(rank_policy,rank_policy)
    detail_level={'Tổng hợp':'summary','Chi tiết':'detailed'}.get(detail_level,detail_level)
    basis=(['x'] if kind.startswith('Hàm mũ') else ['1','x']) if basis is None else basis
    config={'x':deepcopy(x),'y':deepcopy(y),'kind':kind,'basis':list(basis),'weights':deepcopy(weights),
            'solver':solver,'rank_policy':rank_policy,'initial':deepcopy(initial),'max_iter':max_iter,
            'tolerance':tolerance,'target':target,'detail_level':detail_level,'display_digits':display_digits}
    data={'kind':kind,'input':config,'solver':solver,'phase':'Đọc cấu hình','status':'pending','failure':None,
          'checks':[],'warnings':[],'predict':None}
    try:
        if solver not in ('qr','normal_gauss','svd','lm'):_fail('invalid_solver','Chọn QR, hệ chuẩn–Gauss, SVD hoặc LM cho bài phi tuyến; không tự thay bộ giải.')
        if rank_policy not in ('unique','minimum_norm'):_fail('invalid_rank_policy','Chọn yêu cầu nghiệm duy nhất hoặc nghiệm chuẩn nhỏ nhất.')
        if rank_policy=='minimum_norm' and solver!='svd':_fail('invalid_rank_policy','Nghiệm chuẩn nhỏ nhất trong luồng này cần chọn SVD; không tự đổi bộ giải.')
        if not isinstance(display_digits,(int,np.integer)) or isinstance(display_digits,bool) or not 0<=display_digits<=50:_fail('invalid_input','Số chữ số hiển thị phải nguyên từ 0 đến 50.')
        if detail_level not in ('summary','detailed'):_fail('invalid_input','Mức trình bày phải là Tổng hợp/Chi tiết.')
        _,_,_,funcs=_prepare(data,x,y,kind,basis,weights)
        nonzero=[_dec(v).adjusted() for v in np.r_[data['theta'].ravel(),data['z'],data['weights']] if v]
        data['precision']=max(80,(max(nonzero)-min(nonzero)+80) if nonzero else 80,8*len(data['labels'])+40)
        with localcontext() as context:
            context.prec=data['precision'];columns,transformed=_weighted_design(data)
            data['phase']='Giải theo bộ giải đã chọn'
            if data['nonlinear']:
                if solver!='lm':_fail('invalid_solver','Mục tiêu SSE thang y của mũ/lũy thừa cần chọn lặp phi tuyến LM trong luồng này; không tự thay QR/Gauss/SVD bằng thuật toán khác.')
                if not isinstance(max_iter,(int,np.integer)) or isinstance(max_iter,bool) or max_iter<1:_fail('invalid_input','Số vòng tối đa phải là số nguyên dương.')
                if not np.isfinite(tolerance) or tolerance<=0:_fail('invalid_input','Ngưỡng dừng phi tuyến phải dương và hữu hạn.')
                if rank_policy!='unique':_fail('invalid_rank_policy','Chế độ chuẩn nhỏ nhất tuyến tính không áp dụng cho phép tối ưu phi tuyến này.')
                if data['rank']['numeric_rank']<len(data['labels']):
                    _fail('rank_deficient','Cơ sở trong số mũ kèm cột hằng thiếu hạng số; không xác định duy nhất các tham số biên độ/số mũ trong độ chính xác đang dùng. Kiểm tra cơ sở trùng (không thêm 1 vào phần mũ đã có A) và số quan sát hiệu lực; không tự bỏ tham số.')
                data['solver']='levenberg_marquardt';predict=_nonlinear(data,funcs,initial,max_iter,tolerance)
            else:
                if solver=='lm':_fail('invalid_solver','Mô hình tuyến tính theo tham số dùng QR, Gauss hoặc SVD; không chọn LM cho bước giải trực tiếp này.')
                coefficients=_qr(data,columns,transformed) if solver=='qr' else _gauss(data) if solver=='normal_gauss' else _svd(data,columns,transformed,rank_policy=='minimum_norm')
                data['coefficients']=coefficients
                predict=_linear_predictor(data,coefficients,funcs)
            data['phase']='Dự đoán và kiểm tra trên dữ liệu gốc';_metrics(data,predict)
            if target is not None:
                if not np.isfinite(float(target)):_fail('invalid_target','Điểm dự đoán phải hữu hạn.')
                try:data['target_prediction']=predict(float(target));data['target']=float(target)
                except ValueError as exc:
                    data['warnings'].append('Điểm dự đoán mới không thuộc miền mô hình: '+str(exc))
            data['predict']=predict;data['status']='nonlinear_stationary' if data['nonlinear'] else 'minimum_norm_fit' if data['rank'].get('resolved_rank',len(data['labels']))<len(data['labels']) else 'unique_fit'
    except _FitFailure as exc:
        data['status']=exc.status;data['failure']={'phase':data['phase'],'message':str(exc)}
        _check(data,data['phase'],'failed',str(exc))
    except (ArithmeticError,ValueError,TypeError,np.linalg.LinAlgError) as exc:
        data['status']='numerical_failure';data['failure']={'phase':data['phase'],'message':str(exc)}
        _check(data,data['phase'],'failed',str(exc))
    return _render(data)
