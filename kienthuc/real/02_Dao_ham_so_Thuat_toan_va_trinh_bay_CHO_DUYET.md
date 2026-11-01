# Đạo hàm số — lý thuyết, thuật toán và lời giải cần hiển thị

**Đặc tả đã được duyệt, 31/10/2026.** Xem [phạm vi](00_Dac_ta_noi_suy_dao_ham_Horner_CHO_DUYET.md) và [các công thức nội suy](01_Noi_suy_da_thuc_Thuat_toan_va_trinh_bay_CHO_DUYET.md). Đây là chuẩn thuật toán và đầu ra đã thống nhất.

## 1. Nhận diện ba loại bài

| Đề cho | Cách giải | Ý nghĩa kết quả |
|---|---|---|
| Đa thức P và yêu cầu P^(s)(c) | Horner lặp, tài liệu 03 | Đạo hàm chính đa thức đã cho; không có sai số xấp xỉ nội suy. |
| Bảng, yêu cầu dựng Stirling/Newton/… rồi tính f' | Dựng đúng P theo đề, sau đó lấy đạo hàm P | `f^(s)(z)≈P^(s)(z)`; giữ nguyên tập mốc của câu nội suy. |
| Bảng, yêu cầu công thức p+1 điểm | Chọn p+1 mốc, dựng trọng số đạo hàm từ Lagrange | Xấp xỉ bằng đạo hàm của đa thức bậc ≤p trên tập đã chọn. |

Không thay đạo hàm của Stirling 9 mốc bằng công thức 3 điểm mà không nói. Hai tập mốc/bậc khác nhau có thể cho kết quả khác nhau. Không dùng sai phân của các giá trị P(z±δ) để thay cho đạo hàm đại số có thể tính trực tiếp.

Ký hiệu: z là điểm tính, s≥1 là cấp đạo hàm, p là bậc tối đa, số mốc K=p+1. Không dùng chữ “bậc” cho cả p và s mà thiếu nhãn.

## 2. Đầu vào và chọn mốc

- Cặp x,y hữu hạn; x phân biệt, sắp cặp theo x và giữ ID nguồn.
- Với chức năng **Đạo hàm từ bảng** hiện tại: `1≤s≤p<m`, m là số cặp nhập. Đề xuất giữ quy tắc này; nếu muốn đạo hàm vượt bậc của đa thức, đi qua chức năng nội suy hoặc Horner và ghi rõ đó là 0 của mô hình.
- z hữu hạn; p,s là số nguyên. Thiếu mốc báo thiếu dữ liệu cho p đã chọn, không tự giảm p.
- Mốc bất kỳ đều dùng được phương pháp trọng số tổng quát; các công thức quen thuộc chứa h chỉ áp dụng đúng lưới tương ứng.

**Quy tắc hiện tại của `calculus.differentiate`:** tìm hàng gần z nhất, hòa chọn hàng bên trái; gọi chỉ số đó là c. Chọn cửa sổ liên tiếp p+1 mốc, bắt đầu ở `max(0,min(c−floor(p/2),m−p−1))`. Công bố c, hàng bắt đầu, các ID được chọn. Với mốc không đều, đây không nhất thiết là p+1 mốc gần z nhất.

Nếu người dùng cần đạo hàm của tập nội suy đã chọn ở câu trước, dùng chính P của câu đó. Không gọi lại quy tắc trên để chọn một tập khác. Việc bổ sung lựa chọn tập mốc thủ công là thay đổi nhập liệu riêng, không phải tính năng đã tồn tại.

z ngoài `[x_min,x_max]` của tập chọn: vẫn tính được đạo hàm P nhưng ghi **đạo hàm của đa thức ngoại suy**. Không đánh đồng với một giá trị có bảo đảm của đạo hàm hàm thật.

## 3. Đạo hàm của đa thức nội suy bất kỳ

Nếu

$$
 P(x)=\sum_{k=0}^{n}\beta_k B_k(x),
$$

thì

$$
 P^{(s)}(z)=\sum_{k=0}^{n}\beta_k B_k^{(s)}(z).
$$

