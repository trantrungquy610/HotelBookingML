"""Mô hình và bộ đặc trưng dùng chung cho các thí nghiệm cuối."""

import json
from pathlib import Path

from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from src.config import (
    CLEAN_CATEGORICAL_FEATURES,
    CONVENTIONAL_CATEGORICAL_FEATURES,
    RANDOM_STATE,
)
from src.features import ENGINEERED_CATEGORICAL_FEATURES
from src.preprocess import build_model_pipeline


CLEAN_NUMERIC_FEATURES = [
    "lead_time",
    "arrival_date_week_number",
    "arrival_date_day_of_month",
    "stays_in_weekend_nights",
    "stays_in_week_nights",
    "adults",
    "children",
    "babies",
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
    "adr",
    "total_of_special_requests",
]
FEATURE_SETS = {
    "clean": (
        CLEAN_NUMERIC_FEATURES,
        [*CLEAN_CATEGORICAL_FEATURES, *ENGINEERED_CATEGORICAL_FEATURES],
    ),
    "conventional": (
        [
            *CLEAN_NUMERIC_FEATURES,
            "arrival_date_year",
            "booking_changes",
            "days_in_waiting_list",
            "required_car_parking_spaces",
        ],
        [
            *CONVENTIONAL_CATEGORICAL_FEATURES,
            *ENGINEERED_CATEGORICAL_FEATURES,
        ],
    ),
}
MODEL_NAMES = (
    "LogisticRegressionTuned",
    "RandomForest",
    "GradientBoosting",
)


def load_best_params(project_root: str | Path) -> dict[str, dict]:
    """Đọc đúng các siêu tham số đã chốt từ T10–T12."""
    root = Path(project_root)
    filenames = {
        "LogisticRegressionTuned": "logistic_regression_best_params.json",
        "RandomForest": "random_forest_best_params.json",
        "GradientBoosting": "gradient_boosting_best_params.json",
    }
    return {
        name: json.loads(
            (root / "models" / filename).read_text(encoding="utf-8")
        )
        for name, filename in filenames.items()
    }


def make_estimator(model_name: str, params: dict):
    """Tạo estimator từ cấu hình đã chốt, không tinh chỉnh trên validation/test."""
    if model_name == "LogisticRegressionTuned":
        return LogisticRegression(**params)
    if model_name == "RandomForest":
        return RandomForestClassifier(**params)
    if model_name == "GradientBoosting":
        return LGBMClassifier(**params)
    raise ValueError(f"Unsupported model: {model_name}")


def make_pipeline(model_name: str, feature_set: str, X_train, params: dict):
    """Tạo pipeline với bộ feature và estimator đã chốt."""
    if feature_set not in FEATURE_SETS:
        raise ValueError(f"Unsupported feature set: {feature_set}")
    numeric, categorical = FEATURE_SETS[feature_set]
    return build_model_pipeline(
        X_train,
        make_estimator(model_name, params),
        numeric_features=numeric,
        categorical_features=categorical,
        scale_numeric=model_name == "LogisticRegressionTuned",
    )


def feature_columns(feature_set: str) -> list[str]:
    """Trả về danh sách cột đầu vào theo thứ tự numeric rồi categorical."""
    numeric, categorical = FEATURE_SETS[feature_set]
    return [*numeric, *categorical]
