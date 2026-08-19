"""Pruebas automáticas de los endpoints FastAPI."""

import csv
import math
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "data" / "simulated_expenses.csv"
client = TestClient(app)


def load_expenses():
    with DATASET_PATH.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


class PredictiveApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expenses = load_expenses()

    def test_health_reports_loaded_model(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["model_loaded"])
        self.assertEqual(body["model_name"], "GradientBoostingRegressor")

    def test_predicts_july_2026_from_simulated_history(self):
        response = client.post(
            "/predict",
            json={"target_period": "2026-07", "expenses": self.expenses},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["target_period"], "2026-07")
        self.assertEqual(body["model_name"], "GradientBoostingRegressor")
        self.assertEqual(len(body["categories"]), 10)
        self.assertTrue(math.isfinite(body["total_projected_amount"]))
        self.assertTrue(all(math.isfinite(item["projected_amount"]) for item in body["categories"]))

    def test_rejects_invalid_category(self):
        invalid = [dict(self.expenses[0]), *self.expenses[1:]]
        invalid[0]["category"] = "Ahorro/Inversión"
        response = client.post("/predict", json={"target_period": "2026-07", "expenses": invalid})
        self.assertEqual(response.status_code, 422)

    def test_rejects_insufficient_history(self):
        insufficient = [
            {"date": "2026-05-10", "category": "Alimentación", "amount": 10000},
            {"date": "2026-06-10", "category": "Alimentación", "amount": 12000},
        ]
        response = client.post(
            "/predict",
            json={"target_period": "2026-07", "expenses": insufficient},
        )
        self.assertEqual(response.status_code, 400)

    def test_rejects_target_or_future_expense(self):
        invalid = [*self.expenses, {"date": "2026-07-01", "category": "Salud", "amount": 15000}]
        response = client.post("/predict", json={"target_period": "2026-07", "expenses": invalid})
        self.assertEqual(response.status_code, 400)

    def test_rejects_empty_expenses(self):
        response = client.post("/predict", json={"target_period": "2026-07", "expenses": []})
        self.assertEqual(response.status_code, 422)

    def test_rejects_nonpositive_amount(self):
        invalid = [dict(self.expenses[0]), *self.expenses[1:]]
        invalid[0]["amount"] = 0
        response = client.post("/predict", json={"target_period": "2026-07", "expenses": invalid})
        self.assertEqual(response.status_code, 422)

    def test_rejects_invalid_date(self):
        invalid = [dict(self.expenses[0]), *self.expenses[1:]]
        invalid[0]["date"] = "2026-02-30"
        response = client.post("/predict", json={"target_period": "2026-07", "expenses": invalid})
        self.assertEqual(response.status_code, 422)

    def test_rejects_invalid_target_period(self):
        response = client.post(
            "/predict",
            json={"target_period": "julio-2026", "expenses": self.expenses},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
