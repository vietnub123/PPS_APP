# CHỈ DẪN CHO AGENT: GHÉP THUẬT TOÁN NỘI SUY NGƯỢC VÀO CHƯƠNG TRÌNH CÓ SẴN

Phiên bản 1.2 · 29/10/2026 · MI3042 – Phương pháp số

Tài liệu đồng hành: **Noi_suy_nguoc_On_thi.pdf**. Đọc PDF cùng guide này trước khi triển khai. Phạm vi chỉ là nội suy ngược. Guide là đặc tả triển khai, không phải yêu cầu xây lại toàn bộ ứng dụng phương pháp số.

## 1. Nhiệm vụ và kết quả mong muốn

**Ngữ cảnh đã xác nhận:** người dùng đã có chương trình chạy được, luồng import dữ liệu và các tham số. Nhiệm vụ là ghép hoặc sửa thuật toán nội suy ngược cùng phần xuất lời giải trong chương trình ấy. Không xây ứng dụng mới, không làm lại import, parser, biểu mẫu tham số hoặc giao diện điều hướng.

Nhận bảng `(x_i, y_i)` và tham số từ luồng hiện có; tính nghiệm và **xuất một lời giải toán có thể đọc và chép lại theo trình tự trong PDF**, kể cả khi dữ liệu không đáp ứng điều kiện hoặc phép tính thất bại.

Không chỉ in đáp số. Phải trình bày dữ liệu, lựa chọn khoảng/nhánh, mốc đã dùng, gốc, bước lưới, bảng hệ số, công thức ký hiệu, công thức thay số, quá trình tính, kiểm tra dừng và kết luận đúng phạm vi.

Ba phương pháp chính:

1. `inverse_function`: nội suy hàm ngược bằng Newton tỷ sai phân hoặc Lagrange.
2. `forward_iteration`: lặp đơn dựng từ Newton tiến trên mốc cách đều.
3. `backward_iteration`: lặp đơn dựng từ Newton lùi trên mốc cách đều.

Chức năng bổ sung: quét nghiệm tại mốc/khoảng đổi dấu; tách nhánh trên bảng; nội suy ngược bậc 1; chia đôi phương trình của đa thức thuận khi người dùng cho phép.

Không thay lặp đơn bằng Newton–Raphson rồi gọi đó là “Newton tiến/lùi”. Newton tiến/lùi trong tài liệu là **dạng đa thức nội suy**, không phải phương pháp tiếp tuyến tìm nghiệm.

Đọc điểm gọi thuật toán hiện tại, kiểu dữ liệu đầu vào/đầu ra và các thành phần dựng công thức/bảng/thông báo của repository. Dùng đúng ngôn ngữ, kiến trúc và thư viện hiện có; không chuyển nền tảng hoặc thêm framework. Các tên hàm, trường và schema trong guide là mô tả ý nghĩa: ánh xạ vào tên tương ứng của chương trình, không bắt buộc đổi tên API hoặc tạo một hệ thống song song.

### 1.1. Ranh giới phần cần làm

| Đã có, phải tái sử dụng | Phần cần ghép/sửa |
|---|---|
| Đọc/import dữ liệu, định dạng số đầu vào | Kiểm tra điều kiện toán học của phương pháp được chọn |
| Các trường tham số, nút chạy, cơ chế chọn phương pháp | Dựng bảng sai phân/tỷ sai phân, đa thức và phép lặp |
| Kiểu kết quả và luồng hiển thị hiện tại | Trả đủ dữ liệu trung gian và các bước lời giải |
| Bộ dựng bảng, công thức và thông báo lỗi | Nội dung bảng, công thức thay số và thông báo lỗi cụ thể |
| Chức năng xuất/in nếu đã có | Đưa đầy đủ lời giải nội suy ngược vào luồng xuất hiện tại |

Không tự thêm màn hình, nút hoặc tham số chỉ vì guide có nhắc tới một đại lượng. Đại lượng suy ra được thì tự tính và trình bày. Tùy chọn kỹ thuật chưa có trên UI có thể dùng cấu hình nội bộ công khai trong kết quả; nếu không hỗ trợ chức năng tùy chọn thì trả trạng thái rõ, không bịa dữ kiện.

Luồng tích hợp: **đầu vào đã import → bộ chuyển đổi mỏng nếu cần → thuật toán và kiểm tra → kết quả/lịch sử/thông báo → bộ dựng lời giải hiện có**.

### 1.2. Người dùng lựa chọn và chủ động chạy

**Quy tắc ưu tiên của module:** người dùng chọn phương pháp, khoảng/nhánh, tập mốc, bậc và tham số qua chương trình hiện có, sau đó chủ động bấm chạy. Module tính đúng cấu hình ấy; trả các bước, số liệu kiểm tra và thông báo để người dùng đánh giá, rồi người dùng quyết định thay đổi và chạy lại.

- Không tự chọn phương pháp hoặc coi một phương pháp là tối ưu rồi chạy thay người dùng.
- Không tự chọn khoảng đầu tiên, chọn nhánh, mở rộng tập mốc, đổi bậc, đổi gốc hoặc đổi chế độ dừng.
- Quét khoảng nghiệm và tách nhánh là chức năng khảo sát, chỉ trình bày các ứng viên; không tự giải các ứng viên đó. Kiểm tra điều kiện trong một lượt giải vẫn thực hiện trên cấu hình người dùng đã chọn.
- Được tự tính **đại lượng suy ra** từ lựa chọn: h, gốc được quy định bởi chiều và khoảng, bảng hệ số, t0 mặc định theo công thức, các giá trị lặp, phần dư và cận có căn cứ. Không coi việc tính các đại lượng này là quyền thay lựa chọn.
- Một lần bấm chạy có thể thực hiện hết các vòng lặp theo ngưỡng/số vòng đã chọn. Không yêu cầu bấm cho từng phép cộng hay từng vòng, trừ khi ứng dụng đã có chế độ chạy từng bước và người dùng chọn chế độ đó.
- Thiếu lựa chọn bắt buộc: trả thông tin còn thiếu qua luồng hiện tại, không tự điền một lựa chọn toán học. Dữ liệu/tập mốc người dùng đã chọn hoặc giá trị mặc định đã hiển thị trước khi bấm chạy được coi là lựa chọn của lượt ấy; không yêu cầu xác nhận lặp lại.
- Điều kiện tính không hợp lệ thì dừng có giải thích. Cảnh báo hoặc chưa chứng nhận được co không tự kích hoạt một cách giải khác. Người dùng đọc số liệu và quyết định thao tác tiếp theo.
- Sau thất bại, có thể hiển thị gợi ý bằng lời. Muốn chạy chia đôi hoặc phương pháp khác, người dùng phải chọn và khởi chạy **một lượt riêng**; không chạy fallback tự động.

Giữ một bản chụp cấu hình của mỗi lượt chạy trong kết quả để công thức/bảng luôn khớp với đúng lựa chọn lúc bấm chạy, kể cả khi người dùng đã đổi tham số trên màn hình sau đó.

## 2. Nguồn toán học và thứ tự ưu tiên

