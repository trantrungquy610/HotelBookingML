"""Tiền xử lý dữ liệu. TV1 triển khai sau mốc M1."""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


def build_preprocessor(
    X: pd.DataFrame,
    *,
    numeric_features: list[str] | None = None,
    categorical_features: list[str] | None = None,
    scale_numeric: bool = True,
) -> ColumnTransformer:
    """Tạo transformer cho numeric/categorical; chỉ fit trên train.

    Nếu không truyền danh sách cột, tự suy ra từ dtype của X.
    """
    raise NotImplementedError("TV1 triển khai sau khi nhóm chốt M1.")


def build_model_pipeline(
    X: pd.DataFrame,
    estimator,
    *,
    numeric_features: list[str] | None = None,
    categorical_features: list[str] | None = None,
    scale_numeric: bool = True,
) -> Pipeline:
    """Ghép preprocessing và estimator thành một sklearn Pipeline."""
    raise NotImplementedError("TV1 triển khai sau khi nhóm chốt M1.")
