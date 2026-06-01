from __future__ import annotations

import unittest
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.database.database import SessionLocal, engine
from backend.app.database.models import Base, Customer
from backend.app.main import app


class APISmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.db: Session = SessionLocal()
        cls.customer_id = uuid4()
        existing = cls.db.get(Customer, cls.customer_id)
        if not existing:
            customer = Customer(
                customer_id=cls.customer_id,
                gender="F",
                owns_car=False,
                owns_realty=True,
                income_total=90000,
                education_type="Higher education",
                family_status="Married",
                housing_type="House / apartment",
                occupation_type="Laborers",
                cnt_children=1,
                family_members=3,
            )
            cls.db.add(customer)
            cls.db.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.close()

    def test_health(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertIn("model_ready", payload)

    def test_model_info(self) -> None:
        response = self.client.get("/model-info")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("model_name", payload)
        self.assertIn("model_version", payload)

    def test_demo_prediction(self) -> None:
        response = self.client.get("/demo-prediction")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("probability_default", payload)
        self.assertIn("risk_category", payload)

    def test_predict_endpoint(self) -> None:
        response = self.client.post(
            f"/predict/{self.customer_id}",
            json={
                "credit_amount": 227520.0,
                "annuity_amount": 13189.5,
                "goods_price": 180000.0,
                "loan_type": "Cash loans",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("probability_default", payload)
        self.assertIn("risk_category", payload)

    def test_customer_detail_contains_predictions(self) -> None:
        response = self.client.get(f"/customer/{self.customer_id}")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("recent_applications", payload)
        self.assertIn("recent_predictions", payload)


if __name__ == "__main__":
    unittest.main()
