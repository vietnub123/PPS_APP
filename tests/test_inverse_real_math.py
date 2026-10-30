"""Tiền kiểm và các bài nội suy ngược trong kienthuc/real ngày 30/10/2026."""
from fractions import Fraction as F
import unittest

from pps.inverse_solution import solve_inverse, from_gui


X=[1.6,1.8,2.0,2.2]
Y=[4.23,3.67,2.99,1.24]


def details(report):
    return report.presentation['inverse_solution']


class RealInverseMathTests(unittest.TestCase):
    def test_real_three_examples_and_initial_row(self):
        for form in ('inverse_lagrange','inverse_newton'):
            r=solve_inverse([1,2,3],[1,4,9],6,form,interval=(2,3))
            d=details(r)
            self.assertIsNone(d['failure']);self.assertEqual(r.value,2.5)
            self.assertEqual(d['model']['coefficients'],[F(1),F(1,3),-F(1,60)])
            self.assertNotIn('iteration',d)
        for backward,target,count,value,q in (
            (False,4,5,1.666001162884,F(11,24)),
            (True,2,6,2.133420489204,F(73,150)),
        ):
            r=solve_inverse(X,Y,target,'backward_iteration' if backward else 'forward_iteration',
                            eps_x=1e-6,eps_y=1e-6,stop_mode='certified')
            d=details(r);it=d['iteration']
            self.assertIsNone(d['failure']);self.assertEqual(d['iterations_done'],count)
            self.assertAlmostEqual(r.value,value,places=12)
            self.assertEqual(it['certificate']['q'],q)
            self.assertEqual(it['certificate']['kind'],'analytic_verified')
            self.assertEqual(it['initial']['iteration'],0)
            self.assertEqual(len(it['history']),count)
            self.assertTrue(any(c['title']=='Khởi tạo so với khoảng mục tiêu' and c['state']=='passed'
                                for c in d['validation_checks']))

    def test_external_half_bound_preserves_conditional_scope_and_guide_rows(self):
        for backward,target,image,count,last_bound in (
            (False,4,['.296130952','.410714286'],5,1.06519e-7),
            (True,2,['-.434285715','-.312619047'],6,6.11127e-7),
        ):
            source={'kind':'user_supplied_bound','J':[-1,0] if backward else [0,1],
                    'q':'.5','invariant_image_bound':image,'source':'Lập luận trên toàn J trong PDF real'}
            r=solve_inverse(X,Y,target,'backward_iteration' if backward else 'forward_iteration',
                            eps_x=1e-6,eps_y=1e-6,stop_mode='certified',convergence_certificate=source)
            d=details(r);it=d['iteration']
            self.assertEqual(d['status'],'conditional_model_tolerance')
            self.assertEqual(len(it['history']),count)
            self.assertEqual(it['certificate']['kind'],'user_supplied_bound')
            self.assertFalse(it['certificate']['independently_verified'])
            self.assertEqual(it['certificate']['q'],F(1,2))
            self.assertLess(abs(float(it['history'][-1]['error_bound_x'])-last_bound),last_bound*5e-6)
            self.assertFalse(it['history'][-2]['position_ok'])

    def test_selected_node_range_cannot_be_replaced_by_larger_branch(self):
        options={'selected_indices':[0,1],'branch_indices':[0,1,2],'interval':(0,1)}
        r=solve_inverse([0,1,2],[0,1,4],2,**options)
        d=details(r)
        self.assertEqual(d['status'],'inverse_extrapolation');self.assertIsNone(r.value)
        self.assertNotIn('model',d)
        self.assertTrue(d['extrapolation']['in_branch'])
        self.assertFalse(d['extrapolation']['in_selected_nodes'])
        allowed=solve_inverse([0,1,2],[0,1,4],2,allow_extrapolation=True,**options)
        self.assertEqual(allowed.value,2)
        self.assertTrue(any('ngoại suy' in w for w in details(allowed)['warnings']))

    def test_selected_uniform_subset_keeps_its_own_spacing(self):
        x=list(range(5))
        r=solve_inverse(x,x,.5,'forward_iteration',selected_indices=[0,2,4])
        self.assertIsNone(details(r)['failure'])
        self.assertEqual(r.value,.5)
        self.assertEqual(details(r)['grid']['h'],F(2))
        variant=solve_inverse(x,x,.5,'forward_iteration',selected_indices=[0,2,4],interval=(0,1))
        self.assertEqual(variant.value,.5)
        self.assertEqual(details(variant)['selection']['indices'],[0,2,4])

    def test_forward_polynomial_can_cross_turning_points_while_inverse_function_cannot(self):
        r=solve_inverse([0,1,2],[0,1,0],.5,'forward_iteration',branch_indices=[0,1,2],interval=(0,1))
        self.assertIsNone(details(r)['failure'])
        self.assertTrue(any('đa thức thuận' in w for w in details(r)['warnings']))
        inverse=solve_inverse([0,1,2],[0,1,0],.5,branch_indices=[0,1,2],interval=(0,1))
        self.assertIsNotNone(details(inverse)['failure'])
        variant=solve_inverse([0,1,2],[0,1,0],.5,'forward_iteration',interval=(0,1))
        self.assertIsNone(details(variant)['failure'])
        self.assertTrue(any('đa thức thuận' in w for w in details(variant)['warnings']))

    def test_uniform_grid_threshold_uses_both_step_scales(self):
        r=solve_inverse([0,1,2.11],[0,1,2.11],.5,'forward_iteration',grid_rtol=.1)
        d=details(r)
        self.assertNotEqual(d['status'],'nonuniform_grid')
        self.assertEqual(d['grid']['thresholds'],[F(1,10),F(111,1000)])
        self.assertEqual(d['grid']['classification'],'approximately_uniform')

    def test_scale_aware_warnings_do_not_modify_data_or_zero_the_denominator(self):
        x=[0,1,2];y=[1e12,1e12+.001,1e12+.002]
        r=solve_inverse(x,y,1e12+.0005,'forward_iteration',stop_mode='certified')
        d=details(r)
        self.assertIsNone(d['failure']);self.assertEqual(r.value,.5)
        self.assertEqual(d['model']['coefficients'][1],F(1,1000))
        self.assertTrue(d['linear_difference_check']['small'])
        self.assertTrue(d['near_y_checks'])
        no_warning=solve_inverse(x,y,1e12+.0005,'forward_iteration',near_y_rtol=0,linear_warning_rtol=0)
        self.assertFalse(details(no_warning)['linear_difference_check']['small'])
        self.assertEqual(details(no_warning)['near_y_checks'],[])

    def test_bare_wrong_or_contradicted_external_certificates_are_rejected(self):
        common={'kind':'user_supplied_bound','J':[0,1],'q':.5,
                'invariant_image_bound':[0,1],'source':'Giả thiết do đề cho'}
        invalid=[.5,{**common,'J':[-1,0]},{**common,'source':''},{**common,'q':0},
                 {**common,'q':1},{**common,'invariant_image_bound':[.4,.41]},
                 {**common,'kind':'analytic_verified'}]
        for certificate in invalid:
            with self.subTest(certificate=certificate):
                r=solve_inverse(X,Y,4,'forward_iteration',stop_mode='certified',convergence_certificate=certificate)
                self.assertEqual(details(r)['status'],'invalid_convergence_certificate')
                self.assertEqual(details(r)['iteration']['history'],[])

    def test_sample_diagnostics_do_not_become_certified_and_practical_selection_stays_practical(self):
        sampled={'kind':'sampled_diagnostic','q':.5,'source':'10 điểm lấy mẫu'}
        r=solve_inverse(X,Y,4,'forward_iteration',stop_mode='certified',convergence_certificate=sampled)
        self.assertEqual(details(r)['status'],'certification_unavailable')
        practical=solve_inverse(X,Y,4,'forward_iteration',stop_mode='practical',eps_x=1e-6,
                                convergence_certificate=sampled)
        self.assertEqual(details(practical)['status'],'practical_stop')
        self.assertIsNone(details(practical)['iteration']['certificate'])
        self.assertTrue(all(row['error_bound_x'] is None for row in details(practical)['iteration']['history']))

    def test_gui_aliases_detail_and_precision_are_preserved(self):
        for method,form in [('Hàm ngược — Lagrange','lagrange'),('Hàm ngược — Newton','divided_difference')]:
            r=from_gui(method,{'target':'6','detail_level':'Chi tiết','digits':'8'},'1 2 3','1 4 9')
            d=details(r)
            self.assertEqual(d['model']['basis'],form)
            self.assertEqual(d['input']['detail_level'],'detailed')
            self.assertEqual(d['input']['display_digits'],8)
        r=from_gui('Hàm ngược — Newton',{'target':'6','digits':'8','display_digits':'10'},'1 2 3','1 4 9')
        self.assertEqual(details(r)['input']['display_digits'],10)


if __name__=='__main__':
    unittest.main()
