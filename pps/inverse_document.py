"""Bố cục lời giải nội suy ngược trong cửa sổ Tk hiện có.

Chỉ đọc cây trình bày và các bảng đã tính. Các nhóm chi tiết được dựng khi
mở lần đầu; thay độ rộng cửa sổ không chạy lại phép nội suy.
"""
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageDraw, ImageFont, ImageTk

from .common import fmt


COLORS = {
    'ink': '#193442', 'muted': '#506875', 'line': '#d6e1e6',
    'header': '#e6f0f2', 'stripe': '#f6f9fa', 'selected': '#e1f0e9',
    'success': '#235e44', 'warning': '#805518', 'failed': '#9a3131', 'error': '#9a3131',
}


def _font(size=15, bold=False):
    # DejaVu đi kèm Matplotlib có cả ∇/Δ và tiếng Việt; Segoe UI khi vẽ
    # trực tiếp bằng Pillow có thể thay ký hiệu ∇ thành ô vuông.
    from matplotlib.font_manager import FontProperties, findfont
    path = findfont(FontProperties(family='DejaVu Sans', weight='bold' if bold else 'normal'))
    return ImageFont.truetype(path, size)


def _wrap(text, font, width):
    lines = []
    for paragraph in str(text).splitlines() or ['']:
        line = ''
        for word in paragraph.split():
            candidate = (line + ' ' + word).strip()
            if line and font.getlength(candidate) > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return lines


def inverse_table_image(report, index, limit=80, font_size=15, column_limit=16):
    """Vẽ đúng các ô đã lưu; đánh dấu theo chỉ số ô của bảng hiển thị."""
    _, headers, source_rows = report.tables[index]
    headers = headers if column_limit is None else headers[:column_limit]
    rows = source_rows if limit is None else source_rows[:limit]
    metadata = report.presentation.get('worked_tables', report.presentation.get('inverse_tables', {})).get(index, {})
    selected = {tuple(cell) for cell in metadata.get('used_cells', [])}
    text_columns = set(metadata.get('text_columns', []))
    regular, bold = _font(font_size), _font(font_size, True)
    strings = [[fmt(value) for value in row[:len(headers)]] for row in rows]
    widths = []
    for column, header in enumerate(headers):
        measures = [bold.getlength(str(header))]
        measures.extend(regular.getlength(row[column]) for row in strings if column < len(row))
        width = max(45, int(max(measures, default=0)) + 20)
        widths.append(min(width, 300) if column in text_columns else width)
    # Diễn giải có thể xuống dòng; số và dấu mũ giữ nguyên một dòng để đọc đúng.
    cells = [[_wrap(str(header), bold, widths[j] - 16) for j, header in enumerate(headers)]]
    cells.extend([
        _wrap(row[j] if j < len(row) else '', regular, widths[j] - 16)
        if j in text_columns else [row[j] if j < len(row) else '']
        for j in range(len(headers))
    ] for row in strings)
    line_height = font_size + 6
    heights = [max(32, max((len(cell) for cell in row), default=1) * line_height + 12) for row in cells]
    result = Image.new('RGB', (max(1, sum(widths)), max(1, sum(heights))), 'white')
    draw = ImageDraw.Draw(result)
    top = 0
    for i, row in enumerate(cells):
        left = 0
        for j, lines in enumerate(row):
            used = i > 0 and (i - 1, j) in selected
            fill = COLORS['header'] if i == 0 else COLORS['selected'] if used else COLORS['stripe'] if i % 2 else 'white'
            draw.rectangle((left, top, left + widths[j], top + heights[i]), fill=fill, outline=COLORS['line'])
            if used:
                draw.rectangle((left + 1, top + 1, left + widths[j] - 1, top + heights[i] - 1), outline='#639880', width=2)
            font = bold if i == 0 or used else regular
            for line_number, line in enumerate(lines):
                x = left + 9 if j in text_columns else left + widths[j] - 9 - font.getlength(line)
                draw.text((x, top + 6 + line_number * line_height), line, font=font, fill=COLORS['ink'])
            left += widths[j]
        top += heights[i]
    return result


