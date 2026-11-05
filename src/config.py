"""Cấu hình dùng chung cho toàn bộ project."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DATA_PATH = RAW_DATA_DIR / "hotels.csv"

RANDOM_STATE = 42
TARGET_COLUMN = "is_canceled"
DATASET_URL = (
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/"
    "master/data/2020/2020-02-11/hotels.csv"
)
