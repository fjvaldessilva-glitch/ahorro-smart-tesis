"""Genera variables conductuales seguras respecto de la fecha de corte para T40.2.1."""

import calendar
import csv
import json
import math
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import median


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "simulated_expenses.csv"
DEVELOPMENT_END = date(2025, 12, 31)
CUTOFF_DAYS = (5, 10, 15, 20, 25)
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
FEATURE_NAMES = (
    "spend_last_7_days",
    "transactions_last_7_days",
    "median_transaction_amount",
    "active_spending_days",
    "days_since_last_expense",
    "has_category_expense_history",
    "previous_month_comparable_spend",
    "previous_month_comparable_transactions",
    "category_previous_month_comparable_spend",
)


def _as_date(value):
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def _normalized_expenses(movements, cutoff_date):
    """Conserva solo gastos válidos conocidos al corte; nunca ingresos ni fechas futuras."""
    normalized = []
    for movement in movements:
        if movement.get("type", "Gasto") != "Gasto":
            continue
        movement_date = _as_date(movement["date"])
        amount = float(movement["amount"])
        if movement_date > cutoff_date:
            continue
        if movement_date.year >= 2026:
            continue
        if movement["category"] not in CATEGORIES or not math.isfinite(amount) or amount <= 0:
            raise ValueError("El movimiento contiene una categoría o monto no válido.")
        normalized.append({"date": movement_date, "category": movement["category"], "amount": amount})
    return sorted(normalized, key=lambda item: (item["date"], item["category"], item["amount"]))


def _previous_month_bounds(cutoff_date):
    previous_end = cutoff_date.replace(day=1) - timedelta(days=1)
    equivalent_day = min(cutoff_date.day, previous_end.day)
    return previous_end.replace(day=1), previous_end.replace(day=equivalent_day)


def compute_behavioral_features(movements, category, cutoff_date):
    """Calcula las ocho variables para una fila categoría-fecha de corte."""
    cutoff_date = _as_date(cutoff_date)
    if cutoff_date.year >= 2026:
        raise ValueError("T40.2.1 solo admite fechas de corte anteriores a 2026.")
    if category not in CATEGORIES:
        raise ValueError("La categoría no pertenece al catálogo oficial.")

    expenses = _normalized_expenses(movements, cutoff_date)
    current_month_start = cutoff_date.replace(day=1)
    last_7_start = cutoff_date - timedelta(days=6)
    previous_start, previous_end = _previous_month_bounds(cutoff_date)

    last_7 = [item for item in expenses if last_7_start <= item["date"] <= cutoff_date]
    current_month = [item for item in expenses if current_month_start <= item["date"] <= cutoff_date]
    current_category = [item for item in current_month if item["category"] == category]
    historical_category = [item for item in expenses if item["category"] == category]
    comparable_previous = [item for item in expenses if previous_start <= item["date"] <= previous_end]
    comparable_category = [item for item in comparable_previous if item["category"] == category]

    values = {
        "spend_last_7_days": sum(item["amount"] for item in last_7),
        "transactions_last_7_days": len(last_7),
        "median_transaction_amount": median(item["amount"] for item in current_category)
        if current_category else 0.0,
        "active_spending_days": len({item["date"] for item in current_month}),
        "days_since_last_expense": (cutoff_date - historical_category[-1]["date"]).days
        if historical_category else cutoff_date.day,
        "has_category_expense_history": int(bool(historical_category)),
        "previous_month_comparable_spend": sum(item["amount"] for item in comparable_previous),
        "previous_month_comparable_transactions": len(comparable_previous),
        "category_previous_month_comparable_spend": sum(item["amount"] for item in comparable_category),
    }
    values = {
        name: round(float(value), 4) if isinstance(value, float) else value
        for name, value in values.items()
    }
    if tuple(values) != FEATURE_NAMES or any(
        isinstance(value, float) and not math.isfinite(value) for value in values.values()
    ):
        raise ValueError("Las variables generadas no son válidas o finitas.")
    return values


def load_development_expenses(path=DATA_PATH):
    expenses = []
    with Path(path).open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames != ["date", "category", "amount"]:
            raise ValueError("El dataset no conserva la estructura validada en T38.")
        for row in reader:
            movement_date = _as_date(row["date"])
            if movement_date <= DEVELOPMENT_END:
                expenses.append({**row, "date": movement_date, "amount": float(row["amount"]), "type": "Gasto"})
    return expenses


def build_enriched_feature_rows(expenses=None):
    """Construye en memoria filas de features, sin objetivos ni entrenamiento."""
    expenses = load_development_expenses() if expenses is None else list(expenses)
    development = [item for item in expenses if _as_date(item["date"]) <= DEVELOPMENT_END]
    by_period = defaultdict(list)
    for expense in development:
        if expense.get("type", "Gasto") == "Gasto":
            by_period[_as_date(expense["date"]).strftime("%Y-%m")].append(expense)

    rows = []
    for period in sorted(by_period):
        year, month = map(int, period.split("-"))
        days_in_month = calendar.monthrange(year, month)[1]
        first_expense_day = min(_as_date(item["date"]).day for item in by_period[period])
        cutoff_days = [day for day in sorted({first_expense_day, *CUTOFF_DAYS}) if day < days_in_month]
        for cutoff_day in cutoff_days:
            cutoff = date(year, month, cutoff_day)
            if not any(_as_date(item["date"]) <= cutoff for item in by_period[period]):
                continue
            for category in CATEGORIES:
                rows.append({
                    "scenario_id": cutoff.isoformat(),
                    "period": period,
                    "category": category,
                    **compute_behavioral_features(development, category, cutoff),
                })
    return rows


def main():
    rows = build_enriched_feature_rows()
    print(json.dumps({"row_count": len(rows), "example_row": rows[0]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
