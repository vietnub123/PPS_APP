# Bài thi thử 20241 — Đề 2, Sheet3

Đọc [bài giải HTML](../../Bai_giai_de_20241.html) để xem công thức, bảng và các vòng lặp được bố trí đầy đủ, ngoại tuyến. [Bản Markdown](../../Bai_giai_de_20241.md) dùng để đọc/sửa trong IDE. [Nhật ký thực hiện](Nhat_ky_thuc_hien.md) ghi nguồn và lựa chọn thuật toán.

Nguồn: `kienthuc/20241_MI3042_GK.jpg` và `kienthuc/20241GKtest2.xlsx`, **Sheet3**, x̄=4, ȳ=6, 106 cặp. Không dùng dữ liệu 20251 hoặc Sheet2. Các công thức, chương trình và phép kiểm chỉ dựa trên repo này.

| JSON mở trong PPS | Nội dung |
|---|---|
| A_Horner.json | Câu a: P″,P‴ tại 2.57, giữ hệ số x² bằng 0 |
| C_Stirling_9.json | Câu c: chọn 9/106 mốc, tính P(4),P′(4) |
| D1_Lap_tien.json | Câu d: nhánh [2.638,2.755], tiến, 9 mốc |
| D2_Lap_tien.json | Nhánh [3.691,3.808], tiến; đúng cùng đa thức với câu c |
| D3_Lap_tien.json | Nhánh [8.254,8.371], tiến, 9 mốc |
| D4_Lap_lui.json | Nhánh [10.594,10.711], lùi, 9 mốc |
| D4_Thu_tien_chua_du_chung_nhan.json | Lượt khảo sát có chủ đích: khởi tạo tiến nằm ngoài J, báo chưa đủ chứng nhận |

Mỗi JSON có bản HTML/TXT cùng tên do bộ tính trong repo xuất, giữ đầy đủ phép thế số từng vòng. Câu b là thuật toán tổng quát, được viết trong bài giải chính. CSV lưu toàn bộ dữ liệu đã trích và ánh xạ dòng Excel. `ket_qua_va_nguon.json` lưu kết quả, phép kiểm và SHA-256 nguồn.

Tái lập từ thư mục gốc, không cần mạng:

```bat
.venv\Scripts\python.exe examples\de_20241\giai_de.py
CHAY_CONSOLE.bat examples\de_20241\A_Horner.json
CHAY_CONSOLE.bat examples\de_20241\C_Stirling_9.json
CHAY_CONSOLE.bat examples\de_20241\D2_Lap_tien.json
```

Đề không ấn định dung sai hoặc bậc cho câu d. Bài giải công bố lựa chọn: 9 mốc/bậc tối đa8 ở mỗi nhánh, ε_x=ε_y=10⁻⁶, tối đa100 vòng. Các cận là cận giải phương trình của mô hình nội suy; chưa có dữ kiện để chặn tổng sai số với hàm thật.
