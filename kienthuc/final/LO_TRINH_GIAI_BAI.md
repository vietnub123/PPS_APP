# Bắt đầu ở đây: từ đề bài đến bài giải hoàn chỉnh

Luồng dùng cho mọi loại bài:

**Đọc đề → ghi dữ kiện và yêu cầu → kiểm tra/tiền xử lý → chọn phương pháp → viết thuật toán → nhập và chạy → kiểm tra kết quả → trình bày bài giải.**

Trong phòng thi, mở file này làm bản đồ. Đọc công thức bằng PDF; các file `.tex` là nguồn sửa tài liệu, không phải chương trình cần chạy.

## 1. Mỗi bước mở file nào?

| Bước | Việc phải làm | File cần mở | Thứ phải có trước khi sang bước sau |
|---|---|---|---|
| 1. Đọc bài toán | Đọc đúng câu, đúng đề/sheet; phân biệt bảng số, biểu thức và các tham số cho riêng | Ảnh/PDF đề và workbook trong [kienthuc](../). Đề 20241: [ảnh](../20241_MI3042_GK.jpg), [dữ liệu](../20241GKtest2.xlsx). Đề 20251 trong repo: [ảnh](../20251_MI3042_GK.jpg), [dữ liệu test2](../20251GKtest2.xlsx) | Bản chép yêu cầu từng câu; tên sheet, vùng dữ liệu, điểm/mức đích và đơn vị |
| 2. Phân tích và nhận dạng | Đề cho gì, hỏi gì, bắt buộc thuật toán/số mốc/bậc/h/sai số/biên nào? | Đoạn đầu và đúng mục 1–9 trong [Guide đi thi nhanh](../../Guide_di_thi_nhanh.md). Xem một quá trình phân tích thật ở mục 1–4 của [nhật ký 20241](../../examples/de_20241/Nhat_ky_thuc_hien.md) | Lựa chọn có căn cứ: nhóm tool, phương pháp, tập mốc/nhánh, tham số đề cho; đánh dấu các lựa chọn do mình tự đặt |
| 3. Kiểm tra và tiền xử lý | Kiểm ô số, dấu, x trùng, lưới, nhánh; đổi gốc/đơn vị nếu cần, đổi cả mục tiêu và biên | [Tiền xử lý Excel PDF](Tien_xu_ly_Excel.pdf), [workbook thao tác](Tien_xu_ly_Excel.xlsx); nguồn sửa [TeX](Tien_xu_ly_Excel.tex) | Hai cột dùng để nhập; nhật ký mọi phép đổi/lọc; công thức khôi phục kết quả về bài gốc |
| 4. Chốt phương pháp và thuật toán | Kiểm điều kiện áp dụng; đọc Input, Output, công thức và thứ tự từng bước | Đúng chương trong [Sổ tay PDF](So_tay_PPS.pdf), theo bảng ở mục 2 dưới đây | Thuật toán tổng quát đúng loại bài, gồm khởi tạo, truy hồi/cách lập bảng, dừng và trả kết quả nếu có lặp |
| 5. Nhập chương trình | Thay dữ liệu và mọi tham số ví dụ; chạy đúng lựa chọn | Phần **Input của tool** ở đầu chương PDF; [hướng dẫn thao tác/JSON](../../Huong_dan_dung_khi_thi.md); một JSON cùng loại ở mục 2 | Một lượt nhập tái lập được: lưu bài thành JSON; không chỉ giữ ảnh đáp số |
| 6. Đọc quá trình tính | Đối chiếu tập mốc, gốc, cơ sở, hệ, bộ giải và các vòng thực sự được tính | Tab **Lời giải toán học**, mở **Chi tiết**; xem trước [58 bài HTML](examples/presentation/index.html). Khi làm bài mới: **Lưu lời giải → HTML** và **Xuất bảng** | Bảng tính, phép thế, các vòng, kết luận/trạng thái, sai số và lý do chưa đạt nếu có |
| 7. Kiểm tra và viết bài | Thế lại điều kiện, đọc tiêu chí dừng, khôi phục biến/đơn vị; viết lời giải theo trình tự suy luận | **Phụ lục C** của [Sổ tay PDF](So_tay_PPS.pdf); phần kiểm tra/kết luận cuối chương; [đối chiếu mẫu 20251](Doi_chieu_mau_20251.md) | Bài giải gồm dữ kiện → lựa chọn → thuật toán/công thức → bảng và tính số → đáp án, sai số |

Không phải bài nào cũng cần đổi dữ liệu. Nếu dữ liệu đã phù hợp, bước 3 chỉ kiểm tra và ghi nhận. Không tịnh tiến hoặc loại điểm chỉ để một phép biến đổi chạy được mà không xét ảnh hưởng đến bài toán.

