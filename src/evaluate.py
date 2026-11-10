"""Metric và đánh giá dùng chung."""

from pathlib import Path

import pandas as pd
from sklearn.base import clone
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    get_scorer,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import TimeSeriesSplit


RESULT_COLUMNS = [
    "model_name",
    "split",
    "average_precision",
    "f1",
    "roc_auc",
    "precision",
    "recall",
    "threshold",
    "cost_scenario",
    "C_FN",
    "C_FP",
    "FN",
    "FP",
    "expected_cost",
    "cost_per_booking",
]


def evaluate_classification(
    y_true,
    y_pred,
    y_score=None,
) -> dict[str, float]:
    """Trả về PR-AUC, F1, ROC-AUC, precision và recall.

    y_score là xác suất/điểm của lớp dương; cần có để tính PR-AUC và ROC-AUC.
    """
    if y_score is None:
        raise ValueError(
            "y_score là bắt buộc để tính average_precision và roc_auc."
        )

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "average_precision": float(average_precision_score(y_true, y_score)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_score)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "tn": float(tn),
        "fp": float(fp),
        "fn": float(fn),
        "tp": float(tp),
    }


def time_series_cv(
    estimator,
    X: pd.DataFrame,
    y,
    *,
    n_splits: int = 5,
    scoring: str = "average_precision",
) -> pd.DataFrame:
    """Đánh giá estimator bằng các fold tăng dần theo thứ tự thời gian.

    X và y phải được sắp xếp theo thời gian từ trước. Mỗi fold fit một bản sao
    estimator chỉ trên phần train của fold, sau đó chấm trên phần validation.
    """
    splitter = TimeSeriesSplit(n_splits=n_splits)
    scorer = get_scorer(scoring)
    y_series = y if hasattr(y, "iloc") else pd.Series(y)
    rows = []

    for fold, (train_index, valid_index) in enumerate(splitter.split(X), start=1):
        fold_estimator = clone(estimator)
        X_train = X.iloc[train_index]
        X_valid = X.iloc[valid_index]
        y_train = y_series.iloc[train_index]
        y_valid = y_series.iloc[valid_index]

        fold_estimator.fit(X_train, y_train)
        rows.append(
            {
                "fold": fold,
                "train_size": len(train_index),
                "validation_size": len(valid_index),
                "score": float(scorer(fold_estimator, X_valid, y_valid)),
                "scoring": scoring,
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "fold",
            "train_size",
            "validation_size",
            "score",
            "scoring",
        ],
    )


def append_result(
    result: dict,
    path: str = "reports/results/results.csv",
) -> None:
    """Ghi một dòng kết quả theo schema thống nhất của dự án.

    Các cột chưa có trong ``result`` được ghi là NA để mọi dòng có cùng schema.
    Cột ngoài schema bị từ chối để tránh ghi nhầm tên metric.
    """
    unexpected = set(result) - set(RESULT_COLUMNS)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ValueError(f"Result chứa cột không hợp lệ: {names}")

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    row = {column: result.get(column, pd.NA) for column in RESULT_COLUMNS}
    row_frame = pd.DataFrame([row], columns=RESULT_COLUMNS)

    if output.exists():
        existing_columns = pd.read_csv(output, nrows=0).columns.tolist()
        if existing_columns != RESULT_COLUMNS:
            raise ValueError(
                f"Schema của {output} không khớp RESULT_COLUMNS: "
                f"{existing_columns}"
            )
        row_frame.to_csv(output, mode="a", header=False, index=False)
    else:
        row_frame.to_csv(output, index=False)