- PDF đồng hành: lý thuyết, dạng bài, ví dụ, ngôn ngữ trình bày và các hiệu chỉnh đã thống nhất.
- Slide của cô Hà Thị Ngọc Yến: `17_NoisuyNguoc_20261(4).pdf`, 9 trang. Trang 5: hàm ngược; 6–7: lặp tiến; 8–9: lặp lùi.
- Bản tổng hợp cũ: `MI3042_Chuong1_Hieu_chinh_va_bo_sung_ma_gia.pdf`, trang 18–20, 32, 43–45.

Các hiệu chỉnh bắt buộc:

- Mẫu số khởi đầu lùi là `∇y_(k+1) = y_(k+1) - y_k`, không phải `Δy_(k+1)`.
- Phân biệt `g=f^(-1)` với đa thức xấp xỉ `Q_m`.
- Mốc x đều không kéo theo mốc y đều. Bảng đảo mặc định dùng tỷ sai phân hoặc Lagrange.
- Bảng có các tung độ tăng không tự chứng minh hàm thật tăng giữa các mốc.
- Giải `P_m(x)=target_y` khác tính `Q_m(target_y)`.
- Không gọi phần dư hoặc sai khác bước là cận sai số vị trí khi chưa có căn cứ.

Nếu thấy mâu thuẫn giữa nguồn cũ và PDF/guide đã hiệu chỉnh, ghi nhận rõ trong phần mô tả thay đổi; không âm thầm khôi phục lỗi cũ.

## 3. Hợp đồng dữ liệu nhận từ chương trình hiện có

Bảng sau mô tả những thông tin thuật toán sử dụng, **không phải danh sách biểu mẫu cần xây thêm**. Trước hết lập bảng ánh xạ tên/đơn vị/giá trị mặc định với tham số hiện tại. Dùng các kiểm tra đầu vào chung của ứng dụng nếu đã có; chỉ bổ sung những kiểm tra toán học hoặc trường hợp còn thiếu.

### 3.1. Các trường

| Trường | Kiểu và yêu cầu | Nguồn/mặc định |
|---|---|---|
| `X`, `Y` | Hai danh sách số hữu hạn, cùng độ dài, ít nhất 2 cặp | Người dùng |
| `target_y` | Số hữu hạn | Người dùng |
| `method` | Một trong ba phương pháp chính; `bisection` là bổ sung | Người dùng |
| `degree` | Số nguyên >=1; không vượt số mốc được chọn trừ 1 | Phải hiển thị, không đoán ngầm |
| `inverse_form` | `divided_difference` hoặc `lagrange` | Mặc định tỷ sai phân |
| `branch_indices` | Dãy chỉ số của nhánh bảng, khi phương pháp cần nhánh | Lựa chọn của người dùng; khảo sát chỉ liệt kê ứng viên |
| `bracket_indices` | Cặp mốc liên tiếp chứa mức | Khoảng người dùng đã chọn, không lấy khoảng đầu tiên ngầm |
| `selected_indices` | Tập mốc đã chọn trong ứng dụng | Giữ đúng lựa chọn; không mở rộng hoặc thay bằng mốc gần hơn |
| `eps_x` | Số dương: ngưỡng theo hoành độ | Bắt buộc với phép giải lặp/chia đôi |
| `eps_y` | Số dương: ngưỡng phần dư | Mặc định công khai, ví dụ `1e-6` |
| `max_iter` | Số nguyên dương | Mặc định công khai `100` |
| `stop_mode` | `certified` hoặc `practical` | Hiển thị rõ |
| `display_digits` | Số chữ số thập phân thông thường | Mặc định 12 cho bảng trung gian |
| `equality_atol_y` | Dung sai coi tung độ gần mức | Mặc định `0`: chỉ bằng đúng dữ liệu |
| `grid_atol`, `grid_rtol` | Dung sai nhận biết lưới gần đều khi tính bằng float | Mặc định công khai, ví dụ `1e-12`, `1e-10` |
| `assumptions` | Liên tục/đơn điệu/đạo hàm do đề cho, trên đoạn nào | Thông tin người dùng cung cấp, không tự tạo |
| `error_data` | Cận E, μ, M và miền áp dụng, nếu đề cho | Tùy chọn; kèm xuất xứ |

Không cần bắt người học nhập những đại lượng chương trình tính được: `h`, gốc, sai phân, tỷ sai phân, `t0`, lịch sử lặp. Chúng là **kết quả của các bước**, phải được hiển thị.

`degree` phải được lấy từ tham số hoặc quy ước hiện có và hiển thị trong lời giải; không suy rằng mọi dữ liệu đều dùng hết mốc. Nếu chưa có thông tin bậc, trả thiếu tham số hoặc dùng mặc định đã được ứng dụng công bố. Nếu một lựa chọn thiếu mốc, báo đúng lỗi; không lén giảm bậc.

Nếu chương trình có sẵn cờ `allow_fallback`, không nối cờ này thành cơ chế tự đổi phương pháp của module nội suy ngược. Chia đôi là lượt chạy riêng theo lựa chọn mới của người dùng. Mọi kiểm tra và trạng thái trong guide phải tuân theo mục 1.2.

### 3.2. Kiểm tra dữ liệu

1. Từ chối danh sách khác độ dài, NaN, vô cực, số mốc không đủ.
2. Giữ ghép cặp X–Y. Nếu sắp tăng X, lưu ánh xạ chỉ số gốc và hiển thị việc sắp.
3. Hai x bằng nhau, y khác nhau: dữ liệu không biểu diễn một hàm đơn trị tại mốc đó.
4. Hai cặp hoàn toàn trùng nhau: cảnh báo; chỉ loại bản sao khi chính sách được hiển thị. Không gộp các mốc “gần nhau” chỉ vì dung sai lưới.
5. Các x quá gần làm mẫu số kém ổn định: cảnh báo cụ thể. Không tự làm tròn hoặc thay dữ liệu để tạo lưới đều.
6. Với lưới gần đều theo dung sai float, ghi `approximately_uniform` và độ lệch tối đa. Chứng nhận nghiêm ngặt phải nói rõ tính đối với mô hình lưới nào. Nếu độ lệch đáng kể, yêu cầu tỷ sai phân hoặc từ chối tiến/lùi đều.
7. Với dữ liệu thập phân nhập dưới dạng chuỗi, nên giữ chuỗi gốc để dựng biểu thức và có thể dùng Decimal/Fraction cho đối chiếu. Không bắt buộc biến mọi phép tính thành phân số khổng lồ.

### 3.3. Hiển thị lỗi: phải có lý do, số liệu và bước thất bại

Không để chia cho 0, NaN hoặc exception thoát ra thành trang trắng. Dùng cơ chế lỗi hiện tại để trả một kết quả có trạng thái, thông báo tiếng Việt, dữ liệu gây lỗi và các bước hợp lệ đã tính trước đó.

Mỗi lỗi/cảnh báo cần: **bước phát hiện → điều kiện bị vi phạm → chỉ số/giá trị cụ thể → hệ quả → hướng xử lý phù hợp**. Không chỉ hiện “Dữ liệu không hợp lệ”.

