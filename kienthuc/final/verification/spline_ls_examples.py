"""Đối chiếu ví dụ của hai chương bằng bộ tính thực tế; chỉ đọc mã PPS."""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import json
import math
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from pps.spline_worked import solve_spline
from pps.least_squares_worked import solve_least_squares


def clean(v):
    if isinstance(v,dict):return {k:clean(a) for k,a in v.items() if not callable(a)}
    if isinstance(v,(list,tuple,np.ndarray)):return [clean(a) for a in v]
    if isinstance(v,(Fraction,Decimal)):return str(v)
    if isinstance(v,np.generic):return clean(v.item())
    if isinstance(v,float) and not math.isfinite(v):return str(v)
    return v


def main():
    out={}
    cases=[
        ('linear',[0,1,2],[0,1,0],'Tuyến tính',{'target':.5}),
        ('quad_left',[0,1,2],[0,1,0],'Bậc hai — biên trái',{'left':0,'target':1.5}),
        ('quad_right',[0,1,2],[0,1,0],'Bậc hai — biên phải',{'right':-4,'target':1.5}),
        ('natural3',[0,1,2],[0,1,0],'Cubic tự nhiên',{'target':1.5,'integral_a':0,'integral_b':2}),
        ('natural4',[0,1,2,3],[0,1,0,1],'Cubic tự nhiên',{'target':1.5}),
        ('natural_unequal',[0,1,3],[0,1,0],'Cubic tự nhiên',{'target':2}),
        ('clamped',[0,1,2],[0,1,0],'Cubic kẹp',{'left':2,'right':-2,'target':.5}),
        ('second',[0,1,2],[0,1,0],'Cubic đạo hàm bậc hai',{'left':-2,'right':-2,'target':.5}),
        ('mixed12',[0,1,2],[0,1,0],'Cubic hỗn hợp',{'left':2,'right':-2,'boundary_orders':(1,2),'target':.5}),
        ('mixed21',[0,1,2],[0,1,0],'Cubic hỗn hợp',{'left':-2,'right':-2,'boundary_orders':(2,1),'target':.5}),
        ('periodic',[0,1,2],[0,1,0],'Cubic tuần hoàn',{'target':.5}),
        ('notaknot',[0,1,2,3],[0,1,8,27],'Cubic not-a-knot',{'target':1.5}),
        ('quartic_left',[0,1,2],[0,1,0],'Bậc 4 — đạo hàm trái',{'derivatives':[1,0,0],'target':1.5}),
        ('quartic_right',[0,1,2],[0,1,16],'Biên tổng quát',{'degree':4,'conditions':[['phải',1,32],['phải',2,48],['phải',3,48]],'target':1.5}),
        ('quartic_mixed',[0,1,2],[0,1,16],'Biên tổng quát',{'degree':4,'conditions':[['trái',1,0],['phải',1,32],['phải',2,48]],'target':1.5}),
        ('quartic_combo',[0,1,2],[0,1,16],'Biên tổng quát',{'degree':4,'conditions':[[[['trái',1,1],['phải',1,1]],32],['phải',2,48],['phải',3,48]],'target':1.5}),
    ]
    for name,x,y,kind,opts in cases:
        r=solve_spline(x,y,kind,**opts);d=r.presentation['worked_solution']
        assert d['failure'] is None,(name,d['failure'])
        assert all(a['passed'] for a in d['checks'])
        out[name]=d
        print(name,'coef=',d['coefficients'],'value=',d.get('evaluation',{}).get('value'))
    ls_cases=[
        ('line_gauss',[0,1,2,3],[1,2,2,4],{'solver':'normal_gauss'}),
        ('line_qr',[0,1,2,3],[1,2,2,4],{'solver':'qr'}),
        ('line_svd',[0,1,2,3],[1,2,2,4],{'solver':'svd'}),
        ('line_weighted',[0,1,2],[1,2,2],{'solver':'normal_gauss','weights':[1,2,1]}),
        ('quadratic',[-2,-1,0,1,2],[5,2,1,2,6],{'basis':['1','x','x^2']}),
        ('power_log',[1,2,4],[3,12,48],{'kind':'Lũy thừa'}),
        ('power_raw',[1,2,4],[3,13,47],{'kind':'Lũy thừa — SSE thang y','solver':'lm','tolerance':1e-6}),
        ('exp_log',[0,1,2],[2,5,18],{'kind':'Hàm mũ','basis':['x']}),
        ('exp_raw',[0,1,2],[2,5,18],{'kind':'Hàm mũ — SSE thang y','basis':['x'],'solver':'lm','tolerance':1e-6}),
        ('log_combination',[0,1,2],list(np.log([1,3,5])),{'kind':'Log của tổ hợp cơ sở','basis':['1','x']}),
        ('reciprocal',[1,2,3],[1/5,1/8,1/11],{'kind':'1/(a+b*x)'}),
        ('rational',[1,2,3],[1/5,2/8,3/11],{'kind':'x/(a+b*x)'}),
        ('a_plus_log',[1,2,4],[1,3,5],{'kind':'a+b*ln(x)'}),
        ('A_Bx',[0,1,2],[2,6,18],{'kind':'A*b^x'}),
        ('minimum_norm',[1,1,1],[1,2,3],{'solver':'svd','rank_policy':'minimum_norm'}),
    ]
    for name,x,y,opts in ls_cases:
        r=solve_least_squares(x,y,**opts);d=r.presentation['worked_solution']
        assert d['failure'] is None,(name,d['failure'])
        out[name]=d
        print(name,'c=',list(map(float,d['coefficients'])),'SSE=',float(d['metrics']['SSE_y']))
        if d.get('nonlinear'):
            tr=d['solver_trace']
            print('LM initial',tr['initial_parameters'],'iterations',len(tr['iterations']),tr['termination'])
            for a in tr['iterations']:print(a['iteration'],a['damping'],a['old_parameters'],a['proposed_parameters'],float(a['sse_before']),float(a['sse_proposed']) if a['sse_proposed'] is not None else None,a['accepted'],a['gradient_norm'],a['step_norm'])
    (Path(__file__).parent/'spline_ls_examples.json').write_text(json.dumps(clean(out),ensure_ascii=False,indent=2),encoding='utf-8')
    print('All examples checked; raw intermediate data saved.')


if __name__=='__main__':main()
