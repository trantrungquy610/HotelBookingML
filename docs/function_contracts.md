# Function contracts – thống nhất T01

Mục tiêu: T06 (TV3), T07 (TV1), T08 (TV2) có thể code song song. Các chữ ký dưới đây là giao diện ban đầu; logic bên trong có thể hoàn thiện sau M1, nhưng không tự ý đổi tên/thứ tự tham số/kiểu trả về.

## T01 – dữ liệu
```python
load_raw(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame
```
Đọc CSV nguyên bản, không biến đổi.

## T06 – `src/evaluate.py` (TV3)
```python
evaluate_classification(y_true, y_pred, y_score=None) -> dict[str, float]
time_series_cv(estimator, X, y, *, n_splits=5, scoring="average_precision")
append_result(result: dict, path="reports/results/results.csv") -> None
```
Metric chính: PR-AUC (`average_precision`) và F1 lớp hủy. Metric phụ: ROC-AUC, precision, recall. Quy ước lớp dương là `is_canceled=1`. Cần thống nhất schema `results.csv` trước khi ghi kết quả.

## T07 – `src/preprocess.py` (TV1)
```python
build_preprocessor(
    X,
    *,
    numeric_features=None,
    categorical_features=None,
    scale_numeric=True,
) -> ColumnTransformer

build_model_pipeline(
    X,
    estimator,
    *,
    numeric_features=None,
    categorical_features=None,
    scale_numeric=True,
) -> sklearn.pipeline.Pipeline
```
Preprocessor được fit bên trong Pipeline trên train fold, không fit trước trên toàn bộ dữ liệu.

## T07 – `src/split.py` (TV1)
```python
temporal_split(df, *, train_end, valid_end, date_col)
    -> (train_df, valid_df, test_df)

random_split(
    df, *, target_col="is_canceled", test_size=0.2,
    valid_size=0.2, random_state=42, stratify=True
) -> (train_df, valid_df, test_df)

hotel_split(
    df, *, hotel_col="hotel", train_hotel, test_hotel
) -> (train_df, test_df)
```
Các mốc thời gian, tỷ lệ và cột ngày thực tế sẽ theo quyết định M1. Các hàm trả về DataFrame còn target để caller tách X/y.

## T08 – `src/features.py` (TV2)
```python
add_features(df, *, copy=True) -> pd.DataFrame
```
Giữ index, không mutate input khi `copy=True`. Chỉ thêm feature có lý do từ EDA; không dùng thông tin phát sinh sau thời điểm booking.

## Quy ước chung
- `RANDOM_STATE = 42` lấy từ `src.config`, không khai báo seed riêng.
- Target: `is_canceled`; positive class: `1`.
- Các module không tự đọc file CSV; dùng `load_raw()`.
- Không dùng `reservation_status` hoặc `reservation_status_date` làm feature đầu vào. Nhóm xác nhận danh sách leakage cuối cùng tại M1.
- Chỉ thay đổi contract khi cả nhóm đồng ý và cập nhật file này.
