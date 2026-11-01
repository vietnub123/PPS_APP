# Nội suy đa thức — lý thuyết, thuật toán và lời giải cần hiển thị

**Đặc tả đã được duyệt, 31/10/2026.** Đọc [phạm vi và tiến độ triển khai](00_Dac_ta_noi_suy_dao_ham_Horner_CHO_DUYET.md) trước. Các mục dưới đây là chuẩn thuật toán và đầu ra đã thống nhất; xem bài mẫu mới để đối chiếu với app.

## 1. Bài toán và chọn phương pháp

Cho m cặp `(x_i,y_i)`, các x phân biệt. Đặt `n=m−1`. Tìm đa thức P bậc không quá n sao cho `P(x_i)=y_i`. Có đúng một đa thức như vậy: hiệu của hai nghiệm có m nghiệm phân biệt nhưng bậc không quá m−1 nên phải bằng 0.

Nếu các y là giá trị của hàm f thì dùng `f(z) ≈ P(z)`. Nếu đề cho dữ liệu đúng là một đa thức bậc ≤n, đây là khôi phục chính đa thức đó. Không mặc định hàm thật là đa thức chỉ vì có bảng dữ liệu.

| Dữ kiện/yêu cầu | Chọn | Điều kiện |
|---|---|---|
| Mốc bất kỳ | Lagrange hoặc Newton tỉ sai phân | x phân biệt; không cần cách đều. |
| Mốc cách đều, gần đầu/cuối tập chọn | Newton tiến/lùi | Dùng đúng gốc đầu/cuối và đúng bảng hệ số. |
| Mốc đều, quanh tâm, mở về phải/trái trước | Gauss I/II | Công bố gốc và thứ tự mốc; có thể dùng cả số mốc chẵn/lẻ. |
| Mốc đều, tâm là một mốc | Stirling | Số mốc lẻ `2N+1`; tâm là mốc giữa tập chọn. |
| Mốc đều, tâm ở giữa hai mốc | Bessel | Số mốc chẵn `2N+2`; gốc là mốc bên trái của cặp giữa. |
| Đề chỉ định công thức | Làm đúng công thức đó | Điều kiện đại số phải hợp lệ; không tự đổi sang công thức khác. |

Cùng một tập mốc và dùng đủ hạng thì các phương pháp trên biểu diễn **cùng P**. Chọn công thức chủ yếu giúp tính/trình bày thuận tiện; không phải cứ đổi tên phương pháp là giảm sai số của cùng đa thức.

Các gợi ý như Stirling gần t=0, Bessel gần t=1/2, Newton tiến gần đầu là gợi ý chọn mốc/cách tính. Không từ chối Stirling chỉ vì `|t|>1/4`. Điểm ngoài tập mốc vẫn đánh giá được đa thức, nhưng phải ghi **ngoại suy**.

## 2. Hợp đồng đầu vào và chọn mốc

### 2.1. Dữ liệu chung

1. Đọc số hữu hạn, x/y cùng độ dài, giữ ID dòng nguồn.
2. Sắp x tăng cùng cả cặp; không sắp x và y riêng.
3. x trùng là lỗi dữ liệu nội suy: cùng x khác y là mâu thuẫn; cùng x cùng y cũng không âm thầm gộp. Yêu cầu xử lý rõ ràng.
4. Bỏ trống số mốc nghĩa là dùng toàn bộ. Nếu đề cho K mốc thì lấy đúng K, bậc tối đa K−1. Bậc thực có thể thấp hơn do hệ số cấp cao bằng 0.
5. Khi chọn một tập con tự động phải có điểm z hữu hạn và `1≤K≤m`. Không tự giảm K để qua điều kiện chẵn/lẻ.
6. Cấp đạo hàm là số nguyên không âm. Cấp 0 là giá trị hàm; chi tiết ở tài liệu 02.

### 2.2. Quy tắc chọn tự động đang dùng và cần công bố

- **Lưới đều:** xét từng cửa sổ K mốc liên tiếp, chọn cửa sổ có trung điểm hai đầu gần z nhất; nếu hòa chọn cửa sổ bên trái. Điều này giữ tính liên tiếp và lưới đều.
- **Lưới bất kỳ:** chọn K mốc có khoảng cách `|x_i−z|` nhỏ nhất, hòa theo thứ tự x tăng; sau đó sắp các mốc đã chọn tăng dần.
- Không gọi cả hai quy tắc là “lấy đối xứng” nếu thực tế tập chọn bị lệch ở biên.
- Bảng phải có: ID nguồn, chỉ số cục bộ, x, y, khoảng cách đến z. Ghi số mốc nhập/số mốc dùng và `[x_min,x_max]` của **tập chọn**.

