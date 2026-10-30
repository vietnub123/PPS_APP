# GUIDE TRIỂN KHAI VÀ HIỂN THỊ NỘI SUY NGƯỢC

Phiên bản sửa lỗi chọn mốc: 30/10/2026, bản 2. Tài liệu đi kèm: **Noi_suy_nguoc_Ly_thuyet_Thuat_toan_Bai_mau.pdf**.

## 0. Bản vá bắt buộc cho lỗi “đủ mốc” và khoảng nghiệm ở giữa bảng

Phần này thay thế mọi cách hiểu trong bản trước rằng Newton tiến phải lấy gốc sát đầu trái khoảng nghiệm hoặc Newton lùi phải lấy gốc sát đầu phải khoảng nghiệm. Đó chỉ là cách chọn cục bộ thuận tiện trong bài mẫu, không phải điều kiện bắt buộc của phương pháp.

### 0.1. Những việc phải sửa trong app

1. **Tách bảng nhập khỏi tập mốc tính.** `points` là bảng dữ liệu; `selected_nodes` là tập dùng lập đa thức. Nếu người dùng chọn “dùng toàn bộ”, giữ tất cả mốc. Nếu chưa có UI chọn tập con, có thể tiếp tục dùng toàn bộ dữ liệu, ghi rõ bậc tối đa tương ứng; không bắt người dùng chọn lại chỉ để chạy được.
2. **Không dời gốc theo vị trí nghiệm rồi đòi thêm mốc.** Với tập tính tăng `x[0]..x[m]`, Newton tiến dùng `origin=x[0]`, Newton lùi dùng `origin=x[m]`. Các hệ số phải đi cùng gốc đó.
3. **Khoảng nghiệm là một lựa chọn độc lập.** Với khoảng `[a,b]`, tính `T=[(a-origin)/h,(b-origin)/h]`. Không ép tiến vào `[0,1]` hoặc lùi vào `[-1,0]` khi nghiệm nằm ở giữa tập mốc.
4. **Không dùng kiểm tra “còn bao nhiêu mốc kể từ khoảng nghiệm” để từ chối tập đã có.** `INSUFFICIENT_NODES` chỉ dùng nếu tập tính thực sự có ít hơn `m+1` mốc cho bậc được yêu cầu. Số vòng lặp không xuất hiện trong điều kiện này.
5. **Không biến việc thiếu chứng nhận hội tụ thành lỗi thiếu dữ liệu.** Chế độ thực hành vẫn chạy phép lặp hợp lệ, ghi chưa có bảo đảm. Chế độ chỉ cho kết quả có chứng nhận phải ghi thiếu chứng nhận, không ghi thiếu mốc.
6. **Không coi rời khoảng nghiệm là lỗi số học.** Trong chế độ thực hành, ghi cảnh báo và tiếp tục; kiểm tra kết quả cuối có thuộc khoảng người dùng yêu cầu hay không. Trong chế độ đã chứng nhận trên một đoạn `J`, rời `J` là vi phạm chứng nhận và phải dừng kiểm tra, không kẹp giá trị vào biên.
7. **Giữ nguyên phương pháp, dữ liệu và gốc đã công bố.** Nếu muốn đổi bậc, gốc hoặc tập mốc, phải là lựa chọn rõ ràng của người dùng.

### 0.2. Áp dụng cho ảnh báo lỗi đã gửi

Ảnh cho biết: đang dùng 36 mốc, bậc tối đa 35, bước `h=0.115`; mức `1.23` được phát hiện giữa `x=2.035` và `2.15`. App không được tự chuyển gốc tiến sang `2.035`, rồi yêu cầu 36 mốc tới `6.06` và báo chỉ còn 27 mốc.

Thay vào đó: giữ gốc đầu của tập 36 mốc đã chọn, lập toàn bộ hệ số, đổi khoảng `[2.035,2.15]` sang biến `t` theo gốc đó, rồi thử lặp với kiểm tra hội tụ đúng loại. Nếu không hội tụ, báo quỹ đạo lặp, độ lệch và lý do dừng thật sự.

Không có đủ bảng `y` gốc trong ảnh để khẳng định phép lặp cụ thể sẽ hội tụ hay cho nghiệm nào. Bản vá này sửa việc từ chối sai ở bước chuẩn bị, không tạo lời hứa hội tụ cho mọi dữ liệu.

### 0.3. Số mốc không phải số vòng

Các mốc được dùng để lập **một công thức**. Sau đó từng vòng dùng lại công thức ấy: `t_1=Φ(t_0)`, `t_2=Φ(t_1)`, ... Không cần mốc dữ liệu mới ở mỗi vòng. Bốn mốc có thể dùng cho hàng chục vòng; 36 mốc không có nghĩa phải lặp 36 lần.

## 1. Nhiệm vụ và ranh giới tích hợp

Chương trình hiện có đã đảm nhiệm nhập dữ liệu và tham số. Chỉ bổ sung phần tính nội suy ngược, kiểm tra điều kiện, ghi lại quá trình và hiển thị lời giải. Không xây lại phần nhập, không thay cấu trúc ứng dụng khi chưa cần thiết.

Kết quả phải phục vụ đồng thời hai nhu cầu:

1. Tính đúng theo phương pháp và các lựa chọn của người dùng.
2. Trình bày như một bài giải có thể đọc, kiểm tra và dùng khi ôn thi.

Các phương pháp phải có:

| Mã phương pháp | Ý nghĩa |
|---|---|
| `inverse_lagrange` | Nội suy hàm ngược bằng Lagrange trên bảng đảo `(y_i, x_i)`. |
| `inverse_newton` | Nội suy hàm ngược bằng Newton **tỉ sai phân** trên bảng đảo. |
| `iterate_forward` | Lập đa thức Newton tiến theo biến `t`, sau đó lặp đơn. |
| `iterate_backward` | Lập đa thức Newton lùi theo biến `t`, sau đó lặp đơn. |

Người dùng chọn phương pháp, nhánh, khoảng nghiệm, mốc, bậc và các tham số. Chương trình được phép quét, đề xuất, kiểm tra và giải thích. **Không âm thầm đổi phương pháp, giảm bậc, đổi khoảng, đổi gốc hoặc thay tập mốc.** Nếu cần đổi, báo lựa chọn cần sửa và chờ thao tác của người dùng trong ứng dụng.

Không giới hạn cứng ở bậc 3. Với mô hình nội suy qua `m+1` mốc, bậc tối đa là `m`; bậc thực tế có thể thấp hơn nếu các hệ số cấp cao bằng 0. Nếu người dùng chỉ định bậc thấp hơn trong một bảng lớn, phải xác định rõ tập `m+1` mốc tính; nếu chọn dùng toàn bộ, không tự bỏ mốc. Bậc 3 trong bài mẫu chỉ đến từ việc chọn bốn mốc.

**Hàm ngược** cần xử lý trên nhánh thích hợp để có ý nghĩa một-một. **Đa thức thuận dùng cho lặp** vẫn lập được từ tập mốc cách đều đi qua nhiều nhánh của bảng; đây không phải lỗi dữ liệu. Nếu người dùng chọn tập như vậy, cảnh báo khả năng nhiều nghiệm và khó hội tụ, giữ khoảng nghiệm được yêu cầu để đối chiếu kết quả.

## 2. Phân biệt hai mô hình trước khi code

### 2.1. Nội suy hàm ngược

Lập đa thức `Q(y)` từ các cặp `(y_i, x_i)`, rồi tính:

\[
\hat x=Q(\bar y).
\]

Không có vòng lặp tìm nghiệm trong phương pháp này. Vòng lặp chạy qua các mốc hoặc các cấp tỉ sai phân là vòng tính đa thức, không phải vòng hội tụ.

### 2.2. Lặp từ đa thức thuận

Lập đa thức `P_x(x)` xấp xỉ hàm thuận, đổi biến `x = origin + h*t`. Đặt:

\[
P(t)=P_x(\mathrm{origin}+ht)=y_{\mathrm{base}}+dt+H(t).
\]

Sau đó giải `P(t) = target_y` bằng:

\[
t_{j+1}=\frac{\mathrm{target\_y}-y_{\mathrm{base}}-H(t_j)}{d}.
\]

**`Q` thường không phải nghịch đảo chính xác của `P_x`.** Vì vậy không được buộc phương pháp hàm ngược phải thỏa `P_x(Q(target_y)) = target_y` rồi báo lỗi nếu không thỏa. Nếu hiển thị độ lệch này, ghi rõ đó là đối chiếu với một mô hình thuận khác, không phải điều kiện hội tụ của phương pháp hàm ngược.

## 3. Hợp đồng đầu vào

Các tên dưới đây là gợi ý ánh xạ, không bắt buộc thay tên đang có của ứng dụng.

