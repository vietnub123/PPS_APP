# Nội suy ngược — bản sửa theo guide v2 ngày 30/10/2026

Đã áp dụng `kienthuc/real/Noi_suy_nguoc_Guide_trien_khai_va_hien_thi (2).md` và PDF lý thuyết mới 25 trang. Quy định §0 của guide mới thay thế yêu cầu cũ rằng gốc tiến/lùi phải sát khoảng nghiệm. Yêu cầu cũ đã gây báo thiếu mốc sai khi nghiệm ở giữa bảng.

## Hành vi đã sửa

- Bảng nhập, tập mốc dùng và khoảng nghiệm là ba dữ kiện riêng. Mặc định giữ toàn bộ tập nhập. Ô **Mốc dùng** nhận JSON các chỉ số dòng gốc, từ 0, ví dụ `[9,10,11,12]`; để trống dùng đủ bảng. Không tự hạ bậc hoặc chọn lại mốc khi phép lặp thất bại.
- Tiến dùng gốc đầu tập mốc, lùi dùng gốc cuối. Hệ số luôn lấy đúng theo gốc đó. Với `[a,b]`, tính `T=[(a−origin)/h,(b−origin)/h]`, không ép T vào [0,1] hay [−1,0]. Chỉ báo thiếu mốc nếu bậc yêu cầu thực sự cần nhiều mốc hơn tập được chọn.
- Tập con có thể bỏ qua một số dòng bảng gốc nếu chính tập dùng vẫn cách đều. Đa thức thuận có thể đi qua điểm đổi chiều của mẫu; báo cảnh báo nhiều nghiệm/khó hội tụ. Hàm ngược vẫn phải dùng nhánh phù hợp, không đảo y trùng/không đơn điệu tùy tiện.
- T là khoảng kết quả yêu cầu; J là đoạn dùng chứng nhận co. Trong chế độ thực hành, t0 hoặc bước lặp ngoài T được ghi cảnh báo và tiếp tục. Không kẹp về biên. Nếu hội tụ ngoài khoảng x yêu cầu thì giữ ứng viên nhưng không nhận thành công.
- Chế độ chỉ có cận nhận kết quả khi chứng nhận đủ điều kiện. Không có chứng nhận là thiếu căn cứ hội tụ, không phải thiếu mốc. Nếu có chứng nhận mà bước lặp rời J thì dừng với vi phạm chứng nhận.
- Giá trị đầu chọn được: tuyến tính tại gốc (mặc định), tuyến tính hai đầu khoảng theo chính đa thức đang dùng, hoặc thủ công. Giữ nguyên giá trị đã chọn. Khi d=0, báo không lập được phép chia tuyến tính này; không âm thầm chọn công thức khác.
- Số mốc dựng một công thức; mọi vòng lặp dùng lại công thức ấy. **Số mốc không phải số vòng lặp.** Dung sai vị trí, phần dư và giới hạn vòng độc lập.

## Kiểm thử hồi quy đúng lỗi người dùng báo

Bảng 36 mốc: x_i=1+0.115i, y_i=2x_i−2.95, mức 1.23, khoảng [2.035,2.15]. Cả hai chiều giữ đủ 36 mốc, bậc tối đa 35, bậc thực tế 1 và trả x=2.09. Tiến giữ gốc 1, T=[9,10]; lùi giữ gốc 5.025, T=[−26,−25]. Không chuyển gốc theo vị trí khoảng rồi đòi các mốc không tồn tại.

Với workbook 104 mốc thật vừa cấp: hai bài lặp cục bộ được khai báo rõ đều đạt sau 5 vòng; dùng nguyên bảng thực sự tràn số ở vòng 3/2. Báo cáo giữ đủ mốc và lý do dừng, không tạo nghiệm thay thế. Xem [kiểm định đề thật](Kiem_dinh_de_20251.md) và [các JSON mở lại được](examples/de_20251).

## Trình bày bài giải

Bảy khối: dữ liệu/lựa chọn → tiền kiểm → sai phân → công thức → căn cứ hội tụ → vòng lặp → kết luận. Bảng sai phân đặt cạnh công thức khi đủ rộng, nhóm tự xếp một cột khi hẹp. Bảng lùi ∇ nằm đúng hàng kết thúc. Một bảng tổng hợp có hàng 0 và mọi vòng; từng ô sai phân, số hạng, phép thế số và phép kiểm tra mở riêng. Mở chi tiết hoặc thay độ rộng không giải lại bài.

Báo cáo phân biệt độ thay đổi bước thực hành với cận sai số có chứng nhận. Giữ quỹ đạo cả khi vượt khoảng, chạm giới hạn vòng hoặc tràn số. HTML/TXT giữ đủ hàng và công thức ngoại tuyến; chi tiết tự mở khi in, bảng dài lặp tiêu đề, bảng quá rộng chia nhóm cột khi in.

Cận sai số chỉ nói về nghiệm đa thức mô hình. Sai số với hàm thật cần thêm cận nội suy/độ dốc, miền và nguồn giả thiết. Chưa có chứng nhận toàn bộ sai số máy bằng số học khoảng. Đúng lựa chọn mốc và triển khai công thức không bảo đảm mọi dữ liệu đều tạo ánh xạ lặp hội tụ.
