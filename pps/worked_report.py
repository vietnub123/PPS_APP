"""Bộ dựng lời giải dùng chung, giữ số tính toán tách khỏi bố cục hiển thị."""
from .inverse_presentation import _Writer, _DIGITS, number, tex_number
from .common import Report


class ReportBuilder(_Writer):
    """Các nhóm, cột và chi tiết chung cho những bài giải phương pháp số."""
    def __init__(self, report, detail_level='summary', display_digits=12):
        super().__init__(report, detail_level)
        self.digits=max(0,int(display_digits))

    def number(self,value,exact=False):
        return number(value,digits=self.digits,exact=exact)

    def tex(self,value,exact=False):
        return tex_number(value,digits=self.digits,exact=exact)

    def table(self,*args,**kwargs):
        token=_DIGITS.set(self.digits)
        try:return super().table(*args,**kwargs)
        finally:_DIGITS.reset(token)

    def expression(self,*args,**kwargs):
        token=_DIGITS.set(self.digits)
        try:return super().expression(*args,**kwargs)
        finally:_DIGITS.reset(token)

    def finish(self):
        super().finish()
        presentation=self.report.presentation
        presentation['worked_layout']=presentation.pop('inverse_layout')
        presentation['worked_tables']=presentation.pop('inverse_tables')
        presentation.pop('difference_tables',None)
        return self.report


def input_failure(title, values, x, y, error):
    """Giữ cấu hình và lý do lỗi ngay cả khi chưa đọc được hai dãy số."""
    report=Report(title)
    report.presentation['worked_solution']={
        'status':'invalid_input','failure':{'step':'Đọc dữ liệu và tham số','message':str(error)},
        'input':{'values':dict(values),'x':x,'y':y}}
    writer=ReportBuilder(report)
    with writer.group('section','1. Dữ liệu và lựa chọn'):
        writer.text('Tham số: '+str(values));writer.text('x: '+str(x));writer.text('y: '+str(y))
    with writer.group('section','2. Chưa tính được kết quả',keep_together=True):
        writer.text(str(error),'failed')
        writer.text('Giữ nguyên dữ liệu; sửa trường chưa hợp lệ rồi chạy lại.')
    return writer.finish()