## 2. Tra đúng loại bài: thuật toán, cách nhập và ví dụ

Mọi **chương** dưới đây đều ở cùng [So_tay_PPS.pdf](So_tay_PPS.pdf). Cột nguồn chỉ nơi sửa/đọc trực tiếp trong IDE. File JSON là một **bài mẫu để thay dữ liệu**, không phải đáp án hay đầu vào dùng chung cho mọi đề.

| Loại bài | Thuật toán, bảng tổng quát và diễn giải | Guide quyết định | JSON nhập mẫu đã có |
|---|---|---|---|
| Lagrange, Newton, Gauss I/II, Stirling, Bessel | **Chương 1**; [nguồn](chapters/01_noi_suy_horner.tex), [khuôn input–quá trình–output](chapters/toolflow_01.tex) | Guide nhanh **mục 1** | [Stirling 7 mốc đọc từ ảnh](examples/presentation/Stirling_7_tu_anh.json), [Bessel](../../examples/02_bessel.json) |
| Horner, giá trị và đạo hàm của đa thức đã biết | **Chương 1**, phần Horner; [nguồn](chapters/01_noi_suy_horner.tex) | Guide nhanh **mục 5** | [01_Horner.json](examples/01_Horner.json) |
| Nội suy ngược: lặp, hàm ngược, chia đôi đa thức | **Chương 2**; [nguồn](chapters/02_noi_suy_nguoc.tex), [khuôn thao tác](chapters/toolflow_02.tex) | Guide nhanh **mục 2** | [Lặp có cận co](examples/02_Nguoc_co_can.json); [các nhánh đề 20251](../../examples/de_20251/README.md) |
| Spline mọi loại biên/bậc được hỗ trợ | **Chương 3**; [nguồn](chapters/03_spline.tex), [khuôn theo loại biên](chapters/toolflow_03.tex) | Guide nhanh **mục 3** | [Bậc 4, đạo hàm đầu phải](examples/03_Spline_bac4_phai.json) |
| Bình phương tối thiểu: từng họ hàm, log hoặc SSE gốc | **Chương 4**, tìm đúng tên mô hình; [nguồn](chapters/04_binh_phuong_toi_thieu.tex). Phép giải Gauss/QR/SVD: [nguồn riêng trong cùng chương](chapters/04a_Gauss_QR_SVD.tex) | Guide nhanh **mục 4** | [QR có trọng số](examples/04_QR_trong_so.json); các mô hình khác ở [thư mục đề 20251](../../examples/de_20251/README.md) |
| Đạo hàm từ bảng số | **Chương 5**, phần đạo hàm; [nguồn](chapters/05_dao_ham_tich_phan.tex), [khuôn nhập và bảng](chapters/toolflow_05.tex) | Guide nhanh **mục 5** | Nạp ví dụ bằng nút **Nạp lại ví dụ của phương pháp**, rồi **Lưu bài** để tạo JSON đúng loại |
| Hình thang, Simpson, trung điểm, Newton–Cotes, tích phân kép | **Chương 5**, phần đúng quy tắc; [nguồn](chapters/05_dao_ham_tich_phan.tex), [khuôn bảng/trọng số](chapters/toolflow_05.tex) | Guide nhanh **mục 6** | [Hình thang, Runge](examples/05_Hinh_thang_Runge.json), [Simpson](../../examples/04_tich_phan.json) |
| Euler, RK, Adams; bài toán Cauchy/hệ ODE | **Chương 6**; [nguồn](chapters/06_phuong_trinh_vi_phan.tex), [khuôn tầng và bước](chapters/toolflow_06.tex) | Guide nhanh **mục 7** | [Adams 3](examples/06_Adams3.json), [hệ dao động](../../examples/05_he_dao_dong.json) |
| Bài toán biên, Robin, trị riêng | **Chương 7**; [nguồn](chapters/07_bien_tri_rieng.tex), [khuôn hệ sai phân](chapters/toolflow_07.tex) | Guide nhanh **mục 8** | [Robin](examples/07_Bien_Robin.json), [trị riêng](examples/08_Tri_rieng.json) |
| Chọn mốc, Chebyshev; câu phụ về cận sai số/điền dữ liệu/giải hệ riêng | **Chương 1** phần chọn mốc; **Phụ lục A** cho API bổ trợ, [nguồn](chapters/08_api_bo_tro.tex) | Guide nhanh **mục 9** | Nạp ví dụ GUI cho chọn mốc; API bổ trợ có lời gọi mẫu trong [hướng dẫn đầy đủ](../../Huong_dan_dung_khi_thi.md) |