| Tình huống phải xử lý | Cách hiện cho người học | Xử lý của thuật toán |
|---|---|---|
| Hai dãy khác độ dài/không đủ cặp | “Có 4 hoành độ nhưng 3 tung độ; chưa ghép được các cặp.” | Dừng trước khi dựng bảng; tái sử dụng kiểm tra chung nếu có |
| NaN/vô cực hoặc dữ liệu không phải số lọt qua parser | Nêu hàng, cột và giá trị không hợp lệ | Dừng; không thay bằng 0 |
| Trùng x, khác y | Nêu hai hàng có cùng x và các y mâu thuẫn | Dừng dựng mô hình hàm tại tập mốc đó |
| Trùng y trong bảng đảo | Nêu hai cặp có cùng y nhưng khác x | Dừng hàm ngược trên tập mốc; đề xuất kiểm tra/tách nhánh |
| Các y rất gần nhau | Nêu hiệu tung độ và cảnh báo nhạy cảm/kém ổn định | Không gọi gần bằng là bằng đúng; giữ chính sách dung sai đã công bố |
| Mốc x không đều | In các bước h_i và độ lệch; nói công thức tiến/lùi đều không áp dụng | Từ chối đúng phương pháp này; không tự làm tròn mốc |
| Thiếu mốc về phía gốc đã chọn | Ví dụ “Tiến bậc 3 tại x_k cần 4 mốc từ x_k về phải, hiện chỉ có 3.” | Dừng; không lấy mốc bên trái để giả làm tiến tại cùng gốc |
| Chưa có khoảng đổi dấu | “Phép quét chưa tìm được khoảng đổi dấu ở mức này; chưa đủ dữ kiện kết luận hàm thật vô nghiệm.” | Trả kết quả khảo sát, không bịa một khoảng |
| Nhiều khoảng/nhánh | Liệt kê từng khoảng và chỉ rõ khoảng người dùng đã chọn | Chỉ giải khoảng đã chọn; nếu chưa chọn, trả cần lựa chọn, không tự chọn hoặc tự giải hết |
| Mức ngoài miền giá trị nhánh | In mức và khoảng tung độ nhánh; ghi ngoại suy ngược | Không tiếp tục nội suy thường; chỉ tính nếu ứng dụng đã cho phép ngoại suy |
| Sai phân cấp một bằng 0 | In Δy_k hoặc ∇y_(k+1) cùng phép trừ tạo ra nó | Dừng trước phép chia; đề xuất chọn lại mốc/phương pháp |
| t0 ngoài J | In t0, J, gốc và công thức đổi biến | Dừng cấu hình lặp đang kiểm soát; không ép t0 về biên |
| Chưa chứng nhận được tính co | In mục còn thiếu: bao ảnh, cận đạo hàm hoặc q<1 | Không kết luận phân kỳ chỉ từ việc thiếu chứng nhận; dùng đúng chế độ đã chọn |
| Giá trị mới rời J | In vòng, t_cũ, t_mới và J | Dừng lặp; giữ lịch sử và vòng thất bại |
| Tràn số/không hữu hạn khi tính sai phân, tỷ sai phân hoặc từng số hạng | Nêu bước, phép toán và các toán hạng đã biết | Dừng có kiểm soát tại nơi phát sinh, không chờ NaN lan đến kết quả |
| Lặp đình trệ hoặc đạt số vòng tối đa | In vòng cuối, sai khác, phần dư, cận nếu có và tiêu chuẩn chưa đạt | Trả chưa đạt; không tô thành công |
| Kết quả hàm ngược ngoài khoảng đang xét | In kết quả, khoảng và các mốc sử dụng | Giữ kết quả thô kèm cảnh báo, không cắt về đầu mút |
| Chia đôi không có hai đầu trái dấu | In F(a), F(b), đoạn và mức | Dừng chia đôi trên đoạn ấy; không tuyên bố đa thức không có nghiệm ở mọi nơi |
| Thiếu cận đạo hàm/sai số nội suy | “Chưa đủ dữ kiện chặn sai số với hàm thật.” | Vẫn có thể tính nghiệm mô hình; không dựng cận giả |

“Rất gần nhau” là cảnh báo số học, phải dựa trên thang dữ liệu và chính sách của ứng dụng; không dùng một ngưỡng tuyệt đối tùy tiện cho mọi đơn vị. Trường hợp thiếu chứng nhận hoặc thiếu cận hàm thật là **giới hạn kết luận**, không tự động là lỗi dữ liệu.

Ví dụ hiển thị khi lặp thất bại:

```text
Bước 7 — Vòng lặp 1 chưa hợp lệ
t_cũ = 0.5
t_mới = 0.5 - 3×0.5×(0.5-1) = 1.25
Đoạn đang kiểm soát: J=[0,1]. Giá trị 1.25 nằm ngoài J.
Phép lặp hiện tại dừng, chưa có kết quả đạt yêu cầu.
Nếu được phép đổi cách giải, có thể xét chia đôi cùng đa thức trên [0,1].
```

Không hiện thông báo lỗi của một phương pháp sang phương pháp khác: hàm ngược không có vòng lặp, và phần dư thuận khác 0 tại Q(target) không phải lỗi hội tụ của hàm ngược.

## 4. Khảo sát trước khi giải: mốc, khoảng và nhánh

### 4.1. Phát hiện nghiệm tại mốc và các khoảng đổi dấu

Quét mọi mốc, không dừng ở khoảng đầu tiên.

Đây là bước khảo sát khi người dùng yêu cầu hoặc là dữ liệu giải thích cho lượt chạy đã chọn; việc tìm được các khoảng không cho phép tự khởi chạy giải nghiệm. Nếu người dùng yêu cầu xử lý nhiều khoảng, phải dùng đúng danh sách đã chọn và báo riêng từng kết quả.

```text
sample_roots = []
near_level_samples = []
brackets = []

với i = 0 .. N-1:
    s[i] = Y[i] - target_y
    nếu s[i] == 0:
        ghi nghiệm tại mốc X[i]
    nếu 0 < abs(s[i]) <= equality_atol_y:
        ghi mốc gần mức, kèm phần dư abs(s[i])
        không gọi đây là nghiệm chính xác

với i = 0 .. N-2:
    nếu s[i] và s[i+1] trái dấu nghiêm ngặt:
        ghi khoảng [X[i], X[i+1]]
    nếu cả hai bằng 0:
        ghi hai mốc nghiệm và đoạn bằng mức trên dữ liệu
```

So dấu trực tiếp; không bắt buộc nhân hai số lớn vì có thể tràn. Một đầu bằng đúng mức thì không ghi thêm khoảng đổi dấu nghiêm ngặt cạnh đầu ấy; nghiệm tại mốc được ghi một lần.

Hai đầu cùng mức chỉ tạo cả đoạn nghiệm đối với **mô hình tuyến tính hằng** trên đoạn đó. Không suy ra hàm thật hằng.

Thông điệp bắt buộc: “Nếu hàm thật liên tục, mỗi khoảng đổi dấu có ít nhất một nghiệm. Phép quét chưa bảo đảm tìm tất cả nghiệm, đặc biệt nghiệm tiếp xúc.”

### 4.2. Tách nhánh trên bảng

Theo dấu hiệu `Y[i+1]-Y[i]`. Khi dấu đổi, điểm chuyển hướng là đầu mút chung của hai nhánh. Hiệu bằng 0 được xử lý riêng thành đoạn phẳng trên mẫu; không cho qua bộ nội suy hàm ngược có tung độ phân biệt.

