from __future__ import annotations

from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from backend.app.database.database import get_db, ping_database
from backend.app.ml.inference import get_model_bundle, score_payload
from backend.app.schemas.customer import CustomerDetailResponse, CustomerListResponse
from backend.app.schemas.prediction import (
    PredictionListResponse,
    PredictionRequest,
    PredictionRequestByCustomer,
    PredictionResponse,
)
from backend.app.services.loan_service import (
    get_customer_detail,
    list_customers,
    list_predictions,
    predict_for_customer,
)

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


@app.get("/customers", response_model=CustomerListResponse)
def get_customers(
    q: str | None = Query(default=None, description="Search customer id or attributes"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db=Depends(get_db),
) -> dict:
    return list_customers(db, q, limit, offset)


@app.get("/customer/{customer_id}", response_model=CustomerDetailResponse)
def get_customer(customer_id: UUID, db=Depends(get_db)) -> dict:
    detail = get_customer_detail(db, customer_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return detail


@app.get("/predictions", response_model=PredictionListResponse)
def get_predictions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db=Depends(get_db),
) -> dict:
    return list_predictions(db, limit, offset)


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
    bundle = get_model_bundle()
    metadata = bundle.get("metadata", {})
    return {
        "model_name": metadata.get("model_name", "LightGBM"),
        "model_version": metadata.get("model_version", "lightgbm_v1"),
        "validation_auc": metadata.get("validation_auc"),
        "feature_count": metadata.get("feature_count"),
    }


@app.get("/demo-prediction")
def demo_prediction() -> dict[str, object]:
    score = score_payload(DEMO_CLIENT)
    bundle = get_model_bundle()
    metadata = bundle.get("metadata", {})
    return {
        "client": DEMO_CLIENT,
        "probability_default": score["probability_default"],
        "risk_category": score["risk_category"],
        "recommendation": score["recommendation"],
        "model_version": str(metadata.get("model_version", "lightgbm_v1")),
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    try:
        score = score_payload(request.model_dump() if hasattr(request, "model_dump") else request.dict())
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Model artifact is missing. Run `python training/train.py` to create models/LightGBM.pkl.",
        )

    return PredictionResponse(
        customer_id=request.customer.customer_id,
        application_id=request.application.application_id,
        probability_default=score["probability_default"],
        risk_category=score["risk_category"],
        model_version=score["model_version"],
        recommendation=score["recommendation"],
    )


@app.post("/predict/{customer_id}", response_model=PredictionResponse)
def predict_for_existing_customer(
    customer_id: UUID,
    request: PredictionRequestByCustomer,
    db=Depends(get_db),
) -> PredictionResponse:
    application_data = request.model_dump() if hasattr(request, "model_dump") else request.dict()
    result = predict_for_customer(db, customer_id, application_data)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found.")

    return PredictionResponse(
        prediction_id=result["prediction_id"],
        application_id=result["application_id"],
        customer_id=result["customer_id"],
        probability_default=result["probability_default"],
        risk_category=result["risk_category"],
        model_version=result["model_version"],
        recommendation=result["recommendation"],
    )
