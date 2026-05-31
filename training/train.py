from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.ml.feature_builder import (  # noqa: E402
    MODEL_CATEGORICAL_COLUMNS,
    MODEL_NUMERIC_COLUMNS,
    ProjectFeatureBuilder,
)

DATA_PATH = ROOT / "dataset" / "train.csv"
MODEL_PATH = ROOT / "models" / "LightGBM.pkl"
METADATA_PATH = ROOT / "models" / "LightGBM.metadata.json"

FIELD_MAP = {
    "gender": "CODE_GENDER",
    "owns_car": "FLAG_OWN_CAR",
    "owns_realty": "FLAG_OWN_REALTY",
    "income_total": "AMT_INCOME_TOTAL",
    "education_type": "NAME_EDUCATION_TYPE",
    "family_status": "NAME_FAMILY_STATUS",
    "housing_type": "NAME_HOUSING_TYPE",
    "occupation_type": "OCCUPATION_TYPE",
    "cnt_children": "CNT_CHILDREN",
    "family_members": "CNT_FAM_MEMBERS",
    "credit_amount": "AMT_CREDIT",
    "annuity_amount": "AMT_ANNUITY",
    "goods_price": "AMT_GOODS_PRICE",
    "loan_type": "NAME_CONTRACT_TYPE",
}


def load_training_frame() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Training data not found at {DATA_PATH}")

    raw = pd.read_csv(DATA_PATH, low_memory=False)
    frame = pd.DataFrame({target: raw[source] for target, source in FIELD_MAP.items()})
    frame["target"] = raw["TARGET"].astype(int)
    return frame


def build_pipeline(scale_pos_weight: float) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline([("imputer", SimpleImputer(strategy="median"))]),
                MODEL_NUMERIC_COLUMNS,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                MODEL_CATEGORICAL_COLUMNS,
            ),
        ],
        remainder="drop",
    )

    try:
        preprocessor.set_output(transform="pandas")
    except AttributeError:
        pass

    classifier = LGBMClassifier(
        objective="binary",
        learning_rate=0.03,
        n_estimators=600,
        num_leaves=64,
        max_depth=-1,
        min_child_samples=40,
        subsample=0.85,
        subsample_freq=1,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=0.5,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        n_jobs=-1,
        verbose=-1,
    )

    return Pipeline(
        steps=[
            ("features", ProjectFeatureBuilder()),
            ("preprocess", preprocessor),
            ("model", classifier),
        ]
    )


def main() -> None:
    frame = load_training_frame()
    y = frame.pop("target")

    x_train, x_valid, y_train, y_valid = train_test_split(
        frame,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    scale_pos_weight = float((y_train == 0).sum() / max((y_train == 1).sum(), 1))
    pipeline = build_pipeline(scale_pos_weight)

    pipeline.fit(x_train, y_train)
    validation_probabilities = pipeline.predict_proba(x_valid)[:, 1]
    validation_auc = roc_auc_score(y_valid, validation_probabilities)

    pipeline.fit(frame, y)

    model_version = f"lightgbm_v1_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    metadata = {
        "model_version": model_version,
        "validation_auc": float(round(validation_auc, 6)),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "source_dataset": str(DATA_PATH),
        "feature_columns": MODEL_NUMERIC_COLUMNS + MODEL_CATEGORICAL_COLUMNS,
        "target_name": "TARGET",
        "scale_pos_weight": scale_pos_weight,
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "metadata": metadata}, MODEL_PATH)
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Saved model artifact to {MODEL_PATH}")
    print(f"Validation ROC-AUC: {validation_auc:.6f}")
    print(f"Model version: {model_version}")


if __name__ == "__main__":
    main()
