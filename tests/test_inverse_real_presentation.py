"""Bố cục theo guide real: tổng hợp dễ đọc, chi tiết đầy đủ và đúng chỉ số."""
from fractions import Fraction
import unittest

from pps.inverse_solution import solve_inverse
from pps.math_view import math_png


X=[1.6,1.8,2,2.2]
Y=[4.23,3.67,2.99,1.24]


def nodes(items):
    for item in items:
        yield item
        yield from nodes(item.get('children',[]))


def visible(items):
    for item in items:
        yield item
        if item['kind']!='details' or item.get('open'):
            yield from visible(item.get('children',[]))


def sample(backward=False,**options):
    return solve_inverse(X,Y,2 if backward else 4,
                         'backward_iteration' if backward else 'forward_iteration',
                         eps_x=1e-6,eps_y=1e-6,stop_mode='certified',**options)


class InverseRealPresentation(unittest.TestCase):
    def test_node_match_has_no_spurious_unmet_model_setup(self):
        r=solve_inverse([0,1,2],[0,1,4],1)
        self.assertEqual(r.value,1)
        self.assertNotIn('Chưa lập bảng hệ số',r.text())
        self.assertNotIn('Chưa lập được công thức',r.text())
        self.assertIn('không cần lập bảng nội suy',r.text())

    def test_preflight_failure_shows_reason_without_empty_calculation_sections(self):
        r=solve_inverse([0,1,2],[0,1,4],2,selected_indices=[0,1],branch_indices=[0,1,2])
        self.assertIsNone(r.value)
        sections=[n['title'].split('.')[0] for n in nodes(r.presentation['inverse_layout']) if n['kind']=='section']
        self.assertEqual(sections,['1','2','7'])
        self.assertIn('ngoại suy',r.text())

    def test_seven_sections_and_real_columns_preserve_order(self):
        r=sample();layout=r.presentation['inverse_layout']
        sections=[n['title'] for n in nodes(layout) if n['kind']=='section']
        self.assertEqual([s.split('.')[0] for s in sections],list('1234567'))
        adjacent=next(n for n in layout if n['kind']=='columns')
        self.assertTrue(adjacent['children'][0]['title'].startswith('3.'))
        self.assertTrue(adjacent['children'][1]['title'].startswith('4.'))

    def test_default_only_three_principal_tables_and_full_hidden_trace(self):
        r=sample();layout=r.presentation['inverse_layout']
        self.assertEqual(sum(n['kind']=='table' for n in visible(layout)),3)
        details=[n for n in nodes(layout) if n['kind']=='details']
        self.assertTrue(details);self.assertTrue(all(not n['open'] for n in details))
        # Mỗi ô sai phân được giữ trong trace đầy đủ, dù chưa mở chi tiết.
        arithmetic=next(table for table in r.tables if table[0]=='Các phép tính đã lưu')
        self.assertEqual(len(arithmetic[2]),6)
        self.assertIn('Các phép tính đã lưu',r.text())
        self.assertIn('Vòng 5',r.text())
        self.assertEqual(sum(n['kind']=='table' for n in nodes(layout)),len(r.tables))

    def test_backward_table_ends_at_the_right_origin_and_keeps_blanks(self):
        r=sample(True)
        i=next(i for i,m in r.presentation['inverse_tables'].items() if m['kind']=='backward')
        name,headers,rows=r.tables[i]
        self.assertEqual(headers[3:],['∇y','∇²y','∇³y'])
        self.assertEqual(rows[0][3:],['—','—','—'])
        self.assertEqual(rows[2][3:],['-0.68','-0.12','—'])
        self.assertEqual(rows[3][2:],['1.24','-1.75','-1.07','-0.95'])
        self.assertEqual(r.presentation['inverse_tables'][i]['used_cells'],[(3,2),(3,3),(3,4),(3,5)])

    def test_one_iteration_summary_includes_initial_and_stop_decision(self):
        r=sample(True)
        summaries=[t for t in r.tables if t[0]=='Bảng tổng hợp vòng lặp']
        self.assertEqual(len(summaries),1)
        title,headers,rows=summaries[0]
        self.assertEqual(len(rows),7)
        self.assertEqual(rows[0][0],'0');self.assertEqual(rows[0][-1],'Khởi tạo')
        self.assertEqual(rows[0][3:5],['—','—'])
        self.assertEqual(rows[-1][-1],'Đạt cả hai')
        self.assertTrue(all(row[-1]=='Tiếp tục' for row in rows[1:-1]))
        self.assertEqual(rows[-1][1],'-0.332897553981')

    def test_practical_summary_does_not_mislabel_step_as_error_bound(self):
        r=solve_inverse(X,Y,4,'forward_iteration',eps_x=1e-6,eps_y=1e-6)
        table=next(t for t in r.tables if t[0]=='Bảng tổng hợp vòng lặp')
        self.assertEqual(table[1][3],'Độ thay đổi theo x')
        self.assertNotIn('Cận sai số',table[1][3])
        self.assertIn('dừng thực hành',r.text())

    def test_short_polynomial_is_compact_and_negative_signs_are_separated(self):
        r=sample()
        formulas=[value for kind,value in r.presentation['blocks'] if kind=='formula']
        polynomial=[f for f in formulas if f.startswith('p(t)=') and '4.23' in f]
        self.assertEqual(len(polynomial),1)
        self.assertIn('-(0.56)',polynomial[0])
        # Các số hạng còn lại có thể xuống dòng theo chiều rộng thực của
        # MathText; không mở mỗi số hạng thành một công thức riêng.
        self.assertLessEqual(sum(f.startswith(r'\qquad ') for f in formulas),2)
        self.assertTrue(any(f.startswith('H(t)=') for f in formulas))
        self.assertNotIn('+(-',polynomial[0]);self.assertNotIn('+-',polynomial[0])

    def test_detail_mode_opens_existing_trace_without_changing_numbers(self):
        summary=sample();detailed=sample(detail_level='detailed')
        self.assertEqual(summary.value,detailed.value)
        self.assertEqual(summary.tables,detailed.tables)
        self.assertTrue(all(n['open'] for n in nodes(detailed.presentation['inverse_layout']) if n['kind']=='details'))

    def test_failed_certified_initialization_does_not_change_stop_mode(self):
        r=solve_inverse([1,1.1,1.2,1.3,1.4],[1,1.21,1.44,1.69,1.96],1.3225,
                        'forward_iteration',interval=(1.149,1.151),stop_mode='certified')
        self.assertEqual(r.presentation['inverse_solution']['status'],'certification_unavailable')
        self.assertIn('không tự chuyển sang dừng thực hành',r.text())
        stop=next(n for n in nodes(r.presentation['inverse_layout']) if n.get('title')=='Hai điều kiện dừng độc lập')
        self.assertFalse(any(n.get('latex','').startswith('s_j=') for n in nodes(stop['children'])))

    def test_negative_samples_direct_methods_and_failure_formulas_render(self):
        reports=[sample(),sample(True),
                 solve_inverse([1,2,3],[1,4,9],6,inverse_form='lagrange'),
                 solve_inverse([0,1,2],[0,1,8],.5,'forward_iteration')]
        for r in reports:
            with self.subTest(method=r.title):
                for kind,value in r.presentation['blocks']:
                    if kind=='formula':self.assertTrue(math_png(value).startswith(b'\x89PNG'))
                self.assertNotIn('\\frac',r.text())
                self.assertIn('7. Kết luận',r.text())
        self.assertIn('1.25',reports[-1].text())
        self.assertIsNone(reports[-1].value)


if __name__=='__main__':unittest.main()
