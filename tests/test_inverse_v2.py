"""Guide bản2: tập mốc/gốc độc lập khoảng mục tiêu, T khác đoạn chứng nhận J."""
from decimal import Decimal
from fractions import Fraction as F
import math
import unittest
from unittest.mock import patch

from pps.inverse_solution import solve_inverse,from_gui
from pps.math_view import math_png


def data(report):return report.presentation['inverse_solution']


class WholeTableInverseV2(unittest.TestCase):
    def test_all_36_nodes_middle_interval_both_origins_and_no_fake_missing_nodes(self):
        x=[F(1)+F(23,200)*i for i in range(36)]
        y=[2*v-F(59,20) for v in x]
        for method,origin,target_t,initial in (
            ('forward_iteration',F(1),(F(9),F(10)),F(218,23)),
            ('backward_iteration',F('5.025'),(F(-26),F(-25)),-F(587,23))):
            for maximum in (1,100):
                with self.subTest(method=method,max_iter=maximum):
                    r=solve_inverse(x,y,F('1.23'),method,degree=35,interval=(F('2.035'),F('2.15')),
                                    eps_x=1e-6,eps_y=1e-6,max_iter=maximum,run_mode='certified_only')
                    d=data(r);it=d['iteration']
                    self.assertIsNone(d['failure']);self.assertEqual(r.value,2.09)
                    self.assertEqual(len(d['used_rows']),36);self.assertEqual(d['degree'],35)
                    self.assertEqual(d['model']['anchor'],origin);self.assertEqual(d['model']['h'],F('.115'))
                    self.assertEqual(it['T'],target_t);self.assertEqual(it['t0'],initial)
                    self.assertEqual(it['certificate']['q'],0)
                    self.assertTrue(all(v==0 for v in d['model']['coefficients'][2:]))
                    self.assertEqual(d['model']['actual_degree'],1)
                    self.assertEqual(it['history'],[])

    def test_gui_keeps_exact_decimal_tokens_for_degree_35(self):
        x=[Decimal(1)+Decimal('.115')*i for i in range(36)]
        y=[2*v-Decimal('2.95') for v in x]
        for method in ('Lặp tiến','Lặp lùi'):
            r=from_gui(method,{'target':'1.23','a':'2.035','b':'2.15','tol':'1e-6'},
                       ' '.join(map(str,x)),' '.join(map(str,y)))
            self.assertEqual(r.value,2.09)
            self.assertTrue(all(v==0 for v in data(r)['model']['coefficients'][2:]))
            self.assertEqual(data(r)['grid']['classification'],'exactly_uniform')

    def test_unique_middle_bracket_is_resolved_without_changing_origin_or_stencil(self):
        for method in ('forward_iteration','backward_iteration'):
            r=solve_inverse(range(8),[2*x+1 for x in range(8)],8,method)
            d=data(r)
            self.assertEqual(r.value,3.5);self.assertEqual(d['interval'],(F(3),F(4)))
            self.assertEqual(len(d['used_rows']),8)
            self.assertEqual(d['model']['anchor'],0 if method=='forward_iteration' else 7)
            self.assertIn('duy nhất',d['interval_source'])

    def test_bracket_indices_do_not_select_new_local_nodes(self):
        r=solve_inverse(range(10),[2*x+1 for x in range(10)],12,'forward_iteration',
                        bracket_indices=[5,6],stop_mode='certified')
        self.assertEqual(r.value,5.5)
        self.assertEqual(data(r)['model']['anchor'],0)
        self.assertEqual(data(r)['selection']['indices'],list(range(10)))
        self.assertEqual(data(r)['iteration']['T'],(F(5),F(6)))

    def test_explicit_uniform_subset_may_skip_original_rows(self):
        r=solve_inverse(range(5),range(5),.5,'forward_iteration',selected_indices=[0,2,4])
        self.assertEqual(r.value,.5)
        self.assertEqual(data(r)['model']['h'],2)
        self.assertEqual(data(r)['selection']['indices'],[0,2,4])
        self.assertEqual(data(r)['iteration']['T'],(F(0),F(1)))

    def test_insufficient_nodes_only_means_actual_count_below_degree_plus_one(self):
        r=solve_inverse([1,1.2,1.4],[1,1.44,1.96],1.5,'forward_iteration',degree=2,max_iter=1)
        self.assertNotEqual(data(r)['status'],'insufficient_nodes')
        self.assertIn('model',data(r));self.assertEqual(len(data(r)['used_rows']),3)
        missing=solve_inverse([1,1.2,1.4],[1,1.44,1.96],1.5,'forward_iteration',degree=3)
        self.assertEqual(data(missing)['status'],'insufficient_nodes')

    def test_forward_full_table_can_cross_target_branch_and_flags_other_root(self):
        r=solve_inverse([-2,-1,0,1,2],[4,1,0,1,4],2,'forward_iteration',
                        interval=(1,2),branch_indices=[2,3,4],eps_x=1e-9,eps_y=1e-9)
        d=data(r)
        self.assertEqual(d['status'],'converged_outside_requested_bracket')
        self.assertIsNone(r.value)
        self.assertAlmostEqual(float(d['last_approximation']),-math.sqrt(2),places=8)
        self.assertEqual(len(d['used_rows']),5)
        self.assertTrue(any('đổi chiều' in warning for warning in d['warnings']))


