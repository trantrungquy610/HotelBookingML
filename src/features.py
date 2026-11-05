"""Feature engineering. TV2 triển khai chi tiết sau EDA."""

import pandas as pd


def add_features(
    df: pd.DataFrame,
    *,
    copy: bool = True,
) -> pd.DataFrame:
    """Tạo đặc trưng từ dữ liệu booking và trả về DataFrame.

    Giữ nguyên index và không sửa DataFrame đầu vào nếu copy=True.
    Danh sách feature sẽ được chốt dựa trên EDA tại T03.
    """
    raise NotImplementedError("TV2 triển khai sau khi hoàn thành T03/EDA.")
