# Sổ tay thuật toán PPS

Mở **[So_tay_PPS.pdf](So_tay_PPS.pdf)** để đọc và in. Bản viết lại có **105 trang, 107 bookmark**, mục lục bấm được, công thức và bảng được dàn trang bằng LaTeX.

Đọc **phần Input → quá trình → output ở đầu mỗi chương** trước, rồi mới đọc phần giải thích và ví dụ số. Tên ô nhập lấy trực tiếp từ GUI; bảng mẫu có hàng đầu, hàng tổng quát thứ i, hàng cuối và các tổng cần chuyển sang bước sau. Công thức tổng/tích có dạng khai triển. Bảng Horner nằm ngang, phân biệt hàng hệ số, hàng nhân, hàng cộng và số dư.

**Chương 4 được viết lại theo từng loại mô hình bình phương tối thiểu**: dữ liệu/miền áp dụng, cơ sở cần nhập, phép đổi biến, bảng tổng quát, hệ cần lập, khôi phục tham số và đọc sai số. Hai nhánh SSE thang y có bảng Jacobian và chu trình LM riêng. Phần giải thích thuật toán Gauss/QR/SVD đã được bỏ khỏi chương này.

Tài liệu có 7 chương chính và hai phụ lục API/đề thi. Các ví dụ 20241/20251 vẫn ghi rõ nguồn và mô hình được dùng.

## Chỉnh sửa

- **[So_tay_PPS.tex](So_tay_PPS.tex)**: trang bìa, mục lục, font, bố cục và thứ tự chương.
- **[chapters/](chapters/)**: sửa trực tiếp nội dung từng chương bằng UTF-8; không cần sửa PDF bằng tay.
- **[chapters/toolflow_01.tex](chapters/toolflow_01.tex)** đến `toolflow_07.tex`: phần khuôn làm chung mới ở đầu các chương; bình phương tối thiểu viết trực tiếp trong **[04_binh_phuong_toi_thieu.tex](chapters/04_binh_phuong_toi_thieu.tex)**.
- **[verification/coverage.csv](verification/coverage.csv)**: đối chiếu 58 lựa chọn GUI với chương tương ứng.
- **[Kiem_tra_va_nguon.md](Kiem_tra_va_nguon.md)**: nguồn, kiểm tra và các giới hạn cần biết.

Biên dịch lại trên Windows với XeLaTeX/MiKTeX, font Times New Roman, Arial và Consolas:

```powershell
& .\kienthuc\final\Build_pdf.ps1
```

Script chạy ba lượt để cập nhật mục lục/tham chiếu, ghi log trong `build/`, dừng nếu có lỗi hoặc tràn nội dung, rồi cập nhật PDF tại đây. Nó tắt tự cài gói; máy cần có sẵn `fontspec`, `amsmath`, `amssymb`, `array`, `longtable`, `booktabs`, `graphicx`, `xcolor`, `geometry`, `fancyhdr`, `hyperref`. Có thể chạy trực tiếp ba lượt `xelatex --disable-installer -output-directory=build So_tay_PPS.tex` từ thư mục này.

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
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Các script chỉ dùng thư viện và dữ liệu repo, xuất kết quả vào thư mục này. Khi sửa thuật toán phải đối chiếu lại nội dung và sinh lại PDF. Đạt kiểm thử không có nghĩa mọi dữ liệu tùy ý đều có nghiệm duy nhất hoặc mọi phép lặp đều hội tụ.

`build_tool_manual.py` mặc định chỉ cập nhật bảng ô nhập từ GUI trong `verification/inputs_*.tex`, giữ nguyên chương bình phương tối thiểu để có thể sửa trực tiếp. Chỉ dùng cờ `--write-ls` khi chủ động muốn sinh lại chương đó từ mẫu trong script; cờ này ghi đè các chỉnh sửa tay của chương 4.
