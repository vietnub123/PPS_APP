# PPS — tra nhanh khi làm bài thi

**Cách dùng:** tìm dạng bài dưới đây → chọn đúng chức năng/phương pháp trong app → thay toàn bộ dữ liệu và tham số ví dụ → chạy → kiểm tra trạng thái → chép các bước được yêu cầu.

**Trước mỗi câu:** xác định đề cho **bảng hay biểu thức**, hỏi **giá trị/đạo hàm/tích phân/tìm ngược/khớp hàm**, bắt buộc **phương pháp, số mốc, bậc, bước và sai số** nào. Đề đã chỉ định thuật toán thì dùng đúng thuật toán ấy.

**Nhập liệu:** dấu thập phân `.`; số cách nhau bằng khoảng trắng; hàm dùng `x^2`, `exp(x)`, `ln(x)`, `sin(x)`. Excel/CSV đặt x,y ở **hai cột đầu**; các ô x̄,ȳ của đề nhập riêng vào tham số. Nội suy/spline cần x phân biệt; hồi quy được giữ nhiều phép đo cùng x.

## 1. Đề cho bảng, hỏi f(x̄), đa thức hoặc đạo hàm

Vào **Nội suy đa thức**. Kiểm tra x có cách đều không: các hiệu x_(i+1)−x_i có cùng h.

| Gặp dữ liệu/yêu cầu | Chọn gì | Lưu ý khi nhập |
|---|---|---|
| x không đều; đề yêu cầu Lagrange | **Lagrange** | Không cần h cố định |
| x không đều; dùng Newton | **Newton → Mốc bất kỳ** | Dùng tỷ sai phân; chọn hướng đề yêu cầu |
| x đều; tính gần đầu/cuối tập mốc | **Newton → Mốc cách đều → Tiến/Lùi** | Tiến lấy gốc đầu tập, lùi lấy gốc cuối tập |
| x đều; đề yêu cầu Gauss | **Gauss I / Gauss II** | I thuận tiện về phía phải gốc giữa, II về phía trái; đọc đúng gốc app in |
| x đều; số mốc lẻ, quanh gốc giữa | **Stirling** | Số mốc dùng phải lẻ |
| x đều; số mốc chẵn, quanh giữa hai mốc trung tâm | **Bessel** | Số mốc dùng phải chẵn, ít nhất 2 |

**Thao tác:** nhập bảng → **Điểm cần tính x** → **Cấp đạo hàm** (`0`: giá trị; `1`: đạo hàm một; `2`: đạo hàm hai) → **Số mốc dùng** → chạy. Bậc p cần p+1 mốc. Ô số mốc để trống dùng toàn bảng; nhập K thì app chọn K mốc quanh điểm tính. Nếu đề chỉ rõ các mốc, chỉ đưa đúng các cặp ấy vào lượt tính.

**Ví dụ:** bảng 104 mốc, đề hỏi Stirling 7 mốc tại 2.55 và f′(2.55): chọn **Stirling**, điểm `2.55`, cấp `1`, số mốc `7`; lời giải có cả P và đạo hàm. Đề hỏi Bessel 8 mốc thì đổi phương pháp và số mốc thành `8`.

**Chép vào bài:** mốc đã chọn, h/gốc, biến t, bảng sai phân/tỷ sai phân, công thức P, phép thế và kết quả. Đạo hàm theo t phải đổi bằng h^(−r); app đã đổi, không chia h lần nữa. Điểm ngoài dải mốc là ngoại suy. Bậc cao không tự làm xấp xỉ tốt hơn.

## 2. Đề cho mức ȳ, yêu cầu tìm x sao cho f(x)=ȳ

Vào **Chọn mốc → Mốc nội suy ngược** để khảo sát mức; đọc các khoảng đổi dấu và nhánh. Nếu có nhiều khoảng, chọn khoảng cần giải theo đề, xử lý từng khoảng riêng.

| Đề yêu cầu | Vào **Nội suy ngược**, chọn | Điều kiện cần nhớ |
|---|---|---|
| Nội suy hàm ngược/đảo bảng | **Hàm ngược — Newton/Lagrange** | Chọn nhánh đơn điệu phù hợp, y dùng phân biệt; x không cần đều |
| Viết/chạy thuật toán lặp tiến hoặc lùi | **Lặp tiến / Lặp lùi** | x dùng cách đều; có công thức lặp hợp lệ, d tại gốc khác 0 |
| Lặp và bảo đảm sai số mô hình bằng cận co | **Lặp có cận co** | Chọn hướng; cần t₀∈J, Φ(J)⊆J, q<1 |
| Giải đa thức thuận bằng chia đôi | **Chia đôi đa thức** | P(a)−ȳ và P(b)−ȳ trái dấu, hoặc một đầu là nghiệm |