Trên lưới không đều, đạo hàm từ bảng hiện có quy tắc chọn khác (§2 tài liệu 02). Cần nói rõ, không hứa hai màn hình sẽ tự chọn cùng tập mốc.

### 2.3. Kiểm tra lưới đều

Tính `h_i=x_(i+1)−x_i`, kiểm tra dương và bằng nhau trong dung sai số học được công bố. Kiểm tra theo **bước h**, không dùng dung sai tỉ lệ với trị tuyệt đối của x: dữ liệu `[10^12,10^12+1,10^12+3]` có bước 1 và 2, không phải lưới đều.

Hiện `common.spacing` lấy h đầu và so các bước bằng `rtol=10^−8, atol=0`. Bản trình bày cần ghi h được sử dụng và độ lệch bước lớn nhất khi cần kiểm tra. Dung sai kiểm tra lưới không phải mức sai số của đáp án. Không làm tròn các x về lưới lý tưởng mà không công bố.

Một mốc: P là hằng số. Có thể tính giá trị/đạo hàm bằng 0 mà không có h hình học; ghi “không cần đổi biến”. Bessel tối thiểu hai mốc; Stirling một mốc là trường hợp hằng số suy biến, không tạo bảng sai phân giả.

## 3. Hai bảng cơ bản

Trong mục này dùng chỉ số toàn cục `i=0,…,n`.

### 3.1. Sai phân tiến — chỉ dùng cho mốc đều

$$
 A_{i,0}=y_i,\qquad A_{i,k}=A_{i+1,k-1}-A_{i,k-1}=\Delta^k y_i,
 \quad 0\le i\le n-k.
$$

```text
A[i,0] = y[i]                       i=0..n
for k=1..n:
    for i=0..n-k:
        A[i,k] = A[i+1,k-1] - A[i,k-1]
```

Hiển thị một tam giác: hàng i gắn với mốc **bắt đầu** của `Δ^k y_i`. Ô ngoài tam giác không xác định, để trống. Có một phép thế mẫu, chẳng hạn `Δ²y_i=Δy_(i+1)−Δy_i`; chi tiết có thể xem mọi phép trừ.

### 3.2. Tỉ sai phân — cho mốc bất kỳ

$$
 D_{i,0}=y_i,\qquad
 D_{i,k}=\frac{D_{i+1,k-1}-D_{i,k-1}}{x_{i+k}-x_i}
       =f[x_i,\ldots,x_{i+k}].
$$

Mã giả như trên nhưng chia thêm `x[i+k]−x[i]`. Mẫu số phải khác 0. Không chia thêm k! vào hệ số tỉ sai phân. Với mốc đều: `D_(i,k)=Δ^k y_i/(k!h^k)`.

Bảng số lưu theo i bắt đầu. Nếu dùng ảnh tam giác neo tại **mốc kết thúc**, phải ghi `f[x_i,…,x_(i+k)]` và chỉ rõ hàng kết thúc i+k; không mô tả ảnh đó là cùng hàng bắt đầu. Chọn một cách trình bày nhất quán, giữ chỉ số đầy đủ để đọc được cả hai.

## 4. Lagrange

Đặt

$$
 W(x)=\prod_{j=0}^{n}(x-x_j),\quad
 d_i=\prod_{j\ne i}(x_i-x_j),\quad
 W_i(x)=\prod_{j\ne i}(x-x_j),\quad
 D_i=\frac{y_i}{d_i}.
$$

$$
 L_i(x)=\frac{W_i(x)}{d_i},\qquad
 P(x)=\sum_{i=0}^{n}y_iL_i(x)=\sum_{i=0}^{n}D_iW_i(x).
$$

`D_i` ở đây là hệ số Lagrange, khác bảng tỉ sai phân `D_(i,k)` mục 3.2. Giao diện cần ghi tên đầy đủ hoặc dùng ký hiệu khác để tránh nhầm.

```text
P = 0
for i=0..n:
    d = 1; Wi = đa thức 1
    for j=0..n, j != i:
        d *= x[i]-x[j]
        Wi *= (x-x[j])
    Di = y[i]/d
    P += Di*Wi
```

**Phải trình bày:** dữ liệu; công thức; bảng `i,x_i,y_i,d_i,D_i`; các tích W_i; phép ghép P; bảng tại z gồm `i,W_i(z),D_iW_i(z),tổng tích lũy`. Nếu hỏi đạo hàm, thêm bảng W_i^(k)(z) và đóng góp (tài liệu 02).

