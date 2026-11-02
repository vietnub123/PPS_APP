# Sổ tay thuật toán PPS

**Chưa biết bắt đầu từ file nào? Đọc [Lộ trình giải bài](LO_TRINH_GIAI_BAI.md): mỗi bước phân tích, chọn phương pháp, viết thuật toán, nhập JSON và diễn giải kết quả dùng đúng tài liệu nào.**

Mở **[So_tay_PPS.pdf](So_tay_PPS.pdf)** để đọc và in. Bản theo mẫu bài thi có **141 trang, 118 bookmark**, mục lục bấm được, công thức và bảng được dàn trang bằng LaTeX.

**Mở trước:** [thư viện 58 bài HTML ngoại tuyến](examples/presentation/index.html), [bài Stirling đúng 7 mốc trên ảnh](examples/presentation/Stirling_7_tu_anh.html), [những khác biệt với mẫu](Doi_chieu_mau_20251.md). Phụ lục C giải thích trật tự trình bày, kiểm tra hệ chuẩn 102 điểm từ các tổng trên ảnh và giải đầy đủ ví dụ Stirling. Giá trị hàm đúng là **−0.791227553804**; giá trị −0.791128 trên ảnh thiếu đóng góp của các hạng cao.

**Tiền xử lý tách riêng:** [hướng dẫn Excel PDF](Tien_xu_ly_Excel.pdf), [nguồn TeX](Tien_xu_ly_Excel.tex), [workbook công thức](Tien_xu_ly_Excel.xlsx). Có đổi gốc/đơn vị, đổi mục tiêu, đạo hàm/biên/tích phân, kiểm tra mốc và dấu, chọn nhánh, lập tổng; chỉ rõ phép đổi nào làm thay họ mô hình. Các sheet `Nhap_tool_*` giữ đúng hai cột đầu x,y. Mở workbook bằng Excel để tính lại công thức trước khi nhập vào app.

Đọc **phần Input → quá trình → output ở đầu mỗi chương** trước, rồi mới đọc phần giải thích và ví dụ số. Tên ô nhập lấy trực tiếp từ GUI; bảng mẫu có hàng đầu, hàng tổng quát thứ i, hàng cuối và các tổng cần chuyển sang bước sau. Công thức tổng/tích có dạng khai triển. Bảng Horner nằm ngang, phân biệt hàng hệ số, hàng nhân, hàng cộng và số dư.

**Chương 4 được viết lại theo từng loại mô hình bình phương tối thiểu**: dữ liệu/miền áp dụng, cơ sở cần nhập, phép đổi biến, bảng tổng quát, hệ cần lập, khôi phục tham số và đọc sai số. Hai nhánh SSE thang y có bảng Jacobian và chu trình LM riêng. **Giữ đầy đủ phần Gauss/QR/SVD**: lập hệ chuẩn, khử và thế ngược, hai lượt trực giao hóa QR, SVD, ngưỡng hạng, nghiệm chuẩn nhỏ nhất và các ví dụ số.

Tài liệu có 7 chương chính và ba phụ lục API/đề thi/trình bày theo mẫu. Các ví dụ 20241/20251 vẫn ghi rõ nguồn và mô hình được dùng. Phần Gauss/QR/SVD giữ đầy đủ. Tool hiện lưu các tầng RK thực tính và dự báo–hiệu chỉnh Adams; số đánh giá của bộ giải ẩn được ghi riêng, không gọi là số vòng Newton.

## Chỉnh sửa

- **[So_tay_PPS.tex](So_tay_PPS.tex)**: trang bìa, mục lục, font, bố cục và thứ tự chương.
- **[chapters/](chapters/)**: sửa trực tiếp nội dung từng chương bằng UTF-8; không cần sửa PDF bằng tay.
- **[chapters/toolflow_01.tex](chapters/toolflow_01.tex)** đến `toolflow_07.tex`: phần khuôn làm chung mới ở đầu các chương; bình phương tối thiểu viết trực tiếp trong **[04_binh_phuong_toi_thieu.tex](chapters/04_binh_phuong_toi_thieu.tex)**.
- **[04a_Gauss_QR_SVD.tex](chapters/04a_Gauss_QR_SVD.tex)**: phần giải thích và ví dụ Gauss, QR, SVD được giữ trong Chương 4. Phụ lục A cũng giữ phần khử Gauss của API.
- **[verification/coverage.csv](verification/coverage.csv)**: đối chiếu 58 lựa chọn GUI với chương tương ứng.
- **[Kiem_tra_va_nguon.md](Kiem_tra_va_nguon.md)**: nguồn, kiểm tra và các giới hạn cần biết.