**Thao tác cho bài lặp:** nhập bảng → mức ȳ → khoảng x `[a,b]` → **Mốc dùng** → khởi tạo → hai dung sai → số vòng tối đa → chạy. **Mốc dùng** để trống giữ nguyên toàn bảng; nhập `[9,10,11,12]` chọn đúng bốn dòng gốc đánh số từ **0**. Đây là lựa chọn của bài làm, phải ghi rõ.

Tiến giữ gốc **đầu tập dùng**, lùi giữ gốc **cuối tập dùng**. Khoảng nghiệm có thể ở giữa bảng: T=[(a−gốc)/h,(b−gốc)/h], không bắt buộc [0,1] hay [−1,0]. **Số vòng không làm tăng số mốc cần có.**

**Chép vào bài:** tập mốc/bậc/gốc/h; p(t)=c₀+d·t+H(t); Φ(t)=(ȳ−c₀−H(t))/d; quy tắc t₀; bảng từng vòng t_k,x_k,phần dư và kiểm tra dừng. Có cận co thì thêm J,q và B_k=|h|q|t_k−t_(k−1)|/(1−q); kiểm cả B_k≤ε_x và phần dư≤ε_y. Mở phần **Chi tiết** để lấy phép thế số.

**Bẫy:** đảo bảng cho Q(ȳ), còn lặp/chia đôi giải P(x)=ȳ; hai kết quả có thể khác. Thực hành ra ngoài T được cảnh báo và tiếp tục; kết quả cuối ngoài khoảng yêu cầu không được nhận. Thiếu chứng nhận, hết vòng và tràn số là ba lý do khác nhau; tăng số vòng không chữa mọi nguyên nhân. Chỉ đổi mốc/phương pháp ở lượt riêng khi đề cho phép.

**Ví dụ phân biệt:** x=`0 1 2`, y=`0 1 4`, mức `2`: đảo bảng ba mốc cho 5/3; chia đôi đa thức thuận trên `[1,2]` cho gần √2. Chọn theo cách đề yêu cầu, không lấy hai đáp số so bằng nhau.

## 3. Đề yêu cầu dựng spline, tính S, S′ hoặc tích phân spline

Vào **Spline**. Mốc có thể không đều. **Đọc điều kiện biên trước khi chọn phương pháp**; không mặc định mọi spline đều là tự nhiên.

| Đề cho | Chọn | Nhập điều kiện |
|---|---|---|
| Ghép đoạn thẳng | **Tuyến tính** | Không cần biên |
| Bậc 2, biết S′ ở một đầu | **Bậc hai — biên trái/phải** | Giá trị S′ ở đúng đầu ấy |
| Bậc 3, S″ hai đầu bằng 0 | **Cubic tự nhiên** | App đặt đúng hai điều kiện này |
| Bậc 3, biết S′ hai đầu | **Cubic kẹp** | Hai giá trị S′ |
| Bậc 3, biết S″ hai đầu | **Cubic đạo hàm bậc hai** | Hai giá trị S″ |
| Một đầu cho S′, đầu kia cho S″ | **Cubic hỗn hợp** | Chọn cấp 1/2 và giá trị ở từng đầu |
| Tuần hoàn / not-a-knot | **Cubic tuần hoàn / Cubic not-a-knot** | App cần tuần hoàn ≥3 mốc, y hai đầu bằng nhau; not-a-knot ≥4 mốc |
| Bậc 4, biết S′,S″,S‴ đầu trái | **Bậc 4 — đạo hàm trái** | Ba số đúng thứ tự, ví dụ `0 2 0` nếu đề cho như vậy |
| Biên khác, bậc khác | **Biên tổng quát** | Nhập bậc và JSON điều kiện, ví dụ `[["trái",1,0],["phải",1,2]]` cho cubic |

**Thao tác:** nhập bảng → chọn biên → nhập giá trị biên → điểm tính/cấp đạo hàm hoặc hai cận tích phân → bộ giải → chạy. Để trống điểm tính nếu chỉ cần dựng spline. Chọn **Thomas** cho hệ ba đường chéo thích hợp, **Gauss** cho hệ cần khử có chọn trụ, **Tự chọn** nếu đề không bắt buộc bộ giải.

**Chép vào bài:** h_i, độ dốc từng đoạn, điều kiện biên, hệ, khử/thế ngược, hệ số/mảnh S_i và phép tính tại điểm hỏi. Mảnh dùng u=x−x_i, nên đạo hàm theo u không chia thêm h_i. Tại nút có thể phải ghi hai đạo hàm một phía; tích phân phải chia đúng các mảnh.

