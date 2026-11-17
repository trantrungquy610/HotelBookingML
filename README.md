# Hotel Booking Cancellation Prediction (CO3117)

Dự án BTL môn Học máy: dự đoán booking khách sạn có bị hủy hay không.

## 1. Yêu cầu
- Python 3.10 hoặc 3.11
- Git
- Kết nối Internet khi tải dữ liệu lần đầu

## 2. Cài đặt

```bash
git clone https://github.com/trantrungquy610/HotelBookingML.git
cd HotelBookingML

# Windows PowerShell:
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
# macOS/Linux:
python3.11 -m venv .venv
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

Nguồn: [TidyTuesday – Hotel bookings CSV](https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-02-11/hotels.csv) (tải trực tiếp, không cần đăng nhập). Cùng dữ liệu này có trên [Kaggle – Hotel booking demand](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand). Bài báo gốc: Antonio, de Almeida, Nunes (2019), *Hotel booking demand datasets*, Data in Brief 22, [doi:10.1016/j.dib.2018.11.126](https://doi.org/10.1016/j.dib.2018.11.126).

## 4. Kiểm tra dữ liệu

```bash
python -c "from src.data import load_raw; df = load_raw(); print(df.shape); print(df.head())"
```

Mục tiêu là `is_canceled` (0: không hủy, 1: hủy). Các quyết định về dữ liệu đã chốt (chi tiết và lý do trong `docs/decisions.md`):

- **Làm sạch** (`src/preprocess.py::clean_data`): bỏ 185 dòng lỗi, còn 119.205 booking.
- **Bộ cột sạch** (dùng cho mọi mô hình chính): 22 cột chỉ gồm thông tin có tại lúc đặt phòng, cộng đặc trưng `arrival_weekday` (`src/features.py`), tổng cộng 23 đặc trưng. Các cột có nguy cơ rò rỉ dữ liệu như `reservation_status`, `deposit_type`, `country` bị loại.
- **Bộ cột thông thường** (30 đặc trưng, giữ lại 7 cột có nguy cơ rò rỉ): chỉ dùng cho thí nghiệm TN1. Danh sách cột của hai bộ nằm trong `src/modeling.py::FEATURE_SETS`.
- **Chia dữ liệu theo ngày đến** (`src/split.py::temporal_split`): train trước 01/01/2017 (78.586 dòng), validation 01–06/2017 (30.386 dòng), test 07–08/2017 (10.233 dòng).

## 5. Chạy các notebook

Sau khi cài môi trường (Mục 2) và tải dữ liệu (Mục 3), chạy các notebook trong `notebooks/` theo thứ tự dưới đây. Trong cột "File tạo ra", `results.csv` là `reports/results/results.csv`; hình được lưu trong `reports/figures/`.

| Thứ tự | Notebook | Nội dung | File tạo ra | Thời gian |
|---|---|---|---|---|
| 1 | `01_eda.ipynb` | Khám phá dữ liệu (EDA): phân bố, xu hướng hủy, khác biệt City/Resort, bằng chứng rò rỉ dữ liệu | 13 hình EDA | 17 giây |
| 2 | `02_features.ipynb` | Chọn đặc trưng mới bằng cross-validation theo thời gian trên train | `feature_candidates.png`, `feature_ablation_cv.png` | 41 giây |
| 3 | `03_baseline.ipynb` | Mô hình mốc: Dummy Classifier và Logistic Regression (CV + validation) | 4 dòng trong `results.csv` | 12 giây |
| 4 | `04_gradient_boosting.ipynb` | Tinh chỉnh Gradient Boosting (LightGBM), đánh giá trên validation, permutation importance | `models/gradient_boosting_best_params.json`, 2 dòng `results.csv`, `gradient_boosting_*.png` | 44 giây |
| 5 | `05_random_forest.ipynb` | Tinh chỉnh Random Forest (36 cấu hình), đánh giá trên validation, permutation importance | `models/random_forest_best_params.json`, 2 dòng `results.csv`, `random_forest_*.png` | khoảng 13 phút |
| 6 | `06_logistic_regression_tuning.ipynb` | Tinh chỉnh Logistic Regression, đánh giá trên validation, permutation importance | `models/logistic_regression_best_params.json`, 2 dòng `results.csv`, `logistic_regression_*.png` | 37 giây |
| 7 | `07_tn1_leakage_split.ipynb` | TN1: bộ cột thông thường/sạch × chia ngẫu nhiên/theo thời gian | 24 dòng `TN1` trong `results.csv`, `reports/results/tn1_summary.csv`, `tn1_leakage_split_comparison.png` | khoảng 2 phút |
| 8 | `08_tn2_hotel_transfer.ipynb` | TN2: học trên một khách sạn, đánh giá trên khách sạn còn lại (City ↔ Resort) | 12 dòng `TN2` trong `results.csv`, `reports/results/tn2_summary.csv`, `tn2_*.png` | 21 giây |
| 9 | `09_tn3_cost_threshold.ipynb` | TN3: chọn ngưỡng theo chi phí trên validation (gọi `scripts/run_tn3_cost_threshold.py`) | `models/cost_thresholds.json`, 9 dòng `TN3` trong `results.csv`, `tn3_cost_by_threshold.png` | 36 giây |
| 10 | `10_final_test_evaluation.ipynb` | Đánh giá cuối một lần trên test, ở ngưỡng 0,5 và ngưỡng theo chi phí (gọi `scripts/run_final_test.py`) | `reports/results/final_test.csv`, `final_test_confusion_matrices.png` | 13 giây |

Thời gian đo trên laptop Intel Core i7-14650HX (16 nhân, 24 luồng), RAM 16 GB; chạy cả 10 notebook mất khoảng 19 phút, trong đó riêng notebook 05 mất khoảng 13 phút. Máy có ít nhân hơn sẽ chạy lâu hơn, nhất là notebook 05.

**Phụ thuộc giữa các notebook**

- Notebook 07–10 đọc siêu tham số tốt nhất từ `models/*_best_params.json` (do 04–06 tạo); notebook 10 đọc thêm ngưỡng từ `models/cost_thresholds.json` (do 09 tạo).
- Các file này đã có sẵn trong repo, nên có thể chạy riêng một notebook bất kỳ mà không cần chạy lại các notebook trước nó. Ví dụ, chỉ chạy `10_final_test_evaluation.ipynb` để xem kết quả cuối trên test.
- Mỗi notebook chỉ thay các dòng của chính nó trong `results.csv`, nên chạy lại không làm trùng dòng hay xóa kết quả của notebook khác.
- Chạy lại sẽ ghi đè các file kết quả và hình bằng kết quả vừa chạy. Kết quả trùng với bản đã lưu trong repo (tag `results-v1`): khi chạy lại cả 10 notebook từ một bản sao mới theo đúng các bước trong README, sai lệch lớn nhất của các metric là khoảng 1e-6 (do sai số tính toán số thực), còn siêu tham số và ngưỡng đã lưu giống hệt.

**Cách 1: chạy trong VS Code**

1. Mở thư mục dự án bằng VS Code.
2. Mở notebook tương ứng trong thư mục `notebooks/`.
3. Chọn Python kernel là môi trường `.venv` đã tạo ở Mục 2.
4. Chọn Run All để chạy toàn bộ notebook.

**Cách 2: chạy bằng dòng lệnh** (từ thư mục gốc của dự án, sau khi đã kích hoạt `.venv`)

Chạy một notebook:

```bash
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 notebooks/01_eda.ipynb
```

Chạy lần lượt cả 10 notebook:

```bash
# macOS/Linux (bash):
for nb in notebooks/*.ipynb; do jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 "$nb"; done
```

```powershell
# Windows PowerShell:
Get-ChildItem notebooks/*.ipynb | Sort-Object Name | ForEach-Object { jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 $_.FullName }
```

Notebook 09 và 10 chỉ gọi script trong `scripts/`, nên cũng có thể chạy trực tiếp:

```bash
python scripts/run_tn3_cost_threshold.py
python scripts/run_final_test.py
```

## 6. Cấu trúc

```text
.
├── data/
│   ├── raw/                  # hotels.csv tải bằng scripts/download_data.py (không commit)
│   └── processed/            # dữ liệu trung gian (không commit)
├── docs/                     # quyết định dữ liệu, split, metric, function contract
├── models/                   # siêu tham số tốt nhất (*_best_params.json), ngưỡng theo chi phí
├── notebooks/                # 10 notebook, chạy theo thứ tự 01 → 10
├── reports/
│   ├── figures/              # hình dùng trong báo cáo
│   └── results/              # results.csv, tn1_summary.csv, tn2_summary.csv, final_test.csv
├── scripts/
│   ├── download_data.py
│   ├── run_tn3_cost_threshold.py
│   └── run_final_test.py
├── src/
│   ├── config.py             # đường dẫn, seed, cột mục tiêu, danh sách cột phân loại
│   ├── data.py               # đọc dữ liệu gốc
│   ├── eda.py                # tính tỉ lệ hủy, vẽ và lưu hình EDA
│   ├── preprocess.py         # làm sạch, Pipeline tiền xử lý
│   ├── features.py           # tạo đặc trưng arrival_weekday
│   ├── split.py              # chia theo thời gian, ngẫu nhiên, theo khách sạn
│   ├── modeling.py           # bộ đặc trưng, tạo mô hình từ siêu tham số đã lưu
│   └── evaluate.py           # metric, CV theo thời gian, chọn ngưỡng, ghi results.csv
├── .gitignore
├── README.md
└── requirements.txt
```

## 7. Quy ước làm việc nhóm
- Seed dùng chung: `RANDOM_STATE = 42` trong `src/config.py`.
- Mỗi thành viên làm trên nhánh riêng; chỉ merge sau review.
- Commit theo Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, ...
- Notebook phải chạy được từ đầu đến cuối (Restart & Run All).
- Không commit `.venv/`, cache, dữ liệu tải về hoặc mô hình lớn.
- Các hàm chia dữ liệu và đánh giá phải dùng chung từ `src/split.py` và `src/evaluate.py`, không tự viết lại ở từng notebook.

## 8. Function contract
Các chữ ký hàm được thống nhất trong `docs/function_contracts.md`. Khi thay đổi chữ ký, cần báo cả nhóm và cập nhật tài liệu trước khi các nhánh phụ thuộc triển khai.
