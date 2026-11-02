"""Đối chiếu ví dụ chương 01, 02, 07, helper và đề thật; sinh bảng phủ GUI.

Chỉ dùng mã/dữ liệu trong repo và phép tính đại số của ví dụ đã biết.
Chạy từ thư mục gốc: .venv/Scripts/python.exe kienthuc/final/verification/manual_examples.py
"""
from pathlib import Path
from fractions import Fraction as F
import csv
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import numpy as np
from pps import interpolation as ip, differential as de, chapter1_tools as ch1
from pps.gui import TOOLS, dispatch
from pps.inverse_solution import solve_inverse
from pps.math_view import export_html

OUT = Path(__file__).resolve().parent
EXAMPLES = OUT.parent / 'examples'


def state(report):
    return report.presentation.get('inverse_solution', report.presentation.get('worked_solution', {}))


def main():
    checked = []
    def close(name, actual, expected, tol=1e-11):
        assert np.allclose(actual, expected, rtol=tol, atol=tol), (name, actual, expected)
        checked.append({'name': name, 'actual': np.asarray(actual).tolist(), 'expected': np.asarray(expected).tolist()})

    # Các đa thức nhỏ biết trước; kiểm cùng mô hình cho cả giá trị và đạo hàm.
    for method in ('Lagrange', 'Newton bất kỳ', 'Newton bất kỳ lùi'):
        p = ip.interpolate([0, 1, 3], [1, 3, 13], method, 2, 1).value
        close(method, [p(2), p.deriv()(2)], [7, 5])
    x = [-2, -1, 0, 1, 2]; y = [17, 1, 1, 5, 25]
    for method in ('Newton tiến', 'Newton lùi', 'Gauss I', 'Gauss II', 'Stirling'):
        p = ip.interpolate(x, y, method, .25, 1).value
        close(method+' five nodes', [p(.25), p.deriv()(.25)], [401/256, 41/16])
    for method in ('Gauss I', 'Gauss II', 'Bessel'):
        p = ip.interpolate([-1, 0, 1, 2], [0, 1, 2, 9], method, .5, 1).value
        close(method+' four nodes', [p(.5), p.deriv()(.5)], [9/8, 3/4])
    h = ip.horner([3, 0, -2, -1], 2, 3)
    close('Horner P(2)', h.value, 19)
    quotient = [1, -3, 0, 2]; remainders = []
    for _ in range(3):
        quotient, rem = ch1.horner_division(quotient, 2); remainders.append(rem)
    remainders.append(float(quotient[0]))
    close('Horner API ascending, derivatives', [math.factorial(k)*v for k,v in enumerate(remainders)], [11,21,24,12])
    EXAMPLES.mkdir(exist_ok=True)
    export_html(h, EXAMPLES/'Horner_bang_phep_tinh.html')

    for method in ('inverse_lagrange', 'inverse_newton'):
        r = solve_inverse([0,1,2], [0,1,4], 2, method)
        assert not state(r)['failure'], state(r)
        close(method, r.value, 5/3)
    for method, expected, rounds in (
        ('forward_iteration', .4880884816754477, 3),
        ('backward_iteration', .488088655982, 5)):
        r=solve_inverse([0,1,2], ['1','3.1','5.4'], 2, method,
                        interval=(0,1), eps_x=1e-6, eps_y=1e-6, stop_mode='certified')
        s=state(r); assert not s['failure'], s
        close(method, r.value, expected, 1e-12)
        assert len(s['iteration']['history'])==rounds
        checked.append({'name': method+' all iterations', 'history': s['iteration']['history']})
    r=solve_inverse([0,1,2], [0,1,4], 2, 'bisection', interval=(1,2), eps_x=.02)
    s=state(r); assert not s['failure']; assert len(s['bisection_history'])==5
    close('Bisection final midpoint', r.value[0], 1.421875)
    close('Fill missing', ch1.fill_missing([0,1,2,3],[1,None,5,10],2).value,[1,2,5,10])
    close('Chebyshev recurrence', ch1.chebyshev_value(3,.5), -1)
    close('Point error bound', ch1.interpolation_error_bound([0,1,2],.5,6).value, .375)
    close('Equal-grid error bound', ch1.interpolation_global_bound([0,1,2],6,'cách đều').value,.5)
    close('Chebyshev global bound', ch1.chebyshev_global_bound(3,0,2,6).value,.25)
    close('Thomas example', ch1.thomas([0,-1,-1],[2,2,2],[-1,-1,0],[1,0,1]).value,[1,1,1])
    close('Gauss pivot example', ch1.gaussian_elimination([[0,2],[1,1]],[4,3]).value,[1,2])
    close('Newton nested API', ch1.newton_horner([0,1,3],[1,2,1],2),7)
    nodes, coef = ch1.newton_append([0,1],[1,2],3,13)
    close('Newton append', coef,[1,2,1])
    for left,right,name in (((0,1,0),(0,1,1),'Dirichlet'),((1,1,0),(1,1,3),'Robin')):
        r=de.bvp('1','0','-2',0,1,.5,left,right)
        close('BVP '+name,r.value[1],[0,.25,1])
    for weight in (1,4):
        r=de.eigen('1','0',str(weight),0,1,1/3,2)
        eig,xv,uv=r.value;close('Eigen weights '+str(weight),eig,np.array([9,27])/weight)
        K=np.array([[18.,-9.],[-9.,18.]])
        close('Eigen residual '+str(weight), K@uv[1:-1]-weight*uv[1:-1]*eig, np.zeros((2,2)))

    # Đề thật: chạy lại đầu vào hiện có, không dùng HTML/TXT cũ làm bộ tính.
    exams={
        'de_20241/A_Horner.json': ('horner',None),
        'de_20241/C_Stirling_9.json': ('poly',(4,5.442986424022284,-2.673281525949639)),
        'de_20241/D1_Lap_tien.json': ('inverse',(2.7287329703355185,13)),
        'de_20241/D2_Lap_tien.json': ('inverse',(3.760763188337928,9)),
        'de_20241/D3_Lap_tien.json': ('inverse',(8.352578825687841,6)),
        'de_20241/D4_Lap_lui.json': ('inverse',(10.641567176922276,4)),
        'de_20251/03a_Stirling_7.json': ('poly',(2.55,.6436027148241059,-.9878215414529198)),
        'de_20251/03b_Bessel_8.json': ('poly',(2.55,.6440331622320021,-.9859948454131918)),
    }
    for path,(kind,expected) in exams.items():
        task=json.loads((ROOT/'examples'/path).read_text(encoding='utf-8-sig'))
        r=dispatch(task['tool'],task['method'],task['values'],task.get('x',''),task.get('y',''))
        if kind=='poly':
            z,v,d=expected; close(path,[r.value(z),r.value.deriv()(z)],[v,d],2e-10)
        elif kind=='inverse':
            assert not state(r)['failure'];close(path,r.value,expected[0])
            assert len(state(r)['iteration']['history'])==expected[1]
        else:
            # Đạo hàm trực tiếp từ đúng hệ số là phép tính đại số đối chiếu.
            c=np.polynomial.Polynomial([1.54,-15.28,0,5.63,-2.78,3.5])
            close(path+' derivative2/3',[c.deriv(2)(2.57),c.deriv(3)(2.57)],[1054.696646,1249.3386])

    weighted=dispatch('Bình phương tối thiểu','Tuyến tính theo cơ sở',
        {'basis':'1;x','weights':'1 2 1','solver':'QR'},'0 1 2','1 2 2')
    assert not state(weighted)['failure']
    export_html(weighted,EXAMPLES/'QR_trong_so.html')
    tasks={
      '01_Horner':{'tool':'Đạo hàm & Horner','method':'Horner','values':{'coef':'3 0 -2 -1','target':2,'order':3}},
      '02_Nguoc_co_can':{'tool':'Nội suy ngược','method':'Lặp có cận co','values':{'target':2,'a':0,'b':1,'tol':1e-6,'residual_tol':1e-6,'direction':'Tiến'},'x':[0,1,2],'y':[1,3.1,5.4]},
      '03_Spline_bac4_phai':{'tool':'Spline','method':'Biên tổng quát','values':{'degree':4,'conditions':[['phải',1,32],['phải',2,48],['phải',3,48]],'target':1.5},'x':[0,1,2],'y':[0,1,16]},
      '04_QR_trong_so':{'tool':'Bình phương tối thiểu','method':'Tuyến tính theo cơ sở','values':{'basis':'1;x','weights':'1 2 1','solver':'QR'},'x':[0,1,2],'y':[1,2,2]},
      '05_Hinh_thang_Runge':{'tool':'Tích phân','method':'Hình thang','values':{'expr':'x^2','a':0,'b':1,'n':2,'tol':.001,'source':'Hàm'}},
      '06_Adams3':{'tool':'Phương trình vi phân','method':'Adams 3','values':{'expr':'x','initial':'1','a':0,'b':.3,'h':.1,'tol':1e-10}},
      '07_Bien_Robin':{'tool':'Bài toán biên','method':'Biên tổng quát','values':{'p':'1','q':'0','f':'-2','a':0,'b':1,'h':.5,'left':'1 1 0','right':'1 1 3'}},
      '08_Tri_rieng':{'tool':'Bài toán biên','method':'Trị riêng','values':{'p':'1','q':'0','f':'1','a':0,'b':1,'h':1/3,'count':2}},
    }
    for name,task in tasks.items():
        task.setdefault('x','');task.setdefault('y','')
        (EXAMPLES/(name+'.json')).write_text(json.dumps(task,ensure_ascii=False,indent=2),encoding='utf-8')
        report=dispatch(task['tool'],task['method'],task['values'],task['x'],task['y'])
        assert not state(report).get('failure'),name
        (EXAMPLES/(name+'.txt')).write_text(report.text(),encoding='utf-8')

    mapping={
      'Nội suy đa thức':('01_noi_suy_horner.tex','Đa thức theo đúng tập mốc; Newton 4 lựa chọn mốc/hướng'),
      'Spline':('03_spline.tex','Biên, hệ số mảnh, khử/thế, đạo hàm/tích phân và giới hạn'),
      'Bình phương tối thiểu':('04_binh_phuong_toi_thieu.tex','Input từng mô hình, bảng biến đổi và tổng quát, lập hệ, khôi phục tham số, vòng LM và output'),
      'Nội suy ngược':('02_noi_suy_nguoc.tex','Chọn nhánh, mô hình, khởi tạo, tiêu chuẩn dừng và lịch sử'),
      'Chọn mốc':('01_noi_suy_horner.tex','Cửa sổ/đảo mức/Chebyshev; quét nhánh ở chương02'),
      'Đạo hàm & Horner':('01_noi_suy_horner.tex','Horner; đạo hàm trực tiếp từ bảng ở chương05'),
      'Tích phân':('05_dao_ham_tich_phan.tex','Hàm/bảng, trọng số, cận sai số/Runge; hình chữ nhật 2D'),
      'Phương trình vi phân':('06_phuong_trinh_vi_phan.tex','Công thức từng bước/tầng, Adams2..5, RK tham số/tùy chỉnh'),
      'Bài toán biên':('07_bien_tri_rieng.tex','Nửa ô Robin; ma trận trị riêng đối xứng, sai số lưới'),
    }
    with (OUT/'coverage.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['Nhóm GUI','Phương pháp','Chương nguồn','Nội dung'])
        for tool,(methods,_) in TOOLS.items():
            for method in methods:
                chapter,desc=mapping[tool]
                if method=='Đạo hàm từ bảng':chapter='05_dao_ham_tich_phan.tex'
                w.writerow([tool,method,chapter,desc])
    source_paths=list((ROOT/'pps').glob('*.py'))+list((OUT.parent/'chapters').glob('*.tex'))
    source_paths+=[OUT.parent/'So_tay_PPS.tex']+list(OUT.glob('*.py'))
    source_paths+=list(OUT.glob('*.tex'))
    source_paths+=list((ROOT/'kienthuc'/'real').glob('*'))
    source_paths += [ROOT/'kienthuc'/v for v in ('20241_MI3042_GK.jpg','20241GKtest2.xlsx','20251_MI3042_GK.jpg','20251GKtest2.xlsx')]
    hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths if p.is_file()}
    (OUT/'source_sha256.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'manual_examples.json').write_text(json.dumps({'checks':checked,'gui_methods':sum(len(v[0]) for v in TOOLS.values())},
        ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    print('PASS:',len(checked),'numeric/trace checks;',sum(len(v[0]) for v in TOOLS.values()),'GUI methods mapped.')


if __name__=='__main__':main()
