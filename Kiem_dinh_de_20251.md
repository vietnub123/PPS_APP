# Chạy đề ảnh và workbook mới

Đã dùng nguyên `kienthuc/20251GKtest2.xlsx`: 104 cặp, bước x=0.115, x̄=2.55, ȳ=1.23. Các cột D/E là tham số đề, không phải cặp dữ liệu bổ sung. Không sửa tệp gốc, bỏ quan sát hoặc dịch y.

Ảnh `20251_MI3042_GK.jpg` chứa hai đề cạnh nhau: bên trái ghi 20251, mô hình `a exp(bx+c/x)`, Stirling 7 mốc và nhắc test1; bên phải in 20241, mô hình `a exp(bx²+c/x)`, Bessel 8 mốc. Tệp mới được cấp tên test2. Do đó các kết quả dưới đây luôn chỉ rõ **mô hình nào chạy trên test2**, không nhận là đáp số test1 chưa có.

## Mở và chạy

Trong ứng dụng chọn **Mở bài**, mở JSON tương ứng tại [examples/de_20251](examples/de_20251), rồi bấm **Tính kết quả**. Mỗi JSON chứa đủ dữ liệu, không cần workbook còn mở. HTML là lời giải đọc/in ngoại tuyến; TXT chứa toàn bộ bảng và phép tính. Các nhóm chi tiết mở được từng bước, tự mở khi in HTML.

```bat
CHAY_CONSOLE.bat examples\de_20251\01a_mu_x2_SSE_104.json
CHAY_CONSOLE.bat examples\de_20251\02a_lap_tien_cuc_bo.json
CHAY_CONSOLE.bat examples\de_20251\03a_Stirling_7.json
```

## Câu a: khớp mô hình và sai số

Workbook có y âm và y đổi dấu. Phép biến đổi `ln(y)` không áp dụng cho nguyên bảng này. Chọn **Hàm mũ** sẽ báo đúng lỗi miền, giữ đủ 104 dòng. Không được xóa hàng âm để tiếp tục một bài khác.

Nếu mục tiêu là tối thiểu tổng bình phương phần dư **trên thang y gốc**, chọn **Hàm mũ — SSE thang y**, bộ giải Levenberg–Marquardt. Cơ sở chỉ nhập phần mũ sau hệ số biên độ: `x^2;1/x` hoặc `x;1/x`; không thêm `1`. Tham số đầu có thể nhập rõ, thứ tự `[a,b,c]`. Lời giải lưu từng bước thử, tham số cũ/mới, Jacobian, λ, SSE, bước nhận/từ chối và lý do dừng.

| Mô hình trên đúng 104 dòng test2 | a | b | c | SSE_y | RMSE_y |
|---|---:|---:|---:|---:|---:|
| a exp(bx²+c/x) | 1.517285755115 | −0.252459156253 | 1.991231506036 | 0.001200335526 | 0.003397305955 |
| a exp(bx+c/x) | 11.672734856420 | −1.290731157028 | 0.981281915998 | 0.061925667170 | 0.024401620999 |

`SSE_y=Σ(y_i−g_i)²`, `MSE_y=SSE_y/104`, `RMSE_y=√MSE_y`. Kết quả được đối chiếu với SciPy tối ưu độc lập. Đây là nghiệm dừng phi tuyến tìm được, không phải chứng nhận cực tiểu toàn cục. Nếu cô bắt buộc tuyến tính hóa qua log thì phải nêu dữ liệu không thỏa giả thiết của cách đó; chạy SSE gốc là một lựa chọn mô hình/mục tiêu được công bố riêng.

Bản chạy: [mũ x²](examples/de_20251/01a_mu_x2_SSE_104.html), [mũ x](examples/de_20251/01b_mu_x_SSE_104.html), [lỗi miền log](examples/de_20251/01c_log_khong_ap_dung.html).

## Câu b: thuật toán lặp nội suy ngược

Quét dữ liệu phát hiện khoảng đổi dấu `[2.035,2.15]` cho mức 1.23. Giữ khoảng này độc lập với tập mốc lập đa thức. Bậc và tập mốc phải ghi rõ trong bài.

| Lựa chọn tường minh | Dòng gốc, từ 0 | Gốc | Kết quả x | Vòng dừng |
|---|---|---:|---:|---:|
| Newton tiến bậc 3, có cận co | [9,10,11,12] | 2.035 | 2.130827273369 | 5 |
| Newton lùi bậc 3, có cận co | [7,8,9,10] | 2.15 | 2.130891279015 | 5 |

