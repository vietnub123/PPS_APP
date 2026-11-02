"""Đối chiếu số của các chương 05–07 bằng repo và số hữu tỷ cơ bản."""
from pathlib import Path
from fractions import Fraction as F
from functools import reduce
import json
import math
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import numpy as np
from pps import calculus as ca, differential as de

OUT=Path(__file__).resolve().parent


def solve_exact(a,b):
    a=[list(map(F,row))+[F(v)] for row,v in zip(a,b)]
    n=len(a)
    for k in range(n):
        pivot=next(i for i in range(k,n) if a[i][k])
        a[k],a[pivot]=a[pivot],a[k]
        for i in range(k+1,n):
            f=a[i][k]/a[k][k]
            for j in range(k,n+1):a[i][j]-=f*a[k][j]
    x=[F(0)]*n
    for i in range(n-1,-1,-1):x[i]=(a[i][-1]-sum(a[i][j]*x[j] for j in range(i+1,n)))/a[i][i]
    return x


def nice(value):
    return f'{float(value):.12g}'


def main():
    data={}
    weights={};tex=[r'\begin{longtable}{rcll}',r'\toprule',r'$d$ & $p$ & Hệ số chung $\kappa_d$ & Vector nguyên $v$, với $w_j=\kappa_d v_j$\\',r'\midrule',r'\endhead']
    for d in range(1,11):
        w=solve_exact([[F(j)**r for j in range(d+1)] for r in range(d+1)],
                      [F(d)**(r+1)/(r+1) for r in range(d+1)])
        actual,p=ca.quadrature_weights(d,'Newton-Cotes',d)
        assert np.allclose(actual,list(map(float,w)),atol=2e-12,rtol=2e-12)
        denominator=math.lcm(*(x.denominator for x in w));integers=[int(x*denominator) for x in w]
        gcd=reduce(math.gcd,(abs(x) for x in integers));factor=F(gcd,denominator);integers=[v//gcd for v in integers]
        weights[d]={'factor':str(factor),'integers':integers,'weights':list(map(str,w)),'p':p}
        fac=str(factor.numerator) if factor.denominator==1 else rf'\frac{{{factor.numerator}}}{{{factor.denominator}}}'
        # Chia dòng các vector dài bằng minipage để không tràn giấy.
        vector=r',\allowbreak '.join(map(str,integers))
        tex.append(rf'{d}&{p}&${fac}$&\begin{{minipage}}[t]{{.55\textwidth}}\raggedright\small $({vector})$\end{{minipage}}\\[4pt]')
    tex.extend([r'\bottomrule',r'\end{longtable}'])
    (OUT/'calculus_nc_weights.tex').write_text('\n'.join(tex)+'\n',encoding='utf-8')
    data['newton_cotes']=weights
    quadratures={}
    for method in ('Hình thang','Trung điểm','Simpson','Newton-Cotes'):
        degree=4 if method=='Newton-Cotes' else 2
        n=4 if method=='Newton-Cotes' else 2
        r=ca.integrate(method,'x^2',0,1,n,degree)
        quadratures[method]={'n':n,'value':r.value,'tables':r.tables}
    adaptive=ca.integrate('Hình thang','x^2',0,1,2,tolerance=.001)
    bounded=ca.integrate('Hình thang','x^2',0,1,2,tolerance=.001,bound=2)
    double=ca.double_integral('x^2+y^2',0,1,0,1,2,'Simpson',1e-7)
    data['quadratures']=quadratures
    data['adaptive']={'value':adaptive.value,'tables':adaptive.tables}
    data['bounded']={'value':bounded.value,'lines':bounded.lines}
    data['double']={'value':double.value,'tables':double.tables}
    for x,y,z,p,s,answer in [([0,1,2],[1,2,5],0,2,1,0),([0,1,3],[1,3,13],1,2,1,3),([0,1,2],[1,2,5],1,2,2,2)]:
        r=ca.differentiate(x,y,z,p,s);assert abs(r.value-answer)<1e-12
    methods=['Euler hiện','Euler ẩn','Hình thang','RK2','RK3','RK4']
    ode={}
    for method in methods:
        r=de.ode(['x'],[1],0,.1,.1,method)
        ode[method]={'value':float(r.value[1][-1,0]),'tables':r.tables}
    ode['RK2 tham số']=float(de.ode(['x'],[1],0,.1,.1,'RK tùy chỉnh',custom=de.custom_rk2('alpha2',.75)).value[1][-1,0])
    for c2,c3 in ((F(3,10),F(4,5)),(F(2,3),F(0)),(F(2,3),F(2,3))):
        key=f'RK3 c2={c2},c3={c3}';tab=de.custom_rk3(float(c2),float(c3))
        ode[key]={'tableau':[v.tolist() for v in tab],'value':float(de.ode(['x'],[1],0,.1,.1,'RK tùy chỉnh',custom=tab).value[1][-1,0])}
    r=de.ode(['y','-x'],[1,0],0,.1,.1,'RK4')
    ode['oscillator']=r.value[1].tolist()
    data['ode']=ode
    R=F(265241,240000);H=F(1,10)
    adams={};adams_tex=[]
    for s in range(2,6):
        history=[R**(s-1-j) for j in range(s)]
        beta=list(map(lambda v:F(str(float(v))),de.AB[s]))
        # Các hệ số hữu tỷ chuẩn, không lấy số float làm chuẩn toán học.
        ab={2:[F(3,2),F(-1,2)],3:[F(23,12),F(-16,12),F(5,12)],4:[F(55,24),F(-59,24),F(37,24),F(-9,24)],5:[F(1901,720),F(-2774,720),F(2616,720),F(-1274,720),F(251,720)]}[s]
        am={2:[F(5,12),F(8,12),F(-1,12)],3:[F(9,24),F(19,24),F(-5,24),F(1,24)],4:[F(251,720),F(646,720),F(-264,720),F(106,720),F(-19,720)],5:[F(475,1440),F(1427,1440),F(-798,1440),F(482,1440),F(-173,1440),F(27,1440)]}[s]
        pred=history[0]+H*sum(b*f for b,f in zip(ab,history))
        tail=sum(a*f for a,f in zip(am[1:],history));new=(history[0]+H*tail)/(1-H*am[0])
        actual=de.ode(['x'],[1],0,float(s*H),float(H),f'Adams {s}')
        assert abs(float(actual.value[1][-1,0])-float(new))<2e-13
        adams[s]={'startup':list(map(str,[R**i for i in range(s)])),'history':list(map(str,history)),'ab':list(map(str,ab)),'am':list(map(str,am)),'predictor':str(pred),'corrected':str(new),'actual':float(actual.value[1][-1,0])}
        adams_tex.extend([r'\examplebreak',rf'\subsubsection*{{Ví dụ Adams {s}: đủ {s-1} bước khởi tạo và một bước Adams}}',
          r'Ví dụ tự dựng: $u^{\prime}=u$, $u(0)=1$, $h=0.1$. Gọi $R_4=265241/240000$ là hệ số tăng trưởng một bước RK4. Ở bước Adams dưới đây, $n=s-1$.',
          r'\begin{center}\begin{tabular}{rrll}\toprule $i$&$t_i$&$u_i$&Cách có giá trị\\\midrule'])
        for i in range(s):adams_tex.append(rf'{i}&{nice(i*H)}&{nice(R**i)}&'+('Điều kiện đầu' if i==0 else rf'RK4: $u_{i} = R_4u_{{{i-1}}}$')+r'\\')
        adams_tex.extend([r'\bottomrule\end{tabular}\end{center}',r'Ở bước Adams, xếp lịch sử từ mới nhất đến cũ nhất:',r'\begin{center}\begin{tabular}{rlll}\toprule $j$&$f_{n-j}$&$\beta_jf_{n-j}$&$a_{j+1}f_{n-j}$\\\midrule'])
        for j,(f,b,a) in enumerate(zip(history,ab,am[1:])):adams_tex.append(rf'{j}&{nice(f)}&{nice(b*f)}&{nice(a*f)}\\')
        adams_tex.extend([r'\bottomrule\end{tabular}\end{center}',
          rf'Dự báo: $u_{{n+1}}^P=u_n+0.1\sum\beta_jf_{{n-j}}={nice(pred)}$.',
          rf'Hiệu chỉnh giải phương trình tuyến tính $(1-0.1\,{str(am[0])})u_{{n+1}}=u_n+0.1\sum a_{{j+1}}f_{{n-j}}$.',
          rf'Kết quả: $u_{{n+1}}={nice(new)}$ tại $t_{{n+1}}={nice(s*H)}$. Đối chiếu app: ${actual.value[1][-1,0]:.12g}$.',
          r'Đây là phép giải đại số của phương trình hiệu chỉnh trong ví dụ tuyến tính, không phải nhật ký các lần gọi nội bộ của bộ giải phi tuyến.'])
    data['adams']=adams
    (OUT/'calculus_adams_examples.tex').write_text('\n'.join(adams_tex)+'\n',encoding='utf-8')
    bvp=de.bvp('1','0','2',0,1,.25,(0,1,0),(0,1,0))
    robin=de.bvp('1','0','-2',0,1,.5,(1,1,0),(1,1,3))
    assert np.allclose(bvp.value[1],bvp.value[0]*(1-bvp.value[0]))
    assert np.allclose(robin.value[1],robin.value[0]**2)
    data['bvp']={'dirichlet':bvp.tables,'robin':robin.tables}
    data['eigen']={}
    for h in (.25,.125,.0625):
        e=de.eigen('1','0','1',0,1,h,1 if h!=.25 else 3)
        data['eigen'][str(h)]={'values':e.value[0].tolist(),'nodes':e.value[1].tolist(),'vectors':e.value[2].tolist()}
    (OUT/'calculus_examples.json').write_text(json.dumps(data,ensure_ascii=False,indent=2,default=lambda v:v.tolist() if hasattr(v,'tolist') else str(v)),encoding='utf-8')
    print('PASS: exact Newton-Cotes1..10; derivative examples; quadratures; all ODE samples; Adams2..5; BVP/Robin; eigen grids.')


if __name__=='__main__':main()