Ví dụ bắt buộc:

```text
Y = [0, 2, 1, 1, 3]
Nhánh chỉ số: [0,1], [1,2], [3,4]
Đoạn phẳng trên mẫu: [2,3]
```

Không sắp cả bảng theo Y để che việc không đơn điệu. Chỉ được sắp các cặp theo Y **bên trong nhánh đã chọn**, giữ ghép cặp và ánh xạ chỉ số.

Nhánh đơn điệu trên bảng là phát hiện số liệu; tính đơn điệu của hàm thật phải đến từ giả thiết đề hoặc chứng minh riêng.

### 4.3. Kiểm tra tập mốc người dùng đã chọn

- Nhận đúng tập mốc, nhánh, khoảng và bậc từ lựa chọn hiện có. Hiển thị lại tập ấy và kiểm tra; không tự thay bằng một tập được cho là tốt hơn.
- Hàm ngược: tập `degree+1` mốc phải thuộc nhánh đã chọn, có tung độ phân biệt. Hướng dẫn “ưu tiên các tung độ gần và bao quanh mức” là tiêu chí để người dùng đánh giá, không phải thuật toán tự lấy/thay mốc. Không tự mở rộng qua biên nhánh.
- Tiến từ khoảng `[x_k,x_(k+1)]`: gốc suy ra là `x_k`; kiểm tra các mốc người dùng chọn có đúng `[k, k+1, ..., k+degree]`, tồn tại và liên tiếp không.
- Lùi từ cùng khoảng: gốc suy ra là `x_(k+1)`; kiểm tra tập mốc có đúng `[k+1-degree, ..., k+1]`, tồn tại và liên tiếp không.
- Không đủ mốc: `insufficient_nodes`. Có thể đề xuất đổi chiều/giảm bậc, nhưng không tự làm nếu người dùng chưa chọn.
- Mốc tiến/lùi không nhất thiết có cùng tập hợp, nên không bắt hai kết quả phải trùng. Dùng chung tập mốc đủ bậc thì hai biểu diễn thuận là cùng đa thức.
- Nếu mở rộng tiến/lùi qua chỗ dữ liệu đổi chiều, nêu rõ. Không tự gọi đó là một nhánh khả nghịch. Muốn giải mô hình trên khoảng vẫn phải kiểm soát nghiệm/hội tụ; giả thiết hàm thật chỉ áp dụng đúng đoạn được cho.

## 5. Các mô-đun tính toán và bảng hệ số

Tách phần toán khỏi phần xuất báo cáo. Một kết quả tính duy nhất cung cấp dữ liệu cho giao diện, công thức và file xuất; không tính lại bằng thuật toán khác trong bộ dựng lời giải.

Gợi ý hàm:

```text
validate_input
scan_level
split_sample_branches
validate_selected_stencil
build_forward_difference_table
build_divided_difference_table
build_inverse_model
build_uniform_newton_model
certify_iteration
iterate_model
bisect_model
build_solution_report
```

### 5.1. Sai phân đều

Với bảng con có M mốc theo x tăng:

```text
D[i,0] = y[i]
với r = 1 .. M-1:
    với i = 0 .. M-r-1:
        D[i,r] = D[i+1,r-1] - D[i,r-1]
```

Tiến: `c[r] = D[0,r]`.

Lùi: `c[r] = D[M-1-r,r]`. Đặc biệt `c[1]=y[M-1]-y[M-2]`; **không phải `D[0,1]` nếu bảng dài hơn hai mốc**.

Bảng tam giác hiển thị các ô không tồn tại bằng ô trống; số 0 thật vẫn hiển thị là 0.

### 5.2. Tỷ sai phân của bảng đảo

Đặt `U = Y_selected`, `V = X_selected`:

```text
T[i,0] = V[i]
với r = 1 .. M-1:
    với i = 0 .. M-r-1:
        denominator = U[i+r] - U[i]
        nếu denominator == 0: báo duplicate_inverse_node
        T[i,r] = (T[i+1,r-1] - T[i,r-1]) / denominator
c[r] = T[0,r]
```

Phải lưu phép trừ, mẫu số và kết quả mỗi ô để có thể mở xem chi tiết.

Đánh giá Newton bằng nhân lồng:

```text
value = c[m]
với r = m-1 giảm tới 0:
    value = c[r] + (target_y - U[r]) * value
```

Giữ đúng thứ tự U đi cùng c; không dựng hệ số một thứ tự rồi đánh giá thứ tự khác.

## 6. Phương pháp hàm ngược

### 6.1. Kết quả toán học

Trên nhánh khả nghịch, `g=f^(-1)`. Dựng `Q_m` từ các cặp `(y_i,x_i)` rồi trả:

```text
x_hat = Q_m(target_y)
```

Với ba mốc:

\[
Q_2(y)=x_0+c_1(y-y_0)+c_2(y-y_0)(y-y_1).
\]

Nếu dùng Lagrange, lưu cho từng i các nhân tử, mẫu số, `L_i(target_y)` và đóng góp `x_i*L_i(target_y)`. Hiển thị tổng các đóng góp. Nếu dùng Newton, xuất bảng tỷ sai phân và dạng nhân lồng bên cạnh công thức khai triển theo cơ sở Newton; không buộc khai triển thành lũy thừa y nếu không cần.

### 6.2. Báo cáo bắt buộc

1. Khoảng/nhánh, mức và các mốc.
2. Bảng trước và sau khi đảo.
3. Khoảng giữa các tung độ, giải thích có/không cách đều.
4. Bảng tỷ sai phân hoặc các cơ sở Lagrange.
5. Công thức ký hiệu, công thức thay hệ số và phép thay `y=target_y`.
6. `x_hat`, kiểm tra nằm trong khoảng/nhánh, cận sai số nếu có dữ kiện.
7. Nếu đánh giá thêm đa thức thuận: ghi rõ phần dư thuận chỉ là đối chiếu giữa mô hình, **không ép nó về 0 và không báo hàm ngược thất bại chỉ vì phần dư này khác 0**.

Không có lịch sử lặp; không tạo bảng các “vòng” giả. Nếu `x_hat` ngoài khoảng đang giải, giữ kết quả thô để chẩn đoán và trả cảnh báo hoặc trạng thái `outside_bracket`; không tự cắt về đầu mút.

Nếu `target_y` ngoài miền tung độ của nhánh: báo `inverse_extrapolation`. Chỉ tính ngoại suy nếu được bật rõ, kèm nhãn; không gọi là nội suy thông thường.

### 6.3. Sai số

Khi biết `M_(m+1)` chặn đạo hàm của hàm ngược trên miền đúng:

\[
|x_{\rm thật}-Q_m(Y^*)|
\le \frac{M_{m+1}}{(m+1)!}\left|\prod_{i=0}^m(Y^*-y_i)\right|.
\]

Nếu không biết M, để cận là `null`, giải thích thiếu dữ kiện. Không suy cận nghiêm ngặt từ số hạng cuối một cách tự động.

## 7. Phép lặp Newton tiến và Newton lùi

### 7.1. Mô hình và cơ sở tính theo bậc bất kỳ

Gọi `a` là gốc, `h>0`, `c[r]` là sai phân cấp r tại gốc đã chọn. Đặt `x=a+h*t`.

