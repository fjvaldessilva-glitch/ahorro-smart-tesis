"""Genera gastos financieros completamente simulados para Ahorro Smart."""

import csv
import random
from calendar import monthrange
from datetime import date
from pathlib import Path


SIMULATION_SEED = 2026
START_DATE = date(2024, 1, 1)
END_DATE = date(2026, 6, 30)
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
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "simulated_expenses.csv"


def iter_months(start: date, end: date):
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        yield year, month
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1


def add_expense(rows, rng, year, month, category, amount, day=None):
    last_day = monthrange(year, month)[1]
    selected_day = day if day is not None else rng.randint(1, last_day)
    rows.append(
        {
            "date": date(year, month, selected_day).isoformat(),
            "category": category,
            "amount": int(round(max(1, amount))),
        }
    )


def generate_expenses():
    rng = random.Random(SIMULATION_SEED)
    rows = []

    for year, month in iter_months(START_DATE, END_DATE):
        # Gastos recurrentes mensuales.
        add_expense(rows, rng, year, month, "Vivienda", rng.gauss(420_000, 15_000), 5)
        add_expense(rows, rng, year, month, "Servicios básicos", rng.gauss(92_000, 14_000), 10)
        add_expense(rows, rng, year, month, "Pago de deudas y créditos", rng.gauss(135_000, 9_000), 15)

        # Gastos variables frecuentes.
        for _ in range(rng.randint(8, 13)):
            add_expense(rows, rng, year, month, "Alimentación", rng.gauss(32_000, 9_000))
        for _ in range(rng.randint(5, 9)):
            add_expense(rows, rng, year, month, "Transporte", rng.gauss(19_000, 6_000))
        for _ in range(rng.randint(1, 4)):
            add_expense(rows, rng, year, month, "Entretenimiento", rng.gauss(35_000, 14_000))

        # Gastos ocasionales o periódicos.
        if rng.random() < 0.55:
            add_expense(rows, rng, year, month, "Salud", rng.gauss(48_000, 20_000))
        if month in (3, 4, 7, 8) or rng.random() < 0.25:
            add_expense(rows, rng, year, month, "Educación", rng.gauss(75_000, 25_000))
        if rng.random() < 0.65:
            add_expense(rows, rng, year, month, "Mascotas", rng.gauss(30_000, 11_000))
        if rng.random() < 0.45:
            add_expense(rows, rng, year, month, "Otros gastos", rng.gauss(42_000, 18_000))

    # Asegura que el historial cubra exactamente los límites comprometidos.
    rows.append({"date": START_DATE.isoformat(), "category": "Otros gastos", "amount": 18_000})
    rows.append({"date": END_DATE.isoformat(), "category": "Otros gastos", "amount": 21_000})
    rows.sort(key=lambda row: (row["date"], row["category"], row["amount"]))
    return rows


def main():
    rows = generate_expenses()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=("date", "category", "amount"))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Dataset simulado generado: {DATA_PATH} ({len(rows)} movimientos)")


if __name__ == "__main__":
    main()
