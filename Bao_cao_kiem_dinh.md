# Báo cáo kiểm định PPS_APP

## Bản hiện hành: guide v2 và ba phần ngày 30/10/2026

Phạm vi theo yêu cầu mới là **nội suy ngược, spline và bình phương tối thiểu**, cùng đường gọi GUI/JSON/CLI và phần trình bày/xuất. Đã đối chiếu guide nội suy ngược bản `(2)`, PDF nội suy ngược mới 25 trang, PDF spline 23 trang, PDF bình phương tối thiểu 23 trang trong `kienthuc/real`. Hai bản PDF spline/hồi quy không và có `(1)` giống nhau về nội dung. Đã đọc ảnh `20251_MI3042_GK.jpg` và chạy trực tiếp toàn bộ 104 cặp từ `20251GKtest2.xlsx` vừa cấp. [Kiểm định đề thật và các đáp số](Kiem_dinh_de_20251.md).

- **Nội suy ngược:** bỏ điều kiện sai buộc gốc sát khoảng nghiệm; giữ gốc đầu/cuối tập dùng và đủ bậc/mốc. T là khoảng mục tiêu, J dùng chứng nhận riêng. Thực hành có thể ra ngoài T và tiếp tục; cuối cùng ngoài khoảng thì không nhận thành công. Có ô chọn tập con theo dòng gốc, ba quy tắc khởi tạo và giới hạn vòng độc lập. Bảng 36 mốc cả hai chiều trả 2.09; bảng thật 104 mốc thực sự tràn số được ghi đúng, không báo thiếu mốc hoặc tự thay mô hình. [Chi tiết bản sửa](Cap_nhat_noi_suy_nguoc.md).
- **Spline:** hệ moment/truy hồi và bộ giải thực tạo ra nghiệm được giữ trong báo cáo. Có đầy đủ khử xuôi, pivot, thế ngược, hệ số theo từng u=x−x_i, kiểm ghép nút/biên, đạo hàm một phía và tích phân chia đoạn. Bổ sung biên hỗn hợp/tổng quát, phân biệt thiếu hạng và mâu thuẫn. Hệ chuẩn lớn dùng băng ba đường chéo, không dựng ma trận đặc chỉ để hiển thị. Hệ lớn tuần hoàn/not-a-knot tự động dùng SciPy được công bố đúng, không tạo trace Thomas giả.
- **Bình phương tối thiểu:** bảng cơ sở, tổng có trọng số, hệ chuẩn và QR/Gauss/SVD thực tế; nghiệm chuẩn nhỏ nhất chỉ khi chọn rõ. Giữ x đo lặp, w=0, R² âm và phân biệt miền/mục tiêu biến đổi. LM giữ tham số, Jacobian, damping, bước thử nhận/từ chối và lý do dừng. Phần phi tuyến trình bày mục tiêu SSE và bước LM thực tế, không in hệ chuẩn tuyến tính của một bài khác. Phân biệt phần dư nội bộ LM với phần dư y−g dùng đánh giá.
- **Trình bày:** nhóm bảng/công thức theo cột ở cửa sổ rộng, chuyển một cột khi hẹp, chi tiết mở riêng và không giải lại khi thay bố cục. HTML ngoại tuyến tự mở đầy đủ chi tiết khi in; TXT giữ đủ hàng. Đã xem ảnh đúng cửa sổ PPS và các trang in công thức/khử/vòng lặp/kết luận của cả ba phần.

Các ca làm lộ lỗi quan trọng trong đợt này:

