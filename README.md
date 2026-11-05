# Hotel Booking Cancellation Prediction (CO3117)

Dự án BTL môn Học máy: dự đoán booking khách sạn có bị hủy hay không.

## 1. Yêu cầu
- Python 3.10 hoặc 3.11
- Git
- Kết nối Internet khi tải dữ liệu lần đầu

## 2. Cài đặt

```bash
git clone <URL_REPOSITORY>
cd <TEN_REPOSITORY>

py -3.11 -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Tải dữ liệu

```bash
python scripts/download_data.py
```

CSV được lưu tại `data/raw/hotels.csv`. Script không ghi đè file đã có, trừ khi dùng:

```bash
python scripts/download_data.py --force
```

Nguồn: [TidyTuesday – Hotel bookings CSV](https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-02-11/hotels.csv).

## 4. Kiểm tra dữ liệu

```bash
python -c "from src.data import load_raw; df = load_raw(); print(df.shape); print(df.head())"
```

Mục tiêu là `is_canceled` (0: không hủy, 1: hủy). Không đưa `reservation_status` và `reservation_status_date` vào mô hình vì đây là các trường có nguy cơ rò rỉ thông tin sau thời điểm đặt phòng; danh sách cột cuối cùng sẽ được nhóm chốt tại M1.

## 5. Cấu trúc

```text
.
├── data/
│   ├── raw/                 # CSV gốc, không chỉnh sửa
│   └── processed/           # dữ liệu trung gian (không commit file lớn)
├── docs/                    # quyết định dữ liệu, split, metric
├── notebooks/                # notebook theo thứ tự thực hiện
├── reports/
│   ├── figures/
│   └── results/
├── scripts/
│   └── download_data.py
├── src/
│   ├── config.py
│   ├── data.py
│   ├── features.py
│   ├── preprocess.py
│   ├── split.py
│   └── evaluate.py
├── .gitignore
└── requirements.txt
```

## 6. Quy ước làm việc nhóm
- Seed dùng chung: `RANDOM_STATE = 42` trong `src/config.py`.
- Mỗi thành viên làm trên nhánh riêng; chỉ merge sau review.
- Commit theo Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, ...
- Notebook phải chạy được từ đầu đến cuối (Restart & Run All).
- Không commit `.venv/`, cache, dữ liệu tải về hoặc mô hình lớn.
- Các hàm chia dữ liệu và đánh giá phải dùng chung từ `src/split.py` và `src/evaluate.py`, không tự viết lại ở từng notebook.

## 7. Function contract
Các chữ ký hàm được thống nhất trong `docs/function_contracts.md`. Khi thay đổi chữ ký, cần báo cả nhóm và cập nhật tài liệu trước khi các nhánh phụ thuộc triển khai.
