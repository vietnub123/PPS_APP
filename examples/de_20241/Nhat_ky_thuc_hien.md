# Nhật ký giải thử — chỉ dùng repo

Đây là bản ghi thao tác, căn cứ lựa chọn và các phép tính có thể chạy lại. Bài thi đã sắp xếp mạch lạc ở [HTML](../../Bai_giai_de_20241.html) và [Markdown](../../Bai_giai_de_20241.md).

## 1. Tìm và đọc nguồn

Lệnh tìm: `rg --files -g '*20241*' -g '*GKtest*' -g '*Guide*'`. Tìm được đúng ảnh đề và workbook 20241. Đã xem toàn bộ ảnh và phóng phần ghi chú: **“Đề 2 sheet 3”**.

Đã đọc `Guide_di_thi_nhanh.md`, đối chiếu `Huong_dan_dung_khi_thi.md` và các hàm đang được gọi trong `pps/gui.py`, `pps/interpolation.py`, `pps/inverse_solution.py`, `pps/inverse_model.py`. Không tra web, không tải thư viện hay lời giải; không dùng đáp số đề khác làm đầu vào.

Dòng “file 20241 chưa có” trong hướng dẫn đầy đủ là ghi nhận của đợt trước. Lượt này đã tìm thấy và đọc workbook mới trong repo; các tham số được lấy trực tiếp từ file hiện có, không lấy nhận định cũ ấy để bỏ qua dữ liệu.

## 2. Đọc workbook, không đoán sheet theo tên file

Dùng `openpyxl` đã có trong môi trường repo, đọc cả ba sheet:

| Sheet | Dữ liệu | Tham số | Cách xử lý |
|---|---|---|---|
| Sheet1 | 106 cặp ở B:C, cột A trống; giống dữ liệu Sheet3 | Không có x̄,ȳ | Không nhập nhầm A:B thành x,y |
| Sheet2 | 106 cặp khác, x bắt đầu 1,1.115,… | D1=4,F1=5 | Không dùng vì ảnh ghi Sheet3 |
| Sheet3 | 106 cặp A:B, x bắt đầu 1,1.117,… | D1=4,F1=6 | Dùng; cũng là sheet đang active |

Kiểm tra tất cả bước bằng phân số của các số thập phân đã đọc: h=0.117, x_i=1+0.117i, i=0,…,105; miền [1,13.285]. Không thay y bằng công thức suy đoán, không làm trơn hoặc thêm dữ liệu. Toàn bộ cặp và dòng Excel được ghi vào `du_lieu_Sheet3.csv`.

## 3. Ghép yêu cầu đề với guide và ô nhập

| Câu | Nhận diện | Chọn công cụ/nhập |
|---|---|---|
| a | Đa thức đã có hệ số; cần đạo hàm bằng Horner | Đạo hàm & Horner → Horner; `3.5 -2.78 5.63 0 -15.28 1.54`; c=2.57; cấp3 |
| b | Viết thuật toán Stirling, 2N+1 mốc | Viết kiểm lưới, chọn cửa sổ, sai phân, hai tổng chẵn/lẻ và đổi đạo hàm |
| c | Bảng đều, yêu cầu đúng9 mốc quanh4 | Nội suy đa thức → Stirling; điểm4; cấp1; số mốc9 |
| d | Tìm x tại mức6 bằng lặp | Quét dấu trước; Nội suy ngược → Lặp có cận co; nhập khoảng, tập9 mốc, hướng và dung sai rõ ràng |

Đã giữ hệ số0 ở câu a. Câu c chọn các dòng gốc22…30, gốc giữa4.042, t̄=−14/39. Hai đại lượng cần tính là Q(t̄) và Q′(t̄)/0.117.

## 4. Quét mức trước khi lặp

Chỉ duyệt các tích `(y_i−6)*(y_(i+1)−6)`. Bốn tích âm ở i=14,23,62,82, cho bốn khoảng [2.638,2.755], [3.691,3.808], [8.254,8.371], [10.594,10.711]. Không có mốc nào đúng mức6. Việc này không chứng minh hàm thật chỉ có bốn nghiệm.

Lựa chọn công bố cho lượt tính chính:

| Nhánh | Tập chỉ số gốc | Hướng | Gốc và J |
|---|---|---|---|
| 1 | 11…19 | Tiến | 2.287; J=[3,4] |
| 2 | 22…30 | Tiến | 3.574; J=[1,2] |
| 3 | 58…66 | Tiến | 7.786; J=[4,5] |
| 4 | 78…86 | Lùi | 11.062; J=[−4,−3] |

Câu d không bắt buộc bậc; chọn cùng số9 mốc như câu c để giữ bậc tối đa8. Với nhánh2, dùng lại đúng chín mốc câu c. Những tập khác là mô hình cục bộ riêng; không gọi chúng là cùng một đa thức toàn bảng. Chọn ε_x=ε_y=10⁻⁶ theo guide; đề không in dung sai này.

Đã chạy riêng ca khảo sát tiến cho nhánh4: t₀≈5.254557731263 nằm ngoài J=[4,5], nên không có chứng nhận áp dụng với seed mặc định. Ca này được lưu với trạng thái thất bại rõ ràng. Lượt chính chọn lùi, t₀≈−3.527326106594 thuộc [−4,−3], rồi kiểm tra lại đầy đủ ảnh và q. Không sửa seed, kẹp biên hoặc đổi phương pháp ngầm.

## 5. Chạy công cụ và kiểm bằng phép tính cơ bản

Tất cả câu số gọi `pps.gui.dispatch`, cùng đường chạy mà GUI và `exam_cli.py` dùng. Mỗi lượt lưu JSON nhập lại được, TXT và HTML đầy đủ từ bộ xuất của repo.

Các phép kiểm bổ sung trong `giai_de.py`:

- Lặp Horner bằng phân số, so từng số dư với bảng app; nhân đúng 2! và3!.
- Dựng sai phân hữu tỷ, cộng riêng hạng Stirling chẵn/lẻ và đạo hàm từng tích; đối chiếu giá trị/đạo hàm app trong ngưỡng10⁻¹¹.
- Đổi gốc đa thức bằng phép nhân/cộng hệ số: Q_Stirling(t−4) bằng **chính xác** đa thức Newton nhánh2. Không so hai nghiệm của hai đa thức khác nhau rồi coi đó là kiểm chứng.
- Với từng nhánh, đọc chứng nhận hữu tỷ q<1 và bao Φ(J), giữ mọi vòng; kiểm nghiệm cuối còn trong khoảng, B≤10⁻⁶ và phần dư≤10⁻⁶.
- Chạy lại các JSON bằng CLI: sáu bài chính phải trả0; ca khảo sát chưa đủ chứng nhận phải trả1.

Không dùng SciPy/root solver hay tài liệu bên ngoài để tạo đáp số tham chiếu. Các công cụ của repo có thể sử dụng thư viện vốn là phụ thuộc của dự án; không có nguồn dữ liệu/toán học mới được đưa vào.

Kết quả kiểm: sáu JSON chính trả mã0, ca khảo sát tiến nhánh4 trả mã1 đúng dự kiến. Đã dựng ảnh bảng/công thức bằng `math_image` và `inverse_table_image` sẵn trong repo để kiểm tra dấu, chỉ số, bảng chín mốc và bảng vòng lặp. Bản HTML không gọi ảnh/script từ mạng; bốn nhóm chi tiết chứa đủ số hạng của 32 vòng. SHA-256 của chín nguồn trong tệp kết quả đã được đối chiếu lại; workbook gốc giữ nguyên.

## 6. Cách đọc và chạy lại

Mở `Bai_giai_de_20241.html`: phần chính có đủ bốn câu, các bảng vòng lặp và kết luận; mở mục chi tiết để thấy T₂…T₈ ở mọi vòng. Khi in HTML, các chi tiết tự mở theo bộ xuất sẵn có. Không cần kết nối mạng vì công thức đã được nhúng thành ảnh.

Chạy `.venv\Scripts\python.exe examples\de_20241\giai_de.py` để tạo lại mọi đầu ra từ workbook. Chạy `CHAY_CONSOLE.bat examples\de_20241\D2_Lap_tien.json` để xem riêng nhánh gần x=4. Hash nguồn, đáp số và kết quả kiểm CLI nằm trong `ket_qua_va_nguon.json`.