| Vị trí | Đầu vào và hành vi sai | Cách sửa và tác động khi làm bài |
|---|---|---|
| `inverse_solution._interval`, chọn gốc | 36 mốc x_i=1+0.115i, mức 1.23 nằm giữa 2.035–2.15: chuyển gốc tới khoảng rồi đòi thêm 36 mốc | Giữ gốc 1 hoặc 5.025 và đủ 36 mốc, đổi T theo gốc thật; hai chiều trả 2.09. Lỗi nghiêm trọng vì từ chối bài hợp lệ ngay bước chuẩn bị. |
| `inverse_solution._iterate` | x=[0,1,2], y=[0,1,8], mức0.5: t₁=1.25 ngoài T bị xem như lỗi không được tiếp tục | Trong thực hành chỉ cảnh báo và tiếp tục theo công thức; giới hạn 1 vòng thì báo hết vòng thật. Kết quả cuối ngoài khoảng không nhận thành công. T và J được kiểm riêng. |
| `least_squares_worked._render`, tổng trọng số | x=[0,1,2], y=[1,2,2], w=[1,2,1]: bảng tổng không trọng số không khớp hệ chuẩn | In đúng Σw=4, Σwx=4, Σwy=7, Σwx²=6, Σwxy=8; hệ cho a=1.25,b=0.5. Trước sửa có thể tính đúng nhưng chép sai hệ trong bài tự luận. |
| `least_squares_worked._render`, lời giải LM | Khớp A exp(bx) với y=[2,5,18]: in thêm Gc=b của cơ sở [1,x], dù bài phi tuyến | In F=Σw(g−y)², định nghĩa phần dư/Jacobian nội bộ và từng bước LM đúng. Không dùng hệ chuẩn của bài tuyến tính khác để giải thích kết quả. |
| `least_squares_worked.solve_least_squares`, hạng phi tuyến | Chọn phần mũ [1,x] ngoài biên độ A, hoặc hai quan sát nhưng ba tham số | Báo thiếu hạng số và không nhận tham số duy nhất; giữ các cơ sở đã chọn. Không âm thầm xóa cột 1 để làm bài chạy qua. |
| `least_squares_worked._nonlinear`, mô hình hằng | Chọn rõ phần mũ rỗng: A exp(0)=A, trước đây ghép mảng cơ sở rỗng làm lỗi dự đoán | Hỗ trợ đúng một tham số: x=[0,1,2], y=[2,5,8], w=[1,2,1] cho A=5, SSE có trọng số18; kiểm giá trị cả ngoài dải x. |

Kiểm chứng bản cuối: `.venv\Scripts\python.exe -m unittest discover -s tests -q` chạy ngoài sandbox: **216 kiểm thử qua, không bỏ qua, 273.753 giây**, gồm 9 kiểm thử GUI thật và hai ca mới về hạng phi tuyến/mô hình hằng. Các lượt kiểm thử riêng trước đó không được cộng vào số 216 này. `compileall`, `git diff --check` và CSV sáu cột/79 dòng nội dung đã kiểm tra.

Sau đó mở rộng kiểm thử GUI hiện có để mở trực tiếp hai JSON đề thật có x/y là mảng 104 phần tử, chạy qua đúng **Mở bài → Tính**: kiểm thử riêng qua trong 7.637 giây. Không thêm một số kiểm thử duy nhất vào tổng 216.

Đã chạy **15 JSON đề mới/mô phỏng qua CLI**: 12 trả mã 0; ba ca lỗi có chủ đích (miền log, tiến/lùi nguyên 104 mốc) trả mã 1 đúng trạng thái. [Nhật ký](examples/de_20251/kiem_tra_cli.txt). Các JSON/HTML/TXT/PDF và ảnh giao diện nằm tại [examples/de_20251](examples/de_20251).

Giới hạn cần đọc cùng đáp số: ảnh có hai đề và nhãn năm khác nhau, chưa có dữ liệu test1; test2 có y âm nên không áp dụng phép log trên nguyên bảng. LM tìm nghiệm dừng, chưa chứng nhận cực tiểu toàn cục. Cận lặp chỉ cho nghiệm đa thức mô hình, chưa bao gồm sai số với hàm thật và toàn bộ sai số máy. Các bằng chứng trên xác nhận những tình huống đã kiểm thử, không bảo đảm mọi dữ liệu đều hội tụ. Các phần môn học khác giữ hồ sơ kiểm định trước, không được suy là vừa được đối chiếu với giáo trình mới.

Kết luận của bản hiện hành:

1. **Bao phủ:** các phương pháp nội suy ngược, spline bậc1–4/biên tổng quát và mô hình bình phương tối thiểu trong ba tài liệu mới có đường gọi và lời giải; bảng CSV nêu từng yêu cầu và giới hạn.
2. **Độ đúng:** đã đối chiếu bài tính hữu tỷ, đa thức biết trước, lưới không đều/ngẫu nhiên, công thức Lagrange độc lập, SciPy tối ưu/spline và dữ liệu workbook gốc. Có kiểm thử các đường thất bại, không chỉ đáp số thành công.
3. **Khả năng làm bài:** GUI/JSON/CLI, bản xuất ngoại tuyến và công thức/phép thế số đã được chạy. Câu viết thuật toán/chứng minh vẫn cần chọn giả thiết và giải thích bằng tay; chương trình cung cấp các tham số và bước tính để trình bày.
4. **Vấn đề còn lại:** không có lỗi khởi chạy hoặc lỗi tái hiện trong các ca hợp lệ đã kiểm thử còn để ngỏ. Những bài không đủ biên, log sai miền, thiếu hạng hoặc lặp không hội tụ phải được báo đúng và cần lựa chọn lại theo đề; không thể đảm bảo mọi tình huống có một đáp số hợp lệ.

