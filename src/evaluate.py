"""Metric và đánh giá dùng chung. TV3 triển khai."""

import pandas as pd


def evaluate_classification(
    y_true,
    y_pred,
    y_score=None,
) -> dict[str, float]:
    """Trả về PR-AUC, F1, ROC-AUC, precision và recall.

    y_score là xác suất/điểm của lớp dương; cần có để tính PR-AUC và ROC-AUC.
    """
    raise NotImplementedError("TV3 triển khai theo docs/metric_and_cost.md.")


def time_series_cv(
    estimator,
    X: pd.DataFrame,
    y,
    *,
    n_splits: int = 5,
    scoring: str = "average_precision",
):
    """Đánh giá cross-validation theo thứ tự thời gian."""
    raise NotImplementedError("TV3 triển khai sau khi nhóm chốt M1.")


def append_result(
    result: dict,
    path: str = "reports/results/results.csv",
) -> None:
    """Ghi một dòng kết quả vào CSV theo schema thống nhất."""
    raise NotImplementedError("TV3 triển khai; thống nhất schema trước khi ghi.")
