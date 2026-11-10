# Đề xuất chia train/validation/test theo thời gian

## 1. Mục tiêu và nguyên tắc

Mục tiêu là ước lượng khả năng dự đoán `is_canceled` cho các booking ở
giai đoạn tương lai, thay vì chỉ đo khả năng ghi nhớ các mẫu ngẫu nhiên trong
toàn bộ dữ liệu. Vì dữ liệu không có ngày tạo booking đáng tin cậy, ngày đến
dự kiến được dùng làm biến thời gian đại diện, ghép từ:

```text
arrival_date_year + arrival_date_month + arrival_date_day_of_month
```

Đây là một xấp xỉ: kết quả phản ánh dự báo cho các giai đoạn đến trong tương
lai, không phải hoàn toàn là dự báo tại đúng ngày booking được tạo.

Các nguyên tắc bắt buộc:

- Sắp xếp theo ngày trước khi chia; không xáo trộn temporal split.
- `train` phải đứng trước `validation`, và `validation` phải đứng trước `test`.
- Chọn hyperparameter bằng `src.evaluate.time_series_cv` trên `train`; chỉ
  dùng `validation` để so sánh mô hình và chọn threshold.
- Chỉ đánh giá `test` một lần sau khi đã khóa quy trình.
- Preprocessor phải được fit bên trong pipeline trên từng train fold.
- Không dùng `reservation_status`, `reservation_status_date` hoặc thông tin
  phát sinh sau thời điểm booking làm feature.
- Kiểm tra tỷ lệ `is_canceled` và số dòng ở cả ba tập; nếu một tập thiếu một
  lớp thì phải ghi nhận rõ trong báo cáo, không tự động gộp tập.

## 2. Phương án được chọn: temporal chính + random baseline

### 2.1. Temporal split dùng để kết luận

Mốc đã chốt tại M1 (số dòng và tỷ lệ hủy của từng tập: `docs/decisions.md`,
Mục 4.1):

| Tập | Khoảng thời gian đến | Vai trò |
|---|---|---|
| Train | 2015–2016 | Fit pipeline và mô hình; chọn hyperparameter bằng `time_series_cv` |
| Validation | 01–06/2017 | So sánh mô hình và chọn threshold |
| Test | 07–08/2017 | Ước lượng cuối cùng trên giai đoạn tương lai |

Đã kiểm tra trên CSV: ngày đến chạy từ 01/07/2015 đến 31/08/2017. Nếu dữ liệu
thay đổi, giữ nguyên nguyên tắc theo thứ tự thời gian và ghi lại mốc thực tế
trong kết quả.

Với `src.split.temporal_split`, caller cần truyền một cột ngày đã ghép và
`train_end`, `valid_end` theo quy ước biên phải nhất quán. Khuyến nghị dùng
`train: date < train_end`, `validation: train_end <= date < valid_end`,
`test: date >= valid_end`; không để dòng có ngày thiếu lọt âm thầm vào một
nhóm.

### 2.2. Random stratified split chỉ làm baseline

Chạy thêm `random_split(..., stratify=True, random_state=42)` để có mốc đối
chiếu. Kết quả random không được dùng thay cho test temporal vì có thể đưa
các booking cùng giai đoạn vào cả train và test, làm metric lạc quan hơn
triển khai thực tế. Chênh lệch lớn giữa random và temporal là tín hiệu cần
kiểm tra leakage, drift hoặc thay đổi phân phối theo thời gian.

## 3. Quy trình thực nghiệm

1. Tạo ngày đến, kiểm tra phạm vi ngày, giá trị thiếu và số dòng theo tháng.
2. Tách temporal train/validation/test trước khi fit preprocessing.
3. Chọn hyperparameter bằng `time_series_cv` trên train (báo mean ± std), fit
   lại mô hình trên toàn bộ train, rồi dùng validation để so sánh mô hình và
   chọn threshold.
4. Ghi PR-AUC, F1 lớp hủy, ROC-AUC, precision, recall và expected cost.
5. Khóa lựa chọn rồi đánh giá đúng một lần trên test bằng mô hình đã fit trên
   train. Không fit lại trên train + validation, vì threshold chọn trên
   validation gắn với mô hình fit trên train.
6. Chạy random baseline độc lập và báo cáo cạnh kết quả temporal, không trộn
   các dòng giữa hai thí nghiệm.

## 4. Kiểm tra tối thiểu cần ghi trong báo cáo

- Mốc thời gian, số dòng và tỷ lệ hủy của từng tập.
- Seed (`RANDOM_STATE = 42`) cho random baseline.
- Danh sách cột bị loại do leakage.
- Mô hình, threshold và chi phí dùng để chọn threshold.
- Metric validation và test; không chọn threshold dựa trên test.

## 5. Hướng mở rộng

Nếu metric dao động mạnh hoặc nhóm cần đánh giá độ ổn định, có thể bổ sung
rolling-origin backtest trên các cửa sổ thời gian. Đây là phần mở rộng, không
thay đổi test temporal cố định dùng để báo cáo cuối cùng.