## Hồ sơ các đợt trước

Các mục bên dưới ghi lại kiểm định ở thời điểm trước guide v2 và lần mở rộng ba phần. Khi có khác biệt về chọn gốc, khoảng T/J, khởi tạo, số kiểm thử hay đường lời giải, dùng bản hiện hành phía trên và hướng dẫn đã cập nhật.

## Phạm vi và nguồn

Đợt **30/10/2026 chỉ tập trung nội suy ngược**, theo toàn bộ guide và PDF 23 trang trong `kienthuc/real`. Đã sửa lỗ hổng kiểm miền tung độ tập mốc, bổ sung tiền kiểm/căn cứ hội tụ và thay cách nối dọc 11 bảng bằng bảy khối có ba bảng chính, nhóm hai cột và chi tiết mở riêng. Bảng lùi ∇ đặt đúng hàng kết thúc; các lựa chọn Newton/Lagrange có trực tiếp trên GUI. [Bản cập nhật và ví dụ](Cap_nhat_noi_suy_nguoc.md) mô tả đầy đủ.

Kiểm chứng đợt 30/10:

- `.venv\Scripts\python.exe -m unittest discover -s tests -q`: **154 kiểm thử qua**, 159.907 giây, không bỏ qua; gồm 8 kiểm thử GUI thật và kiểm tra co giãn/mở chi tiết không giải lại bài toán.
- Sau hoàn thiện cách nhóm phần kiểm tra khi in và hai ca trình bày mốc đúng mức/lỗi tiền kiểm: `python -m unittest tests.test_inverse_real_export tests.test_inverse_real_presentation tests.test_inverse_guide -q`: **40 kiểm thử qua**, 58.861 giây. Tổng số kiểm thử hiện có là 156; hai lệnh trên là hai lượt chạy riêng.
- Ba bài `real` đã đối chiếu độc lập: hàm ngược 2.5; tiến mức 4 dừng vòng 5 tại 1.666001162884; lùi mức 2 dừng vòng 6 tại 2.133420489204. Chặn tự động q=11/24 và q=73/150 khác q=0.5 minh họa nhưng hợp lệ; ví dụ nhận q=0.5 giữ nhãn có điều kiện theo nguồn.
- Đã chạy 13 JSON nội suy ngược bằng CLI: 11 bài trả mã 0; E rời đoạn và bài ngoại suy chưa bật trả mã 1 cùng lời giải lỗi. `compileall`, `git diff --check` và CSV sáu cột qua.
- Đã xem ảnh đúng HWND cửa sổ PPS ở rộng/hẹp: ba nhóm chuyển 2→1 cột, bảng lùi giữ đúng ∇ và các ô hệ số. Đã xuất và xem bản in HTML/PDF A4 của tiến, lùi, hàm ngược và ngoại suy bị chặn; chi tiết đầy đủ, bảng dài lặp tiêu đề, kiểm tra/quyết định từng vòng được giữ cùng nhóm. Các bản HTML mẫu cũ cũng đã cập nhật theo bố cục mới.

Đợt cập nhật nội suy ngược ngày 29/10 theo guide mới và cả hai PDF 26/36 trang được ghi trong [Cap_nhat_noi_suy_nguoc.md](Cap_nhat_noi_suy_nguoc.md). Quy tắc mới giữ nguyên t0, mốc, bậc và khoảng đã chọn; thay thế cách chọn tâm đoạn hoặc tự chọn mốc gần mức ở bản trước. Có lời giải 9 bước và các ví dụ HTML đầy đủ cho cả kết quả đạt/thất bại.

Đợt rà soát tiếp theo cho các thuật toán còn lại được ghi riêng trong [Kiem_dinh_thuat_toan_khac.md](Kiem_dinh_thuat_toan_khac.md): nội suy ngược, toàn bộ biến thể spline/hồi quy đang có, đạo hàm–tích phân, Euler/RK/Adams, bài toán biên và trị riêng. Đã sửa thêm các lỗi tái hiện được và thêm 40 kiểm thử độc lập cho đợt này.

