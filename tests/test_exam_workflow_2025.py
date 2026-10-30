"""Các ca mô phỏng bài thi 2025; không phải dữ liệu đề gốc chưa được cung cấp."""
from decimal import Decimal
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np
from numpy.testing import assert_allclose

from pps.gui import dispatch
from pps.math_view import export_html, math_png


def table36():
    x=[Decimal(1)+Decimal('.115')*i for i in range(36)]
    y=[2*v-Decimal('2.95') for v in x]
    return ' '.join(map(str,x)),' '.join(map(str,y))


class ExamWorkflow2025(unittest.TestCase):
    def test_exponential_json_without_basis_keeps_the_standard_two_parameter_model(self):
        for method in ('Hàm mũ','Hàm mũ — SSE thang y'):
            report=dispatch('Bình phương tối thiểu',method,{},[0,1,2],[2,4,8])
            data=report.presentation['worked_solution']
            self.assertIsNone(data['failure'],str(data['failure']))
            self.assertEqual(len(data['coefficients']),2)
            assert_allclose(report.value(np.array([0.,1.,2.])),[2,4,8],atol=1e-9)

    def test_whole_36_node_table_middle_bracket_keeps_data_and_origin(self):
        x,y=table36()
        for method,origin,interval in [('Lặp tiến',1,(9,10)),('Lặp lùi',5.025,(-26,-25))]:
            with self.subTest(method=method):
                r=dispatch('Nội suy ngược',method,
                           {'target':'1.23','a':'2.035','b':'2.15','tol':'1e-8',
                            'residual_tol':'1e-8','max_iter':'100'},x,y)
                d=r.presentation['inverse_solution']
                self.assertIsNone(d['failure'],str(d['failure']))
                self.assertAlmostEqual(r.value,2.09,places=10)
                self.assertEqual(len(d['used_rows']),36)
                self.assertEqual(d['degree'],35)
                self.assertAlmostEqual(float(d['model']['anchor']),origin)
                assert_allclose([float(v) for v in d['iteration']['T']],interval,atol=1e-12)
                self.assertNotEqual(d['status'],'insufficient_nodes')

    def test_nonuniform_spline_boundary_derivative_and_integral_in_one_run(self):
        x=np.array([0,.25,.8,1.4,2.])
        y=x**3-2*x+1
        r=dispatch('Spline','Cubic kẹp',
                   {'left':'-2','right':'10','target':'.7','order':'1',
                    'integral_a':'0','integral_b':'2','solver':'Thomas'},x.tolist(),y.tolist())
        d=r.presentation['worked_solution']
        self.assertIsNone(d.get('failure'),str(d.get('failure')))
        z=np.linspace(0,2,23)
        assert_allclose(r.value(z),z**3-2*z+1,atol=2e-12)
        self.assertAlmostEqual(r.value(.7,nu=1),3*.7**2-2,places=11)
        self.assertAlmostEqual(r.value.integrate(0,2),2,places=11)
        self.assertIn('Thomas',r.text())

    def test_regression_with_repeated_x_weights_and_three_solvers(self):
        x=[0,0,1,2,3];y=[1,2,3,4,6];weights=[1,0,2,1,3]
        A=np.column_stack([np.ones(len(x)),x]);w=np.sqrt(weights)
        expected=np.linalg.lstsq(A*w[:,None],np.asarray(y)*w,rcond=None)[0]
        for solver in ('QR','Hệ chuẩn — Gauss','SVD'):
            r=dispatch('Bình phương tối thiểu','Tuyến tính theo cơ sở',
                       {'basis':'1;x','weights':weights,'solver':solver,'target':'1.5'},x,y)
            self.assertIsNone(r.presentation['worked_solution'].get('failure'),str(r.presentation['worked_solution'].get('failure')))
            assert_allclose(r.value(np.array([0,1.5,3])),expected[0]+expected[1]*np.array([0,1.5,3]),atol=2e-11)

    def test_weighted_worked_sums_match_the_displayed_normal_system(self):
        report=dispatch('Bình phương tối thiểu','Tuyến tính theo cơ sở',
                        {'basis':'1;x','weights':'1 2 1','solver':'Hệ chuẩn — Gauss'},[0,1,2],[1,2,2])
        table=next(t for t in report.tables if t[0].startswith('Bảng tổng có trọng số'))
        self.assertEqual(table[2][-1],['Tổng','4','4','7','6','8'])

    def test_raw_sse_exponential_records_actual_parameter_updates(self):
        r=dispatch('Bình phương tối thiểu','Hàm mũ — SSE thang y',
                   {'basis':'x','solver':'Levenberg–Marquardt','initial':'1 0',
                    'max_iter':'100','tol':'1e-10'},'0 1 2','2 5 18')
        d=r.presentation['worked_solution']
        self.assertIsNone(d.get('failure'),str(d.get('failure')))
        prediction=np.asarray(r.value(np.array([0,1,2.])))
        self.assertLess(float(np.sum((prediction-[2,5,18])**2)),.29)
        self.assertIn('Levenberg',r.text())
        self.assertTrue(d.get('iterations') or d.get('iteration_history') or d.get('solver_trace'))
        self.assertFalse(any(title=='Hệ chuẩn và vế phải' for title,_,_ in r.tables))
        self.assertIn('ρ_i=',r.text())
        self.assertTrue(any('F thử' in headers for _,headers,_ in r.tables))

    def test_all_three_worked_reports_export_offline_with_trace(self):
        x,y=table36()
        reports=[dispatch('Nội suy ngược','Lặp tiến',{'target':'1.23','a':'2.035','b':'2.15'},x,y),
                 dispatch('Spline','Cubic tự nhiên',{'target':'2'},'0 1 3','0 1 0'),
                 dispatch('Bình phương tối thiểu','Tuyến tính theo cơ sở',{'basis':'1;x','solver':'Hệ chuẩn — Gauss'},'0 1 2 3','1 2 2 4')]
        with tempfile.TemporaryDirectory() as folder:
            for i,report in enumerate(reports):
                self.assertTrue(report.presentation.get('inverse_layout') or report.presentation.get('worked_layout'))
                self.assertNotIn('\\frac',report.text())
                target=Path(folder)/f'{i}.html';export_html(report,target)
                html=target.read_text(encoding='utf-8')
                self.assertTrue('data:image/png;base64,' in html,'Missing offline formulas')
                self.assertNotIn('src="http',html)
                self.assertIn('beforeprint',html)
                for kind,value in report.presentation['blocks']:
                    if kind=='formula':self.assertTrue(math_png(value).startswith(b'\x89PNG'))