Nếu đề/giáo viên yêu cầu bảng tích W và chia Horner: cho thêm quá trình `W_(r+1)=W_r(x−x_r)`, `W_0=1`, sau đó chia W cho từng `(x−x_i)` để lấy W_i, ghi thương và số dư 0. Đây là cách dựng tương đương, không phải điều kiện cần mới của Lagrange.

Không tính `W(z)/(z−x_i)` khi z trùng x_i: đó là dạng 0/0. Dùng tích bỏ mốc trực tiếp, hoặc phép chia đa thức đã thực hiện trước. Kiểm tra `ΣL_i(z)=1`, `P(x_i)=y_i`.

### Ví dụ tự dựng: mốc không đều

`x=[0,1,3]`, `y=[1,3,13]`, tính tại z=2.

| i | d_i | D_i | W_i(x) | D_i W_i(2) |
|---|---:|---:|---|---:|
| 0 | 3 | 1/3 | (x−1)(x−3) | −1/3 |
| 1 | −2 | −3/2 | x(x−3) | 3 |
| 2 | 6 | 13/6 | x(x−1) | 13/3 |

`P(x)=x²+x+1`, `P(2)=7`. Chỉ số âm ở mẫu d_1 phải được giữ; không thay mọi hiệu bằng trị tuyệt đối.

## 5. Newton tỉ sai phân tiến và lùi

### 5.1. Tiến từ đầu trái

$$
 P(x)=\sum_{k=0}^{n}c_kB_k(x),\quad
 c_k=D_{0,k},\quad B_0=1,\quad B_k=\prod_{j=0}^{k-1}(x-x_j).
$$

Lập bảng D; đặt `B=1,P=0`; mỗi k lấy `c_k`, cộng `c_kB`; trước hạng k+1 nhân B với `(x−x_k)`. Ghi cả B dạng tích và hệ số nếu cần khai triển.

### 5.2. Lùi từ đầu phải

$$
 P(x)=\sum_{k=0}^{n}\tilde c_k\tilde B_k(x),\quad
 \tilde c_k=D_{n-k,k},\quad
 \tilde B_k=\prod_{j=0}^{k-1}(x-x_{n-j}).
$$

Hệ số bậc 0 là y_n. Không lấy hệ số tiến ghép với tích lùi. Thứ tự đánh giá lồng là `x_n,x_(n−1),…`, và hệ số phải theo đúng thứ tự đó.

**Bảng chính:** `k, nguồn D_(i,k), giá trị c_k, B_k, B_k(z), đóng góp, tổng`. Bảng tỉ sai phân đặt phía trên; màu ô được chọn trùng các nguồn c_k.

Ví dụ tự dựng mục 4 có bảng:

| x | y | D_(i,1) | D_(i,2) |
|---:|---:|---:|---:|
| 0 | 1 | 2 | 1 |
| 1 | 3 | 5 | |
| 3 | 13 | | |

Tiến: `1+2x+x(x−1)`; lùi: `13+5(x−3)+(x−3)(x−1)`. Cả hai bằng `x²+x+1` và tại 2 bằng 7. Không chia hệ số cuối 1 cho 2!.

## 6. Newton sai phân tiến và lùi

### 6.1. Tiến

Gốc `a=x_0`, `t=(x−a)/h`:

$$
 Q(t)=P(a+ht)=\sum_{k=0}^{n}\frac{\Delta^k y_0}{k!}B_k(t),
 \quad B_0=1,\quad B_{k+1}=B_k(t-k).
$$

### 6.2. Lùi

Gốc `a=x_n`, `t=(x−a)/h`:

$$
 Q(t)=\sum_{k=0}^{n}\frac{\Delta^k y_{n-k}}{k!}B_k(t),
 \quad B_0=1,\quad B_{k+1}=B_k(t+k).
$$

Tương đương dùng `∇^k y_n=Δ^k y_(n−k)`. Nếu bảng lưu Δ thì ghi đúng Δ và hàng bắt đầu; không đổi ký hiệu thành ∇ nhưng giữ nguyên hàng một cách mơ hồ.

```text
F = 1; B = 1; Q = 0
for k=0..n:
    if k>0: F *= k
    sigma = A[0,k]                  # tiến
         hoặc A[n-k,k]             # lùi
    beta = sigma/F
    Q += beta*B
    ghi k, vị trí sigma, sigma, F, beta, B
    B *= (t-k)                     # tiến, chuẩn bị hạng sau
         hoặc (t+k)                # lùi
```

Bảng thế số có `B_k(t_z), beta_k B_k(t_z), tổng`. Ghi rõ `t_z=(z−a)/h`. Giữ giai thừa đúng một lần. Không ép tiến có t∈[0,1] hoặc lùi có t∈[−1,0] như điều kiện tồn tại của đa thức.

## 7. Gauss I và Gauss II

