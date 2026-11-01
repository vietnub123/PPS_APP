# Đặc tả nội suy, đạo hàm và Horner — bản chờ duyệt

Ngày đối chiếu: 31/10/2026. **Người dùng đã duyệt đặc tả và cho triển khai.** Giữ tên tệp để truy lại bản đã duyệt; kết quả triển khai và bài mẫu xem [báo cáo cập nhật](../../Cap_nhat_trinh_bay_noi_suy_dao_ham_Horner.md).

## 1. Vấn đề cần sửa

Bài giải `Bai_giai_de_20241.html` đã được dựng bằng script riêng `examples/de_20241/giai_de.py`: script gọi bộ tính của app, rồi tự tính thêm bằng số hữu tỷ và tự dựng lời giải bằng `ReportBuilder`. Vì vậy, không thể lấy độ đầy đủ của bài giải đó để khẳng định màn hình Stirling/Horner hiện tại có cùng thông tin. Cách trình bày trước đã không làm rõ điều này.

Bộ tài liệu này quy định trực tiếp những gì **mỗi lần chạy trong tool phải tự sinh ra** từ dữ liệu đang nhập. Không dùng script theo một đề cụ thể để lấp phần còn thiếu. Các ví dụ có ghi rõ nguồn; ví dụ tự dựng không được gọi là dữ liệu đề thi.

## 2. Các tài liệu cần duyệt

| Tài liệu | Nội dung |
|---|---|
| [01 — Nội suy đa thức](01_Noi_suy_da_thuc_Thuat_toan_va_trinh_bay_CHO_DUYET.md) | Lagrange; Newton tỉ sai phân tiến/lùi; Newton sai phân tiến/lùi; Gauss I/II; Stirling; Bessel. Chọn mốc, chỉ số, mã giả, bảng từng hạng, ví dụ, ca biên. Bổ trợ Chebyshev, thêm mốc, điền giá trị thiếu có giả thiết bậc. |
| [02 — Đạo hàm](02_Dao_ham_so_Thuat_toan_va_trinh_bay_CHO_DUYET.md) | Đạo hàm của đa thức nội suy; công thức p+1 điểm trên mốc bất kỳ; trọng số; hệ số đổi biến; sai số và nhiễu; ví dụ. |
| [03 — Horner](03_Horner_Thuat_toan_va_trinh_bay_CHO_DUYET.md) | Tính giá trị; chia đa thức; chia lặp lấy đạo hàm; Horner Newton; bảng nhân–cộng và ví dụ đề 20241. |

Nội suy ngược tiếp tục theo [đặc tả hiện có](Noi_suy_nguoc_Guide_trien_khai_va_hien_thi%20%282%29.md), nhất là §0 về chọn mốc và khoảng nghiệm. Spline có tài liệu riêng `03Spline_Phuong_phap_luan_Thuat_toan_Bai_mau.pdf` trong cùng thư mục. Bản này không thay hai đặc tả đó và không yêu cầu sửa bình phương tối thiểu, tích phân hay phương trình vi phân.

## 3. Hiện trạng có bằng chứng từ repo

Các kết luận sau lấy từ mã và báo cáo thực tế, chưa dựa vào việc mở cửa sổ GUI trong lượt đối chiếu này.

| Phần | Tool hiện có | Phần đề xuất bổ sung |
|---|---|---|
| Chọn mốc nội suy | `interpolate`/`select_points` giữ toàn bảng khi bỏ trống số mốc; chọn tập con khi nhập số mốc. | ID dòng gốc, lý do chọn cửa sổ, chỉ số cục bộ, bậc tối đa, điểm có nằm trong tập chọn hay không. |
| Nội suy thông thường | Công thức, bảng sai phân/tỉ sai phân hoặc bảng Lagrange, bảng tích, đa thức và kết quả cấp đạo hàm được yêu cầu. | Các bước suy luận và bảng nối **ô sai phân → hệ số → tích cơ sở → đóng góp số → tổng**. |
| Stirling 9 mốc đề 20241 | `C_Stirling_9.txt` có bảng sai phân, bảng tích và cách ghép hạng bằng ký hiệu. Chạy `order=1` chỉ ghi kết quả đạo hàm tại điểm tính. | Tính đồng thời giá trị hàm và đạo hàm khi đề cần cả hai; giải thích từng trung bình sai phân, giai thừa, tích cơ sở, phép thế số và tổng. |
| Bảng lớn | Trên 32 mốc, hoặc khi khai triển tràn số, app chuyển sang dạng tích; có bảng hệ số công thức và Newton lồng tương đương. | Giữ đủ vết tính theo phương pháp được chọn; công khai cách đánh giá số, không dùng hệ số Newton lồng để thay mất lời giải Stirling/Bessel. |
| Đạo hàm từ bảng | `calculus.differentiate` chọn p+1 mốc và in trọng số, đóng góp, kết quả. | Công bố quy tắc chọn mốc, cách dựng từng trọng số, kiểm tra moment, công thức quen thuộc nếu lưới phù hợp, giải thích sai số. |
| Horner | Có hệ số nhập, bảng hai cột hệ số/giá trị tích lũy cho mỗi lượt, các kết quả đã nhân giai thừa. | Công thức truy hồi, cột phép nhân và phép cộng, thương/số dư, liên hệ giữa các lượt, chứng minh hệ số Taylor và bảng tổng kết đạo hàm. |
| Báo cáo | Các phần trên chủ yếu dùng `presentation['formulas']`, bảng và `after_tables`; chưa có lời giải bố cục đầy đủ như script đề 20241. | Một nguồn dữ liệu tính chung cho màn hình, văn bản và HTML, với bố cục nêu trong từng tài liệu. |

