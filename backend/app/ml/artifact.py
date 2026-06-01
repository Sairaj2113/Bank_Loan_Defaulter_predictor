from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parents[3] / "models" / "LightGBM.pkl"


class _FallbackRiskModel:
    def predict_proba(self, frame: pd.DataFrame) -> np.ndarray:
        probabilities: list[float] = []
        for _, row in frame.iterrows():
            income = float(row.get("income_total", 0) or 0)
            credit = float(row.get("credit_amount", 0) or 0)
            annuity = float(row.get("annuity_amount", 0) or 0)
            family_members = float(row.get("family_members", 1) or 1)
            children = float(row.get("cnt_children", 0) or 0)
            assets = float(row.get("owns_car", 0) or 0) + float(row.get("owns_realty", 0) or 0)

            ratio_credit_income = credit / max(income, 1.0)
            ratio_annuity_income = annuity / max(income, 1.0)
            burden = ratio_credit_income + (ratio_annuity_income * 2.5)
            family_penalty = 0.05 if family_members >= 4 else 0.0
            child_penalty = 0.04 if children > 0 else 0.0
            asset_bonus = 0.08 if assets >= 2 else 0.0

            probability = 0.22 + (0.18 * min(burden, 4.0)) + family_penalty + child_penalty - asset_bonus
            probabilities.append(float(min(max(probability, 0.03), 0.97)))

        positives = np.array(probabilities, dtype=float)
        negatives = 1.0 - positives
        return np.column_stack([negatives, positives])


def load_model_bundle(path: Path | None = None) -> dict[str, Any]:
    model_path = Path(path) if path is not None else MODEL_PATH
    if not model_path.exists():
        return {
            "pipeline": _FallbackRiskModel(),
            "metadata": {
                "model_name": "FallbackRiskModel",
                "model_version": "fallback_v1",
                "validation_auc": None,
                "feature_count": None,
            },
        }

    bundle = joblib.load(model_path)
    if isinstance(bundle, dict):
        return bundle

    return {"pipeline": bundle, "metadata": {}}
