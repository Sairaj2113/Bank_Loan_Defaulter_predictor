from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

RAW_NUMERIC_COLUMNS = [
    "owns_car",
    "owns_realty",
    "income_total",
    "cnt_children",
    "family_members",
    "credit_amount",
    "annuity_amount",
    "goods_price",
]

RAW_CATEGORICAL_COLUMNS = [
    "gender",
    "education_type",
    "family_status",
    "housing_type",
    "occupation_type",
    "loan_type",
]

ENGINEERED_NUMERIC_COLUMNS = [
    "asset_ownership_score",
    "asset_gap",
    "income_log",
    "credit_log",
    "annuity_log",
    "goods_log",
    "credit_to_income",
    "annuity_to_income",
    "goods_to_income",
    "credit_to_annuity",
    "goods_to_credit",
    "income_per_family_member",
    "income_per_child",
    "credit_per_family_member",
    "annuity_per_family_member",
    "payment_rate",
    "monthly_income",
    "monthly_payment_share",
    "loan_term_months",
    "loan_burden_score",
    "income_after_annuity",
    "family_dependency_ratio",
    "credit_goods_gap",
    "income_loan_gap",
    "credit_to_goods_ratio",
    "annuity_to_goods_ratio",
    "high_credit_load",
    "high_payment_burden",
    "large_family",
    "has_children",
]

MODEL_NUMERIC_COLUMNS = RAW_NUMERIC_COLUMNS + ENGINEERED_NUMERIC_COLUMNS
MODEL_CATEGORICAL_COLUMNS = RAW_CATEGORICAL_COLUMNS
MODEL_INPUT_COLUMNS = MODEL_NUMERIC_COLUMNS + MODEL_CATEGORICAL_COLUMNS


def _coerce_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype("int64")

    normalized = series.astype("string").str.strip().str.lower()
    mapped = normalized.map(
        {
            "y": 1,
            "yes": 1,
            "true": 1,
            "1": 1,
            "n": 0,
            "no": 0,
            "false": 0,
            "0": 0,
        }
    )
    numeric = pd.to_numeric(series, errors="coerce")
    return mapped.fillna(numeric).fillna(0).astype("int64")


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = pd.to_numeric(denominator, errors="coerce").replace(0, np.nan)
    numerator = pd.to_numeric(numerator, errors="coerce")
    return numerator / denominator


def _coerce_frame(data: Any) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        frame = data.copy()
    elif hasattr(data, "model_dump"):
        frame = pd.DataFrame([data.model_dump()])
    elif hasattr(data, "dict"):
        frame = pd.DataFrame([data.dict()])
    elif isinstance(data, dict):
        if "customer" in data or "application" in data:
            customer = data.get("customer", {}) or {}
            application = data.get("application", {}) or {}
            merged = {**customer, **application}
            frame = pd.DataFrame([merged])
        else:
            frame = pd.DataFrame([data])
    else:
        frame = pd.DataFrame([dict(data)])

    return frame


class ProjectFeatureBuilder(BaseEstimator, TransformerMixin):
    """Turn project payloads into the model feature matrix."""

    def fit(self, X: Any, y: Any = None):  # noqa: D401
        return self

    def transform(self, X: Any) -> pd.DataFrame:
        frame = _coerce_frame(X)
        frame = self._normalize(frame)
        frame = self._engineer(frame)

        for column in MODEL_INPUT_COLUMNS:
            if column not in frame.columns:
                frame[column] = np.nan

        return frame[MODEL_INPUT_COLUMNS]

    def _normalize(self, frame: pd.DataFrame) -> pd.DataFrame:
        normalized = frame.copy()

        for column in ["owns_car", "owns_realty"]:
            if column in normalized.columns:
                normalized[column] = _coerce_bool(normalized[column])
            else:
                normalized[column] = 0

        numeric_defaults = {
            "income_total": np.nan,
            "cnt_children": 0,
            "family_members": 1,
            "credit_amount": np.nan,
            "annuity_amount": np.nan,
            "goods_price": np.nan,
        }
        for column, default in numeric_defaults.items():
            if column in normalized.columns:
                normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
            else:
                normalized[column] = default

        for column in RAW_CATEGORICAL_COLUMNS:
            if column not in normalized.columns:
                normalized[column] = "unknown"
            normalized[column] = (
                normalized[column]
                .astype("string")
                .fillna("unknown")
                .str.strip()
                .replace("", "unknown")
            )

        return normalized

    def _engineer(self, frame: pd.DataFrame) -> pd.DataFrame:
        engineered = frame.copy()

        income = engineered["income_total"].clip(lower=1.0)
        credit = engineered["credit_amount"].clip(lower=1.0)
        annuity = engineered["annuity_amount"].clip(lower=1.0)
        goods = engineered["goods_price"].clip(lower=1.0)
        family_members = engineered["family_members"].clip(lower=1.0)
        children = engineered["cnt_children"].clip(lower=0.0)

        engineered["asset_ownership_score"] = engineered["owns_car"] + engineered["owns_realty"]
        engineered["asset_gap"] = 2 - engineered["asset_ownership_score"]
        engineered["income_log"] = np.log1p(income)
        engineered["credit_log"] = np.log1p(credit)
        engineered["annuity_log"] = np.log1p(annuity)
        engineered["goods_log"] = np.log1p(goods)
        engineered["credit_to_income"] = _safe_divide(credit, income)
        engineered["annuity_to_income"] = _safe_divide(annuity, income)
        engineered["goods_to_income"] = _safe_divide(goods, income)
        engineered["credit_to_annuity"] = _safe_divide(credit, annuity)
        engineered["goods_to_credit"] = _safe_divide(goods, credit)
        engineered["income_per_family_member"] = _safe_divide(income, family_members)
        engineered["income_per_child"] = _safe_divide(income, children + 1)
        engineered["credit_per_family_member"] = _safe_divide(credit, family_members)
        engineered["annuity_per_family_member"] = _safe_divide(annuity, family_members)
        engineered["payment_rate"] = _safe_divide(annuity, credit)
        engineered["monthly_income"] = income / 12.0
        engineered["monthly_payment_share"] = _safe_divide(annuity, engineered["monthly_income"].clip(lower=1.0))
        engineered["loan_term_months"] = _safe_divide(credit, annuity)
        engineered["loan_burden_score"] = engineered["annuity_to_income"] * engineered["credit_to_annuity"]
        engineered["income_after_annuity"] = income - annuity
        engineered["family_dependency_ratio"] = _safe_divide(children, family_members)
        engineered["credit_goods_gap"] = credit - goods
        engineered["income_loan_gap"] = income - credit
        engineered["credit_to_goods_ratio"] = _safe_divide(credit, goods)
        engineered["annuity_to_goods_ratio"] = _safe_divide(annuity, goods)
        engineered["high_credit_load"] = (engineered["credit_to_income"] > 3).astype("int64")
        engineered["high_payment_burden"] = (engineered["annuity_to_income"] > 0.3).astype("int64")
        engineered["large_family"] = (family_members > 4).astype("int64")
        engineered["has_children"] = (children > 0).astype("int64")

        return engineered


def payload_to_frame(payload: Any) -> pd.DataFrame:
    """Convert a prediction payload into a single-row dataframe."""
    return ProjectFeatureBuilder().transform(payload)


def probability_to_risk(probability: float) -> str:
    if probability >= 0.70:
        return "HIGH_RISK"
    if probability >= 0.35:
        return "MEDIUM_RISK"
    return "LOW_RISK"