Đã đọc 52 trang `kienthuc/MI3042_Chuong1_Hieu_chinh_va_bo_sung_ma_gia.pdf`, gồm lý thuyết chương 1, các mã A01–A32, B01–B04 và ba mẫu ghép thuật toán. PDF này không chứa đối tượng ảnh nhúng; công thức và bảng là nội dung PDF có thể trích xuất. Đã đọc cả hai đề trong `20191_MI3042_GK.pdf`, đề `20211_MI3042_GK.pdf`, và nhìn trực tiếp bốn ảnh đề 20221, 20222, 20231, 20241. Đã đọc thân các hàm ở `pps/common.py`, `interpolation.py`, `calculus.py`, `differential.py`, tuyến gọi của `gui.py` và phần trình bày `math_view.py`. Bảng chi tiết ở `Bao_phu_kien_thuc.csv`.

**Căn cứ phạm vi là chương 1.** Đề cũ có câu đạo hàm số và tích phân số thuộc chương 2; PDF chương 1 chỉ giải thích mối liên hệ, không cung cấp toàn bộ giả thiết/cận sai số chương 2. Không suy ra rằng mã chương 2–3 đã được kiểm định đầy đủ. Các file dữ liệu riêng được nhắc trong một số đề (như `testdata_ab.text`, `Kip2Cau1.txt`, dữ liệu khí hậu, file có mật khẩu của 20231/20241) không có trong thư mục đề. `data/extracted_data.json` có các bảng `cau23_a`… và `table1`, nhưng không có căn cứ xác nhận chúng chính là các file dữ liệu đó. Vì vậy chưa thể tính đáp số cá nhân hóa cho các câu ấy.

## Lỗi đã thấy và đã sửa

| Vị trí | Đầu vào làm lộ lỗi; kết quả cũ | Kết quả đúng và sửa đổi | Tác động khi thi |
|---|---|---|---|
| `pps/common.py:points` | `x=[2,0,2,1]`, `y=[4,0,99,1]`: bỏ cặp `(2,99)` rồi nội suy như thể dữ liệu hợp lệ | Báo `ValueError` khi mốc trùng; luôn sắp cả cặp. Hai y khác nhau tại một x không thể thuộc một hàm đơn trị | Cao: có thể trả đa thức sai mà người dùng không biết đã mất dữ liệu |
| `pps/interpolation.py:interpolate`, bảng Lagrange | Với hai mốc `(0,1),(1,2)`, bảng `D_i` cũ có dấu `[1,-2]` do dùng `x_j-x_i`, dù nhãn ghi `x_i-x_j` | Đổi ma trận sang `x_i-x_j`; bảng `D_i=[-1,2]`, phù hợp `P(x)=1+x`. Đa thức tính trước đây đã đúng, lỗi nằm ở bảng lời giải | Cao nếu chép bảng hệ số vào bài tự luận |
| `pps/interpolation.py:least_squares` | Mô hình lũy thừa với `x=[-1,0,1,2]`, `y=[-2,-1,1,4]` trước đây tự dịch x và y rồi vẫn gắn nhãn lũy thừa; hàm được khớp không còn là `A*x^b` của đề | Từ chối x≤0, y=0 hoặc y đổi dấu theo đúng phép log; giữ mô hình gốc. Bổ sung trọng số và tách SSE/MSE/RMSE thang gốc với SSE thang biến đổi | Cao: có thể báo tham số của một mô hình khác đề |
| `pps/interpolation.py:spline` | Tên spline không nhận diện rơi vào nhánh biên đạo hàm cấp hai; `Cubic tuần hoàn` cũ thực chất bị tính như biên cấp hai | Kiểm tra tên phương pháp; hỗ trợ tuần hoàn, not-a-knot; kiểm tra điều kiện áp dụng. Bổ sung spline bậc 4 theo đạo hàm đầu trái và hệ biên hai đầu qua `chapter1_tools.py` | Cao: trả một spline khác điều kiện biên của đề |
| `pps/interpolation.py:inverse` | Kết quả lặp được in như nghiệm đạt dung sai dù chưa chứng minh ánh xạ co; không kiểm tra nghiệm cuối còn trong nhánh x | Không nhận nghiệm nằm ngoài nhánh; báo rõ đây là dừng thực hành theo phần dư và sai khác bước. Bổ sung đảo bảng và chia đôi mô hình | Cao khi kết luận hội tụ/bảo đảm sai số từ một bước lặp |
| `pps/interpolation.py:select_points` | Bảng x không đều bị chặn dù Lagrange/Newton tỷ sai phân hỗ trợ; chọn ngoài hai đầu không được ghi như ngoại suy | Mốc không đều chọn K cặp gần z; mốc đều chọn cửa sổ liên tiếp; ghi ngoại suy và cảnh báo phương pháp thích hợp | Trung bình: thiếu lối làm cho dạng đề mốc bất kỳ |

