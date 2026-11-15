"""T16: đánh giá cuối trên test với cấu hình và threshold đã khóa."""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import TARGET_COLUMN
from src.data import load_raw
from src.evaluate import RESULT_COLUMNS, evaluate_classification
from src.features import add_features
from src.modeling import MODEL_NAMES, feature_columns, load_best_params, make_pipeline
from src.preprocess import clean_data
from src.split import temporal_split


THRESHOLDS_PATH = PROJECT_ROOT / "models" / "cost_thresholds.json"
FINAL_PATH = PROJECT_ROOT / "reports" / "results" / "final_test.csv"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"


def main() -> None:
    if not THRESHOLDS_PATH.exists():
        raise FileNotFoundError("Run T15 first to create cost_thresholds.json.")
    threshold_config = json.loads(THRESHOLDS_PATH.read_text(encoding="utf-8"))
    primary = threshold_config["primary_scenario"]
    thresholds = threshold_config["thresholds"]
    df = add_features(clean_data(load_raw()))
    train, _valid, test = temporal_split(
        df, train_end="2017-01-01", valid_end="2017-07-01",
        date_col="arrival_date",
    )
    params = load_best_params(PROJECT_ROOT)
    rows = []
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, len(MODEL_NAMES), figsize=(14, 4))
    for ax, model_name in zip(axes, MODEL_NAMES):
        features = feature_columns("clean")
        pipeline = make_pipeline(
            model_name, "clean", train[features], params[model_name]
        ).fit(train[features], train[TARGET_COLUMN])
        y_score = pipeline.predict_proba(test[features])[:, 1]
        policies = {
            "default_0.5": 0.5,
            "cost_selected": float(thresholds[model_name][primary]),
        }
        for policy, threshold in policies.items():
            y_pred = (y_score >= threshold).astype(int)
            metrics = evaluate_classification(
                test[TARGET_COLUMN], y_pred, y_score
            )
            c_fn, c_fp = threshold_config["cost_scenarios"][primary]
            expected = c_fn * metrics["FN"] + c_fp * metrics["FP"]
            rows.append({
                "model_name": model_name,
                "experiment": "main",
                "feature_set": "clean",
                "split": "temporal",
                "train_hotel": "all",
                "eval_hotel": "all",
                "eval_set": "test",
                "policy": policy,
                "threshold": threshold,
                "n_eval": len(test),
                "eval_cancel_rate": float(test[TARGET_COLUMN].mean()),
                "average_precision": metrics["average_precision"],
                "average_precision_std": pd.NA,
                "f1": metrics["f1"],
                "roc_auc": metrics["roc_auc"],
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "cost_scenario": primary,
                "C_FN": c_fn,
                "C_FP": c_fp,
                "TN": metrics["TN"],
                "FP": metrics["FP"],
                "FN": metrics["FN"],
                "TP": metrics["TP"],
                "expected_cost": expected,
                "cost_per_booking": expected / len(test),
                "params": json.dumps(params[model_name], sort_keys=True),
            })
        chosen = rows[-1]
        ConfusionMatrixDisplay.from_predictions(
            test[TARGET_COLUMN],
            (y_score >= chosen["threshold"]).astype(int),
            display_labels=["Không hủy", "Hủy"],
            values_format=",d",
            colorbar=False,
            ax=ax,
        )
        ax.set_title(model_name)
        ax.grid(False)
    fig.tight_layout()
    fig.savefig(
        FIGURES_DIR / "final_test_confusion_matrices.png",
        dpi=160,
        bbox_inches="tight",
    )
    plt.close(fig)

    result = pd.DataFrame(rows)
    result.to_csv(FINAL_PATH, index=False)
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