Muốn tra một tên phương pháp cụ thể trong 58 lựa chọn, dùng [coverage.csv](verification/coverage.csv), hoặc mục **Dàn ý trình bày của đủ 58 lựa chọn** ở Phụ lục C.

## 3. Thuật toán để chép ra nằm ở đâu?

Phân biệt ba thứ:

1. **Thuật toán toán học để viết bài thi:** công thức và các bước trong đúng Chương 1–7 của sổ tay. Chép theo đề đang làm, ghi rõ Input, Output, khởi tạo, các bước/lượt và dừng/trả kết quả. Với phương pháp hữu hạn như Horner/spline, không tự thêm điều kiện hội tụ.
2. **Dàn ý bài giải:** [outline58.tex](verification/outline58.tex), đã đưa vào Phụ lục C, được sinh từ [exam_style.py](../../pps/exam_style.py). Dàn ý giúp không quên bước nhưng không chứa thay cho mọi công thức và truy hồi của từng thuật toán.
3. **Mã nguồn thực thi:** các file Python trong `pps/`. Đây là nơi kiểm tool đang làm gì, không phải đoạn Python để chép thay cho thuật toán nếu đề yêu cầu mã giả.

**Hiện chưa có một file mã giả độc lập, đồng nhất Input–Output–B1… cho trọn 58 lựa chọn.** Phần thuật toán chi tiết đang nằm trong từng chương. Riêng ví dụ đề 20241 có mục **Câu b. Thuật toán Stirling với 2N+1 mốc** trong [bài giải Markdown](../../Bai_giai_de_20241.md), hoặc [HTML](../../Bai_giai_de_20241.html). Đó là ví dụ cho Stirling, không là thuật toán chung cho mọi phương pháp.

## 4. “Code nhập như nào” có hai cách

### Cách A: thao tác GUI

1. Chạy `CHAY_PPS.bat` ở thư mục gốc.
2. Chọn nhóm và phương pháp từ quyết định đã ghi ở bước phân tích.
3. Đọc **Input của tool** trong đúng chương PDF, rồi điền các ô tương ứng.
4. Nhập hai dãy x,y hoặc nhập file có x,y ở hai cột đầu. Với bài hàm/ODE/biên, nhập biểu thức và các tham số theo đúng tên biến của tool.
5. **Lưu bài** ra JSON trước khi chạy để giữ lại toàn bộ lựa chọn.
6. Bấm **Tính kết quả**; mở Chi tiết; **Lưu lời giải** thành HTML; **Xuất bảng** nếu cần.

Mở JSON mẫu: **Mở bài → chọn JSON → thay toàn bộ dữ liệu/tham số → Lưu bài sang file của mình → Tính kết quả**. Không sửa đè bài mẫu khi làm một đề mới.

### Cách B: sửa JSON rồi chạy terminal

File nhập gồm năm trường: `tool`, `method`, `values`, `x`, `y`. Ví dụ đúng 7 mốc trên ảnh đã gửi:

```json
{
  "tool": "Nội suy đa thức",
  "method": "Stirling",
  "values": {"target": "4.15", "order": "1", "count": "7"},
  "x": "3.760 3.875 3.990 4.105 4.220 4.335 4.450",
  "y": "-0.9384 -0.8979 -0.8110 -0.8056 -0.7548 -0.7416 -0.7049"
}
```

Từ PowerShell tại thư mục gốc:

```powershell
.\CHAY_CONSOLE.bat kienthuc\final\examples\presentation\Stirling_7_tu_anh.json
```

Hoặc dùng Python của môi trường dự án:

```powershell
.\.venv\Scripts\python.exe exam_cli.py kienthuc\final\examples\presentation\Stirling_7_tu_anh.json
```

Console in lời giải văn bản. Muốn xuất HTML bằng giao diện thì mở chính JSON đó trong GUI và chọn **Lưu lời giải**. Cú pháp JSON/Python khác nhau giữa các bài; lấy mẫu đúng loại, không chỉ thay `method` rồi giữ tham số của một nhóm khác.

Tên khóa nhập và giá trị mặc định của từng phương pháp được khai báo trong hàm `fields` ở [pps/gui.py](../../pps/gui.py). `dispatch` cùng file chuyển bài nhập sang bộ giải; [exam_cli.py](../../exam_cli.py) gọi chính đường đó. Khi thi, thường chỉ cần JSON và phần Input trong PDF.

## 5. Diễn giải quá trình tính: đọc mẫu hay đọc kết quả của bài mình?

**Trước khi làm bài:** mở [index HTML 58 lựa chọn](examples/presentation/index.html) để xem hình thức, bảng và cách đọc vòng lặp. 58 bài mặc định là dữ liệu tự dựng. Bài [Stirling 7 mốc từ ảnh](examples/presentation/Stirling_7_tu_anh.html) được ghi riêng nguồn.