## Cập nhật các trường hợp biên ngày 27/10/2026

| Vị trí | Ca làm lộ lỗi hoặc giới hạn cũ | Kết quả sau sửa và bằng chứng |
|---|---|---|
| `interpolate` | Bảng 101 mốc bị chặn bởi `n > 100`; giai thừa và tích khai triển cũng có thể tràn số nếu chỉ xóa điều kiện chặn | Bỏ chặn 100. Bảng trên 32 mốc giữ dạng tích; đây là thay đổi cách biểu diễn, **không giảm số mốc**. Dùng `NewtonPolynomial` với Decimal và độ chính xác theo bậc/độ chênh thang. Tất cả phương pháp được thử trên hơn 100 mốc; Stirling 501 mốc của x² trả P(0.5)=0.25 và P′(0.5)=1 |
| `gui.fields`, `dispatch`, `interpolate(count=...)` | Toàn bảng có 100 mốc nhưng đề chỉ yêu cầu Stirling 9 mốc; trước đây phải tự tách ngoài chức năng nội suy | Ô **Số mốc dùng** chọn đúng K mốc quanh điểm tính, ghi K/N và xuất mốc đã dùng. Bảng 100 mốc y=x² chọn K=9 trả P′(49.2)=98.4. Không tự đổi toàn bảng thành nhóm nhỏ khi người dùng để trống K |
| `interpolate`, `difference_model` | Gauss I/II từng bị giới hạn số mốc lẻ mặc dù có thể dùng một phía nhiều hơn một mốc | Hỗ trợ số chẵn: gốc giữa trái cho Gauss I và giữa phải cho Gauss II. Kiểm tra từ 1 đến 10 mốc. Stirling đối xứng vẫn cần số lẻ; Bessel vẫn cần số chẵn |
| `interpolate`, nhánh Lagrange | `x=[0], y=[7]` gọi `Poly.fromroots` với mảng rỗng và lỗi | Trả đa thức hằng 7; đạo hàm cấp cao bằng 0 |
| `common.spacing` | `x=[0,1e-14,2.4e-14]` từng được coi là cách đều vì dung sai tuyệt đối 1e-12 lớn hơn bước | Dùng dung sai tương đối theo bước, từ chối đúng lưới không đều này |
| `calculus.differentiate` | `x=[0,1e-7,2e-7], y=[1e12,1e12,1e12]`, tại 0.5e-7 với bậc 2/cấp 1 trả **2048** thay vì 0. Với 101 mốc -50…50 của x³, bậc 100/cấp 2 tại 0.25 trả **45.154746935676144** thay vì 1.5 | Sinh hệ số Lagrange quanh điểm tính và cộng đóng góp bằng Decimal, chỉ giữ tới cấp đạo hàm cần lấy. Hai ca trả 0 và 1.5; thử thêm bước 1e-160 khi trọng số vượt miền float nhưng đạo hàm vẫn hữu hạn |
| `common.fmt` | `fmt(-1e-12)` hiển thị 0 ở thiết lập mặc định, che mất dấu và độ lớn | Hiển thị khoa học cho số rất nhỏ/lớn, không biến một số khác 0 thành 0 ở thiết lập mặc định |
| `thomas`, `gaussian_elimination` | Hệ `1e-100*I*u=1e-100*[2,3]` bị coi suy biến vì ngưỡng pivot dùng `max(1, scale)` | Dùng ngưỡng theo thang hệ thực sự; thử các thang 1e-100, 1, 1e100 và nghiệm giải tích |
| `common.data_pairs`, nhập Excel/CSV | Dòng đầu `[0,'bad']` có thể bị bỏ như tiêu đề, mất một quan sát | Chỉ bỏ dòng rỗng hoặc tiêu đề nhận diện được. Dòng dữ liệu hỏng báo rõ số dòng. JSON nhận số, dãy số và UTF-8 BOM |
| Horner, Chebyshev, cận nội suy | Chặn cấp Horner 100, bậc sinh mốc Chebyshev 1000; cận có tích/giai thừa dễ tràn hoặc hụt số | Bỏ hai chặn tùy ý; đạo hàm trên bậc được ghi bằng 0. Đã thử yêu cầu cấp 1000, sinh 1201 mốc, cận 201/501 mốc và bổ sung Newton khi tích các hiệu hụt số |
| Chia đôi, tích phân, ODE, BVP | Dung sai NaN, chia đôi bị kẹt ở hai float sát nhau, lưới rất nhỏ không đều; ODE không giải ngược thời gian; Neumann thuần có thể không xác định nghiệm duy nhất | Từ chối đầu vào không hợp lệ với lý do; hỗ trợ ODE ngược chiều và khoảng thời gian 0; báo hệ Neumann q=0 không duy nhất. Lưới tích phân hợp lệ không bị hủy chỉ vì bước Runge phụ 2n vượt giới hạn tài nguyên |
| Hồi quy và phần hiển thị | Hàm cơ sở có miền đứt đoạn có thể khớp được tại mọi dữ liệu nhưng lỗi khi vẽ giữa các mốc; nút trợ giúp trỏ tới file không tồn tại | Giữ kết quả khớp hợp lệ và ghi không vẽ được toàn dải. Trợ giúp đọc đúng `Huong_dan_dung_khi_thi.md` |

