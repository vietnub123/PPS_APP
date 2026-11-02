"""Hồi quy con lăn toàn app: popup Tcl không có đối tượng widget Python."""
from types import SimpleNamespace
import tkinter as tk
import unittest
from unittest.mock import Mock

from pps.gui import App


class ScrollFormTests(unittest.TestCase):
    def setUp(self):
        # Không cần tạo cửa sổ Tk để tái hiện lỗi ánh xạ native popup.
        self.canvas=SimpleNamespace(master=None,yview_scroll=Mock())
        self.body=SimpleNamespace(master=self.canvas)
        self.app=SimpleNamespace(form_canvas=self.canvas,form_body=self.body,winfo_containing=Mock())
        self.event=SimpleNamespace(x_root=120,y_root=240,delta=120)

    def test_native_popdown_and_destroyed_window_do_not_raise_or_scroll_form(self):
        for error in (KeyError('popdown'),tk.TclError('bad window path name')):
            with self.subTest(error=type(error).__name__):
                self.app.winfo_containing.side_effect=error
                self.assertIsNone(App.scroll_form(self.app,self.event))
        self.canvas.yview_scroll.assert_not_called()

    def test_wheel_still_scrolls_form_children_in_both_directions(self):
        self.app.winfo_containing.return_value=SimpleNamespace(master=self.body)
        for delta,expected in ((120,-1),(-240,2)):
            with self.subTest(delta=delta):
                self.canvas.yview_scroll.reset_mock()
                self.event.delta=delta
                App.scroll_form(self.app,self.event)
                self.canvas.yview_scroll.assert_called_once_with(expected,'units')

    def test_wheel_over_result_panel_or_outside_app_does_not_scroll_form(self):
        for widget in (SimpleNamespace(master=None),None):
            with self.subTest(widget=widget):
                self.app.winfo_containing.return_value=widget
                App.scroll_form(self.app,self.event)
        self.canvas.yview_scroll.assert_not_called()


if __name__=='__main__':unittest.main()