β_k là hệ số cố định được lập từ dữ liệu, không phụ thuộc điểm đánh giá. Nếu `deg B_k<s` thì đóng góp bằng 0. Bảng phải nối được đến bảng β_k và B_k trong lời giải nội suy.

### 3.1. Đổi biến chuẩn hóa

Nếu `x=a+ht`, `Q(t)=P(a+ht)`, `t_z=(z−a)/h`, thì

$$
 P^{(s)}(z)=h^{-s}Q^{(s)}(t_z)
          =\sum_k\frac{\beta_k}{h^s}B_k^{(s)}(t_z).
$$

Phải ghi riêng ba số: `t_z`, `Q^(s)(t_z)`, `h^−s Q^(s)(t_z)`. Đây là chỗ bắt buộc trong Stirling/Gauss/Bessel/Newton đều. Nếu h≠1 thì thiếu h^−s cho đáp số sai.

Nên dùng ký hiệu Q cho đa thức theo t, P cho đa thức theo x. Nếu ghi P(t) theo quy ước khác thì phải định nghĩa rõ; không viết P'(t_z) rồi gọi ngay đó là f'(z).

### 3.2. Cách lấy đạo hàm tích không chia cho nhân tử

Không dùng `B'(t)=B(t)Σ1/(t−r)` tại điểm có `t=r`: biểu thức trung gian không xác định dù đạo hàm vẫn hữu hạn.

Để tính mọi đạo hàm đến s của tích `B(t)=∏(t−r_j)` tại τ, lưu `g_l=B^(l)(τ)`:

```text
g[0]=1; g[1..s]=0
for mỗi nhân tử (t-r):
    for l=s xuống 1:
        g[l]=(tau-r)*g[l]+l*g[l-1]
    g[0]=(tau-r)*g[0]
```

Phải cập nhật cấp cao xuống thấp để dùng g cũ. Áp dụng cho `(t²−j²)` bằng hai nhân tử `(t−j)(t+j)`, t² bằng hai nhân tử t. Hạng B_0=1 có đạo hàm cấp ≥1 bằng 0. Với Bessel, tính cả nhân tử `(t−1/2)` trước khi kết luận đóng góp đạo hàm.

Nếu cần vết chi tiết, bảng từng nhân tử có `nhân tử, g_0,…,g_s`. Không cần khai triển toàn bộ đa thức để lấy đạo hàm tại một điểm.

### 3.3. Bảng bắt buộc

| Cột | Ý nghĩa |
|---|---|
| k, nguồn β_k | Liên hệ với lời giải dựng P; giữ cả các β_k=0. |
| B_k(t) hoặc B_k(x) | Dạng tích, không chỉ dãy hệ số vô danh. |
| B_k^(s)(t_z) hoặc B_k^(s)(z) | Đạo hàm cơ sở đã tính. |
| β_k B_k^(s) | Đóng góp trước đổi biến nếu đang dùng t. |
| β_k B_k^(s)/h^s | Đóng góp theo x nếu có đổi biến. |
| Tổng tích lũy | Đối chiếu được kết quả cuối. |

Nếu yêu cầu cả giá trị và đạo hàm thì hai bảng thế số có thể đặt cạnh nhau. Có thể ghép các cột khi bảng còn gọn; màn hình hẹp cho cuộn ngang hoặc tách bảng theo cùng k. Không lặp lại bảng dữ liệu/sai phân cho mỗi cấp đạo hàm.

## 4. Công thức p+1 điểm trên mốc bất kỳ

Với tập chọn `x_0,…,x_p`, Lagrange:

$$
 L_i(x)=\prod_{j\ne i}\frac{x-x_j}{x_i-x_j},\qquad
 w_i=L_i^{(s)}(z),\qquad
 f^{(s)}(z)\approx P^{(s)}(z)=\sum_{i=0}^{p}w_i y_i.
$$

### 4.1. Thuật toán dựng trọng số

Đặt `x=z+u`, chỉ cần hệ số u^s của tử số `∏_(j≠i)(z−x_j+u)`. Gọi a_l là hệ số u^l, lưu đến l=s. Các a_l là hệ số Taylor, **chưa nhân l!**.

