
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

# Các biến phân loại của bộ feature sạch (clean).
CLEAN_CATEGORICAL_FEATURES = [
    "hotel",
    "arrival_date_month",
    "meal",
    "market_segment",
    "distribution_channel",
    "reserved_room_type",
    "customer_type",
    "agent",
    "company",
]

# Bộ feature thông thường (conventional) bổ sung 3 biến phân loại.
CONVENTIONAL_CATEGORICAL_FEATURES = [
    *CLEAN_CATEGORICAL_FEATURES,
    "assigned_room_type",
    "deposit_type",
    "country",
]
