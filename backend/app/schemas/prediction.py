from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

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


class PredictionRequestByCustomer(BaseModel):
    credit_amount: float = Field(..., gt=0)
    annuity_amount: float = Field(..., gt=0)
    goods_price: float = Field(..., gt=0)
    loan_type: str


class PredictionRequest(BaseModel):
    customer: CustomerPayload
    application: LoanApplicationPayload


class PredictionResponse(BaseModel):
    prediction_id: Optional[UUID] = None
    application_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    probability_default: float
    risk_category: str
    model_version: str
    recommendation: str


class PredictionListItem(BaseModel):
    prediction_id: UUID
    application_id: UUID
    customer_id: UUID
    probability_default: float
    risk_category: str
    model_version: str
    predicted_at: Optional[datetime] = None


class PredictionListResponse(BaseModel):
    items: list[PredictionListItem]
    total: int
    limit: int
    offset: int
