"""Nghiệm thu A–G theo guide 1.2 và PDF nội suy ngược ngày 29/10/2026."""
from copy import deepcopy
from decimal import Decimal
from fractions import Fraction as F
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from numpy.polynomial import Polynomial
from numpy.testing import assert_allclose

from pps.inverse_solution import solve_inverse, bisect_solution, InverseFailure
from pps.inverse_model import evaluate, expand_newton, InverseMap
from pps import interpolation as ip, chapter1_tools as ch1
from pps.gui import dispatch
from pps.math_view import math_png, export_html, table_image


B_X=[1.2,1.4,1.6,1.8]
B_Y=[1.728,2.744,4.096,5.832]
C_X=[1,1.2,1.4,1.6]
C_Y=[1,1.728,2.744,4.096]


def example(backward=False,**options):
    return solve_inverse(C_X if backward else B_X,C_Y if backward else B_Y,3.5 if backward else 2.2,
                         'backward_iteration' if backward else 'forward_iteration',
                         eps_x=options.pop('eps_x',1e-6),eps_y=options.pop('eps_y',1e-6),
                         stop_mode=options.pop('stop_mode','certified'),**options)


def data(report):return report.presentation['inverse_solution']


class GuideAcceptance(unittest.TestCase):
    def test_float_conversion_cannot_claim_an_unattainable_tolerance(self):
        r=solve_inverse([0,1],[0,3],1,'forward_iteration',eps_x=1e-30,
                        eps_y=1e-30,stop_mode='certified')
        d=data(r)
        self.assertEqual(d['status'],'numerical_resolution_limit');self.assertIsNone(r.value)
        self.assertGreater(d['result']['rounding_error_bound_x'],Decimal('1e-30'))
        self.assertIn('float',r.text())

    def test_pdf_36_pages_degree_four_certificate_and_rows(self):
        r=solve_inverse([0,1,2,3,4],[0,1.01,2.16,3.81,6.56],.5,
                        'forward_iteration',degree=4,stop_mode='certified',eps_x=1e-8,eps_y=1e-8)
        d=data(r);history=d['iteration']['history']
        self.assertEqual(d['status'],'certified_model_tolerance')
        self.assertEqual(d['model']['coefficients'],list(map(F,['0','1.01','.14','.36','.24'])))
        self.assertEqual(d['model']['polynomial'],[F(0),F(1),F(0),F(0),F(1,100)])
        self.assertEqual(d['iteration']['certificate']['q'],F(3,101))
        self.assertEqual(len(history),3)
        assert_allclose([float(row['t_new']) for row in history],
                        [.499356319143,.499377995432,.499378103147],atol=5e-13,rtol=0)
        assert_allclose([float(row['error_bound_x']) for row in history],
                        [1.31841e-4,6.63560e-7,3.29741e-9],rtol=5e-6)
        assert_allclose([float(term['value']) for term in history[0]['term_contributions']],
                        [-.017498284482,.022572044480,-.009423642332],atol=5e-13,rtol=0)
        self.assertFalse(history[1]['position_ok']);self.assertTrue(history[2]['position_ok'])
        for group in r.presentation['formulas']:
            for latex in group[1]:self.assertTrue(math_png(latex))

    def test_A_inverse_newton_and_lagrange_have_no_iteration(self):
        for form in ('divided_difference','lagrange'):
            r=solve_inverse([1,1.5,2],[2,3.75,6],3,inverse_form=form,interval=(1,1.5),degree=2,
                            selected_indices=[0,1,2],branch_indices=[0,1,2])
            d=data(r);self.assertEqual(d['status'],'inverse_value_computed')
            self.assertAlmostEqual(r.value,109/84,places=14)
            self.assertEqual(d['model']['coefficients'],[F(1),F(2,7),-F(1,63)])
            self.assertEqual(d['model']['forward_residual'],-F(131,7056))
            self.assertNotIn('iteration',d)
            polynomial=expand_newton(d['model']['nodes'],d['model']['coefficients'])
            for y,x in zip([F(2),F(15,4),F(6)],[F(1),F(3,2),F(2)]):self.assertEqual(evaluate(polynomial,y),x)
            if form=='lagrange':self.assertEqual([term['basis_value'] for term in d['model']['lagrange_terms']],[F(9,28),F(16,21),-F(1,12)])

    def test_B_forward_certificate_and_all_three_rows_match_pdf(self):
        r=example();d=data(r);history=d['iteration']['history'];certificate=d['iteration']['certificate']
        self.assertEqual(d['status'],'certified_model_tolerance')
        self.assertEqual(d['model']['coefficients'],[F('1.728'),F('1.016'),F('.336'),F('.048')])
        self.assertEqual(certificate['q'],F(20,127))
        self.assertEqual(certificate['image'],(F(468,1016),F(514,1016)))
        self.assertEqual(d['iteration']['t0'],F(59,127));self.assertEqual(len(history),3)
        assert_allclose([float(row['t_new']) for row in history],[.502690582044,.502956940638,.502957233946],atol=5e-13,rtol=0)
        assert_allclose([float(row['x_new']) for row in history],[1.300538116409,1.300591388128,1.300591446789],atol=5e-13,rtol=0)
        assert_allclose([float(row['error_bound_x']) for row in history],[1.42518328637e-3,9.95733060156e-6,1.09647748213e-8],rtol=5e-11)
        assert_allclose([float(row['residual_y']) for row in history],[2.70620331089e-4,2.98000650093e-7,3.15944894219e-10],rtol=5e-10)
        self.assertFalse(history[1]['position_ok']);self.assertTrue(history[1]['residual_ok'])
        self.assertTrue(history[2]['position_ok'] and history[2]['residual_ok'])
        terms=history[0]['term_contributions']
        self.assertAlmostEqual(float(terms[0]['value']),-.041789075578151,places=14)
        self.assertAlmostEqual(float(terms[1]['value']),.003055444221125,places=14)
        self.assertEqual(certificate['arithmetic'],'exact_rational')
        self.assertFalse(certificate['machine_rounding_certified'])

    def test_C_backward_uses_last_column_entries_and_negative_t(self):
        r=example(True);d=data(r);history=d['iteration']['history']
        self.assertEqual(d['status'],'certified_model_tolerance')
        self.assertEqual(d['model']['coefficients'],list(map(F,['4.096','1.352','.336','.048'])))
        self.assertEqual(d['iteration']['certificate']['q'],F(23,169))
        self.assertEqual(d['iteration']['certificate']['image'],(-F(596,1352),-F(550,1352)))
        self.assertEqual(d['iteration']['J'],(F(-1),F(0)))
        self.assertEqual(len(history),3)
        assert_allclose([float(row['t_new']) for row in history],[-.407924219119,-.408541512016,-.408527249318],atol=5e-13,rtol=0)
        assert_allclose([float(row['error_bound_x']) for row in history],[1.03670714344e-3,1.94489542914e-5,4.49372665234e-7],rtol=5e-11)
        self.assertAlmostEqual(r.value,1.518294550136,places=12)

    def test_D_scan_does_not_solve_or_choose_a_branch(self):
        x=[1.2,1.4,1.6,1.8,2,2.2,2.4,2.6,2.8]
        y=[4.02,3.98,4.23,3.67,2.99,1.24,.87,2.08,4.54]
        r=solve_inverse(x,y,4)
        d=data(r);self.assertEqual(d['status'],'selection_required');self.assertIsNone(r.value)
        self.assertEqual(d['sample_scan']['brackets'],[(0,1),(1,2),(2,3),(7,8)])
        self.assertEqual(d['sample_scan']['branches'],[[0,1],[1,2],[2,3,4,5,6],[6,7,8]])
        expected=[1.3,1.416,1.682142857143,2.756097560976]
        for (a,b),answer in zip(d['sample_scan']['brackets'],expected):
            separate=solve_inverse(x,y,4,selected_indices=[a,b],branch_indices=[a,b],interval=(x[a],x[b]))
            self.assertAlmostEqual(separate.value,answer,places=11)

    def test_E_failure_keeps_the_failed_first_row_and_has_no_fallback(self):
        with patch('pps.chapter1_tools.bisect_model') as fallback:
            r=solve_inverse([0,1,2],[0,1,8],.5,'forward_iteration',stop_mode='practical',max_iter=1)
            fallback.assert_not_called()
        d=data(r);self.assertEqual(d['status'],'max_iter_reached');self.assertIsNone(r.value)
        row=d['iteration']['history'][0]
        self.assertEqual(row['t_old'],Decimal('.5'));self.assertEqual(row['t_new'],Decimal('1.25'))
        self.assertEqual(row['status'],'continue')
        self.assertFalse(row['in_target_t_interval'])
        self.assertIn('1.25',r.text());self.assertIn('Vòng 1',r.text())
        certified=solve_inverse([0,1,2],[0,1,8],.5,'forward_iteration',stop_mode='certified')
        self.assertEqual(data(certified)['status'],'certification_unavailable')
        self.assertEqual(data(certified)['iteration']['history'],[])
        # Chỉ một lượt mới, được chọn rõ, mới chạy chia đôi cùng P.
        separate=solve_inverse([0,1,2],[0,1,8],.5,'bisection',interval=(0,1))
        self.assertAlmostEqual(separate.value[0],(2+math.sqrt(10))/6,places=9)

    def test_F_bisection_returns_midpoint_of_final_bracket(self):
        r=bisect_solution(Polynomial([0,0,1]),2,1,2,1e-3)
        self.assertEqual(r.value,(1.4150390625,(1.4140625,1.416015625)))
        d=data(r);self.assertEqual(len(d['bisection_history']),9)
        self.assertEqual(d['result']['iteration_error_bound_x'],F(1,1024))
        self.assertGreater(float(d['result']['residual_y']),1e-6)  # Phần dư không phải điều kiện dừng vị trí.

    def test_G_middle_interval_keeps_the_submitted_stencil(self):
        x=[1,1.2,1.4];y=[1,1.44,1.96]
        r=solve_inverse(x,y,1.5,'forward_iteration',degree=2)
        self.assertIsNone(data(r)['failure'])
        self.assertAlmostEqual(r.value,math.sqrt(1.5),places=9)
        self.assertEqual(data(r)['model']['anchor'],F(1))
        self.assertEqual(data(r)['iteration']['T'],(F(1),F(2)))
        self.assertEqual(data(r)['selection']['indices'],[0,1,2])
        missing=solve_inverse(x,y,1.5,'forward_iteration',degree=3)
        self.assertEqual(data(missing)['status'],'insufficient_nodes')
        backward=solve_inverse(x,y,1.5,'backward_iteration',stop_mode='certified')
        self.assertAlmostEqual(backward.value,math.sqrt(1.5),places=9)


