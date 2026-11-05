# Feature Decisions – Rà soát Data Leakage

## 1. Mục tiêu

Tài liệu này ghi nhận việc rà soát từng cột trong bộ dữ liệu **Hotel Booking Demand** nhằm phát hiện và xử lý hiện tượng *data leakage* (rò rỉ dữ liệu).

Bài toán của nhóm là dự đoán một lượt đặt phòng khách sạn có bị hủy hay không.

- **Target:** `is_canceled`
- **Thời điểm dự đoán giả định:** tại thời điểm khách tạo booking.
- **Nguyên tắc:** Chỉ sử dụng những thông tin có thể biết được tại thời điểm dự đoán. Không sử dụng thông tin được tạo ra hoặc cập nhật sau khi việc hủy phòng đã xảy ra.

Việc rà soát dựa trên ý nghĩa của từng biến và thời điểm thông tin có thể được ghi nhận. Một cột có tương quan cao với target không tự động đồng nghĩa với leakage; cần xem xét liệu thông tin đó có sẵn tại thời điểm dự đoán hay không.

## 2. Data leakage là gì?

Data leakage xảy ra khi mô hình được sử dụng thông tin mà trên thực tế không thể biết tại thời điểm dự đoán. Điều này có thể khiến kết quả đánh giá trên tập kiểm tra cao bất thường, nhưng hiệu quả khi triển khai thực tế lại thấp.

Trong bài toán này, có hai dạng cần chú ý:

- **Target leakage:** Feature chứa trực tiếp hoặc gián tiếp kết quả cần dự đoán. Ví dụ: trạng thái đặt phòng sau khi khách đã hủy.
- **Temporal leakage:** Feature chứa thông tin chỉ được ghi nhận sau thời điểm tạo booking. Ví dụ: ngày cập nhật trạng thái hủy hoặc số lần thay đổi booking được ghi nhận trong quá trình xử lý đặt phòng.

## 3. Nguyên tắc phân loại feature

Mỗi cột được phân loại theo một trong ba quyết định:

| Quyết định | Ý nghĩa |
|---|---|
| KEEP | Có thể sử dụng nếu giá trị phản ánh thông tin có sẵn tại thời điểm tạo booking. |
| DROP | Loại khỏi tập feature vì chứa thông tin kết quả hoặc thông tin phát sinh sau thời điểm dự đoán. |
| REVIEW | Chưa đủ căn cứ xác nhận thời điểm ghi nhận. Tạm thời không đưa vào bộ feature clean cho đến khi kiểm tra được nguồn gốc và thời điểm cập nhật. |

**Lưu ý:** Việc phân loại KEEP không có nghĩa là đã xác minh được lịch sử cập nhật của từng bản ghi. Nếu dataset chỉ cung cấp giá trị cuối cùng mà không có snapshot tại thời điểm tạo booking, nhóm cần ghi nhận giới hạn này trong báo cáo.

## 4. Bảng quyết định cho từng cột

