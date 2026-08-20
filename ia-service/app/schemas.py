"""Esquemas de entrada y salida del servicio predictivo."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


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
    cutoff_date: date
    expenses: list[HistoricalExpense] = Field(min_length=1)


class CategoryProjection(BaseModel):
    category: ExpenseCategory
    projected_amount: float
    raw_prediction: float
    nonnegative_adjustment: bool


class PredictionResponse(BaseModel):
    cutoff_date: date
    projected_period: str
    model_name: str
    prediction_objective: str
    categories: list[CategoryProjection]
    spent_to_date: float
    total_projected_amount: float
    previous_month_total: float
    has_previous_month_data: bool
    current_month_expenses_used: int
