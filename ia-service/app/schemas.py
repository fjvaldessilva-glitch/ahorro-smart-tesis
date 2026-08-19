"""Esquemas de entrada y salida del servicio predictivo."""

import re
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


ExpenseCategory = Literal[
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
]


class HistoricalExpense(BaseModel):
    date: date
    category: ExpenseCategory
    amount: float = Field(gt=0)


class PredictionRequest(BaseModel):
    target_period: str
    expenses: list[HistoricalExpense] = Field(min_length=1)

    @field_validator("target_period")
    @classmethod
    def validate_target_period(cls, value):
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
            raise ValueError("target_period debe utilizar el formato YYYY-MM.")
        return value


class CategoryProjection(BaseModel):
    category: ExpenseCategory
    projected_amount: float
    raw_prediction: float
    nonnegative_adjustment: bool


class PredictionResponse(BaseModel):
    target_period: str
    model_name: str
    categories: list[CategoryProjection]
    total_projected_amount: float
    historical_months_used: int
