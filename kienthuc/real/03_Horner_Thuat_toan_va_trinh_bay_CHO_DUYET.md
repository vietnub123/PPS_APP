# Horner — lý thuyết, thuật toán và lời giải cần hiển thị

**Đặc tả đã được duyệt, 31/10/2026.** Xem [hiện trạng và quy tắc chung](00_Dac_ta_noi_suy_dao_ham_Horner_CHO_DUYET.md). Đây là chuẩn thuật toán và đầu ra dùng để triển khai Horner trong tool.

## 1. Phân biệt các việc dùng Horner

| Bài toán | Kết quả cần có |
|---|---|
| Tính P(c) | Một lượt nhân–cộng, số dư P(c). |
| Chia P(x) cho x−c | Hệ số thương và số dư; đẳng thức chia. |
| Tính P'(c),…,P^(s)(c) | Chia liên tiếp; số dư lượt r là P^(r)(c)/r!. |
| Tính đa thức dạng Newton | Horner có nhân tử x−x_j; hệ số là tỉ sai phân theo đúng thứ tự mốc. |

Horner là sơ đồ tính hữu hạn; không phải phương pháp tìm nghiệm hay vòng lặp đến epsilon. Nếu được dùng trong Newton tìm nghiệm, đó là một thuật toán khác gọi Horner để tính P/P'.

## 2. Thứ tự hệ số — phải ghi trước khi tính

Trong tài liệu này và màn hình **Đạo hàm & Horner → Horner**, dùng hệ số **bậc giảm**:

$$
 P(x)=a_0x^n+a_1x^{n-1}+\cdots+a_{n-1}x+a_n.
$$

Ví dụ `[3,0,−2,−1]` biểu diễn `3x³+0x²−2x−1`. Bậc bị thiếu phải có số 0; không xóa số 0 nằm giữa/cuối dãy.

`chapter1_tools.horner_division` nhận hệ số **bậc tăng** và trả thương bậc tăng. Vì vậy cùng đa thức trên phải gọi bằng `[-1,−2,0,3]`. Không tự truyền dãy GUI cho API đó. Hệ số Newton trong mục 7 lại là hệ số theo thứ tự cơ sở Newton, không phải hệ số lũy thừa.

Hệ số và c hữu hạn; dãy không rỗng, một chiều; s là số nguyên không âm. Có thể có hệ số 0 đầu dãy: giữ bản nhập để đối chiếu, xác định bậc thực từ hệ số khác 0 đầu tiên. Đa thức toàn 0 có giá trị và mọi đạo hàm bằng 0. Đa thức hằng chỉ cần một hệ số.

**Hiện trạng:** `interpolation.horner` đi theo độ dài dãy nhập để tạo các lượt. Chuẩn hóa số 0 đầu dãy và cách ghi bậc thực nêu trên là yêu cầu trình bày cần được duyệt; không được xóa dữ kiện đầu vào trên bản báo cáo.

## 3. Một lượt Horner và phép chia

### 3.1. Công thức

$$
 b_0=a_0,\qquad b_j=a_j+c\,b_{j-1},\quad j=1,\ldots,n.
$$

$$
 P(c)=b_n,\qquad
 P(x)=(x-c)Q_1(x)+b_n,
$$

$$
 Q_1(x)=b_0x^{n-1}+b_1x^{n-2}+\cdots+b_{n-1}.
$$

```text
b[0]=a[0]
for j=1..n:
    product=c*b[j-1]
    b[j]=a[j]+product
    ghi j,a[j],b[j-1],product,b[j]
quotient=b[0..n-1]
remainder=b[n]
```

Lượt đầu với n=0 cho số dư hằng số và thương 0; không truy cập b[−1] để tính hàng đầu.

### 3.2. Dạng bảng bắt buộc

Bảng chính của mỗi lượt:

| j | Bậc của hệ số đầu vào | A_j | b_(j−1) | c·b_(j−1) | b_j=A_j+c·b_(j−1) |
|---|---|---|---|---|---|
| 0 | bậc hiện tại | A_0 | — | — | A_0 |
| 1.. | … | … | … | … | … |

Ghi ngay dưới bảng: thương theo đúng thứ tự hệ số, số dư, đẳng thức chia. Dấu “—” ở hàng đầu nghĩa là không cần phép nhân, không phải dữ liệu bị thiếu.

