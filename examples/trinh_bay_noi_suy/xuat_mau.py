"""Xuất nguyên báo cáo của app; không tính/thêm bảng lời giải riêng."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))

from pps.gui import dispatch
from pps.math_view import export_html


def main():
    folder=Path(__file__).resolve().parent
    for path in sorted(folder.glob('[0-9][0-9]_*.json')):
        task=json.loads(path.read_text(encoding='utf-8'))
        report=dispatch(task['tool'],task['method'],task['values'],task.get('x',''),task.get('y',''))
        export_html(report,path.with_suffix('.html'))
        path.with_suffix('.txt').write_text(report.text(),encoding='utf-8')
        print(path.stem,report.presentation['worked_solution']['status'])


if __name__=='__main__':main()
