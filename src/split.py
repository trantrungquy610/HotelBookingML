
"""Các cách chia dữ liệu dùng chung cho mọi mô hình."""

import pandas as pd
from sklearn.model_selection import train_test_split


def temporal_split(
    df: pd.DataFrame,
    *,
    train_end,
    valid_end,
    date_col: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Chia theo thời gian và sắp xếp từng tập tăng dần.

    train: date < train_end
    valid: train_end <= date < valid_end
    test:  date >= valid_end

    Giữ nguyên index và target.
    """
    if date_col not in df.columns:
        raise ValueError(f"Missing date column: {date_col}")

    dates = pd.to_datetime(df[date_col], errors="coerce")

    if dates.isna().any():
        raise ValueError(f"{date_col} contains missing/invalid dates.")

    train_end = pd.Timestamp(train_end)
    valid_end = pd.Timestamp(valid_end)

    if train_end >= valid_end:
        raise ValueError("train_end must be earlier than valid_end.")

    train = df.loc[dates < train_end].copy()
    valid = df.loc[
        (dates >= train_end) & (dates < valid_end)
    ].copy()
    test = df.loc[dates >= valid_end].copy()

    train = train.sort_values(date_col, kind="mergesort")
    valid = valid.sort_values(date_col, kind="mergesort")
    test = test.sort_values(date_col, kind="mergesort")

    return train, valid, test


def random_split(
    df: pd.DataFrame,
    *,
    target_col: str = "is_canceled",
    test_size: float = 0.086,
    valid_size: float = 0.255,
    random_state: int = 42,
    stratify: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Chia ngẫu nhiên train/validation/test.

    test_size và valid_size đều tính trên TOÀN BỘ dữ liệu.
    """
    if target_col not in df.columns:
        raise ValueError(f"Missing target column: {target_col}")

    if not (0 < test_size < 1):
        raise ValueError("test_size must be between 0 and 1.")

    if not (0 < valid_size < 1 - test_size):
        raise ValueError(
            "valid_size must be positive and smaller than 1-test_size."
        )

    y = df[target_col]

    stratify_y = y if stratify else None

    train_valid, test = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_y,
    )

    # valid_size tính trên toàn bộ df, nên cần đổi
    # thành tỷ lệ trên phần train_valid.
    valid_fraction_remaining = valid_size / (1 - test_size)

    stratify_remaining = (
        train_valid[target_col] if stratify else None
    )

    train, valid = train_test_split(
        train_valid,
        test_size=valid_fraction_remaining,
        random_state=random_state,
        stratify=stratify_remaining,
    )

    return train, valid, test


def hotel_split(
    df,
    *,
    hotel_col="hotel",
    train_hotel,
    test_hotel,
):
    """Chia dữ liệu theo khách sạn.

    Parameters
    ----------
    df : pandas.DataFrame
        Dữ liệu đầu vào.
    hotel_col : str, default="hotel"
        Tên cột chứa loại khách sạn.
    train_hotel : str
        Khách sạn được dùng làm tập train.
    test_hotel : str
        Khách sạn được dùng làm tập test.

    Returns
    -------
    train : pandas.DataFrame
        Các dòng thuộc train_hotel.
    test : pandas.DataFrame
        Các dòng thuộc test_hotel.

    Notes
    -----
    Các dòng thuộc khách sạn khác hai giá trị trên sẽ bị loại.
    Hàm không thực hiện chia dữ liệu theo thời gian.
    """
    if hotel_col not in df.columns:
        raise ValueError(f"Không tìm thấy cột '{hotel_col}'.")

    if train_hotel == test_hotel:
        raise ValueError("train_hotel và test_hotel phải khác nhau.")

    available_hotels = set(df[hotel_col].dropna().unique())

    if train_hotel not in available_hotels:
        raise ValueError(f"Không tìm thấy khách sạn train: {train_hotel}")

    if test_hotel not in available_hotels:
        raise ValueError(f"Không tìm thấy khách sạn test: {test_hotel}")

    train = df.loc[df[hotel_col] == train_hotel].copy()
    test = df.loc[df[hotel_col] == test_hotel].copy()

    return train, test