| Trường | Kiểu/ý nghĩa | Kiểm tra |
|---|---|---|
| `points` | Danh sách cặp `(x, y)` kèm ID dòng gốc. | Hữu hạn, không làm lệch cặp khi sắp xếp. |
| `target_y` | Mức cần giải. | Hữu hạn. |
| `method` | Một trong bốn mã ở trên. | Phải có và được hỗ trợ. |
| `selected_branch` | Nhánh mục tiêu khi cần. | Bắt buộc xét ý nghĩa một-một cho hàm ngược; không ép toàn bộ tập mốc thuận phải cùng nhánh. |
| `bracket` | Khoảng `[a,b]` đang yêu cầu tìm nghiệm. | Độc lập với hai đầu tập mốc tính; giữ nguyên lựa chọn và kiểm tra kết quả thuộc khoảng. |
| `selected_nodes` | Danh sách `m+1` mốc được chọn. | Không tự bổ sung hay loại bớt. |
| `degree` | Bậc tối đa của mô hình qua tập mốc. | `m+1` mốc tính cho bậc tối đa m; không lấy số vòng làm số mốc. |
| `node_selection` | `all_imported` hoặc tập con được chọn rõ. | Giữ nguyên lựa chọn; bảng nhập lớn không buộc người dùng dùng bậc cao. |
| `initial_rule` | `origin_linear`, `bracket_linear` hoặc `manual`. | Công bố lựa chọn; không tự thay khởi tạo sau một bước thất bại. |
| `initial_t` | Giá trị đầu khi chọn thủ công. | Hữu hạn. |
| `run_mode` | `practical` hoặc `certified_only`. | Chế độ thực hành không bị chặn chỉ vì thiếu chứng nhận. |
| `certificate_interval` | Đoạn J dùng chứng minh hội tụ, nếu có. | Có thể khác đoạn T của khoảng nghiệm; phải chứa khởi tạo để áp dụng định lý. |
| `eps_x` | Ngưỡng theo vị trí `x`. | Hữu hạn, dương; áp dụng cho phép lặp. |
| `eps_y` | Ngưỡng độ lệch phương trình. | Hữu hạn, dương; áp dụng cho phép lặp. |
| `max_iterations` | Số vòng tối đa. | Số nguyên dương. |
| `detail_level` | Tổng hợp hoặc chi tiết. | Mặc định luôn có bảng tổng hợp; có thể mở từng vòng. |
| `display_digits` | Số chữ số hiển thị. | Không tác động đến số dùng để tính. |
| `grid_atol`, `grid_rtol` | Dung sai nhận dạng lưới đều. | Không âm; không dùng thay ngưỡng sai số nghiệm. |
| `near_y_atol`, `near_y_rtol` | Ngưỡng cảnh báo tung độ gần trùng. | Chỉ cảnh báo nhạy số; không tự gộp mốc. |
| `convergence_certificate` | Căn cứ hội tụ và cận `q`, nếu có. | Phân loại nguồn và mức xác minh, xem mục 9. |
| `allow_extrapolation` | Lựa chọn ngoại suy tường minh, nếu ứng dụng hỗ trợ. | Mặc định không chạy ngoại suy như một phép nội suy bình thường. |

`origin` có thể âm hoặc bằng 0. Chỉ yêu cầu `h > 0` sau khi các mốc được sắp tăng.

## 4. Tiền kiểm dữ liệu, nhánh và khoảng

### 4.1. Kiểm tra chung

Thực hiện trước khi chia hoặc lập bảng:

1. Số phần tử hợp lệ; mọi `x`, `y`, `target_y` đều hữu hạn.
2. Giữ cặp `(x,y)` và ID dòng khi tạo góc nhìn sắp theo `x`.
3. Mốc `x` đôi một phân biệt. Nếu trùng, nêu các dòng và dừng lựa chọn hiện tại; không tự lấy trung bình.
4. `degree` nguyên dương; đủ và đúng số mốc.
5. Các mốc thuộc đúng tập người dùng chọn. Hàm ngược cần nhánh thích hợp; với lặp thuận, tập mốc đi qua điểm đổi chiều chỉ phát sinh cảnh báo về mô hình/nhiều nghiệm, không tự thành lỗi thiếu mốc.

### 4.2. Quét khoảng đổi dấu

Tại mỗi mốc, tính `F_i = y_i - target_y`.

```text
nghiệm_tại_mốc ← rỗng
khoảng_đổi_dấu ← rỗng

Với i = 0 đến N-1:
    Nếu F_i bằng 0:
        ghi mốc x_i vào nghiệm_tại_mốc

Với i = 0 đến N-2:
    Nếu F_i và F_(i+1) khác 0 và trái dấu:
        ghi khoảng (x_i, x_(i+1))
    Nếu cả hai bằng 0:
        ghi nhận hai đầu cùng đạt mức trên bảng

Trả các danh sách và giới hạn của phép quét
```

So dấu trực tiếp để tránh tràn số do tích `F_i * F_(i+1)`.

Nếu sử dụng ngưỡng để nhận dạng `|F_i| <= tolerance`, nhãn là **“mốc gần đạt mức theo ngưỡng…”**, không phải bằng đúng. Không dùng `eps_y` để âm thầm xóa hoặc gộp những khoảng nhỏ.

Nếu cả hai đầu cùng đạt mức, chỉ biết hai đầu cùng mức. Không tuyên bố cả đoạn là nghiệm khi chưa có mô hình/hypothesis tương ứng.

### 4.3. Tách nhánh trên bảng

Theo dõi dấu của `y_(i+1)-y_i`:

- Dấu dương liên tiếp: nhánh tăng trên bảng.
- Dấu âm liên tiếp: nhánh giảm trên bảng.
- Đổi dấu: điểm chuyển hướng là biên chung của hai nhánh.
- Hiệu bằng 0: ghi riêng đoạn có hai tung độ bằng nhau; không đưa một cặp trùng tung độ vào bảng đảo.

Đầu ra phải nói **“đơn điệu trên các mốc đã cho”**. Muốn kết luận về hàm thật cần giả thiết như liên tục, đơn điệu nghiêm ngặt trên toàn đoạn. Kiểm tra hữu hạn các mẫu không chứng minh được điều này.

### 4.4. Kiểm tra khoảng đang chọn

- Nếu hai đầu trái dấu: báo có đổi dấu trên bảng; kèm giả thiết liên tục để bảo đảm tồn tại nghiệm của hàm thật.
- Nếu một đầu bằng mức: có thể trả mốc đó, đồng thời ghi đây là nghiệm tại mốc dữ liệu.
- Nếu hai đầu cùng dấu: báo “khoảng chọn không được xác nhận bằng phép đổi dấu”; không suy ra hàm thật không có nghiệm.
- Nhiều khoảng: hiển thị danh sách. Mỗi lần chạy gắn với một khoảng; không âm thầm chọn khoảng đầu tiên.
- Không lấy hai mốc đầu/cuối tập tính làm khoảng nghiệm chỉ vì đã chọn tiến/lùi. Khoảng ở giữa tập tính là bình thường.
- Để đối chiếu mô hình thuận, tính thêm `P_x(a)-target_y` và `P_x(b)-target_y` khi cần. Nếu hai đầu là mốc đã nội suy, giá trị khớp dữ liệu trong sai số số học. Nếu là điểm khác, phải đánh giá đa thức, không gán giá trị từ một dòng gần đó.

## 5. Thuật toán hàm ngược bằng Lagrange

### 5.1. Điều kiện

Chọn một nhánh thích hợp. Nếu muốn khẳng định hàm ngược thật tồn tại, cần giả thiết về tính một-một của hàm trên nhánh, chẳng hạn liên tục và đơn điệu nghiêm ngặt. Về mặt lập đa thức, các tung độ đã chọn phải đôi một phân biệt.

Mức `target_y` cần nằm trong miền giá trị nhánh và được bao bởi miền tung độ của tập mốc nếu chạy ở chế độ nội suy. Nếu ngoài miền đó, dừng và nêu ngoại suy, hoặc chạy chỉ khi người dùng đã chọn ngoại suy tường minh; luôn giữ nhãn ngoại suy.

### 5.2. Công thức

\[
L_i(\bar y)=\prod_{r\ne i}\frac{\bar y-y_r}{y_i-y_r},
\qquad \hat x=\sum_{i=0}^{m}x_iL_i(\bar y).
\]

### 5.3. Mã giả

```text
Kiểm tra các y_i phân biệt
Tạo bảng đảo (y_i, x_i)
tổng ← 0

Với i = 0 đến m:
    cơ_sở ← 1
    danh_sách_thừa_số ← rỗng

    Với r = 0 đến m, bỏ qua r = i:
        mẫu ← y_i - y_r
        kiểm tra mẫu khác 0
        thừa_số ← (target_y - y_r) / mẫu
        cơ_sở ← cơ_sở × thừa_số
        lưu tử, mẫu, thừa_số để trình bày

    đóng_góp ← x_i × cơ_sở
    tổng ← tổng + đóng_góp
    lưu hàng [i, x_i, L_i, đóng_góp, tổng_tạm]

x_hat ← tổng
Kiểm tra hữu hạn và vị trí x_hat
Trả kết quả cùng bảng, bước tính, cảnh báo
```

Nếu `target_y` trùng chính xác một `y_i`, có thể trả `x_i` sớm; vẫn ghi rõ mốc được nhận dạng và phương pháp đang chọn. Không trả “hội tụ sau 0 vòng” vì đây không phải phương pháp lặp.