class InverseContractTests(unittest.TestCase):
    def test_initial_guess_is_kept_even_when_another_start_would_converge(self):
        x=np.linspace(1,1.4,5)
        r=solve_inverse(x,x*x,1.3225,'forward_iteration',interval=(1.149,1.151),stop_mode='certified')
        self.assertEqual(data(r)['status'],'certification_unavailable')
        self.assertEqual(data(r)['iteration']['history'],[])
        self.assertGreater(float(data(r)['iteration']['t0']),1.51)

    def test_count_and_degree_do_not_authorize_automatic_point_selection(self):
        for options in ({'count':2},{'degree':1}):
            r=solve_inverse([0,1,2],[0,1,4],2,**options)
            self.assertEqual(data(r)['status'],'selection_required')
            self.assertEqual(len(data(r)['used_rows']),3)

    def test_practical_mode_reports_step_instead_of_an_error_bound(self):
        r=example(stop_mode='practical');d=data(r)
        self.assertEqual(d['status'],'practical_stop')
        self.assertIsNone(d['iteration']['certificate'])
        self.assertIsNone(d['result']['iteration_error_bound_x'])
        self.assertTrue(all(row['error_bound_x'] is None for row in d['iteration']['history']))

    def test_maximum_iterations_and_independent_residual_tolerance(self):
        r=example(max_iter=1)
        self.assertEqual(data(r)['status'],'max_iter_reached');self.assertEqual(len(data(r)['iteration']['history']),1)
        r=example(eps_x=1e-3,eps_y=1e-12)
        row=data(r)['iteration']['history'][1]
        self.assertTrue(row['position_ok']);self.assertFalse(row['residual_ok'])

    def test_linear_and_exact_sample_solutions_have_no_dummy_iterations(self):
        r=solve_inverse([2,3],[5,9],7,'forward_iteration',stop_mode='certified')
        self.assertEqual(r.value,2.5);self.assertEqual(data(r)['status'],'linear_model_value')
        self.assertEqual(data(r)['iteration']['history'],[])
        r=solve_inverse([0,1,2],[0,1,4],1)
        self.assertEqual(r.value,1);self.assertEqual(data(r)['status'],'exact_sample_match')

    def test_inverse_output_outside_bracket_is_kept_unclipped(self):
        r=solve_inverse([0,1,2],[0,1,1.1],.5,interval=(0,1))
        self.assertEqual(data(r)['status'],'outside_bracket')
        self.assertAlmostEqual(r.value,-17/11)

    def test_near_uniform_grid_states_which_model_is_certified(self):
        r=solve_inverse([0,1,2+1e-12],[0,1.1,2.4],.5,'forward_iteration',stop_mode='certified')
        self.assertEqual(data(r)['grid']['classification'],'approximately_uniform')
        self.assertTrue(any('mô hình' in warning for warning in data(r)['warnings']))
        bad=solve_inverse([0,1,2.2],[0,1,4],.5,'forward_iteration')
        self.assertEqual(data(bad)['status'],'nonuniform_grid');self.assertTrue(data(bad)['grid']['steps'])

    def test_failure_reports_input_indices_and_preserves_original_sort_mapping(self):
        r=solve_inverse([2,1,1],[6,2,3],2.5)
        self.assertEqual(data(r)['status'],'duplicate_abscissa');self.assertIn('1 và 2',data(r)['failure']['message'])
        r=solve_inverse([2,1,1.5],[6,2,3.75],3)
        self.assertEqual(data(r)['sort_order'],[1,2,0]);self.assertAlmostEqual(r.value,109/84)
        r=solve_inverse([0,1,2],[1,1,2],1.5)
        self.assertEqual(data(r)['status'],'duplicate_inverse_node')

    def test_true_function_bounds_require_explicit_data_and_domain(self):
        r=solve_inverse([1,1.5,2],[2,3.75,6],3,error_data={'M':'4/81','domain':[2,6],'source':'PDF trang 18'})
        self.assertEqual(data(r)['result']['true_function_error_bound_x'],F(1,54))
        r=example(error_data={'E':2e-5,'mu':4,'domain':[1.2,1.4],'source':'Giả thiết đề'})
        self.assertGreater(float(data(r)['result']['true_function_error_bound_x']),5e-6)
        r=example(error_data={'E':2e-5,'mu':4})
        self.assertIsNone(data(r)['result']['true_function_error_bound_x'])
        r=example(error_data={'E':2e-5,'mu':0,'domain':[1.2,1.4],'source':'Dữ kiện sai'})
        self.assertEqual(data(r)['status'],'certified_model_tolerance')
        self.assertIsNone(data(r)['result']['true_function_error_bound_x'])

    def test_near_level_is_not_exact_and_hidden_turning_points_are_not_removed(self):
        r=solve_inverse([0,1],[1e-12,1],.5,equality_atol_y=1)
        self.assertEqual(data(r)['status'],'inverse_value_computed')
        self.assertTrue(data(r)['sample_scan']['near_level_samples'])
        self.assertEqual(data(r)['sample_scan']['sample_roots'],[])
        r=solve_inverse([0,1,2],[0,2,1],.5,selected_indices=[0,2],interval=(0,2))
        self.assertEqual(data(r)['status'],'invalid_branch')

    def test_conservative_q_failure_is_not_called_proven_divergence(self):
        x=list(range(5));y=[0,1,-25.2,-232.2,-927.2]
        r=solve_inverse(x,y,.5,'forward_iteration',stop_mode='certified',interval=(0,1))
        certificate=data(r)['iteration']['certificate']
        self.assertEqual(certificate['derivative_state'],'not_verified')
        self.assertEqual(data(r)['status'],'certification_unavailable')

    def test_snapshot_is_not_changed_by_later_edits(self):
        x=B_X.copy();values={'target':'2.2','a':'1.2','b':'1.4','tol':'1e-6','residual_tol':'1e-6'}
        r=dispatch('Nội suy ngược','Lặp có cận co',values,' '.join(map(str,x)),' '.join(map(str,B_Y)))
        saved=deepcopy(data(r)['input']['ui']);values['target']='9';x[0]=0
        self.assertEqual(data(r)['input']['ui'],saved)

    def test_bad_inputs_and_failed_rows_remain_available_through_gui(self):
        r=dispatch('Nội suy ngược','Lặp tiến',{'target':'.5','tol':'1e-6','max_iter':'1'},'0 1 2','0 1 8')
        self.assertEqual(data(r)['status'],'max_iter_reached');self.assertIsNone(r.value)
        for x,y in [('0 1','0'),('0 nan','1 2'),('bad','1 2')]:
            r=dispatch('Nội suy ngược','Lặp tiến',{'target':'.5','tol':'1e-6'},x,y)
            self.assertIsNotNone(data(r)['failure']);self.assertTrue(r.text())
        with self.assertRaises(InverseFailure) as ctx:ip.inverse([0,1,2],[0,1,8],.5,max_steps=1)
        self.assertEqual(data(ctx.exception.report)['status'],'max_iter_reached')

    def test_subnormal_sign_change_does_not_underflow_in_survey(self):
        exact,intervals,flat=ch1.scan_level([0,1],[-1e-200,1e-200],0).value
        self.assertEqual(intervals,[(0,1)]);self.assertEqual(exact,[])

    def test_forward_backward_models_match_on_the_same_stencil_for_any_degree(self):
        for count in range(2,8):
            x=[F(11,10)+F(i,5) for i in range(count)]
            y=[F((i+1)**3+i%2) for i in range(count)]
            forward=InverseMap(x,y,F(3));backward=InverseMap(x,y,F(3),True)
            for value in x+[x[0]+F(1,13)]:
                pf=evaluate(forward.polynomial_exact,(value-forward.origin_exact)/forward.h_exact)
                pb=evaluate(backward.polynomial_exact,(value-backward.origin_exact)/backward.h_exact)
                self.assertEqual(pf,pb)
            for value,expected in zip(x,y):
                self.assertEqual(evaluate(forward.polynomial_exact,(value-forward.origin_exact)/forward.h_exact),expected)

    def test_iteration_and_term_details_are_not_hardcoded_to_degree_three(self):
        x=list(range(5));y=[float(F(v)+F(v*v,100)+F(v**3,1000)+F(v**4,10000)) for v in x]
        r=solve_inverse(x,y,.5,'forward_iteration',stop_mode='certified',eps_x=1e-10,eps_y=1e-10)
        self.assertEqual(data(r)['status'],'certified_model_tolerance')
        self.assertLess(abs(r.value+r.value**2/100+r.value**3/1000+r.value**4/10000-.5),1e-9)
        self.assertEqual(len(data(r)['iteration']['history'][0]['term_contributions']),3)
        self.assertEqual(len(data(r)['iteration']['history'][0]['term_contributions'][-1]['factors']),4)


