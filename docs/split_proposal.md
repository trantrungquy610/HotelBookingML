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
- Chỉ dùng `validation` để chọn mô hình, feature, threshold và hyperparameter.
- Chỉ đánh giá `test` một lần sau khi đã khóa quy trình.
- Preprocessor phải được fit bên trong pipeline trên từng train fold.
- Không dùng `reservation_status`, `reservation_status_date` hoặc thông tin
  phát sinh sau thời điểm booking làm feature.
- Kiểm tra tỷ lệ `is_canceled` và số dòng ở cả ba tập; nếu một tập thiếu một
  lớp thì phải ghi nhận rõ trong báo cáo, không tự động gộp tập.

## 2. Phương án được chọn: temporal chính + random baseline

### 2.1. Temporal split dùng để kết luận

Đề xuất ban đầu:

| Tập | Khoảng thời gian đến | Vai trò |
|---|---|---|
| Train | 2015–2016 | Fit pipeline và mô hình |
| Validation | 01–06/2017 | Chọn mô hình, tham số và threshold |
| Test | 07–08/2017 | Ước lượng cuối cùng trên giai đoạn tương lai |

Các mốc trên cần được xác nhận bằng min/max và số dòng thực tế sau khi tải
CSV. Nếu dữ liệu thực tế có ngày biên khác, giữ nguyên nguyên tắc theo thứ tự
thời gian và ghi lại mốc thực tế trong kết quả.

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
3. Fit các pipeline trên train; dùng validation để chọn mô hình và threshold.
4. Ghi PR-AUC, F1 lớp hủy, ROC-AUC, precision, recall và expected cost.
5. Khóa lựa chọn, fit lại trên train + validation nếu quy trình cho phép, rồi
   đánh giá đúng một lần trên test.
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
rolling-origin backtest trên các cửa sổ thời gian. Đây là mở rộng sau phương
án B, không thay đổi test temporal cố định dùng để báo cáo cuối cùng.