### 5.4. Hiển thị bắt buộc

1. Nhánh, khoảng, mốc, bậc và bảng đảo.
2. Công thức `L_i` tổng quát và công thức đã thay số cho từng `i` ở chế độ chi tiết.
3. Bảng `i | x_i | L_i(target_y) | x_i*L_i(target_y)`.
4. Phép cộng các đóng góp và `x_hat`.
5. Kiểm tra vị trí; cận sai số chỉ khi có dữ kiện hợp lệ để tính.

Các giá trị cơ sở âm có thể hoàn toàn hợp lệ. Đừng cắt chúng về `[0,1]`.

## 6. Thuật toán hàm ngược bằng Newton tỉ sai phân

### 6.1. Lập bảng

Đánh số cục bộ `0..m`. Đặt:

\[
T_{i,0}=x_i,
\qquad
T_{i,r}=\frac{T_{i+1,r-1}-T_{i,r-1}}{y_{i+r}-y_i}.
\]

Ở cấp `r`, chỉ số `i` chạy `0..m-r`. Các mốc trong mẫu là **tung độ `y`**. Lưu bảng đầy đủ để hiển thị; lấy `c_r = T[0][r]`.

### 6.2. Tính dạng lồng

```text
v ← c_m
lưu bước khởi tạo v

Với r = m-1 giảm đến 0:
    v_cũ ← v
    v ← c_r + (target_y - y_r) × v_cũ
    lưu r, c_r, y_r, v_cũ, v_mới

x_hat ← v
```

### 6.3. Hiển thị

- Bảng đảo và bảng tỉ sai phân theo từng cấp; tô/đánh dấu hàng hệ số `T[0][r]`.
- Đa thức Newton với các thừa số `(y-y_0), (y-y_1), ...`.
- Công thức đã thay `target_y`; từng bước dạng lồng nếu người dùng mở chi tiết.
- Kết quả, kiểm tra vị trí và giới hạn của kết luận sai số.

Không dùng công thức tiến/lùi sai phân thường trên bảng đảo chỉ vì `x_i` ban đầu cách đều. Không đưa hệ số chia `r!` vào bảng tỉ sai phân này.

## 7. Lập đa thức thuận cho phép lặp, không giới hạn bậc

### 7.1. Kiểm tra lưới đều

Với các mốc tăng đã chọn, đặt `h = x[1] - x[0] > 0`. Với từng bước `h_i = x[i+1]-x[i]`, kiểm tra:

\[
|h_i-h|\le\mathrm{grid\_atol}
+\mathrm{grid\_rtol}\max(|h_i|,|h|).
\]

Hiển thị `h`, độ lệch lớn nhất và ngưỡng sử dụng. Dung sai này dùng nhận dạng lưới trong tính toán dấu phẩy động, không phải thay đổi dữ liệu thực sự không đều thành đều. Nếu dữ liệu đi qua kiểm tra trong dung sai, ghi rõ giả thiết lưới đều đang dùng; không ghi các tọa độ đã bị “sửa” như số liệu gốc.

### 7.2. Lập một bảng sai phân tiến dùng chung

\[
D_{i,0}=y_i,
\qquad D_{i,r}=D_{i+1,r-1}-D_{i,r-1}.
\]

```text
Với i = 0 đến m:
    D[i][0] ← y[i]

Với r = 1 đến m:
    Với i = 0 đến m-r:
        D[i][r] ← D[i+1][r-1] - D[i][r-1]
```

### 7.3. Lấy hệ số và chọn gốc từ tập mốc, không từ khoảng nghiệm

Gọi các mốc tính sau khi sắp tăng là `x[0]..x[m]`. Tập này phải cách đều theo kiểm tra ở 7.1. Không bắt buộc các dòng được chọn phải liền nhau trong bảng nhập lớn nếu chính tập được chọn vẫn cách đều.

| Trường | Newton tiến | Newton lùi |
|---|---|---|
| Mốc gốc | Mốc đầu **tập tính** `x[0]`. | Mốc cuối **tập tính** `x[m]`. |
| `origin` | `x[0]`. | `x[m]`. |
| `c_r`, r = 0..m | `D[0][r]`. | `D[m-r][r]`. |
| `y_base` | `c_0 = y[0]`. | `c_0 = y[m]`. |
| `d` | `c_1 = Δy` tại gốc. | `c_1 = ∇y` tại gốc. |
| Biến | `t=(x-origin)/h`. | `t=(x-origin)/h`. |
| Đoạn T của khoảng `[a,b]` | `[(a-x[0])/h,(b-x[0])/h]`. | `[(a-x[m])/h,(b-x[m])/h]`. |

**Không cố định T thành `[0,1]` hoặc `[-1,0]`.** Hai đoạn đó chỉ xuất hiện khi khoảng nghiệm trùng hai mốc đầu của tập tiến hoặc hai mốc cuối của tập lùi. Ví dụ, khoảng giữa mốc thứ 10 và 11 của tập tính tiến tương ứng `T=[9,10]`.

Khi hiển thị bảng lùi tại hàng của mốc phải, ô `∇^r y_j` ánh xạ từ `D[j-r][r]`. Không nhầm cách đặt ô trên màn hình với cách lưu mảng.

Không dịch gốc vào sát nghiệm trong khi giữ nguyên mảng hệ số cũ. Nếu người dùng đổi tập tính để có gốc mới, lập lại bảng và hệ số. Chuyển đa thức sang gốc bất kỳ là một phép biến đổi riêng, không phải đổi mỗi biến `origin`.

### 7.3a. Khi nào thật sự thiếu mốc?

- Yêu cầu bậc tối đa 3 nhưng tập tính chỉ có 3 mốc: thiếu một mốc cho mô hình bậc 3.
- Chọn toàn bộ 36 mốc cho bậc tối đa 35: đủ, dù khoảng nghiệm nằm ở giữa bảng.
- Chọn rõ mô hình cục bộ bắt đầu tại 2.035, bậc 35 nhưng chỉ chọn được 27 mốc: thiếu cho **lựa chọn cục bộ này**. Không áp lỗi đó lên tập toàn bảng chưa bị đổi.
- Có đủ mốc nhưng `d=0`, lưới không đều hoặc phép lặp phân kỳ: dùng đúng loại lỗi tương ứng, không gọi chung “thiếu mốc”.

### 7.4. Tính cơ sở bằng truy hồi

Đặt `B_0(t)=1`. Với `r=1..m`:

\[
B_r(t)=
\begin{cases}
B_{r-1}(t)(t-r+1)/r,&\text{tiến},\\
B_{r-1}(t)(t+r-1)/r,&\text{lùi}.
\end{cases}
\]

Như vậy:

\[
P(t)=\sum_{r=0}^{m}c_r B_r(t),
\qquad
H(t)=\sum_{r=2}^{m}c_rB_r(t).
\]

Vì `B_1(t)=t`, có `P(t)=c_0+c_1*t+H(t)`. Nếu `m=1`, `H(t)=0`: đó là nội suy tuyến tính, không phải lỗi thiếu số hạng.

Truy hồi tránh phải tính giai thừa lớn và các tích dài riêng biệt. Để trình bày vẫn sinh ra dạng dễ đọc, ví dụ:

\[
P(t)=c_0+c_1t+\frac{c_2}{2}t(t-1)
+\frac{c_3}{6}t(t-1)(t-2)+\cdots
\]

cho tiến; dùng dấu cộng trong các thừa số cho lùi. Hiển thị đến đúng bậc được chọn; không in dấu `...` thay cho các số hạng cần thiết trong bài chạy cụ thể.

### 7.5. Mã giả đánh giá đa thức và ghi từng số hạng

```text
ĐÁNH_GIÁ(t, c, hướng):
    cơ_sở ← 1
    đạo_hàm_cơ_sở ← 0
    H ← 0
    H_phẩy ← 0
    các_số_hạng ← rỗng

    Với r = 1 đến m:
        Nếu hướng tiến: thừa_số ← t - (r-1)
        Nếu hướng lùi:  thừa_số ← t + (r-1)

        cơ_sở_cũ ← cơ_sở
        đạo_hàm_cũ ← đạo_hàm_cơ_sở
        cơ_sở ← cơ_sở_cũ × thừa_số / r
        đạo_hàm_cơ_sở ← (đạo_hàm_cũ × thừa_số + cơ_sở_cũ) / r

        số_hạng ← c[r] × cơ_sở
        lưu [r, cơ_sở, c[r], số_hạng]

        Nếu r >= 2:
            H ← H + số_hạng
            H_phẩy ← H_phẩy + c[r] × đạo_hàm_cơ_sở

    P ← c[0] + c[1] × t + H
    Trả P, H, H_phẩy, các_số_hạng
```

Phải dùng cơ sở **cũ** trong công thức đạo hàm. Không ghi đè trước rồi vô tình lấy giá trị mới.

## 8. Thiết lập phương trình lặp và khởi tạo

