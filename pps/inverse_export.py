"""Xuất lời giải nội suy ngược có nhóm, cột và chi tiết ra HTML ngoại tuyến."""
import base64
import html
import io
from pathlib import Path

from .common import fmt


def _escape(value):
    return html.escape(str(value))


def _fallback_layout(report):
    nodes, current = [], None
    for kind, value in report.presentation.get('blocks', []):
        if kind == 'heading':
            current = {'kind': 'section', 'title': value, 'children': []}
            nodes.append(current)
        else:
            node = {'kind': kind, 'latex' if kind == 'formula' else 'index' if kind == 'table' else 'text': value}
            (nodes if current is None else current['children']).append(node)
    return nodes


def export_inverse_html(report, path):
    """Lưu đầy đủ trace; chi tiết đóng trên màn hình và mở hết khi in."""
    from .math_view import math_image

    tables = report.presentation.get('worked_tables', report.presentation.get('inverse_tables', {}))

    def formula(latex):
        im = math_image(latex)
        out = io.BytesIO()
        im.save(out, format='PNG')
        # Ảnh được dựng 130 dpi; chiều CSS 96 dpi giữ cỡ chữ gần văn bản.
        width = round(im.width * 96 / 130, 2)
        return ('<div class="formula"><img alt="Công thức toán học" '
                f'style="width:{width}px" src="data:image/png;base64,'
                + base64.b64encode(out.getvalue()).decode() + '"></div>')

    def table(index, show_title=True):
        name, headers, rows = report.tables[index]
        metadata = tables.get(index, {})
        selected = {tuple(cell) for cell in metadata.get('used_cells', [])}
        text_columns = set(metadata.get('text_columns', []))
        # Chia theo cả số cột và độ dài số, tránh bảng 7 cột nhưng các số
        # hữu tỷ dài vẫn tràn lề giấy. Lặp cột chỉ số ở từng phần.
        widths = []
        for j, header in enumerate(headers):
            longest = max([min(28, len(str(header)))] + [len(fmt(row[j])) for row in rows if j < len(row)])
            width = max(35, longest * 5.4 + 14)
            widths.append(min(width, 220) if j in text_columns else width)
        groups, group, width = [], [], 0
        for j in range(len(headers)):
            if group and (len(group) >= 7 or width + widths[j] > 640):
                groups.append(group)
                group, width = ([0], widths[0]) if j else ([], 0)
            group.append(j)
            width += widths[j]
        if group:
            groups.append(group)
        parts = ['<div class="table-block">']
        if show_title:
            parts.append('<h3>' + _escape(name) + '</h3>')
        # Màn hình giữ một bảng tổng hợp. Chỉ bản in chia bảng quá rộng,
        # tránh nối nhiều bảng nhỏ theo chiều dọc ngay trên màn hình rộng.
        variants = [(groups, '')] if len(groups) == 1 else [
            ([list(range(len(headers)))], 'screen-table'), (groups, 'print-table')]
        for variant_groups, variant_class in variants:
            if variant_class:
                parts.append(f'<div class="{variant_class}">')
            for part, columns in enumerate(variant_groups, 1):
                if len(variant_groups) > 1:
                    parts.append(f'<p class="muted table-part">Nhóm cột {part}/{len(variant_groups)}</p>')
                parts.append('<div class="table-scroll"><table><thead><tr>')
                parts.extend('<th scope="col"' + (' class="text-cell"' if j in text_columns else '') + '>' + _escape(headers[j]) + '</th>' for j in columns)
                parts.append('</tr></thead><tbody>')
                for i, row in enumerate(rows):
                    parts.append('<tr>')
                    for j in columns:
                        classes = []
                        if (i, j) in selected:
                            classes.append('used')
                        if j in text_columns:
                            classes.append('text-cell')
                        attribute = ' class="' + ' '.join(classes) + '"' if classes else ''
                        value = fmt(row[j]) if j < len(row) else ''
                        parts.append('<td' + attribute + '>' + _escape(value) + '</td>')
                    parts.append('</tr>')
                parts.append('</tbody></table></div>')
            if variant_class:
                parts.append('</div>')
        parts.append('</div>')
        return ''.join(parts)

    def preferred_print_width(node):
        kind = node.get('kind')
        if kind == 'formula':
            return math_image(node.get('latex', '0')).width * 96 / 130
        if kind == 'table':
            # Chỉ ghép cột in nếu mỗi bảng nhỏ đọc được ở nửa trang A4.
            _, headers, rows = report.tables[node['index']]
            lengths = [max([len(str(header))] + [len(fmt(row[j])) for row in rows if j < len(row)])
                       for j, header in enumerate(headers)]
            return sum(max(35, length * 5 + 14) for length in lengths)
        if kind == 'details':
            return 0
        return max((preferred_print_width(child) for child in node.get('children', [])), default=0)

    def render(nodes):
        parts = []
        for node in nodes:
            kind = node.get('kind')
            if kind in ('section', 'panel'):
                tag = 'section' if kind == 'section' else 'div'
                heading = 'h2' if kind == 'section' else 'h3'
                group_class=kind+(' keep-together' if node.get('keep_together') else '')
                parts.append(f'<{tag} class="{group_class}">')
                if node.get('title'):
                    parts.append(f'<{heading}>' + _escape(node['title']) + f'</{heading}>')
                parts.append(render(node.get('children', [])))
                parts.append(f'</{tag}>')
            elif kind == 'columns':
                children = node.get('children', [])
                stack = any(preferred_print_width(child) > 330 for child in children)
                parts.append('<div class="columns' + (' print-stack' if stack else '') + '">')
                for child in children:
                    parts.append('<div class="column-card">' + render([child]) + '</div>')
                parts.append('</div>')
            elif kind == 'details':
                attribute = ' open' if node.get('open') else ''
                parts.append('<details' + attribute + '><summary>' + _escape(node.get('title', 'Chi tiết')) + '</summary>')
                parts.append('<div class="detail-body">' + render(node.get('children', [])) + '</div></details>')
            elif kind == 'text':
                tone = node.get('tone', '')
                if tone == 'error':
                    tone = 'failed'
                allowed = tone if tone in ('success', 'warning', 'failed', 'muted') else ''
                parts.append('<p' + (f' class="{allowed}"' if allowed else '') + '>' + _escape(node.get('text', '')) + '</p>')
            elif kind == 'formula':
                parts.append(formula(node.get('latex', '0')))
            elif kind == 'table':
                parts.append(table(node['index'], node.get('title', True)))
        return ''.join(parts)

    style = r'''
:root{color-scheme:light}*{box-sizing:border-box}body{font:16px/1.48 "Segoe UI",Arial,sans-serif;color:#193442;background:#fff;max-width:1320px;margin:0 auto;padding:28px}h1{font-size:27px;line-height:1.25;margin:0 0 20px}h2{font-size:20px;line-height:1.35;margin:0 0 12px}h3{font-size:15px;line-height:1.4;margin:0 0 8px}p{margin:7px 0 10px}.section{margin:0 0 22px;min-width:0}.panel{min-width:0}.columns{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;align-items:start;margin-bottom:22px}.column-card{padding:14px;border:1px solid #d6e1e6;border-radius:6px;min-width:0}.column-card>.section{margin-bottom:0}.formula{max-width:100%;overflow-x:auto;margin:9px 0 12px;break-inside:avoid}.formula img{display:block;max-width:none;height:auto}.table-block{margin:10px 0 16px;min-width:0}.table-scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}th,td{border:1px solid #d6e1e6;padding:6px 8px;text-align:right;white-space:nowrap;vertical-align:top}th{background:#e6f0f2;font-weight:600;white-space:normal}tbody tr:nth-child(even){background:#f6f9fa}.text-cell{text-align:left;white-space:normal;overflow-wrap:anywhere}.used{background:#e1f0e9!important;font-weight:600;box-shadow:inset 0 0 0 1px #639880}.success{color:#235e44}.warning{color:#805518}.failed{color:#9a3131}.muted{color:#506875}.table-part{font-size:13px;margin-bottom:4px}details{margin:10px 0 14px;border:1px solid #d6e1e6;border-radius:5px}summary{cursor:pointer;padding:10px 12px;font-weight:600;background:#f6f9fa}.detail-body{padding:10px 12px 4px;min-width:0}.detail-body .columns{margin-bottom:12px}
@media(max-width:900px){body{padding:16px}.columns{grid-template-columns:minmax(0,1fr)}h1{font-size:23px}}
@page{size:A4;margin:14mm}
@media print{body{font-size:10.5pt;line-height:1.35;padding:0;margin:0;max-width:none}h1{font-size:18pt;margin-bottom:12px}h2{font-size:13pt;margin-bottom:8px}h3{font-size:10.5pt}h1,h2,h3,summary{break-after:avoid}p{orphans:2;widows:2;margin:5px 0 7px}.section{margin-bottom:14px}.columns{grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px;margin-bottom:14px}.columns.print-stack{display:block}.columns.print-stack>.column-card{margin-bottom:10px}.column-card{padding:8px;border-radius:0;break-inside:auto}.formula{overflow:visible;margin:6px 0 8px}.formula img{max-width:100%;height:auto}table{font-size:9pt}th,td{padding:4px 5px}thead{display:table-header-group}tr{break-inside:avoid}.table-scroll{overflow:visible}.table-block{margin:7px 0 11px;break-inside:auto}details{border:0;margin:8px 0 12px;break-inside:auto}details>summary{padding:6px 0;background:none}details:not([open])>.detail-body{display:block!important}details::details-content{content-visibility:visible!important;display:block!important}.detail-body{padding:4px 0 0}summary::marker{content:""}}
'''
    style += '\n.print-table{display:none}@media print{.screen-table{display:none}.print-table{display:block}.keep-together{break-inside:avoid}}\n'
    style += '''
@page{margin:12mm}
@media print{body{font-size:10pt;line-height:1.28}.section{margin-bottom:10px}
p{margin:4px 0 6px}.columns{gap:9px;margin-bottom:10px}.column-card{padding:6px}
.formula{margin:3px 0 5px}details{margin:6px 0 9px}details>summary{padding:4px 0}
.detail-body{padding-top:3px}.table-block{margin:6px 0 9px}}
'''
    script = '''
(()=>{let closed=[];addEventListener('beforeprint',()=>{closed=[...document.querySelectorAll('details:not([open])')];closed.forEach(item=>item.open=true)});addEventListener('afterprint',()=>{closed.forEach(item=>item.open=false);closed=[]})})();
'''
    layout = report.presentation.get('worked_layout') or report.presentation.get('inverse_layout') or _fallback_layout(report)
    content = ('<!doctype html><html lang="vi"><head><meta charset="utf-8">'
               '<meta name="viewport" content="width=device-width,initial-scale=1">'
               '<title>' + _escape(report.title) + '</title><style>' + style + '</style></head><body>'
               '<h1>' + _escape(report.title) + '</h1>' + render(layout)
               + '<script>' + script + '</script></body></html>')
    Path(path).write_text(content, encoding='utf-8')