`tests/test_edge_cases.py` còn so sánh đa thức 35 mốc với tổng Lagrange tính độc lập bằng `fractions.Fraction`; dữ liệu không phải đa thức bậc thấp, nên phép thử phát hiện được việc tự cắt bậc. Một kiểm thử chạy ví dụ của **từng phương pháp trong GUI** qua `dispatch` và dựng ảnh công thức mà không cần tạo cửa sổ. Không có giả thiết rằng mọi bảng lớn đều là đa thức đơn giản hoặc đều ít nhiễu.

## Chức năng được bổ sung

`pps/chapter1_tools.py` có truy hồi Chebyshev, chia Horner, bổ sung mốc Newton, cận sai số nội suy tại điểm/toàn dải đều/toàn đoạn Chebyshev, điền ô thiếu khi **đề cho** bậc, quét mức, tách nhánh đơn điệu trên bảng, nội suy bằng hàm ngược, lặp với cận co trên đoạn được nhập, chia đôi nghiệm đa thức thuận, giải hệ Thomas/Gauss có chọn trụ, spline bậc 1–4 theo đạo hàm đầu trái, spline có điều kiện đạo hàm hai đầu, kiểm tra giá trị/đạo hàm tại nút, các mô hình khớp sau biến đổi ở trang 49 và tối ưu SSE thang y trực tiếp cho mô hình mũ/lũy thừa. Các hàm này không suy đoán điều kiện còn thiếu từ dữ liệu.

Giao diện có thêm lựa chọn hàm ngược, lặp có cận co, chia đôi đa thức, spline bậc 4, tuần hoàn, not-a-knot, trọng số bình phương tối thiểu và khớp mũ/lũy thừa trên thang y gốc. `exam_cli.py` chạy các file bài JSON trong terminal nếu không mở được cửa sổ. Các hàm bổ sung còn lại có ví dụ Python trong `Huong_dan_dung_khi_thi.md`.

## Kiểm chứng toán học độc lập