| STT | Cột | Quyết định | Giải thích |
|---:|---|---|---|
| 1 | `hotel` | KEEP | Loại khách sạn (Resort Hotel hoặc City Hotel), có thể biết khi tạo booking. |
| 2 | `is_canceled` | DROP – TARGET | Đây là biến mục tiêu cần dự đoán, tuyệt đối không được đưa vào X. |
| 3 | `lead_time` | KEEP | Số ngày từ ngày đặt phòng đến ngày đến dự kiến. Có thể xác định tại thời điểm booking được tạo. |
| 4 | `arrival_date_year` | KEEP | Năm đến dự kiến, là thông tin của kế hoạch đặt phòng. |
| 5 | `arrival_date_month` | KEEP | Tháng đến dự kiến. Cần lưu ý giá trị có thể thay đổi nếu khách đổi ngày đến. |
| 6 | `arrival_date_week_number` | KEEP | Tuần trong năm của ngày đến dự kiến. Có thể được xác định từ ngày đến ban đầu. |
| 7 | `arrival_date_day_of_month` | KEEP | Ngày trong tháng của ngày đến dự kiến. Có thể được xác định từ ngày đến ban đầu. |
| 8 | `stays_in_weekend_nights` | REVIEW | Số đêm cuối tuần dự kiến có thể thay đổi khi khách chỉnh sửa thời gian lưu trú. |
| 9 | `stays_in_week_nights` | REVIEW | Số đêm ngày thường dự kiến có thể thay đổi khi khách chỉnh sửa booking. |
| 10 | `adults` | REVIEW | Số người lớn có thể thay đổi sau khi booking được tạo. |
| 11 | `children` | REVIEW | Số trẻ em có thể thay đổi sau khi booking được tạo. |
| 12 | `babies` | REVIEW | Số trẻ sơ sinh có thể thay đổi sau khi booking được tạo. |
| 13 | `meal` | REVIEW | Loại bữa ăn có thể được cập nhật trong quá trình thay đổi booking. |
| 14 | `country` | REVIEW | Quốc gia của khách có thể chưa được xác định chính xác tại thời điểm đặt phòng; tài liệu nghiên cứu gốc lưu ý thông tin quốc tịch có thể chỉ chính xác khi khách check-in. |
| 15 | `market_segment` | REVIEW | Phân khúc thị trường có thể là thông tin ban đầu của booking, nhưng cần xác minh thời điểm ghi nhận và cập nhật. |
| 16 | `distribution_channel` | REVIEW | Kênh phân phối có thể được biết khi đặt phòng, nhưng cần xác minh giá trị trong dataset có bị cập nhật về sau hay không. |
| 17 | `is_repeated_guest` | KEEP | Cho biết khách đã từng lưu trú trước đó hay chưa. Có thể xác định từ lịch sử trước booking hiện tại. |
| 18 | `previous_cancellations` | KEEP | Số booking trước đây của khách đã bị hủy. Chỉ sử dụng thông tin lịch sử có trước booking hiện tại. |
| 19 | `previous_bookings_not_canceled` | KEEP | Số booking trước đây của khách không bị hủy. Chỉ sử dụng thông tin lịch sử có trước booking hiện tại. |
| 20 | `reserved_room_type` | REVIEW | Loại phòng khách đặt ban đầu có thể dùng được, nhưng cần xác minh đây là loại phòng tại thời điểm tạo booking hay giá trị cuối cùng. |
| 21 | `assigned_room_type` | DROP | Loại phòng thực tế được phân cho khách. Có thể khác loại phòng đặt ban đầu và được xác định trong quá trình xử lý booking hoặc check-in. |
| 22 | `booking_changes` | DROP | Số lần thay đổi booking từ khi tạo đến khi check-in hoặc hủy. Đây là thông tin phát sinh sau thời điểm tạo booking. |
| 23 | `deposit_type` | REVIEW | Loại hình đặt cọc có thể được xác định khi booking được tạo, nhưng cần xác minh có thay đổi trong quá trình xử lý hay không. |
| 24 | `agent` | REVIEW | Mã đại lý đặt phòng. Cần xác minh giá trị có sẵn tại thời điểm tạo booking hay được bổ sung/cập nhật về sau. |
| 25 | `company` | REVIEW | Mã công ty/tổ chức liên quan đến booking. Cần xác minh thời điểm ghi nhận. |
| 26 | `days_in_waiting_list` | DROP | Số ngày booking nằm trong danh sách chờ trước khi được xác nhận. Đây là thông tin chỉ có thể biết sau một khoảng thời gian chờ. |
| 27 | `customer_type` | REVIEW | Loại khách hàng có thể được xác định ban đầu hoặc cập nhật trong quá trình xử lý. Cần xác minh snapshot tại thời điểm tạo booking. |
| 28 | `adr` | REVIEW | Giá trung bình mỗi đêm có thể thay đổi theo số người, thời gian lưu trú hoặc các điều chỉnh của booking. Cần xác minh giá trị có phải giá tại thời điểm đặt phòng hay không. |
| 29 | `required_car_parking_spaces` | REVIEW | Số chỗ đỗ xe yêu cầu có thể thay đổi trong quá trình cập nhật booking. |
| 30 | `total_of_special_requests` | REVIEW | Tổng số yêu cầu đặc biệt có thể tăng hoặc thay đổi sau khi booking được tạo. |
| 31 | `reservation_status` | DROP | Trạng thái đặt phòng như Canceled, Check-Out hoặc No-Show trực tiếp phản ánh kết quả của booking, có thể tiết lộ target. |
| 32 | `reservation_status_date` | DROP | Ngày cập nhật trạng thái đặt phòng. Có thể cho biết thời điểm booking bị hủy hoặc hoàn tất lưu trú, nên không phù hợp với dự đoán tại thời điểm tạo booking. |