Cả hai dùng ε_x=ε_y=10⁻⁹. Đã đối chiếu nghiệm với đa thức dựng độc lập và nghiệm tìm bằng Brent. Hai tập mốc khác nhau tạo hai đa thức khác nhau, nên không kỳ vọng đáp số trùng tuyệt đối. Đề chỉ định mốc/bậc nào thì giữ đúng lựa chọn đó.

Chép thuật toán theo công thức trong báo cáo: dựng `p(t)=c0+d*t+H(t)`, `Φ(t)=(ȳ−c0−H(t))/d`, khởi tạo `t0=(ȳ−c0)/d`, lặp `t_(k+1)=Φ(t_k)`, đổi `x_k=origin+h*t_k`. Chế độ có cận kiểm `t0∈J`, `Φ(J)⊆J`, `q=max|Φ′|<1`, rồi kiểm cả `B_k=|h|q|t_k−t_(k−1)|/(1−q)≤ε_x` và `|p(t_k)−ȳ|≤ε_y`. Báo cáo có hệ số, chặn, từng số hạng và phép thế số của mọi vòng.

**Ca nguyên 104 mốc:** tiến giữ gốc 1, T=[9,10]; lùi giữ gốc 12.845, T=[−94,−93]; bậc tối đa 103. Chương trình thử đúng phép lặp, ghi tràn số ở vòng 3/2, không báo thiếu mốc và không tự đổi sang mô hình cục bộ. Hai JSON `02c`/`02d` là các ca thất bại có chủ đích, TXT giữ toàn bộ quỹ đạo. Chúng không có đáp số được công nhận.

Bản chạy: [tiến](examples/de_20251/02a_lap_tien_cuc_bo.html), [lùi](examples/de_20251/02b_lap_lui_cuc_bo.html). Tập cục bộ là lựa chọn được khai báo qua ô **Mốc dùng**, không phải cách chương trình âm thầm sửa một phép lặp không hội tụ.

## Câu c: giá trị và đạo hàm

Nhập nguyên 104 cặp vào **Nội suy đa thức**, điểm 2.55, cấp đạo hàm 1, số mốc theo đề. Phần chọn mốc ghi đúng các hàng và gốc đổi biến trong báo cáo.

| Phương pháp | Số mốc | P(2.55) | P′(2.55) |
|---|---:|---:|---:|
| Stirling | 7 | 0.643602714824 | −0.987821541453 |
| Bessel | 8 | 0.644033162232 | −0.985994845413 |

Đã so giá trị và đạo hàm với tổng Lagrange dạng tích tính độc lập, gồm hệ số h⁻¹. [Stirling](examples/de_20251/03a_Stirling_7.html), [Bessel](examples/de_20251/03b_Bessel_8.html).

## Spline và các ca bổ sung

Ảnh đề mới không có câu spline. Ca này **tự đặt trên dữ liệu thật**, điều kiện tự nhiên chọn rõ: S(2.55)=0.644019495981, S′(2.55)=−0.981423912732, tích phân từ 2.035 đến 2.955 bằng 0.696713440263. Giữ đủ 104 mốc; hệ ba đường chéo giải Thomas thực tế. Đã so với SciPy CubicSpline độc lập. [Lời giải](examples/de_20251/04_spline_104.html).

Các bài `05`–`08` là mô phỏng/đối chiếu tài liệu real: spline có đủ moment, khử và thế ngược; hồi quy trọng số có hệ chuẩn và khử Gauss; LM có cả bước thử bị từ chối; bảng 36 mốc cho khoảng ở giữa. Hai chiều ở bài 36 mốc đều giữ đủ dữ liệu, trả 2.09 với bậc tối đa 35 và bậc thực tế 1.

Các kiểm thử còn bao gồm lưới không đều, điểm trùng cho spline, dữ liệu đo lặp cho hồi quy, trọng số 0, thiếu hạng, thiếu/thừa/mâu thuẫn điều kiện biên, đạo hàm hai phía ở nút, đảo cận tích phân, giới hạn vòng và kết quả lặp ngoài khoảng yêu cầu. Xem [hướng dẫn sử dụng](Huong_dan_dung_khi_thi.md) để chọn thuật toán và nhập điều kiện đúng đề.
