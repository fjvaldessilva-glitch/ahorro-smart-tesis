"""Carga del modelo y preparación consistente de variables de inferencia."""

import json
import logging
import math
from collections import defaultdict
from pathlib import Path

import joblib


LOGGER = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "expense_forecast_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"
TRAINING_START_PERIOD = "2024-01"
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


def period_to_index(period, origin=TRAINING_START_PERIOD):
    year, month = map(int, period.split("-"))
    origin_year, origin_month = map(int, origin.split("-"))
    return (year - origin_year) * 12 + month - origin_month


def shift_period(period, offset):
    year, month = map(int, period.split("-"))
    absolute_month = year * 12 + month - 1 + offset
    return f"{absolute_month // 12:04d}-{absolute_month % 12 + 1:02d}"


def month_sequence(start_period, end_period):
    start_index = period_to_index(start_period)
    end_index = period_to_index(end_period)
    if end_index < start_index:
        return []
    return [shift_period(start_period, offset) for offset in range(end_index - start_index + 1)]


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
            self.model = joblib.load(MODEL_PATH)
            self.metadata = metadata
        except Exception as error:  # El estado queda disponible para /health sin exponer un traceback.
            self.load_error = str(error)
            LOGGER.exception("No fue posible cargar los artefactos predictivos.")

    def _prepare_features(self, target_period, expenses):
        target_index = period_to_index(target_period)
        if target_index < 3:
            raise ValueError("El período objetivo no permite construir tres meses previos compatibles con el modelo.")

        monthly_amounts = defaultdict(float)
        observed_periods = set()
        for expense in expenses:
            expense_period = expense.date.strftime("%Y-%m")
            if expense_period >= target_period:
                raise ValueError("El historial contiene movimientos del período objetivo o posteriores.")
            if expense_period < TRAINING_START_PERIOD:
                raise ValueError("El historial contiene movimientos anteriores al período base del modelo.")
            monthly_amounts[(expense_period, expense.category)] += expense.amount
            observed_periods.add(expense_period)

        required_periods = [shift_period(target_period, offset) for offset in (-3, -2, -1)]
        if not set(required_periods).issubset(observed_periods):
            raise ValueError("Se requieren movimientos históricos en cada uno de los tres meses previos al objetivo.")

        earliest_period = min(observed_periods)
        last_historical_period = shift_period(target_period, -1)
        historical_months = month_sequence(earliest_period, last_historical_period)
        target_month = int(target_period[5:7])
        features = []
        for category in CATEGORIES:
            previous_values = [monthly_amounts[(period, category)] for period in required_periods]
            features.append(
                [
                    category,
                    target_month,
                    target_index,
                    previous_values[2],
                    previous_values[1],
                    previous_values[0],
                    sum(previous_values) / 3,
                    math.sin(2 * math.pi * target_month / 12),
                    math.cos(2 * math.pi * target_month / 12),
                ]
            )
        return features, len(historical_months)

    def predict(self, target_period, expenses):
        if not self.is_loaded:
            raise RuntimeError("El modelo predictivo no está disponible.")
        features, historical_months_used = self._prepare_features(target_period, expenses)
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
            "target_period": target_period,
            "model_name": self.model_name,
            "categories": projections,
            "total_projected_amount": round(sum(item["projected_amount"] for item in projections), 2),
            "historical_months_used": historical_months_used,
        }


predictor = Predictor()
