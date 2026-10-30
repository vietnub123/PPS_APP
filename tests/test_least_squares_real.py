"""Đối chiếu độc lập PDF bình phương tối thiểu real và các tình huống thi."""
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

import numpy as np
from numpy.testing import assert_allclose
from scipy.optimize import least_squares

from pps.least_squares_worked import solve_least_squares as solve, LOG_MODEL
from pps.math_view import export_html,math_png


def data(report):return report.presentation['worked_solution']


class LeastSquaresReal(unittest.TestCase):
    def test_pdf_line_gauss_actual_pivot_trace_and_optimality(self):
        r=solve([0,1,2,3],[1,2,2,4],solver='normal_gauss');d=data(r)
        self.assertIsNone(d['failure']);assert_allclose(list(map(float,d['coefficients'])),[.9,.9],atol=1e-14)
        self.assertEqual(d['gram'],[[Decimal(4),Decimal(6)],[Decimal(6),Decimal(14)]])
        self.assertEqual(d['rhs'],[Decimal(9),Decimal(18)])
        trace=d['solver_trace'];self.assertEqual(trace['kind'],'normal_gauss')
        self.assertEqual(trace['steps'][0]['pivot_row'],1);self.assertTrue(trace['steps'][0]['swapped'])
        self.assertAlmostEqual(float(trace['steps'][0]['eliminations'][0]['multiplier']),2/3)
        self.assertAlmostEqual(float(d['metrics']['SSE_y']),.7)
        self.assertAlmostEqual(float(d['metrics']['MSE_y']),.175)
        self.assertAlmostEqual(float(d['metrics']['R_squared']),81/95)
        self.assertLess(max(map(abs,d['optimality'])),Decimal('1e-60'))

    def test_pdf_quadratic_qr_reconstructs_same_actual_design(self):
        r=solve([-2,-1,0,1,2],[5,2,1,2,6],basis=['1','x','x^2']);d=data(r)
        self.assertIsNone(d['failure']);assert_allclose(list(map(float,d['coefficients'])),[32/35,1/5,8/7],atol=1e-14)
        self.assertAlmostEqual(float(d['metrics']['SSE_y']),4/35)
        trace=d['solver_trace'];q=np.array(trace['Q'],float).T;rmat=np.array(trace['R'],float)
        assert_allclose(q@rmat,d['theta'],atol=1e-14)
        assert_allclose(q.T@q,np.eye(3),atol=1e-14)
        self.assertEqual(trace['kind'],'qr')
        self.assertNotIn('Các phép chia trong thế ngược',r.title)

    def test_pdf_log_exponential_has_separate_original_and_log_objectives(self):
        r=solve([0,1,2],[2,5,18],kind='Hàm mũ',basis=['x']);d=data(r)
        self.assertIsNone(d['failure'])
        self.assertAlmostEqual(float(d['coefficients'][1]),np.log(3),places=13)
        self.assertAlmostEqual(r.value(0),1.882072057762,places=10)
        self.assertAlmostEqual(float(d['metrics']['SSE_y']),1.55796930657563,places=12)
        self.assertAlmostEqual(float(d['metrics']['SSE_transformed']),.0221607667,places=9)
        self.assertIn('Không đồng nhất với SSE_y',r.text())

    def test_pdf_power_and_log_of_linear_combination(self):
        r=solve([1,2,4],[3,12,48],kind='Lũy thừa');d=data(r)
        self.assertIsNone(d['failure']);assert_allclose(r.value([1,2,4]),[3,12,48],atol=1e-12)
        log=solve([0,1,2],np.log([1,3,5]),kind=LOG_MODEL,basis=['1','x']);d=data(log)
        self.assertIsNone(d['failure']);self.assertEqual(d['transform'],'exp(y)')
        assert_allclose(list(map(float,d['coefficients'])),[1,2],atol=2e-15)
        self.assertAlmostEqual(log.value(0),0,places=14)
        with self.assertRaises(ValueError):log.value(-1)

    def test_zero_weights_keep_rows_and_do_not_change_objective(self):
        r=solve([0,1,2],[1,200,5],weights=[1,0,1]);d=data(r)
        self.assertIsNone(d['failure']);self.assertEqual(d['effective_observations'],2)
        self.assertEqual(len(d['residuals']),3);assert_allclose(r.value([0,1,2]),[1,3,5],atol=1e-14)
        self.assertLess(d['metrics']['weighted_objective_y'],Decimal('1e-55'))
        self.assertGreater(d['metrics']['SSE_y'],10000)
        self.assertIsNone(d['metrics']['statistical_sigma'])
        bad=solve([0,1],[1,2],weights=[0,0]);self.assertEqual(data(bad)['status'],'invalid_weights')

    def test_repeated_x_minimum_norm_requires_explicit_selection(self):
        failed=solve([1,1,1],[1,2,3]);self.assertEqual(data(failed)['status'],'rank_deficient')
        self.assertIsNone(failed.value);self.assertIn('không duy nhất',failed.text())
        r=solve([1,1,1],[1,2,3],solver='svd',rank_policy='minimum_norm');d=data(r)
        self.assertEqual(d['status'],'minimum_norm_fit')
        assert_allclose(list(map(float,d['coefficients'])),[1,1],atol=1e-14)
        self.assertAlmostEqual(float(d['metrics']['SSE_y']),2,places=13)
        self.assertEqual(len(d['x']),3)

    def test_arbitrary_basis_and_no_implicit_intercept(self):
        x=np.array([-.7,.3,1.2,2.9]);theta=np.column_stack((x,1/x));y=2*x-3/x
        r=solve(x,y,basis=['x','1/x']);d=data(r)
        self.assertEqual(d['labels'],['x','1/x']);assert_allclose(list(map(float,d['coefficients'])),[2,-3],atol=2e-14)
        bad=solve([0,1],[1,2],basis=['x','1/x']);self.assertEqual(data(bad)['status'],'basis_domain_error')
        duplicate=solve([0,1,2],[1,2,4],kind='Hàm mũ',basis=['1','x'])
        self.assertEqual(data(duplicate)['status'],'rank_deficient')

    def test_transformed_reciprocal_and_prediction_at_zero(self):
        x=np.array([1.,2.,3.,4.]);y=x/(2+3*x)
        r=solve(x,y,kind='x/(a+b*x)');d=data(r)
        self.assertIsNone(d['failure']);assert_allclose(list(map(float,d['coefficients'])),[3,2],atol=1e-13)
        self.assertAlmostEqual(r.value(0),0)
        invalid=solve([0,1],[0,.2],kind='x/(a+b*x)')
        self.assertEqual(data(invalid)['status'],'transform_domain_error')

    def test_scaled_qr_handles_large_offset_and_constant_y_r2_not_applicable(self):
        x=1e12+np.arange(4.)
        r=solve(x,[1,2,3,4]);d=data(r)
        self.assertIsNone(d['failure']);assert_allclose(r.value(x),[1,2,3,4],atol=1e-12)
        constant=solve([-2,0,3],[7,7,7]);self.assertIsNone(data(constant)['metrics']['R_squared'])
        self.assertIsNotNone(constant.value)

    def test_nonlinear_trace_matches_independent_scipy_optimization(self):
        x=np.array([0.,1.,2.]);y=np.array([2.,5.,18.])
        r=solve(x,y,kind='Hàm mũ — SSE thang y',basis=['x'],solver='lm');d=data(r)
        self.assertIsNone(d['failure']);trace=d['solver_trace']
        self.assertEqual(trace['kind'],'levenberg_marquardt');self.assertTrue(trace['iterations'])
        independent=least_squares(lambda p:p[0]*np.exp(p[1]*x)-y,[1.8,1.1],xtol=1e-14,ftol=1e-14,gtol=1e-14)
        assert_allclose(list(map(float,d['coefficients'])),independent.x,rtol=1e-7,atol=1e-7)
        self.assertAlmostEqual(float(d['metrics']['SSE_y']),float(np.sum(independent.fun**2)),places=10)
        accepted=[step['sse_proposed'] for step in trace['iterations'] if step['accepted']]
        self.assertTrue(all(a>=b for a,b in zip(accepted,accepted[1:])))
        for step in trace['iterations']:
            jac=step['jacobian'];delta=step['step_internal']
            lhs=(jac.T@jac+step['damping']*np.diag(step['jacobian_column_norms']**2))@delta
            assert_allclose(lhs,-jac.T@step['residual_scaled'],atol=1e-12,rtol=1e-10)
        self.assertIn('không có chứng nhận cực tiểu toàn cục',r.text())
        failed=solve(x,y,kind='Hàm mũ — SSE thang y',basis=['x'],solver='lm',max_iter=1)
        self.assertEqual(data(failed)['status'],'max_iterations');self.assertIsNone(failed.value)
        self.assertEqual(len(data(failed)['solver_trace']['iterations']),1)

    def test_nonlinear_zero_weight_outlier_cannot_change_scaling_or_solution(self):
        base=solve([0,1,2],[2,5,18],kind='Hàm mũ — SSE thang y',solver='lm')
        extra=solve([0,1,2,3],[2,5,18,1e200],kind='Hàm mũ — SSE thang y',weights=[1,1,1,0],solver='lm')
        self.assertIsNone(data(extra)['failure'])
        assert_allclose(list(map(float,data(extra)['coefficients'])),list(map(float,data(base)['coefficients'])),rtol=1e-9)
        self.assertEqual(data(extra)['solver_trace']['yscale'],18)
        self.assertGreater(data(extra)['metrics']['SSE_y'],Decimal('1e399'))
        self.assertLess(data(extra)['metrics']['weighted_objective_y'],Decimal(1))

    def test_large_weights_and_negative_r_squared_are_preserved(self):
        r=solve([0,1,2],[1,2,2],weights=[1e300,2e300,1e300],solver='normal_gauss')
        self.assertIsNone(data(r)['failure'])
        assert_allclose(list(map(float,data(r)['coefficients'])),[1.25,.5],atol=1e-14)
        self.assertGreater(data(r)['metrics']['weighted_objective_y'],Decimal('1e298'))
        no_intercept=solve([1,2,3],[100,101,100],basis=['x'])
        self.assertLess(data(no_intercept)['metrics']['R_squared'],0)

    def test_invalid_choices_and_domains_remain_failed_reports(self):
        cases=[({'x':[0,1],'y':[1,2],'weights':[1,-1]},'invalid_weights'),
               ({'x':[0,1],'y':[0,2],'kind':'Hàm mũ'},'transform_domain_error'),
               ({'x':[0,1],'y':[1,2],'solver':'normal_gauss','rank_policy':'minimum_norm'},'invalid_rank_policy'),
               ({'x':[0,1],'y':[1,2],'kind':'Hàm mũ — SSE thang y','solver':'qr'},'invalid_solver')]
        for options,status in cases:
            with self.subTest(status=status):
                r=solve(**options);self.assertEqual(data(r)['status'],status);self.assertIsNone(r.value)
                self.assertTrue(r.text())

    def test_nonlinear_dependent_exponent_basis_does_not_claim_identified_parameters(self):
        for x,y,basis in [([0,1,2],[2,4,8],['1','x']),
                          ([1,2],[2,4],['x','1/x'])]:
            r=solve(x,y,kind='Hàm mũ — SSE thang y',basis=basis)
            self.assertEqual(data(r)['status'],'rank_deficient')
            self.assertIsNone(r.value)
            self.assertEqual(len(data(r)['x']),len(x))

    def test_explicit_constant_exponential_is_the_weighted_mean(self):
        r=solve([0,1,2],[2,5,8],kind='Hàm mũ — SSE thang y',basis=[],weights=[1,2,1])
        self.assertIsNone(data(r)['failure'],str(data(r)['failure']))
        self.assertEqual(len(data(r)['coefficients']),1)
        assert_allclose(r.value(np.array([-3.,0.,1.,10.])),[5,5,5,5],atol=1e-9)
        self.assertAlmostEqual(float(data(r)['metrics']['weighted_objective_y']),18,places=9)
        for kind,value in r.presentation['blocks']:
            if kind=='formula':self.assertTrue(math_png(value).startswith(b'\x89PNG'))

    def test_synthetic_2025_style_basis_weighted_noisy_measurements(self):
        # Dữ liệu mô phỏng dạng bài; không nhận là bảng gốc của một đề 2025.
        x=np.array([-.8,-.1,.4,.4,1.2,2.,3.1]);y=1.2-.7*x+.4*np.cos(x)+np.array([.02,-.01,.03,-.02,.01,-.03,.04])
        weights=np.array([1,2,1,3,0,2,1.]);theta=np.column_stack((np.ones(len(x)),x,np.cos(x)))
        independent=np.linalg.lstsq(theta*np.sqrt(weights)[:,None],y*np.sqrt(weights),rcond=None)[0]
        r=solve(x,y,basis=['1','x','cos(x)'],weights=weights);d=data(r)
        self.assertIsNone(d['failure']);assert_allclose(list(map(float,d['coefficients'])),independent,atol=2e-14)
        self.assertEqual(len(d['x']),7)

    def test_formulas_and_full_offline_report_render_for_pdf_samples(self):
        reports=[solve([0,1,2,3],[1,2,2,4],solver='normal_gauss'),
                 solve([0,1,2],[2,5,18],kind='Hàm mũ'),
                 solve([0,1,2],[2,5,18],kind='Hàm mũ — SSE thang y',solver='lm')]
        with tempfile.TemporaryDirectory() as folder:
            for i,r in enumerate(reports):
                self.assertIn('worked_layout',r.presentation)
                for kind,value in r.presentation['blocks']:
                    if kind=='formula':self.assertTrue(math_png(value).startswith(b'\x89PNG'))
                target=Path(folder)/f'fit_{i}.html';export_html(r,target)
                html=target.read_text(encoding='utf-8')
                self.assertTrue('data:image/png;base64,' in html)
                self.assertTrue('src="http' not in html)
                self.assertNotIn('\\frac',r.text())


if __name__=='__main__':unittest.main()