**Bẫy:** spline bậc p trơn C^(p−1) cần p−1 điều kiện bổ sung độc lập. Đếm đủ điều kiện chưa có nghĩa độc lập/tương thích. Không được tự gán biên còn thiếu. Spline vẫn có thể dao động giữa mốc; không tự làm trơn nhiễu.

**Ví dụ:** x=`0 1 2 3`, y=`0 1 0 1`, đề cho biên tự nhiên và hỏi S′(1.5): chọn **Cubic tự nhiên**, điểm `1.5`, cấp `1`, bộ giải **Thomas** → S′(1.5)=−4/3.

## 4. Đề yêu cầu khớp hàm, xác định a,b,c…, bình phương tối thiểu

Vào **Bình phương tối thiểu**. Dữ liệu đo có nhiễu không nhất thiết được khớp đi qua mọi điểm. Chọn đúng **dạng hàm và thang sai số** đề yêu cầu.

| Mô hình đề cho | Phương pháp | Ô cơ sở |
|---|---|---|
| a+b·x | **Tuyến tính theo cơ sở** | `1;x` |
| a+b·x+c·x² | **Tuyến tính theo cơ sở** | `1;x;x^2` |
| a·x+b/x, hoặc tổ hợp cơ sở khác | **Tuyến tính theo cơ sở** | `x;1/x`, hoặc đúng các cơ sở đề cho |
| a·exp(b·x) | **Hàm mũ** hoặc **Hàm mũ — SSE thang y** | `x` |
| a·exp(b·x+c/x) | Như trên | `x;1/x` |
| a·exp(b·x²+c/x) | Như trên | `x^2;1/x` |
| a·x^b | **Lũy thừa** hoặc **Lũy thừa — SSE thang y** | Không nhập cơ sở riêng |
| ln(a+b·x) | **Log của tổ hợp cơ sở** | `1;x` |
| 1/(a+b·x); x/(a+b·x); a+b·ln(x); A·B^x | Chọn đúng tên dạng hàm trong danh sách | Không nhập cơ sở riêng |

**Chọn cách giải:** đề yêu cầu lập/giải hệ chuẩn → **Hệ chuẩn — Gauss**; giải trực tiếp theo thiết kế → **QR**. **SVD + Chuẩn nhỏ nhất** chỉ khi chủ động chọn loại nghiệm đó; thiếu hạng thì các tham số không xác định duy nhất theo yêu cầu mặc định.

**Chọn thang:** **Hàm mũ/Lũy thừa** dùng log, tối ưu trên thang log; **…SSE thang y** dùng LM để tối ưu Σw_i(y_i−g_i)² trên dữ liệu gốc. Cách log cần y cùng dấu, khác 0; lũy thừa còn cần x>0. Nếu đề yêu cầu a>0 thì mô hình mũ/lũy thừa có y>0. Không xóa hoặc dịch y âm để ép phép log chạy được. SSE gốc cho phép y đổi dấu, nhưng phải là mục tiêu đề cho phép.

**Thao tác:** nhập bảng → mô hình/cơ sở → trọng số (trống: đều bằng 1) → bộ giải → nếu LM thì nhập tham số đầu theo thứ tự `A b1 b2…`, ngưỡng và số vòng → chạy. Trọng số không âm, ít nhất một dương; giữ dòng x lặp và dòng w=0. Hàm mũ đã có biên độ A: **không thêm `1` vào cơ sở phần mũ**.

**Chép vào bài:** phép biến đổi nếu có, bảng cơ sở/các tổng, hệ và cách giải, tham số khôi phục, phần dư và sai số. Với LM ghi cả khởi tạo, λ, tham số/SSE từng bước thử, bước nhận/từ chối và lý do dừng. SSE=Σr_i²; MSE=SSE/N; RMSE=√MSE. Không nhầm với sigma dùng N−p hoặc mục tiêu có trọng số/thang log.

**Bẫy miền:** `1/y` cần y≠0; bản biến đổi `x/(a+b*x)` cần cả x,y≠0; `ln(x)` cần x>0; `ln(a+b*x)` cần đối số sau khớp dương tại điểm dự đoán. Đọc tham số đã ánh xạ về mô hình gốc. LM chưa có chứng nhận cực tiểu toàn cục; RMSE không phải cận sai số dự đoán.

**Ví dụ:** x=`0 1 2`, y=`1 2 2`, trọng số=`1 2 1`, mô hình a+b·x → **Tuyến tính theo cơ sở**, `1;x`, **Hệ chuẩn — Gauss** → a=1.25, b=0.5. Để trống trọng số sẽ thành bài khớp khác.

