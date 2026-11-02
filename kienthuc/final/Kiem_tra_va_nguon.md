# Nguồn và kiểm tra bản sổ tay

Đối chiếu ngày 02/11/2026. Bản đọc: [So_tay_PPS.pdf](So_tay_PPS.pdf). Bản sửa trực tiếp: [So_tay_PPS.tex](So_tay_PPS.tex) và [chapters/](chapters/).

## Phạm vi và nguồn

Sổ tay ánh xạ đủ **58 lựa chọn phương pháp trong 9 nhóm GUI**, kể cả các nhánh Newton, biên spline, các bộ giải hồi quy, RK tham số và Adams. Xem [coverage.csv](verification/coverage.csv). Các hàm chỉ có qua Python được mô tả riêng ở Phụ lục A.

Nguồn quyết định hành vi thực tế là `pps/gui.py` cùng các mô-đun tính toán, mô hình và trình bày trong `pps/`. Các tài liệu nội bộ dùng để đối chiếu thuật ngữ, công thức và cách trình bày gồm:

- [Chương 1 hiệu chỉnh](../real/MI3042_Chuong1_Hieu_chinh_va_bo_sung_ma_gia.pdf).
- [Lý thuyết nội suy ngược](<../real/Noi_suy_nguoc_Ly_thuyet_Thuat_toan_Bai_mau (1).pdf>) và [guide triển khai](<../real/Noi_suy_nguoc_Guide_trien_khai_va_hien_thi (2).md>).
- [Spline](../real/03Spline_Phuong_phap_luan_Thuat_toan_Bai_mau.pdf) và [bình phương tối thiểu](../real/03Binh_phuong_toi_thieu_Phuong_phap_luan_Thuat_toan_Bai_mau.pdf).
- Các đặc tả `00_Dac_ta...`, `01_Noi_suy...`, `02_Dao_ham...`, `03_Horner...` trong `kienthuc/real`.
- Ảnh đề, workbook `20241GKtest2.xlsx`, `20251GKtest2.xlsx`; đầu vào và nhật ký ở `examples/de_20241`, `examples/de_20251`; `Kiem_dinh_de_20251.md`.

Không dùng lời giải trên mạng. Các bảng tầng RK hoặc phép giải tay BVP/trị riêng được ghi là phép tính từ công thức và kiểm kết quả với app. Không nhận chúng là log nội bộ của SciPy/LAPACK. Hash SHA-256 của mã, chương, script và tài liệu nguồn được lưu trong [source_sha256.json](verification/source_sha256.json).

## Kết quả kiểm tra

Bản viết lại tổ chức nội dung theo **input cụ thể → bảng/quá trình tổng quát → output**. Tên trường được lấy lại từ `pps/gui.py`; chương bình phương tối thiểu tách từng mô hình và bỏ phần giảng Gauss/QR/SVD. Thay đổi trong đợt này là nội dung và công cụ kiểm tra tài liệu.

| Kiểm tra | Kết quả và dữ liệu đối chiếu |
|---|---|
| Biểu mẫu và hệ trong bản viết lại | **58 biểu mẫu GUI**, kiểm các trường nhập; **8 hệ hai tham số sau biến đổi** so với bộ khớp thực tế có trọng số; **2 Jacobian SSE gốc** kiểm qua hiệu đối xứng. [Script](verification/check_tool_manual.py), [kết quả](verification/tool_manual_check.json). |
| Chương 01, 02, 07, helper và đề thật | **43 phép đối chiếu số/lịch sử** qua [manual_examples.py](verification/manual_examples.py); có đủ 3 vòng tiến, 5 vòng lùi, 5 lần chia đôi; chạy lại 4 nhánh đề 20241 và Stirling/Bessel đề 20251. [Kết quả](verification/manual_examples.json). |
| Spline và bình phương tối thiểu | **16 bài spline, 15 bài hồi quy**; biên trái/phải/trộn/tổ hợp, lưới không đều, các biến đổi, QR/Gauss/SVD và các bước LM. [Script](verification/spline_ls_examples.py), [dữ liệu trung gian](verification/spline_ls_examples.json). |
| Giải tích số và ODE | Kiểm trọng số Newton–Cotes 1–10 bằng hệ moment hữu tỷ; đạo hàm, quadrature, các RK, Adams 2–5, BVP/Robin và giảm lưới trị riêng. [Script](verification/calculus_verification.py), [kết quả](verification/calculus_examples.json). |
| Công thức thật sinh từ tool | **78 trường hợp, 1.354 lượt công thức, 360 công thức khác nhau; 0 lỗi phân tích cú pháp hoặc cảnh báo thiếu glyph** ở bộ kiểm đã chạy. [Audit](verification/latex_audit.json), [script](verification/audit_latex.py). |
| Kiểm thử hồi quy repo trước đợt viết lại hướng dẫn | `Ran 223 tests`; kết quả `OK (skipped=1)`. Nhóm `test_gui.GuiTests` bị bỏ qua do môi trường không có Tcl/Tk dùng được. Các test số học, xuất báo cáo và ba test xử lý cuộn Combobox chạy được. [Log](verification/test_suite.txt), [tóm tắt có cấu trúc](verification/test_summary.json). |
| PDF viết lại | **105 trang, 107 bookmark**; mục lục/tham chiếu biên dịch ba lượt. Log cuối không có lỗi, tham chiếu chưa xác định, thiếu ký tự hay hộp tràn. Kiểm biên trang toàn PDF; xem trực tiếp các trang bảng tổng quát Horner, BPTT, lũy thừa, phân thức, LM, spline, tích phân, ODE và đề thật. [Kết quả kiểm PDF](verification/pdf_inspection.json). |