class _ImageViewport(ttk.Frame):
    """Cuộn tại bảng/công thức rộng, không ép toàn bộ trang rộng theo ảnh."""
    def __init__(self, parent, image, *, max_height=None, on_page_wheel=None):
        super().__init__(parent, style='Inverse.TFrame')
        self.columnconfigure(0, weight=1)
        height = image.height + 8
        if max_height:
            height = min(height, max_height)
        self.canvas = tk.Canvas(self, width=1, height=height, background='white', highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky='ew')
        self.horizontal = ttk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.vertical = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.horizontal.set, yscrollcommand=self.vertical.set,
                              scrollregion=(0, 0, image.width + 10, image.height + 8))
        self.photo = ImageTk.PhotoImage(image, master=self)
        self.canvas.create_image(5, 4, image=self.photo, anchor='nw')
        self.image_width = image.width + 10
        self.vertical_scroll = image.height + 8 > height
        self.on_page_wheel = on_page_wheel
        if self.vertical_scroll:
            self.vertical.grid(row=0, column=1, sticky='ns')
        self.canvas.bind('<Configure>', self._resize)
        self.canvas.bind('<MouseWheel>', self._wheel)

    def _resize(self, event):
        if event.width + 1 < self.image_width:
            self.horizontal.grid(row=1, column=0, sticky='ew')
        else:
            self.horizontal.grid_remove()
            self.canvas.xview_moveto(0)

    def _wheel(self, event):
        if self.vertical_scroll:
            first, last = self.canvas.yview()
            direction = -int(event.delta / 120)
            if (direction < 0 and first > 0) or (direction > 0 and last < 1):
                self.canvas.yview_scroll(direction, 'units')
                return 'break'
        return self.on_page_wheel(event) if self.on_page_wheel else None


class _Columns(ttk.Frame):
    def __init__(self, parent, document, nodes):
        super().__init__(parent, style='Inverse.TFrame')
        self.document = document
        self.panels = []
        self.column_count = 0
        for node in nodes:
            panel = ttk.Frame(self, padding=(10, 8), relief='solid', borderwidth=1, style='Inverse.TFrame')
            panel.columnconfigure(0, weight=1)
            document._render_nodes(panel, [node])
            self.panels.append(panel)
        self.bind('<Configure>', self._resize)
        self._arrange(1)

    def _arrange(self, count):
        if count == self.column_count:
            return
        self.column_count = count
        for column in range(2):
            self.columnconfigure(column, weight=1 if column < count else 0,
                                 uniform='inverse_columns' if column < count else '')
        for i, panel in enumerate(self.panels):
            panel.grid_forget()
            panel.grid(row=i // count, column=i % count, sticky='nsew',
                       padx=(0 if i % count == 0 else 8, 0), pady=(0, 10))

    def _resize(self, event):
        self._arrange(2 if event.width >= 840 and len(self.panels) > 1 else 1)


class _Details(ttk.Frame):
    def __init__(self, parent, document, node):
        super().__init__(parent, style='Inverse.TFrame')
        self.document, self.node = document, node
        self.opened = False
        self.built = False
        self.columnconfigure(0, weight=1)
        self.button = ttk.Button(self, text='', command=self.toggle, style='InverseDetail.TButton')
        self.button.grid(row=0, column=0, sticky='ew')
        self.content = ttk.Frame(self, padding=(12, 8), style='Inverse.TFrame')
        self.content.columnconfigure(0, weight=1)
        self.set_open(bool(node.get('open', False)))

    def set_open(self, opened):
        self.opened = bool(opened)
        self.button.configure(text=('▾  ' if self.opened else '▸  ') + self.node.get('title', 'Chi tiết'))
        if self.opened:
            if not self.built:
                self.document._render_nodes(self.content, self.node.get('children', []))
                self.built = True
            self.content.grid(row=1, column=0, sticky='ew')
        else:
            self.content.grid_remove()

    def toggle(self):
        self.set_open(not self.opened)