Đổi sang **chỉ số quanh gốc**: `x_j=a+jh`, `t=(x−a)/h`. Nếu vị trí gốc trong mảng là c thì `y_j` chính là dữ liệu hàng `c+j`; `Δ^k y_j=A_(c+j,k)`.

### 7.1. Gốc và thứ tự mốc

| Phương pháp | Vị trí gốc trong m mốc đã sắp | Thứ tự độ lệch r_j |
|---|---|---|
| Gauss I | `c=floor((m−1)/2)` | 0,1,−1,2,−2,…, chỉ giữ mốc có trong tập |
| Gauss II | `c=floor(m/2)` | 0,−1,1,−2,2,…, chỉ giữ mốc có trong tập |

Với m lẻ hai gốc trùng nhau; với m chẵn chúng là hai mốc giữa khác nhau. Bảng phải có ID gốc và toàn bộ thứ tự r_j, không chỉ ghi “x₀” mà để người đọc đoán là đầu bảng hay giữa bảng.

### 7.2. Công thức đầy đủ, không dừng ở dấu ba chấm

Đặt `B_0=1`, `B_k(t)=∏_(j=0)^(k−1)(t−r_j)`.

$$
 Q_{\mathrm{GI}}(t)=\sum_{k=0}^{n}
       \frac{\Delta^k y_{-\lfloor k/2\rfloor}}{k!}B_k(t),
$$

$$
 Q_{\mathrm{GII}}(t)=\sum_{k=0}^{n}
       \frac{\Delta^k y_{-\lceil k/2\rceil}}{k!}B_k(t).
$$

| k | B_k Gauss I | nguồn GI | B_k Gauss II | nguồn GII |
|---|---|---|---|---|
| 0 | 1 | y_0 | 1 | y_0 |
| 1 | t | Δy_0 | t | Δy_−1 |
| 2 | t(t−1) | Δ²y_−1 | t(t+1) | Δ²y_−1 |
| 3 | t(t−1)(t+1) | Δ³y_−1 | t(t+1)(t−1) | Δ³y_−2 |
| 4 | t(t−1)(t+1)(t−2) | Δ⁴y_−2 | t(t+1)(t−1)(t+2) | Δ⁴y_−2 |

Mã giả: tạo thứ tự r; lập bảng Δ; mỗi k lấy nguồn theo công thức, chia k!, nhân B_k và cộng; cập nhật `B_(k+1)=B_k(t−r_k)`. Các tập mốc trên luôn cho các ô nguồn hợp lệ; sai chỉ số phải được phát hiện, không thay bằng 0.

## 8. Stirling — 2N+1 mốc

### 8.1. Ký hiệu và công thức tổng quát

Mốc chọn `x_−N,…,x_0,…,x_N`, `a=x_0`, `t=(x−a)/h`. Đặt `Q(t)=P(a+ht)`.

$$
\begin{aligned}
Q(t)=y_0
&+\sum_{r=0}^{N-1}
 \frac{\Delta^{2r+1}y_{-r-1}+\Delta^{2r+1}y_{-r}}{2(2r+1)!}
 t\prod_{j=1}^{r}(t^2-j^2)\\
&+\sum_{r=1}^{N}
 \frac{\Delta^{2r}y_{-r}}{(2r)!}
 t^2\prod_{j=1}^{r-1}(t^2-j^2).
\end{aligned}
$$

Tích rỗng bằng 1. Hạng 0 là y_0. Hạng lẻ dùng **trung bình hai ô** rồi chia k!, hạng chẵn dùng **một ô** rồi chia k!. Không chia thêm 2 vào hạng chẵn.

| k | σ_k trước chia k! | B_k(t) |
|---|---|---|
| 0 | y_0 | 1 |
| 1 | (Δy_−1+Δy_0)/2 | t |
| 2 | Δ²y_−1 | t² |
| 3 | (Δ³y_−2+Δ³y_−1)/2 | t(t²−1) |
| 4 | Δ⁴y_−2 | t²(t²−1) |
| 5 | (Δ⁵y_−3+Δ⁵y_−2)/2 | t(t²−1)(t²−4) |
| 6 | Δ⁶y_−3 | t²(t²−1)(t²−4) |
| 7 | (Δ⁷y_−4+Δ⁷y_−3)/2 | t(t²−1)(t²−4)(t²−9) |
| 8 | Δ⁸y_−4 | t²(t²−1)(t²−4)(t²−9) |

### 8.2. Mã giả

