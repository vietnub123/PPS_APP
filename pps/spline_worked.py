"""Spline và lời giải theo tài liệu real: cùng một bộ hệ số, đúng bộ giải.

Các bài thông thường được giải bằng số hữu tỷ của số thập phân đã đọc.
Trace khử/truy hồi chính là phép tính tạo hệ số, không giải lại để trang trí.
"""
from copy import deepcopy
from fractions import Fraction
import math

import numpy as np
from scipy.interpolate import CubicSpline, PPoly

from .common import Report, points
from .worked_report import ReportBuilder


def _q(value):
    if isinstance(value,Fraction):return value
    if not np.isfinite(float(value)):raise ValueError('Giá trị phải hữu hạn.')
    return Fraction(str(float(value)))


def _integer(value,label,minimum=0):
    if isinstance(value,(bool,np.bool_)) or not isinstance(value,(int,np.integer)) or value<minimum:
        raise ValueError(f'{label} phải là số nguyên từ {minimum} trở lên.')
    return int(value)


def _piece(coefficients,u,order=0):
    total=Fraction(0)
    for k in range(len(coefficients)-1,order-1,-1):
        total=total*u+coefficients[k]*(math.factorial(k)//math.factorial(k-order))
    return total


def _magnitude(coefficients,u,order=0):
    return sum((abs(c)*(math.factorial(k)//math.factorial(k-order))*abs(u)**(k-order)
                for k,c in enumerate(coefficients) if k>=order),Fraction(0))


def _check(data,title,value,scale=1,explanation=''):
    tolerance=Fraction(1,10**10)*abs(_q(scale))
    passed=abs(value)<=tolerance
    data['checks'].append({'title':title,'value':value,'tolerance':tolerance,'passed':passed,'explanation':explanation})
    return passed


def _thomas(lower,diagonal,upper,rhs):
    n=len(diagonal);b=list(diagonal);d=list(rhs);forward=[]
    for i in range(n):
        old_b,old_d=b[i],d[i]
        if i:
            if not b[i-1]:raise ValueError(f'Pivot Thomas bằng 0 ở hàng {i-1}; cần chọn bộ giải khác.')
            factor=lower[i]/b[i-1]
            b[i]-=factor*upper[i-1];d[i]-=factor*d[i-1]
        else:factor=Fraction(0)
        if not b[i]:raise ValueError(f'Pivot Thomas bằng 0 ở hàng {i}; không tự đổi bộ giải.')
        forward.append({'i':i,'lower':lower[i],'previous_pivot':b[i-1] if i else None,
                        'factor':factor,'original_diagonal':old_b,'pivot':b[i],
                        'original_rhs':old_d,'reduced_rhs':d[i],
                        'c_prime':upper[i]/b[i] if i<n-1 else Fraction(0),'d_prime':d[i]/b[i]})
    values=[Fraction(0)]*n;back=[]
    for i in range(n-1,-1,-1):
        contribution=upper[i]*values[i+1] if i<n-1 else Fraction(0)
        values[i]=(d[i]-contribution)/b[i]
        back.append({'i':i,'rhs':d[i],'upper_contribution':contribution,'pivot':b[i],'value':values[i]})
    return values,{'kind':'Thomas hữu tỷ','forward':forward,'backward':back}


def _gauss(matrix,rhs):
    """Khử có chọn trụ trên mọi hàng; chấp nhận thêm điều kiện tương thích."""
    if not matrix:raise ValueError('Chưa có hệ phương trình.')
    a=[list(row)+[value] for row,value in zip(matrix,rhs)];m=len(a);n=len(matrix[0]);rank=0;pivots=[];steps=[]
    for column in range(n):
        if rank>=m:break
        selected=max(range(rank,m),key=lambda row:abs(a[row][column]))
        if not a[selected][column]:continue
        a[rank],a[selected]=a[selected],a[rank]
        pivot=a[rank][column];eliminations=[]
        for i in range(rank+1,m):
            if not a[i][column]:continue
            factor=a[i][column]/pivot
            for j in range(column,n+1):a[i][j]-=factor*a[rank][j]
            eliminations.append((i,factor))
        steps.append({'step':rank,'column':column,'selected_row':selected,'pivot':pivot,'eliminations':eliminations})
        pivots.append((rank,column));rank+=1
    for row in a:
        if not any(row[:n]) and row[n]:raise ValueError('Các điều kiện spline không tương thích: hạng ma trận mở rộng lớn hơn hạng hệ số.')
    if rank<n:raise ValueError(f'Chưa xác định spline duy nhất: hạng hệ số {rank} nhỏ hơn số ẩn {n}. Cần thêm điều kiện độc lập.')
    values=[Fraction(0)]*n;back=[]
    for row,column in reversed(pivots):
        contribution=sum((a[row][j]*values[j] for j in range(column+1,n)),Fraction(0))
        values[column]=(a[row][n]-contribution)/a[row][column]
        back.append({'i':column,'rhs':a[row][n],'upper_contribution':contribution,'pivot':a[row][column],'value':values[column]})
    return values,{'kind':'Gauss chọn trụ hữu tỷ','forward':steps,'backward':back,'rank':rank,'unknowns':n,'equations':m}


def _moments(data,x,y,h,slopes,kind,left,right,orders,solver):
    n=len(x)
    regular=kind not in ('Cubic tuần hoàn','Cubic not-a-knot')
    if regular:
        if kind=='Cubic tự nhiên':orders=(2,2);left=right=0
        elif kind=='Cubic đạo hàm bậc hai':orders=(2,2)
        elif kind=='Cubic kẹp':orders=(1,1)
        elif kind not in ('Cubic hỗn hợp','Cubic biên hỗn hợp'):raise ValueError('Loại spline bậc 3 không được hỗ trợ.')
        if len(orders)!=2 or any(v not in (1,2) for v in orders):raise ValueError('Biên hỗn hợp cần mỗi cấp là 1 hoặc 2.')
        if left is None or right is None:raise ValueError('Thiếu giá trị điều kiện biên trái/phải; không tự gán độ dốc hoặc độ cong bằng 0.')
        left,right=_q(left),_q(right);data['boundary_conditions']=[('trái',orders[0],left),('phải',orders[1],right)]
        lower=[Fraction(0)]*n;diagonal=[Fraction(0)]*n;upper=[Fraction(0)]*n;rhs=[Fraction(0)]*n
        for i in range(1,n-1):lower[i]=h[i-1];diagonal[i]=2*(h[i-1]+h[i]);upper[i]=h[i];rhs[i]=6*(slopes[i]-slopes[i-1])
        if orders[0]==2:diagonal[0]=1;rhs[0]=left
        else:diagonal[0]=2*h[0];upper[0]=h[0];rhs[0]=6*(slopes[0]-left)
        if orders[1]==2:diagonal[-1]=1;rhs[-1]=right
        else:lower[-1]=h[-1];diagonal[-1]=2*h[-1];rhs[-1]=6*(right-slopes[-1])
        matrix=None
        if n<=80 or solver=='Gauss':
            matrix=[[Fraction(0)]*n for _ in range(n)]
            for i in range(n):
                matrix[i][i]=diagonal[i]
                if i:matrix[i][i-1]=lower[i]
                if i<n-1:matrix[i][i+1]=upper[i]
        data['system']={'matrix':matrix if n<=80 else None,'rhs':rhs,'variable':'M','lower':lower,'diagonal':diagonal,'upper':upper}
        if solver=='Gauss':
            moments,trace=_gauss(matrix,rhs)
        else:moments,trace=_thomas(lower,diagonal,upper,rhs)
        data['moments']=moments;data['solver']=trace
        for i in range(n):
            terms=[diagonal[i]*moments[i]]
            if i:terms.append(lower[i]*moments[i-1])
            if i<n-1:terms.append(upper[i]*moments[i+1])
            _check(data,f'Phương trình moment hàng {i}',sum(terms,Fraction(0))-rhs[i],max([abs(rhs[i])]+list(map(abs,terms))))
        return [[y[i],slopes[i]-h[i]*(2*moments[i]+moments[i+1])/6,moments[i]/2,
                 (moments[i+1]-moments[i])/(6*h[i])] for i in range(n-1)]
    if n>80 and solver=='auto':
        if kind=='Cubic tuần hoàn':
            if y[0]!=y[-1]:raise ValueError('Biên tuần hoàn cần hai tung độ đầu/cuối bằng nhau; không tự sửa dữ liệu.')
            bc='periodic';data['boundary_conditions']=[('chu kỳ',0,0),('chu kỳ',1,0),('chu kỳ',2,0)]
        else:bc='not-a-knot';data['boundary_conditions']=[('not-a-knot',3,0)]
        core=CubicSpline(np.array(list(map(float,x))),np.array(list(map(float,y))),bc_type=bc,extrapolate=False)
        moments=list(map(_q,core(np.array(list(map(float,x))),2)))
        rows=[];rhs=[]
        if bc=='periodic':
            rows.append({0:Fraction(1),n-1:Fraction(-1)});rhs.append(Fraction(0))
        else:
            rows.append({0:-1/h[0],1:1/h[0]+1/h[1],2:-1/h[1]});rhs.append(Fraction(0))
        for i in range(1,n-1):rows.append({i-1:h[i-1],i:2*(h[i-1]+h[i]),i+1:h[i]});rhs.append(6*(slopes[i]-slopes[i-1]))
        if bc=='periodic':
            row={}
            for j,value in ((0,2*h[0]),(1,h[0]),(n-2,h[-1]),(n-1,2*h[-1])):row[j]=row.get(j,Fraction(0))+value
            rows.append(row);rhs.append(6*(slopes[0]-slopes[-1]))
        else:rows.append({n-3:-1/h[-2],n-2:1/h[-2]+1/h[-1],n-1:-1/h[-1]});rhs.append(Fraction(0))
        data['system']={'matrix':None,'sparse_rows':rows,'rhs':rhs,'variable':'M'}
        data['moments']=moments;data['solver']={'kind':'SciPy CubicSpline — '+bc,'forward':[],'backward':[],
               'note':'Bảng lớn: bộ giải thư viện theo đúng biên. Không tạo trace Thomas hoặc Gauss giả.'}
        for i,(row,value) in enumerate(zip(rows,rhs)):
            terms=[a*moments[j] for j,a in row.items()]
            system_scale=sum(map(abs,row.values()),Fraction(0))*max(map(abs,moments))
            _check(data,f'Phương trình moment hàng {i}',sum(terms,Fraction(0))-value,max([abs(value),system_scale]+list(map(abs,terms))))
        return [[y[i],slopes[i]-h[i]*(2*moments[i]+moments[i+1])/6,moments[i]/2,
                 (moments[i+1]-moments[i])/(6*h[i])] for i in range(n-1)]
    matrix=[[Fraction(0)]*n for _ in range(n)];rhs=[Fraction(0)]*n
    for i in range(1,n-1):
        matrix[i][i-1]=h[i-1];matrix[i][i]=2*(h[i-1]+h[i]);matrix[i][i+1]=h[i]
        rhs[i]=6*(slopes[i]-slopes[i-1])
    if kind=='Cubic tuần hoàn':
        if n<3:raise ValueError('Biên tuần hoàn theo hệ trong tài liệu cần ít nhất 3 mốc; hai mốc phải chọn quy ước riêng.')
        if y[0]!=y[-1]:raise ValueError('Biên tuần hoàn cần hai tung độ đầu/cuối bằng nhau; không tự sửa dữ liệu.')
        matrix[0][0]=1;matrix[0][-1]=-1
        for j,value in ((0,2*h[0]),(1,h[0]),(n-2,h[-1]),(n-1,2*h[-1])):matrix[-1][j]+=value
        rhs[-1]=6*(slopes[0]-slopes[-1]);data['boundary_conditions']=[('chu kỳ',0,0),('chu kỳ',1,0),('chu kỳ',2,0)]
    elif kind=='Cubic not-a-knot':
        if n<4:raise ValueError('Not-a-knot chuẩn cần ít nhất 4 mốc; không tự dùng quy ước đặc biệt cho bảng ngắn.')
        matrix[0][0]=-1/h[0];matrix[0][1]=1/h[0]+1/h[1];matrix[0][2]=-1/h[1]
        matrix[-1][-3]=-1/h[-2];matrix[-1][-2]=1/h[-2]+1/h[-1];matrix[-1][-1]=-1/h[-1]
        data['boundary_conditions']=[('not-a-knot',3,0)]
    else:
        if kind=='Cubic tự nhiên':orders=(2,2);left=right=0
        elif kind=='Cubic đạo hàm bậc hai':orders=(2,2)
        elif kind=='Cubic kẹp':orders=(1,1)
        elif kind not in ('Cubic hỗn hợp','Cubic biên hỗn hợp'):raise ValueError('Loại spline bậc 3 không được hỗ trợ.')
        if len(orders)!=2 or any(v not in (1,2) for v in orders):raise ValueError('Biên hỗn hợp cần mỗi cấp là 1 hoặc 2.')
        if left is None or right is None:raise ValueError('Thiếu giá trị điều kiện biên trái/phải; không tự gán độ dốc hoặc độ cong bằng 0.')
        left,right=_q(left),_q(right);data['boundary_conditions']=[('trái',orders[0],left),('phải',orders[1],right)]
        if orders[0]==2:matrix[0][0]=1;rhs[0]=left
        else:matrix[0][0]=2*h[0];matrix[0][1]=h[0];rhs[0]=6*(slopes[0]-left)
        if orders[1]==2:matrix[-1][-1]=1;rhs[-1]=right
        else:matrix[-1][-2]=h[-1];matrix[-1][-1]=2*h[-1];rhs[-1]=6*(right-slopes[-1])
    regular=kind not in ('Cubic tuần hoàn','Cubic not-a-knot')
    data['system']={'matrix':matrix,'rhs':rhs,'variable':'M'}
    if solver=='Thomas' and not regular:raise ValueError('Hệ tuần hoàn/not-a-knot không phải ba đường chéo thông thường; chọn Gauss hoặc tự động, không bỏ hệ số ngoài băng.')
    if regular and solver!='Gauss':
        lower=[matrix[i][i-1] if i else Fraction(0) for i in range(n)]
        diagonal=[matrix[i][i] for i in range(n)]
        upper=[matrix[i][i+1] if i<n-1 else Fraction(0) for i in range(n)]
        moments,trace=_thomas(lower,diagonal,upper,rhs)
        data['system'].update(lower=lower,diagonal=diagonal,upper=upper)
    elif n<=80 or solver=='Gauss':moments,trace=_gauss(matrix,rhs)
    else:
        bc='periodic' if kind=='Cubic tuần hoàn' else 'not-a-knot'
        core=CubicSpline(np.array(list(map(float,x))),np.array(list(map(float,y))),bc_type=bc,extrapolate=False)
        moments=list(map(_q,core(np.array(list(map(float,x))),2)))
        trace={'kind':'SciPy CubicSpline — '+bc,'forward':[],'backward':[],
               'note':'Bảng lớn: bộ giải thư viện theo đúng biên. Không tạo trace Thomas hoặc Gauss giả.'}
    data['moments']=moments;data['solver']=trace
    for i,row in enumerate(matrix):
        residual=sum((a*v for a,v in zip(row,moments)),Fraction(0))-rhs[i]
        _check(data,f'Phương trình moment hàng {i}',residual,max([abs(rhs[i])]+[abs(a*v) for a,v in zip(row,moments)]))
    return [[y[i],slopes[i]-h[i]*(2*moments[i]+moments[i+1])/6,moments[i]/2,
             (moments[i+1]-moments[i])/(6*h[i])] for i in range(n-1)]


def _boundary_equations(x,y,h,degree,conditions):
    n=len(h);size=n*(degree+1);matrix=[];rhs=[];labels=[]
    def row(segment,u,order):
        values=[Fraction(0)]*size
        for power in range(order,degree+1):
            values[segment*(degree+1)+power]=Fraction(math.factorial(power),math.factorial(power-order))*u**(power-order)
        return values
    for i in range(n):
        matrix.extend([row(i,Fraction(0),0),row(i,h[i],0)]);rhs.extend([y[i],y[i+1]])
        labels.extend([f'S_{i}(x_{i})=y_{i}',f'S_{i}(x_{i+1})=y_{i+1}'])
    for i in range(n-1):
        for order in range(1,degree):
            a=row(i,h[i],order);b=row(i+1,Fraction(0),order)
            matrix.append([v-w for v,w in zip(a,b)]);rhs.append(Fraction(0));labels.append(f'Ghép cấp {order} tại x_{i+1}')
    for condition in conditions:
        if len(condition)==3 and isinstance(condition[0],str):
            side,order,value=condition;terms=[(side,order,1)]
        elif len(condition)==2:terms,value=condition
        else:raise ValueError('Điều kiện phải là [trái/phải,cấp,giá trị] hoặc [các hạng,giá trị].')
        values=[Fraction(0)]*size
        for side,order,weight in terms:
            if side not in ('trái','phải'):raise ValueError('Phía biên phải là trái hoặc phải.')
            order=_integer(order,'Cấp đạo hàm biên')
            if order>degree:raise ValueError('Cấp điều kiện biên lớn hơn bậc spline.')
            segment,u=(0,Fraction(0)) if side=='trái' else (n-1,h[-1])
            values=[a+_q(weight)*b for a,b in zip(values,row(segment,u,order))]
        matrix.append(values);rhs.append(_q(value));labels.append(str(condition))
    return matrix,rhs,labels


def _build(data,kind,left,right,options):
    x,y=data['x'],data['y'];h=data['h'];slopes=data['slopes'];n=len(h)
    solver=options.get('solver','auto')
    if solver not in ('auto','Thomas','Gauss'):raise ValueError('Bộ giải phải là auto, Thomas hoặc Gauss.')
    if kind=='Tuyến tính':
        data['degree']=1;data['boundary_conditions']=[];data['solver']={'kind':'Công thức dây cung','forward':[],'backward':[]}
        return [[y[i],slopes[i]] for i in range(n)]
    if kind.startswith('Bậc hai'):
        data['degree']=2;right_end=kind.endswith('phải');given=right if right_end else left
        if given is None:raise ValueError('Spline bậc 2 còn thiếu một độ dốc đầu '+('phải.' if right_end else 'trái.'))
        m=[Fraction(0)]*(n+1);m[-1 if right_end else 0]=_q(given);trace=[]
        for i in range(n-1,-1,-1) if right_end else range(n):
            old=m[i+1] if right_end else m[i];new=2*slopes[i]-old
            m[i if right_end else i+1]=new
            trace.append({'segment':i,'old':old,'slope':slopes[i],'new':new,'side':'phải' if right_end else 'trái'})
        data['slopes_at_nodes']=m;data['boundary_conditions']=[('phải' if right_end else 'trái',1,_q(given))]
        data['solver']={'kind':'Truy hồi đạo hàm bậc 2','recurrence':trace,'forward':[],'backward':[]}
        return [[y[i],m[i],(m[i+1]-m[i])/(2*h[i])] for i in range(n)]
    if kind.startswith('Cubic'):
        data['degree']=3
        return _moments(data,x,y,h,slopes,kind,left,right,options.get('boundary_orders',(1,2)),solver)
    if kind in ('Bậc 4 — đạo hàm trái','Đạo hàm đầu trái'):
        degree=4 if kind.startswith('Bậc 4') else _integer(options.get('degree',4),'Bậc spline',1)
        raw_derivatives=options.get('derivatives')
        derivatives=[] if raw_derivatives is None else list(raw_derivatives)
        if len(derivatives)!=degree-1:raise ValueError(f'Bậc {degree} cần đúng {degree-1} đạo hàm đầu trái; hiện có {len(derivatives)}. Không phải thiếu mốc.')
        v=list(map(_q,derivatives));coefficients=[];trace=[]
        for i in range(n):
            row=[y[i]]+[v[k-1]/math.factorial(k) for k in range(1,degree)]
            known=sum((c*h[i]**k for k,c in enumerate(row)),Fraction(0));row.append((y[i+1]-known)/h[i]**degree)
            next_v=[_piece(row,h[i],order) for order in range(1,degree)]
            trace.append({'segment':i,'incoming':v.copy(),'known_endpoint':known,'last_coefficient':row[-1],'outgoing':next_v.copy()})
            coefficients.append(row);v=next_v
        data['degree']=degree;data['boundary_conditions']=[('trái',k,_q(value)) for k,value in enumerate(derivatives,1)]
        data['solver']={'kind':'Truy hồi các đạo hàm một đầu','general_recurrence':trace,'forward':[],'backward':[]}
        return coefficients
    if kind in ('Biên tổng quát','Spline biên tổng quát'):
        degree=_integer(options.get('degree',3),'Bậc spline',1);conditions=options.get('conditions')
        if not isinstance(conditions,(list,tuple)):raise ValueError('Cần danh sách conditions gồm tất cả điều kiện biên của đề.')
        data['degree']=degree;data['boundary_conditions']=deepcopy(conditions)
        matrix,rhs,labels=_boundary_equations(x,y,h,degree,conditions)
        data['system']={'matrix':matrix,'rhs':rhs,'labels':labels,'variable':'a'}
        values,trace=_gauss(matrix,rhs);data['solver']=trace
        return [values[i*(degree+1):(i+1)*(degree+1)] for i in range(n)]
    raise ValueError('Loại spline không được hỗ trợ.')


def _validate(data):
    c=data['coefficients'];h=data['h'];y=data['y'];p=data['degree']
    data['interpolation_checks']=[];data['join_checks']=[]
    for i,row in enumerate(c):
        for side,u,expected in (('trái',Fraction(0),y[i]),('phải',h[i],y[i+1])):
            value=_piece(row,u);residual=value-expected
            data['interpolation_checks'].append((i,side,value,expected,residual))
            _check(data,f'Nội suy đoạn {i}, đầu {side}',residual,max(abs(value),abs(expected)))
    for i in range(1,len(data['x'])-1):
        for order in range(p):
            a=_piece(c[i-1],h[i-1],order);b=_piece(c[i],Fraction(0),order)
            data['join_checks'].append((i,order,a,b,a-b))
            scale=max(abs(a),abs(b),_magnitude(c[i-1],h[i-1],order),_magnitude(c[i],Fraction(0),order))
            _check(data,f'Ghép cấp {order} tại nút {i}',a-b,scale)
    for condition in data.get('boundary_conditions',[]):
        if len(condition)==3 and condition[0] in ('trái','phải'):
            side,order,expected=condition
            value=_piece(c[0],Fraction(0),order) if side=='trái' else _piece(c[-1],h[-1],order)
            magnitude=_magnitude(c[0],Fraction(0),order) if side=='trái' else _magnitude(c[-1],h[-1],order)
            _check(data,f'Biên {side}, đạo hàm cấp {order}',value-_q(expected),max(magnitude,abs(_q(expected))))
    kind=data['method']
    if kind=='Cubic tuần hoàn':
        for order in range(3):
            a=_piece(c[0],Fraction(0),order);b=_piece(c[-1],h[-1],order)
            _check(data,f'Ghép chu kỳ cấp {order}',a-b,max(abs(a),abs(b),_magnitude(c[0],Fraction(0),order),_magnitude(c[-1],h[-1],order)))
    if kind=='Cubic not-a-knot':
        for i in (1,len(c)-1):
            a=_piece(c[i-1],h[i-1],3);b=_piece(c[i],Fraction(0),3)
            moments=data['moments']
            scale=max(abs(a),abs(b),abs(moments[i-1]/h[i-1]),abs(moments[i]/h[i-1]),abs(moments[i]/h[i]),abs(moments[i+1]/h[i]))
            _check(data,f'Not-a-knot tại nút {i}',a-b,scale)
    system=data.get('system')
    if system and system.get('variable')=='a':
        flat=[v for row in c for v in row]
        for i,(row,rhs) in enumerate(zip(system['matrix'],system['rhs'])):
            terms=[a*v for a,v in zip(row,flat)]
            _check(data,f'Điều kiện đầy đủ hàng {i}',sum(terms,Fraction(0))-rhs,max([abs(rhs)]+list(map(abs,terms))))


def _evaluate(data,pp,target,order,allow):
    if target is None:return
    z=_q(target);x=data['x'];c=data['coefficients'];order=_integer(order,'Cấp đạo hàm')
    outside=not x[0]<=z<=x[-1]
    if outside and not allow:raise ValueError('Điểm đánh giá ngoài miền spline; cần bật ngoại suy tường minh để kéo dài mảnh biên.')
    i=min(max(int(np.searchsorted(np.array(list(map(float,x))),float(z),side='right'))-1,0),len(c)-1)
    u=z-x[i];value=_piece(c[i],u,order)
    info={'target':z,'order':order,'segment':i,'u':u,'value':value,'outside':outside,'common_derivative':True}
    data['evaluation']=info
    if outside:data['warnings'].append('Đánh giá ngoại suy bằng mảnh biên theo lựa chọn tường minh; không kẹp điểm về đầu mút.')
    if 0<i<len(x)-1 and z==x[i] and order:
        info['sides']=[]
        for k in range(min(order,len(c[i])-1)+1):
            a=_piece(c[i-1],data['h'][i-1],k);b=_piece(c[i],Fraction(0),k)
            info['sides'].append((k,a,b,a-b))
            magnitude=max(abs(a),abs(b),_magnitude(c[i-1],data['h'][i-1],k),_magnitude(c[i],Fraction(0),k))
            if a!=b and abs(a-b)>Fraction(1,10**10)*magnitude:
                info['common_derivative']=False;info['value']=None
                raise ValueError(f'Không có đạo hàm chung cấp {order} tại nút {float(z):.12g}: đạo hàm cấp {k} trái={float(a):.12g}, phải={float(b):.12g}. Giữ spline và hai phía để xem.')


def _integrate(data,a,b,allow):
    if a is None and b is None:return
    if a is None or b is None:raise ValueError('Tích phân spline cần cả hai cận a,b.')
    left,right=map(_q,(a,b));sign=1
    if right<left:left,right=right,left;sign=-1
    x=data['x']
    if not allow and (left<x[0] or right>x[-1]):raise ValueError('Cận tích phân ngoài miền spline; chưa bật ngoại suy.')
    cuts=sorted(set([left,right]+[v for v in x if left<v<right]));total=Fraction(0);rows=[]
    for lo,hi in zip(cuts,cuts[1:]):
        mid=(lo+hi)/2;i=min(max(int(np.searchsorted(np.array(list(map(float,x))),float(mid),side='right'))-1,0),len(x)-2)
        u,v=lo-x[i],hi-x[i]
        contribution=sign*sum((c*(v**(k+1)-u**(k+1))/(k+1) for k,c in enumerate(data['coefficients'][i])),Fraction(0))
        total+=contribution;rows.append((i,lo,hi,u,v,contribution,total))
    data['integral']={'a':_q(a),'b':_q(b),'value':total,'rows':rows}


def _formula(w,lhs,row,var='u'):
    # Sinh chuỗi toán từ hệ số đã có; không raster hóa hàng trăm mảnh
    # đang thu gọn chỉ để đo độ rộng trong bước dựng báo cáo.
    chunks=[];latex=plain=''
    for power,value in enumerate(row):
        if not value:continue
        absolute=abs(value)
        exact=not isinstance(value,Fraction) or value.numerator.bit_length()+value.denominator.bit_length()<100
        coefficient=w.tex(absolute,exact=exact);coefficient_plain=w.number(absolute,exact=exact)
        tail='' if not power else var if power==1 else rf'{var}^{{{power}}}'
        tail_plain='' if not power else var if power==1 else f'{var}^{power}'
        term=coefficient+(r'\,' if power else '')+tail
        term_plain=coefficient_plain+('*' if power else '')+tail_plain
        if latex and len(plain)+len(term_plain)>85:
            chunks.append((latex,plain));latex=plain=''
        sign='-' if value<0 else '+' if latex or chunks else ''
        latex+=sign+term;plain+=sign+term_plain
    if not latex and not chunks:latex=plain='0'
    if latex:chunks.append((latex,plain))
    for i,(a,b) in enumerate(chunks):w.formula((lhs+'=' if not i else r'\qquad ')+a,(lhs+' = ' if not i else '    ')+b)


def _report(data,pp=None):
    report=Report('Spline — '+data['method'],value=pp)
    report.presentation['worked_solution']=data
    shown_digits=data['input'].get('display_digits',12)
    if isinstance(shown_digits,bool) or not isinstance(shown_digits,(int,np.integer)) or shown_digits<0:shown_digits=12
    w=ReportBuilder(report,data['input'].get('detail_level','summary'),shown_digits);num=w.number;tex=w.tex
    with w.group('section','1. Bài toán, dữ liệu và điều kiện biên'):
        w.text(f'Phương pháp: {data["method"]}; bậc tối đa {data.get("degree","chưa xác định")}. Có {len(data.get("x",[]))} mốc và {max(0,len(data.get("x",[]))-1)} đoạn. Mốc không đều là hợp lệ.')
        if data.get('x'):w.table('Các cặp sau sắp tăng x',['dòng gốc','x_i','y_i'],zip(data['sort_order'],data['x'],data['y']))
        else:w.text('X đã nhận: '+str(data['input']['x'])+'; Y đã nhận: '+str(data['input']['y']))
        if data.get('sort_order')!=list(range(len(data.get('x',[])))):w.text('Đã giữ ghép cặp và lưu số dòng gốc khi sắp x.')
        for condition in data.get('boundary_conditions',[]):w.text('Điều kiện đã chọn: '+str(condition)+'.')
        if not data.get('boundary_conditions') and data.get('degree')==1:w.text('Spline tuyến tính không cần điều kiện biên bổ sung.')
        w.text('Spline thông thường là phép dựng mảnh/giải hệ, không có vòng hội tụ t=Phi(t).')
    with w.group('section','2. Tiền kiểm và số điều kiện'):
        if data.get('x'):w.text('✓ Các cặp hữu hạn, hoành độ phân biệt; giữ nguyên tất cả mốc.','success')
        if 'degree' in data:w.text(f'Bậc p={data["degree"]} cần {data["degree"]-1} điều kiện bổ sung độc lập ngoài nội suy và ghép đạo hàm. Đếm đủ hàng chưa tự chứng minh độc lập.')
        if data.get('failure'):w.text(data['failure']['stage']+': '+data['failure']['message'],'failed')
        for warning in data['warnings']:w.text(warning,'warning')
    if data.get('h'):
        with w.group('section','3. Các khoảng, hệ phương trình và hệ số'):
            with w.group('columns'):
                with w.group('panel','Lưới và độ dốc'):
                    w.table('Độ dài và độ dốc từng đoạn',['i','x trái','x phải','h_i','δ_i'],
                            ((i,data['x'][i],data['x'][i+1],h,data['slopes'][i]) for i,h in enumerate(data['h'])),exact=True)
                if data.get('coefficients'):
                    with w.group('panel','Hệ số các mảnh'):
                        w.text('u=x−x_i; hệ số theo bậc tăng từ trái sang phải.')
                        w.table('Hệ số theo u=x−x_i, bậc tăng',['i']+[f'u^{k}' for k in range(data['degree']+1)],
                                ([i]+row for i,row in enumerate(data['coefficients'])),exact=True)
            if data.get('system'):
                system=data['system'];matrix=system['matrix'];variable=system['variable']
                w.text('Ẩn moment M_i=S″(x_i).' if variable=='M' else 'Ẩn a_(i,r) là hệ số của u^r trong từng mảnh; giữ tất cả điều kiện được đưa vào.')
                if variable=='M':
                    w.formula(r'h_{i-1}M_{i-1}+2(h_{i-1}+h_i)M_i+h_iM_{i+1}=6(\delta_i-\delta_{i-1})',
                              'Hàng trong: h_(i-1)M_(i-1)+2(h_(i-1)+h_i)M_i+h_i M_(i+1)=6(δ_i−δ_(i-1)).')
                with w.details('Hệ phương trình đầy đủ đã dùng'):
                    if matrix is not None:
                        w.table('Ma trận hệ và vế phải',[f'{variable}_{i}' for i in range(len(matrix[0]))]+['vế phải'],
                                (row+[value] for row,value in zip(matrix,system['rhs'])),exact=True)
                    else:
                        if 'sparse_rows' in system:
                            w.table('Các hàng hệ thưa đã dùng',['i','hệ số theo chỉ số moment','vế phải'],
                                    ((i,', '.join(f'M_{j}: {num(v,exact=True)}' for j,v in row.items()),value) for i,(row,value) in enumerate(zip(system['sparse_rows'],system['rhs']))),text_columns=(1,))
                            w.text('Giữ các liên kết hai đầu/ngoài băng; không biến hệ này thành Thomas thường.')
                        else:
                            w.table('Ba đường chéo và vế phải',['i','l_i','b_i','q_i','r_i'],
                                ((i,*row) for i,row in enumerate(zip(system['lower'],system['diagonal'],system['upper'],system['rhs']))),exact=True)
                            w.text('Giữ dạng ba đường chéo; không dựng ma trận đặc chỉ để hiển thị bảng lớn.')
    solver=data.get('solver')
    if solver:
        with w.group('section','4. Truy hồi, khử và thế ngược thực tế'):
            w.text('Bộ giải đã dùng: '+solver['kind']+'.')
            if solver.get('note'):w.text(solver['note'],'muted')
            if solver.get('recurrence'):
                w.formula(r'm_{i+1}=2\delta_i-m_i,\quad c_i=\frac{m_{i+1}-m_i}{2h_i}',
                          'Trái→phải: m_(i+1)=2δ_i−m_i; phải→trái: m_i=2δ_i−m_(i+1); c_i=(m_(i+1)−m_i)/(2h_i).')
                w.table('Truy hồi đạo hàm',['đoạn','độ dốc δ_i','đạo hàm đã biết','đạo hàm mới'],
                        ((r['segment'],r['slope'],r['old'],r['new']) for r in solver['recurrence']),exact=True)
            if solver.get('general_recurrence'):
                w.formula(r'a_{i,p}=\frac{y_{i+1}-\sum_{r=0}^{p-1}a_{i,r}h_i^r}{h_i^p}',
                          'Hệ số cuối a_(i,p)=(y_(i+1)−sum_(r=0)^(p−1) a_(i,r)h_i^r)/h_i^p; truyền đồng thời mọi đạo hàm sang đoạn kế.')
                for row in solver['general_recurrence']:
                    with w.details('Đoạn '+str(row['segment'])+' — truyền đạo hàm'):
                        w.text('Đạo hàm đầu vào: ['+', '.join(num(v,exact=True) for v in row['incoming'])+'].')
                        w.text('Giá trị đầu phải từ các hệ số đã biết: '+num(row['known_endpoint'],exact=True)+'. Hệ số bậc p: '+num(row['last_coefficient'],exact=True)+'.')
                        w.text('Đạo hàm truyền sang đoạn sau: ['+', '.join(num(v,exact=True) for v in row['outgoing'])+'].')
            if solver.get('forward'):
                with w.details('Mọi bước khử đã dùng'):
                    if solver['kind'].startswith('Thomas'):
                        w.formula(r'\lambda_i=\frac{l_i}{\widetilde b_{i-1}},\quad\widetilde b_i=b_i-\lambda_iq_{i-1},\quad\widetilde r_i=r_i-\lambda_i\widetilde r_{i-1}',
                                  'λ_i=l_i/b_tilde_(i−1); b_tilde_i=b_i−λ_i q_(i−1); r_tilde_i=r_i−λ_i r_tilde_(i−1).')
                        w.table('Khử xuôi Thomas',['i','l_i','pivot trước','λ_i','b_i','b sau khử','r_i','r sau khử'],
                             ((r['i'],r['lower'],r['previous_pivot'],r['factor'],r['original_diagonal'],r['pivot'],r['original_rhs'],r['reduced_rhs']) for r in solver['forward']),exact=True)
                        w.table('Các tỉ số sau khử',['i','c′_i=q_i/b sau khử','d′_i=r sau khử/b sau khử'],
                             ((r['i'],r['c_prime'],r['d_prime']) for r in solver['forward']),exact=True)
                    else:
                        w.table('Chọn trụ Gauss',['bước','cột','hàng chọn','pivot','các hệ số khử'],
                                ((r['step'],r['column'],r['selected_row'],r['pivot'],str([(i,num(f,exact=True)) for i,f in r['eliminations']])) for r in solver['forward']),exact=True,text_columns=(4,))
            if solver.get('backward'):
                w.table('Thế ngược',['ẩn','vế phải sau khử','đóng góp ẩn sau','pivot','nghiệm'],
                        ((r['i'],r['rhs'],r['upper_contribution'],r['pivot'],r['value']) for r in solver['backward']),exact=True)
            if data.get('moments'):w.text('M = ['+', '.join(num(v,exact=True) for v in data['moments'])+'].')
    if data.get('coefficients'):
        with w.group('section','5. Các mảnh và miền áp dụng'):
            w.text('Mỗi mảnh dùng u=x−mốc trái của chính đoạn đó. Không thay x toàn cục trực tiếp vào đa thức theo u.')
            for i,row in enumerate(data['coefficients']):
                with w.details(f'Mảnh {i}: [{num(data["x"][i])}, {num(data["x"][i+1])}]'):
                    w.formula(rf'u=x-({tex(data["x"][i])}),\quad 0\leq u\leq {tex(data["h"][i])}',
                              f'u=x−({num(data["x"][i])}), 0≤u≤{num(data["h"][i])}.')
                    _formula(w,rf'S_{{{i}}}(x_i+u)',row)
        with w.group('section','6. Kiểm tra nút, biên và đánh giá'):
            checks=data['checks'];passed=sum(r['passed'] for r in checks)
            w.text(f'{passed}/{len(checks)} kiểm tra nội suy, ghép đạo hàm, hệ và biên đạt ngưỡng công bố.',
                   'success' if passed==len(checks) else 'failed')
            with w.details('Mọi phần dư và phép kiểm tra'):
                w.table('Kiểm tra điều kiện đã chọn',['điều kiện','phần dư','ngưỡng','đạt'],
                        ((r['title'],r['value'],r['tolerance'],r['passed']) for r in checks),text_columns=(0,))
                if data.get('join_checks'):w.table('Hai phía tại nút',['nút','cấp','trái','phải','chênh'],data['join_checks'],exact=True)
            evaluation=data.get('evaluation')
            if evaluation:
                i=evaluation['segment'];order=evaluation['order'];z=evaluation['target'];u=evaluation['u']
                w.text(f'z={num(z)} dùng đoạn {i}: [{num(data["x"][i])}, {num(data["x"][i+1])}], u=z−x_i={num(u)}. Đầu mút phải cuối cùng dùng mảnh cuối.')
                if evaluation['value'] is not None:
                    w.formula(rf'S^{{({order})}}({tex(z)})={tex(evaluation["value"])}',
                              f'S^({order})({num(z)})={num(evaluation["value"],exact=True)}.')
                    w.text('Đạo hàm theo x bằng đạo hàm theo u vì du/dx=1; không chia thêm h_i.')
                if evaluation.get('sides'):w.table('Đạo hàm hai phía tại điểm hỏi',['cấp','trái','phải','chênh'],evaluation['sides'],exact=True)
            if data.get('integral'):
                result=data['integral'];w.table('Tích phân chia tại các nút',['đoạn','a','b','u trái','u phải','đóng góp','tổng tạm'],result['rows'],exact=True)
                w.formula(rf'\int_{{{tex(result["a"])}}}^{{{tex(result["b"])}}}S(x)\,dx={tex(result["value"])}',
                          f'Tích phân từ {num(result["a"])} tới {num(result["b"])} = {num(result["value"],exact=True)}.')
    with w.group('section','7. Kết luận đúng phạm vi',keep_together=True):
        if data.get('failure'):w.text(data['failure']['message'],'failed')
        elif pp is not None:w.text(f'Đã dựng {len(data["coefficients"])} mảnh bậc không quá {data["degree"]}, giữ đúng dữ liệu và điều kiện biên.','success')
        w.text('Phần dư nút/hệ và chênh đạo hàm kiểm tra việc giải mô hình; chúng không phải cận sai số với hàm thật giữa các mốc. Spline nội suy không tự làm trơn nhiễu hoặc bảo đảm giữ đơn điệu.','muted')
    w.finish()
    if pp is not None:
        xx=np.array(list(map(float,data['x'])));yy=np.array(list(map(float,data['y'])));report.scatter=(xx,yy)
        grid=np.linspace(xx[0],xx[-1],400);values=pp(grid)
        if np.all(np.isfinite(values)):report.curves=[(grid,values,data['method'])]
        else:data['warnings'].append('Không vẽ được toàn miền bằng float; các hệ số vẫn được giữ.')
    return report


def solve_spline(x,y,kind='Cubic tự nhiên',left=None,right=None,target=None,**options):
    """Giữ lựa chọn bậc/biên, trả Report có trace và PPoly khi dựng được."""
    data={'family':'spline','method':kind,'input':{'x':deepcopy(x),'y':deepcopy(y),'left':left,'right':right,'target':target,**deepcopy(options)},
          'status':'pending','failure':None,'checks':[],'warnings':[],'phase':'Đọc dữ liệu'}
    pp=None
    try:
        _integer(options.get('display_digits',12),'Số chữ số hiển thị')
        if options.get('detail_level','summary') not in ('summary','detailed'):raise ValueError('Mức trình bày phải là summary hoặc detailed.')
        xx,yy,_=points(x,y,2)
        original=np.asarray(x,float);data['sort_order']=np.argsort(original,kind='stable').tolist()
        data['x']=list(map(_q,xx));data['y']=list(map(_q,yy));data['h']=[b-a for a,b in zip(data['x'],data['x'][1:])]
        data['slopes']=[(b-a)/h for a,b,h in zip(data['y'],data['y'][1:],data['h'])]
        data['phase']='Lập hệ, truy hồi và tính hệ số'
        coefficients=_build(data,kind,left,right,options);data['coefficients']=coefficients
        columns=np.asarray([[float(v) for v in row[::-1]] for row in coefficients],float).T
        if not np.all(np.isfinite(columns)):raise ValueError('Hệ số vượt miền float; đổi đơn vị x,y hoặc điều kiện biên.')
        pp=PPoly(columns,xx,extrapolate=False)
        data['phase']='Kiểm tra mọi điều kiện';_validate(data)
        for i,row in enumerate(coefficients):
            endpoint=float(pp(float(data['x'][i+1])))
            magnitude=sum((abs(c)*data['h'][i]**k for k,c in enumerate(row)),Fraction(0))
            _check(data,f'PPoly sau chuyển float tại mốc {i+1}',_q(endpoint)-data['y'][i+1],max(magnitude,abs(data['y'][i+1])))
        if any(not r['passed'] for r in data['checks']):raise ValueError('Có điều kiện nội suy/ghép/biên chưa đạt; xem từng phần dư, không báo thành công.')
        data['phase']='Đánh giá điểm và tích phân';raw_allow=options.get('allow_extrapolation',False)
        allow=raw_allow is True or isinstance(raw_allow,str) and raw_allow.casefold()=='true'
        _evaluate(data,pp,target,options.get('order',options.get('derivative_order',0)),allow)
        _integrate(data,options.get('integral_a'),options.get('integral_b'),allow)
        data['status']='spline_constructed'
    except (ValueError,TypeError,ArithmeticError,OverflowError) as exc:
        data['status']='evaluation_failed' if pp is not None else 'invalid_spline'
        data['failure']={'stage':data['phase'],'message':str(exc)}
    return _report(data,pp)
