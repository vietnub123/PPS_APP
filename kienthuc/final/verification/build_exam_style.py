"""Sinh dàn ý 58 lựa chọn, HTML ngoại tuyến và workbook tiền xử lý.

Các bài mặc định là dữ liệu tự dựng của repo. Ca 7 mốc ghi riêng nguồn ảnh
người dùng; không gọi bảng 20251GKtest2 là bảng test1 của ảnh.
"""
from pathlib import Path
import html
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from pps.exam_style import outline
from pps.gui import TOOLS, fields, dispatch
from pps.math_view import export_html
from audit_latex import gui_cases
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.workbook.properties import CalcProperties

FINAL=Path(__file__).resolve().parents[1]


def tex(text):
    special={'\\':r'\textbackslash{}','_':r'\_','&':r'\&','%':r'\%','#':r'\#','$':r'\$',
             '{':r'\{','}':r'\}','^':r'\textasciicircum{}','~':r'\textasciitilde{}'}
    maths={'→':r'\to','−':'-','≤':r'\le','≥':r'\ge','≠':r'\ne','Σ':r'\sum',
           'Φ':r'\Phi','φ':r'\varphi','ε':r'\varepsilon','λ':r'\lambda','δ':r'\delta',
           'θ':r'\theta','π':r'\pi','τ':r'\tau','α':r'\alpha','β':r'\beta','γ':r'\gamma',
           '∂':r'\partial','′':r'\prime','″':r'\prime\prime','‴':r'\prime\prime\prime',
           '≈':r'\approx','ᵀ':r'{}^T','√':r'\sqrt{\vphantom{x}}'}
    result=''
    for ch in str(text):
        if ch in maths: result+=r'\ensuremath{'+maths[ch]+'}'
        elif ch in special: result+=special[ch]
        else: result+=ch
        if ch in ',;/=+(': result+=r'\allowbreak{}'
    return result


def build_catalog():
    lines=[r'\section{Dàn ý trình bày của đủ 58 lựa chọn}',
           'Các dàn ý sau lấy từ cùng danh mục mà GUI và HTML sử dụng. Đây là đường đi của bài giải; các bảng tổng quát, phép khử, công thức và ví dụ chi tiết vẫn được giữ trong các chương trước. Không thay lời giải số bằng một đoạn mã giả.',
           'Trong tool, nhóm Chi tiết có thể mở ra; bản HTML in ra mở toàn bộ chi tiết. Bản sao chép và các bảng xuất giữ mọi bước đã lưu.']
    count=0
    for tool,(methods,_) in TOOLS.items():
        lines.append(r'\subsection{'+tex(tool)+'}')
        for method in methods:
            count+=1
            recipe=outline(tool,method)
            lines.append(r'\examplebreak\subsubsection*{'+str(count)+'. '+tex(method)+'}')
            labels=[label for _,label,_,_ in fields(tool,method)]
            lines.append(r'\textbf{Input:} '+tex('; '.join(labels))+'.')
            if TOOLS[tool][1] and method not in ('Horner','Chebyshev'):
                lines.append('Bảng cặp $x,y$ là đầu vào riêng của lượt chạy; giữ ánh xạ nguồn nếu chọn một phần bảng.')
            lines.append(r'\begin{enumerate}')
            lines.extend(r'\item '+tex(step) for step in recipe['steps'])
            lines.append(r'\end{enumerate}')
            lines.append(r'\textbf{Output:} '+tex(recipe['output']))
    assert count==58
    (FINAL/'verification/outline58.tex').write_text('\n\n'.join(lines)+'\n',encoding='utf-8')


