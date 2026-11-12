"""Feature engineering (T08).

`add_features` runs after `src.preprocess.clean_data` and before the data is
split. It only applies fixed row-wise rules and learns nothing from the data,
so running it on the full dataset does not leak information. The choice of
features is justified in notebooks/02_features.ipynb.
"""

import pandas as pd

# Columns created by add_features, grouped by how build_preprocessor encodes
# them. Append these to the clean and conventional feature lists.
ENGINEERED_CATEGORICAL_FEATURES = ["arrival_weekday"]
ENGINEERED_NUMERIC_FEATURES: list[str] = []

_REQUIRED_COLUMNS = {"arrival_date"}


def add_features(
    df: pd.DataFrame,
    *,
    copy: bool = True,
) -> pd.DataFrame:
    """Add engineered features to a cleaned booking DataFrame.

    Call it after `clean_data`, which creates the `arrival_date` column.

    Added columns:
        arrival_weekday: day name of the arrival date ("Monday" ... "Sunday").
            Known at booking time; the clean feature set cannot derive it
            because it drops `arrival_date_year`.

    The index and the number of rows are kept. The input is not modified when
    `copy=True`.
    """
    missing = _REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}. Run clean_data first."
        )

    data = df.copy() if copy else df

    arrival = pd.to_datetime(data["arrival_date"], errors="raise")
    if arrival.isna().any():
        raise ValueError("arrival_date contains missing values.")

    data["arrival_weekday"] = arrival.dt.day_name()
    return data
