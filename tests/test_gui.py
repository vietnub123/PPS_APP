"""Desktop integration tests; Tk window stays withdrawn during tests."""
import json
import tempfile
import time
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch
from openpyxl import Workbook, load_workbook
from pps.gui import App, TOOLS, dispatch


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:cls.app=App();cls.app.withdraw()
        except tk.TclError as exc:
            raise unittest.SkipTest(f'Không có môi trường Tcl/Tk dùng được: {exc}') from exc

    @classmethod
    def tearDownClass(cls):cls.app.close()

    def test_every_method_accepts_its_editable_example(self):
        for tool,(methods,_) in TOOLS.items():
            self.app.select_tool(tool)
            for method in methods:
                with self.subTest(tool=tool,method=method):
                    self.app.method.set(method);self.app.show_form()
                    self.app.reset_example()
                    s=self.app.snapshot()
                    r=dispatch(tool,method,s['values'],s['x'],s['y'])
                    self.assertTrue(r.title)
                    if tool=='Nội suy ngược':self.assertIsNone(r.presentation['inverse_solution']['failure'])
                    if tool in ('Spline','Bình phương tối thiểu'):self.assertIsNone(r.presentation['worked_solution']['failure'])
                    self.app.display(r)
                    self.app.update_idletasks()

    def test_failed_inverse_report_stays_visible_and_exportable(self):
        self.app.select_tool('Nội suy ngược')
        r=dispatch('Nội suy ngược','Lặp tiến',{'target':'.5','tol':'1e-6','max_iter':'1'},'0 1 2','0 1 8')
        self.app.display(r);self.app.update_idletasks()
        self.assertIs(self.app.report,r)
        self.assertIn('Chưa đạt',self.app.status.get())
        self.assertTrue(self.app.table_select['values'])
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'failed.html'
            with patch('pps.gui.filedialog.asksaveasfilename',return_value=str(target)):
                self.app.export_report()
            self.assertIn('1.25',target.read_text(encoding='utf-8'))

    def test_inverse_layout_reflows_and_opens_details_without_solving_again(self):
        r=dispatch('Nội suy ngược','Lặp có cận co',
                   {'target':'4','a':'1.6','b':'1.8','tol':'1e-6','residual_tol':'1e-6'},
                   '1.6 1.8 2 2.2','4.23 3.67 2.99 1.24')
        self.app.display(r)
        try:
            self.app.deiconify();self.app.geometry('1500x810+0+0');self.app.update()
            view=self.app.math_document.inverse_document
            self.assertIs(view.report,r)
            self.assertTrue(view.column_groups)
            self.assertTrue(any(group.column_count==2 for group in view.column_groups))
            detail=next(section for section in view.detail_sections if not section.opened)
            with patch('pps.gui.dispatch',side_effect=AssertionError('Resizing must not solve')):
                detail.set_open(True);self.app.update_idletasks()
                self.assertTrue(detail.opened);self.assertTrue(detail.content.winfo_children())
                detail.toggle();self.assertFalse(detail.opened)
                self.app.geometry('1050x810+0+0');self.app.update()
                self.assertTrue(all(group.column_count==1 for group in view.column_groups))
            self.assertIs(self.app.report,r)
            self.assertAlmostEqual(r.value,1.666001162884,places=11)
            self.app.math_document.message('Đã chọn phương pháp khác.')
            self.app.update_idletasks()
            self.assertFalse(view.winfo_ismapped())
            self.assertTrue(self.app.math_document.text.winfo_ismapped())
        finally:
            self.app.withdraw();self.app.geometry('1380x860')

    def test_inverse_json_choices_survive_load_run_and_method_switch(self):
        source=Path(__file__).resolve().parents[1]/'examples'/'noi_suy_nguoc'/'A_lagrange.json'
        with patch('pps.gui.filedialog.askopenfilename',return_value=str(source)):
            self.app.load_project()
        state=self.app.snapshot()
        self.assertEqual(state['values']['inverse_form'],'lagrange')
        self.assertEqual(state['values']['interval'],'[1,1.5]')
        self.assertIsNone(self.app.report)
        r=dispatch(state['tool'],state['method'],state['values'],state['x'],state['y'])
        self.assertEqual(r.presentation['inverse_solution']['model']['basis'],'lagrange')
        self.app.method.set('Lặp tiến');self.app.show_form()
        self.assertNotIn('inverse_form',self.app.snapshot()['values'])
        self.app.method.set('Hàm ngược — Lagrange');self.app.show_form()
        self.assertEqual(self.app.snapshot()['values']['inverse_form'],'lagrange')
        self.app.reset_example()
        self.assertNotIn('inverse_form',self.app.snapshot()['values'])

    def test_saved_inverse_selected_indices_remain_json_and_worked_subjects_display(self):
        task={'tool':'Nội suy ngược','method':'Lặp có cận co',
              'values':{'target':'4','a':'1.6','b':'1.8','tol':'1e-6','residual_tol':'1e-6',
                        'selected_indices':[0,1,2,3]},
              'x':'1.6 1.8 2 2.2','y':'4.23 3.67 2.99 1.24'}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'selected.json';path.write_text(json.dumps(task),encoding='utf-8')
            with patch('pps.gui.filedialog.askopenfilename',return_value=str(path)):self.app.load_project()
            state=self.app.snapshot()
            self.assertEqual(json.loads(state['values']['selected_indices']),[0,1,2,3])
            report=dispatch(state['tool'],state['method'],state['values'],state['x'],state['y'])
            self.assertIsNone(report.presentation['inverse_solution']['failure'])
        for tool,method,values,x,y in [
            ('Spline','Cubic tự nhiên',{'target':'2'},'0 1 3','0 1 0'),
            ('Bình phương tối thiểu','Tuyến tính theo cơ sở',{'basis':'1;x','solver':'Hệ chuẩn — Gauss'},'0 1 2 3','1 2 2 4'),
            ('Nội suy đa thức','Stirling',{'target':'.25','order':'1'},'-2 -1 0 1 2','17 1 1 5 25'),
            ('Đạo hàm & Horner','Horner',{'coef':'3 0 -2 -1','target':'2','order':'3'},'',''),
            ('Đạo hàm & Horner','Đạo hàm từ bảng',{'target':'1','degree':'2','order':'1'},'0 1 3','1 3 13')]:
            with self.subTest(tool=tool):
                report=dispatch(tool,method,values,x,y)
                self.assertIsNone(report.presentation['worked_solution']['failure'])
                self.app.display(report);self.app.update_idletasks()
                self.assertIs(self.app.math_document.inverse_document.report,report)
                self.assertIn('Hoàn tất',self.app.status.get())
        # Các bài đề thật lưu x/y dưới dạng mảng JSON, dùng đúng đường Mở bài.
        folder=Path(__file__).resolve().parents[1]/'examples'/'de_20251'
        for stem in ('01a_mu_x2_SSE_104','02a_lap_tien_cuc_bo'):
            with patch('pps.gui.filedialog.askopenfilename',return_value=str(folder/(stem+'.json'))):
                self.app.load_project()
            state=self.app.snapshot()
            report=dispatch(state['tool'],state['method'],state['values'],state['x'],state['y'])
            data=report.presentation.get('inverse_solution',report.presentation.get('worked_solution'))
            self.assertIsNone(data['failure'],str(data['failure']))
    def test_excel_csv_import_export_and_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp); source=tmp/'input.xlsx'
            wb=Workbook();ws=wb.active;ws.append(['x','y'])
            for x in range(3):ws.append([x,x*x])
            wb.save(source)
            self.app.select_tool('Nội suy đa thức');self.app.method.set('Newton');self.app.show_form()
            self.app.form['newton_nodes'].set('Mốc bất kỳ')
            with patch('pps.gui.filedialog.askopenfilename',return_value=str(source)):
                self.app.import_data()
            s=self.app.snapshot();self.assertEqual(s['x'],'0.0 1.0 2.0')
            self.app.display(dispatch(s['tool'],s['method'],s['values'],s['x'],s['y']))
            out=tmp/'output.xlsx'
            with patch('pps.gui.filedialog.asksaveasfilename',return_value=str(out)):self.app.export_tables()
            wb=load_workbook(out);self.assertEqual(len(wb.sheetnames),2);self.assertEqual(wb.worksheets[0]['A2'].value,0);wb.close()
            out=tmp/'output.csv'
            with patch('pps.gui.filedialog.asksaveasfilename',return_value=str(out)):self.app.export_tables()
            self.assertIn('0.0',out.read_text(encoding='utf-8-sig'))
            project=tmp/'project.json'
            with patch('pps.gui.filedialog.asksaveasfilename',return_value=str(project)):self.app.save_project()
            self.app.select_tool('Bài toán biên')
            with patch('pps.gui.filedialog.askopenfilename',return_value=str(project)):self.app.load_project()
            self.assertEqual(self.app.snapshot(),json.loads(project.read_text(encoding='utf-8')))

    def test_newton_variants_precision_and_switch(self):
        from pps.common import set_display_digits,fmt
        import numpy as np
        for nodes in ('Mốc cách đều','Mốc bất kỳ'):
            for direction in ('Tiến','Lùi'):
                r=dispatch('Nội suy đa thức','Newton',{'target':'1.5','order':'0','direction':direction,'newton_nodes':nodes},'0 1 2 3','1 2 5 10')
                self.assertAlmostEqual(r.value(1.5),3.25)
        self.assertNotIn('Newton',TOOLS)
        r=dispatch('Newton','Mốc bất kỳ',{'target':'1.5','order':'0','direction':'Lùi'},'0 0.7 2 3','1 1.49 5 10')
        self.assertAlmostEqual(r.value(1.5),3.25)
        set_display_digits(0);self.assertEqual(fmt(100), '100')
        set_display_digits(10);self.assertEqual(fmt(1/3),'0.3333333333')
        set_display_digits(7)
        self.app.select_tool('Nội suy đa thức')
        self.app.display(r)
        self.app.method.set('Gauss I');self.app.show_form()
        self.assertIsNone(self.app.report)
        self.assertEqual(len(self.app.tree.get_children()),0)

    def test_interpolation_builds_polynomial_without_a_target(self):
        report=dispatch('Nội suy đa thức','Lagrange',{'target':'','order':'0'},
                        '1.2 1.5 1.7 1.8 2.1 2.3',
                        '.892 1.179 1.358 1.445 1.688 1.839')
        self.assertAlmostEqual(report.value(0), -34011/5500, places=13)

    def test_async_calculate_button(self):
        self.app.select_tool('Nội suy đa thức');self.app.reset_example();self.app.run()
        deadline=time.monotonic()+20
        while self.app.future and not self.app.future.done() and time.monotonic()<deadline:
            self.app.update();time.sleep(.02)
        self.assertTrue(self.app.future.done())
        self.app.poll();self.assertIsNotNone(self.app.report)


if __name__=='__main__':unittest.main()
