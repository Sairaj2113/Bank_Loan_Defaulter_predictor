from __future__ import annotations

from functools import lru_cache

from backend.app.ml.artifact import load_model_bundle
from backend.app.ml.feature_builder import payload_to_frame, probability_to_risk


@lru_cache(maxsize=1)
def get_model_bundle():
    bundle = load_model_bundle()
    if "pipeline" not in bundle:
        raise RuntimeError("Saved model bundle is missing the pipeline object.")
    return bundle


def score_payload(payload: dict) -> dict[str, object]:
    bundle = get_model_bundle()
    pipeline = bundle["pipeline"]
    metadata = bundle.get("metadata", {})
    features = payload_to_frame(payload)
    probability = float(pipeline.predict_proba(features)[0, 1])
    risk_category = probability_to_risk(probability)
    recommendation = "APPROVE" if risk_category == "LOW_RISK" else "REVIEW" if risk_category == "MEDIUM_RISK" else "REJECT"

    return {
        "probability_default": round(probability, 6),
        "risk_category": risk_category,
        "recommendation": recommendation,
        "model_version": str(metadata.get("model_version", "lightgbm_v1")),
    }