Có thể thêm sơ đồ Horner ba hàng truyền thống: hệ số; c nhân các tích lũy; các tổng. Không chỉ đưa bảng hai cột rồi để người đọc tự đoán truy hồi.

### 3.3. Ví dụ tự dựng

`P(x)=3x³−2x−1`, c=2, nhập `3 0 -2 -1`.

| j | A_j | c·b_(j−1) | b_j |
|---:|---:|---:|---:|
| 0 | 3 | — | 3 |
| 1 | 0 | 6 | 6 |
| 2 | −2 | 12 | 10 |
| 3 | −1 | 20 | 19 |

`Q_1(x)=3x²+6x+10`, số dư 19:

$$
 3x^3-2x-1=(x-2)(3x^2+6x+10)+19,\qquad P(2)=19.
$$

## 4. Chia Horner liên tiếp để lấy đạo hàm

### 4.1. Vì sao phải nhân giai thừa?

Đặt Q_0=P. Chia liên tiếp tại cùng c:

$$
 Q_r(x)=(x-c)Q_{r+1}(x)+s_r.
$$

Thay lần lượt vào P:

$$
 P(x)=s_0+s_1(x-c)+s_2(x-c)^2+\cdots+s_n(x-c)^n.
$$

Đây là khai triển Taylor chính xác của đa thức, suy ra

$$
 P^{(r)}(c)=r!s_r.
$$

Lượt chia r+1 tạo số dư s_r. Chỉ số lượt là 1,2,…; chỉ số đạo hàm là 0,1,…; phải đặt nhãn để không lệch một lượt.

### 4.2. Mã giả đầy đủ

```text
A = hệ số của P theo bậc giảm, đã xác định bậc thực n
F = 1
for r=0..min(s,n):
    b[0]=A[0]
    ghi hàng đầu
    for j=1..length(A)-1:
        b[j]=A[j]+c*b[j-1]
        ghi A[j],c*b[j-1],b[j]
    sr=b[-1]
    derivative[r]=F*sr
    ghi r,đa thức Qr,hệ số A,thương b[:-1],sr,F,derivative[r]
    A=b[:-1]                   # bỏ số dư, giữ thương cho lượt sau
    F *= r+1
mọi cấp r>n có đạo hàm 0, không dựng hàng nghìn bảng 0
```

Khi đã đến hằng số thì kết thúc phần chia; phần kết luận liệt kê các cấp còn lại bằng 0. Không đưa số dư vào dãy hệ số lượt sau. Giai thừa phải được giữ đủ miền số trước phép nhân; không tràn chỉ vì r! ở float trong khi tích cuối còn biểu diễn được.

### 4.3. Ví dụ tiếp mục 3

| r | Hệ số đầu vào Q_r | Dãy b sau lượt r+1 | s_r | r! | P^(r)(2) |
|---:|---|---|---:|---:|---:|
| 0 | 3,0,−2,−1 | 3,6,10,19 | 19 | 1 | 19 |
| 1 | 3,6,10 | 3,12,34 | 34 | 1 | 34 |
| 2 | 3,12 | 3,18 | 18 | 2 | 36 |
| 3 | 3 | 3 | 3 | 6 | 18 |

Đây là bảng tổng kết; các bảng nhân–cộng từng lượt vẫn có trong chi tiết. Khai triển quanh 2:

$$
 P(x)=19+34(x-2)+18(x-2)^2+3(x-2)^3.
$$

Không ghi P''(2)=18: 18 là s_2, cần nhân 2!.

## 5. Ví dụ đề 20241 trong repo

Nguồn `../20241_MI3042_GK.jpg`, câu a. Đề cho

$$
 P(x)=3.5x^5-2.78x^4+5.63x^3+0x^2-15.28x+1.54,
 \quad c=2.57.
$$

