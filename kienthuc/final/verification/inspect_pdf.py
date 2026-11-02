"""Đọc PDF đã biên dịch: trang, bookmark, ký tự lỗi, biên trang và ảnh để soát."""
from pathlib import Path
import json
import unicodedata
import pdfplumber
import pypdfium2 as pdfium

FINAL=Path(__file__).resolve().parents[1]
PDF=FINAL/'So_tay_PPS.pdf'
BUILD=FINAL/'build'
BUILD.mkdir(exist_ok=True)
needles={'horner':'Mẫu bảng ngang tổng quát','inverse':'Bảng đủ các vòng','spline':'Mười phương trình',
    'least_squares':'Hàng i là khuôn','power_model':'Lũy thừa: Ax mũ b',
    'rational_model':'trả lại đúng thứ tự a,b','raw_lm':'một vòng nhận gì',
    'cubic_template':'Khuôn bảng cubic','integration':'Vector nguyên','ode':'Ví dụ Adams 4',
    'bvp':'Ví dụ Robin','exam':'Tìm mọi nghiệm',
    'gauss_restored':'toàn bộ phép khử và thế ngược',
    'qr_restored':'QR: hai lượt trực giao hóa',
    'svd_restored':'SVD: ngưỡng hạng','image_case':'0.791227553804'}
with pdfplumber.open(PDF) as doc:
    texts=[unicodedata.normalize('NFC',p.extract_text() or '') for p in doc.pages]
    compact=lambda t:''.join(t.split())
    hits={k:next((i for i,t in enumerate(texts) if compact(v) in compact(t)),None) for k,v in needles.items()}
    # Khi một tiêu đề có trong mục lục, dùng trang nội dung cuối cùng tìm thấy.
    for k,v in needles.items():
        matches=[i for i,t in enumerate(texts) if compact(v) in compact(t)]
        if matches:hits[k]=matches[-1]
    details={'pages':len(doc.pages),'bookmarks':len(list(doc.doc.get_outlines())),
        'review_pages_zero_based':hits,'replacement_chars':sum(t.count('\ufffd') for t in texts),
        'over_page_words':[]}
    for i,page in enumerate(doc.pages):
        bad=[w['text'] for w in page.extract_words() if w['x0']<0 or w['x1']>page.width+1]
        if bad:details['over_page_words'].append({'page':i+1,'words':bad})
    (BUILD/'pdf_text.txt').write_text('\n\n'.join(texts),encoding='utf-8')
pdf=pdfium.PdfDocument(PDF)
for label,i in {'cover':0,'toc':1,**hits}.items():
    if i is not None:pdf[i].render(scale=1.4).to_pil().save(BUILD/('review_'+label+'.png'))
assert details['replacement_chars']==0 and not details['over_page_words'], details
assert all(i is not None for i in hits.values()), hits
with pdfplumber.open(FINAL/'Tien_xu_ly_Excel.pdf') as excel:
    text='\n'.join(unicodedata.normalize('NFC',page.extract_text() or '') for page in excel.pages)
    outside=[{'page':i+1,'word':word['text']} for i,page in enumerate(excel.pages) for word in page.extract_words()
             if word['x0']<0 or word['x1']>page.width+1]
    assert '\ufffd' not in text and not outside
    for phrase in ('SUMSQ','Nhap_tool_doi','102'):
        assert phrase in ''.join(text.split()),phrase
    details['preprocessing_pdf']={'pages':len(excel.pages),'replacement_chars':text.count('\ufffd'),
                                  'over_page_words':outside,'formula_and_input_sheet_names_found':True}
excel=pdfium.PdfDocument(FINAL/'Tien_xu_ly_Excel.pdf')
excel[0].render(scale=1.4).to_pil().save(BUILD/'review_preprocessing_cover.png')
excel[2].render(scale=1.4).to_pil().save(BUILD/'review_preprocessing_transform.png')
(FINAL/'verification'/'pdf_inspection.json').write_text(json.dumps(details,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(details,ensure_ascii=False,indent=2))
