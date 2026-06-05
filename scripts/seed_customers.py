from __future__ import annotations

import argparse
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.database.database import SessionLocal, engine  # noqa: E402
from backend.app.database.models import Base, Customer  # noqa: E402

DATASET_PATH = ROOT / "dataset" / "train.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed the customers table from train.csv")
    parser.add_argument("--rows", type=int, default=200, help="Number of rows to load into customers")
    parser.add_argument(
        "--mode",
        choices=["head", "sample"],
        default="head",
        help="Use the first rows or a deterministic sample from train.csv",
    )
    return parser.parse_args()


def load_source_frame(rows: int, mode: str) -> pd.DataFrame:
    usecols = [
        "SK_ID_CURR",
        "CODE_GENDER",
        "FLAG_OWN_CAR",
        "FLAG_OWN_REALTY",
        "AMT_INCOME_TOTAL",
        "NAME_EDUCATION_TYPE",
        "NAME_FAMILY_STATUS",
        "NAME_HOUSING_TYPE",
        "OCCUPATION_TYPE",
        "CNT_CHILDREN",
        "CNT_FAM_MEMBERS",
    ]
    frame = pd.read_csv(DATASET_PATH, usecols=usecols, low_memory=False)
    if mode == "sample":
        frame = frame.sample(n=min(rows, len(frame)), random_state=42)
    else:
        frame = frame.head(rows)
    return frame


def normalize_text(value: object, fallback: str = "unknown") -> str:
    if pd.isna(value):
        return fallback
    text_value = str(value).strip()
    return text_value if text_value else fallback


def to_bool_flag(value: object) -> bool:
    return str(value).strip().upper() == "Y"


def build_customer_records(frame: pd.DataFrame) -> list[Customer]:
    records: list[Customer] = []
    for _, row in frame.iterrows():
        source_id = str(int(row["SK_ID_CURR"]))
        records.append(
            Customer(
                customer_id=uuid5(NAMESPACE_URL, f"customer:{source_id}"),
                source_customer_id=int(source_id),
                gender=normalize_text(row["CODE_GENDER"], "XNA"),
                owns_car=to_bool_flag(row["FLAG_OWN_CAR"]),
                owns_realty=to_bool_flag(row["FLAG_OWN_REALTY"]),
                income_total=float(row["AMT_INCOME_TOTAL"]),
                education_type=normalize_text(row["NAME_EDUCATION_TYPE"]),
                family_status=normalize_text(row["NAME_FAMILY_STATUS"]),
                housing_type=normalize_text(row["NAME_HOUSING_TYPE"]),
                occupation_type=normalize_text(row["OCCUPATION_TYPE"]),
                cnt_children=int(row["CNT_CHILDREN"] if pd.notna(row["CNT_CHILDREN"]) else 0),
                family_members=int(row["CNT_FAM_MEMBERS"] if pd.notna(row["CNT_FAM_MEMBERS"]) else 1),
            )
        )
    return records


def main() -> None:
    args = parse_args()
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")

    Base.metadata.bind = engine
    source_frame = load_source_frame(args.rows, args.mode)
    customers = build_customer_records(source_frame)

    with SessionLocal() as session:
        for customer in customers:
            session.merge(customer)
        session.commit()

    print(f"Seeded {len(customers)} customer rows into the customers table.")


if __name__ == "__main__":
    main()
