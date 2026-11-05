"""Đọc dữ liệu thô. Không làm sạch hoặc biến đổi dữ liệu tại module này."""

from pathlib import Path
import pandas as pd

from src.config import RAW_DATA_PATH


def load_raw(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Đọc CSV gốc và trả về DataFrame.

    Parameters
    ----------
    path:
        Đường dẫn CSV. Mặc định là data/raw/hotels.csv.

    Raises
    ------
    FileNotFoundError
        Nếu chưa tải dữ liệu; chạy `python scripts/download_data.py`.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy {path}. Hãy chạy: python scripts/download_data.py"
        )
    return pd.read_csv(path)