```text
kiểm tra m=2N+1; c=N; a=x[c]; lập bảng A
Q = đa thức y[c]
ghi hạng 0
for r=0..N-1:
    k = 2r+1
    u = A[c-r-1,k]; v = A[c-r,k]
    sigma = (u+v)/2
    B = t * product(t^2-j^2, j=1..r)
    beta = sigma/k!
    Q += beta*B
    ghi hai ô u,v, phép trung bình, sigma,k!,beta,B

    k = 2r+2
    sigma = A[c-r-1,k]
    B = t^2 * product(t^2-j^2, j=1..r)
    beta = sigma/k!
    Q += beta*B
    ghi ô nguồn, sigma,k!,beta,B
```

Mã giả dùng k! để dễ đọc; triển khai được phép cập nhật giai thừa và các tích đệ quy để tránh lặp việc. Không chuyển giai thừa lớn sang float trước khi chia.

### 8.3. Bảng cần xuất trong lời giải

1. Tập chọn: ID nguồn, j=−N,…,N, x_j,y_j; giải thích tâm/gốc.
2. Một bảng sai phân đầy đủ, đánh dấu cả hai ô nguồn của mỗi hạng lẻ.
3. Bảng lập hạng: `k, nguồn, u/v nếu có, σ_k, k!, β_k=σ_k/k!, B_k(t)`.
4. Q dạng tích đã **thế hệ số số**; Q khai triển theo t là dạng phụ để đối chiếu.
5. Bảng thế số: `k, B_k(t_z), β_kB_k(t_z), tổng`.
6. Nếu cần đạo hàm: thêm bảng đạo hàm cơ sở, đóng góp đã chia h^s và tổng; không chỉ in một dòng đáp số.
7. Kết luận có cả P(z) và P'(z) nếu bài hỏi cả hai. Quy định đề xuất: khi yêu cầu cấp s>0, luôn hiện P(z) và cấp s; các cấp trung gian nằm ở chi tiết.

### 8.4. Ví dụ tự dựng, kiểm lại được toàn bộ

`x=[−2,−1,0,1,2]`, `y=[17,1,1,5,25]`, z=1/4. N=2, a=0,h=1,t_z=1/4.

| j | y_j | Δy_j | Δ²y_j | Δ³y_j | Δ⁴y_j |
|---:|---:|---:|---:|---:|---:|
| −2 | 17 | −16 | 16 | −12 | 24 |
| −1 | 1 | 0 | 4 | 12 | |
| 0 | 1 | 4 | 16 | | |
| 1 | 5 | 20 | | | |
| 2 | 25 | | | | |

σ_1=(0+4)/2=2; σ_2=4; σ_3=(−12+12)/2=0; σ_4=24. Do đó

$$
 Q(t)=1+2t+2t^2+0\,t(t^2-1)+t^2(t^2-1)=1+2t+t^2+t^4.
$$

| k | β_k | B_k(1/4) | đóng góp P | B'_k(1/4) | đóng góp P' (h=1) |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 1 | 1 | 0 | 0 |
| 1 | 2 | 1/4 | 1/2 | 1 | 2 |
| 2 | 2 | 1/16 | 1/8 | 1/2 | 1 |
| 3 | 0 | −15/64 | 0 | −13/16 | 0 |
| 4 | 1 | −15/256 | −15/256 | −7/16 | −7/16 |

`P(1/4)=401/256=1.56640625`; `P'(1/4)=41/16=2.5625`. Hạng k=3 bằng 0 vẫn xuất hiện để biết đã xét đủ cấp.

### 8.5. Mẫu đề 20241 — dữ liệu thật trong repo

Nguồn `../20241GKtest2.xlsx`, Sheet3; điểm cần tính D1=4. Chọn 9 mốc của câu c, chỉ số dữ liệu gốc 22..30, dòng Excel 24..32. Đây là tập đã dùng trong bài giải cũ, được ghi lại để duyệt yêu cầu đầu ra.

| j | x_j | y_j |
|---:|---:|---:|
| −4 | 3.574 | 6.3054 |
| −3 | 3.691 | 6.1283 |
| −2 | 3.808 | 5.9039 |
| −1 | 3.925 | 5.6358 |
| 0 | 4.042 | 5.3284 |
| 1 | 4.159 | 4.9864 |
| 2 | 4.276 | 4.6151 |
| 3 | 4.393 | 4.2201 |
| 4 | 4.510 | 3.8074 |

`h=0.117`, `t_z=(4−4.042)/0.117=−14/39`. |t_z|≈0.359 không phải lý do loại Stirling: đề yêu cầu Stirling và dữ liệu thỏa điều kiện.

