# PPS_APP — Ứng dụng Tính toán & Phương pháp số

**PPS_APP** là phần mềm tính toán khoa học và giải bài toán số học chuyên sâu viết bằng **Python** kết hợp giao diện đồ họa trực quan (**Tkinter**). Ứng dụng hỗ trợ trình bày lời giải toán học bằng công thức LaTeX sắc nét (MathText), vẽ đồ thị tương tác, lập bảng sai phân / bảng tích chuẩn mực và xuất báo cáo đa định dạng (HTML, Excel, CSV, JSON).

---

## 🌟 Tính năng chính

### 1. Nội suy & Xấp xỉ hàm số
- **Đa thức nội suy**:
  - Lagrange, Newton (mốc bất kỳ qua tỷ sai phân, mốc cách đều tiến / lùi).
  - Nội suy trung tâm: Gauss I, Gauss II, Stirling, Bessel (hỗ trợ ký hiệu chuẩn $t$, $h$, $x_0$).
  - Không còn chặn 100 mốc: bảng lớn giữ dạng tích và dùng số thập phân với độ chính xác tăng theo dữ liệu; đã kiểm tra Stirling 501 mốc.
  - Ô **Số mốc dùng** cho phép chọn K mốc quanh điểm tính từ toàn bộ bảng; để trống để dùng toàn bảng. Stirling dùng số lẻ; Bessel dùng số chẵn.
  - Bảng sai phân so le và bảng tích bậc giảm dần theo đúng chuẩn bài giảng.
- **Nội suy ngược**: Lặp tiến/lùi với tiêu chuẩn dừng thực hành; nhánh lặp có kiểm tra co trên đoạn nhập; nội suy bảng đảo và chia đôi nghiệm đa thức thuận.
- **Đường cong Spline**: Tuyến tính, bậc hai có đạo hàm biên, bậc ba với biên tự nhiên/kẹp/cấp hai/tuần hoàn/not-a-knot; bậc bốn với ba đạo hàm đầu trái.
- **Hồi quy bình phương tối thiểu (Least Squares)**:
  - Đa thức bậc tùy ý, hàm lũy thừa ($y = a x^b$), hàm mũ ($y = a e^{bx}$), hoặc tổ hợp hàm cơ sở tự chọn.
  - Hỗ trợ trọng số dương và giải bình phương tối thiểu bằng SVD. Mô hình log kiểm tra miền xác định, không tự dịch dữ liệu.
- **Đa thức Chebyshev & Sơ đồ Horner**:
  - Sinh $n+1$ mốc Chebyshev tối ưu trên đoạn $[a, b]$.
  - Thuật toán Horner tính giá trị đa thức và các cấp đạo hàm.

### 2. Đạo hàm & Tích phân số
- **Đạo hàm số từ bảng mốc**: Lập công thức đạo hàm nhiều cấp (cấp 1 đến $p$) dựa trên hệ số trọng số Lagrange.
- **Tích phân số 1 chiều**:
  - Nhập từ biểu thức giải tích $f(x)$ hoặc bảng số liệu rời rạc $(x, y)$.
  - Các công thức: Hình thang (Trapezoidal), Simpson 1/3, Simpson 3/8, Trung điểm (Midpoint), Newton-Cotes bậc 1 đến 10.
  - Tự động chia lưới theo dung sai mong muốn hoặc ước lượng sai số theo quy tắc Runge / cận đạo hàm $M$.
- **Tích phân kép**: Tính tích phân trên miền chữ nhật $[a, b] \times [c, d]$ bằng phương pháp tích Tensor lưới tự tinh chỉnh.

### 3. Phương trình vi phân (ODE)
- Giải bài toán giá trị ban đầu (Cauchy) cho **một phương trình** hoặc **hệ phương trình vi phân cấp 1**:
  - Phương pháp Euler (Hiện & Ẩn).
  - Phương pháp Hình thang (Trapezoidal ODE).
  - Họ Runge-Kutta: RK2 (Euler cải tiến, Heun), RK3, RK4 cổ điển, RK tham số.
  - Phương pháp đa bước Adams: Adams-Bashforth (dự báo) kết hợp Adams-Moulton (hiệu chỉnh) từ cấp 2 đến cấp 5.
  - Bảng Butcher tùy biến cho phương pháp Runge–Kutta hiện (ma trận tam giác dưới nghiêm ngặt).