## 5. Đề hỏi đạo hàm từ bảng hoặc từ đa thức đã biết

| Đề cho | Thao tác | Chép |
|---|---|---|
| Bảng x,y; hỏi đạo hàm cấp r, dùng đa thức bậc p | **Đạo hàm & Horner → Đạo hàm từ bảng**; nhập điểm, p,r; cần p+1 mốc, 1≤r≤p | Mốc được chọn, trọng số, tổng đóng góp và kết quả |
| Đa thức có sẵn hệ số | **Đạo hàm & Horner → Horner**; nhập hệ số bậc **giảm dần**, điểm và đạo hàm đến cấp cần lấy | Sơ đồ Horner và các giá trị đạo hàm |

Ví dụ P(x)=2x³−3x+1 nhập `2 0 -3 1`, không bỏ hệ số x² bằng 0. Nếu đề bắt buộc đạo hàm qua Stirling/Bessel thì dùng mục 1, không đổi sang công thức khác.

## 6. Đề hỏi tích phân số

Vào **Tích phân** → chọn phương pháp → **Nguồn dữ liệu: Hàm/Bảng** → cận a,b → tham số lưới → chạy.

| Phương pháp | Dữ liệu/lưới cần có |
|---|---|
| **Hình thang** | n khoảng; bảng đủ n+1 mốc gồm hai đầu |
| **Simpson** (1/3) | n **chẵn**, bảng đủ n+1 mốc |
| **Trung điểm** | n giá trị tại **tâm** các khoảng; bảng x không phải hai đầu khoảng |
| **Newton-Cotes** bậc m | n chia hết cho m; Simpson 3/8 tương ứng bậc `3` |
| **Tích phân kép** | Biểu thức f(x,y), cận x=[a,b], y=[c,d]; Simpson cần số khoảng mỗi chiều chẵn |

**Lưu ý:** n là **số khoảng**, không phải số mốc. Chức năng tích phân từ bảng hiện yêu cầu khớp lưới đều của [a,b]; bảng không đều không được đưa thẳng vào rồi coi như đều. Nếu có biểu thức và đề cố định n, để trống dung sai tự chia lưới. Bảng hữu hạn không tự sinh được dữ liệu khi chia nhỏ bước.

**Chép:** h, n, bảng trọng số/giá trị, công thức và tổng. Nếu đề cho cận M₂/M₄ hợp lệ thì nhập để tính cận lý thuyết; nếu chỉ dùng Runge, ghi **ước lượng**. Đọc đúng Runge đang áp dụng cho lưới n hay 2n. Đảo cận phải đổi dấu.

**Ví dụ:** ∫₀¹x²dx bằng Simpson, 10 khoảng → biểu thức `x^2`, a=`0`, b=`1`, n=`10`, nguồn **Hàm**, để trống dung sai tự chia lưới → gần 1/3.

## 7. Đề cho phương trình vi phân và điều kiện đầu

Vào **Phương trình vi phân**. App dùng **t** là biến độc lập; nghiệm gọi **x,y,z**, tối đa 3 thành phần.

| Đề yêu cầu | Chọn/nhập |
|---|---|
| Euler hiện, Euler ẩn, hình thang | Đúng tên; ngưỡng bước ẩn là sai số giải bước, không phải sai số toàn khoảng |
| Runge–Kutta bậc 2/3/4 | **RK2/RK3/RK4** theo đề; không tự thay bằng bậc khác |
| RK2/RK3 có tham số hoặc bảng Butcher cho trước | **RK2 tham số / RK3 tham số / RK tùy chỉnh**; bảng tùy chỉnh hiện chỉ nhận RK hiện, A tam giác dưới nghiêm ngặt |
| Adams s bước | **Adams 2…5**; app dùng RK4 khởi tạo, AB dự báo và AM hiệu chỉnh |

**Ví dụ nhập:** đề y′=t+y, y(0)=1 → vế phải `t+x`, giá trị đầu `1`, thời điểm đầu `0`, cuối theo đề, h theo đề. Hệ u′=v, v′=−u → vế phải `y; -x`, giá trị đầu theo thứ tự u,v.

**Chép:** phương trình và ánh xạ tên biến, điều kiện đầu, h, công thức phương pháp, bảng các bước/tầng RK hoặc dự báo–hiệu chỉnh. Chọn h cùng chiều a→b và **(b−a)/h là số nguyên**; app không tự thêm bước cuối ngắn hơn. Khi xét sai số toàn cục có thể đối chiếu h và h/2 nếu đề cho phép; không gọi đó là cận bảo đảm khi chưa đủ giả thiết.