| k | phép lấy σ_k | σ_k | β_k |
|---:|---|---:|---:|
| 0 | y_0 | 5.3284 | 5.3284 |
| 1 | (−0.3074−0.3420)/2 | −0.3247 | −0.3247 |
| 2 | Δ²y_−1 | −0.0346 | −0.0173 |
| 3 | (0.0047+0.0053)/2 | 0.005 | 1/1200 |
| 4 | Δ⁴y_−2 | 0.0006 | 1/40000 |
| 5 | (0.0003−0.0003)/2 | 0 | 0 |
| 6 | Δ⁶y_−3 | −0.0006 | −1/1200000 |
| 7 | (−0.0014+0.0010)/2 | −0.0002 | −1/25200000 |
| 8 | Δ⁸y_−4 | 0.0024 | 1/16800000 |

$$
\begin{aligned}
Q_8(t)={}&5.3284-0.3247t-0.0173t^2
+\frac{t(t^2-1)}{1200}
+\frac{t^2(t^2-1)}{40000}\\
&-\frac{t^2(t^2-1)(t^2-4)}{1200000}
-\frac{t(t^2-1)(t^2-4)(t^2-9)}{25200000}\\
&+\frac{t^2(t^2-1)(t^2-4)(t^2-9)}{16800000}.
\end{aligned}
$$

Tool sau sửa phải tự lập được bảng thế từng hạng Q và Q'/h từ dữ liệu này. Đáp số đối chiếu:

$$
 P_8(4)\approx5.442986424022284,\qquad
 P'_8(4)\approx-2.673281525949639.
$$

Các đáp số này là giá trị của mô hình qua 9 cặp đã nhập. Chưa có cận sai số với hàm thật vì đề/bảng chưa cho cận đạo hàm cần thiết. Việc các số này từng được script riêng tính ra không có nghĩa bảng thế từng hạng đã có trong GUI.

Bảng thế số mẫu cần sinh từ cùng mô hình (các ô dưới làm tròn, tổng dùng số đầy đủ):

| k | B_k(t_z) | β_k B_k(t_z) | B'_k(t_z) | β_k B'_k(t_z)/0.117 |
|---:|---:|---:|---:|---:|
| 0 | 1 | 5.3284 | 0 | 0 |
| 1 | −0.358974358974 | 0.116558974359 | 1 | −2.77521367521 |
| 2 | 0.128862590401 | −0.00222932281394 | −0.717948717949 | 0.106158229235 |
| 3 | 0.312715993189 | 0.000260596660991 | −0.613412228797 | −0.00436903296864 |
| 4 | −0.112257023196 | −0.00000280642557990 | 0.532915254809 | 0.000113870780942 |
| 5 | −1.21056657982 | 0 | 2.15008898001 | 0 |
| 6 | 0.434562361985 | −0.000000362135301654 | −1.98239339315 | 0.0000141196110623 |
| 7 | 10.7391024730 | −0.000000426154860040 | −18.2046100606 | 0.00000617440308661 |
| 8 | −3.85506242621 | −0.000000229468001560 | 17.2740906999 | 0.00000878820243176 |
| Tổng | | **5.442986424022284** | | **−2.673281525949639** |

Đây mới là bảng tính thêm được yêu cầu cho tool. Nó không phải ảnh chụp hay bản sao của bảng hiện có trên màn hình.

## 9. Bessel — 2N+2 mốc

Chỉ số `j=−N,…,N+1`; gốc a=x_0 là mốc bên trái của cặp giữa, `t=(x−a)/h`. Đặt

$$
 E_0=1,\qquad E_r(t)=\prod_{j=0}^{r-1}(t+j)(t-j-1).
$$

$$
 Q(t)=\sum_{r=0}^{N}
 \left[
 \frac{\Delta^{2r}y_{-r}+\Delta^{2r}y_{-r+1}}{2(2r)!}E_r(t)
 +\frac{\Delta^{2r+1}y_{-r}}{(2r+1)!}(t-\tfrac12)E_r(t)
 \right].
$$

Hạng chẵn lấy trung bình **hai ô**, hạng lẻ lấy **một ô**. Hạng đầu là `(y_0+y_1)/2`, không phải y_0. Hai hạng đầu cộng lại chính là đường thẳng qua hai mốc giữa.

```text
c=N; lập A; E=1; Q=0
for r=0..N:
    k=2r
    sigma_even=(A[c-r,k]+A[c-r+1,k])/2
    Q += sigma_even/k! * E
    ghi hạng chẵn, hai ô nguồn và phép trung bình
    k=2r+1
    sigma_odd=A[c-r,k]
    Q += sigma_odd/k! * (t-1/2)*E
    ghi hạng lẻ và ô nguồn
    E *= (t+r)*(t-r-1)
```

Bảng/bố cục như Stirling nhưng đúng quy tắc trung bình Bessel. Với 2 mốc N=0, kết quả phải là nội suy tuyến tính; tại t=1/2, tất cả hạng lẻ triệt tiêu nhưng đạo hàm của chúng có thể khác 0.