**Tiến**: `a=x_k`, `J=[0,1]`, nhân tử cấp r:

\[
B_r(t)=\frac{t(t-1)\cdots(t-r+1)}{r!}.
\]

**Lùi**: `a=x_(k+1)`, `J=[-1,0]`, nhân tử cấp r:

\[
B_r(t)=\frac{t(t+1)\cdots(t+r-1)}{r!}.
\]

Cả hai: `p(t)=c[0]+Σ c[r]*B_r(t)` và `c[1] != 0`.

Với bậc 3, báo cáo phải viết đủ:

\[
p_{\rm tiến}(t)=c_0+c_1t+\frac{c_2}{2}t(t-1)+\frac{c_3}{6}t(t-1)(t-2),
\]

\[
p_{\rm lùi}(t)=c_0+c_1t+\frac{c_2}{2}t(t+1)+\frac{c_3}{6}t(t+1)(t+2).
\]

Công thức chung dùng trong bộ tính:

```text
term[r](t) = c[r] * B_r(t), r>=2
high_sum(t) = tổng term[r](t) từ r=2 đến degree
Phi(t) = (target_y - c[0] - high_sum(t)) / c[1]
t0 = (target_y - c[0]) / c[1]
```

`high_sum` chỉ là cấu trúc nội bộ. Báo cáo phải xuất các số hạng cụ thể; không thay toàn bộ phần giải thích bằng một ký hiệu H(t) chưa khai triển.

Đánh giá cơ sở bằng truy hồi để tránh viết cứng bậc 3:

```text
basis = 1
với r = 1 .. degree:
    tiến: basis *= (t - (r-1)) / r
    lùi:  basis *= (t + (r-1)) / r
    term[r] = c[r] * basis
```

Đạo hàm có thể tính bằng hệ số đa thức đã dựng từ các cơ sở. Các hệ số lũy thừa và các sai phân là hai loại khác nhau, phải đặt tên rõ.

### 7.2. Chứng nhận hội tụ

Để gắn nhãn `certified_model_convergence`, phải có đủ:

1. `t0` thuộc đoạn đóng J.
2. Chứng minh `Phi(J) ⊆ J`.
3. Cận bảo đảm `abs(Phi'(t)) <= q < 1` trên cả J.

Mỗi mục lưu `verified / not_verified / disproved`, cách kiểm tra, miền và phép chặn. `not_verified` không đồng nghĩa phương pháp chắc chắn phân kỳ.

Các cách chấp nhận được:

- Phân tích dấu/tính đơn điệu của đạo hàm đa thức, kiểm tra đầu mút và điểm cực trị, kèm phép chặn có căn cứ.
- Số học khoảng có làm tròn ra ngoài, hoặc số học hữu tỷ, có thể chia nhỏ J rồi hợp các khoảng bao.
- Cận do đề cung cấp có miền và xuất xứ rõ; gắn nhãn “theo giả thiết đề”, không giả vờ chương trình đã chứng minh độc lập.

Không lấy max từ một lưới mẫu float rồi gọi đó là cận nghiêm ngặt. Nếu dùng khảo sát số gần đúng, đặt `estimated_q` và để `certified_q=null`. Tìm nghiệm đạo hàm gần đúng cũng chưa tự tạo chứng nhận nghiêm ngặt nếu không có kiểm soát sai số.

Nếu phép chặn thô cho q>=1, chỉ kết luận **chưa chứng nhận bằng phép chặn này**. Chỉ khẳng định vi phạm tính co nếu có lập luận/cận dưới phản ví dụ đủ rõ.

Giá trị q không nhất thiết tối ưu. Nếu dùng q lớn hơn nhưng vẫn hợp lệ, cận sai số và số vòng có thể khác ví dụ; báo cáo phải dùng nhất quán q đã chọn. Các bảng tham chiếu trong PDF dùng q cụ thể nêu trong từng bài.

### 7.3. Pseudocode vòng lặp

```text
kiểm tra c[1] != 0
t = (target_y - c[0]) / c[1]
kiểm tra t hữu hạn và thuộc J
certificate = certify_iteration(Phi, J, t)

nếu stop_mode == certified và certificate chưa đủ:
    trả certification_unavailable, kèm các kiểm tra và lý do
    không tự chuyển sang practical

nếu degree == 1:
    x_hat = a + h*t
    kiểm tra phần dư trong số học sử dụng
    trả nghiệm mô hình tuyến tính, không tạo các vòng giả

history = []
với iteration = 1 .. max_iter:
    old = t
    contributions = từng term[r](old), r=2..degree
    high_sum = tổng các contributions
    numerator = target_y - c[0] - high_sum
    new = numerator / c[1]

    nếu new không hữu hạn:
        trả nonfinite_iteration, kèm lịch sử và vòng thất bại
    nếu new ngoài J:
        trả left_iteration_interval, kèm giá trị và đoạn J
        không ép new về biên

    x_new = a + h*new
    delta_t = abs(new-old)
    step_x = h*delta_t
    p_new = đánh giá cùng đa thức p tại new
    residual_y = abs(p_new-target_y)

    nếu có chứng nhận đầy đủ với q:
        bound_x = h*q/(1-q)*delta_t
        position_ok = bound_x <= eps_x
    nếu không:
        bound_x = null
        position_ok = step_x <= eps_x

    residual_ok = residual_y <= eps_y
    lưu tất cả giá trị của vòng và hai cờ đạt/chưa đạt

    nếu position_ok và residual_ok:
        status = certified_model_tolerance nếu có chứng nhận
                 practical_stop nếu không có chứng nhận
        trả x_new, history, status và phạm vi kết luận

    nếu new == old nhưng chưa đạt tiêu chuẩn:
        trả numerical_stagnation, kèm phần dư

    t = new

trả max_iter_reached, lưu bước cuối để chẩn đoán
không gắn nhãn đã đạt nghiệm yêu cầu
```

`certified_model_tolerance` trong số học float thông thường biểu thị chứng nhận toán học của mô hình và tiêu chuẩn lặp; báo cáo phải ghi giới hạn rằng chưa bao gồm một chứng nhận toàn bộ sai số số học máy nếu bộ tính không dùng interval/độ chính xác có kiểm soát. Không tuyên bố một mức bảo đảm máy tính mạnh hơn thực tế.

Không tự chạy fallback. Giữ kết quả/lịch sử thất bại, hiển thị lý do và có thể nêu phương án người dùng cân nhắc. Chỉ chạy chia đôi ở một lượt riêng sau khi người dùng chọn phương pháp đó và bấm chạy.

### 7.4. Thông tin từng vòng phải lưu

```text
iteration, t_old
basis_factors[]          # ví dụ [t_old,t_old-1,t_old-2]
factorial_denominators[]
term_contributions[]     # cả dấu, hệ số và giá trị
high_sum, numerator, denominator
t_new, x_new, delta_t, step_x
p_at_new, residual_y
q_used, error_bound_x    # null nếu không được chứng nhận
position_ok, residual_ok, status
```

Phải có thể mở từng vòng xem phép thay số. Trong màn hình chính có thể chỉ mở sẵn vòng đầu và vòng dừng; xuất bản đầy đủ thì phải có tùy chọn đưa tất cả vòng vào.

