# Cập nhật lời giải nội suy, đạo hàm và Horner

Triển khai theo bộ đặc tả trong `kienthuc/real` đã được người dùng duyệt. Bài mẫu trực tiếp của app: [mục lục](examples/trinh_bay_noi_suy/README.md).

## Nội suy đa thức

Áp dụng Lagrange, Newton tỉ sai phân tiến/lùi, Newton đều tiến/lùi, Gauss I/II, Stirling và Bessel. Lời giải có tập mốc/ID gốc, điều kiện, đổi biến, công thức đầy đủ, bảng trung gian, nguồn từng hệ số, giai thừa/mẫu chia, tích cơ sở và bảng thế số cộng từng hạng.

Khi yêu cầu đạo hàm cấp dương, app trình bày cả giá trị hàm và đạo hàm trên cùng tập mốc. Đạo hàm tích không chia cho nhân tử bằng 0; hệ số h^−s được ghi rõ. Bessel tại tâm vẫn giữ đóng góp đạo hàm từ các hạng có giá trị bằng 0.

Tính trung gian Decimal với độ chính xác của mô hình. Báo cáo đối chiếu tổng theo công thức đã chọn với Horner Newton ổn định trên các mốc nhập; nếu lệch đáng kể, có cảnh báo và trạng thái riêng. Bảng nhỏ kiểm tra trực tiếp công thức tại từng mốc. Không dùng đa thức khai triển theo x có hệ số rất lớn để thay lời giải theo biến chuẩn hóa.

## Horner và đạo hàm từ bảng

Horner ghi đúng các phép nhân–cộng đã sinh ra kết quả, thương và số dư của mỗi lượt; giải thích s_r=P^(r)(c)/r!; bảng tổng kết nhân giai thừa. Giữ hệ số 0 giữa/cuối, xác định bậc thực khi có 0 đầu dãy, không tạo các lượt thừa khi cấp đạo hàm vượt bậc.

Đạo hàm từ bảng công bố cửa sổ mốc được chọn. Mỗi trọng số có mẫu số, hệ số Taylor, giai thừa và quá trình nhân từng nhân tử; bảng đóng góp có tổng tích lũy và kiểm tra moment. Nhận diện các công thức hai/ba điểm quen thuộc khi mốc và điểm tính khớp đúng điều kiện.

Các phần bổ trợ chọn mốc, Chebyshev và điền dữ liệu theo giả thiết bậc cũng có lời giải, các mốc/ứng viên đã xét và điều kiện kết luận. Không bổ sung màn hình nhập liệu mới cho API chưa có trong GUI.

## Trình bày và bản xuất

Tk, TXT và HTML đọc cùng cây lời giải và các bảng đã tính. Hai bảng nhỏ đặt cạnh nhau khi đủ rộng; bảng rộng cuộn ngang; các phép tính dài có nhóm chi tiết độc lập. Bản xuất giữ đủ dữ liệu và mở chi tiết khi in. Chữ số trong bài JSON được dùng cho nội suy, đạo hàm, Horner và chọn mốc.

Các HTML/TXT trong `examples/trinh_bay_noi_suy` được xuất nguyên từ `dispatch`, cùng đường chạy của nút Tính kết quả. Script xuất mẫu chỉ đọc JSON và lưu báo cáo; không tính đáp án hoặc chèn bảng riêng như script bài giải trước.

## Kiểm tra

- Đối chiếu từng hạng và đạo hàm của các công thức với đa thức Lagrange hữu tỷ dựng độc lập, gồm cả Gauss số mốc chẵn/lẻ.
- Đối chiếu Stirling chín mốc từ toàn bộ Sheet3 đề 20241 và bốn lượt Horner của câu a.
- Kiểm trọng số/moment, mốc không đều, trùng điểm tính với mốc, đổi biến h khác 1, số dư/hệ số bằng 0, cấp đạo hàm vượt bậc và ánh xạ dòng sau sắp/chọn mốc.
- Kiểm việc dựng công thức, xuất HTML ngoại tuyến, bảng đầy đủ, cột và chi tiết in; giữ các kiểm tra ca biên/bảng lớn có sẵn.

Kết quả: `python -m unittest discover -s tests -q` chạy **218 test**, hoàn tất `OK (skipped=1)`. Bộ kiểm tra riêng lời giải/công thức hiển thị chạy **17 test**, đều qua; sáu bài mẫu chạy CLI thành công và xuất HTML ngoại tuyến đủ bảng/công thức. `py_compile` và kiểm tra lỗi khoảng trắng trong diff đều qua.

Môi trường hiện tại không khởi tạo được Tcl/Tk (`init.tcl` không dùng được), nên một nhóm kiểm tra cửa sổ GUI được bỏ qua. Các hình xem bảng dùng bộ vẽ của app, không được gọi là ảnh GUI. Cần mở lại app đang chạy để nạp phiên bản mã mới.