class InversePresentationTests(unittest.TestCase):
    def test_long_inverse_text_and_html_do_not_drop_coefficient_rows(self):
        from pps.common import Report
        r=Report('Nội suy ngược',presentation={'inverse_solution':{'method':'inverse_function'},
                                               'blocks':[('table',0)]})
        r.table('Các ô đã tính',['ô','giá trị'],[(i,f'cell_{i}') for i in range(705)])
        self.assertIn('cell_704',r.text());self.assertNotIn('Hiển thị 600',r.text())
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'all.html';export_html(r,target)
            self.assertIn('cell_704',target.read_text(encoding='utf-8'))

    def test_B_C_E_render_and_export_complete_offline_reports(self):
        reports=[example(),example(True),solve_inverse([0,1,2],[0,1,8],.5,'forward_iteration')]
        with tempfile.TemporaryDirectory() as folder:
            for name,report in zip(('B','C','E'),reports):
                for kind,value in report.presentation['blocks']:
                    if kind=='formula':self.assertTrue(math_png(value).startswith(b'\x89PNG'))
                for index in report.presentation['inverse_tables']:
                    self.assertGreater(table_image(report,index).width,0)
                target=Path(folder)/(name+'.html');export_html(report,target)
                text=target.read_text(encoding='utf-8')
                self.assertIn('<table>',text);self.assertIn('data:image/png;base64,',text)
                self.assertNotIn('src="http',text);self.assertNotIn('\\frac',text)
                self.assertNotIn('\\frac',report.text())
                self.assertIn('7. Kết luận',report.text())
            self.assertIn('1.25',reports[-1].text())
