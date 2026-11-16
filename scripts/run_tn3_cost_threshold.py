"""T15: chọn threshold theo chi phí trên validation."""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import TARGET_COLUMN
from src.data import load_raw
from src.evaluate import (
    RESULT_COLUMNS,
    append_result,
    evaluate_classification,
    select_cost_threshold,
)
from src.features import add_features
from src.modeling import MODEL_NAMES, feature_columns, load_best_params, make_pipeline
from src.preprocess import clean_data
from src.split import temporal_split


RESULTS_PATH = PROJECT_ROOT / "reports" / "results" / "results.csv"
THRESHOLDS_PATH = PROJECT_ROOT / "models" / "cost_thresholds.json"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
SCENARIOS = {
    "balanced": (1.0, 1.0),
    "fill_rooms": (2.0, 1.0),
    "cautious_overbooking": (1.0, 2.0),
}


def main() -> None:
    df = add_features(clean_data(load_raw()))
    # Use the sorted train split, as in T16: RandomForest bootstraps by row
    # position, so a differently ordered train set gives a different forest
    train, valid, _test = temporal_split(
        df, train_end="2017-01-01", valid_end="2017-07-01",
        date_col="arrival_date",
    )
    params = load_best_params(PROJECT_ROOT)
    feature_set = "clean"
    thresholds = {}
    curve_rows = []
    result_rows = []

    for model_name in MODEL_NAMES:
        features = feature_columns(feature_set)
        pipeline = make_pipeline(
            model_name, feature_set, train[features], params[model_name]
        )
        pipeline.fit(train[features], train[TARGET_COLUMN])
        y_score = pipeline.predict_proba(valid[features])[:, 1]

        thresholds[model_name] = {}
        for scenario, (c_fn, c_fp) in SCENARIOS.items():
            selected = select_cost_threshold(
                valid[TARGET_COLUMN], y_score, c_fn=c_fn, c_fp=c_fp
            )
            thresholds[model_name][scenario] = selected["threshold"]
            result_rows.append({
                "model_name": model_name,
                "experiment": "TN3",
                "feature_set": feature_set,
                "split": "temporal",
                "train_hotel": "all",
                "eval_hotel": "all",
                "eval_set": "validation",
                "n_eval": len(valid),
                "eval_cancel_rate": float(valid[TARGET_COLUMN].mean()),
                "average_precision": selected["average_precision"],
                "f1": selected["f1"],
                "roc_auc": selected["roc_auc"],
                "precision": selected["precision"],
                "recall": selected["recall"],
                "threshold": selected["threshold"],
                "cost_scenario": scenario,
                "C_FN": c_fn,
                "C_FP": c_fp,
                "TN": selected["TN"],
                "FP": selected["FP"],
                "FN": selected["FN"],
                "TP": selected["TP"],
                "expected_cost": selected["expected_cost"],
                "cost_per_booking": selected["cost_per_booking"],
                "params": json.dumps(params[model_name], sort_keys=True),
            })
            for threshold in [i / 100 for i in range(1, 100)]:
                metrics = evaluate_classification(
                    valid[TARGET_COLUMN],
                    (y_score >= threshold).astype(int),
                    y_score,
                )
                curve_rows.append({
                    "model_name": model_name,
                    "scenario": scenario,
                    "threshold": threshold,
                    "expected_cost": c_fn * metrics["FN"] + c_fp * metrics["FP"],
                })

    THRESHOLDS_PATH.write_text(
        json.dumps(
            {
                "cost_scenarios": SCENARIOS,
                "primary_scenario": "cautious_overbooking",
                "thresholds": thresholds,
                "selection_set": "validation",
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    curves = pd.DataFrame(curve_rows)
    fig, axes = plt.subplots(1, len(MODEL_NAMES), figsize=(15, 4), sharey=True)
    for ax, model_name in zip(axes, MODEL_NAMES):
        subset = curves[curves["model_name"] == model_name]
        for scenario in SCENARIOS:
            line = subset[subset["scenario"] == scenario]
            ax.plot(line["threshold"], line["expected_cost"], label=scenario)
            ax.axvline(
                thresholds[model_name][scenario], linestyle="--", alpha=0.5
            )
        ax.set_title(model_name)
        ax.set_xlabel("Threshold")
        ax.grid(alpha=0.2)
    axes[0].set_ylabel("Expected cost")
    axes[-1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(
        FIGURES_DIR / "tn3_cost_by_threshold.png", dpi=160, bbox_inches="tight"
    )
    plt.close(fig)

    if RESULTS_PATH.exists():
        existing = pd.read_csv(RESULTS_PATH, dtype=str, keep_default_na=False)
        if list(existing.columns) != RESULT_COLUMNS:
            raise ValueError("results.csv does not match RESULT_COLUMNS")
        owned = (
            existing["experiment"].eq("TN3")
            & existing["eval_set"].eq("validation")
        )
        existing.loc[~owned].to_csv(RESULTS_PATH, index=False)
    for row in result_rows:
        append_result(row, path=str(RESULTS_PATH))
    print(pd.DataFrame(result_rows)[
        ["model_name", "cost_scenario", "threshold", "expected_cost"]
    ].to_string(index=False))


if __name__ == "__main__":
    main()