Script [run_regression.py](verification/run_regression.py) ghi log UTF-8 và trả mã thoát từ kết quả unittest. Cách này tránh PowerShell cũ biến dòng tiến độ ghi ra stderr thành `NativeCommandError`; dòng tiến độ đó tự nó không phải lỗi thuật toán.

## Những gì đã sửa trong phần công thức của app

1. `pps/math_view.py`: chuyển literal số khoa học, chẳng hạn `5e-101`, thành ký pháp toán `5\cdot 10^{-101}` trước khi MathText vẽ. Chuỗi cũ vẫn có thể parse nhưng hiển thị chữ `e` như một biến, nên chỉ kiểm parse chưa đủ. Giữ nguyên các biểu thức như `e^{3x}` và tên có chứa `e`.
2. `pps/least_squares_worked.py`: ghi rõ bài toán `Phi c ≈ z` và mục tiêu bình phương có trọng số; với QR, định nghĩa cả `B = sqrt(W/w_max) Phi` **và** `z̃ = sqrt(W/w_max) z`. Hệ tam giác thực tế là `R c = Qᵀ z̃`; hệ chuẩn vẫn được trình bày đúng vai trò.
3. Bổ sung kiểm thử cho ký pháp số khoa học và đối chiếu vế phải QR có trọng số. Các phép tính số của bộ giải không bị thay bởi hai sửa đổi trình bày này.

## Giới hạn được ghi thẳng trong sổ tay

- Nội suy bậc cao và ngoại suy có thể nhạy số; đủ mốc không bảo đảm một phép lặp hội tụ. Hai ca toàn bộ 104 mốc thất bại được giữ nguyên trạng thái, không được thay lén bằng bài cục bộ thành công.
- Phân biệt nghiệm của đa thức thuận với giá trị đa thức nội suy hàm ngược; phân biệt cận nghiệm mô hình với sai số so với hàm thật.
- Spline bậc 4 đầu phải/trộn có thể nhập qua **Biên tổng quát**. Nhánh này hiện dùng Gauss trên hệ hệ số; lựa chọn Thomas ở nhánh đó bị bỏ qua trong mã hiện tại. Sổ tay công khai giới hạn này; đợt viết tài liệu không thay thuật toán để che sự khác biệt.
- QR/SVD và giải hệ chuẩn cùng giải bài hồi quy tuyến tính nhưng đi qua các phép toán khác nhau. Tuyến tính hóa log tối ưu thang biến đổi; LM tối ưu SSE thang y và không chứng nhận cực tiểu toàn cục.
- ODE/BVP/trị riêng dùng bộ giải thư viện ở một số bước. Báo cáo không lưu toàn bộ vòng nội bộ. Dung sai bước ẩn hoặc phần dư ma trận không phải sai số toàn cục của bài liên tục.
- GUI chưa được kiểm trực quan trong phiên làm việc này vì Tcl/Tk không khởi tạo được. PDF đã được render và xem trực tiếp; các HTML mẫu đã được xuất từ báo cáo thật. Bộ audit công thức là một tập trường hợp cụ thể, không phải chứng minh mọi biểu thức người dùng có thể nhập đều hiển thị đúng.

## Cập nhật sau khi sửa mã

Chạy các lệnh trong [README](README.md), xem lại bảng số và `failure/status`, rồi chạy `Build_pdf.ps1`. Kiểm PDF bằng `python kienthuc/final/verification/inspect_pdf.py` nếu môi trường có `pdfplumber` và `pypdfium2`. Ảnh xem thử, log biên dịch và văn bản trích PDF nằm trong `build/`; thư mục này được bỏ qua khi đưa vào Git.
