from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import cast, func, or_, String
from sqlalchemy.orm import Session

from backend.app.database.models import Customer, LoanApplication, ModelPrediction
from backend.app.ml.inference import score_payload


def _customer_dict(customer: Customer) -> dict:
    return {
        "customer_id": customer.customer_id,
        "source_customer_id": int(customer.source_customer_id) if customer.source_customer_id is not None else None,
        "gender": customer.gender,
        "owns_car": customer.owns_car,
        "owns_realty": customer.owns_realty,
        "income_total": float(customer.income_total),
        "education_type": customer.education_type,
        "family_status": customer.family_status,
        "housing_type": customer.housing_type,
        "occupation_type": customer.occupation_type,
        "cnt_children": int(customer.cnt_children or 0),
        "family_members": int(customer.family_members or 0),
        "created_at": customer.created_at,
    }


def _application_dict(application: LoanApplication) -> dict:
    return {
        "application_id": application.application_id,
        "customer_id": application.customer_id,
        "credit_amount": float(application.credit_amount),
        "annuity_amount": float(application.annuity_amount),
        "goods_price": float(application.goods_price),
        "loan_type": application.loan_type,
        "application_date": application.application_date,
        "status": application.status,
    }


def _prediction_dict(prediction: ModelPrediction, application: LoanApplication, customer: Customer) -> dict:
    return {
        "prediction_id": prediction.prediction_id,
        "application_id": prediction.application_id,
        "customer_id": customer.customer_id,
        "probability_default": float(prediction.probability_default),
        "risk_category": prediction.risk_category,
        "model_version": prediction.model_version,
        "predicted_at": prediction.predicted_at.isoformat() if prediction.predicted_at else None,
        "credit_amount": float(application.credit_amount),
        "loan_type": application.loan_type,
    }


def list_customers(db: Session, query: str | None, limit: int, offset: int) -> dict:
    filters = []
    if query:
        like_pattern = f"%{query}%"
        filters.append(
            or_(
                cast(Customer.customer_id, String).ilike(like_pattern),
                cast(Customer.source_customer_id, String).ilike(like_pattern),
                Customer.gender.ilike(like_pattern),
                Customer.education_type.ilike(like_pattern),
                Customer.family_status.ilike(like_pattern),
                Customer.housing_type.ilike(like_pattern),
                Customer.occupation_type.ilike(like_pattern),
            )
        )

    total = db.query(func.count(Customer.customer_id)).filter(*filters).scalar() or 0
    customers = (
        db.query(Customer)
        .filter(*filters)
        .order_by(Customer.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "items": [_customer_dict(customer) for customer in customers],
        "total": int(total),
        "limit": limit,
        "offset": offset,
    }


def get_customer_detail(db: Session, customer_id: UUID) -> dict | None:
    customer = db.get(Customer, customer_id)
    if not customer:
        return None

    applications = (
        db.query(LoanApplication)
        .filter(LoanApplication.customer_id == customer_id)
        .order_by(LoanApplication.application_date.desc())
        .limit(10)
        .all()
    )

    predictions = (
        db.query(ModelPrediction, LoanApplication)
        .join(LoanApplication, LoanApplication.application_id == ModelPrediction.application_id)
        .filter(LoanApplication.customer_id == customer_id)
        .order_by(ModelPrediction.predicted_at.desc())
        .limit(10)
        .all()
    )

    return {
        "customer": _customer_dict(customer),
        "recent_applications": [_application_dict(application) for application in applications],
        "recent_predictions": [
            {
                **_prediction_dict(prediction, application, customer),
            }
            for prediction, application in predictions
        ],
    }


def list_predictions(db: Session, limit: int, offset: int) -> dict:
    total = db.query(func.count(ModelPrediction.prediction_id)).scalar() or 0
    rows = (
        db.query(ModelPrediction, LoanApplication, Customer)
        .join(LoanApplication, LoanApplication.application_id == ModelPrediction.application_id)
        .join(Customer, Customer.customer_id == LoanApplication.customer_id)
        .order_by(ModelPrediction.predicted_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    items = []
    for prediction, application, customer in rows:
        items.append(_prediction_dict(prediction, application, customer))

    return {
        "items": items,
        "total": int(total),
        "limit": limit,
        "offset": offset,
    }


def predict_for_customer(
    db: Session,
    customer_id: UUID,
    application_data: dict,
) -> dict | None:
    customer = db.get(Customer, customer_id)
    if not customer:
        return None

    payload = {
        "customer": _customer_dict(customer),
        "application": application_data,
    }
    score = score_payload(payload)

    application = LoanApplication(
        application_id=uuid4(),
        customer_id=customer_id,
        credit_amount=application_data["credit_amount"],
        annuity_amount=application_data["annuity_amount"],
        goods_price=application_data["goods_price"],
        loan_type=application_data["loan_type"],
        status="UNDER_REVIEW",
    )
    db.add(application)
    db.flush()

    prediction = ModelPrediction(
        prediction_id=uuid4(),
        application_id=application.application_id,
        probability_default=score["probability_default"],
        risk_category=score["risk_category"],
        model_version=score["model_version"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(application)
    db.refresh(prediction)

    return {
        "prediction_id": prediction.prediction_id,
        "application_id": application.application_id,
        "customer_id": customer_id,
        "probability_default": score["probability_default"],
        "risk_category": score["risk_category"],
        "model_version": score["model_version"],
        "recommendation": score["recommendation"],
    }