Cần P''(c),P'''(c). Nhập `3.5 -2.78 5.63 0 -15.28 1.54`, đạo hàm đến cấp 3. **Không liên quan đến workbook** vì đa thức đã in trực tiếp trong đề.

### Lượt 1: Q_0=P, số dư s_0=P(c)

| j | A_j | 2.57·b_(j−1) | b_j |
|---:|---:|---:|---:|
| 0 | 3.5 | — | 3.5 |
| 1 | −2.78 | 8.995 | 6.215 |
| 2 | 5.63 | 15.97255 | 21.60255 |
| 3 | 0 | 55.5185535 | 55.5185535 |
| 4 | −15.28 | 142.682682495 | 127.402682495 |
| 5 | 1.54 | 327.42489401215 | 328.96489401215 |

Thương Q_1 có hệ số `3.5,6.215,21.60255,55.5185535,127.402682495`; `s_0=328.96489401215`.

### Lượt 2: Q_1, số dư s_1=P'(c)

| j | A_j | 2.57·b_(j−1) | b_j |
|---:|---:|---:|---:|
| 0 | 3.5 | — | 3.5 |
| 1 | 6.215 | 8.995 | 15.21 |
| 2 | 21.60255 | 39.0897 | 60.69225 |
| 3 | 55.5185535 | 155.9790825 | 211.497636 |
| 4 | 127.402682495 | 543.54892452 | 670.951607015 |

Thương Q_2 có hệ số `3.5,15.21,60.69225,211.497636`; `s_1=670.951607015`.

### Lượt 3: Q_2, số dư s_2=P''(c)/2!

| j | A_j | 2.57·b_(j−1) | b_j |
|---:|---:|---:|---:|
| 0 | 3.5 | — | 3.5 |
| 1 | 15.21 | 8.995 | 24.205 |
| 2 | 60.69225 | 62.20685 | 122.8991 |
| 3 | 211.497636 | 315.850687 | 527.348323 |

Thương Q_3 có hệ số `3.5,24.205,122.8991`; `s_2=527.348323`.

### Lượt 4: Q_3, số dư s_3=P'''(c)/3!

| j | A_j | 2.57·b_(j−1) | b_j |
|---:|---:|---:|---:|
| 0 | 3.5 | — | 3.5 |
| 1 | 24.205 | 8.995 | 33.2 |
| 2 | 122.8991 | 85.324 | 208.2231 |

Thương Q_4 có hệ số `3.5,33.2`; `s_3=208.2231`. Không cần chia tiếp để trả lời câu a.

| Cấp r | Số dư s_r | Nhân r! | Đạo hàm tại 2.57 |
|---:|---:|---:|---:|
| 0 | 328.96489401215 | 1 | 328.96489401215 |
| 1 | 670.951607015 | 1 | 670.951607015 |
| 2 | 527.348323 | 2 | **1054.696646** |
| 3 | 208.2231 | 6 | **1249.3386** |

Các số trên được kiểm bằng số hữu tỷ của đúng hệ số thập phân trong đề và đối chiếu kết quả `interpolation.horner`. Bảng nhân–cộng đầy đủ ở tài liệu là mẫu đầu ra cần có sau duyệt; bảng hiện có trong `A_Horner.txt` chỉ có hệ số/giá trị tích lũy.

## 6. Kiểm tra bằng đạo hàm đồng thời — cách khác, không trộn bảng

Nếu cần một cách đối chiếu, Horner đồng thời tính đạo hàm thật qua tích `(xB+A)`:

```text
d[0]=a[0]; d[1..s]=0
for j=1..n:
    for r=s xuống 1:
        d[r]=c*d[r]+r*d[r-1]
    d[0]=c*d[0]+a[j]
```

Cuối cùng `d[r]=P^(r)(c)`. Đây là giá trị đạo hàm thật, khác s_r của sơ đồ chia lặp (s_r đã chia r!). Nếu dùng d[r]/r! làm trạng thái Taylor thì truy hồi cũng phải đổi. Không ghép nhãn “số dư” của chia lặp với số d[r] của thuật toán này.

Để phù hợp mục tiêu trình bày phép chia và đạo hàm, **chia lặp là cách chính đề xuất**; cách đồng thời là kiểm tra/chi tiết khi cần, không tự thay mất sơ đồ mà đề yêu cầu.

## 7. Horner cho đa thức Newton

Cho thứ tự mốc `ξ_0,…,ξ_n` và hệ số tương ứng c_k:

$$
 P(x)=c_0+(x-\xi_0)[c_1+(x-\xi_1)[\cdots+(x-\xi_{n-1})c_n]].
$$

```text
v=c[n]
for k=n-1 xuống 0:
    factor=z-xi[k]
    product=factor*v
    v=c[k]+product
    ghi k,xi[k],factor,v_cũ,c[k],product,v_mới
```

Ở đây ξ_n là mốc cuối của bộ dữ liệu nhưng không còn xuất hiện trong tích của hạng cao nhất. Không đảo thứ tự mốc mà giữ c_k cũ. Newton lùi dùng thứ tự từ phải sang trái và hệ số được dựng theo thứ tự đó.

