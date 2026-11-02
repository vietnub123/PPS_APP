"""Kiểm khuôn input của 58 lựa chọn và công thức khớp hai tham số trong bản mới."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import numpy as np
from pps.gui import TOOLS,fields
from pps.least_squares_worked import solve_least_squares

OUT=Path(__file__).resolve().parent
groups={'poly':'Nội suy đa thức','inverse':'Nội suy ngược','spline':'Spline','ls':'Bình phương tối thiểu',
    'calculus':'Tích phân','ode':'Phương trình vi phân','bvp':'Bài toán biên','nodes':'Chọn mốc','horner':'Đạo hàm & Horner'}
forms=[]
for slug,group in groups.items():
    src=(OUT/f'inputs_{slug}.tex').read_text(encoding='utf-8')
    for method in TOOLS[group][0]:
        row={'tool':group,'method':method,'fields':[]}
        for key,label,default,helptext in fields(group,method):
            assert key.replace('_',r'\_') in src,(group,method,key)
            row['fields'].append({'key':key,'label':label,'default':default})
        forms.append(row)

x=np.array([1.,2.,3.,4.]);w=np.array([1.,2.,3.,1.]);results=[]
cases=[('Tuyến tính theo cơ sở',1.2+.7*x,['1','x'],x,1.2+.7*x),
    ('Lũy thừa',3*x**2,None,np.log(x),np.log(3*x**2)),
    ('Hàm mũ',2*np.exp(.3*x),['x'],x,np.log(2*np.exp(.3*x))),
    ('Log của tổ hợp cơ sở',np.log(1+2*x),['1','x'],x,1+2*x),
    ('1/(a+b*x)',1/(2+3*x),None,x,2+3*x),
    ('x/(a+b*x)',x/(2+3*x),None,1/x,(2+3*x)/x),
    ('a+b*ln(x)',1+2*np.log(x),None,np.log(x),1+2*np.log(x)),
    ('A*b^x',2*3**x,None,x,np.log(2*3**x))]
for kind,y,basis,u,v in cases:
    s1=w.sum();su=(w*u).sum();sv=(w*v).sum();suu=(w*u*u).sum();suv=(w*u*v).sum()
    d=s1*suu-su*su
    expected=np.array([(sv*suu-su*suv)/d,(s1*suv-su*sv)/d])
    r=solve_least_squares(x,y,kind,basis=basis,weights=w)
    state=r.presentation['worked_solution'];assert not state['failure'],kind
    actual=np.array(list(map(float,state['coefficients'])))
    np.testing.assert_allclose(actual,expected,rtol=1e-11,atol=1e-11)
    np.testing.assert_allclose(r.value(x),y,rtol=1e-11,atol=1e-11)
    results.append({'model':kind,'linear_coefficients':actual.tolist(),'normal_system':[[s1,su],[su,suu]],'rhs':[sv,suv]})

# Hàng Jacobian của hai mô hình raw SSE: đạo hàm đại số so với hiệu đối xứng.
for z,theta,p in [('power',np.log(x)[:,None],np.array([3.,1.7])),
                  ('exponential',np.column_stack([x*x,1/x]),np.array([1.5,-.2,1.8]))]:
    def pred(par):return par[0]*np.exp(theta@par[1:])
    value=pred(p);jac=np.column_stack([np.exp(theta@p[1:]),value[:,None]*theta])
    for j in range(len(p)):
        step=np.zeros_like(p);step[j]=1e-6
        np.testing.assert_allclose((pred(p+step)-pred(p-step))/(2e-6),jac[:,j],rtol=1e-7,atol=1e-7)
    results.append({'model':z+' Jacobian','jacobian':jac.tolist()})

(OUT/'tool_manual_check.json').write_text(json.dumps({'forms':forms,'model_checks':results},ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS:',len(forms),'GUI forms; 8 transformed systems and 2 raw SSE Jacobians.')
