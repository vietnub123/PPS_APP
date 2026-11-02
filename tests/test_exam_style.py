"""Kiểm tra tính trung thực của lời giải, bảng ngang và các tầng thực tính."""
from fractions import Fraction as F
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

from pps import interpolation as ip, differential as de, calculus as ca
from pps.exam_style import outline
from pps.gui import TOOLS, dispatch, _dispatch, fields
from pps.least_squares_worked import solve_least_squares
from pps.math_view import export_html, math_png
from pps.spline_worked import solve_spline


def nodes(layout):
    for node in layout:
        yield node
        yield from nodes(node.get('children',[]))


class ExamStyleTests(unittest.TestCase):
    def test_every_gui_choice_has_its_own_algorithm_outline(self):
        total=0
        for tool,(methods,_) in TOOLS.items():
            for method in methods:
                total+=1
                with self.subTest(tool=tool,method=method):
                    recipe=outline(tool,method)
                    self.assertGreaterEqual(len(recipe['steps']),3)
                    self.assertTrue(recipe['output'])
        self.assertEqual(total,58)
        self.assertNotEqual(outline('Spline','Cubic kẹp'),outline('Spline','Cubic tự nhiên'))
        self.assertNotEqual(outline('Bình phương tối thiểu','Hàm mũ'),outline('Bình phương tối thiểu','Hàm mũ — SSE thang y'))

    def test_numpy_input_and_legacy_newton_remain_supported(self):
        x=np.arange(5.);y=x*x
        values={'target':'1.5','order':'1','count':'5'}
        report=dispatch('Nội suy đa thức','Stirling',values,x,y)
        reference=_dispatch('Nội suy đa thức','Stirling',values,x,y)
        np.testing.assert_array_equal(report.value(x),reference.value(x))
        self.assertIn('exam_style',report.presentation)
        legacy=dispatch('Newton','Mốc bất kỳ',{'target':'1.5','direction':'Lùi'},x,y)
        self.assertAlmostEqual(legacy.value(1.5),2.25)

    def test_image_stirling_exact_oracle_detects_missing_terms(self):
        xx=list(map(F,['3.760','3.875','3.990','4.105','4.220','4.335','4.450']))
        yy=list(map(F,['-.9384','-.8979','-.8110','-.8056','-.7548','-.7416','-.7049']))
        # Oracle Lagrange rationnel, indépendant du choix des différences Stirling.
        z=F('4.15');p=F(0);dp=F(0)
        for i,x in enumerate(xx):
            others=[v for j,v in enumerate(xx) if j!=i]
            den=math.prod(x-v for v in others)
            p+=yy[i]*math.prod(z-v for v in others)/den
            dp+=yy[i]*sum(math.prod(z-v for k,v in enumerate(others) if k!=j) for j in range(len(others)))/den
        r=ip.interpolate(list(map(float,xx)),list(map(float,yy)),'Stirling',float(z),1)
        self.assertAlmostEqual(r.value(float(z)),float(p),places=14)
        self.assertAlmostEqual(r.value.deriv()(float(z)),float(dp),places=14)
        self.assertAlmostEqual(float(p),-.791227553803524,places=14)
        t=F(9,23);truncated=F('-.8056')+F('.0281')*t+F('.0227')*t*t
        self.assertGreater(abs(float(p-truncated)),9e-5)
        horizontal=[(name,head,rows) for name,head,rows in r.tables if name.startswith('Horner theo t')]
        self.assertEqual(len(horizontal),2)
        for _,head,rows in horizontal:
            self.assertEqual(len(rows),3)
            self.assertEqual(len(rows[0]),len(head))

    def test_horner_horizontal_shift_and_remainder_are_explicit(self):
        r=ip.horner([3,0,-2,-1],2,2)
        rows=[rows for title,_,rows in r.tables if title.startswith('Sơ đồ Horner ngang')]
        self.assertEqual(len(rows),3)
        self.assertEqual(rows[0][0][1:],['3','0','-2','-1'])
        self.assertEqual(rows[0][1][1:],[ '—','6','12','20'])
        self.assertEqual(rows[0][2][1:],['3','6','10','19'])
        self.assertEqual(r.value,19)
        self.assertIn('2!·s_2',r.text())

    def test_ls_symbolic_system_simplifies_x_times_reciprocal(self):
        x=np.arange(1.,6.);y=-2*np.exp(-.3*x+.8/x)
        r=solve_least_squares(x,y,'Hàm mũ',['x','1/x'])
        data=r.presentation['worked_solution']
        self.assertIsNone(data['failure'])
        rows=next(rows for title,_,rows in r.tables if title=='Khuôn hệ chuẩn theo các cơ sở đã chọn')
        self.assertEqual(rows[1][3],'N');self.assertEqual(rows[2][2],'N')
        np.testing.assert_allclose([float(v) for v in data['coefficients']],[math.log(2),-.3,.8],atol=2e-14)
        for _,formulas in r.presentation['formulas']:
            for formula in formulas:self.assertTrue(math_png(formula))
        bad=solve_least_squares([1,2,3],[-2,-1,.1],'Hàm mũ',['x'])
        self.assertIsNone(bad.value)
        self.assertEqual(len(bad.presentation['worked_solution']['y']),3)

    def test_rk_stage_table_matches_actual_step_without_extra_rhs_calls(self):
        from unittest.mock import patch
        from pps.common import function as original
        evaluations=[]
        def counted(*args,**kwargs):
            f=original(*args,**kwargs)
            def evaluate(*a):evaluations.append(a);return f(*a)
            return evaluate
        with patch('pps.differential.function',side_effect=counted):
            r=de.ode(['x'],[1],0,.1,.1,'RK4')
        trace=r.presentation['ode_trace'][0]
        self.assertEqual(len(evaluations),4)
        np.testing.assert_allclose([s['state'][0] for s in trace['stages']],[1,1.05,1.0525,1.10525])
        np.testing.assert_allclose([s['slope'][0] for s in trace['stages']],[1,1.05,1.0525,1.10525])
        self.assertAlmostEqual(1+sum(s['increment'][0] for s in trace['stages']),r.value[1][1,0])
        r=de.ode(['y','-x'],[1,0],0,.2,.1,'RK2')
        self.assertEqual(len(r.presentation['ode_trace']),2)
        self.assertEqual(r.presentation['ode_trace'][0]['stages'][0]['slope'].shape,(2,))

    def test_adams_keeps_startup_and_actual_predictor_corrector(self):
        r=de.ode(['x'],[1],0,.4,.1,'Adams 3')
        steps=r.presentation['ode_trace']
        self.assertEqual([s['kind'] for s in steps[:2]],['RK4 khởi tạo Adams']*2)
        step=steps[2]
        expected=step['state']+.1*sum(c*v for c,v in zip(de.AB[3],step['history']))
        np.testing.assert_array_equal(step['predicted'],expected)
        self.assertLess(step['implicit']['residual'],1e-10)
        self.assertGreaterEqual(step['implicit']['nfev'],1)
        self.assertIn('không phải số vòng Newton',r.text())

    def test_spline_coordinate_transform_includes_boundary_derivatives(self):
        x=np.array([1000.,1002,1004,1006]);u=(x-1000)/2
        y=5+4*(u**3+u)
        # y'=4/2*(3u²+1); phải đổi đạo hàm biên khi đưa về u,v.
        a=solve_spline(x,y,'Cubic kẹp',2,56,1003)
        b=solve_spline(u,(y-5)/4,'Cubic kẹp',1,28,1.5)
        self.assertIsNone(a.presentation['worked_solution']['failure'])
        self.assertAlmostEqual(a.value(1003),5+4*b.value(1.5),places=12)
        self.assertAlmostEqual(a.value.derivative()(1003),2*b.value.derivative()(1.5),places=12)

    def test_double_integral_reports_main_grid_not_the_probe(self):
        r=ca.double_integral('x^2+y^2',1,0,0,1,4,'Simpson',1e-8)
        grid=r.presentation['quadrature_grid']
        self.assertEqual(grid['n'],r.tables[0][2][-1][0])
        self.assertNotEqual(grid['n'],r.tables[1][2][-1][1])
        weights=grid['weights'];values=grid['values'];n=grid['n']
        self.assertEqual(values.shape,(n+1,n+1))
        independently=-float(weights@values@weights)/n**2
        self.assertAlmostEqual(independently,r.value,places=14)
        self.assertAlmostEqual(r.value,-2/3,places=14)

    def test_eigen_operator_table_matches_returned_pairs(self):
        r=de.eigen('1+x','2','1+x',0,1,.25,2)
        _,_,rows=r.tables[-1]
        diagonal=np.array([float(row[3]) for row in rows])
        off=np.array([float(row[4]) for row in rows[:-1]])
        operator=np.diag(diagonal)+np.diag(off,1)+np.diag(off,-1)
        eig,x,u=r.value
        transformed=np.sqrt(1+x[1:-1,None])*u[1:-1]
        np.testing.assert_allclose(operator@transformed,transformed*eig,atol=1e-12)
        np.testing.assert_allclose(np.max(abs(u),axis=0),np.ones(2))

    def test_new_layout_exports_all_saved_tables_and_implicit_details(self):
        values={k:d for k,_,d,_ in fields('Phương trình vi phân','Euler ẩn')}
        r=dispatch('Phương trình vi phân','Euler ẩn',values,'','')
        layout=r.presentation['worked_layout']
        self.assertEqual(sum(n['kind']=='table' for n in nodes(layout)),len(r.tables))
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'implicit.html';export_html(r,path)
            content=path.read_text(encoding='utf-8')
            self.assertIn('nfev',content)
            self.assertIn('beforeprint',content)
            self.assertIn('Times New Roman',content)
            self.assertIn('Output cần đọc',content)


if __name__=='__main__':unittest.main()