### Ví dụ tự dựng

`x=[−1,0,1,2]`, `y=[0,1,2,9]` (từ `x³+1`), a=0,h=1,z=1/2.

Sai phân: Δ=[1,1,7], Δ²=[0,6], Δ³=[6]. Các hạng:

$$
 Q(t)=\frac32+(t-\tfrac12)+\frac32t(t-1)
       +(t-\tfrac12)t(t-1)=1+t^3.
$$

Tại t=1/2: đóng góp giá trị `3/2,0,−3/8,0`, tổng `9/8=1.125`; đóng góp đạo hàm `0,1,0,−1/4`, tổng `3/4=0.75`. Không bỏ hạng lẻ khỏi quá trình tính đạo hàm chỉ vì giá trị hạng lẻ tại tâm bằng 0.

## 10. Khai triển, đánh giá và giữ vết tính

Mỗi hạng có thể được lưu dưới dạng `(nguồn σ_k, β_k, các nhân tử B_k)`. Để khai triển bảng tích, dùng hệ số bậc tăng `b_0,…,b_d`. Nhân với `(u−r)`:

$$
 \tilde b_0=-rb_0,\quad
 \tilde b_j=b_{j-1}-rb_j\ (1\le j\le d),\quad
 \tilde b_{d+1}=b_d.
$$

Tạo mảng mới hoặc cập nhật đúng chiều; ghi thứ tự hệ số ở đầu bảng. Tổng hệ số của Q là tổng β_k nhân hệ số B_k.

Có thể đánh giá số ổn định bằng Newton lồng tương đương trên cùng tập mốc. **Phải tách hai việc:** lời giải theo công thức đã chọn và cách đánh giá số bên trong. So sánh hai kết quả trong độ chính xác phù hợp. Nếu lệch đáng kể, báo mất chính xác khi khai triển/cộng hạng; không giấu chênh lệch và không đổi mốc.

Không bắt buộc khai triển Q((x−a)/h) thành các lũy thừa x rất lớn chỉ để “đẹp”. Dạng Q(t) kèm định nghĩa t là một đa thức hoàn chỉnh.

## 11. Sai số và kiểm tra

Nếu `f∈C^m` trên đoạn chứa tập mốc và z, dữ liệu chính xác `y_i=f(x_i)`:

$$
 f(z)-P(z)=\frac{f^{(m)}(\xi_z)}{m!}\prod_{i=0}^{m-1}(z-x_i),\qquad
 |f(z)-P(z)|\le\frac{M_m}{m!}\left|\prod_i(z-x_i)\right|.
$$

M_m phải là cận đúng trên đoạn liên quan. Không có M_m thì chỉ ghi chưa có cận. Hạng đầu bị bỏ là gợi ý ước lượng khi có căn cứ, không mặc định là cận bảo đảm.

Nếu dữ liệu có sai lệch `|δy_i|≤η_i`, phần sai lệch đa thức do dữ liệu thỏa `|δP(z)|≤Σ|L_i(z)|η_i`. Tăng bậc có thể tăng khuếch đại nhiễu và dao động; tăng chữ số tính không loại bỏ điều này.

Đối chiếu: P tại mốc; tổng L_i; cùng tập mốc giữa các dạng; công thức đổi biến; các hạng cấp cao bằng 0 với dữ liệu bậc thấp. Sai lệch tại mốc nhỏ chỉ là kiểm tra thực hiện, không là cận sai số giữa mốc của hàm thật.

## 12. Danh sách ca biên để nghiệm thu sau duyệt

| Ca | Hành vi cần có |
|---|---|
| Stirling bảng nhập 100 mốc, chọn 9 | Chạy đúng 9; công bố ID và h. Dùng toàn 100 thì báo cần số lẻ, không tự bỏ 1. |
| Stirling 101/501 mốc | Giữ đủ dữ liệu khi được chọn; không tràn vì giai thừa float; có vết hệ số và xuất đủ. Không hứa kết quả luôn ổn định. |
| Bessel 2/4/8 mốc | Đúng các hạng cuối, không truy cập ô ngoài bảng. |
| Gauss số mốc 1..10 | Đúng gốc/thứ tự/chỉ số cả chẵn lẫn lẻ. |
| Điểm ở đầu/cuối/ngoài tập | Không đòi thêm mốc ngoài tập đã chọn; công bố tập bị lệch và ngoại suy nếu có. |
| z trùng mốc hoặc t=0,±1,… | Không chia cho nhân tử bằng 0 khi đánh giá/đạo hàm. |
| y hằng, bậc thực thấp | Hạng 0 được giữ; đạo hàm phù hợp; các hệ số 0 không bị coi là thiếu dữ liệu. |
| Mốc trùng, NaN/Inf, K sai | Báo đúng nguyên nhân, chưa tạo đáp số thành công. |
| Mốc không đều hoặc gốc 10^12 | Chọn thuật toán hợp lệ; kiểm tra theo khoảng mốc; không nhận nhầm lưới đều. |
| Hệ số/giá trị vượt miền số | Ghi thất bại số học và gợi ý đổi đơn vị/tập mốc do người dùng chọn; không in Inf thành đáp án. |
| Đề hỏi giá trị và đạo hàm | Cùng tập mốc, cùng Q, đủ cả hai bảng thế số và kết luận. |