```text
for i=0..p:
    a[0]=1; a[1..s]=0; denominator=1
    for j=0..p, j != i:
        v=z-x[j]
        for l=s xuống 1:
            a[l]=v*a[l]+a[l-1]
        a[0]=v*a[0]
        denominator *= x[i]-x[j]
        ghi j,v,denominator,a[0..s] nếu mở chi tiết
    w[i]=s!*a[s]/denominator
    contribution[i]=w[i]*y[i]
answer=sum(contribution)
```

Chỉ giữ đến s vì các phép nhân tiếp theo không hạ bậc. Thuật toán không chia cho z−x_j, nên làm được khi z trùng mốc. Mẫu denominator khác 0 nhờ x phân biệt.

### 4.2. Đầu ra phải có

1. Số cặp nhập, p,s,z; tập p+1 mốc được chọn và quy tắc chọn.
2. Công thức Lagrange và định nghĩa w_i.
3. Một hàng mẫu tính w_i, gồm mẫu số, hệ số u^s và s!; phần chi tiết có đủ mọi i.
4. Bảng `i,x_i,y_i,denominator_i,a_s,w_i,w_i y_i,tổng`.
5. Công thức đã thế các trọng số số vào y_i; kết quả cuối.
6. Kiểm tra moment và nhận xét về độ nhạy/sai số khi đủ dữ kiện.

### 4.3. Kiểm tra moment độc lập

Vì công thức phải đúng với mọi đa thức bậc ≤p:

$$
 \sum_{i=0}^{p}w_i(x_i-z)^r=
 \begin{cases}s!,&r=s,\\0,&0\le r\le p,\ r\ne s.\end{cases}
$$

Kiểm tra bằng tọa độ đã dịch quanh z giúp tránh lũy thừa rất lớn khi x có gốc lớn. Sai số kiểm tra so với thang tổng các hạng, không dùng một ngưỡng tuyệt đối cho mọi đơn vị/h. Moment đúng kiểm tra cách tính trọng số; không chứng minh dữ liệu không nhiễu hay hàm thật đủ trơn.

## 5. Các công thức quen thuộc và sai số

Trong mục này h>0, các giá trị f là chính xác và hàm đủ trơn trên đoạn chứa các điểm. Đặt `E=f^(s)(z)−D`, với D là công thức xấp xỉ.

| Công thức | D | Cận sai số đủ điều kiện |
|---|---|---|
| Hai điểm tiến, đạo hàm 1 | `[f(z+h)−f(z)]/h` | `abs(E)≤M_2 h/2` |
| Hai điểm lùi, đạo hàm 1 | `[f(z)−f(z−h)]/h` | `abs(E)≤M_2 h/2` |
| Ba điểm giữa, đạo hàm 1 | `[f(z+h)−f(z−h)]/(2h)` | `abs(E)≤M_3 h²/6` |
| Ba điểm tiến, đạo hàm 1 | `[−3f(z)+4f(z+h)−f(z+2h)]/(2h)` | `abs(E)≤M_3 h²/3` |
| Ba điểm lùi, đạo hàm 1 | `[3f(z)−4f(z−h)+f(z−2h)]/(2h)` | `abs(E)≤M_3 h²/3` |
| Ba điểm giữa, đạo hàm 2 | `[f(z−h)−2f(z)+f(z+h)]/h²` | `abs(E)≤M_4 h²/12` |

M_r là cận `|f^(r)|` trên đoạn liên quan; h^r có đúng đơn vị. Các cận này là công thức lý thuyết dùng để giải thích khi phù hợp; **không phải các trường M_r đã có trên màn hình đạo hàm hiện tại**. Bản này chưa đề xuất tự suy M_r từ bảng.

Ví dụ lập luận cho sai phân giữa cấp 1: `D=(1/(2h))∫_(−h)^h f'(z+u)du`. Khai triển f'(z+u) quanh z đến bậc 1 với phần dư bị chặn `M_3u²/2`; tích phân phần lẻ triệt tiêu, suy cận `M_3h²/6`. Không lấy đạo hàm biểu thức chứa ξ và giả sử ξ là hằng số.

