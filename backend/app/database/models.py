from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, Integer, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, mapped_column

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    customer_id = mapped_column(UUID(as_uuid=True), primary_key=True)
    source_customer_id = mapped_column(Integer, index=True)
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


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    application_id = mapped_column(UUID(as_uuid=True), primary_key=True)
    customer_id = mapped_column(UUID(as_uuid=True))
    credit_amount = mapped_column(Numeric(15, 2))
    annuity_amount = mapped_column(Numeric(15, 2))
    goods_price = mapped_column(Numeric(15, 2))
    loan_type = mapped_column(String(50))
    application_date = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    status = mapped_column(String(50))


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    prediction_id = mapped_column(UUID(as_uuid=True), primary_key=True)
    application_id = mapped_column(UUID(as_uuid=True))
    probability_default = mapped_column(Float)
    risk_category = mapped_column(String(50))
    model_version = mapped_column(String(50))
    predicted_at = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


class AdminUser(Base):
    __tablename__ = "admin_users"

    admin_id = mapped_column(UUID(as_uuid=True), primary_key=True)
    username = mapped_column(String(100), unique=True)
    password_hash = mapped_column(Text)
    role = mapped_column(String(50))
    created_at = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = mapped_column(UUID(as_uuid=True), primary_key=True)
    admin_id = mapped_column(UUID(as_uuid=True))
    action = mapped_column(Text)
    created_at = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    model_id = mapped_column(UUID(as_uuid=True), primary_key=True)
    model_name = mapped_column(String(100))
    model_version = mapped_column(String(50))
    roc_auc = mapped_column(Float)
    deployed = mapped_column(Boolean)
    created_at = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
