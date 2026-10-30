"""Đối chiếu đề ảnh và dữ liệu 20251GKtest2.xlsx do người dùng cung cấp."""
from pathlib import Path
import unittest

import numpy as np
from numpy.testing import assert_allclose
from openpyxl import load_workbook
from scipy.interpolate import CubicSpline
from scipy.optimize import least_squares, brentq

from pps.common import data_pairs
from pps.gui import dispatch


ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'kienthuc'/'20251GKtest2.xlsx'


def exam_data():
    workbook=load_workbook(SOURCE,read_only=True,data_only=True)
    try:rows=list(workbook.active.values)
    finally:workbook.close()
    xy=np.asarray(data_pairs(rows),float)
    return xy[:,0],xy[:,1],float(rows[1][3]),float(rows[1][4])


class ActualExam20251(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x,cls.y,cls.xbar,cls.ybar=exam_data()

    def test_full_import_keeps_negative_rows_and_metadata(self):
        self.assertEqual(len(self.x),104)
        self.assertEqual((self.xbar,self.ybar),(2.55,1.23))
        self.assertTrue(np.any(self.y<0))
        assert_allclose(np.diff(self.x),.115,atol=2e-15,rtol=0)

    def test_exam_exponential_log_domain_is_reported_without_deleting_rows(self):
        for basis in ('x;1/x','x^2;1/x'):
            report=dispatch('Bình phương tối thiểu','Hàm mũ',{'basis':basis},self.x,self.y)
            data=report.presentation['worked_solution']
            self.assertIsNotNone(data['failure'])
            self.assertIsNone(report.value)
            self.assertEqual(len(data['x']),104)
            self.assertIn('log',str(data['failure']).lower())

    def test_both_printed_exponential_forms_fit_raw_sse_on_all_104_rows(self):
        # Ảnh có hai mẫu b*x và b*x²; cùng kiểm trên đúng tệp được cấp,
        # không tự gán tệp test2 thành dữ liệu test1 chưa được cung cấp.
        for power,initial in ((1,[12,-1.3,1]),(2,[1.5,-.25,2])):
            with self.subTest(power=power):
                basis='x;1/x' if power==1 else 'x^2;1/x'
                report=dispatch('Bình phương tối thiểu','Hàm mũ — SSE thang y',
                    {'basis':basis,'solver':'Levenberg–Marquardt','max_iter':'200','tol':'1e-11'},self.x,self.y)
                data=report.presentation['worked_solution']
                self.assertIsNone(data['failure'],str(data['failure']))
                reference=least_squares(lambda p:p[0]*np.exp(p[1]*self.x**power+p[2]/self.x)-self.y,
                                         initial,x_scale='jac',ftol=1e-13,xtol=1e-13,gtol=1e-13,max_nfev=1000)
                prediction=report.value(self.x)
                sse=float(np.sum((prediction-self.y)**2))
                self.assertAlmostEqual(sse,float(np.sum(reference.fun**2)),places=9)
                self.assertEqual(len(data['x']),104)
                self.assertTrue(data['solver_trace']['iterations'])

    def test_inverse_local_models_have_independent_bracketed_reference(self):
        for direction,indices in [('Tiến',[9,10,11,12]),('Lùi',[7,8,9,10])]:
            with self.subTest(direction=direction):
                report=dispatch('Nội suy ngược','Lặp có cận co',
                    {'target':str(self.ybar),'a':'2.035','b':'2.15','tol':'1e-9','residual_tol':'1e-9',
                     'direction':direction,'selected_indices':indices},self.x,self.y)
                data=report.presentation['inverse_solution']
                self.assertIsNone(data['failure'],str(data['failure']))
                # Đa thức thuận được dựng độc lập ở biến địa phương có thang1.
                xx=self.x[indices];yy=self.y[indices];origin=xx[0];h=xx[1]-xx[0]
                coeff=np.polynomial.polynomial.polyfit((xx-origin)/h,yy,3)
                reference=brentq(lambda z:np.polynomial.polynomial.polyval((z-origin)/h,coeff)-self.ybar,
                                 2.035,2.15,xtol=1e-14)
                self.assertLessEqual(abs(report.value-reference),float(data['result']['iteration_error_bound_x'])+1e-12)
                self.assertEqual(len(data['original_rows']),104)
                self.assertEqual(data['selection']['indices'],indices)
                self.assertEqual(len(data['iteration']['history']),data['iterations_done'])

    def test_whole_real_table_is_attempted_without_invented_missing_nodes(self):
        for method,anchor in [('Lặp tiến',self.x[0]),('Lặp lùi',self.x[-1])]:
            report=dispatch('Nội suy ngược',method,
                {'target':'1.23','a':'2.035','b':'2.15','max_iter':'3'},self.x,self.y)
            data=report.presentation['inverse_solution']
            self.assertNotIn(data['status'],('insufficient_nodes','invalid_stencil'))
            self.assertEqual(len(data['used_rows']),104)
            self.assertAlmostEqual(float(data['model']['anchor']),anchor)
            self.assertTrue(data['iteration']['history'])

    def test_actual_stirling_and_bessel_value_and_derivative(self):
        for method,count in [('Stirling',7),('Bessel',8)]:
            report=dispatch('Nội suy đa thức',method,
                            {'target':'2.55','order':'1','count':str(count)},self.x,self.y)
            selected=np.sort(np.argsort(abs(self.x-self.xbar),kind='stable')[:count])
            xx=self.x[selected];yy=self.y[selected];origin=self.xbar;scale=.115
            # Lagrange dưới dạng tích và đạo hàm tích, không dùng core nội suy.
            value=derivative=0.
            for i in range(count):
                nodes=(xx-origin)/scale;den=np.prod([nodes[i]-nodes[j] for j in range(count) if j!=i])
                value+=yy[i]*np.prod([-nodes[j] for j in range(count) if j!=i])/den
                derivative+=yy[i]*sum(np.prod([-nodes[j] for j in range(count) if j!=i and j!=k])
                                      for k in range(count) if k!=i)/den/scale
            self.assertAlmostEqual(report.value(self.xbar),value,places=10)
            self.assertAlmostEqual(report.value.deriv()(self.xbar),derivative,places=9)

    def test_spline_on_actual_data_preserves_nodes_and_query(self):
        report=dispatch('Spline','Cubic tự nhiên',{'target':'2.55','order':'1',
                        'integral_a':'2.035','integral_b':'2.955'},self.x,self.y)
        self.assertIsNone(report.presentation['worked_solution']['failure'])
        reference=CubicSpline(self.x,self.y,bc_type='natural')
        assert_allclose(report.value(self.x),self.y,atol=2e-12)
        self.assertAlmostEqual(report.value(2.55),reference(2.55),places=10)
        self.assertAlmostEqual(report.value(2.55,nu=1),reference(2.55,nu=1),places=9)
        self.assertAlmostEqual(report.value.integrate(2.035,2.955),reference.integrate(2.035,2.955),places=10)