## 4. Quy tắc trình bày chung đề xuất

Một lời giải phải đọc được theo trình tự:

1. **Đề yêu cầu gì:** giá trị, đạo hàm cấp nào, số mốc/bậc nào, phương pháp nào.
2. **Dữ liệu nào được dùng:** số cặp nhập, tập chọn, dòng nguồn, các điều kiện đã kiểm tra.
3. **Vì sao dùng được phương pháp:** mốc đều/bất kỳ, số mốc chẵn/lẻ, vị trí điểm tính. Nếu đề chỉ định thì nói rõ đang làm theo đề.
4. **Công thức và ký hiệu:** định nghĩa chỉ số và biến trước khi thế số.
5. **Quá trình tính:** mỗi hàng có nguồn, phép tính và kết quả; đủ mọi cấp đến bậc yêu cầu.
6. **Thế số và cộng kết quả:** chỉ ra các đóng góp, đơn vị/đổi biến khi lấy đạo hàm.
7. **Đối chiếu và kết luận:** kết quả, kiểm tra đại số/số học, loại sai số nào đã biết.

Không gọi vòng lập bảng sai phân hay lượt Horner là “vòng hội tụ”. Các phương pháp trong ba tài liệu là phép tính hữu hạn, không cần epsilon để dừng. Số vòng do số mốc, bậc và cấp đạo hàm quyết định.

### Bố cục

- Trên cùng có thẻ kết quả ngắn, nhưng bên dưới vẫn giữ thứ tự lời giải đầy đủ.
- Hai bảng nhỏ có thể đặt cạnh nhau: dữ liệu với tham số; bảng hệ số với bảng thế số; hai lượt Horner. Màn hình hẹp chuyển thành một cột theo đúng thứ tự đọc.
- Bảng sai phân là bảng rộng riêng, cuộn ngang. Không biến mỗi cấp thành một bảng dọc lặp lại dữ liệu.
- Bảng tích hệ số là phần chi tiết; bảng hạng dạng tích có ký hiệu và số là phần chính. Không bắt người đọc tự suy từ một ma trận hệ số dài.
- Bảng dài có phần chi tiết thu gọn và xuất đầy đủ. Phải ghi số hàng/cấp đã ẩn; không tạo cảm giác các hàng ẩn không được tính.
- HTML ngoại tuyến giữ cùng nội dung; bản in mở phần chi tiết. Không cần Internet để đọc công thức.
- Không hiện ô chưa định nghĩa bằng số 0. Hệ số tính được bằng 0 vẫn phải có hàng và được phân biệt với ô trống.

### Số học

Các bảng là vết của phép tính thật, không dựng lại bằng những số đã làm tròn trên màn hình. Hiển thị đủ chữ số để theo dõi; chỉ làm tròn ở khâu trình bày. Với dữ liệu thập phân cần tính chính xác để đối chiếu, ghi rõ đang hiểu các số thập phân đã nhập là dữ liệu của mô hình, không phải giá trị thật không sai số.

Đa thức dạng tích, đa thức khai triển và kết quả đánh giá ổn định phải cùng một mô hình. Nếu khai triển theo x mất chính xác, lấy dạng tích/biến chuẩn hóa làm chính và ghi nguyên nhân. Không in một đa thức khai triển sai rồi đặt bên cạnh đáp số đúng mà không giải thích.

## 5. Tiêu chí chấp nhận trước khi sửa giao diện