**Sau khi chạy bài mình:** dùng HTML/TXT vừa xuất từ lượt chạy đó. Trong từng bước, đọc:

- Số liệu nào lấy từ đầu vào hoặc bảng trước?
- Công thức nào tạo ô/hệ số/giá trị mới?
- Mỗi hàng của bảng có nghĩa gì; có phải bước thời gian, tầng RK, vòng nghiệm hay bước khử không?
- Kết quả đó chuyển sang bước nào?
- Đã đạt tiêu chí dừng nào; sai số đang nói về mô hình, thang biến đổi hay hàm thật?

HTML đã lưu là ảnh chụp kết quả của một lượt chạy, không tự cập nhật khi đổi dữ liệu hoặc code. Khi cần kết quả của phiên bản hiện tại, chạy lại JSON rồi xuất HTML mới.

Nếu muốn kiểm nội dung trình bày ở mã nguồn:

| Phần | File |
|---|---|
| Nội suy đa thức, Horner, đạo hàm từ bảng, chọn mốc | [polynomial_worked.py](../../pps/polynomial_worked.py) |
| Nội suy ngược | [inverse_presentation.py](../../pps/inverse_presentation.py); lời giải/trạng thái từ [inverse_solution.py](../../pps/inverse_solution.py) |
| Spline | [spline_worked.py](../../pps/spline_worked.py) |
| Bình phương tối thiểu | [least_squares_worked.py](../../pps/least_squares_worked.py) |
| Tích phân | [calculus.py](../../pps/calculus.py), bố cục chung [exam_style.py](../../pps/exam_style.py) |
| ODE, biên, trị riêng | [differential.py](../../pps/differential.py), bố cục chung [exam_style.py](../../pps/exam_style.py) |
| Vẽ trong GUI / xuất HTML | [inverse_document.py](../../pps/inverse_document.py) / [inverse_export.py](../../pps/inverse_export.py) cho báo cáo có bố cục nhóm |

## 6. Một bài thi mẫu đi qua đủ các bước

Với đề 20241:

1. **Đề:** [20241_MI3042_GK.jpg](../20241_MI3042_GK.jpg).
2. **Dữ liệu:** [20241GKtest2.xlsx](../20241GKtest2.xlsx), Sheet3 theo ghi chú của đề; xem [README bài mẫu](../../examples/de_20241/README.md).
3. **Quá trình tìm dữ liệu và quyết định:** [Nhat_ky_thuc_hien.md](../../examples/de_20241/Nhat_ky_thuc_hien.md), mục 1–4.
4. **Học cách giải và thuật toán:** Guide nhanh mục 1, 2, 5; sổ tay Chương 1, 2; thuật toán Stirling minh họa ở câu b trong bài giải.
5. **Nhập chương trình:** [A_Horner.json](../../examples/de_20241/A_Horner.json), [C_Stirling_9.json](../../examples/de_20241/C_Stirling_9.json), các file D1–D4 cho từng nhánh ngược trong cùng thư mục.
6. **Đọc phép tính của lượt chạy hiện tại:** mở JSON trong app, chạy và xuất HTML mới. Các HTML/TXT cùng tên đã có là kết quả được lưu trước đó.
7. **Xem cách viết thành bài:** [Bai_giai_de_20241.html](../../Bai_giai_de_20241.html). Đối chiếu số với lượt vừa chạy khi dùng lại bài mẫu.

Với đề 20251, đọc [Kiem_dinh_de_20251.md](../../Kiem_dinh_de_20251.md), [README các ca nhập](../../examples/de_20251/README.md) và [đối chiếu ảnh lời giải mới](Doi_chieu_mau_20251.md). Workbook test2 của repo không phải toàn bộ bảng test1 của bốn ảnh lời giải gửi sau; không ghép hai nguồn thành cùng một đề/dữ liệu.

## 7. Những file nên mở sẵn khi thi

1. **File này:** tra bước nào dùng tài liệu nào.
2. **Guide_di_thi_nhanh.md:** nhận dạng câu và chọn phương pháp.
3. **So_tay_PPS.pdf:** công thức, thuật toán, bảng tổng quát và cách diễn giải.
4. **Tien_xu_ly_Excel.pdf + workbook:** chỉ mở khi cần kiểm/đổi dữ liệu.
5. **JSON và HTML của chính bài đang làm:** một bên giữ đầu vào, một bên giữ quá trình và kết quả.

Trước khi thi, làm bước kiểm môi trường trong [Huong_dan_dung_khi_thi.md](../../Huong_dan_dung_khi_thi.md): chạy `KIEM_TRA.bat`, thử GUI và console trên chính máy mang đi, chuẩn bị thư viện trước khi mất mạng.
