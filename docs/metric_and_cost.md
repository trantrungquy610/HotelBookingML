# Metric và giả định chi phí

## 1. Bài toán ra quyết định

Mục tiêu là dự đoán `is_canceled = 1`, trong đó lớp dương luôn là booking bị
hủy. Mô hình không chỉ được so sánh bằng accuracy: tỷ lệ hủy có thể mất cân
bằng và quyết định vận hành phụ thuộc vào ngưỡng xác suất.

Hai loại sai lầm được quy ước:

| Kết quả | Ý nghĩa vận hành | Sai lầm |
|---|---|---|
| Dự đoán không hủy, thực tế hủy | Có thể còn phòng không bán được | False negative (FN) |
| Dự đoán hủy, thực tế không hủy | Có thể nhận quá số phòng hoặc thiếu phòng | False positive (FP) |

Chi phí thực tế chưa có trong dữ liệu, nên báo cáo dùng chi phí chuẩn hóa và
ghi rõ đây là giả định, không phải giá trị tài chính đã xác minh.

## 2. Bộ metric bắt buộc

### Metric chính

- **PR-AUC / Average Precision**: đo chất lượng xếp hạng lớp hủy trong bối
  cảnh mất cân bằng; không phụ thuộc một threshold duy nhất.
- **F1 lớp hủy**: báo cáo ở threshold mặc định 0.5 và ở threshold chọn theo
  chi phí trên validation; cân bằng precision và recall khi chưa có chi phí
  đáng tin cậy.

Khi PR-AUC và F1 chọn ra hai mô hình khác nhau, chọn theo PR-AUC vì metric này
không phụ thuộc threshold.

### Metric phụ

- **Precision**: trong các booking bị gắn cờ hủy, tỷ lệ thực sự hủy; thấp
  nghĩa là nhiều cảnh báo có thể dẫn tới quyết định overbooking sai.
- **Recall**: trong các booking thực sự hủy, tỷ lệ phát hiện được; thấp nghĩa
  là bỏ sót nhiều cơ hội lấp phòng.
- **ROC-AUC**: dùng để so sánh khả năng phân biệt tổng quát, nhưng không dùng
  làm metric duy nhất khi lớp hủy mất cân bằng.

`src.evaluate.evaluate_classification` phải trả về ít nhất:
`average_precision`, `f1`, `roc_auc`, `precision`, `recall` và số đếm `TN`,
`FP`, `FN`, `TP` (cùng tên cột với `results.csv`). Khi `y_score` không
có, PR-AUC và ROC-AUC phải được báo là không tính được theo contract thay vì
thay bằng giá trị giả.

## 3. Mô hình chi phí chuẩn hóa

Đặt:

```text
expected_cost = C_FN * FN + C_FP * FP
```

Trong đó `C_FN` là chi phí một booking bị hủy nhưng không được phát hiện
(phòng trống), còn `C_FP` là chi phí một booking bị gắn cờ hủy nhưng thực tế
không hủy (rủi ro nhận quá số phòng). Có thể chia cho số booking để báo cáo
`cost_per_booking`.

Ba kịch bản sensitivity đề xuất:

| Kịch bản | `C_FN` | `C_FP` | Diễn giải |
|---|---:|---:|---|
| Cân bằng | 1 | 1 | Chưa biết chi phí nào lớn hơn |
| Ưu tiên lấp phòng | 2 | 1 | Phòng trống đắt hơn rủi ro overbooking |
| Thận trọng overbooking | 1 | 2 | Overbooking đắt hơn phòng trống |

Kịch bản chính (chốt tại M1): **Thận trọng overbooking** (`C_FN = 1`,
`C_FP = 2`). Hai kịch bản còn lại dùng cho sensitivity analysis. Không đổi
kịch bản chính sau khi xem test.

## 4. Chọn threshold đúng quy trình

1. Huấn luyện trên train.
2. Tính xác suất lớp hủy trên validation.
3. Quét các threshold ứng viên và chọn threshold làm nhỏ nhất
   `expected_cost` theo kịch bản đã chọn; nếu hòa, ưu tiên threshold có
   precision cao hơn để hạn chế overbooking.
4. Khóa threshold, sau đó đánh giá một lần trên test.
5. Báo cáo metric ở threshold mặc định 0.5 và threshold chi phí để tránh
   nhầm chất lượng mô hình với chính sách vận hành.

PR-AUC/ROC-AUC phải dùng score liên tục; F1, precision, recall và cost dùng
nhãn sau threshold. Threshold không được tối ưu trên test.

## 5. Cách báo cáo kết quả

Mỗi dòng kết quả theo `RESULT_COLUMNS` trong `src/evaluate.py` (chốt tại M1,
`docs/decisions.md` Mục 6):

- **Định danh:** `model_name`, `experiment` (`main`, `TN1`, `TN2`, `TN3`),
  `feature_set` (`clean`, `conventional`), `split` (`temporal` hoặc
  `random_baseline`), `params` (hyperparameter dạng JSON).
- **Tập đánh giá:** `train_hotel`, `eval_hotel` (`all`, `City Hotel`,
  `Resort Hotel`), `eval_set` (`cv`, `validation`, `test`), `n_eval`,
  `eval_cancel_rate` (tỷ lệ hủy của tập đánh giá, cũng là mốc của PR-AUC).
- **Metric:** `average_precision` (với dòng `cv` là trung bình qua các fold),
  `average_precision_std`, `f1`, `roc_auc`, `precision`, `recall`.
- **Threshold và chi phí:** `threshold`, `cost_scenario`, `C_FN`, `C_FP`,
  `TN`, `FP`, `FN`, `TP`, `expected_cost`, `cost_per_booking`.

Kết luận chính dựa trên temporal test. Random baseline chỉ dùng làm mốc tham
chiếu; nếu random tốt hơn nhiều temporal, cần nêu khả năng drift hoặc leakage
thay vì chọn random vì metric cao hơn.

## 6. Giới hạn và giả định cần xác nhận

- Chi phí 1/2 là đơn vị tương đối, chưa đại diện cho doanh thu/phạt thực tế.
- Một booking có thể có nhiều phòng, nhưng dữ liệu hiện tại không cung cấp
  đầy đủ giá trị phòng và chi phí overbooking; chưa nên diễn giải
  `expected_cost` thành tiền.
- Cần xác nhận với nghiệp vụ liệu false positive có thực sự dẫn tới
  overbooking hay chỉ là một cảnh báo để nhân viên xem xét.
- Khi có chi phí tiền thật, thay bảng kịch bản bằng đơn giá đã được phê duyệt
  và giữ nguyên quy trình chọn threshold trên validation.
