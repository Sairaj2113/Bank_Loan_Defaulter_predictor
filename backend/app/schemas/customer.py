from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CustomerRead(BaseModel):
    customer_id: UUID
    source_customer_id: Optional[int] = None
    gender: str
    owns_car: bool
    owns_realty: bool
    income_total: float
    education_type: str
    family_status: str
    housing_type: str
    occupation_type: str
    cnt_children: int
    family_members: int
    created_at: Optional[datetime] = None


class CustomerListResponse(BaseModel):
    items: list[CustomerRead]
    total: int
    limit: int
    offset: int


class CustomerDetailResponse(BaseModel):
    customer: CustomerRead
    recent_applications: list[dict]
    recent_predictions: list[dict]