def build_workbook():
    book=Workbook();book.remove(book.active)
    book.calculation=CalcProperties(calcId=191029,fullCalcOnLoad=True,forceFullCalc=True)
    ws=book.create_sheet('Doc_truoc')
    for row in [
        ['TIỀN XỬ LÝ PPS — DỮ LIỆU TỰ DỰNG, KHÔNG PHẢI ĐỀ TEST1'],
        ['Đọc Tien_xu_ly_Excel.pdf trước khi dùng. Công thức tính lại khi mở bằng Excel.'],
        ['Du_lieu_goc: giữ ID và cặp x,y. Không sửa sheet này khi chọn biến đổi.'],
        ['Tinh_tien: nhập c,s,d,r tại J2:J5; đổi cả điểm và mức mục tiêu.'],
        ['Kiem_tra_moc: kiểm tra số, mốc trùng, bước và khoảng đổi dấu quanh J3.'],
        ['Log_cung_dau: y<0; các dòng sai miền hiện #N/A, không tự bị loại.'],
        ['Mau_lan_dau: có một y>0 để thấy cảnh báo; không dùng ABS để che khác dấu.'],
        ['Bang_tong: cơ sở 1,x,1/x trên đúng dữ liệu âm của sheet Log_cung_dau.'],
        ['Nhập tool bằng Nhap_tool_goc / Nhap_tool_doi / Nhap_tool_log_goc: đúng hai cột đầu x,y; không đưa cột ID thành x.'],
        ['Giữ đủ chữ số; ID là cột theo dõi, không nhập thành x. Tool đọc hai cột đầu của sheet nhập là x,y.'],
        ['Tịnh tiến y làm thay đổi họ hàm mũ/lũy thừa nói chung; luôn khôi phục mô hình gốc.'],
    ]:ws.append(row)
    ws.column_dimensions['A'].width=118
    original=[(0,1000,5),(1,1002,9),(2,1004,17),(3,1006,29),(4,1008,45)]
    ws=book.create_sheet('Du_lieu_goc');ws.append(['ID','x gốc','y gốc'])
    for row in original:ws.append(row)
    ws=book.create_sheet('Tinh_tien')
    ws.append(['ID','x gốc','y gốc','u=(x-c)/s','v=(y-d)/r','x khôi phục','y khôi phục',None,'tham số','giá trị'])
    for i in range(2,7):
        ws.append([f'=Du_lieu_goc!A{i}',f'=Du_lieu_goc!B{i}',f'=Du_lieu_goc!C{i}',
                   f'=(B{i}-$J$2)/$J$3',f'=(C{i}-$J$4)/$J$5',f'=$J$2+$J$3*D{i}',f'=$J$4+$J$5*E{i}'])
    for row, (name,value) in enumerate([('c',1000),('s',2),('d',5),('r',4),('x đích',1003),('y mức',12.5)],2):
        ws.cell(row,9,name);ws.cell(row,10,value)
    ws.cell(8,9,'u đích');ws.cell(8,10,'=(J6-J2)/J3')
    ws.cell(9,9,'v mức');ws.cell(9,10,'=(J7-J4)/J5')
    ws.cell(11,9,'V tự dựng');ws.cell(11,10,1.875)
    ws.cell(12,9,'y về gốc');ws.cell(12,10,'=J4+J5*J11')
    ws.cell(13,9,'V đạo hàm');ws.cell(13,10,2)
    ws.cell(14,9,'y đạo hàm');ws.cell(14,10,'=J5/J3*J13')
    ws=book.create_sheet('Kiem_tra_moc')
    ws.append(['ID','x','y','hai ô số','x bị trùng','h kế tiếp','lưới đều','đổi dấu mức', 'tham số','giá trị'])
    for i in range(2,7):
        ws.append([f'=Du_lieu_goc!A{i}',f'=Du_lieu_goc!B{i}',f'=Du_lieu_goc!C{i}',
                   f'=AND(ISNUMBER(B{i}),ISNUMBER(C{i}))',f'=COUNTIF($B$2:$B$6,B{i})>1',
                   f'=B{i+1}-B{i}' if i<6 else None,
                   f'=ABS(F{i}-$J$2)<=1E-8*ABS($J$2)' if i<6 else None,
                   f'=(C{i}-$J$3)*(C{i+1}-$J$3)<0' if i<6 else None])
    ws.cell(2,9,'h');ws.cell(2,10,2);ws.cell(3,9,'y mức');ws.cell(3,10,12.5)
    for name,mixed in [('Log_cung_dau',False),('Mau_lan_dau',True)]:
        ws=book.create_sheet(name)
        ws.append(['ID','x','y','z=ln(-y), chỉ khi y<0','hợp lệ theo nhánh âm'])
        for row,(x,y) in enumerate([(1,-2),(2,-1.4),(3,-.9),(4,-.5),(5,-.3)],2):
            ws.append([row-2,x,.1 if mixed and row==6 else y,f'=IF(C{row}<0,LN(-C{row}),NA())',f'=AND(B{row}<>0,C{row}<0)'])
        ws.cell(8,2,'Số y âm');ws.cell(8,3,'=COUNTIF(C2:C6,"<0")')
        ws.cell(9,2,'Số y dương');ws.cell(9,3,'=COUNTIF(C2:C6,">0")')
        ws.cell(10,2,'Số y bằng 0');ws.cell(10,3,'=COUNTIF(C2:C6,"=0")')
    ws=book.create_sheet('Bang_tong')
    ws.append(['ID','x','y','Z=ln(-y)','x^2','1/x','1/x^2','xZ','Z/x'])
    for i in range(2,7):
        ws.append([f'=Log_cung_dau!A{i}',f'=Log_cung_dau!B{i}',f'=Log_cung_dau!C{i}',f'=Log_cung_dau!D{i}',
                   f'=B{i}^2',f'=1/B{i}',f'=1/B{i}^2',f'=B{i}*D{i}',f'=D{i}/B{i}'])
    ws.cell(8,1,'Tổng')
    for col in ['B','D','E','F','G','H','I']:ws[f'{col}8']=f'=SUM({col}2:{col}6)'
    ws['A10']='N';ws['B10']='=COUNT(B2:B6)'
    ws['A12']='Hệ chuẩn: 3 cột đầu là ma trận, cột cuối là vế phải'
    for i,row in enumerate([['=B10','=B8','=F8','=D8'],['=B8','=E8','=B10','=H8'],['=F8','=B10','=G8','=I8']],13):
        for j,value in enumerate(row,2):ws.cell(i,j,value)
    for sheet,source,xcol,ycol in [('Nhap_tool_goc','Du_lieu_goc','B','C'),
                                  ('Nhap_tool_doi','Tinh_tien','D','E'),
                                  ('Nhap_tool_log_goc','Log_cung_dau','B','C')]:
        ws=book.create_sheet(sheet);ws.append(['x','y'])
        for i in range(2,7):ws.append([f'={source}!{xcol}{i}',f'={source}!{ycol}{i}'])
    for ws in book:
        ws.freeze_panes='B2'
        for cell in ws[1]:cell.font=Font(name='Arial',bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='244C5A')
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.font=Font(name='Arial',size=11,color='135D84' if cell.data_type=='f' else '17232B')
                cell.alignment=Alignment(vertical='top',wrap_text=True)
                if cell.data_type=='f':cell.number_format='0.0000000000'
        if ws.title!='Doc_truoc':
            for col in range(1,ws.max_column+1):ws.column_dimensions[ws.cell(1,col).column_letter].width=24 if col>1 else 12
        ws.sheet_view.showGridLines=False
        ws.print_options.horizontalCentered=True
        ws.sheet_properties.pageSetUpPr.fitToPage=True
        ws.page_setup.orientation='landscape';ws.page_setup.paperSize=ws.PAPERSIZE_A4
        ws.page_setup.fitToWidth=1;ws.page_setup.fitToHeight=0
        ws.print_title_rows='1:1'
    book.save(FINAL/'Tien_xu_ly_Excel.xlsx')