class InverseDocument(ttk.Frame):
    """Trang lời giải thích ứng độ rộng, có các chi tiết mở độc lập."""
    def __init__(self, parent):
        super().__init__(parent, style='Inverse.TFrame')
        style = ttk.Style(self)
        style.configure('Inverse.TFrame', background='white')
        style.configure('Inverse.TLabel', background='white')
        style.configure('InverseDetail.TButton', foreground=COLORS['ink'], padding=(10, 7), anchor='w')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(self, background='white', highlightthickness=0, width=1)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.body = ttk.Frame(self.canvas, padding=(18, 16), style='Inverse.TFrame')
        self.body.columnconfigure(0, weight=1)
        self.window = self.canvas.create_window((0, 0), window=self.body, anchor='nw', width=1)
        self.canvas.bind('<Configure>', self._resize)
        self.body.bind('<Configure>', self._content_resize)
        self.bind('<MouseWheel>', self._wheel)
        self.canvas.bind('<MouseWheel>', self._wheel)
        self.report = None
        self.detail_sections = []
        self.column_groups = []

    def _resize(self, event):
        self.canvas.itemconfigure(self.window, width=max(1, event.width))

    def _content_resize(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _wheel(self, event):
        self.canvas.yview_scroll(-int(event.delta / 120), 'units')
        return 'break'

    def clear(self):
        for widget in self.body.winfo_children():
            widget.destroy()
        self.detail_sections.clear()
        self.column_groups.clear()
        self.report = None
        self.canvas.yview_moveto(0)

    def show(self, report):
        self.clear()
        self.report = report
        title = self._label(self.body, report.title, font=('Segoe UI', 18, 'bold'))
        title.grid(row=0, column=0, sticky='ew', pady=(0, 12))
        self._render_nodes(self.body, report.presentation.get('worked_layout', report.presentation.get('inverse_layout', [])), start=1)
        self.canvas.yview_moveto(0)

    def _label(self, parent, text, *, font=('Segoe UI', 11), tone=None):
        color = COLORS.get(tone, COLORS['ink'])
        label = ttk.Label(parent, text=str(text), font=font, foreground=color, style='Inverse.TLabel',
                          anchor='w', justify='left', wraplength=600, width=1)
        label.bind('<Configure>', lambda event: label.configure(wraplength=max(40, event.width - 8)))
        label.bind('<MouseWheel>', self._wheel)
        return label

    def _render_nodes(self, parent, nodes, start=0):
        for row, node in enumerate(nodes, start):
            kind = node.get('kind')
            if kind in ('section', 'panel'):
                widget = ttk.Frame(parent, style='Inverse.TFrame')
                widget.columnconfigure(0, weight=1)
                if node.get('title'):
                    heading = self._label(widget, node['title'], font=('Segoe UI', 13 if kind == 'section' else 11, 'bold'))
                    heading.grid(row=0, column=0, sticky='ew', pady=(0, 7))
                self._render_nodes(widget, node.get('children', []), start=1)
            elif kind == 'columns':
                widget = _Columns(parent, self, node.get('children', []))
                self.column_groups.append(widget)
            elif kind == 'details':
                widget = _Details(parent, self, node)
                self.detail_sections.append(widget)
            elif kind == 'formula':
                from .math_view import math_image
                widget = _ImageViewport(parent, math_image(node.get('latex', '0')), on_page_wheel=self._wheel)
            elif kind == 'table':
                index = node['index']
                widget = ttk.Frame(parent, style='Inverse.TFrame')
                widget.columnconfigure(0, weight=1)
                name, headers, rows = self.report.tables[index]
                if node.get('title', True):
                    label = self._label(widget, name, font=('Segoe UI', 10, 'bold'))
                    label.grid(row=0, column=0, sticky='ew', pady=(0, 4))
                # Toàn bộ bảng thường gặp được giữ trong viewport. Bảng rất lớn
                # xem trong tab dữ liệu/xuất; không tạo ảnh hàng trăm nghìn pixel.
                limit = None if len(rows) <= 500 else 80
                picture = _ImageViewport(widget, inverse_table_image(self.report, index, limit), max_height=520,
                                         on_page_wheel=self._wheel)
                picture.grid(row=1, column=0, sticky='ew')
                if (limit is not None and len(rows) > limit) or len(headers) > 16:
                    shown_rows = len(rows) if limit is None else min(limit, len(rows))
                    label = self._label(widget, f'Bản xem hiển thị {shown_rows}/{len(rows)} hàng, {min(16, len(headers))}/{len(headers)} cột. Tab bảng dữ liệu và bản xuất giữ đầy đủ.', tone='muted')
                    label.grid(row=2, column=0, sticky='ew', pady=(4, 0))
            elif kind == 'text':
                widget = self._label(parent, node.get('text', ''), tone=node.get('tone'))
            else:
                continue
            widget.grid(row=row, column=0, sticky='ew', pady=(0, 8 if kind != 'section' else 14))