Biên dịch lại trên Windows với XeLaTeX/MiKTeX, font Times New Roman, Arial và Consolas:

```powershell
& .\kienthuc\final\Build_pdf.ps1
```

Script chạy ba lượt cho mỗi tài liệu `So_tay_PPS` và `Tien_xu_ly_Excel`, ghi log trong `build/`, dừng nếu có lỗi hoặc tràn nội dung, rồi cập nhật cả hai PDF tại đây. Nó tắt tự cài gói; máy cần có sẵn `fontspec`, `amsmath`, `amssymb`, `array`, `longtable`, `booktabs`, `graphicx`, `xcolor`, `geometry`, `fancyhdr`, `hyperref`. Chạy `verification/build_exam_style.py` trước khi biên dịch nếu vừa sửa danh mục dàn ý dùng chung.

## Mở ví dụ trong app

Trong GUI chọn **Mở bài**, mở một JSON tại **[examples/](examples/)** rồi bấm **Tính kết quả**. Có tám bài nhỏ, từ Horner đến trị riêng; TXT đi kèm lưu kết quả chạy thực tế. Hai HTML minh họa Horner và QR có trọng số đọc được ngoại tuyến.

Các đề thật vẫn dùng tệp gốc ở `examples/de_20241` và `examples/de_20251`; sổ tay ghi rõ câu nào là đề thật và câu nào tự đặt trên dữ liệu thật.

## Chạy lại kiểm tra

Từ thư mục gốc repo:

```powershell
.venv\Scripts\python.exe kienthuc/final/verification/build_tool_manual.py
.venv\Scripts\python.exe kienthuc/final/verification/check_tool_manual.py
.venv\Scripts\python.exe kienthuc/final/verification/manual_examples.py
.venv\Scripts\python.exe kienthuc/final/verification/spline_ls_examples.py
.venv\Scripts\python.exe kienthuc/final/verification/calculus_verification.py
.venv\Scripts\python.exe kienthuc/final/verification/audit_latex.py
.venv\Scripts\python.exe kienthuc/final/verification/build_exam_style.py
.venv\Scripts\python.exe kienthuc/final/verification/verify_exam_style.py
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Các script chỉ dùng thư viện và dữ liệu repo, xuất kết quả vào thư mục này. Khi sửa thuật toán phải đối chiếu lại nội dung và sinh lại PDF. Đạt kiểm thử không có nghĩa mọi dữ liệu tùy ý đều có nghiệm duy nhất hoặc mọi phép lặp đều hội tụ.

Kết quả đợt trình bày theo mẫu: [đối chiếu 58 đường tính và workbook](verification/exam_style_verification.json), [234 test repo](verification/test_summary.json), [9 test GUI với Tk thật](verification/gui_exam_style_summary.json). Trong sandbox, lớp GUI bị bỏ qua vì không nạp được Tcl/Tk; đã chạy riêng và đạt cả 9 test ngoài sandbox. Kiểm thử CSV/Excel kiểm đúng nội dung và số bảng thực xuất thay cho kỳ vọng cũ cố định hai sheet.

`build_tool_manual.py` mặc định chỉ cập nhật bảng ô nhập từ GUI trong `verification/inputs_*.tex`, giữ nguyên chương bình phương tối thiểu để có thể sửa trực tiếp. Chỉ dùng cờ `--write-ls` khi chủ động muốn sinh lại chương đó từ mẫu trong script; cờ này ghi đè các chỉnh sửa tay của chương 4.