Tài liệu này không cấp phép tự thay đổi mô hình để vượt lỗi. Việc sửa thuật toán/trình bày chỉ thực hiện sau khi bản đặc tả được duyệt.

## 13. Thuật toán bổ trợ liên quan trực tiếp đến nội suy

### 13.1. Sinh mốc Chebyshev khi được quyền chọn nơi lấy dữ liệu

Với bậc n≥0, số mốc m=n+1, đoạn a<b, dùng nghiệm Chebyshev:

$$
 x_i=\frac{a+b}{2}+\frac{b-a}{2}
       \cos\frac{(2i+1)\pi}{2m},\qquad i=0,\ldots,m-1.
$$

```text
kiểm tra n nguyên không âm, a<b hữu hạn
m=n+1
for i=0..m-1:
    theta=(2i+1)*pi/(2m)
    x[i]=(a+b)/2+(b-a)/2*cos(theta)
sắp x tăng, kiểm tra các x còn phân biệt trong biểu diễn số
```

Đầu ra: bậc/số mốc/đoạn; bảng `i,theta_i,x_i`; nhắc phải tính hoặc đo y mới tại các mốc này. Không gán các y của bảng cũ cho x mới. Bộ mốc nghiệm này không chứa hai đầu a,b; không nhầm với mốc cực trị Chebyshev có chứa đầu đoạn.

Nếu `|f^(m)|≤M_m` trên [a,b] và dùng đúng m mốc này, cận giá trị trên toàn đoạn là

$$
 \|f-P\|_\infty\le
 \frac{M_m(b-a)^m}{2^{2m-1}m!}.
$$

Đây là cực tiểu hóa chuẩn tích mốc monic, không bảo đảm mọi hàm sẽ có sai số thực nhỏ nhất trong mọi cách chọn mốc. API `chebyshev_global_bound` cần truyền a,b thật; không suy a,b từ min/max của các nghiệm đã sinh.

Ví dụ tự dựng n=2,[a,b]=[−1,1]: các mốc tăng là `−√3/2,0,√3/2`; chưa có y thì chưa lập được đa thức nội suy.

### 13.2. Thêm một mốc vào Newton

Giữ thứ tự mốc cũ, đánh giá P_n tại mốc mới bằng Horner Newton, rồi tính hệ số hạng mới theo [03, §7](03_Horner_Thuat_toan_va_trinh_bay_CHO_DUYET.md#7-horner-cho-đa-thức-newton). Không dựng lại bảng cũ nếu không cần; không nhầm thêm mốc với tăng số vòng hội tụ.

### 13.3. Điền tung độ thiếu khi đề cho bậc tối đa d

Đây là bài riêng, không phải giấy phép bỏ các dòng thiếu ở đầu vào nội suy thông thường.

```text
kiểm tra x phân biệt, d nguyên không âm
đánh dấu các y đã biết và còn thiếu
cần ít nhất d+1 mốc có y đã biết
chọn công khai d+1 mốc đã biết, dựng P_d bằng Newton/Lagrange
với mọi mốc đã biết còn lại:
    kiểm tra P_d(x_i) phù hợp y_i theo dung sai dữ liệu được công bố
nếu mâu thuẫn: báo không tương thích với giả thiết bậc d
nếu phù hợp: điền P_d(x_i) ở các ô thiếu
```

Lời giải có tập dựng P, P dạng tích, bảng đối chiếu các mốc đã biết, bảng giá trị điền và trạng thái tương thích. Khi dữ liệu chính xác, yêu cầu khớp chính xác theo số học phù hợp; với số đo thì dung sai phải có ý nghĩa và được công bố, không tự biến bài này thành bình phương tối thiểu.

Ví dụ tự dựng: x=[0,1,2,3], y=[0,thiếu,4,9],d=2 → P=x², điền y(1)=1. Nếu chỉ biết y ở 0 và 3 thì thiếu điều kiện cho d=2; không tự chọn một nghiệm trong vô số đa thức.