Hiển thị theo thứ tự: tập mốc và gốc; `x=origin+h*t`; khoảng `[a,b]` và đoạn T tương ứng; đa thức đầy đủ; H(t); phương trình; công thức lặp:

\[
\Phi(t)=\frac{\mathrm{target\_y}-y_{\mathrm{base}}-H(t)}d.
\]

Kiểm tra `d != 0` và mọi số hữu hạn. `d` gần 0 là cảnh báo nhạy số theo ngưỡng công bố. `d==0` không lập được phép lặp bằng cách chia này; không thay mẫu bằng số nhỏ tùy ý.

### 8.1. Quy tắc khởi tạo được lựa chọn và công bố

**`origin_linear` — theo phần tuyến tính tại gốc, như trong slide và hai bài mẫu lặp:**

\[
t_0=\frac{\mathrm{target\_y}-y_{\mathrm{base}}}{d},
\qquad x_0=\mathrm{origin}+h t_0.
\]

**`bracket_linear` — nội suy tuyến tính giữa hai đầu khoảng:** nếu biết giá trị ở hai đầu là `y_a,y_b` và `y_a != y_b`, dùng

\[
x_0=a+(b-a)\frac{\mathrm{target\_y}-y_a}{y_b-y_a},
\qquad t_0=\frac{x_0-\mathrm{origin}}h.
\]

Nếu a,b không phải mốc đã chọn và mục tiêu là nghiệm mô hình thuận, lấy `y_a=P_x(a)`, `y_b=P_x(b)`. Hiển thị rõ đang dùng giá trị mô hình hay số liệu mốc; không lấy nhầm dòng gần nhất.

**`manual` — người dùng cung cấp t_0 hoặc x_0:** chuyển đổi và công bố cách nhập.

Nếu app chưa có lựa chọn khởi tạo, giữ `origin_linear` để tương thích và hiển thị công thức. Không bắt buộc thêm một màn hình mới chỉ để xử lý lỗi mốc. Nếu bổ sung lựa chọn khác, phải cho người dùng thấy quy tắc đang dùng và không đổi ngầm.

### 8.2. Khởi tạo ngoài khoảng nghiệm không có nghĩa thiếu mốc

Nếu `t_0` ngoài T, ghi cảnh báo. Phép lặp có thể còn hội tụ vào khoảng hoặc có thể không; chưa kết luận từ riêng điều đó. Ở chế độ thực hành, được chạy nếu giá trị hữu hạn và công thức xác định. Ở chế độ chứng nhận, cần chứng minh trên một đoạn J chứa t_0 và xét kết quả thuộc khoảng yêu cầu.

Nếu t_0 nằm ngoài đoạn chứng nhận đã cung cấp, chứng nhận đó **không áp dụng cho lần chạy này**. Không giả vờ dùng cận q cũ, không ghi lỗi thiếu mốc. Người dùng có thể chọn lại khởi tạo/J, hoặc chạy thực hành theo lựa chọn rõ ràng.

## 9. Chứng nhận hội tụ và cận q

### 9.1. Điều kiện đầy đủ

Để gọi là có bảo đảm co trên đoạn đóng `J`, cần có đủ:

\[
t_0\in J,\qquad\Phi(J)\subseteq J,\qquad
\max_{t\in J}|\Phi'(t)|\le q<1.
\]

Với công thức đang dùng:

\[
\Phi'(t)=-H'(t)/d.
\]

Phải ghi rõ đoạn **J dùng để chứng nhận**, phân biệt với **T là ảnh của khoảng nghiệm đang yêu cầu**. Có thể chọn J lớn hơn T nếu chứa khởi tạo và đủ các điều kiện. Không lấy q kiểm tra trên một đoạn rồi áp vào các bước nằm ngoài đoạn đó.

Định lý co là điều kiện **đủ**. Không có chứng nhận chưa có nghĩa dữ liệu sai hoặc không được thử lặp. `certified_only` có thể dừng vì thiếu chứng nhận; `practical` vẫn thử lặp với nhãn chưa bảo đảm. Nếu phép lặp hội tụ ngoài khoảng mục tiêu, phải thông báo rõ và không ghi là đã tìm được nghiệm yêu cầu.

### 9.2. Phân loại chứng cứ

| Loại | Có được tự ghi “bảo đảm” không? | Yêu cầu |
|---|---|---|
| `analytic_verified` | Có, nếu đủ ba điều kiện. | Cận được suy ra bằng biến đổi hợp lệ; các bài mẫu dùng cách này. |
| `interval_verified` | Có. | Dùng phép tính khoảng có bao ngoài, kiểm tra toàn đoạn; lưu cách chia khoảng và cận. |
| `user_supplied_bound` | Chỉ ghi “theo cận/giả thiết do người dùng cung cấp”. | Có `J`, `q`, căn cứ giữ nguyên đoạn; không giả vờ phần mềm đã chứng minh độc lập. |
| `sampled_diagnostic` | Không. | Chỉ lấy mẫu giá trị đạo hàm hoặc hàm lặp; ghi rõ khảo sát số. |
| `unavailable` | Không. | Chưa có cận hội tụ. |
| `condition_failed` | Không. | Chỉ ra điều kiện đủ nào không thỏa; không suy ra chắc chắn mọi quỹ đạo đều phân kỳ. |
| `not_applicable_to_seed` | Không. | Chứng nhận không chứa khởi tạo đang dùng; chạy thực hành nếu đã chọn chế độ ấy. |

Không nhận một số `q=0.5` trần rồi tự đánh dấu đủ điều kiện hội tụ. Cũng không ước lượng `q` từ vài bước lặp rồi gọi là cận trên toàn đoạn.

### 9.3. Cách kiểm tra đa thức bậc thấp

Để chặn `|H'|`, xét `H'` ở hai đầu và tại tất cả điểm tới hạn trong đoạn thỏa `H''=0`. Để chặn ảnh `Φ(J)`, xét hai đầu và điểm tới hạn của `Φ` hoặc dùng bất đẳng thức có chứng minh.

Nếu tự tìm nghiệm các đa thức phụ chỉ bằng thuật toán gần đúng thông thường, cần phân biệt khảo sát với chứng nhận. Với bậc cao, không bắt buộc viết bộ chứng minh đại số tổng quát: có thể dùng tính khoảng có chứng nhận hoặc để trạng thái chưa xác minh. Phép tính nội suy vẫn hỗ trợ mọi bậc khả dụng; trạng thái bảo đảm chỉ bật khi có đủ căn cứ.

## 10. Vòng lặp, sai số và điều kiện dừng

Sau khi có giá trị mới `t_new`, tính:

\[
x_{\mathrm{new}}=\mathrm{origin}+h t_{\mathrm{new}},
\]

\[
s_j=|h|\,|t_{\mathrm{new}}-t_{\mathrm{old}}|,
\]

\[
r_j=|P(t_{\mathrm{new}})-\mathrm{target\_y}|.
\]

Nếu có chứng nhận hợp lệ:

\[
B_j=\frac{q}{1-q}s_j.
\]

`B_j` là cận sai số theo `x` đối với nghiệm mô hình, `s_j` chỉ là độ thay đổi giữa hai bước. **Đừng dùng cùng tên “sai số” cho cả hai.**

### 10.1. Quy tắc dừng

| Trường hợp | Điều kiện dừng thành công | Nhãn |
|---|---|---|
| Đã chứng nhận đủ điều kiện co | `B_j <= eps_x` **và** `r_j <= eps_y`. | “Đạt ngưỡng với cận sai số lặp theo mô hình”. |
| Theo giả thiết/cận của người dùng | Cùng hai điều kiện trên. | “Đạt theo cận/giả thiết được cung cấp”. |
| Chưa có chứng nhận | `s_j <= eps_x` **và** `r_j <= eps_y`. | “Dừng thực hành; chưa có cận sai số bảo đảm”. |
| Đạt các ngưỡng nhưng x ngoài khoảng mục tiêu | Không coi là nghiệm của khoảng yêu cầu. | “Lặp đạt ngưỡng tại nghiệm khác/ngoài khoảng yêu cầu”. |
| Hết số vòng | Chưa đạt các điều kiện tương ứng. | “Chưa hội tụ sau L vòng”. |

Không dùng một ngưỡng `eps` cho cả vị trí và giá trị hàm nếu ứng dụng đã tách được hai ngưỡng. Hai đại lượng có thể khác đơn vị và quy mô.

Với `q=0`, công thức vẫn hợp lệ và cho `B_j=0`, nếu đã chứng minh hàm lặp là hằng và giữ nguyên đoạn. Không chia cho `q` trong thuật toán dừng.

### 10.2. Mã giả đầy đủ sau bản vá