## 5. Các cột có nguy cơ leakage cao

Những cột sau được xác định là cần loại khỏi tập feature vì có nguy cơ leakage rõ ràng:

### 5.1. `reservation_status`

Cột này thể hiện trạng thái cuối cùng của booking:

- `Canceled`: Booking đã bị hủy.
- `Check-Out`: Khách đã hoàn tất lưu trú.
- `No-Show`: Khách không đến.

Vì `is_canceled` là biến cần dự đoán, sử dụng `reservation_status` sẽ khiến mô hình gần như biết trước kết quả. Đây là trường hợp target leakage điển hình.

**Quyết định: DROP.**

### 5.2. `reservation_status_date`

Đây là ngày cập nhật trạng thái đặt phòng cuối cùng. Nếu booking bị hủy, ngày này có thể phản ánh thời điểm hủy.

Thông tin này không có sẵn tại thời điểm tạo booking và có thể giúp mô hình suy ra kết quả cần dự đoán.

**Quyết định: DROP.**

### 5.3. `booking_changes`

Cột này ghi nhận số lần thay đổi booking kể từ khi tạo đến khi check-in hoặc hủy.

Tại thời điểm khách vừa tạo booking, số lần thay đổi trong tương lai chưa thể biết được. Sử dụng giá trị cuối cùng sẽ làm mô hình tiếp cận thông tin tương lai.

**Quyết định: DROP.**

### 5.4. `assigned_room_type`

Cột này thể hiện loại phòng được phân thực tế cho khách. Giá trị có thể khác với loại phòng khách đã đặt ban đầu.

Do việc phân phòng có thể diễn ra sau khi booking được tạo, cột này không được xem là thông tin an toàn cho bài toán dự đoán tại thời điểm tạo booking.

**Quyết định: DROP.**

### 5.5. `days_in_waiting_list`

Cột này thể hiện số ngày booking phải chờ trước khi được xác nhận. Giá trị chỉ được hình thành sau một khoảng thời gian chờ.

Nếu mục tiêu là dự đoán ngay khi khách gửi yêu cầu đặt phòng, đây là thông tin chưa thể biết.

**Quyết định: DROP.**

## 6. Hai bộ feature phục vụ thực nghiệm TN1

Để đánh giá ảnh hưởng của leakage, nhóm sử dụng hai bộ feature.

### 6.1. Bộ feature thông thường (Baseline)

Theo kế hoạch thực nghiệm của nhóm, bộ baseline chỉ loại `reservation_status` khỏi các cột đầu vào. Biến target `is_canceled` luôn được tách riêng và không được đưa vào X.

Bộ này được dùng làm mốc so sánh, không được xem là bộ feature đã sạch leakage. Đặc biệt, `reservation_status_date` và các cột có thông tin phát sinh sau thời điểm tạo booking vẫn có thể khiến kết quả bị lạc quan.

### 6.2. Bộ feature clean

Bộ clean loại bỏ các cột được xác định có nguy cơ leakage rõ ràng và tạm thời loại cả những cột chưa xác minh được thời điểm ghi nhận.

**Các cột KEEP được đề xuất ban đầu:**

```python
CLEAN_FEATURES = [
    "hotel",
    "lead_time",
    "arrival_date_year",
    "arrival_date_month",
    "arrival_date_week_number",
    "arrival_date_day_of_month",
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
]
```

Đây là bộ feature clean theo hướng thận trọng, dựa trên ý nghĩa của biến và giả định rằng các giá trị phản ánh thông tin có trước hoặc tại thời điểm tạo booking.

Các cột REVIEW chưa được đưa vào bộ clean cho đến khi nhóm xác minh được thời điểm ghi nhận. Nếu có bằng chứng rằng một cột REVIEW đã có sẵn tại thời điểm tạo booking, nhóm có thể cân nhắc bổ sung và ghi rõ lý do.

## 7. Kiểm tra dữ liệu bằng Python