## 8. Chia đôi mô hình: bổ sung có kiểm soát

Dùng đúng đa thức P đã chọn, không âm thầm dựng lại đa thức khác. Gọi F(x)=P(x)-target_y.

1. Kiểm tra nghiệm đầu mút và dấu hai đầu.
2. Nếu không có đầu nghiệm và hai đầu cùng dấu, trả `no_model_sign_change`.
3. Trong khi nửa độ rộng lớn hơn eps_x, chia tại trung điểm và giữ nửa trái dấu.
4. Xuất mỗi lần chia: a,b,c,F(a),F(c),F(b), dấu, khoảng mới, nửa độ rộng.
5. Trả trung điểm **của khoảng cuối** và cận nửa độ rộng.

Điều kiện dừng vị trí của chia đôi không cần đồng thời đạt eps_y trừ khi người dùng yêu cầu bổ sung rõ. Đừng gắn sai ngưỡng phần dư quá chặt khiến một bài vốn đạt eps_x bị báo thất bại vô cớ; nếu yêu cầu cả hai, ghi tường minh và tiếp tục chia hoặc báo giới hạn số học.

Chứng nhận là tồn tại ít nhất một nghiệm mô hình trong khoảng được giữ; không tự kết luận nghiệm duy nhất.

## 9. Hợp đồng kết quả và các trạng thái

Kết quả nên gồm ba phần độc lập: dữ liệu đầu vào chuẩn hóa; dữ liệu tính toán có cấu trúc; mô hình báo cáo. Không trộn chuỗi LaTeX vào con số dùng cho tính tiếp.

Ví dụ schema khái quát:

```json
{
  "method": "forward_iteration",
  "status": "certified_model_tolerance",
  "input": {},
  "assumptions": [],
  "sample_scan": {"sample_roots": [], "brackets": [], "branches": []},
  "selection": {"indices": [], "degree": 3, "anchor": 1.2, "h": 0.2},
  "model": {"variable": "t", "basis": "forward", "difference_coefficients": []},
  "iteration": {"J": [0, 1], "t0": null, "certificate": {}, "history": []},
  "result": {
    "x_hat": null,
    "residual_y": null,
    "iteration_error_bound_x": null,
    "true_function_error_bound_x": null,
    "rounding_error_bound_x": null,
    "scope": "forward_interpolant_root"
  },
  "warnings": [],
  "report_steps": []
}
```

Schema này minh họa cấu trúc; các giá trị null sẽ được tính khi chạy. Với hàm ngược, `scope=inverse_interpolant_value`, không cố điền các trường lặp.

Các trạng thái tối thiểu cần phân biệt:

| Trạng thái | Ý nghĩa |
|---|---|
| `exact_sample_match` | Đúng mức tại một mốc dữ liệu |
| `near_level_sample` | Gần mức theo dung sai, kèm phần dư |
| `inverse_value_computed` | Đã tính Q(target), không phải đã chứng minh sai số hàm thật |
| `certified_model_tolerance` | Đạt cận vị trí mô hình và ngưỡng phần dư đã quy định |
| `practical_stop` | Đạt tiêu chuẩn thực hành, chưa có cận bảo đảm |
| `certification_unavailable` | Chưa chứng nhận co trong chế độ yêu cầu bảo đảm |
| `selection_required` | Chưa có lựa chọn phương pháp/khoảng/nhánh/tập mốc bắt buộc; không tự điền |
| `insufficient_nodes` / `nonuniform_grid` | Không đủ điều kiện dựng công thức đã chọn |
| `duplicate_inverse_node` | Tung độ lặp trong bảng đảo |
| `outside_bracket` / `inverse_extrapolation` | Kết quả ra ngoài khoảng hoặc mức ngoài nhánh |
| `left_iteration_interval` / `nonfinite_iteration` | Phép lặp vi phạm miền hoặc giá trị không hữu hạn |
| `max_iter_reached` / `numerical_stagnation` | Chưa đạt yêu cầu |

Chuyển các mã kỹ thuật thành câu tiếng Việt ở giao diện người học. Không hiện raw JSON hoặc stack trace trong lời giải toán thông thường.

## 10. Quy định về sai số và chữ số

### 10.1. Lặp

Sau khi có t_new:

\[
B_x=h\frac{q}{1-q}|t_{\rm new}-t_{\rm old}|.
\]

Không dùng `1/(1-q)` rồi ghi đó là cận theo công thức hậu nghiệm mới nhất; hệ số đúng với sai khác cặp đang dùng là `q/(1-q)`.

Nếu không có q hợp lệ: `error_bound_x=null`; `step_x` vẫn được hiển thị nhưng ghi “sai khác bước”.

### 10.2. Cận hàm thật

Nếu đề cho `|f-P|<=E`, `|f'|>=mu>0` trên đúng đoạn chứa điểm tính và nghiệm thật:

\[
|x_{\rm hat}-x_{\rm thật}|\le\frac{E+|P(x_{\rm hat})-Y^*|}{\mu}.
\]

Phải hiển thị E, mu, miền áp dụng và nguồn. Thiếu một điều kiện thì không tự xuất cận này. Với hàm ngược, dùng công thức sai số của Q theo biến y nếu có cận đạo hàm g.

### 10.3. Làm tròn

Không cập nhật vòng lặp bằng số đã làm tròn để in. Khi in d chữ số sau dấu chấm, cộng cận làm tròn `0.5*10^(-d)` vào cận cần phát biểu cho số được in, hoặc in thêm chữ số để còn dư ngân sách sai số.

Phần dư nhỏ như `3.15945e-10` phải hiện bằng dạng khoa học, không hiện `0.000000` làm người đọc tưởng bằng 0 chính xác. Ngưỡng dừng và các cờ đạt/chưa đạt dùng số nội bộ, không dùng chuỗi hiển thị.

## 11. Ghép phần xuất lời giải vào bộ dựng hiện có

Các yêu cầu dưới đây quy định **nội dung và định dạng kết quả nội suy ngược**, không yêu cầu dựng giao diện mới. Tái sử dụng bảng, công thức, khối thông báo và chức năng xuất hiện tại. Nếu ứng dụng chỉ xuất văn bản/HTML/PDF, trình bày qua đúng luồng ấy, không bổ sung màn hình hay framework.

### 11.1. Thứ tự các khối lời giải

1. **Đề bài và thông số đã chọn**: bảng dữ liệu, mức, bậc, phương pháp, eps_x/eps_y; lấy từ bản chụp cấu hình của lượt chạy.
2. **Ý tưởng**: 2–4 câu nói đang đảo bảng hay giải đa thức thuận và vì sao chọn chiều.
3. **Khoảng/nhánh và mốc người dùng đã chọn**: bất đẳng thức tung độ, khoảng, giả thiết và các mốc; trình bày kết quả kiểm tra lựa chọn, không tự thay nó.
4. **Bảng hệ số**: sai phân hoặc tỷ sai phân, làm nổi các ô thực sự được dùng.
5. **Công thức**: ký hiệu → thay hệ số → phương trình hoặc phép lặp cụ thể; mỗi công thức ở dòng riêng.
6. **Giá trị đầu và hội tụ**: t0, J, cận q cùng lý do hoặc nhãn chưa chứng nhận.
7. **Quá trình tính**: minh họa thay số; bảng vòng lặp. Nếu đã có cơ chế mở chi tiết, đưa dữ liệu vào đó; nếu không, xuất các bước dưới bảng hoặc trong bản đầy đủ, không bắt xây nút mới.
8. **Kiểm tra dừng**: hai bất đẳng thức, số cụ thể, đạt/chưa đạt; chỉ rõ vì sao dừng ở vòng này.
9. **Kết luận**: x, khoảng phù hợp, số vòng, sai số, phạm vi mô hình/hàm thật.

