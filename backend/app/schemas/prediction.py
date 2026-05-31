from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CustomerPayload(BaseModel):
    customer_id: Optional[str] = None
    gender: str = Field(..., examples=["F"])
    owns_car: bool = False
    owns_realty: bool = False
    income_total: float = Field(..., gt=0)
    education_type: str
    family_status: str
    housing_type: str
    occupation_type: str
    cnt_children: int = Field(default=0, ge=0)
    family_members: int = Field(default=1, ge=1)


class LoanApplicationPayload(BaseModel):
    application_id: Optional[str] = None
    credit_amount: float = Field(..., gt=0)
    annuity_amount: float = Field(..., gt=0)
    goods_price: float = Field(..., gt=0)
    loan_type: str


class PredictionRequest(BaseModel):
    customer: CustomerPayload
    application: LoanApplicationPayload


class PredictionResponse(BaseModel):
    customer_id: Optional[str] = None
    application_id: Optional[str] = None
    probability_default: float
    risk_category: str
    model_version: str
    recommendation: str

