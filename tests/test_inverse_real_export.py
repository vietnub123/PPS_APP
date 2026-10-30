"""Bản HTML rộng giữ một bảng chính; phần chia cột chỉ dùng khi in."""
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest

from pps.inverse_solution import solve_inverse
from pps.math_view import export_html


class VisibleTables(HTMLParser):
    def __init__(self):
        super().__init__();self.stack=[];self.count=0

    def handle_starttag(self,tag,attrs):
        attributes=dict(attrs)
        hidden=(self.stack[-1][1] if self.stack else False)
        hidden=hidden or 'print-table' in attributes.get('class','').split()
        hidden=hidden or (tag=='details' and 'open' not in attributes)
        if tag=='table' and not hidden:self.count+=1
        if tag not in ('meta','img','br','hr','input','link'):self.stack.append((tag,hidden))

    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                del self.stack[i:];break


class InverseRealExport(unittest.TestCase):
    def test_screen_keeps_three_main_tables_and_print_preserves_all_rows(self):
        r=solve_inverse([1.6,1.8,2,2.2],[4.23,3.67,2.99,1.24],2,
                        'backward_iteration',eps_x=1e-6,eps_y=1e-6,stop_mode='certified')
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'inverse.html';export_html(r,path)
            html=path.read_text(encoding='utf-8')
        parser=VisibleTables();parser.feed(html)
        self.assertEqual(parser.count,3)
        self.assertIn('.screen-table{display:none}',html)
        self.assertIn('beforeprint',html)
        self.assertIn('Vòng 6',html)
        self.assertIn('-0.332897553981',html)
        self.assertIn('thead{display:table-header-group}',html)
        self.assertNotIn('src="http',html)

    def test_long_table_stays_one_on_screen_and_splits_only_for_print(self):
        from pps.common import Report
        r=Report('Bảng nội suy',presentation={'inverse_layout':[{'kind':'table','index':0}],
                                              'inverse_tables':{0:{'text_columns':[]}}})
        r.table('Dữ liệu đủ cột',['i']+[f'cấp {i}' for i in range(6)],
                [[0]+['123456789012345678901234567890']*6])
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'long.html';export_html(r,path)
            html=path.read_text(encoding='utf-8')
        parser=VisibleTables();parser.feed(html)
        self.assertEqual(parser.count,1)
        self.assertTrue('class="screen-table"' in html,'Missing single-table screen version')
        self.assertTrue('class="print-table"' in html,'Missing print groups for long numbers')
        self.assertTrue('Nhóm cột' in html,'Print should split wide values')