Với hàm ngược, bỏ các khối lặp không áp dụng và thay bằng phép đánh giá Q(target).

### 11.2. Các thông số phải nhìn thấy được

| Nhóm | Phải hiện |
|---|---|
| Đầu vào | X,Y,target,bậc,phương pháp,ngưỡng,số vòng tối đa |
| Chọn dữ liệu | Khoảng,nhánh,chỉ số,các cặp được dùng và lý do chọn |
| Dựng mô hình | Gốc,h,các hệ số,mẫu giai thừa,đổi biến,J |
| Khởi tạo | Tử,mẫu,t0,x0 và kiểm tra t0 thuộc J |
| Hội tụ | Bao ảnh Phi(J),cận đạo hàm,q,cách chứng nhận |
| Từng vòng | Giá trị cũ,các số hạng cấp cao,tử,mẫu,giá trị mới,x,phần dư,sai khác,cận |
| Kết thúc | Điều kiện nào đạt,số vòng,kết quả,làm tròn,loại sai số |

### 11.3. Bố cục

- Font tiếng Việt rõ; công thức render bằng bộ dựng toán sẵn có của dự án, không để lộ chuỗi LaTeX chưa render.
- Tiêu đề và số bước nhất quán với PDF. Dùng màu nhấn tiết chế, đủ tương phản khi in đen trắng.
- Bảng có tiêu đề, đơn vị/ý nghĩa đại lượng; số canh phải hoặc thẳng dấu thập phân.
- Nếu bảng quá rộng: tách bảng `t,x` và bảng kiểm tra sai số; không thu nhỏ toàn bộ chữ đến khó đọc.
- Dòng t_old → đóng góp cấp cao → t_new phải truy vết được. Không chỉ đưa một bảng số cuối mà giấu công thức.
- Không nhét nội dung kỹ thuật như schema, tên hàm, mã trạng thái vào luồng người học. Giữ chúng cho chế độ debug/xuất máy.
- Khi xuất PDF/HTML để in: không cắt công thức ngang trang, lặp tiêu đề bảng dài, giữ lời giải đầy đủ ngay cả khi UI có khối thu gọn.
- Khối kết quả không chỉ tô “thành công” mà phải có câu kết luận tiếng Việt về ý nghĩa và độ chính xác.

## 12. Các bộ dữ liệu nghiệm thu

Các cấu hình dưới đây là lựa chọn tường minh của người dùng trong ca kiểm thử, không phải lựa chọn mà module được tự suy đoán. Chỉ số bắt đầu từ 0.

| Bộ | Tập mốc người dùng chọn | Khoảng/nhánh người dùng chọn |
|---|---|---|
| A | `[0,1,2]` | Nhánh `[0,2]`, khoảng `[0,1]` |
| B | `[0,1,2,3]` | Nhánh `[0,3]`, khoảng `[0,1]` |
| C | `[0,1,2,3]` | Nhánh `[0,3]`, khoảng `[2,3]` |
| D | Cả bảng để khảo sát | Chỉ quét, không tự giải; kết quả bậc 1 chỉ kiểm tra sau khi người dùng chọn riêng từng khoảng |
| E | `[0,1,2]` | Khoảng `[0,1]`, phương pháp tiến bậc 2 |
| F | Đa thức thuận đã chỉ định | Đoạn giá trị x `[1,2]`, chọn chia đôi trong một lượt riêng |

### A. Hàm ngược bậc 2

```text
X=[1,1.5,2]
Y=[2,3.75,6]
target_y=3
degree=2
method=inverse_function
```

Kỳ vọng:

- Khoảng mức chọn: x thuộc (1,1.5); bảng đảo dùng cả 3 mốc.
- Tỷ sai phân cấp một: `2/7`, `2/9`; cấp hai `-1/63`.
- `Q(y)=1+(2/7)(y-2)-(1/63)(y-2)(y-3.75)`.
- `Q(3)=109/84≈1.297619047619`.
- Lagrange tại mức có trọng số `[9/28,16/21,-1/12]`; cùng kết quả.
- Đa thức thuận `P(x)=x²+x` có nghiệm mức 3 là `(-1+sqrt(13))/2≈1.302775637732`, khác Q(3).
- Phần dư thuận tại Q(3) là `-131/7056≈-0.0185657596372`. Không báo lỗi hội tụ.

### B. Newton tiến bậc 3 – bảng chuẩn giống PDF

```text
X=[1.2,1.4,1.6,1.8]
Y=[1.728,2.744,4.096,5.832]
target_y=2.2
degree=3
method=forward_iteration
eps_x=eps_y=1e-6
max_iter=100
```

Hệ số: `[1.728,1.016,0.336,0.048]`; gốc 1.2; h=0.2; J=[0,1].

```text
p(t)=1.728+1.016t+0.168t(t-1)+0.008t(t-1)(t-2)
Phi(t)=(0.472-0.168t(t-1)-0.008t(t-1)(t-2))/1.016
t0=0.464566929133858...
q=20/127
Phi(J) nằm trong [0.468/1.016,0.514/1.016] thuộc J
```

| Vòng | t_new | x_new | B_x với q=20/127 | residual_y |
|---|---:|---:|---:|---:|
| 1 | 0.502690582044 | 1.300538116409 | 1.42518328637e-3 | 2.70620331089e-4 |
| 2 | 0.502956940638 | 1.300591388128 | 9.95733060156e-6 | 2.98000650093e-7 |
| 3 | 0.502957233946 | 1.300591446789 | 1.09647748213e-8 | 3.15944894219e-10 |

Phải giải thích vòng 2 chưa đạt eps_x dù phần dư đã đạt. Nếu dùng cận co khác hợp lệ, ghi q đó; không giả mạo B để ép khớp bảng tham chiếu. Trong chế độ tái hiện bài PDF phải dùng chứng nhận q nêu trên.

Chi tiết vòng đầu phải thấy:

```text
term2=-0.041789075578151...
term3= 0.003055444221125...
t1=(0.472-term2-term3)/1.016
```

Các chữ số cuối hai term phải tính lại từ t0 đầy đủ; số hiển thị có thể ít hơn. Kết quả cuối `1.300591447` khi làm tròn 9 chữ số.

### C. Newton lùi bậc 3

```text
X=[1,1.2,1.4,1.6]
Y=[1,1.728,2.744,4.096]
target_y=3.5
degree=3
method=backward_iteration
eps_x=eps_y=1e-6
```

Hệ số lùi: `[4.096,1.352,0.336,0.048]`; gốc 1.6; h=0.2; J=[-1,0].

