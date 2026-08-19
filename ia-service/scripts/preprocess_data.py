"""Valida y agrega mensualmente los gastos simulados de Ahorro Smart."""

import csv
import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path


SIMULATION_SEED = 2026
EXPECTED_START_DATE = date(2024, 1, 1)
EXPECTED_END_DATE = date(2026, 6, 30)
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
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_PATH = DATA_DIR / "simulated_expenses.csv"
PROCESSED_PATH = DATA_DIR / "processed_monthly_expenses.csv"
SUMMARY_PATH = DATA_DIR / "dataset_summary.json"


def read_and_validate():
    counters = {
        "invalid_dates": 0,
        "invalid_categories": 0,
        "invalid_amounts": 0,
        "empty_values": 0,
    }
    valid_rows = []

    with RAW_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames != ["date", "category", "amount"]:
            raise ValueError("El dataset debe contener únicamente date, category y amount.")

        for line_number, row in enumerate(reader, start=2):
            values = [row.get(field, "").strip() for field in reader.fieldnames]
            if any(not value for value in values):
                counters["empty_values"] += 1

            parsed_date = None
            try:
                parsed_date = date.fromisoformat(values[0])
            except ValueError:
                counters["invalid_dates"] += 1

            if values[1] not in CATEGORIES:
                counters["invalid_categories"] += 1

            amount = None
            try:
                amount = float(values[2])
                if not math.isfinite(amount) or amount <= 0:
                    counters["invalid_amounts"] += 1
            except ValueError:
                counters["invalid_amounts"] += 1

            if parsed_date and values[1] in CATEGORIES and amount and math.isfinite(amount):
                valid_rows.append((parsed_date, values[1], amount))

    if any(counters.values()):
        details = ", ".join(f"{key}={value}" for key, value in counters.items())
        raise ValueError(f"Procesamiento detenido por datos inválidos: {details}")
    if not valid_rows:
        raise ValueError("El dataset no contiene movimientos para procesar.")

    valid_rows.sort(key=lambda row: (row[0], row[1], row[2]))
    if valid_rows[0][0] != EXPECTED_START_DATE or valid_rows[-1][0] != EXPECTED_END_DATE:
        raise ValueError("El dataset no cubre exactamente el período comprometido.")
    return valid_rows, counters


def aggregate_monthly(rows):
    aggregates = defaultdict(lambda: {"monthly_amount": 0.0, "transaction_count": 0})
    for expense_date, category, amount in rows:
        key = (expense_date.year, expense_date.month, category)
        aggregates[key]["monthly_amount"] += amount
        aggregates[key]["transaction_count"] += 1

    processed = []
    for (year, month, category), values in sorted(aggregates.items()):
        monthly_amount = round(values["monthly_amount"], 2)
        if monthly_amount <= 0:
            raise ValueError("Se detectó un total mensual menor o igual a cero.")
        processed.append(
            {
                "year": year,
                "month": month,
                "period": f"{year:04d}-{month:02d}",
                "category": category,
                "monthly_amount": monthly_amount,
                "transaction_count": values["transaction_count"],
            }
        )
    return processed


def main():
    rows, counters = read_and_validate()
    processed = aggregate_monthly(rows)

    with PROCESSED_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        fields = ("year", "month", "period", "category", "monthly_amount", "transaction_count")
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(processed)

    summary = {
        "simulation_seed": SIMULATION_SEED,
        "start_date": rows[0][0].isoformat(),
        "end_date": rows[-1][0].isoformat(),
        "total_transactions": len(rows),
        "total_categories": len({row[1] for row in rows}),
        "categories": list(CATEGORIES),
        "total_amount": round(sum(row[2] for row in rows), 2),
        **counters,
        "raw_rows": len(rows),
        "processed_rows": len(processed),
    }
    with SUMMARY_PATH.open("w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, ensure_ascii=False, indent=2)
        json_file.write("\n")
    print(f"Dataset validado y procesado: {PROCESSED_PATH} ({len(processed)} filas)")


if __name__ == "__main__":
    main()