- Đa thức `x³−2x+1` với 8 mốc đều `0.3,…,1.0`: Bessel trả `P(0.64)=-0.017856`, `P′(0.64)=-0.7712`, khớp ví dụ trang 52 và giải tích. Trường hợp này cũng kiểm tra số mốc 8, bậc tối đa 7, gốc giữa trái 0.6 và hệ số `h⁻¹` cho đạo hàm.
- Nội suy ngược `x²=2` trên `[1,2]`: đảo bảng ba điểm cho `5/3`, còn chia đôi đa thức thuận cho `√2` trong dung sai `10⁻¹²`. Hai đại lượng không được tráo đổi.
- Spline tự nhiên qua `(0,0),(1,1),(2,0)` cho `S(0.5)=0.6875`, `S′(0.5)=1.125`, đúng trang 52. Spline bậc 4 với đạo hàm đầu trái `[1,0,0]` có hai mảnh `u` và `1+u−2u⁴` như trang 47; bài thử so sánh độc lập với cách giải hệ đầy đủ.
- Hồi quy trọng số `[1,2,1]` trên `(0,1),(1,2),(2,2)` trả `a=5/4`, `b=1/2`, đúng ví dụ trang 48. Các phép biến đổi mũ, nghịch đảo, log khôi phục lại dữ liệu được tạo từ mô hình biết trước.
- Đề 20241 câu a: với `P=3.5x⁵−2.78x⁴+5.63x³−15.28x+1.54`, tại `c=2.57` chương trình trả `P″=1054.696646`, `P‴=1249.3386`; đã so với biểu thức đạo hàm giải tích trong kiểm thử, kể cả hệ số x² bằng 0.
- Kiểm thử biên: mốc trùng, lưới không đều cho công thức đều, sai miền log/căn/chia, thiếu điều kiện spline, không đổi dấu khi chia đôi, ô y thiếu nhưng không đủ giả thiết, và điều kiện biên tuần hoàn không hợp lệ. Kiểm thử tính chất đa thức đã chạy cho Lagrange, Newton, Gauss I/II, Stirling và Bessel.

Chạy `python -m unittest tests.test_chapter1_audit tests.test_numerics tests.test_math_view tests.test_regression_repeated -q`: bộ kiểm thử toán học qua. Chạy `python -m compileall -q pps tests exam_cli.py`: qua. Chạy `.venv\Scripts\python.exe exam_cli.py examples\02_bessel.json`: chạy tại máy này và in `P′(1.5)=3` khi không gọi Internet.

Ngày 29/10 chạy `.venv\Scripts\python.exe -m unittest discover -s tests -q` **ngoài sandbox**: **131 kiểm thử qua, không có kiểm thử bị bỏ qua** (108.144 giây). Trong đó có 27 kiểm thử nội suy ngược mới: A–G, bài bậc 4 PDF 36 trang, bất biến đa thức, dữ liệu lỗi, cận sai số, giới hạn float, công thức và xuất toàn bộ hàng. Sau sửa cuối ở tuyến mở JSON để giữ lựa chọn Lagrange/khoảng riêng, chạy riêng `.venv\Scripts\python.exe -m unittest tests.test_gui -q`: **7 kiểm thử GUI thật qua** (67.893 giây), gồm kiểm thử mới cho giữ lựa chọn qua mở/chạy/chuyển phương pháp và nạp lại ví dụ. Đây là hai lượt chạy riêng; tổng số kiểm thử hiện tại là 132.

Đã chạy cả 7 JSON mới qua `exam_cli.py`: A (hai biểu diễn), B, C, F và bậc 4 trả mã 0; E trả mã 1 với đầy đủ vòng thất bại. Đã xuất HTML/văn bản qua bộ dựng hiện có; render toàn bộ lời giải B, C, E và bài bậc 4 để xem. Đã in HTML B, C, E bằng Edge headless sang PDF (6, 6 và 4 trang), xem các công thức, bảng, dấu âm/số mũ và phần kết luận. Các bản in thử ở `examples/noi_suy_nguoc/`; không cần mạng để mở. `compileall` và `git diff --check` qua.

Lỗi `_tkinter.TclError: Can't find a usable init.tcl` chỉ xuất hiện trong sandbox kiểm định; chạy ngoài sandbox đã xác nhận cửa sổ hoạt động trên môi trường hiện tại. Điều này không thay việc thử trên chính máy thi. `CHAY_CONSOLE.bat` vẫn cung cấp đường chạy ngoại tuyến dự phòng.

## Điều chưa được bảo đảm