```text
p(t)=4.096+1.352t+0.168t(t+1)+0.008t(t+1)(t+2)
Psi(t)=(-0.596-0.168t(t+1)-0.008t(t+1)(t+2))/1.352
t0=-0.440828402366864...
q=23/169
Psi(J) nằm trong [-0.596/1.352,-0.550/1.352] thuộc J
```

| Vòng | t_new | x_new | B_x với q=23/169 | residual_y |
|---|---:|---:|---:|---:|
| 1 | -0.407924219119 | 1.518415156176 | 1.03670714344e-3 | 8.34579996846e-4 |
| 2 | -0.408541512016 | 1.518291697597 | 1.94489542914e-5 | 1.92831672034e-5 |
| 3 | -0.408527249318 | 1.518294550136 | 4.49372665234e-7 | 4.43975042499e-7 |

Kết quả in: `1.518294550`. Không được lấy `0.728` làm hệ số tuyến tính tại gốc phải.

### D. Bảng của cô: nhiều khoảng ở mức 4

```text
X=[1.2,1.4,1.6,1.8,2.0,2.2,2.4,2.6,2.8]
Y=[4.02,3.98,4.23,3.67,2.99,1.24,0.87,2.08,4.54]
target_y=4
```

Khoảng đổi dấu: `(1.2,1.4)`, `(1.4,1.6)`, `(1.6,1.8)`, `(2.6,2.8)`.

Nhánh trên mẫu: `[1.2,1.4]` giảm; `[1.4,1.6]` tăng; `[1.6,2.4]` giảm; `[2.4,2.8]` tăng.

Nếu giải bậc 1 từng khoảng: `1.3`, `1.416`, `1.682142857143`, `2.756097560976`. Không báo tất cả là nghiệm thật chính xác.

### E. Phép lặp không phù hợp

```text
X=[0,1,2]
Y=[0,1,8]
target_y=0.5
degree=2
method=forward_iteration
```

`p(t)=3t²-2t`; `Phi(t)=0.5-3t(t-1)`; t0=0.5; t1=1.25 ngoài [0,1].

Chế độ practical: báo rời đoạn ngay vòng 1. Chế độ certified: báo không có chứng nhận trước khi chạy. Không dùng kết quả một phương pháp khác và gọi lặp thành công.

Không tự chạy chia đôi sau thất bại. Nếu người dùng chọn chia đôi cùng mô hình trên [0,1] ở lượt chạy riêng, nghiệm khoảng `0.860379610028`; lưu phương pháp và kết quả của hai lượt tách biệt.

### F. Chia đôi

`P(x)=x²`, mức 2, đoạn [1,2], eps_x=1e-3. Sau 9 lần chia, khoảng `[1.4140625,1.416015625]`; trung điểm `1.4150390625`; cận `0.0009765625`.

### G. Kiểm tra biên và tính trung thực

- `X=[0,1,2,3], Y=[1,-1,0,2], target=0`: nghiệm tại mốc x=2; chỉ khoảng đổi dấu nghiêm ngặt (0,1), không thêm (1,2).
- `X=[0,2], Y=[1,1], target=0`: không có khoảng đổi dấu; không tuyên bố hàm thật vô nghiệm. Nếu hàm thật là (x-1)² thì có nghiệm x=1.
- `X=[-1,0,1],Y=[1,0,1]`: không đảo cả bảng thành một hàm ngược; tách hai nhánh.
- Dữ liệu `[1,1.2,1.4]`, Y `[1,1.44,1.96]`, mức 1.5, yêu cầu tiến bậc 2 tại đầu trái khoảng: báo thiếu mốc 1.6. Lùi bậc 2 tại 1.4 là lựa chọn khác hợp lệ nếu được chọn.
- Không đều thật sự: tiến/lùi từ chối. Hàm ngược bằng tỷ sai phân là lựa chọn khác có thể áp dụng trên nhánh hợp lệ, chỉ chạy sau khi người dùng đã chọn nó.
- eps_x/eps_y<=0, max_iter không nguyên dương: lỗi đầu vào cụ thể.
- max_iter=1 cho ví dụ B: lưu vòng đầu và báo chưa đạt, không tô thành công.

## 13. Kiểm thử và điều kiện hoàn thành

Chạy kiểm thử có ý nghĩa cho các bộ A–G; so sánh số trong dung sai phù hợp. Không buộc chuỗi số float khớp từng ký tự. Dùng dữ liệu chính xác hoặc tính độc lập độ chính xác cao làm đối chiếu.

Các kiểm tra toán cần có:

- P tại các mốc phải khớp Y trong dung sai số học.
- Q tại các mốc đảo phải khớp X.
- Cùng tập mốc, Newton thuận tiến và lùi phải đánh giá cùng đa thức; chỉ khác cơ sở biểu diễn.
- Bảng báo cáo và kết quả dùng đúng một bộ dữ liệu tính toán.
- Trong chế độ có chứng nhận, mọi bước được trả là đạt phải thỏa chính các bất đẳng thức đã in.
- Trong chế độ practical, không được xuất cận co hay nhãn bảo đảm giả.
- Nội dung công thức tiến/lùi, bảng và điều kiện dừng phải đúng khi xuất/in, không chỉ khi nhìn màn hình.
- Thay đổi phương pháp/khoảng/tập mốc trên màn hình chưa được tự tính; chỉ thực hiện khi người dùng kích hoạt lượt chạy theo cơ chế hiện tại.
- Có nhiều khoảng thì không tự chọn khoảng đầu hoặc tự giải hết; thiếu lựa chọn thì trả thông tin cần chọn.
- Lựa chọn mốc/bậc không phù hợp phải được giữ trong báo cáo lỗi, không tự sửa để tạo một kết quả thành công.
- Ví dụ E không được tạo kết quả chia đôi nếu người dùng chưa chọn và chạy chia đôi riêng.

Kiểm tra trình bày bằng cách xuất lời giải B và C, xem toàn bộ công thức và bảng. Nếu có PDF, render để kiểm tra không tràn/cắt chữ, không biến dấu âm hay số mũ thành ký tự lỗi. Kiểm tra cả một trường hợp thất bại E: lời giải phải giải thích lý do, không để màn hình trống.

Hoàn thành khi:

1. Ba phương pháp chính chạy được với bậc phù hợp dữ liệu, có kiểm tra điều kiện.
2. Bộ A–G cho kết quả và trạng thái đúng.
3. Người học truy được từng số của ví dụ: từ bảng đến hệ số, từ hệ số đến công thức, từ vòng cũ đến vòng mới.
4. Báo cáo rõ mọi tham số, điều kiện dừng và phạm vi sai số.
5. Ghi rõ điểm tích hợp, ánh xạ tham số hiện tại, các thay đổi thuật toán/phần xuất lời giải và kết quả kiểm tra thực sự đã chạy. Dùng cách chạy/import vốn có; không làm lại tài liệu cài đặt ứng dụng hoặc tuyên bố đã kiểm thử khi chưa thực hiện.

Không mở rộng sang các chương phương pháp số khác khi chưa được yêu cầu. Nếu môi trường hiện có hạn chế thư viện chứng nhận, vẫn làm phần tính toán và trình bày đầy đủ, trả nhãn chưa chứng nhận đúng thực tế; không bịa một chứng minh hội tụ để hoàn tất giao diện.
