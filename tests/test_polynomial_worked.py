"""Đối chiếu phép tính hiển thị với đại số hữu tỷ và đề thật, không chỉ đáp số."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
import math
import tempfile
import unittest

from openpyxl import load_workbook

from pps import interpolation as ip, calculus as ca
from pps import chapter1_tools as ch1
from pps.common import set_display_digits
from pps.gui import dispatch
from pps.math_view import export_html, math_png


ROOT=Path(__file__).resolve().parents[1]


def mul(a,b):
    c=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return c


def exact_polynomial(x,y):
    answer=[F(0)]*len(x)
    for i in range(len(x)):
        b=[F(1)];den=F(1)
        for j in range(len(x)):
            if i!=j:
                b=mul(b,[-x[j],F(1)]);den*=x[i]-x[j]
        for k,v in enumerate(b):answer[k]+=v*y[i]/den
    return answer


def evaluate(a,z,order=0):
    for _ in range(order):a=[i*a[i] for i in range(1,len(a))] or [F(0)]
    value=F(0)
    for v in reversed(a):value=value*z+v
    return value


class PolynomialWorkedTests(unittest.TestCase):
    def test_displayed_term_sums_match_independent_exact_polynomial(self):
        # Chẵn/lẻ, gốc Gauss khác nhau, dữ liệu không chỉ là một bậc thấp.
        for count in range(1,9):
            x=list(range(count));y=[(i*i+3*i)%11-4 for i in x]
            ref=exact_polynomial(list(map(F,x)),list(map(F,y)))
            methods=['Lagrange','Newton bất kỳ','Newton bất kỳ lùi','Newton tiến','Newton lùi','Gauss I','Gauss II']
            methods+=['Stirling'] if count%2 else ['Bessel']
            for method in methods:
                with self.subTest(count=count,method=method):
                    r=ip.interpolate(x,y,method,.25,2)
                    d=r.presentation['worked_solution']
                    self.assertEqual(len(d['terms']),count)
                    for order in (0,2):
                        self.assertAlmostEqual(float(d['values'][order]),float(evaluate(ref,F(1,4),order)),places=10)
                    self.assertTrue(all(row['passed'] for row in d['comparison']))

    def test_actual_20241_stirling_trace_contains_both_answers_and_sources(self):
        book=load_workbook(ROOT/'kienthuc/20241GKtest2.xlsx',read_only=True,data_only=True)
        try:rows=list(book['Sheet3'].values)
        finally:book.close()
        x=[r[0] for r in rows[1:]];y=[r[1] for r in rows[1:]]
        r=dispatch('Nội suy đa thức','Stirling',{'target':'4','count':'9','order':'1'},x,y)
        d=r.presentation['worked_solution']
        self.assertEqual(d['used_ids'],list(range(22,31)))
        self.assertEqual(d['h'],Decimal('.117'))
        self.assertAlmostEqual(float(d['tau']),-14/39)
        self.assertAlmostEqual(float(d['values'][0]),5.442986424022284,places=13)
        self.assertAlmostEqual(float(d['values'][1]),-2.673281525949639,places=13)
        self.assertEqual(d['terms'][1]['operands'],[Decimal('-.3074'),Decimal('-.3420')])
        self.assertEqual(d['terms'][5]['sigma'],0)
        self.assertEqual(d['terms'][7]['source_rows'],[0,1])
        self.assertEqual(d['terms'][8]['denominator'],math.factorial(8))
        with localcontext() as ctx:
            ctx.prec=d['precision']
            self.assertEqual(sum((t['value'] for t in d['terms']),Decimal(0)),d['values'][0])
            self.assertEqual(sum((t['derivative'] for t in d['terms']),Decimal(0)),d['values'][1])
        text=r.text()
        for phrase in ('Đóng góp từng hạng vào P(z)','Đóng góp từng hạng vào đạo hàm','các ô nguồn'):
            self.assertIn(phrase,text)

    def test_roots_of_basis_and_change_of_variable_are_safe(self):
        for method in ('Gauss I','Gauss II','Stirling','Newton tiến','Newton lùi'):
            d=ip.interpolate([2,4,6],[4,16,36],method,4,2).presentation['worked_solution']
            self.assertEqual(d['values'][0],16)
            self.assertEqual(d['values'][2],2)
            self.assertEqual(d['raw_derivative'],8)
        b=ip.interpolate([-1,0,1,2],[0,1,2,9],'Bessel',.5,1).presentation['worked_solution']
        self.assertEqual(b['values'][0],Decimal('1.125'))
        self.assertEqual(b['values'][1],Decimal('.75'))
        self.assertEqual(b['terms'][3]['value'],0)
        self.assertEqual(b['terms'][3]['derivative'],Decimal('-.25'))

    def test_selection_preserves_source_ids_and_reports_extrapolation(self):
        r=ip.interpolate([4,0,3,1,2],[16,0,9,1,4],'Stirling',1.2,1,count=3)
        self.assertEqual(r.presentation['worked_solution']['used_ids'],[1,3,4])
        self.assertEqual(r.presentation['selection'],{'input_count':5,'used_count':3})
        r=ip.interpolate([0,1,2],[0,1,4],'Stirling',5,1)
        self.assertIn('ngoại suy',r.text())

    def test_unequal_newton_uses_divided_differences_without_factorials(self):
        for method in ('Newton bất kỳ','Newton bất kỳ lùi','Lagrange'):
            d=ip.interpolate([0,1,3],[1,3,13],method,2,1).presentation['worked_solution']
            self.assertAlmostEqual(float(d['values'][0]),7,places=12)
            self.assertAlmostEqual(float(d['values'][1]),5,places=12)
            if method!='Lagrange':
                self.assertEqual(d['terms'][2]['beta'],1)
                self.assertEqual(d['terms'][2]['denominator'],1)

    def test_horner_trace_reconstructs_every_multiplication_and_taylor_coefficient(self):
        r=ip.horner([3.5,-2.78,5.63,0,-15.28,1.54],2.57,3)
        d=r.presentation['worked_solution'];passes=d['passes'];c=F('2.57')
        self.assertEqual([p['remainder'] for p in passes],list(map(Decimal,['328.96489401215','670.951607015','527.348323','208.2231'])))
        self.assertEqual(passes[2]['derivative'],Decimal('1054.696646'))
        self.assertEqual(passes[3]['derivative'],Decimal('1249.3386'))
        for i,p in enumerate(passes):
            if i:self.assertEqual(p['input'],passes[i-1]['quotient'])
            for row in p['steps'][1:]:
                self.assertEqual(F(row['product']),c*F(row['previous']))
                self.assertEqual(F(row['accumulated']),F(row['input'])+F(row['product']))
            self.assertEqual(F(p['derivative']),math.factorial(i)*F(p['remainder']))
        self.assertIn('c·b_(j−1)',r.text())

    def test_horner_leading_zeros_constant_and_orders_above_degree(self):
        for coef,value,degree in [([0,0,1,0,0],4,2),([7],7,0),([0,0],0,0)]:
            d=ip.horner(coef,2,1000).presentation['worked_solution']
            self.assertEqual(d['degree'],degree)
            self.assertEqual(d['passes'][0]['derivative'],value)
            self.assertEqual(len(d['passes']),degree+1)

    def test_derivative_weights_and_moments_at_nodes_and_unequal_grid(self):
        for x,y,z,order,weights,value in [
            ([0,1,2],[1,2,5],0,1,[F(-3,2),F(2),F(-1,2)],0),
            ([0,1,2],[1,2,5],1,2,[F(1),F(-2),F(1)],2),
            ([0,1,3],[1,3,13],1,1,[F(-2,3),F(1,2),F(1,6)],3),
        ]:
            d=ca.differentiate(x,y,z,2,order).presentation['worked_solution']
            self.assertAlmostEqual(float(d['value']),value,places=12)
            self.assertTrue(all(row['passed'] for row in d['moments']))
            for row,wanted in zip(d['weights_trace'],weights):
                self.assertAlmostEqual(float(row['weight']),float(wanted),places=12)
                self.assertEqual(len(row['steps']),2)
                self.assertEqual(row['steps'][-1]['coefficients'][order],row['coefficient'])

    def test_worked_html_has_columns_full_tables_and_print_details(self):
        r=ip.interpolate([-2,-1,0,1,2],[17,1,1,5,25],'Stirling',.25,1)
        for _,forms in r.presentation['formulas']:
            for latex in forms:self.assertTrue(math_png(latex).startswith(b'\x89PNG'))
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'loi_giai.html';export_html(r,path)
            content=path.read_text(encoding='utf-8')
        for fragment in ('class="columns','<details','beforeprint','Đóng góp từng hạng','data:image/png;base64,','print-table'):
            self.assertIn(fragment,content)
        self.assertNotIn('src="http',content)
        self.assertNotIn('MathJax',content)

    def test_display_digits_are_respected_without_changing_trace_numbers(self):
        try:
            set_display_digits(3)
            r=ip.horner([1,0,0],1.234567,1)
            self.assertEqual(r.presentation['worked_solution']['passes'][0]['remainder'],Decimal('1.524155677489'))
            self.assertIn('1.524',r.text())
        finally:set_display_digits(7)

    def test_supplementary_selection_chebyshev_and_missing_data_reports(self):
        r=ip.select_points([4,0,3,1,2],[16,0,9,1,4],1.2,3)
        self.assertEqual(r.presentation['worked_solution']['used_ids'],[1,3,4])
        self.assertIn('cửa sổ',r.text())
        r=ip.chebyshev(2,-1,1)
        self.assertEqual(len(r.presentation['worked_solution']['angles']),3)
        self.assertIn('không chứa hai đầu',r.text())
        for _,forms in r.presentation['formulas']:
            for latex in forms:self.assertTrue(math_png(latex).startswith(b'\x89PNG'))
        r=ch1.fill_missing([0,1,2,3],[0,None,4,9],2)
        self.assertEqual(r.value[1],1)
        self.assertEqual(r.presentation['worked_solution']['selected_ids'],[0,2,3])
        self.assertIn('Kiểm tra tương thích bậc',r.text())


if __name__=='__main__':unittest.main()
