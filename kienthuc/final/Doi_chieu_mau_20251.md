# Đối chiếu mẫu trình bày người dùng gửi

Nguồn là bốn ảnh lời giải MI3042 20251 trong cuộc hội thoại. Áp dụng cách lập luận và bảng biểu; không lấy mọi phép xử lý hoặc số kết quả trong mẫu làm chuẩn thuật toán.

| Điểm | Mẫu trên ảnh | Hành vi được giữ trong tool |
|---|---|---|
| Dữ liệu khớp | Loại hai điểm dương, khớp 102 điểm âm | Giữ các dòng đã nhập; nhánh log báo sai miền khi có 0/lẫn dấu. Nếu muốn lọc, người dùng xử lý trước và công bố ID, lý do, tập tính sai số. |
| Hàm mục tiêu | Khớp `ln(-y)` | Phân biệt bình phương tối thiểu trên thang biến đổi với LM tối ưu SSE trên y gốc. Hai nhánh không là cùng bài tối ưu. |
| Hệ chuẩn | Suy ra từ điều kiện cực trị | Có hệ tổng quát và hệ số cụ thể; nhật ký giải vẫn theo đúng Gauss, QR hoặc SVD được chọn. |
| Mốc nội suy ngược | Tự chọn hướng/gốc từ khoảng đổi dấu và hạ bậc theo phía | Giữ tập mốc/hướng đã chọn; gốc ở đầu/cuối tập. Khoảng nghiệm không tự thay tập mốc hay bậc. |
| Dừng lặp | Chỉ độ đổi t nhỏ; bỏ khoảng thất bại | Kiểm tra theo x và phần dư y; chế độ có cận co còn có chứng nhận. Giữ các bước và trạng thái thất bại. |
| Các kết quả ngược in trên ảnh | Hai cửa sổ sáu mốc, khác lựa chọn trong mã giả thông thường bậc 3/4 | Chỉ đối chiếu kết quả khi biết đúng toàn bộ mốc, bậc, gốc và quy tắc lặp. |
| Stirling 7 mốc | In `f(4.15)≈-0.791128` | Tính đủ bậc 6 cho `-0.79122755380352395`; đạo hàm `0.43526738412512027` khớp ảnh sau làm tròn. |
| Số quan sát | n đôi lúc là số dòng, đôi lúc là chỉ số cuối | Dùng N dòng, i=0,…,N−1. |
| RMSE và sigma | Dùng ký hiệu σ với mẫu số N | Nêu đúng định nghĩa RMSE; phân biệt ước lượng thống kê mẫu số N−p và mục tiêu ở thang log. |

Với đúng bảy mốc trên ảnh, oracle Lagrange bằng phân số độc lập cho cùng giá trị và đạo hàm như Stirling. Con số `-0.791128` gần với tổng mới gồm ba hạng `-.8056+.0281t+.0227t²`, chưa tính bốn hạng còn lại. Không sửa giá trị của tool theo số thiếu hạng này.

Các tổng đã làm tròn của hệ 102 điểm trên ảnh cho `C0≈0.86846450, b≈-0.30595013, c≈0.91461331, A≈-2.38324857`, phù hợp chữ số tham số được in. Đây là kiểm tra hệ đã cho, chưa kiểm chứng RMSE `0.111911`: chưa có đủ bảng test1. `20251GKtest2.xlsx` trong repo là bảng khác.

Tịnh tiến, đổi đơn vị, chọn nhánh và lọc dữ liệu được hướng dẫn riêng trong [Tiền xử lý bằng Excel](Tien_xu_ly_Excel.pdf), nguồn [TeX](Tien_xu_ly_Excel.tex), kèm [workbook công thức](Tien_xu_ly_Excel.xlsx). Mọi phép đổi phải kèm mục tiêu mới, cách đổi kết quả/đạo hàm/biên về biến gốc và ảnh hưởng tới họ mô hình.

Cách trình bày áp dụng: dữ liệu → đặt biến/mô hình → công thức và bảng tổng quát → thế số → quá trình thực tính → kết luận/sai số. Danh mục dùng chung cho 58 lựa chọn nằm ở `pps/exam_style.py`. [Thư viện HTML](examples/presentation/index.html) gồm 58 bài mặc định tự dựng và một bài đúng 7 mốc trên ảnh. Phụ lục C của [sổ tay PDF](So_tay_PPS.pdf) trình bày đối chiếu này bằng công thức và bảng.
