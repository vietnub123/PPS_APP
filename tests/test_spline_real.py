"""Đối chiếu độc lập các bài spline trong real và dữ liệu thi tự dựng."""
from fractions import Fraction as F
import math
import tempfile
from pathlib import Path
import unittest

import numpy as np
from numpy.testing import assert_allclose
from scipy.interpolate import CubicSpline

from pps.spline_worked import solve_spline
from pps.math_view import math_png,export_html


def info(report):return report.presentation['worked_solution']


class SplineReal(unittest.TestCase):
    def test_linear_and_quadratic_pdf_values_and_nodal_derivative(self):
        r=solve_spline([0,1,2],[0,1,0],'Tuyến tính',target=.5)
        self.assertEqual(info(r)['evaluation']['value'],F(1,2))
        r=solve_spline([0,1,2],[0,1,0],'Tuyến tính',target=1,order=1)
        self.assertEqual(info(r)['status'],'evaluation_failed')
        self.assertFalse(info(r)['evaluation']['common_derivative'])
        self.assertIsNotNone(r.value)
        r=solve_spline([0,1,2],[0,1,0],'Bậc hai — biên trái',left=0,target=1.5)
        self.assertEqual(info(r)['slopes_at_nodes'],[F(0),F(2),F(-4)])
        self.assertEqual(info(r)['evaluation']['value'],F(5,4))
        assert_allclose(r.value.c,[[1,-3],[0,2],[0,1]])

    def test_natural_pdf_thomas_is_actual_solver_and_preserves_every_parameter(self):
        r=solve_spline([0,1,2,3],[0,1,0,1],target=1.5)
        d=info(r)
        self.assertIsNone(d['failure']);self.assertEqual(d['moments'],[F(0),F(-4),F(4),F(0)])
        self.assertEqual(d['evaluation']['value'],F(1,2))
        self.assertEqual(d['solver']['kind'],'Thomas hữu tỷ')
        self.assertEqual(len(d['solver']['forward']),4)
        self.assertEqual(len(d['solver']['backward']),4)
        self.assertEqual(d['solver']['forward'][2]['factor'],F(1,4))
        self.assertEqual(d['solver']['forward'][2]['pivot'],F(15,4))
        self.assertEqual(d['solver']['forward'][2]['reduced_rhs'],F(15))
        self.assertTrue(all(c['passed'] for c in d['checks']))

    def test_nonuniform_natural_and_clamped_pdf_examples(self):
        r=solve_spline([0,1,3],[0,1,0],target=2)
        self.assertEqual(info(r)['moments'],[F(0),-F(3,2),F(0)])
        self.assertEqual(info(r)['evaluation']['value'],F(7,8))
        r=solve_spline([0,1,2],[0,1,0],'Cubic kẹp',left=2,right=-2,target=.5)
        self.assertEqual(info(r)['moments'],[F(-2)]*3)
        self.assertEqual(info(r)['evaluation']['value'],F(3,4))
        for z in np.linspace(0,2,11):self.assertAlmostEqual(r.value(z),2*z-z*z,places=13)

    def test_right_quadratic_and_mixed_boundary_reproduce_known_polynomial(self):
        x=np.array([-2,-.2,.5,2,4]);y=x*x+3*x-1
        r=solve_spline(x,y,'Bậc hai — biên phải',right=11,target=0)
        self.assertIsNone(info(r)['failure']);assert_allclose(r.value(np.linspace(-2,4,37)),np.linspace(-2,4,37)**2+3*np.linspace(-2,4,37)-1,atol=3e-14)
        r=solve_spline(x,x**3-2*x+4,'Cubic hỗn hợp',left=10,right=24,boundary_orders=(1,2))
        self.assertIsNone(info(r)['failure'])
        z=np.linspace(-2,4,37);assert_allclose(r.value(z),z**3-2*z+4,atol=5e-13)

    def test_periodic_notaknot_and_general_boundary_keep_actual_solver(self):
        r=solve_spline([0,1,2],[0,1,0],'Cubic tuần hoàn')
        self.assertEqual(info(r)['moments'],list(map(F,[6,-6,6])))
        self.assertIn('Gauss',info(r)['solver']['kind'])
        self.assertAlmostEqual(r.value(0,1),r.value(2,1),places=14)
        x=[-1,0,2,3,5];y=[v**3-2*v+1 for v in x]
        r=solve_spline(x,y,'Cubic not-a-knot')
        z=np.linspace(-1,5,21);assert_allclose(r.value(z),z**3-2*z+1,atol=1e-12)
        r=solve_spline([0,1,2],[0,1,0],'Biên tổng quát',degree=3,
                       conditions=[['trái',1,2],['phải',1,-2],['trái',2,-2]])
        self.assertIsNone(info(r)['failure'])
        self.assertGreater(info(r)['solver']['equations'],info(r)['solver']['unknowns'])
        self.assertAlmostEqual(r.value(.5),.75)

    def test_missing_incompatible_and_dependent_conditions_have_distinct_reason(self):
        for options,fragment in [({'conditions':[]},'chưa xác định'),
                                 ({'conditions':[['trái',1,0],['trái',1,1]]},'không tương thích'),
                                 ({'conditions':[['trái',1,0],['trái',1,0]]},'chưa xác định')]:
            r=solve_spline([0,1,2],[0,1,0],'Biên tổng quát',degree=3,**options)
            self.assertIsNone(r.value);self.assertIn(fragment,info(r)['failure']['message'].lower())
        r=solve_spline([0,1],[0,1],'Cubic kẹp',left=1)
        self.assertIn('Thiếu',info(r)['failure']['message'])

    def test_degree_four_and_general_degree_use_simultaneous_derivative_transfer(self):
        r=solve_spline([0,1,2],[0,1,0],'Bậc 4 — đạo hàm trái',derivatives=np.array([1,0,0]),target=1.5)
        self.assertIsNone(info(r)['failure']);assert_allclose(r.value.c[:,0],[0,0,0,1,0])
        assert_allclose(r.value.c[:,1],[-2,0,0,1,1])
        self.assertEqual(info(r)['evaluation']['value'],F(11,8))
        x=[-1,0,1,2];degree=5
        def f(z):return z**5-2*z**3+z-4
        derivatives=[0,-8,48,-120]  # f'(-1),f''(-1),f'''(-1),f''''(-1)
        # Correct analytic derivatives: 5x^4−6x²+1;20x³−12x;60x²−12;120x.
        r=solve_spline(x,[f(z) for z in x],'Đạo hàm đầu trái',degree=degree,derivatives=derivatives)
        self.assertIsNone(info(r)['failure']);z=np.linspace(-1,2,31);assert_allclose(r.value(z),[f(v) for v in z],atol=1e-12)

    def test_endpoint_high_derivative_and_integral_are_piecewise_correct(self):
        r=solve_spline([0,1,2,3],[0,1,0,1],target=3,order=2,integral_a=3,integral_b=0)
        self.assertEqual(info(r)['evaluation']['segment'],2)
        self.assertEqual(info(r)['evaluation']['value'],0)
        self.assertEqual(info(r)['integral']['value'],-F(3,2))
        self.assertEqual(len(info(r)['integral']['rows']),3)
        r=solve_spline([0,1,2,3],[0,1,0,1],target=1,order=4)
        self.assertEqual(info(r)['status'],'evaluation_failed')
        self.assertIn('cấp 3',info(r)['failure']['message'])

    def test_extrapolation_and_invalid_data_are_not_silently_changed(self):
        r=solve_spline([0,1],[0,1],'Tuyến tính',target=2)
        self.assertIsNotNone(r.value);self.assertEqual(info(r)['status'],'evaluation_failed')
        r=solve_spline([0,1],[0,1],'Tuyến tính',target=2,allow_extrapolation=True)
        self.assertEqual(info(r)['evaluation']['value'],2)
        for x,y in [([0,0],[1,2]),([0,math.nan],[0,1]),([0,1],[1])]:
            r=solve_spline(x,y);self.assertIsNone(r.value);self.assertIsNotNone(info(r)['failure'])

    def test_large_standard_grid_does_not_construct_dense_matrix(self):
        x=np.linspace(-2,3,201);r=solve_spline(x,2*x+1,target=.25)
        self.assertIsNone(info(r)['failure']);self.assertIsNone(info(r)['system']['matrix'])
        self.assertAlmostEqual(r.value(.25),1.5,places=13)
        self.assertEqual(len(info(r)['coefficients']),200)

    def test_large_periodic_and_notaknot_keep_sparse_system_and_library_trace(self):
        x=np.linspace(0,2*math.pi,101);y=np.sin(x);y[-1]=y[0]
        r=solve_spline(x,y,'Cubic tuần hoàn',target=x[25],order=1)
        self.assertIsNone(info(r)['failure']);self.assertIsNone(info(r)['system']['matrix'])
        self.assertIn('SciPy',info(r)['solver']['kind'])
        self.assertEqual(len(info(r)['system']['sparse_rows']),101)
        x=np.linspace(-2,3,101);y=x*x
        r=solve_spline(x,y,'Cubic not-a-knot',target=.5)
        self.assertIsNone(info(r)['failure']);self.assertAlmostEqual(r.value(.5),.25,places=12)

    def test_random_nonuniform_solutions_match_independent_library(self):
        rng=np.random.default_rng(2025)
        for kind,bc,left,right in [('Cubic tự nhiên','natural',None,None),
                                    ('Cubic kẹp',((1,.7),(1,-.2)),.7,-.2),
                                    ('Cubic đạo hàm bậc hai',((2,1.2),(2,-.6)),1.2,-.6)]:
            x=np.cumsum(rng.uniform(.1,1,9));y=rng.normal(size=9)
            r=solve_spline(x,y,kind,left,right)
            self.assertIsNone(info(r)['failure']);z=np.linspace(x[0],x[-1],101)
            assert_allclose(r.value(z),CubicSpline(x,y,bc_type=bc)(z),atol=3e-12,rtol=1e-12)

    def test_reports_render_all_formulas_and_export_full_trace(self):
        reports=[solve_spline([0,1,2,3],[0,1,0,1],target=1.5),
                 solve_spline([0,1,3],[0,1,0],target=2,order=1,integral_a=0,integral_b=3),
                 solve_spline([0,1,2],[0,1,0],'Bậc 4 — đạo hàm trái',derivatives=[1,0,0])]
        for r in reports:
            self.assertIn('worked_layout',r.presentation)
            self.assertIn('Thế ngược',r.text()) if info(r)['method'].startswith('Cubic') else None
            for kind,value in r.presentation['blocks']:
                if kind=='formula':self.assertTrue(math_png(value).startswith(b'\x89PNG'))
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'spline.html';export_html(reports[0],path)
            html=path.read_text(encoding='utf-8')
            self.assertIn('Thomas',html);self.assertIn('data:image/png;base64,',html)
            self.assertNotIn('src="http',html)


if __name__=='__main__':unittest.main()
