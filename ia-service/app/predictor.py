"""Carga del modelo de cierre mensual y preparación consistente de variables."""

import calendar
import json
import logging
import math
from collections import defaultdict
from pathlib import Path

import joblib


LOGGER = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "month_end_forecast_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "month_end_model_metadata.json"
CATEGORIES = (
    "Alimentación",
    "Transporte",
    "Vivienda",
    "Servicios básicos",
    "Salud",
    "Educación",
    "Pago de deudas y créditos",
    "Entretenimiento",
    "Mascotas",
    "Otros gastos",
)
FEATURES = (
    "category", "month", "day_of_month", "days_in_month", "month_progress",
    "category_spend_to_date", "category_transactions_to_date", "total_spend_to_date",
    "total_transactions_to_date", "category_average_transaction_to_date",
    "overall_average_transaction_to_date", "month_sin", "month_cos",
    "previous_month_category_total", "previous_month_total", "has_previous_month_data",
)


def shift_period(period, offset):
    year, month = map(int, period.split("-"))
    absolute_month = year * 12 + month - 1 + offset
    return f"{absolute_month // 12:04d}-{absolute_month % 12 + 1:02d}"


class Predictor:
    def __init__(self):
        self.model = None
        self.metadata = None
        self.load_error = None
        self._load_artifacts()

    @property
    def is_loaded(self):
        return self.model is not None and self.metadata is not None

    @property
    def model_name(self):
        return self.metadata.get("model_name") if self.metadata else None

    @property
    def sklearn_version(self):
        return self.metadata.get("sklearn_version") if self.metadata else None

    @property
    def prediction_objective(self):
        return self.metadata.get("prediction_objective") if self.metadata else None

    def _load_artifacts(self):
        try:
            if not MODEL_PATH.is_file():
                raise FileNotFoundError(f"No existe el modelo: {MODEL_PATH}")
            if not METADATA_PATH.is_file():
                raise FileNotFoundError(f"No existen los metadatos: {METADATA_PATH}")
            with METADATA_PATH.open(encoding="utf-8") as metadata_file:
                metadata = json.load(metadata_file)
            if tuple(metadata.get("categories", ())) != CATEGORIES:
                raise ValueError("Las categorías del modelo no coinciden con el catálogo oficial.")
            if tuple(metadata.get("input_features", ())) != FEATURES:
                raise ValueError("Las variables del modelo no coinciden con la inferencia del servicio.")
            if metadata.get("uses_budget") is not False:
                raise ValueError("El artefacto no declara correctamente la exclusión del presupuesto.")
            self.model = joblib.load(MODEL_PATH)
            self.metadata = metadata
        except Exception as error:  # El estado queda disponible para /health sin exponer un traceback.
            self.load_error = str(error)
            LOGGER.exception("No fue posible cargar los artefactos predictivos.")

    def _prepare_features(self, cutoff_date, expenses):
        current_period = cutoff_date.strftime("%Y-%m")
        previous = shift_period(current_period, -1)
        current_by_category = defaultdict(list)
        previous_by_category = defaultdict(float)
        current_expenses = []
        previous_month_total = 0.0
        has_previous_month_data = False
        for expense in expenses:
            expense_period = expense.date.strftime("%Y-%m")
            if expense.date > cutoff_date:
                raise ValueError("Los gastos no pueden tener una fecha posterior a cutoff_date.")
            if expense_period == current_period:
                current_expenses.append(expense)
                current_by_category[expense.category].append(expense.amount)
            elif expense_period == previous:
                has_previous_month_data = True
                previous_by_category[expense.category] += expense.amount
                previous_month_total += expense.amount

        if not current_expenses:
            raise ValueError(
                "No existen gastos registrados en el mes en curso para generar una proyección."
            )

        month = cutoff_date.month
        days_in_month = calendar.monthrange(cutoff_date.year, month)[1]
        month_progress = cutoff_date.day / days_in_month
        spent_to_date = sum(expense.amount for expense in current_expenses)
        total_transactions = len(current_expenses)
        features = []
        for category in CATEGORIES:
            category_amounts = current_by_category[category]
            category_spend = sum(category_amounts)
            category_transactions = len(category_amounts)
            features.append(
                [
                    category, month, cutoff_date.day, days_in_month, month_progress,
                    category_spend, category_transactions, spent_to_date, total_transactions,
                    category_spend / category_transactions if category_transactions else 0.0,
                    spent_to_date / total_transactions,
                    math.sin(2 * math.pi * month / 12), math.cos(2 * math.pi * month / 12),
                    previous_by_category[category] if has_previous_month_data else 0.0,
                    previous_month_total if has_previous_month_data else 0.0,
                    int(has_previous_month_data),
                ]
            )
        return features, {
            "projected_period": current_period,
            "spent_to_date": spent_to_date,
            "previous_month_total": previous_month_total if has_previous_month_data else 0.0,
            "has_previous_month_data": has_previous_month_data,
            "current_month_expenses_used": total_transactions,
        }

    def predict(self, cutoff_date, expenses):
        if not self.is_loaded:
            raise RuntimeError("El modelo predictivo no está disponible.")
        features, context = self._prepare_features(cutoff_date, expenses)
        raw_predictions = self.model.predict(features)
        projections = []
        for category, raw_value in zip(CATEGORIES, raw_predictions):
            raw_prediction = float(raw_value)
            if not math.isfinite(raw_prediction):
                raise RuntimeError("El modelo produjo una predicción no finita.")
            adjusted = raw_prediction < 0
            projected_amount = max(0.0, raw_prediction)
            projections.append(
                {
                    "category": category,
                    "projected_amount": round(projected_amount, 2),
                    "raw_prediction": round(raw_prediction, 2),
                    "nonnegative_adjustment": adjusted,
                }
            )
        return {
            "cutoff_date": cutoff_date,
            "projected_period": context["projected_period"],
            "model_name": self.model_name,
            "prediction_objective": self.prediction_objective,
            "categories": projections,
            "spent_to_date": round(context["spent_to_date"], 2),
            "total_projected_amount": round(sum(item["projected_amount"] for item in projections), 2),
            "previous_month_total": round(context["previous_month_total"], 2),
            "has_previous_month_data": context["has_previous_month_data"],
            "current_month_expenses_used": context["current_month_expenses_used"],
        }


predictor = Predictor()
