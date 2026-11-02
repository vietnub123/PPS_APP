"""Rà công thức thật do các đường tính GUI sinh ra, không cần cửa sổ Tk."""
from pathlib import Path
import json
import sys
import warnings

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from pps.gui import TOOLS,fields,dispatch
from pps.math_view import math_png,export_html


def gui_cases():
    for tool,(methods,_) in TOOLS.items():
        for method in methods:
            values={key:default for key,_,default,_ in fields(tool,method)}
            x='0 1 2 3 4';y='0 1 4 9 16'
            if method=='Bessel':x,y='0 1 2 3','0 1 4 9'
            if method=='Cubic tuần hoàn':y='0 1 0 -1 0'
            if tool=='Bình phương tối thiểu':
                if method.startswith('Lũy thừa'):x,y='1 2 3 4 5','1 4 9 16 25'
                if method.startswith('Hàm mũ'):y='1 2 4 8 16'
                samples={'Log của tổ hợp cơ sở':('0 1 2 3 4','0 1.0986122886681098 1.6094379124341003 1.9459101490553132 2.1972245773362196'),
                         '1/(a+b*x)':('0 1 2 3 4','.5 .3333333333333333 .25 .2 .1666666666666667'),
                         'x/(a+b*x)':('1 2 3 4 5','.3333333333333333 .5 .6 .6666666666666667 .7142857142857143'),
                         'a+b*ln(x)':('1 2 3 4 5','1 2.386294361119891 3.1972245773362196 3.772588722239781 4.218875824868201'),
                         'A*b^x':('0 1 2 3 4','1 2 4 8 16')}
                x,y=samples.get(method,(x,y))
            if tool=='Nội suy ngược':
                x,y=('1 2 3','1 4 9') if method.startswith('Hàm ngược') else ('0 1 2','0 1 4') if method=='Chia đôi đa thức' else ('1.6 1.8 2 2.2','4.23 3.67 2.99 1.24')
            yield tool+' / '+method,tool,method,values,x,y
    for nodes in ('Mốc cách đều','Mốc bất kỳ'):
        for direction in ('Tiến','Lùi'):
            yield 'Newton '+nodes+' '+direction,'Nội suy đa thức','Newton',{'newton_nodes':nodes,'direction':direction,'target':'1.5','order':'2'},'0 1 2 3','1 2 5 10'
    for solver in ('QR','Hệ chuẩn — Gauss','SVD'):
        yield 'LS weighted '+solver,'Bình phương tối thiểu','Tuyến tính theo cơ sở',{'solver':solver,'basis':'1;x;cos(x)','weights':'1 2 1 3 1','target':'.5'},'0 1 2 3 4','1 2 2 4 5'
    for basis in ('x;1/x','sqrt(x);ln(x)','1;x;x^2'):
        yield 'LS basis '+basis,'Bình phương tối thiểu','Tuyến tính theo cơ sở',{'basis':basis},'1 2 3 4 5','1 4 9 16 25'
    for order in (0,1,2,4,8):
        yield 'Stirling derivative '+str(order),'Nội suy đa thức','Stirling',{'target':'4','order':str(order)},'3.574 3.691 3.808 3.925 4.042 4.159 4.276 4.393 4.510','6.3054 6.1283 5.9039 5.6358 5.3284 4.9864 4.6151 4.2201 3.8074'
    yield 'ODE radical-log','Phương trình vi phân','RK4',{'expr':'sqrt(t+1)+ln(t+1)+x','initial':'1','a':'0','b':'.2','h':'.1','tol':'1e-10'},'', ''
    for value in ('1e-100','1e12'):
        yield 'Horner scientific '+value,'Đạo hàm & Horner','Horner',{'coef':'1 0 1','target':value,'order':'2'},'', ''
    yield 'Integral scientific','Tích phân','Simpson',{'expr':'1e-100*x','a':'0','b':'1','n':'4','source':'Hàm'},'', ''
    yield 'ODE scientific','Phương trình vi phân','RK4',{'expr':'x','initial':'1e-100','a':'0','b':'.2','h':'.1','tol':'1e-10'},'', ''


def formulas(report):
    for name,items in report.presentation.get('formulas',[]):
        for item in items:yield name,item
    for kind,value in report.presentation.get('blocks',[]):
        if kind=='formula':yield 'block',value
    for name,items in report.presentation.get('after_tables',[]):
        for item in items:yield name,item


def main():
    result={'cases':[],'errors':[],'unique_formulas':0,'formula_occurrences':0}
    seen=set()
    for title,tool,method,values,x,y in gui_cases():
        case={'name':title,'tool':tool,'method':method}
        try:
            report=dispatch(tool,method,values,x,y)
            case['status']=report.presentation.get('worked_solution',report.presentation.get('inverse_solution',{})).get('status','computed')
            case['formulas']=0
            for origin,latex in formulas(report):
                case['formulas']+=1;result['formula_occurrences']+=1
                if latex in seen:continue
                seen.add(latex)
                try:
                    with warnings.catch_warnings(record=True) as captured:
                        warnings.simplefilter('always')
                        math_png(latex)
                    glyph=[str(w.message) for w in captured if 'Glyph' in str(w.message) or 'missing' in str(w.message).lower()]
                    if glyph:result['errors'].append({'case':title,'origin':origin,'latex':latex,'error':glyph})
                except Exception as error:
                    result['errors'].append({'case':title,'origin':origin,'latex':latex,'error':str(error)})
        except Exception as error:
            result['errors'].append({'case':title,'error':str(error)})
        result['cases'].append(case)
    result['unique_formulas']=len(seen)
    path=Path(__file__).with_name('latex_audit.json')
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Cases:',len(result['cases']),'unique formulas:',len(seen),'errors:',len(result['errors']))
    for error in result['errors']:print(json.dumps(error,ensure_ascii=False))
    return bool(result['errors'])


if __name__=='__main__':raise SystemExit(main())
