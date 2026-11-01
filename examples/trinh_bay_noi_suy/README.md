# Mẫu lời giải xuất trực tiếp từ app

Các HTML/TXT ở đây lấy nguyên `Report` từ `pps.gui.dispatch`, cùng đường tính của nút **Tính kết quả**. Script `xuat_mau.py` chỉ đọc bài JSON và xuất báo cáo; không tự tính lại đáp án hay thêm bảng trình bày.

| Mẫu | Nguồn và nội dung |
|---|---|
| [01 — Stirling đề 20241](01_Stirling_20241.html) | Toàn bộ 106 cặp Sheet3 trong `kienthuc/20241GKtest2.xlsx`, z=4, chọn 9 mốc, lấy cả giá trị và đạo hàm cấp 1. Có ánh xạ ID 22..30, bảng sai phân, nguồn hệ số, bảng thế từng hạng và đổi biến. |
| [02 — Horner đề 20241](02_Horner_20241.html) | Đa thức câu a từ ảnh đề; c=2.57, đạo hàm đến cấp 3. Có bốn lượt nhân–cộng, thương, số dư và giai thừa. |
| [03 — Bessel tại giữa hai mốc](03_Bessel_tam.html) | Ví dụ tự dựng x=[−1,0,1,2], y=[0,1,2,9], z=0.5. Cho thấy hạng lẻ có giá trị 0 vẫn đóng góp vào đạo hàm. |
| [04 — Đạo hàm mốc bất kỳ](04_Dao_ham_moc_bat_ky.html) | Ví dụ tự dựng x=[0,1,3], y=[1,3,13], z=1, p=2,s=1. Có quá trình dựng trọng số và kiểm tra moment. |
| [05 — Newton tỉ sai phân lùi](05_Newton_bat_ky_lui.html) | Cùng bảng tự dựng không đều, z=2; thấy hệ số tỉ sai phân không chia thêm giai thừa. |
| [06 — Đạo hàm ở đầu bảng](06_Dao_ham_dau_bang.html) | Ví dụ tự dựng x=[0,1,2], y=[1,2,5], z=0,p=2,s=1. Tập mốc một phía và công thức ba điểm tiến. |

Mở HTML bằng trình duyệt để đọc/in ngoại tuyến. Mở JSON bằng **Mở bài** trong app để chạy lại. Mỗi mẫu có TXT với toàn bộ các bước, kể cả chi tiết đang thu gọn trên màn hình.

Từ thư mục gốc repo, xuất lại:

```powershell
.venv\Scripts\python.exe examples\trinh_bay_noi_suy\xuat_mau.py
```

Các số trong bảng được làm tròn để đọc; quá trình tính giữ độ chính xác trung gian. Bài mẫu không tự cung cấp cận sai số đối với hàm thật.

Xem nhanh hình bảng được dựng bằng cùng bộ vẽ của app: [Stirling](Xem_bang_Stirling.png), [Horner](Xem_bang_Horner.png). Đây là hình xem các bảng, không phải ảnh chụp cửa sổ GUI.