class IterationIntervalV2(unittest.TestCase):
    def test_exact_linear_root_at_rational_interval_endpoint_is_not_pushed_out(self):
        r=solve_inverse([0,1],[0,3],1,'forward_iteration',interval=(F(1,3),F(2,3)),stop_mode='certified')
        self.assertEqual(data(r)['status'],'linear_model_value')
        self.assertIsNone(data(r)['failure'])
        self.assertEqual(data(r)['result']['x_internal'],F(1,3))
        self.assertAlmostEqual(r.value,1/3)

    @staticmethod
    def convex(**options):
        x=list(range(6));y=[F(v)+F(v*v,20) for v in x]
        return solve_inverse(x,y,F('4.5'),'forward_iteration',interval=(3,4),
                             eps_x=1e-8,eps_y=1e-8,**options)

    def test_practical_seed_outside_target_is_warning_and_can_converge_inside(self):
        r=self.convex();d=data(r);it=d['iteration']
        self.assertEqual(d['status'],'practical_stop');self.assertIsNone(d['failure'])
        self.assertGreater(it['t0'],4);self.assertFalse(it['initial']['in_target_t_interval'])
        self.assertAlmostEqual(r.value,(-1+math.sqrt(1.9))/.1,places=8)
        self.assertTrue(it['history'][-1]['in_target_t_interval'])
        for row in it['history']:
            self.assertIn('p_at_old',row);self.assertIn('high_prime_old',row)
            self.assertIn('p_at_new',row);self.assertIn('high_prime_new',row)
            self.assertIsNone(row['error_bound_x'])

    def test_certificate_interval_is_separate_from_target_T(self):
        r=self.convex(stop_mode='certified',certificate_interval=(F(3),F('4.5')))
        d=data(r);it=d['iteration']
        self.assertEqual(d['status'],'certified_model_tolerance')
        self.assertEqual(it['T'],(F(3),F(4)));self.assertEqual(it['J'],(F(3),F('4.5')))
        self.assertTrue(it['certificate']['verified'])
        self.assertTrue(all(row['in_certificate_interval'] for row in it['history']))
        self.assertIn('T=[3, 4]',r.text());self.assertIn('J=[3, 4.5]',r.text())

    def test_certificate_not_containing_seed_does_not_apply(self):
        r=self.convex(stop_mode='certified')
        d=data(r)
        self.assertEqual(d['status'],'certification_unavailable')
        self.assertEqual(d['iteration']['convergence']['kind'],'not_applicable_to_seed')
        self.assertEqual(d['iteration']['history'],[])
        self.assertIn('không phải thiếu mốc',d['failure']['message'])

    def test_practical_leaving_target_keeps_running_and_never_uses_bisection(self):
        with patch('pps.chapter1_tools.bisect_model') as fallback:
            r=solve_inverse([0,1,2],[0,1,8],.5,'forward_iteration',max_iter=2)
            fallback.assert_not_called()
        d=data(r);rows=d['iteration']['history']
        self.assertEqual(d['status'],'max_iter_reached');self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]['t_new'],Decimal('1.25'))
        self.assertEqual(rows[1]['t_new'],Decimal('-.4375'))
        self.assertEqual(d['iteration']['target_exit_iterations'],[1,2])
        self.assertIsNotNone(rows[0]['residual_y'])
        self.assertIn('ngoài T',r.text())

    def test_manual_seed_is_preserved_and_its_formula_is_presented(self):
        r=self.convex(initial_rule='manual',initial_t='3.8',max_iter=1)
        d=data(r);self.assertEqual(d['iteration']['t0'],F('3.8'))
        self.assertEqual(d['iteration']['history'][0]['t_old'],Decimal('3.8'))
        self.assertIn('Khởi tạo thủ công',r.text())
        self.assertNotIn('t_0=(4.5-(0))/(1.05)',r.text())

    def test_bracket_linear_uses_polynomial_at_non_nodes(self):
        r=solve_inverse([0,1,2],[0,1,4],F('1.5'),'forward_iteration',
                        interval=(F('1.1'),F('1.4')),initial_rule='bracket_linear',max_iter=1)
        initial=data(r)['iteration']['initial_rule']
        self.assertEqual(initial['ya'],F('1.21'));self.assertEqual(initial['yb'],F('1.96'))
        self.assertEqual(initial['t0'],F('1.216'))
        self.assertIn('đa thức thuận',initial['source_a'])
        self.assertIn('1.216',r.text())

    def test_divergence_retains_failed_row_and_true_cause(self):
        r=solve_inverse([0,1,2],[0,1,8],.5,'forward_iteration',max_iter=100)
        d=data(r)
        self.assertEqual(d['status'],'nonfinite_iteration')
        self.assertGreater(len(d['iteration']['history']),2)
        self.assertEqual(d['iteration']['history'][-1]['status'],'nonfinite_iteration')
        self.assertIn('tràn',r.text())
        self.assertNotIn('thiếu mốc kể từ',r.text())
        for kind,value in r.presentation['blocks']:
            if kind=='formula':self.assertTrue(math_png(value))


if __name__=='__main__':unittest.main()