Có thể sử dụng các đoạn code sau để kiểm tra dataset và minh họa một số dấu hiệu leakage.

### 7.1. Kiểm tra dữ liệu và danh sách cột

```python
from src.data import load_raw

df = load_raw()

print("Shape:", df.shape)
print("Columns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isna().sum().sort_values(ascending=False))
```

### 7.2. Kiểm tra phân phối target

```python
print(df["is_canceled"].value_counts())
print(df["is_canceled"].value_counts(normalize=True))
```

### 7.3. Kiểm tra mối quan hệ giữa reservation_status và target

```python
import pandas as pd

print(
    pd.crosstab(
        df["reservation_status"],
        df["is_canceled"],
        margins=True
    )
)
```

Bảng chéo này giúp quan sát mức độ liên hệ giữa trạng thái booking và kết quả hủy phòng. Nếu trạng thái `Canceled` gần như xác định trực tiếp target, đây là bằng chứng thực nghiệm hỗ trợ quyết định loại `reservation_status`.

Lưu ý: Kiểm tra thống kê chỉ hỗ trợ nhận diện dấu hiệu leakage. Quyết định cuối cùng vẫn phải dựa trên ý nghĩa và thời điểm có được thông tin.

### 7.4. Tạo X và y cho bộ clean

```python
TARGET = "is_canceled"

CLEAN_FEATURES = [
    "hotel",
    "lead_time",
    "arrival_date_year",
    "arrival_date_month",
    "arrival_date_week_number",
    "arrival_date_day_of_month",
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
]

X_clean = df[CLEAN_FEATURES].copy()
y = df[TARGET].copy()

assert TARGET not in X_clean.columns
assert "reservation_status" not in X_clean.columns
assert "reservation_status_date" not in X_clean.columns
assert "assigned_room_type" not in X_clean.columns
assert "booking_changes" not in X_clean.columns

print("X_clean shape:", X_clean.shape)
print("y shape:", y.shape)
```

## 8. Giới hạn và lưu ý khi diễn giải kết quả

Tài liệu nghiên cứu gốc về Hotel Booking Demand mô tả dữ liệu được trích xuất từ hệ thống quản lý khách sạn và booking log. Nghiên cứu cũng lưu ý rằng một số thuộc tính booking, chẳng hạn số người, thời gian lưu trú và lựa chọn phòng, có thể thay đổi trong quá trình xử lý booking hoặc khi check-in.

Vì vậy, cần phân biệt:

1. Một biến có ý nghĩa hợp lý để dùng tại thời điểm tạo booking.
2. Giá trị thực tế của biến trong dataset có chắc chắn là giá trị tại thời điểm tạo booking hay không.

Dataset dạng bảng hiện tại không cung cấp đầy đủ lịch sử thay đổi theo thời gian cho từng cột. Do đó, nhóm chưa thể khẳng định tất cả các cột KEEP đều đã được xác minh tuyệt đối là không có temporal leakage.

Bộ clean trong tài liệu này là lựa chọn thận trọng dựa trên thông tin hiện có, không thay thế được việc kiểm tra snapshot tại thời điểm tạo booking.

## 9. Kết luận

Qua rà soát 32 cột của Hotel Booking Demand, nhóm xác định:

- `is_canceled` là biến mục tiêu, không được đưa vào tập feature.
- `reservation_status` là biến có nguy cơ target leakage rõ ràng.
- `reservation_status_date`, `booking_changes`, `assigned_room_type` và `days_in_waiting_list` có nguy cơ temporal leakage và cần loại bỏ.
- Một số cột khác có thể thay đổi sau khi booking được tạo nên được đánh dấu REVIEW.
- Hai bộ feature baseline và clean sẽ được sử dụng để so sánh ảnh hưởng của việc xử lý leakage trong thực nghiệm TN1.

**Kết quả mong đợi:** Bộ clean có thể cho metric thấp hơn baseline, nhưng phản ánh sát hơn khả năng dự đoán trong bối cảnh thực tế tại thời điểm tạo booking.

## 10. Tài liệu tham khảo

Antonio, N., de Almeida, A., & Nunes, L. (2019). *Hotel booking demand datasets*. Data in Brief, 22, 41–49.

DOI: https://doi.org/10.1016/j.dib.2018.11.126