Với công thức một phía ba điểm, có thể dùng phần dư nội suy tại điểm nút z hoặc chứng minh bằng hạt nhân tích phân để được h²M_3/3; không cộng các chặn Taylor thô rồi khẳng định ra cùng hằng số.

Nếu đề không yêu cầu công thức quen thuộc hoặc mốc không khớp, dùng trọng số tổng quát; không gắn nhãn “sai phân giữa O(h²)” cho một tập mốc bất kỳ.

## 6. Ví dụ lời giải tự dựng

### 6.1. Ba điểm ở đầu bảng, đạo hàm cấp 1

Cho `x=[0,1,2]`, `y=[1,2,5]`, z=0,p=2,s=1. Các giá trị từ `f(x)=x²+1`, nhưng tool chỉ cần bảng.

| i | x_i | y_i | denominator_i | a_1 | w_i | w_i y_i |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 1 | 2 | −3 | −3/2 | −3/2 |
| 1 | 1 | 2 | −1 | −2 | 2 | 4 |
| 2 | 2 | 5 | 2 | −1 | −1/2 | −5/2 |

Ví dụ hàng i=0: `L_0(u)=(u−1)(u−2)/2=(u²−3u+2)/2`, do đó `w_0=1!·(−3)/2`. Tổng `P'(0)=0`.

Thế dạng quen thuộc: `D=[−3·1+4·2−5]/2=0`. Moment r=0,1,2 lần lượt là `0,1,0`. Vì ở ví dụ tự dựng f bậc 2 nên đạo hàm khớp đúng; với bảng đo bất kỳ chỉ có thể kết luận đang lấy đạo hàm P.

### 6.2. Cùng ba điểm, đạo hàm cấp 2 ở giữa

z=1,p=2,s=2. Trọng số `[1,−2,1]`, đóng góp `[1,−4,5]`, tổng `P''(1)=2`. Chỉ rõ `h=1` và mẫu h²; không lấy trọng số cấp 1 để tính cấp 2.

### 6.3. Mốc không đều

`x=[0,1,3]`, `y=[1,3,13]`, z=1,p=2,s=1. Nội suy `P=x²+x+1`.

| x_i | y_i | w_i | đóng góp |
|---:|---:|---:|---:|
| 0 | 1 | −2/3 | −2/3 |
| 1 | 3 | 1/2 | 3/2 |
| 3 | 13 | 1/6 | 13/6 |

Tổng `P'(1)=3`. Moment quanh z: `Σw=0`, `Σw(x_i−1)=1`, `Σw(x_i−1)²=0`. Không có một h chung nên không dùng công thức ba điểm giữa đều.

### 6.4. Kiểm tra hệ số đổi biến với h khác 1

Tự dựng từ `f(x)=x²`: chọn x=[2,4,6],y=[4,16,36], gốc a=4,h=2. Khi `t=(x−4)/2`, `Q(t)=16+16t+4t²`.

Tại z=4: `t_z=0`, `Q'(0)=16`, `P'(4)=16/2=8`; `Q''(0)=8`, `P''(4)=8/2²=2`. Đây là ca bắt buộc để phát hiện thiếu h^−s.

### 6.5. Đề 20241, lấy đạo hàm Stirling

Dùng chính Q_8 và chín mốc ở [01, §8.5](01_Noi_suy_da_thuc_Thuat_toan_va_trinh_bay_CHO_DUYET.md#85-mẫu-đề-20241--dữ-liệu-thật-trong-repo). `a=4.042`, `h=0.117`, `t_z=−14/39`.

Lời giải phải có phép đạo hàm từng cơ sở, chẳng hạn

$$
 \frac{d}{dt}[t(t^2-1)]=3t^2-1,\qquad
 \frac{d}{dt}[t^2(t^2-1)]=4t^3-2t.
$$

Tính cả các hạng cấp 6,7,8, cộng `Q'_8(t_z)≈−0.3127739385361077`, rồi

$$
 P'_8(4)=\frac{Q'_8(-14/39)}{0.117}
        \approx-2.673281525949639.