## 8. Đề cho điều kiện ở hai đầu; hoặc hỏi trị riêng

**Bài toán biên → Biên tổng quát:** app giải **(p·u′)′−q·u=−f**. Chuyển đề về đúng dạng rồi nhập p,q,f,a,b,h. Ví dụ u″=2 tương ứng `p=1`, `q=0`, **`f=-2`**.

Biên nhập theo **alpha·u′+beta·u=gamma**, đạo hàm theo x tăng ở cả hai đầu: u(a)=2 → `0 1 2`; u′(b)=3 → `1 0 3`; u′(a)+2u(a)=4 → `1 2 4`. Biên dùng pháp tuyến ngoài phải đổi dấu trước khi nhập. Hai biên chỉ cho đạo hàm có thể không xác định nghiệm duy nhất.

**Bài toán biên → Trị riêng:** app giải **−(p·u′)′+q·u=λ·r·u**, với **u(a)=u(b)=0**. Nhập p,q, ô **r(x)**, đoạn, h, số trị riêng. p tại nửa bước và r tại nút phải dương. Các kiểu biên trị riêng khác chưa có trong lựa chọn này.

**Chép:** dạng phương trình đã chuyển, điều kiện biên, lưới, hệ sai phân và nghiệm/trị riêng. Phần dư hệ nhỏ không tự là sai số nhỏ với bài toán liên tục.

## 9. Chọn mốc; câu phụ về sai số, hệ hoặc dữ liệu thiếu

| Yêu cầu | Cách làm |
|---|---|
| Chọn K mốc quanh điểm tính | **Chọn mốc → Mốc cách đều**; nhập điểm/K, xem đúng các cặp được chọn. Kiểm tra lại yêu cầu lưới của thuật toán sau đó |
| Sinh n+1 mốc Chebyshev trên [a,b] | **Chọn mốc → Chebyshev**, nhập **bậc n** và hai đầu; phải tính y tại các x mới, không ghép y của lưới cũ |
| Cận sai số nội suy | Gọi Python `ch1.interpolation_error_bound(x,z,M_N)`, N là **số mốc**, M_N chặn đạo hàm cấp N; cần căn cứ cho M_N |
| Điền y thiếu, đề cho bậc d | Python `ch1.fill_missing(x,y,degree=d)` với ô thiếu là `None`; cần ít nhất d+1 mốc đã biết và dữ liệu tương thích |
| Giải hệ Gauss/Thomas riêng | Python `ch1.gaussian_elimination(A,b)` / `ch1.thomas(lower,diag,upper,b)`; Thomas chỉ cho hệ ba đường chéo thích hợp |

Các hàm `ch1` dùng sau `from pps import chapter1_tools as ch1`; ví dụ và tham số chi tiết ở [hướng dẫn đầy đủ](Huong_dan_dung_khi_thi.md). Không có căn cứ M_N/độ dốc thì chưa thể lấy sai lệch tại các mốc làm cận sai số của hàm thật.

## 10. Trước khi chép đáp án

1. Kiểm lại dữ liệu, mô hình, mốc/bậc, điều kiện biên và đơn vị; không để sót tham số ví dụ.
2. Đọc **kết luận/trạng thái dừng**. “Giá trị cuối để xem” chưa phải nghiệm đạt yêu cầu. Thiếu hạng, sai miền log, thiếu chứng nhận và hết vòng cần xử lý đúng nguyên nhân.
3. Chép thuật toán/công thức, bảng cần thiết, phép thế, kết quả và loại sai số; đề đòi chứng minh/giải thích thì vẫn phải viết lập luận.
4. Chọn **Chi tiết** khi cần các bước khử/vòng lặp; **Lưu lời giải** ra HTML để xem/in ngoại tuyến, **Xuất bảng** khi cần tra đầy đủ số liệu. Số chữ số hiển thị không phải số chữ số được bảo đảm đúng.

**Mở sẵn để luyện thao tác:** [bài mẫu theo loại](examples/de_20251/README.md), [đề ảnh và workbook 20251 đã đối chiếu](Kiem_dinh_de_20251.md). Ảnh chứa hai biến thể đề; đáp số ở tài liệu ghi rõ mô hình chạy trên tệp test2.

**Chạy ngoại tuyến:** chuẩn bị thư viện trước; mở `CHAY_PPS.bat`. Nếu dùng console: `CHAY_CONSOLE.bat examples\de_20251\02a_lap_tien_cuc_bo.json`. Thay nội dung bài JSON theo đề đang làm.
