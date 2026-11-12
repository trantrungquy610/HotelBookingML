
"""Tiền xử lý dữ liệu cho Hotel Booking Demand."""

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def clean_data(
    df: pd.DataFrame,
    *,
    copy: bool = True,
) -> pd.DataFrame:
    """Làm sạch dữ liệu theo quyết định M1.

    Không xóa dòng trùng. Không học tham số từ dữ liệu.
    """
    data = df.copy() if copy else df

    required = {
        "adr", "adults", "children", "babies",
        "meal", "agent", "company", "country",
        "arrival_date_year", "arrival_date_month",
        "arrival_date_day_of_month",
    }
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    # Loại booking lỗi
    invalid_adr = (data["adr"] < 0) | (data["adr"] > 1000)

    no_guests = (
        data["adults"].fillna(0)
        + data["children"].fillna(0)
        + data["babies"].fillna(0)
    ) == 0

    invalid_children = (
        (data["children"] >= 9)
        | (data["babies"] >= 9)
    )

    data = data.loc[
        ~(invalid_adr | no_guests | invalid_children)
    ].copy()

    # Chuẩn hóa meal
    data["meal"] = data["meal"].replace({"Undefined": "SC"})

    # Điền thiếu
    data["children"] = data["children"].fillna(0)

    # Mã định danh là categorical, không phải numeric
    for col in ["agent", "company"]:
        data[col] = data[col].astype("string").fillna("none")

    data["country"] = (
        data["country"].astype("string").fillna("missing")
    )

    # Tạo arrival_date phục vụ chia dữ liệu, không dùng làm feature
    month_map = {
        month: i
        for i, month in enumerate(
            [
                "January", "February", "March", "April",
                "May", "June", "July", "August",
                "September", "October", "November", "December",
            ],
            start=1,
        )
    }

    month_num = data["arrival_date_month"].map(month_map)

    if month_num.isna().any():
        raise ValueError("arrival_date_month contains invalid values.")

    data["arrival_date"] = pd.to_datetime(
        {
            "year": data["arrival_date_year"],
            "month": month_num,
            "day": data["arrival_date_day_of_month"],
        },
        errors="raise",
    )

    return data


def build_preprocessor(
    X: pd.DataFrame,
    *,
    numeric_features: list[str] | None = None,
    categorical_features: list[str] | None = None,
    scale_numeric: bool = True,
) -> ColumnTransformer:
    """Tạo transformer cho numeric/categorical.

    Việc fit transformer phải thực hiện bên trong Pipeline trên train.
    """

    if numeric_features is None and categorical_features is None:
        categorical_features = X.select_dtypes(
            include=["object", "category", "string"]
        ).columns.tolist()

        numeric_features = [
            col for col in X.columns
            if col not in categorical_features
        ]
    elif numeric_features is None or categorical_features is None:
        raise ValueError(
            "Provide both numeric_features and categorical_features, "
            "or let both be inferred."
        )

    numeric_features = list(numeric_features)
    categorical_features = list(categorical_features)

    if set(numeric_features) & set(categorical_features):
        raise ValueError("Numeric and categorical columns overlap.")

    selected = set(numeric_features) | set(categorical_features)
    if selected != set(X.columns):
        raise ValueError(
            "Every column in X must belong to numeric or categorical features."
        )

    numeric_steps = [
        ("imputer", SimpleImputer(strategy="median"))
    ]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    numeric_pipeline = Pipeline(numeric_steps)

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(
            strategy="constant",
            fill_value="missing",
        )),
        ("onehot", OneHotEncoder(
            handle_unknown="infrequent_if_exist",
            min_frequency=0.01,
        )),
    ])

    transformers = []

    if numeric_features:
        transformers.append(
            ("numeric", numeric_pipeline, numeric_features)
        )

    if categorical_features:
        transformers.append(
            ("categorical", categorical_pipeline, categorical_features)
        )

    return ColumnTransformer(
        transformers=transformers,
        remainder="drop",
    )


def build_model_pipeline(
    X: pd.DataFrame,
    estimator,
    *,
    numeric_features: list[str] | None = None,
    categorical_features: list[str] | None = None,
    scale_numeric: bool = True,
) -> Pipeline:
    """Ghép preprocessing và estimator thành sklearn Pipeline."""

    preprocessor = build_preprocessor(
        X,
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        scale_numeric=scale_numeric,
    )

    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", estimator),
    ])
