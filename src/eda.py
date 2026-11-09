"""Helpers for exploratory data analysis (T03).

Functions here only describe the data. They must not be used to fit any
transformation that later feeds a model.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

from src.config import PROJECT_ROOT, TARGET_COLUMN

FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def save_figure(fig: plt.Figure, name: str, *, dpi: int = 150) -> Path:
    """Save `fig` to reports/figures/<name>.png and return the file path."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return path


def cancel_rate_table(
    df: pd.DataFrame,
    col: str,
    *,
    target: str = TARGET_COLUMN,
    top: int | None = None,
) -> pd.DataFrame:
    """Booking count, share of all rows and cancellation rate per value of `col`.

    Missing values form their own group. Rows are sorted by count, and `top`
    keeps only the most frequent values.
    """
    table = (
        df.groupby(col, dropna=False)[target]
        .agg(n_bookings="size", cancel_rate="mean")
        .sort_values("n_bookings", ascending=False)
    )
    table.insert(1, "share", table["n_bookings"] / len(df))
    if top is not None:
        table = table.head(top)
    return table


def arrival_date(df: pd.DataFrame) -> pd.Series:
    """Build the arrival date from the year, month-name and day columns."""
    month = df["arrival_date_month"].map(
        {name: i for i, name in enumerate(MONTH_ORDER, start=1)}
    )
    parts = pd.DataFrame({
        "year": df["arrival_date_year"],
        "month": month,
        "day": df["arrival_date_day_of_month"],
    })
    return pd.to_datetime(parts).rename("arrival_date")


def plot_cancel_rate(
    table: pd.DataFrame,
    ax: plt.Axes,
    *,
    overall: float | None = None,
    title: str | None = None,
) -> plt.Axes:
    """Horizontal bars of cancellation rate per category, labelled with counts.

    `table` is the output of `cancel_rate_table`. `overall` draws a dashed
    reference line at the overall cancellation rate.
    """
    positions = range(len(table))
    ax.barh(positions, table["cancel_rate"], color="#4C72B0")
    ax.set_yticks(list(positions), [str(v) for v in table.index])
    ax.invert_yaxis()
    for pos, (rate, n) in enumerate(zip(table["cancel_rate"], table["n_bookings"])):
        ax.text(rate + 0.01, pos, f"{rate:.0%} (n={n:,})", va="center", fontsize=8)
    if overall is not None:
        ax.axvline(overall, color="grey", linestyle="--", linewidth=1)
    ax.set_xlim(0, 1.35)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xlabel("Tỉ lệ hủy")
    if title:
        ax.set_title(title)
    return ax