| Mã | Yêu cầu phải đọc được từ đầu ra của tool |
|---|---|
| A1 | Biết chính xác lấy mốc nào, có thay tập mốc hay không. |
| A2 | Mọi hạng có chỉ số đúng, hệ số đúng, tích cơ sở đúng và đóng góp số. |
| A3 | Chạy Stirling với yêu cầu cả giá trị lẫn đạo hàm phải có cả hai kết quả cùng quá trình; không cần script riêng. |
| A4 | Nhìn bảng Horner kiểm lại được từng phép nhân–cộng, thương, số dư và giai thừa. |
| A5 | Mốc bất kỳ không bị ép dùng sai phân đều; chẵn/lẻ sai được báo đúng nguyên nhân; không tự bỏ mốc. |
| A6 | Điểm trùng mốc và nghiệm/hệ số bằng 0 không gây chia 0 trong cách đánh giá đạo hàm. |
| A7 | Cùng tập mốc: các công thức nội suy đầy đủ cho cùng đa thức trong sai số tính toán; khác tập mốc không bị ép có cùng đáp số. |
| A8 | Sai số nội suy hàm thật, sai số dữ liệu, làm tròn và sai số kiểm tra tại mốc không bị đánh đồng. |
| A9 | Bảng trên màn hình và bản xuất chứa cùng vết tính; bảng lớn không bị mất dữ liệu vì giới hạn ảnh. |
| A10 | Mỗi ví dụ ghi rõ “tự dựng” hoặc tệp/sheet/dòng của đề; phần tự chọn được ghi rõ. |

## 6. Nguồn và phạm vi kiểm tra

Chỉ dùng tài liệu/mã trong repo và phép biến đổi đại số cơ bản:

- `../MI3042_Chuong1_Hieu_chinh_va_bo_sung_ma_gia.pdf`: nền lý thuyết Chương 1, đặc biệt Horner, Lagrange, Newton và nội suy trung tâm. Các khoảng dùng thuận lợi là khuyến nghị, không tự biến thành điều kiện cấm.
- `../../pps/interpolation.py`, `../../pps/calculus.py`, `../../pps/polynomial_model.py`, `../../pps/chapter1_tools.py`: đối chiếu thuật toán thực tế.
- `../../pps/gui.py`, `../../pps/math_view.py`: đối chiếu trường nhập và khả năng trình bày.
- `../../examples/de_20241/A_Horner.txt`, `C_Stirling_9.txt`, `giai_de.py`: phân biệt báo cáo tool với báo cáo script tự bổ sung.
- `../20241_MI3042_GK.jpg`, `../20241GKtest2.xlsx`: ví dụ đề thật; chỉ Stirling và Horner được dùng lại trong bản này.
- `../../tests/test_edge_cases.py`, `../../tests/test_chapter1_audit.py`: ca kiểm tra có sẵn, không lấy việc test qua làm bằng chứng rằng lời giải đã đầy đủ.

Các ví dụ số trong ba tài liệu được kiểm bằng phép tính hữu tỷ và đối chiếu hàm hiện có. **Việc đối chiếu này xác nhận các ví dụ; chưa phải kiểm định mọi công thức/cách trình bày cho mọi dữ liệu.**

## 7. Các đối chiếu đã làm cho bản tài liệu

- Dựng đa thức từ đúng công thức/chỉ số Gauss I, Gauss II, Stirling, Bessel trong bản này bằng phép cộng/nhân hữu tỷ; so với Lagrange dựng độc lập trên cùng tập: **30 trường hợp** với số mốc từ 1 đến 10 theo điều kiện chẵn/lẻ. Kiểm giá trị và hai cấp đạo hàm tại bốn điểm mỗi trường hợp, bằng nhau chính xác.
- Kiểm ba bảng trọng số đạo hàm mẫu bằng hữu tỷ và moment đến bậc 2; đối chiếu kết quả với `calculus.differentiate`.
- Kiểm cả Newton tiến/lùi tỉ sai phân và sai phân đều theo công thức trong bản; kiểm hai ví dụ nhỏ Stirling/Bessel bằng hữu tỷ và đối chiếu bộ tính hiện có.
- Kiểm toàn bộ bốn lượt Horner đề 20241, các tích trung gian, số dư và phép nhân 2!,3! bằng hữu tỷ; đối chiếu `interpolation.horner`.
- Đọc lại chín cặp trực tiếp từ workbook Sheet3, kiểm t=−14/39, các σ_k/β_k, bảng đóng góp giá trị và đạo hàm Stirling, đáp số cuối.
- Kiểm đường dẫn tài liệu và cách đóng/mở khối công thức/mã. Các kiểm tra này không mở GUI và không xác nhận các bảng đề xuất đã được triển khai.