```text
LẶP_NỘI_SUY_NGƯỢC(tham_số):
    Tiền kiểm dữ liệu, phương pháp, tập mốc và bậc
    Không yêu cầu khoảng nghiệm sát đầu/cuối tập mốc
    Lập bảng D từ đúng selected_nodes
    Nếu tiến: origin=x[0], c[r]=D[0][r]
    Nếu lùi:  origin=x[m], c[r]=D[m-r][r]
    h ← bước của tập mốc
    T ← [(a-origin)/h, (b-origin)/h]
    y_base ← c[0]; d ← c[1]
    Nếu d==0: trả ZERO_LINEAR_DIFFERENCE
    Lập P, H, Φ

    t_old ← khởi tạo theo initial_rule đang được công bố
    Nếu không hữu hạn: trả NUMERICAL_FAILURE
    Nếu t_old ngoài T: ghi cảnh báo, không ghi lỗi thiếu mốc

    Xét chứng nhận trên J và việc J chứa t_old
    Nếu có đủ căn cứ: certificate_active ← đúng
    Nếu không: certificate_active ← sai, lưu nguyên nhân
    Nếu run_mode=certified_only và thiếu chứng nhận:
        trả CERTIFICATE_UNAVAILABLE
    Lưu hàng 0 và các cảnh báo

    Với j = 1 đến max_iterations:
        _, H_old, _, terms_old ← ĐÁNH_GIÁ(t_old)
        t_new ← (target_y-y_base-H_old)/d
        Nếu t_new không hữu hạn: lưu lỗi, trả NUMERICAL_FAILURE

        Nếu certificate_active và t_new ngoài J:
            lưu vi phạm đoạn chứng nhận, trả CERTIFICATE_VIOLATION
        Nếu t_new ngoài T:
            ghi cảnh báo rời khoảng mục tiêu; không cắt về biên
            trong chế độ thực hành, tiếp tục phép tính

        x_new ← origin+h*t_new
        P_new, H_new, _, terms_new ← ĐÁNH_GIÁ(t_new)
        step_x ← |h|*|t_new-t_old|
        residual ← |P_new-target_y|
        Nếu có đại lượng không hữu hạn: lưu lỗi, trả NUMERICAL_FAILURE

        Nếu certificate_active:
            bound_x ← q/(1-q)*step_x
            pass_x ← bound_x <= eps_x
        Nếu không:
            bound_x ← không có
            pass_x ← step_x <= eps_x
        pass_y ← residual <= eps_y
        Lưu hàng và toàn bộ chi tiết vòng j

        Nếu pass_x và pass_y:
            Nếu x_new không thuộc [a,b]:
                trả CONVERGED_OUTSIDE_REQUESTED_BRACKET
            Trả thành công đúng loại chứng cứ
        Nếu t_new==t_old: trả STAGNATED
        t_old ← t_new

    Trả MAX_ITERATIONS, giữ bảng và giá trị cuối
```

Đa thức xác định với mọi t hữu hạn; T không phải miền xác định của công thức. Một bước ra khỏi T không phải lý do tự phát sinh “thiếu mốc”. Nếu có thêm giới hạn vận hành do người dùng đặt, công bố và kiểm tra giới hạn đó bằng trạng thái riêng. Không âm thầm dùng giới hạn vận hành để đổi đoạn chứng nhận.

### 10.3. Những lỗi thứ tự phải tránh

- Cập nhật `t_old=t_new` trước khi tính sai khác, làm `step_x` luôn bằng 0.
- Tính độ lệch tại `t_old` nhưng gắn vào hàng `t_new`.
- Chỉ kiểm tra sai khác bước rồi ghi bảo đảm sai số.
- Dừng khi một trong hai điều kiện đạt; guide yêu cầu cả hai.
- Làm tròn `t_new` theo số chữ số hiển thị trước khi dùng vòng sau.
- Hết vòng nhưng vẫn trả trạng thái “thành công”.

## 11. Dữ liệu kết quả và trace trình bày

Tách phần tính khỏi renderer. Phần tính trả số, biểu thức và trace có cấu trúc; renderer mới chuyển chúng thành bảng/công thức. Điều này giúp màn hình, bản in và xuất PDF dùng cùng một kết quả.

### 11.1. Đối tượng kết quả gợi ý

```text
InverseInterpolationResult
    method, degree, target_y
    selected_branch, bracket, selected_nodes, origin, target_t_interval, initial_rule, run_mode
    status, status_message
    validation_checks[]
    warnings[]
    inverse_table hoặc difference_table
    coefficient_selection[]
    expressions {coordinate_change, polynomial, correction, iteration, initial}
    convergence {kind, interval, q, invariant_image_bound, evidence}
    direct_calculation_rows[]       # cho Lagrange/Newton hàm ngược
    iteration_rows[]               # cho lặp tiến/lùi
    solution_x                     # chỉ khi có kết quả hợp lệ theo trạng thái
    last_approximation             # kể cả khi chưa hội tụ
    iterations_done
    final_checks[]
    error_scope                    # nghiệm mô hình / hàm thật / dữ liệu
```

`solution_x` và `last_approximation` cần phân biệt. Khi thất bại/hết vòng, có thể hiển thị giá trị cuối để xem, nhưng không đặt nó trong ô “nghiệm đạt yêu cầu”.

### 11.2. Một hàng vòng lặp

```text
IterationRow
    iteration
    old_t
    old_correction_H
    correction_terms_at_old_t[]
    new_t
    new_x
    new_polynomial_value
    step_t_abs
    step_x_abs
    certified_bound_x hoặc null
    residual_y
    pass_position_threshold
    pass_residual_threshold
    in_target_t_interval
    in_certificate_interval hoặc null
    decision {continue, stop_certified, stop_conditional, stop_practical, failed}
```

Lưu `old_t` để khi mở chi tiết có thể tái hiện đúng công thức đã dùng. Không dựng lại giá trị cũ từ các số đã làm tròn trên màn hình.

### 11.3. Một phép kiểm tra

```text
Check
    title
    state {passed, failed, warning, not_verified, not_applicable}
    observed_value
    expected_condition
    explanation
```

`not_verified` khác `failed`. Thiếu thông tin chứng minh hàm thật đơn điệu không đồng nghĩa đã chứng minh hàm không đơn điệu.

## 12. Quy định bố cục hiển thị

### 12.1. Thứ tự bảy khối

**Khối 1 — Bài toán và lựa chọn.**

Hiện mức cần tìm, khoảng đang giải, nhánh, phương pháp, bậc, mốc, ngưỡng và số vòng tối đa. Nếu đã có nhiều khoảng đổi dấu, thể hiện khoảng hiện tại là lựa chọn nào.

**Khối 2 — Kiểm tra điều kiện.**

Liệt kê từng kiểm tra và căn cứ: hữu hạn, đủ mốc, mẫu khác 0, lưới đều, mức được bao, khởi tạo trong đoạn… Không gom tất cả thành một câu “Dữ liệu hợp lệ” làm người đọc không biết đã kiểm tra gì.

**Khối 3 — Bảng tính trung gian.**

Hiện bảng đảo hoặc bảng sai phân/tỉ sai phân. Ô không có giá trị để trống hoặc dùng `—`, không điền `0`. Đánh dấu đúng các ô dùng làm hệ số và ghi gốc tính.

**Khối 4 — Thiết lập công thức.**

Mỗi nội dung thành một công thức riêng: đổi biến, đa thức, `H(t)`, phương trình, hàm lặp, khởi tạo. Trước tiên ghi tên và ý nghĩa, sau đó công thức tổng quát, cuối cùng thay số. Không nhét một chuỗi công thức dài vào đoạn văn.

**Khối 5 — Hội tụ và tiêu chuẩn dừng.**

Hiện riêng T (ảnh của khoảng nghiệm) và J (đoạn chứng nhận, nếu có), loại chứng cứ, ảnh của J, q và công thức B_j, r_j. Chế độ thực hành có thể chạy ngay với nhãn chưa bảo đảm; không dựng thêm điều kiện thiếu mốc vì gốc xa.

**Khối 6 — Quá trình tính.**

- Hàm ngược: bảng cơ sở/đóng góp hoặc tỉ sai phân và các bước dạng lồng.
- Lặp: bảng tổng hợp luôn hiện; mỗi vòng có thể mở xem chi tiết.

**Khối 7 — Kết luận.**

Kết quả, số vòng, lý do dừng, các kiểm tra cuối và phạm vi sai số. Khi thất bại, thay bằng nguyên nhân, giá trị cuối và lựa chọn người dùng có thể điều chỉnh.

### 12.2. Chi tiết bắt buộc của một vòng

```text
Vòng j

✓ 1. Dùng giá trị cũ t_(j-1) = ...
✓ 2. Tính từng số hạng của H(t_(j-1)), rồi cộng = ...
✓ 3. Thay vào công thức: t_j = ... = ...
✓ 4. Đổi về x_j = origin + h*t_j = ...
✓ 5. Tính B_j (hoặc chỉ độ thay đổi nếu chưa có cận) và r_j

Kiểm tra vị trí: [giá trị] <= [ngưỡng] — Đạt/Chưa đạt
Kiểm tra độ lệch: [giá trị] <= [ngưỡng] — Đạt/Chưa đạt
Quyết định: Tiếp tục / Dừng theo loại chứng cứ / Lỗi
```

Các dấu ✓ ở 1–5 nói đã hoàn thành phép tính. Dấu ✓ ở phép kiểm tra chỉ xuất hiện khi điều kiện thật sự đạt. Không tô xanh cả hàng chưa hội tụ chỉ vì đã tính xong.

