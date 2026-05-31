from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, mapped_column

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    customer_id = mapped_column(UUID(as_uuid=True), primary_key=True)
    gender = mapped_column(String(20))
    owns_car = mapped_column(Boolean)
    owns_realty = mapped_column(Boolean)
    income_total = mapped_column(Numeric(15, 2))
    education_type = mapped_column(String(100))
    family_status = mapped_column(String(100))
    housing_type = mapped_column(String(100))
    occupation_type = mapped_column(String(100))
    cnt_children = mapped_column(Integer)
    family_members = mapped_column(Integer)
    created_at = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

