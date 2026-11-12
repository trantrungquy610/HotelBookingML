# Quyết định M1

> **Trạng thái:** đã chốt ngày 10/11/2026 (PR #3, #4). Mục 3.3 cập nhật danh sách đặc trưng sau T08.
>
> **Căn cứ:** `notebooks/01_eda.ipynb` (T03), `docs/feature_decisions.md` (T04), `docs/split_proposal.md` và `docs/metric_and_cost.md` (T05).
> Nếu các tài liệu trên mâu thuẫn với file này thì **làm theo file này**.

## 1. Luồng xử lý chung

```text
load_raw() -> clean_data() -> add_features() -> chọn cột theo bộ -> chia dữ liệu -> Pipeline (fit trên train)
  (T01)        (T07, TV1)      (T08, TV2)                            (T07, TV1)      (T07, TV1)
```

- `clean_data` và `add_features` chỉ biến đổi từng dòng theo quy tắc cố định, không học gì từ dữ liệu. Vì vậy chạy hai bước này trước khi chia không gây leakage.
- Mọi bước học từ dữ liệu (one-hot, gom mức hiếm, chuẩn hóa) phải nằm trong Pipeline và chỉ fit trên train.

## 2. Làm sạch dữ liệu: `clean_data(df, *, copy=True) -> pd.DataFrame` [đã xác nhận: TV1]

Đây là hàm mới thêm vào contract, đặt trong `src/preprocess.py`.

| Bước | Quy tắc | Số dòng (dữ liệu gốc) | Lý do |
|---|---|---:|---|
| Bỏ dòng lỗi | `adr` < 0 | 1 | Giá âm (−6,38) |
| | `adr` > 1000 | 1 | Giá 5.400, trong khi mức cao thứ hai chỉ là 510 |
| | `adults` + `children` + `babies` = 0 | 180 | Booking không có khách |
| | `children` ≥ 9 hoặc `babies` ≥ 9 | 3 | 9–10 trẻ đi cùng 1–2 người lớn |
| | **Tổng** | **185 (0,15%)** | Còn 119.205 dòng, tỉ lệ hủy 37,08% |
| Giữ dòng trùng | Không bỏ | 31.994 bản sao | Phần lớn là booking đoàn thật. Bản sao có cùng ngày đến nên khi chia theo thời gian luôn nằm chung một tập |
| Gộp `meal` | `Undefined` → `SC` | 1.169 | Theo bài báo, hai mức có cùng nghĩa. `Undefined` chỉ xuất hiện ở Resort, nên cần gộp cho TN2 |
| Điền giá trị thiếu | `children` → 0 | 4 | |
| | `agent`, `company` → chuỗi; thiếu → `"none"` | 16.340 / 112.593 | Đây là mã định danh, không phải số. Giá trị thiếu nghĩa là không đặt qua đại lý/công ty |
| | `country` thiếu → `"missing"` | 488 | Chỉ dùng ở bộ cột thông thường |
| Thêm cột ngày | `arrival_date` = ghép năm, tháng, ngày đến (kiểu datetime) | | Chỉ dùng để chia dữ liệu, **không** đưa vào X |

## 3. Bộ cột

### 3.1. Bộ cột sạch: 22 cột [đã xác nhận: TV1]

Bộ này dùng cho kết luận chính, TN1, TN2 và TN3.

```python
CLEAN_FEATURES = [
    "hotel", "lead_time", "arrival_date_month", "arrival_date_week_number",
    "arrival_date_day_of_month", "stays_in_weekend_nights", "stays_in_week_nights",
    "adults", "children", "babies", "meal", "market_segment", "distribution_channel",
    "is_repeated_guest", "previous_cancellations", "previous_bookings_not_canceled",
    "reserved_room_type", "agent", "company", "customer_type", "adr",
    "total_of_special_requests",
]
```

**Quy tắc chọn:** một cột chỉ bị bỏ khi thỏa **cả hai** điều kiện: (a) có cơ chế khiến giá trị được ghi nhận sau lúc đặt, **và** (b) có dấu hiệu thống kê bất thường. Nếu chỉ có (a), cột vẫn được giữ và ghi vào phần hạn chế. Quy tắc này giúp không bỏ nhầm các cột hợp lệ.

| Cột bị bỏ | Bằng chứng (EDA Mục 9) |
|---|---|
| `reservation_status` | Khớp 100% với nhãn |
| `reservation_status_date` | 95,3% booking hủy có ngày này trước ngày đến, còn booking Check-Out luôn có ngày ≥ ngày đến |
| `assigned_room_type` | Phòng giao khác phòng đặt thì tỉ lệ hủy chỉ 5,4% (so với 41,6%). Phòng thường được giao lúc check-in |
| `booking_changes` | Số lần sửa được đếm đến lúc check-in hoặc hủy. Có sửa thì hủy 15,7%, không sửa thì 40,9% |
| `days_in_waiting_list` | Chỉ biết sau khi booking được xác nhận |
| `deposit_type` | Tính từ các khoản thanh toán đến ngày đến hoặc ngày hủy. Non Refund hủy 99,4% (n = 14.587) |
| `country` | Quốc tịch thường chỉ được ghi đúng khi check-in. PRT hủy 56,6%, các nước khác 23,6% |
| `required_car_parking_spaces` | 7.416 booking có yêu cầu đỗ xe, không booking nào bị hủy |
| `arrival_date_year` | Không phải leakage. Lý do bỏ: năm của tập test (2017) không có trong train; mùa vụ đã thể hiện qua tháng và tuần |

**Giữ lại nhưng ghi vào hạn chế (Mục 5.3 của báo cáo):** `total_of_special_requests`, `adults`, `children`, `babies`, `stays_*`, `meal`, `reserved_room_type`, `adr`. Giá trị trong dữ liệu là trạng thái ngày trước ngày đến, nên các cột này có thể đã bị sửa sau lúc đặt.

### 3.2. Bộ cột thông thường: 29 cột, chỉ dùng cho TN1 [xác nhận: TV1]

Gồm 22 cột sạch và 7 cột: `arrival_date_year`, `assigned_room_type`, `booking_changes`, `days_in_waiting_list`, `deposit_type`, `country`, `required_car_parking_spaces`.

Bộ này **bỏ cả `reservation_status` và `reservation_status_date`**, trong khi kế hoạch ban đầu chỉ bỏ `reservation_status`. Lý do:

- `docs/function_contracts.md` đã quy định không dùng hai cột này làm feature.
- `reservation_status_date` là cột ngày nên bắt buộc phải chọn cách mã hóa, và kết quả phụ thuộc gần như hoàn toàn vào cách đó. Nếu mã hóa thành "số ngày so với ngày đến" thì cột gần như lộ nhãn, khi đó TN1 chỉ chứng minh một điều hiển nhiên.
- Khi bỏ cột này, TN1 đo được phần rò rỉ khó nhận ra hơn (7 cột ở trên) cộng với ảnh hưởng của cách chia ngẫu nhiên. Kết quả này có giá trị hơn cho báo cáo.

### 3.3. Đặc trưng tạo thêm (T08, TV2)

- Chỉ tạo đặc trưng từ các cột có trong bộ tương ứng.
- **Đã chốt (T08): chỉ thêm `arrival_weekday`** (thứ trong tuần của ngày đến, biến phân loại) cho cả bộ sạch và bộ thông thường. Bộ sạch dùng cho mô hình gồm 22 cột gốc và `arrival_weekday`.
- Các ứng viên còn lại (`prev_cancel_ratio`, `has_history`, `has_agent`, `has_company`, `country_group`, ...) không thêm. Bằng chứng ở `notebooks/02_features.ipynb` (chỉ dùng tập train).

### 3.4. Mã hóa (T07, TV1)

- **Biến phân loại:** `hotel`, `arrival_date_month`, `meal`, `market_segment`, `distribution_channel`, `reserved_room_type`, `customer_type`, `agent`, `company`; bộ thông thường có thêm `assigned_room_type`, `deposit_type`, `country`.
  - Mã hóa bằng `OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=...)`. TV1 chọn giá trị `min_frequency` dựa trên train.
  - Gom mức hiếm là bắt buộc với `agent` (333 mã), `company` (352 mã) và `country` (177 mã).
- **Biến số:**
  - Logistic Regression: chuẩn hóa; gợi ý thêm `log1p` cho `lead_time` và `adr` (EDA Mục 10).
  - RF/GBM: không cần chuẩn hóa (`scale_numeric=False`).
- **Kiểm tra khi tách X:** code tách X phải có `assert` để chặn các cột cấm lọt vào: `is_canceled`, `reservation_status`, `reservation_status_date`, `arrival_date`. Với bộ sạch, chặn thêm 7 cột ở Mục 3.2.

## 4. Chia dữ liệu

### 4.1. Chia theo thời gian (thiết lập chính) [xác nhận: TV3, theo đề xuất T05]

- Cột ngày: `arrival_date`.
- Quy ước biên:
  - train: `arrival_date < 2017-01-01`;
  - validation: `2017-01-01 <= arrival_date < 2017-07-01`;
  - test: `arrival_date >= 2017-07-01`.

| Tập | Ngày đến | Số dòng | Tỉ lệ | Tỉ lệ hủy | City (tỉ lệ hủy) | Resort (tỉ lệ hủy) |
|---|---|---:|---:|---:|---:|---:|
| Train | 01/07/2015–31/12/2016 | 78.586 | 65,9% | 36,2% | 51.714 (41,4%) | 26.872 (26,3%) |
| Validation | 01/01–30/06/2017 | 30.386 | 25,5% | 39,3% | 20.767 (44,5%) | 9.619 (28,1%) |
| Test | 01/07–31/08/2017 | 10.233 | 8,6% | 37,1% | 6.679 (36,6%) | 3.554 (38,1%) |

- `temporal_split` trả về mỗi tập **đã sắp xếp theo `arrival_date`** (sort ổn định, giữ nguyên index). `time_series_cv` cần dữ liệu đã sắp xếp như vậy, vì file CSV xếp toàn bộ Resort trước rồi mới đến City.
- Phương án trong EDA (validation 01–04/2017, test 05–08/2017) cho tập test dài hơn, nhưng không được chọn. Lý do: validation khi đó lệch mùa so với test, và tỉ lệ hủy của hai tập cách nhau xa hơn (36,5% so với 40,6%, thay vì 39,3% so với 37,1%). Ngưỡng chọn trên validation (TN3) vì vậy khó dùng được trên test.
- **Hạn chế cần ghi trong báo cáo:** tập test chỉ gồm 2 tháng cao điểm hè.

### 4.2. Chia ngẫu nhiên (chỉ dùng cho TN1)

- Gọi `random_split(..., test_size=0.086, valid_size=0.255, stratify=True, random_state=42)`. Hai tỉ lệ này **tính trên toàn bộ dữ liệu**; TV1 ghi rõ điều này trong docstring.
- Với tỉ lệ trên, số dòng mỗi tập gần bằng khi chia theo thời gian.
- Tỉ lệ hủy của tập test ngẫu nhiên xấp xỉ 37,1% (do stratify), bằng tập test theo thời gian. Vì vậy PR-AUC của hai cách chia so sánh trực tiếp được với nhau.

### 4.3. Chia theo khách sạn (TN2)

- Giữ nguyên mốc thời gian: train trên phần train của khách sạn A, rồi đánh giá trên phần test của chính A và phần test của khách sạn B.
- Cách này tách được ảnh hưởng của việc đổi khách sạn khỏi ảnh hưởng của thời gian.
- Dùng bộ cột sạch **nhưng bỏ cột `hotel`**: khi chỉ train trên một khách sạn, cột này là hằng số.
- Siêu tham số giữ nguyên như cấu hình chính.

## 5. Đánh giá

### 5.1. Metric [xác nhận: TV3]

- **Metric chính: PR-AUC và F1 lớp hủy** (giống kế hoạch, `docs/function_contracts.md` và `docs/metric_and_cost.md`).
  - PR-AUC tính bằng `average_precision_score`. Luôn ghi kèm mốc so sánh, bằng tỉ lệ hủy của tập đánh giá.
  - F1 lớp hủy báo cáo ở ngưỡng 0,5 và ở ngưỡng theo chi phí (TN3).
- **Chọn mô hình theo PR-AUC.** Nếu PR-AUC và F1 chọn ra hai mô hình khác nhau thì theo PR-AUC, vì PR-AUC không phụ thuộc ngưỡng.
- **Metric phụ:**
  - ROC-AUC, dùng khi so sánh các tập có tỉ lệ hủy khác nhau.
  - Precision và Recall.
- Không dùng accuracy làm metric chính, vì một mô hình luôn đoán "không hủy" cũng đạt khoảng 63%.

### 5.2. Quy trình

| Việc | Dữ liệu dùng |
|---|---|
| Chọn siêu tham số | `time_series_cv` trên train (5 fold, `scoring="average_precision"`), báo mean ± std |
| So sánh mô hình, chọn ngưỡng (TN3), early stopping (nếu có) | Validation |
| Đánh giá cuối | Test, chạy một lần sau khi đóng băng cấu hình (M3) |

- **Không huấn luyện lại trên train + validation** trước khi chạy test. Ngưỡng chọn trên validation là ngưỡng của mô hình học trên train; nếu học lại thì phân phối xác suất thay đổi và ngưỡng đó không còn đúng.
- **TN1:** dùng cùng một bộ siêu tham số (của cấu hình chính: bộ sạch, chia theo thời gian) cho cả 4 ô. Như vậy chỉ còn hai yếu tố thay đổi là bộ cột và cách chia.
- Mọi kết quả trên test (kể cả TN1, TN2) chỉ chạy sau khi đã chốt cấu hình. Không quay lại chỉnh mô hình sau khi xem kết quả test.
- Seed: `RANDOM_STATE = 42` lấy từ `src.config`.

### 5.3. Chi phí cho TN3 [xác nhận: TV3]

- Công thức và 3 kịch bản giữ nguyên như trong `docs/metric_and_cost.md`.
- **Kịch bản chính: C_FN = 1, C_FP = 2** ("Thận trọng overbooking"). Hai kịch bản còn lại dùng để phân tích độ nhạy.
- Lý do:
  - Dự đoán nhầm một booking "sẽ hủy" có thể dẫn đến nhận quá số phòng: khách đến mà không còn phòng. Trường hợp này thường được coi là tệ hơn một phòng bị trống. Đây là giả định, không phải số liệu tài chính.
  - Nếu xác suất dự đoán được hiệu chỉnh tốt, ngưỡng tối ưu theo lý thuyết là C_FP / (C_FN + C_FP):

    | Kịch bản (C_FN : C_FP) | Ngưỡng lý thuyết |
    |---|---:|
    | 1 : 1 | 0,5 |
    | 2 : 1 | 0,33 |
    | 1 : 2 | 0,67 |

  - Kịch bản 1 : 1 gần như trùng với ngưỡng mặc định, nên không dùng làm kịch bản chính.
  - TN3 có thể so ngưỡng tìm được trên validation với ngưỡng lý thuyết.
- Quét ngưỡng từ 0,01 đến 0,99, bước 0,01, trên tập validation.

## 6. Schema `reports/results/results.csv` [xác nhận: TV3]

```python
RESULT_COLUMNS = [
    "model_name", "experiment", "feature_set", "split",
    "train_hotel", "eval_hotel", "eval_set", "n_eval", "eval_cancel_rate",
    "average_precision", "average_precision_std", "f1", "roc_auc", "precision", "recall",
    "threshold", "cost_scenario", "C_FN", "C_FP", "TN", "FP", "FN", "TP",
    "expected_cost", "cost_per_booking", "params",
]
```

| Cột mới | Giá trị |
|---|---|
| `experiment` | `main`, `TN1`, `TN2`, `TN3` |
| `feature_set` | `clean`, `conventional` |
| `train_hotel`, `eval_hotel` | `all`, `City Hotel`, `Resort Hotel` |
| `eval_set` | `cv`, `validation`, `test` |
| `n_eval`, `eval_cancel_rate` | Số dòng và tỉ lệ hủy của tập đánh giá (= mốc của PR-AUC) |
| `average_precision_std` | Độ lệch chuẩn qua các fold, chỉ có ở dòng `cv`. Ở dòng này, `average_precision` là giá trị trung bình |
| `TN`, `TP` | Thêm cạnh `FN`, `FP` để dựng lại confusion matrix |
| `params` | Siêu tham số, lưu dạng chuỗi JSON |

- `split` giữ nguyên hai giá trị như T06: `temporal`, `random_baseline`.
- `evaluate_classification` cần trả về key đúng với tên cột: `TN`, `FP`, `FN`, `TP` (chữ hoa). Hiện hàm trả về chữ thường, nên `append_result` báo lỗi khi nhận kết quả của nó.
- Khi hai nhánh cùng thêm dòng vào `results.csv`, merge sẽ bị xung đột. Cách xử lý: giữ dòng của cả hai phía.

## 7. Các quyết định khác

- **Gradient Boosting:** dùng LightGBM, ghi rõ version khi thêm vào `requirements.txt` [xác nhận: TV3].
- **Thư mục kết quả:** `reports/figures/` vẫn ignore, vì hình có thể tạo lại bằng cách chạy notebook. `reports/results/results.csv` được track (đã làm ở T06).
- **Thay đổi contract**, cập nhật `docs/function_contracts.md` cùng lúc:
  - thêm `clean_data` (Mục 2);
  - `temporal_split` trả về dữ liệu đã sắp xếp theo ngày;
  - `test_size` và `valid_size` của `random_split` tính trên toàn bộ dữ liệu;
  - `evaluate_classification` trả về `TN`, `FP`, `FN`, `TP`.