### 12.3. Bảng tổng hợp phép lặp

| Vòng | `t_j` | `x_j` | Cận sai số `B_j` | Độ lệch `r_j` | Trạng thái |
|---:|---:|---:|---:|---:|---|
| 0 | Giá trị đầu | Giá trị đầu | — | — | Khởi tạo |
| 1… | Giá trị mới | Giá trị mới | Nếu có chứng nhận | Tại giá trị mới | Tiếp tục/Đạt/Lỗi |

Nếu chưa có chứng nhận, đổi tiêu đề cột `B_j` thành **“Độ thay đổi giữa hai bước theo x”**. Không để tiêu đề “cận sai số” rồi điền `step_x` vào đó.

Ở màn hình hẹp, có thể tách bảng `j,t_j,x_j` và bảng kiểm tra `j,B_j,r_j,trạng thái`; giữ cùng chỉ số vòng. Không thu nhỏ chữ đến mức khó đọc chỉ để nhét đủ cột.

### 12.4. Quy định định dạng

- Căn phải số trong bảng; căn trái diễn giải.
- Số cùng cột dùng cùng số chữ số hiển thị. Sai số nhỏ dùng dạng `6.11127 × 10⁻⁷` hoặc LaTeX tương đương.
- Chế độ chi tiết nên hiện khoảng 12 chữ số sau dấu thập phân cho các bài mẫu; đây là lựa chọn hiển thị, không phải lời khẳng định ngần ấy chữ số đúng so với hàm thật.
- Số âm khi thay vào công thức phải có ngoặc: `a - (-b)`.
- Không có `+ -0.56`; định dạng thành `-0.56`.
- Hệ số bằng 0 có thể được lược khỏi biểu thức rút gọn nhưng vẫn giữ trong bảng hệ số.
- Không dùng màu làm tín hiệu duy nhất: luôn có nhãn chữ, dấu ✓ hoặc cảnh báo.
- Không đánh đồng `—` (không áp dụng/chưa có) với `0` (giá trị tính được).
- Công thức phải render thành toán học, không hiện nguyên chuỗi `\frac` cho người dùng.
- Bản in lặp tiêu đề bảng khi qua trang; không tách nhãn bước khỏi công thức theo sau; giữ phần kiểm tra và quyết định gần vòng tương ứng.

## 13. Mẫu đầu ra hoàn chỉnh — Newton lùi

### 13.1. Bài toán và lựa chọn

**Tìm x khi y = 2 bằng lặp Newton lùi bậc 3.**

| Tham số | Giá trị |
|---|---|
| Khoảng đang giải | `(2.0, 2.2)` |
| Các mốc | `1.6, 1.8, 2.0, 2.2` |
| Các tung độ | `4.23, 3.67, 2.99, 1.24` |
| Gốc lùi | `2.2` |
| Bước h | `0.2` |
| Ngưỡng vị trí | `10^-6` |
| Ngưỡng độ lệch | `10^-6` |
| Số vòng tối đa minh họa | `100` |

✓ Các mốc hữu hạn, phân biệt, cách đều.

✓ Đủ bốn mốc cho bậc 3.

✓ Hai đầu khoảng trái dấu: `2.99 - 2 = 0.99 > 0`, `1.24 - 2 = -0.76 < 0`.

✓ Các tung độ giảm trên tập mốc đã chọn. Đây là kiểm tra trên bảng; chưa dùng nó để khẳng định hàm thật đơn điệu giữa mọi mốc.

### 13.2. Bảng sai phân lùi

| x | y | ∇y | ∇²y | ∇³y |
|---:|---:|---:|---:|---:|
| 1.6 | 4.23 | — | — | — |
| 1.8 | 3.67 | -0.56 | — | — |
| 2.0 | 2.99 | -0.68 | -0.12 | — |
| **2.2** | **1.24** | **-1.75** | **-1.07** | **-0.95** |

✓ Lấy các hệ số tại gốc `2.2`, không lấy hàng đầu của bảng tiến.

### 13.3. Đổi biến và lập phương trình

\[
t=\frac{x-2.2}{0.2},\qquad x=2.2+0.2t,\qquad t\in[-1,0].
\]

\[
P(t)=1.24-1.75t-\frac{1.07}{2}t(t+1)
-\frac{0.95}{6}t(t+1)(t+2).
\]

\[
H(t)=-\frac{1.07}{2}t(t+1)-\frac{0.95}{6}t(t+1)(t+2).
\]

\[
1.24-1.75t+H(t)=2
\quad\Longrightarrow\quad
t_{j+1}=\frac{H(t_j)-0.76}{1.75}.
\]

\[
t_0=\frac{2-1.24}{-1.75}=-0.434285714286.
\]

### 13.4. Chứng nhận hội tụ

Trên `J=[-1,0]`:

\[
0\le H(t)\le0.212916667.
\]

Ảnh của đoạn được bao bởi `[-0.434285715,-0.312619047]`, nằm trong `J` (cận thập phân làm tròn bao ngoài).

Đạo hàm:

\[
H'(t)=-0.475t^2-2.02t-511/600.
\]

Vì `H''(t)=-0.95t-2.02 < 0`, chỉ cần xét hai đầu để chặn `|H'|`:

\[
\max|\psi'(t)|=\frac{511/600}{1.75}=\frac{73}{150}<0.5.
\]

✓ Chọn `q=0.5`. ✓ Giá trị đầu nằm trong đoạn. ✓ Ảnh giữ nguyên đoạn.

Do đó:

\[
B_j=0.2|t_j-t_{j-1}|,\qquad r_j=|P(t_j)-2|.
\]

### 13.5. Chi tiết vòng 1

✓ Dùng `t_0=-0.434285714286`.

✓ Thay vào từng số hạng của `H`, rồi cộng:

\[
H(t_0)\approx0.192345320117.
\]

✓ Cập nhật:

\[
t_1=\frac{0.192345320117-0.76}{1.75}
\approx-0.324374102791.
\]

✓ Đổi biến:

\[
x_1=2.2+0.2(-0.324374102791)\approx2.135125179442.
\]

✓ Tính các đại lượng kiểm tra:

\[
B_1\approx2.19823223\times10^{-2},
\quad r_1\approx1.69535089\times10^{-2}.
\]

Vị trí: chưa đạt `10^-6`. Độ lệch: chưa đạt `10^-6`. **Tiếp tục.**

### 13.6. Chi tiết vòng 2

✓ Dùng giá trị mới nhất `t_1=-0.324374102791`.

\[
H(t_1)\approx0.175391811189,
\]

\[
t_2=\frac{0.175391811189-0.76}{1.75}
\approx-0.334061822178.
\]

\[
x_2\approx2.133187635564,
\]

\[
B_2\approx1.93754388\times10^{-3},
\quad r_2\approx2.30696296\times10^{-3}.
\]

Cả hai chưa đạt: **tiếp tục với t_2**.

### 13.7. Bảng lặp

| j | t_j | x_j | B_j | r_j | Quyết định |
|---:|---:|---:|---:|---:|---|
| 0 | -0.434285714286 | 2.113142857143 | — | — | Khởi tạo |
| 1 | -0.324374102791 | 2.135125179442 | 2.19823×10^-2 | 1.69535×10^-2 | Tiếp tục |
| 2 | -0.334061822178 | 2.133187635564 | 1.93754×10^-3 | 2.30696×10^-3 | Tiếp tục |
| 3 | -0.332743557629 | 2.133451288474 | 2.63653×10^-4 | 3.04510×10^-4 | Tiếp tục |
| 4 | -0.332917563310 | 2.133416487338 | 3.48011×10^-5 | 4.03637×10^-5 | Tiếp tục |
| 5 | -0.332894498348 | 2.133421100330 | 4.61299×10^-6 | 5.34736×10^-6 | Tiếp tục |
| **6** | **-0.332897553981** | **2.133420489204** | **6.11127×10^-7** | **7.08467×10^-7** | **✓ Đạt cả hai** |

### 13.8. Kết luận mẫu

**Kết quả: x ≈ 2.133420489204 sau 6 vòng.**

- ✓ Nằm trong khoảng đang xét `(2.0,2.2)`.
- ✓ Cận sai số lặp `6.11127×10^-7 <= 10^-6`.
- ✓ Độ lệch phương trình `7.08467×10^-7 <= 10^-6`.
- Phạm vi bảo đảm: nghiệm của đa thức nội suy đã chọn. Chưa có cận sai số mô hình hoặc sai số đầu vào để cam kết cùng độ chính xác với nghiệm hàm thật.

## 14. Hai mẫu đối chiếu còn lại

### 14.1. Hàm ngược — Lagrange và Newton phải khớp

Dữ liệu `x=[1,2,3]`, `y=[1,4,9]`, mức `6`, bậc `2`, nhánh dương. Bảng đảo có mốc `1,4,9` không cách đều.

Tỉ sai phân:

\[
T_{0,1}=1/3,\quad T_{1,1}=1/5,\quad T_{0,2}=-1/60.
\]

\[
Q_2(y)=1+(y-1)/3-(y-1)(y-4)/60.
\]

