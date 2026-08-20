"""Pruebas automáticas de los endpoints FastAPI de cierre mensual."""

import math
import unittest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
CUTOFF = "2026-08-10"
CURRENT_EXPENSES = [
    {"date": "2026-08-03", "category": "Alimentación", "amount": 25000},
    {"date": "2026-08-10", "category": "Transporte", "amount": 15000},
]
PREVIOUS_EXPENSES = [
    {"date": "2026-07-05", "category": "Alimentación", "amount": 30000},
    {"date": "2026-07-20", "category": "Vivienda", "amount": 120000},
]


def predict(expenses=None, cutoff_date=CUTOFF):
    return client.post(
        "/predict",
        json={"cutoff_date": cutoff_date, "expenses": expenses or CURRENT_EXPENSES},
    )


class PredictiveApiTests(unittest.TestCase):
    def test_health_reports_month_end_model(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["model_loaded"])
        self.assertEqual(body["model_name"], "LinearRegression")
        self.assertEqual(body["sklearn_version"], "1.9.0")
        self.assertEqual(
            body["prediction_objective"],
            "Estimación del gasto al cierre del mes en curso",
        )

    def test_predicts_without_previous_history(self):
        response = predict()
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["cutoff_date"], CUTOFF)
        self.assertEqual(body["projected_period"], "2026-08")
        self.assertEqual(body["model_name"], "LinearRegression")
        self.assertFalse(body["has_previous_month_data"])
        self.assertEqual(body["previous_month_total"], 0)
        self.assertEqual(body["spent_to_date"], 40000)
        self.assertEqual(body["current_month_expenses_used"], 2)
        self.assertEqual(len(body["categories"]), 10)
        self.assertTrue(math.isfinite(body["total_projected_amount"]))

    def test_predicts_with_previous_history(self):
        response = predict([*PREVIOUS_EXPENSES, *CURRENT_EXPENSES])
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["has_previous_month_data"])
        self.assertEqual(body["previous_month_total"], 150000)
        self.assertEqual(body["spent_to_date"], 40000)
        self.assertTrue(math.isfinite(body["total_projected_amount"]))

    def test_returns_ten_finite_category_predictions(self):
        body = predict().json()
        self.assertEqual(len(body["categories"]), 10)
        self.assertTrue(all(math.isfinite(item["projected_amount"]) for item in body["categories"]))
        self.assertTrue(all(math.isfinite(item["raw_prediction"]) for item in body["categories"]))

    def test_rejects_empty_expenses(self):
        response = client.post("/predict", json={"cutoff_date": CUTOFF, "expenses": []})
        self.assertEqual(response.status_code, 422)

    def test_rejects_invalid_category(self):
        invalid = [{**CURRENT_EXPENSES[0], "category": "Ahorro/Inversión"}]
        self.assertEqual(predict(invalid).status_code, 422)

    def test_rejects_nonpositive_amount(self):
        invalid = [{**CURRENT_EXPENSES[0], "amount": 0}]
        self.assertEqual(predict(invalid).status_code, 422)

    def test_rejects_invalid_cutoff_date(self):
        self.assertEqual(predict(cutoff_date="2026-02-30").status_code, 422)

    def test_rejects_invalid_expense_date(self):
        invalid = [{**CURRENT_EXPENSES[0], "date": "2026-02-30"}]
        self.assertEqual(predict(invalid).status_code, 422)

    def test_rejects_expense_after_cutoff(self):
        invalid = [
            *CURRENT_EXPENSES,
            {"date": "2026-08-11", "category": "Salud", "amount": 10000},
        ]
        response = predict(invalid)
        self.assertEqual(response.status_code, 400)
        self.assertIn("posterior", response.json()["detail"])

    def test_rejects_when_current_month_has_no_expenses(self):
        response = predict(PREVIOUS_EXPENSES)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "No existen gastos registrados en el mes en curso para generar una proyección.",
        )


if __name__ == "__main__":
    unittest.main()
