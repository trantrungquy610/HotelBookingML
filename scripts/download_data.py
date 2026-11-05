"""Tải Hotel Booking Demand CSV về data/raw/hotels.csv."""

import argparse
import sys
from pathlib import Path
from urllib.request import urlopen

# Cho phép chạy trực tiếp: python scripts/download_data.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DATASET_URL, RAW_DATA_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Ghi đè file nếu đã tồn tại")
    args = parser.parse_args()

    output: Path = RAW_DATA_PATH
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists() and not args.force:
        print(f"Đã có dữ liệu: {output}. Dùng --force để tải lại.")
        return

    print(f"Đang tải dữ liệu từ: {DATASET_URL}")
    with urlopen(DATASET_URL, timeout=60) as response:
        content = response.read()

    if not content or not content.startswith(b"hotel,"):
        raise RuntimeError("Nội dung tải về không giống CSV mong đợi; không lưu file.")

    output.write_bytes(content)
    print(f"Đã lưu {len(content):,} bytes tại: {output}")


if __name__ == "__main__":
    main()
