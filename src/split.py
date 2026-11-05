"""Các cách chia dữ liệu dùng chung cho mọi mô hình."""

import pandas as pd


def temporal_split(
    df: pd.DataFrame,
    *,
    train_end,
    valid_end,
    date_col: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Chia train/validation/test theo mốc thời gian tăng dần."""
    raise NotImplementedError("TV1 triển khai sau khi nhóm chốt M1.")


def random_split(
    df: pd.DataFrame,
    *,
    target_col: str = "is_canceled",
    test_size: float = 0.2,
    valid_size: float = 0.2,
    random_state: int = 42,
    stratify: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Chia ngẫu nhiên thành train/validation/test."""
    raise NotImplementedError("TV1 triển khai sau khi nhóm chốt M1.")


def hotel_split(
    df: pd.DataFrame,
    *,
    hotel_col: str = "hotel",
    train_hotel: str,
    test_hotel: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Chia theo khách sạn: train trên một khách sạn, test trên khách sạn kia."""
    raise NotImplementedError("TV1 triển khai sau khi nhóm chốt M1.")