- `inverse()` dừng thực hành. `inverse_controlled()` giữ t0, kiểm tra `t0∈J`, `φ(J)⊆J`, `|φ′|≤q<1` bằng chặn hữu tỷ trên cả đoạn. Không xác nhận được thì giữ lời giải thất bại; chia đôi phải được chọn và chạy riêng. Báo cáo tách cận lặp `h q|t_{k+1}−t_k|/(1−q)`, phần chuyển sang float và phần làm tròn số in. Chưa chứng nhận toàn bộ sai số máy bằng số học khoảng. Cận hàm thật cần thêm `E,μ>0`, miền và nguồn giả thiết.
- B03 nhận `p−1` điều kiện đạo hàm đơn hoặc tổ hợp tuyến tính ở hai đầu, giải hệ thưa sau chuẩn hóa và báo suy biến trong độ chính xác máy. Hồi quy dùng SVD đổi thang/QR Decimal; các hàm `thomas`/`gaussian_elimination` in bước khử sau đổi thang từng hàng và phần dư hệ gốc. Những câu yêu cầu **viết thuật toán/chứng minh** vẫn phải trình bày các bước và giả thiết bằng tay theo PDF.
- Mô hình phi tuyến sau log/nghịch đảo tối ưu trên thang biến đổi. `original_scale_fit` giải trực tiếp SSE thang y cho mũ/lũy thừa bằng lặp phi tuyến và có thể đến cực tiểu cục bộ; chưa có lối tương ứng cho các dạng nghịch đảo.
- Không thể lấy sai lệch tại mốc, sai khác hai lần chia lưới hoặc SSE làm cận bảo đảm cho hàm thật khi chưa có giả thiết về đạo hàm, độ dốc và sai số dữ liệu. Nội suy bậc cao có thể mất ổn định số, nhất là ngoại suy.
- Decimal giảm lỗi tính trung gian nhưng không loại bỏ độ nhạy của bài toán hoặc sai số dữ liệu đầu vào. Dữ liệu x,y vẫn được nhập dưới dạng float; mốc đã trùng do làm tròn trước khi nhập không thể khôi phục. Số chữ số làm việc là lựa chọn số học, không phải chứng nhận sai số bằng số học khoảng cho mọi đầu vào.
- Không còn chặn 100 mốc nội suy; thuật toán toàn bảng vẫn dùng thời gian bậc hai và độ chính xác trung gian tăng theo số mốc/thang dữ liệu. Chưa kiểm tra kích thước tùy ý lớn. Các giới hạn tài nguyên lưới tích phân/ODE/BVP còn giữ và được báo trong thông báo lỗi. Chưa chạy kiểm thử đạt giới hạn một triệu khoảng tích phân vì bảng kết quả rất lớn.
- Đề 20191 yêu cầu spline cấp 4 qua ba mốc của `cos(x)` nhưng không ghi ba điều kiện biên: nếu hiểu là spline bậc 4 trơn C³ thì **chưa xác định duy nhất**. Cần nêu điều kiện thiếu trong bài làm, không tự gán biên tự nhiên hay đạo hàm của cos nếu đề không cho phép.
- Đề 20231 có câu cận sai số đạo hàm và tích phân Simpson/Newton–Cotes. Các phần đó thuộc chương 2 nhưng tài liệu kiến thức được cung cấp chỉ là chương 1; chưa xác nhận công thức cận đạo hàm/tích phân theo đúng giáo trình chương 2. Các câu phụ thuộc file dữ liệu đề riêng chưa chạy được trên số liệu thật.

## Kết luận riêng

1. **Bao phủ:** các thao tác tính của chương 1 có đường gọi được mô tả trong bảng CSV; các biến thể tối ưu phi tuyến thang y gốc cho mô hình nghịch đảo chưa có. Không quy thành tỷ lệ phần trăm.
2. **Độ đúng đã kiểm chứng:** có bằng chứng đại số, nghiệm giải tích, ví dụ trang 34–52, kiểm thử biên và so sánh hai cách giải độc lập. Bằng chứng này áp dụng cho các trường hợp đã chạy, không chứng minh mọi đầu vào đều đúng.
3. **Khả năng làm bài:** GUI và terminal đã chạy được trên môi trường hiện tại; cần sẵn thư viện và dữ liệu để dùng ngoại tuyến. Một số đề cần file riêng chưa có, phần tự luận không thể thay bằng kết quả chạy chương trình. Bảng lớn có thể dùng toàn bộ hoặc chọn đúng K mốc theo đề.
4. **Vấn đề nghiêm trọng còn lại:** không còn lỗi khởi chạy GUI được xác nhận ngoài sandbox ở môi trường này. Nhánh lặp cũ không có cận hội tụ bảo đảm; nhánh mới có kiểm tra co nhưng cận chỉ cho đa thức mô hình. Chưa có bằng chứng để kết luận đúng cho mọi đầu vào hay mọi chương của môn học; các thiếu sót phạm vi và dữ liệu đã nêu vẫn còn.