$$

Hiển thị P_8(4)≈5.442986424022284 ở cùng kết luận nếu đề cần cả hai. Không dùng các hệ số đã làm tròn của P(x) với độ lớn hàng trăm nghìn để tính lại đạo hàm và giấu sai lệch triệt tiêu.

## 7. Sai số tổng quát và nhiễu

### 7.1. Không đạo hàm phần dư chứa ξ như hằng số

Đẳng thức giá trị `f(x)−P(x)=f^(p+1)(ξ_x)ω(x)/(p+1)!` không cho phép coi ξ_x không đổi khi đạo hàm. Cận cho đạo hàm phải được chứng minh riêng hoặc dùng lập luận Taylor/moment sau.

### 7.2. Cận từ Taylor cho trọng số bất kỳ

Giả sử f có đạo hàm liên tục đến p+1 trên đoạn chứa z và mọi mốc, `|f^(p+1)|≤M_(p+1)`, và trọng số thỏa các moment đến p. Khai triển từng f(x_i) quanh z rồi cộng với trọng số:

$$
 \left|f^{(s)}(z)-\sum_i w_i f(x_i)\right|
 \le \frac{M_{p+1}}{(p+1)!}
       \sum_i|w_i|\,|x_i-z|^{p+1}.
$$

Đây là cận hợp lệ nhưng có thể thô và không tận dụng triệt tiêu do đối xứng. Không gọi nó là cận tốt nhất. Nếu các moment triệt tiêu thêm ở bậc cao hơn và biết đạo hàm cao hơn, có thể chứng minh cận tốt hơn, như công thức giữa mục 5.

### 7.3. Sai số dữ liệu

Nếu `|δy_i|≤η_i` thì sai số do dữ liệu bị chặn bởi `Σ|w_i|η_i`. Nếu mọi η_i≤η thì cận là `ηΣ|w_i|`. Hệ số w thường tăng theo h^−s, nên giảm bước không luôn làm kết quả tốt hơn khi dữ liệu có nhiễu/làm tròn.

Có thể cộng cận xấp xỉ và cận dữ liệu khi cả hai giả thiết đúng. Sai số tính toán cần xét riêng. Không biến số chữ số hiển thị thành số chữ số chính xác được bảo đảm.

## 8. Ca biên và nghiệm thu

| Tình huống | Cần thể hiện |
|---|---|
| z trùng mốc | Tính trọng số/tích không chia 0. |
| z ở biên | Cửa sổ một phía được công bố; không đòi mốc ở phía không có. |
| z ngoài tập | Ghi ngoại suy, giữ đúng tập đã công bố. |
| p hoặc s không nguyên, s=0 ở màn hình đạo hàm, s>p | Báo điều kiện đầu vào của màn hình, không tự sửa tham số. |
| p≥m | Thiếu p+1 mốc; giữ nguyên p được yêu cầu. |
| y hằng | Đạo hàm các cấp hợp lệ bằng 0 trong sai số số học; trọng số có moment đúng. |
| x có gốc lớn, h rất nhỏ | Dịch/đổi thang và độ chính xác trung gian phù hợp; không nhận nhầm mốc trùng/đều. |
| Trọng số vượt miền float nhưng tổng còn hữu hạn | Giữ số trung gian đủ miền/độ chính xác; đừng tràn chỉ vì chuyển từng w sang float. |
| Đạo hàm cấp >bậc P đã biết | Giá trị của mô hình là 0; không khẳng định f^(s) thật bằng 0. |
| Bessel đúng tâm, hạng lẻ có giá trị 0 | Vẫn xét đạo hàm của hạng đó. |
| Thiếu cận đạo hàm cao | Nói chưa có cận của hàm thật; không dùng phần dư tại mốc thay thế. |

Mỗi trường hợp thành công phải có công thức, bảng đóng góp và kết luận. Mỗi lỗi phải nêu tham số/dữ liệu gây lỗi; không đưa một giá trị trung gian chưa hợp lệ làm đáp án.