### 4. Bài toán biên (BVP) & Bài toán trị riêng
- **Bài toán biên cấp 2**: Giải phương trình dạng $[p(x)u']' - q(x)u = -f(x)$ với các loại điều kiện biên:
  - Dirichlet ($u$ tại biên)
  - Neumann ($u'$ tại biên)
  - Robin (kết hợp tuyến tính $\alpha u' + \beta u = \gamma$)
  - Sử dụng sai phân hữu hạn đưa về hệ ma trận ba đường chéo (Tridiagonal matrix).
- **Bài toán trị riêng**: Tìm các trị riêng nhỏ nhất và đồ thị hàm riêng tương ứng.

---

## 🚀 Hướng dẫn cài đặt & Khởi chạy

### Yêu cầu hệ thống
- Hệ điều hành: Windows 10/11 (hoặc Linux/macOS có cài đặt môi trường đồ họa Tk).
- Cài mới trên Windows: **Python 3.12, 64-bit**, có `pip`, `venv` và **Tcl/Tk (Tkinter)**.
- **Python 3.11 không chạy được bản mã hiện tại.** Lỗi `f-string expression part cannot include a backslash` trong ảnh là lỗi cú pháp do phiên bản Python; đổi dữ liệu Stirling hoặc cài lại thư viện không giải quyết được. Python 3.12 hỗ trợ cú pháp này theo [PEP 701 trong tài liệu Python](https://docs.python.org/3.12/whatsnew/3.12.html#pep-701-syntactic-formalization-of-f-strings).

### Cách 1: Khởi chạy nhanh trên Windows (Khuyên dùng)
1. Cài **Python 3.12 64-bit** từ Python.org. Có thể dùng [trang Python 3.12.10](https://www.python.org/downloads/release/python-31210/), mục **Windows installer (64-bit)**. Chọn bản cài đầy đủ, không dùng *embeddable package*. Giữ các thành phần **pip**, **tcl/tk and IDLE**, **Python Launcher**; nên bật **Add python.exe to PATH**. Không cần gỡ Python 3.11 đang dùng cho dự án khác.
2. Mở một terminal mới, kiểm tra:

   ```powershell
   py -3.12 --version
   py -3.12 -c "import struct; print(struct.calcsize('P') * 8)"
   ```

   Kết quả phải là `Python 3.12.x` và `64`.
3. Đóng ứng dụng PPS, chạy **`CAI_DAT.bat`**. Bộ cài chọn rõ Python 3.12 64-bit, tạo `.venv`, nâng cấp pip, cài các phiên bản trong `requirements.txt`, kiểm tra phụ thuộc và biên dịch/import các mô-đun để phát hiện lỗi môi trường ngay khi cài.
4. Chạy **`CHAY_PPS.bat`** để mở ứng dụng. Các file chạy luôn dùng Python của `.venv`, không tự quay về một Python mặc định có thể là 3.11. Môi trường 3.13 64-bit đang hoạt động vẫn được các file chạy chấp nhận; bộ cài chuẩn hóa môi trường mới về 3.12.

**Nếu đã có `.venv` từ Python 3.11 hoặc môi trường bị hỏng:** chỉ cần chạy lại `CAI_DAT.bat` sau khi cài Python 3.12. Bộ cài đổi tên thư mục cũ thành `.venv.backup-<thời gian>-<mã>` trong cùng repo rồi tạo `.venv` mới; không xóa môi trường cũ. `.venv` đã đúng 3.12 64-bit được dùng lại và cài/kiểm tra thư viện. Nếu chưa tìm thấy Python 3.12 hoặc thiếu thành phần cơ bản, bộ cài dừng trước khi thay môi trường cũ.

**Không chép `.venv` từ máy khác.** Chỉ chép mã nguồn, dữ liệu và `requirements.txt`, rồi chạy bộ cài trên máy nhận. Cài thêm Python 3.12 không tự nâng cấp `.venv` cũ.

Nếu không có lệnh `py` hoặc Python nằm ở đường dẫn tùy chỉnh, có thể chỉ rõ file thực thi:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup_environment.ps1 -PythonExe "C:\duong-dan\Python312\python.exe"
```

`ExecutionPolicy Bypass` ở đây chỉ áp dụng cho tiến trình chạy script cài đặt; không đổi thiết lập PowerShell toàn máy. Nếu pip báo chưa tải được thư viện, kiểm tra Internet và chạy lại `CAI_DAT.bat`.

Để chạy không cần cửa sổ Tk, dùng `CHAY_CONSOLE.bat examples\02_bessel.json` hoặc `.venv\Scripts\python.exe exam_cli.py examples\02_bessel.json`. Chuẩn bị thư viện trước khi ngắt mạng. Xem [hướng dẫn dùng khi thi](Huong_dan_dung_khi_thi.md), [báo cáo kiểm định](Bao_cao_kiem_dinh.md) và [bảng bao phủ](Bao_phu_kien_thuc.csv).

Đợt kiểm tra các thuật toán còn lại và các lỗi đã sửa ở ODE, biên Robin, trị riêng, spline, hồi quy và tích phân được ghi trong [kiểm định thuật toán khác](Kiem_dinh_thuat_toan_khac.md).

### Cách 2: Tạo môi trường thủ công bằng đúng Python 3.12

Trên Windows, đóng PPS và giữ bản sao `.venv` cũ nếu có. Cách đơn giản để đổi phiên bản là dùng `CAI_DAT.bat` ở trên. Với thư mục **chưa có `.venv`**, chạy:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe main.py
```

Không cần kích hoạt môi trường khi dùng đường dẫn Python đầy đủ như trên. Không dùng `py -3 -m venv` hoặc `pip` trần vì chúng có thể trỏ sang phiên bản khác.

Trên Linux/macOS, dùng Python 3.12 có hỗ trợ Tk và môi trường mới:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

### Kiểm tra sau khi cài / xử lý lỗi phiên bản

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
.\.venv\Scripts\python.exe -m pip check
```

Python phải là `3.12.x` và đường dẫn phải nằm trong `.venv` của **đúng bản repo đang mở**. Nếu vẫn báo 3.11, chạy lại `CAI_DAT.bat`; trong VS Code chọn **Python: Select Interpreter → .venv\Scripts\python.exe** rồi mở terminal mới.

Để kiểm tra cửa sổ Tk, chạy `py -3.12 -m tkinter`. Nếu thiếu `_tkinter` hoặc không tìm được `init.tcl`, mở trình cài Python 3.12, dùng **Modify/Repair** và cài **tcl/tk and IDLE**, rồi chạy lại bộ cài repo. Không cài `tkinter` bằng pip. Nếu chạy từ nút Run của IDE vẫn lỗi nhưng `CHAY_PPS.bat` chạy được, kiểm tra lại interpreter mà IDE đã chọn.

---

## 🖥️ Hướng dẫn sử dụng nhanh

1. **Chọn phương pháp**: Ở cột danh mục bên trái, chọn nhóm công cụ (Nội suy, Đạo hàm, Tích phân, Vi phân, Biên...) rồi chọn thuật toán cụ thể.
2. **Nhập dữ liệu**:
   - Dán hoặc gõ dãy mốc $x, y$ (cách nhau bởi dấu cách hoặc xuống dòng).
   - Nhập từ file **Excel (.xlsx)** hoặc **CSV** bằng nút **Nhập bảng**.
   - Hỗ trợ nhập hàm số toán học: `sin(x)`, `cos(x)`, `exp(x)`, `ln(x)`, `sqrt(x)`, `x^2`...
3. **Tính toán**: Nhấn nút **Tính kết quả** (hoặc phím tắt **`Ctrl + Enter`**).
4. **Xem & Xuất kết quả**:
   - **Tab Lời giải toán học**: Hiển thị công thức ký hiệu toán LaTeX trực quan, các bước phân tích chi tiết.
   - **Tab Bảng số liệu**: Xem bảng sai phân, bảng tích, bảng bước tính dạng bảng trực quan.
   - **Tab Đồ thị**: Đồ thị trực quan với các công cụ phóng to (zoom), di chuyển (pan), đặt lại góc nhìn và lưu ảnh.
   - **Lưu bài / Mở bài** (`Ctrl + S` / `Ctrl + O`): Lưu toàn bộ thông số đầu vào vào file `.json` để tiếp tục làm việc sau.
   - **Lưu lời giải**: Xuất báo cáo lời giải độc lập ra file HTML (có sẵn công thức KaTeX & hình ảnh) hoặc TXT.
   - **Xuất bảng**: Lưu bảng dữ liệu số ra file Excel (`.xlsx`) hoặc `.csv`.

---

## 📁 Cấu trúc thư mục

```text
PPS_APP/
├── pps/                        # Gói mã nguồn cốt lõi của ứng dụng
│   ├── gui.py                  # Giao diện người dùng Tkinter & điều phối tác vụ
│   ├── interpolation.py        # Thuật toán nội suy, xấp xỉ, spline, bình phương tối thiểu
│   ├── calculus.py             # Tính đạo hàm & tích phân số
│   ├── differential.py         # Phương trình vi phân ODE, bài toán biên BVP & trị riêng
│   ├── common.py               # Xử lý chuỗi biểu thức, bảng sai phân, xác thực dữ liệu
│   └── math_view.py            # Dựng công thức MathText LaTeX và xuất báo cáo HTML
├── examples/                   # Các ví dụ mẫu (.json) cho từng phương pháp
├── tests/                      # Bộ kiểm thử tự động (Unit tests & GUI tests)
├── data/                       # Dữ liệu bài tập đã trích xuất
├── output/                     # Báo cáo, ảnh lời giải và kết quả chạy bài tập
├── CAI_DAT.bat                 # Script cài đặt môi trường tự động
├── scripts/                    # Chọn Python 3.12, sao lưu/tạo .venv và kiểm tra phiên bản
├── CHAY_PPS.bat                # Script chạy nhanh ứng dụng
├── KIEM_TRA.bat                # Script chạy kiểm thử độ chính xác
├── main.py                     # Điểm khởi động ứng dụng
├── requirements.txt            # Danh sách thư viện Python cần thiết
└── README.md                   # Tài liệu giới thiệu dự án
```

---

## 🧪 Kiểm thử (Testing)

Để kiểm tra độ chính xác của toàn bộ các thuật toán và giao diện, chạy script:
```bash
KIEM_TRA.bat
```
Hoặc qua dòng lệnh:
```bash
.venv\Scripts\python.exe -m unittest discover -s tests -v
```
Bộ kiểm thử kiểm tra tái lập đa thức chuẩn, các phương pháp tích phân, ODE, cách trình bày và tải/xuất dữ liệu Excel/CSV.
