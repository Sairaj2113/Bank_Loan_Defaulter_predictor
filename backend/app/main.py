from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from backend.app.database.database import ping_database
from backend.app.ml.artifact import load_model_bundle
from backend.app.ml.feature_builder import probability_to_risk, payload_to_frame
from backend.app.schemas.prediction import PredictionRequest, PredictionResponse

app = FastAPI(title="Loan Risk Assessment API", version="1.0.0")

DEMO_CLIENT = {
    "customer": {
        "customer_id": "demo-customer-001",
        "gender": "F",
        "owns_car": False,
        "owns_realty": False,
        "income_total": 90000.0,
        "education_type": "Higher education",
        "family_status": "Married",
        "housing_type": "House / apartment",
        "occupation_type": "Laborers",
        "cnt_children": 2,
        "family_members": 4,
    },
    "application": {
        "application_id": "demo-application-001",
        "credit_amount": 227520.0,
        "annuity_amount": 13189.5,
        "goods_price": 180000.0,
        "loan_type": "Cash loans",
    },
}


@lru_cache(maxsize=1)
def get_model_bundle():
    bundle = load_model_bundle()
    if "pipeline" not in bundle:
        raise RuntimeError("Saved model bundle is missing the pipeline object.")
    return bundle


@app.get("/health")
def health() -> dict[str, str]:
    try:
        bundle = get_model_bundle()
        model_ready = bool(bundle)
    except FileNotFoundError:
        model_ready = False
    return {
        "status": "ok",
        "model_ready": str(model_ready).lower(),
    }


@app.get("/db-health")
def db_health() -> dict[str, str]:
    try:
        connected = ping_database()
    except Exception as exc:  # pragma: no cover - runtime diagnostics only
        return {
            "status": "down",
            "detail": str(exc),
        }
    return {
        "status": "up",
        "connected": str(bool(connected)).lower(),
    }


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return """
    <html>
      <head>
        <title>Loan Risk Assessment API</title>
        <style>
          body { font-family: Arial, sans-serif; background: #f5f7fb; color: #172033; margin: 0; padding: 40px; }
          .card { max-width: 760px; margin: 0 auto; background: white; border-radius: 18px; padding: 32px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); }
          h1 { margin-top: 0; }
          code { background: #eef2ff; padding: 2px 6px; border-radius: 6px; }
          ul { line-height: 1.7; }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>Loan Risk Assessment API</h1>
          <p>The model is loaded and ready for demo predictions.</p>
          <ul>
            <li>Health check: <code>/health</code></li>
            <li>Database check: <code>/db-health</code></li>
            <li>Model details: <code>/model-info</code></li>
            <li>Interactive docs: <code>/docs</code></li>
            <li>Demo prediction: <code>/demo-prediction</code></li>
          </ul>
        </div>
      </body>
    </html>
    """


@app.get("/model-info")
def model_info() -> dict[str, object]:
    try:
        bundle = get_model_bundle()
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Model artifact is not loaded.")

    metadata = bundle.get("metadata", {})
    return {
        "model_version": metadata.get("model_version", "unknown"),
        "validation_auc": metadata.get("validation_auc"),
        "trained_at": metadata.get("trained_at"),
    }


@app.get("/demo-prediction")
def demo_prediction() -> dict[str, object]:
    try:
        bundle = get_model_bundle()
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Model artifact is not loaded.")

    pipeline = bundle["pipeline"]
    metadata = bundle.get("metadata", {})
    features = payload_to_frame(DEMO_CLIENT)
    probability = float(pipeline.predict_proba(features)[0, 1])
    risk_category = probability_to_risk(probability)
    recommendation = "APPROVE" if risk_category == "LOW_RISK" else "REVIEW" if risk_category == "MEDIUM_RISK" else "REJECT"

    return {
        "client": DEMO_CLIENT,
        "probability_default": round(probability, 6),
        "risk_category": risk_category,
        "recommendation": recommendation,
        "model_version": str(metadata.get("model_version", "lightgbm_v1")),
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    try:
        bundle = get_model_bundle()
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Model artifact is missing. Run `python training/train.py` to create models/LightGBM.pkl.",
        )

    pipeline = bundle["pipeline"]
    metadata = bundle.get("metadata", {})

    request_payload = request.model_dump() if hasattr(request, "model_dump") else request.dict()
    features = payload_to_frame(request_payload)
    probability = float(pipeline.predict_proba(features)[0, 1])
    risk_category = probability_to_risk(probability)
    recommendation = "APPROVE" if risk_category == "LOW_RISK" else "REVIEW" if risk_category == "MEDIUM_RISK" else "REJECT"

    return PredictionResponse(
        customer_id=request.customer.customer_id,
        application_id=request.application.application_id,
        probability_default=round(probability, 6),
        risk_category=risk_category,
        model_version=str(metadata.get("model_version", "lightgbm_v1")),
        recommendation=recommendation,
    )