def build_html():
    target=FINAL/'examples/presentation';target.mkdir(exist_ok=True)
    links=[]
    for i,(title,tool,method,values,x,y) in enumerate(list(gui_cases())[:58],1):
        r=dispatch(tool,method,values,x,y)
        export_html(r,target/f'{i:02}.html')
        links.append((f'{i:02}.html',title+' — dữ liệu tự dựng'))
    sample={'tool':'Nội suy đa thức','method':'Stirling',
            'values':{'target':'4.15','order':'1','count':'7'},
            'x':'3.760 3.875 3.990 4.105 4.220 4.335 4.450',
            'y':'-0.9384 -0.8979 -0.8110 -0.8056 -0.7548 -0.7416 -0.7049'}
    (target/'Stirling_7_tu_anh.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    r=dispatch(sample['tool'],sample['method'],sample['values'],sample['x'],sample['y'])
    export_html(r,target/'Stirling_7_tu_anh.html')
    (target/'Stirling_7_tu_anh.txt').write_text(r.text(),encoding='utf-8')
    links.insert(0,('Stirling_7_tu_anh.html','Đối chiếu đúng 7 mốc trên ảnh người dùng — P(4.15)=-0.7912276'))
    content='<!doctype html><html lang="vi"><meta charset="utf-8"><title>Lời giải theo mẫu</title><style>body{max-width:1000px;margin:30px auto;font:18px/1.6 "Times New Roman"}a{color:#14576b}li{margin:8px 0}</style><h1>Lời giải theo mẫu — đủ 58 lựa chọn</h1><p>Mỗi tệp mở ngoại tuyến. Mở Chi tiết để đọc mọi bước; khi in, các chi tiết được mở đầy đủ. Các ví dụ 01–58 là ví dụ tự dựng, không phải toàn bộ dữ liệu test1 của ảnh.</p><ul>'
    content+=''.join('<li><a href="'+html.escape(path)+'">'+html.escape(title)+'</a></li>' for path,title in links)
    content+='</ul></html>'
    (target/'index.html').write_text(content,encoding='utf-8')
    print('Generated 58 method HTMLs, image case, outline58.tex and Excel workbook.')


if __name__=='__main__':
    build_catalog();build_workbook();build_html()