Ví dụ tự dựng: `ξ=[0,1,3]`, `c=[1,2,1]`, z=2. Khởi tạo v=1; k=1: `v=2+(2−1)·1=3`; k=0: `v=1+(2−0)·3=7`.

Nếu đánh giá trên biến chuẩn hóa u=(x−a)/b thì các mốc ξ và điểm đánh giá đều phải cùng biến u. Đạo hàm theo x cần thêm b^−s. Không lấy mốc theo x ghép với hệ số theo u.

API `chapter1_tools.newton_horner` hiện chỉ trả số, chưa có báo cáo từng bước; bảng vừa nêu là yêu cầu khi dùng cách đánh giá này trong lời giải. Chức năng thêm mốc `newton_append` giữ thứ tự mốc cũ, tính hệ số mới

$$
 c_{n+1}=\frac{y_{\rm new}-P_n(x_{\rm new})}
                   {\prod_{j=0}^{n}(x_{\rm new}-\xi_j)}.
$$

Chỉ áp dụng khi mốc mới khác mọi mốc cũ; nếu trình bày thì phải cho P_n ở mốc mới, tích mẫu và hệ số mới. Đây là bổ trợ dạng Newton, không phải một lượt chia Horner lấy đạo hàm.

## 8. Bố cục lời giải đề xuất

1. Đa thức đã đọc từ hệ số, điểm c, các cấp cần tính; xác nhận hệ số 0 bị thiếu bậc đã được giữ.
2. Truy hồi một lượt và ý nghĩa thương/số dư.
3. Nếu lấy đạo hàm: giải thích `P^(r)(c)=r!s_r` một lần.
4. Các lượt cạnh nhau từng đôi khi đủ rộng; mỗi lượt có bảng nhân–cộng, thương/số dư. Khi hẹp chuyển thành một cột theo số lượt.
5. Bảng tổng kết `r,s_r,r!,P^(r)(c)` và nhấn các cấp đề hỏi.
6. Đối chiếu và giới hạn số học. Với yêu cầu cấp rất cao, gom các cấp >n thành một ghi chú bằng 0.

Không lặp công thức lý thuyết dài ở từng lượt. Không dùng riêng một bảng tổng kết để thay toàn bộ quá trình nếu đề hỏi thuật toán/bảng Horner.

## 9. Ca biên, số học và kiểm tra

| Ca | Kết quả/hành vi cần có |
|---|---|
| P hằng, s=0 hoặc s>0 | Một lượt tính hằng; mọi đạo hàm cấp dương bằng 0. |
| P toàn 0 | Mọi kết quả 0; không suy “không có dữ liệu”. |
| Hệ số 0 ở đầu/giữa/cuối | Đầu: ghi bậc thực; giữa/cuối: giữ đúng vị trí lũy thừa. |
| c=0 hoặc c âm | Truy hồi vẫn đúng; c âm cần ghi ngoặc trong phép thế. |
| s>n, ví dụ 1000 | Chỉ chia đến bậc thực; ghi các cấp còn lại bằng 0, không tạo 1001 bảng. |
| c là nghiệm | Số dư 0 là hợp lệ; thương vẫn tính được. |
| Nghiệm bội q | Các số dư s_0,…,s_(q−1) bằng 0 trong số học chính xác; không suy bội chỉ từ số hiển thị làm tròn thành 0. |
| Hệ số hoặc c không hữu hạn | Báo lỗi trước khi trình bày đáp án. |
| Kết quả cuối vượt miền số | Báo nguyên nhân; không in Inf/NaN như đáp số. |
| Triệt tiêu mạnh hoặc bậc lớn | Giữ độ chính xác trung gian, ghi độ nhạy; số chữ số in không là cận sai số. |

Kiểm tra quan trọng: đẳng thức `P=(x−c)Q+s_0`; chuỗi thương/số dư; khai triển Taylor từ s_r tái tạo P; ví dụ đa thức biết đạo hàm; cả hai thứ tự hệ số GUI/API. Không cần tính lại bằng đạo hàm số với bước rất nhỏ để làm “chuẩn”.

Với hệ số đầu vào có sai số, Horner chỉ tính trên đa thức tương ứng với số đã nhập. Tính chính xác các phép trên số thập phân không có nghĩa các hệ số thực nghiệm ban đầu chính xác tuyệt đối.