Lagrange tại `6` cho cơ sở `[-1/4,1,1/4]`, đóng góp `[-1/4,2,3/4]`. Cả hai cách cho `x_hat=2.5`.

Nếu biết hàm thật `f(x)=x²`, nghiệm thật là `sqrt(6)≈2.449489743`, nên sai số thực tế khoảng `0.050510257`. Bài mẫu không yêu cầu sai số `10^-6`. Độ lệch `2.5²-6=0.25` không chứng minh thuật toán hàm ngược đã code sai.

### 14.2. Lặp Newton tiến

Dùng `x=[1.6,1.8,2.0,2.2]`, `y=[4.23,3.67,2.99,1.24]`, mức `4`, khoảng `(1.6,1.8)`, bậc `3`.

Hệ số tiến: `c=[4.23,-0.56,-0.12,-0.95]`. Gốc `1.6`, bước `0.2`, đoạn `J=[0,1]`.

\[
H(t)=-0.06t(t-1)-\frac{0.95}{6}t(t-1)(t-2),
\]

\[
t_0=(4-4.23)/(-0.56)=0.410714285714,
\]

\[
t_{j+1}=\frac{-0.23-H(t_j)}{-0.56}.
\]

Có `Φ([0,1]) ⊂ [0.296130952,0.410714286] ⊂ [0,1]`. Cận chính xác của đạo hàm hàm lặp là `11/24 < 0.5`; chọn `q=0.5`. Dùng hai ngưỡng `10^-6`.

| j | t_j | x_j | B_j | r_j | Quyết định |
|---:|---:|---:|---:|---:|---|
| 0 | 0.410714285714 | 1.682142857143 | — | — | Khởi tạo |
| 1 | 0.327890163360 | 1.665578032672 | 1.65648×10^-2 | 1.25891×10^-3 | Tiếp tục |
| 2 | 0.330138219858 | 1.666027643972 | 4.49611×10^-4 | 7.86910×10^-5 | Tiếp tục |
| 3 | 0.329997700276 | 1.665999540055 | 2.81039×10^-5 | 4.84217×10^-6 | Tiếp tục |
| 4 | 0.330006347015 | 1.666001269403 | 1.72935×10^-6 | 2.98253×10^-7 | Tiếp tục |
| **5** | **0.330005814420** | **1.666001162884** | **1.06519×10^-7** | **1.83697×10^-8** | **✓ Đạt cả hai** |

Đặc biệt kiểm tra vòng 4: độ lệch đã đạt nhưng cận vị trí chưa đạt. Nếu chương trình dừng ở vòng 4 với hai ngưỡng trên thì logic dừng đang sai.

## 15. Mã trạng thái và thông báo lỗi

Các mã có thể đổi tên theo hệ thống hiện có, nhưng phải giữ khác biệt về ý nghĩa.

| Mã | Ý nghĩa/thông báo cho người đọc |
|---|---|
| `DIRECT_RESULT` | Đã tính xong kết quả theo mô hình hàm ngược; không có vòng hội tụ. |
| `NODE_MATCH` | Mốc dữ liệu đạt mức cần tìm; nêu rõ mốc. |
| `CERTIFIED_MODEL_CONVERGENCE` | Đủ chứng nhận co, đạt hai ngưỡng cho nghiệm mô hình. |
| `CONDITIONAL_MODEL_CONVERGENCE` | Đạt theo cận/giả thiết do người dùng cung cấp. |
| `PRACTICAL_STOP` | Đạt tiêu chuẩn thực hành; chưa có cận bảo đảm. |
| `INVALID_INPUT` | Thiếu/không hợp lệ, kèm trường và dòng cụ thể. |
| `DUPLICATE_X` | Mốc x trùng, không tự gộp. |
| `DUPLICATE_INVERSE_NODE` | Tung độ làm mốc đảo trùng; phép nội suy này không xác định. |
| `NONUNIFORM_GRID` | Tập mốc không đạt kiểm tra cách đều. |
| `INSUFFICIENT_NODES` | Tập tính thực sự ít hơn m+1 mốc cho bậc yêu cầu; không dùng cho khoảng nghiệm ở giữa bảng. |
| `EXTRAPOLATION_REQUIRES_SELECTION` | Mức ngoài miền tập mốc; cần lựa chọn ngoại suy tường minh nếu hỗ trợ. |
| `ZERO_LINEAR_DIFFERENCE` | Không lập được công thức lặp do mẫu d bằng 0. |
| `INITIAL_OUTSIDE_TARGET` | Cảnh báo t_0 ngoài T; không phải lỗi mốc và không chặn chế độ thực hành. |
| `ITERATE_OUTSIDE_TARGET` | Cảnh báo bước mới ra ngoài T; giữ trace, không kẹp biên. |
| `CERTIFICATE_UNAVAILABLE` | Người dùng chọn chỉ chạy có chứng nhận nhưng chưa đủ căn cứ áp dụng. |
| `CERTIFICATE_VIOLATION` | Đã công bố chứng nhận mà bước ra ngoài J; dừng kiểm tra tính đúng của chứng nhận/số học. |
| `CONVERGED_OUTSIDE_REQUESTED_BRACKET` | Đạt ngưỡng tại điểm ngoài khoảng yêu cầu; không ghi là đã tìm nghiệm trong khoảng. |
| `NUMERICAL_FAILURE` | Phép tính không hữu hạn hoặc tràn số, chỉ rõ bước. |
| `STAGNATED` | Giá trị không thay đổi trong số máy nhưng điều kiện dừng chưa đạt. |
| `MAX_ITERATIONS` | Hết số vòng mà chưa đạt; giữ giá trị cuối để xem. |
| `OUTSIDE_SELECTED_BRANCH` | Kết quả hàm ngược nằm ngoài nhánh/khoảng lựa chọn; cần xem lại, không tự ép về biên. |

Thông báo tốt phải có: điều gì không đạt, giá trị quan sát được, điều kiện cần và lựa chọn có thể sửa. Ví dụ: “Bậc tối đa 3 cần 4 mốc tính, tập đang chọn chỉ có 3.” Với tập đã có 36 mốc, không phát sinh thông báo cần 36 mốc nữa kể từ khoảng nghiệm.

## 16. Sai số: lời kết luận được phép in

### 16.1. Hàm ngược

Nếu biết `g=f^-1` thuộc lớp `C^(m+1)` và `M` chặn được đạo hàm cấp `m+1` trên đoạn chứa mọi tung độ liên quan:

\[
|g(\bar y)-Q_m(\bar y)|
\le\frac{M}{(m+1)!}\left|\prod_{i=0}^{m}(\bar y-y_i)\right|.
\]

Không biết `M` thì không chế ra cận từ số chữ số hiển thị hay sai khác hai phương pháp. Có thể hiển thị đối chiếu thực hành, ghi đúng tên.

### 16.2. Lặp thuận

`B_j` chặn khoảng cách đến nghiệm `x_P*` của mô hình `P_x`, không tự chặn khoảng cách đến nghiệm hàm thật.

Nếu có thêm `|f-P_x| <= E`, `|f'| >= mu > 0` trên đoạn chứa nghiệm thật và xấp xỉ, thì:

\[
|\hat x-x_{\mathrm{true}}|
\le\frac{E+|P_x(\hat x)-\bar y|}{\mu}.
\]

Phải ghi nguồn/giả thiết của `E` và `mu`. Không vừa cộng `B_j` vào công thức này vừa dùng chính độ lệch tại xấp xỉ mà không giải thích: đây là một cận hoàn chỉnh theo độ lệch tại điểm đang tính, không cần đếm sai số hai lần.

### 16.3. Dữ liệu

Sai số số liệu là thành phần khác. Nếu bảng chỉ có hai chữ số thập phân mà không biết sai số nguồn, không được mặc nhiên cho rằng chúng là giá trị đúng của hàm thật đến vô hạn chữ số. Chương trình có thể tính nghiệm của mô hình từ bảng đến ngưỡng nhỏ, nhưng lời kết luận phải nêu đúng phạm vi.

## 17. Kiểm chứng có ý nghĩa trước khi ghép vào ứng dụng

Không cần kiểm thử mọi câu chữ. Cần kiểm chứng các chỗ dễ sai về công thức, chỉ số và trạng thái.

