"""Đối chiếu số/trạng thái và workbook của bản trình bày theo mẫu.

Có thể thêm --baseline tmp/presentation_baseline.json để đối chiếu ảnh
chụp số liệu trước đợt sửa; không cần baseline để kiểm adapter trình bày.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from openpyxl import load_workbook

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from pps.gui import dispatch, _dispatch
from audit_latex import gui_cases

OUT=Path(__file__).resolve().parent


def clean(value):
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,(tuple,list)):return [clean(v) for v in value]
    if isinstance(value,dict):return {str(k):clean(v) for k,v in value.items() if not callable(v)}
    if isinstance(value,np.generic):return value.item()
    if callable(value):
        try:return clean(value(np.array([.25,.75,1.5])))
        except (ValueError,ArithmeticError):return 'callable'
    if value is None or isinstance(value,(str,int,float,bool)):return value
    return str(value)


def numeric(report,title):
    return {'title':title,'value':clean(report.value),
            'worked':clean(report.presentation.get('worked_solution',report.presentation.get('inverse_solution',{})))}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path)
    args=parser.parse_args()
    baseline=json.loads(args.baseline.read_text(encoding='utf-8')) if args.baseline else None
    result={'cases':[],'baseline_sha256':hashlib.sha256(args.baseline.read_bytes()).hexdigest() if baseline else None}
    for i,(title,tool,method,values,x,y) in enumerate(list(gui_cases())[:58]):
        report=dispatch(tool,method,values,x,y);core=_dispatch(tool,method,values,x,y)
        snapshot=numeric(report,title)
        assert snapshot==numeric(core,title),title
        assert clean(report.tables)==clean(core.tables),title
        if baseline:assert snapshot==baseline[i],title
        assert report.presentation['exam_style']['method']==method
        result['cases'].append({'title':title,'numeric_state_unchanged':True,'baseline_matched':True if baseline else None})
    workbook=load_workbook(OUT.parent/'Tien_xu_ly_Excel.xlsx',data_only=False)
    assert workbook.calculation.fullCalcOnLoad
    assert workbook['Tinh_tien']['D2'].value=='=(B2-$J$2)/$J$3'
    assert workbook['Tinh_tien']['J14'].value=='=J5/J3*J13'
    assert workbook['Mau_lan_dau']['C6'].value>0
    assert workbook['Mau_lan_dau']['D6'].value=='=IF(C6<0,LN(-C6),NA())'
    for sheet in ('Nhap_tool_goc','Nhap_tool_doi','Nhap_tool_log_goc'):
        assert [c.value for c in workbook[sheet][1]]==['x','y']
    result['workbook']={'sheets':len(workbook.sheetnames),'formulas':sum(c.data_type=='f' for sheet in workbook for row in sheet for c in row),
                        'excel_recalculation_required':True,'input_sheets_two_columns':True}
    workbook.close()
    result['source_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [ROOT/'pps/exam_style.py',ROOT/'pps/polynomial_worked.py',ROOT/'pps/least_squares_worked.py',
                  ROOT/'pps/calculus.py',ROOT/'pps/differential.py',OUT.parent/'Tien_xu_ly_Excel.tex']}
    (OUT/'exam_style_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS:',len(result['cases']),'methods; numeric states and tables unchanged by adapter; workbook',result['workbook'])


if __name__=='__main__':main()