1. **Đúng mốc:** đa thức tiến/lùi phải tái tạo từng tung độ tại các mốc đã chọn trong dung sai số học hợp lý. Đây là kiểm tra mô hình, không phải cận sai số đối với hàm thật.
2. **Lagrange và Newton hàm ngược:** cùng tập mốc phải cho cùng giá trị trong sai số số học; đối chiếu ví dụ mục 14.1.
3. **Mọi bậc:** thử `m=1,2,3` và bậc tối đa 35 với dữ liệu hồi quy ở mục 20 để phát hiện code viết cứng hoặc đòi mốc theo vị trí nghiệm. Với `m=1`, `H=0` và công thức lặp cho nghiệm tuyến tính trực tiếp.
4. **Hướng lùi:** kiểm tra `c_r=D[m-r][r]` và gốc phải; không chỉ kiểm tra ví dụ có sai phân cấp cao bằng 0.
5. **Dừng đúng:** ví dụ tiến không dừng ở vòng 4; dừng ở vòng 5. Ví dụ lùi dừng ở vòng 6 với q=0.5 và hai ngưỡng 10^-6.
6. **Cận sai số:** dùng một phương pháp độc lập như chia đôi đa thức để đối chiếu nghiệm mô hình, xác nhận sai số thực tế nhỏ hơn `B_j` đã công bố.
7. **Thất bại:** mốc trùng, lưới không đều, d=0, giá trị không hữu hạn, ra khỏi đoạn và hết vòng đều phải giữ đúng trạng thái; không trả nhãn thành công.
8. **Hiển thị:** công thức chứa số âm, ô trống, hệ số 0, cảnh báo chưa xác minh và hai bảng vòng lặp phải đọc được cả ở màn hình hẹp và bản in.

Ngưỡng đối chiếu số máy cần theo quy mô và phép tính; không yêu cầu mọi chuỗi thập phân cuối cùng giống tuyệt đối giữa các ngôn ngữ. Các số trong bài mẫu là giá trị tham chiếu đã làm tròn để trình bày.

## 18. Tiêu chí hoàn thành

- [ ] Không đòi gốc sát khoảng nghiệm; T tính từ khoảng và gốc thật.
- [ ] Phân biệt số mốc, bậc tối đa và số vòng lặp.
- [ ] Tập 36 mốc với khoảng ở giữa không bị báo thiếu mốc giả.
- [ ] Chế độ thực hành không bị chặn vì thiếu chứng nhận hoặc t ra khỏi T.
- [ ] Đạt ngưỡng ngoài khoảng yêu cầu được ghi trạng thái riêng.
- [ ] Người dùng lựa chọn được cả bốn phương pháp và bậc khả dụng.
- [ ] Không tự đổi phương pháp, nhánh, mốc, bậc hoặc khoảng.
- [ ] Tiền kiểm đầy đủ, có thông báo lỗi cụ thể.
- [ ] Bảng đảo/sai phân/tỉ sai phân và ô hệ số hiển thị đúng.
- [ ] Đa thức và công thức lặp có đầy đủ số hạng theo bậc đang chọn.
- [ ] Từng vòng lưu giá trị cũ, phần hiệu chỉnh, giá trị mới và các phép kiểm tra.
- [ ] Dấu ✓ chỉ gắn với công việc đã hoàn tất hoặc điều kiện đã đạt, không che các điều kiện chưa đạt.
- [ ] Phân biệt cận sai số với độ thay đổi bước; phân biệt chứng nhận với khảo sát số.
- [ ] Bảng và kết quả khớp ba bài mẫu trong PDF và guide.
- [ ] Lỗi/hết vòng không bị trình bày thành thành công.
- [ ] Không làm tròn trung gian theo số chữ số hiển thị.
- [ ] Kết luận sai số ghi đúng phạm vi nghiệm mô hình/hàm thật/số liệu.
- [ ] Lời giải đọc được, in được và giữ công thức đúng khi ngoại tuyến nếu ứng dụng có chức năng này.

## 19. Nguồn và quy ước đã hiệu chỉnh

Đối chiếu slide “Nội suy ngược” của Hà Thị Ngọc Yến, trang 2–9, và phần nội suy ngược trong bản chương 1 người dùng cung cấp, mục 1.6, các thuật toán A21–A25. PDF đi kèm giải thích lý thuyết và ba bài mẫu theo cùng quy ước.

Các điểm hiệu chỉnh quan trọng:

- Khởi tạo lùi dùng `∇y_(k+1) = y_(k+1)-y_k`, không phải `Δy_(k+1)` như lỗi ký hiệu ở slide cuối.
- `g=f^-1` là hàm ngược thật, `Q_m` là đa thức xấp xỉ; không dùng chung một ký hiệu cho cả hai khi viết sai số.
- Điều kiện `origin > 0` không cần thiết.
- Tính đơn điệu nghiêm ngặt phục vụ hàm ngược/tính duy nhất trên nhánh; không phải điều kiện bắt buộc của mọi bài toán tìm nghiệm.
- Sai phân cấp cao nhỏ chỉ gợi ý thực hành; không thay thế chứng nhận hội tụ.
- Không có giới hạn lý thuyết cứng ở bậc 3 trong các công thức này.


## 20. Kiểm thử hồi quy bắt buộc cho lỗi mốc ở giữa bảng

Đây là **dữ liệu tổng hợp để kiểm thử**, không phải bảng y của ảnh người dùng. Dùng số hữu tỉ hoặc độ chính xác đủ cao khi xác nhận giá trị tham chiếu; sai phân cấp cao của dữ liệu gần tuyến tính có thể bị nhiễu số máy.

\[
x_i=1+0.115i,\qquad y_i=2x_i-2.95,\qquad i=0,\ldots,35.
\]

Giữ đủ 36 mốc; mức 1.23; khoảng mục tiêu [2.035,2.15]. Vì phương trình thật là tuyến tính, nghiệm đúng là x=2.09. Các sai phân từ cấp 2 trở lên bằng 0 trong số học chính xác; đa thức có bậc thực tế 1 dù mô hình qua 36 mốc cho phép bậc tối đa 35.

| Đại lượng | Tiến trên toàn bộ 36 mốc | Lùi trên toàn bộ 36 mốc |
|---|---:|---:|
| Gốc | 1.0 | 5.025 |
| Bước h | 0.115 | 0.115 |
| Đoạn T | [9,10] | [-26,-25] |
| Sai phân bậc nhất d | 0.23 | 0.23 |
| H(t) | 0 | 0 |
| t_0 theo origin_linear | 218/23 ≈ 9.478260869565 | -587/23 ≈ -25.521739130435 |
| Nghiệm | 2.09 | 2.09 |
| Hệ số co | q=0, hàm lặp hằng trong T | q=0, hàm lặp hằng trong T |

Yêu cầu kiểm thử:

1. Không báo thiếu mốc ở cả hai hướng.
2. Không ép T về [0,1] hoặc [-1,0].
3. Không dịch gốc tới 2.035 hoặc 2.15.
4. Với dữ liệu tính chính xác, một lần cập nhật cho lại t_0, residual=0, cận=0. Kết quả x=2.09.
5. Khi dùng số máy, đối chiếu trong dung sai số học; không cắt các hệ số cấp cao về 0 âm thầm. Nếu có phép nhận dạng bậc thấp, phải là xử lý có ngưỡng công bố.
6. Giới hạn max_iterations=100 không thay số mốc, bậc hay hệ số.

Kiểm thử bổ sung: t_0 ngoài T nhưng công thức hữu hạn không bị báo thiếu mốc; chứng nhận không chứa t_0 không được áp dụng; bước thực hành rời T được ghi cảnh báo; một nghiệm đạt ngưỡng ngoài [a,b] không được báo là nghiệm của khoảng đã chọn.

## 21. Quy trình lựa chọn phương pháp để đưa vào phần Hướng dẫn

1. Nếu đề chỉ định phương pháp, dùng phương pháp đó và kiểm tra điều kiện thực sự của nó.
2. Nếu muốn tính trực tiếp trên một nhánh thích hợp, có các y_i phân biệt: chọn hàm ngược. Lagrange thuận tiện để trình bày từng đóng góp; Newton tỉ sai phân thuận tiện khi giữ bảng hệ số, thêm mốc hoặc tính nhiều mức y. Cùng tập mốc, hai cách cho cùng đa thức.
3. Nếu muốn giải mô hình thuận bằng hai phép lặp trong giáo trình: cần lưới x đều. Tiến lấy gốc đầu tập tính; lùi lấy gốc cuối. Cả hai hợp lệ cả khi khoảng nghiệm ở giữa tập, nhưng có công thức lặp và khả năng hội tụ khác nhau.
4. Nếu đang chọn mô hình cục bộ, gốc gần khoảng nghiệm thường giúp diễn giải và giữ |t| nhỏ; đủ mốc theo hướng tương ứng chỉ là điều kiện của lựa chọn cục bộ đó. Không áp thành giới hạn chung của toàn bảng.
5. Không đủ chứng nhận q<1: không tự coi là phân kỳ. Có thể thử thực hành với giới hạn vòng, theo dõi độ lệch; hoặc người dùng chọn lại gốc/tập mốc/bậc hay phương pháp giải phương trình khác. Không tự chuyển cách giải và ghi như vẫn dùng cách cũ.
6. Mốc không cách đều: hai công thức sai phân thường tiến/lùi trong guide không áp dụng; vẫn có thể dùng hàm ngược trên nhánh thích hợp, hoặc dựng đa thức thuận bằng công thức mốc bất kỳ rồi chọn bộ giải khác theo yêu cầu. Không bịa bước h.

Chỉ kiểm tra thực tế công thức và quỹ đạo mới biết phép lặp đã chọn có chạy tốt với dữ liệu cụ thể hay không. “Đủ mốc” không phải chứng minh hội tụ, và thiếu chứng minh hội tụ không phải thiếu mốc.
