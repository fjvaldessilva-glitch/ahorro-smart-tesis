"""Analiza patrones descriptivos en los gastos simulados de Ahorro Smart."""

import csv
import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path
from statistics import mean, median, pstdev


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "simulated_expenses.csv"
PROCESSED_PATH = BASE_DIR / "data" / "processed_monthly_expenses.csv"
ANALYSIS_DIR = BASE_DIR / "analysis"
SUMMARY_PATH = ANALYSIS_DIR / "patterns_summary.json"
REPORT_PATH = ANALYSIS_DIR / "patterns_report.md"


def rounded(value, digits=2):
    result = round(float(value), digits)
    if not math.isfinite(result):
        raise ValueError("El análisis produjo un valor numérico no finito.")
    return result


def load_raw_data():
    rows = []
    with RAW_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames != ["date", "category", "amount"]:
            raise ValueError("Las columnas del dataset original no corresponden a T38.")
        for row in reader:
            rows.append(
                {
                    "date": date.fromisoformat(row["date"]),
                    "category": row["category"],
                    "amount": float(row["amount"]),
                }
            )
    return rows


def load_processed_data():
    rows = []
    expected = ["year", "month", "period", "category", "monthly_amount", "transaction_count"]
    with PROCESSED_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames != expected:
            raise ValueError("Las columnas del dataset procesado no corresponden a T38.")
        for row in reader:
            rows.append(
                {
                    "year": int(row["year"]),
                    "month": int(row["month"]),
                    "period": row["period"],
                    "category": row["category"],
                    "monthly_amount": float(row["monthly_amount"]),
                    "transaction_count": int(row["transaction_count"]),
                }
            )
    return rows


def month_sequence(start_date, end_date):
    periods = []
    year, month = start_date.year, start_date.month
    while (year, month) <= (end_date.year, end_date.month):
        periods.append(f"{year:04d}-{month:02d}")
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return periods


def linear_trend(values):
    count = len(values)
    if count < 2:
        return {"slope_per_month": 0.0, "direction": "sin tendencia suficiente"}
    x_mean = (count - 1) / 2
    y_mean = mean(values)
    denominator = sum((index - x_mean) ** 2 for index in range(count))
    slope = sum((index - x_mean) * (value - y_mean) for index, value in enumerate(values)) / denominator
    tolerance = y_mean * 0.001
    direction = "ascendente" if slope > tolerance else "descendente" if slope < -tolerance else "estable"
    return {"slope_per_month": rounded(slope), "direction": direction}


def calculate_metrics(raw_rows, processed_rows):
    start_date = min(row["date"] for row in raw_rows)
    end_date = max(row["date"] for row in raw_rows)
    periods = month_sequence(start_date, end_date)
    total_months = len(periods)
    total_amount = sum(row["amount"] for row in raw_rows)

    raw_by_category = defaultdict(list)
    processed_by_category = defaultdict(list)
    monthly_totals = {period: 0.0 for period in periods}
    for row in raw_rows:
        raw_by_category[row["category"]].append(row)
    for row in processed_rows:
        processed_by_category[row["category"]].append(row)
        monthly_totals[row["period"]] += row["monthly_amount"]

    category_metrics = []
    for category in sorted(raw_by_category):
        raw_category = raw_by_category[category]
        monthly_category = processed_by_category[category]
        amounts = [row["monthly_amount"] for row in monthly_category]
        category_total = sum(row["amount"] for row in raw_category)
        average_amount = mean(amounts)
        deviation = pstdev(amounts) if len(amounts) > 1 else 0.0
        category_metrics.append(
            {
                "category": category,
                "total_amount": rounded(category_total),
                "total_transactions": len(raw_category),
                "months_present": len(monthly_category),
                "coverage_percentage": rounded(len(monthly_category) / total_months * 100),
                "average_monthly_amount": rounded(average_amount),
                "median_monthly_amount": rounded(median(amounts)),
                "standard_deviation_monthly_amount": rounded(deviation),
                "coefficient_of_variation": rounded(deviation / average_amount, 4) if average_amount else 0.0,
                "average_transactions_per_month": rounded(len(raw_category) / total_months),
                "percentage_of_total_spending": rounded(category_total / total_amount * 100, 4),
            }
        )

    monthly_values = [monthly_totals[period] for period in periods]
    calendar_month_values = defaultdict(list)
    for period, amount in monthly_totals.items():
        calendar_month_values[int(period[5:7])].append(amount)
    calendar_averages = {
        f"{month:02d}": rounded(mean(values))
        for month, values in sorted(calendar_month_values.items())
    }
    trend = linear_trend(monthly_values)
    monthly_metrics = {
        "evolution": [
            {"period": period, "total_amount": rounded(monthly_totals[period])}
            for period in periods
        ],
        "average_total_monthly_amount": rounded(mean(monthly_values)),
        "median_total_monthly_amount": rounded(median(monthly_values)),
        "standard_deviation_total_monthly_amount": rounded(pstdev(monthly_values)),
        "calendar_month_average": calendar_averages,
        "trend": trend,
        "highest_frequency_category": max(category_metrics, key=lambda item: item["total_transactions"])["category"],
        "highest_spending_share_category": max(category_metrics, key=lambda item: item["total_amount"])["category"],
        "recurrent_categories": [
            item["category"] for item in category_metrics if item["coverage_percentage"] >= 90
        ],
    }
    return start_date, end_date, total_months, total_amount, category_metrics, monthly_metrics


def select_patterns(category_metrics, analysis_period):
    dominant = max(category_metrics, key=lambda item: item["percentage_of_total_spending"])
    frequent = max(category_metrics, key=lambda item: item["total_transactions"])
    stable_candidates = [
        item
        for item in category_metrics
        if item["coverage_percentage"] >= 90 and item["category"] != dominant["category"]
    ]
    stable = min(stable_candidates or category_metrics, key=lambda item: item["coefficient_of_variation"])

    return [
        {
            "id": "P01",
            "name": f"Participación monetaria dominante de {dominant['category']}",
            "description": "Categoría con la mayor proporción del gasto total del escenario simulado.",
            "categories": [dominant["category"]],
            "period": analysis_period,
            "evidence": {
                "percentage_of_total_spending": dominant["percentage_of_total_spending"],
                "total_amount": dominant["total_amount"],
                "coverage_percentage": dominant["coverage_percentage"],
            },
            "technical_interpretation": "La categoría concentra la mayor participación monetaria observada; se describe una asociación cuantitativa, no una causa.",
            "predictive_relevance": "Su peso relativo justifica considerar categoría, período y monto al evaluar posteriormente técnicas predictivas.",
        },
        {
            "id": "P02",
            "name": f"Alta frecuencia de transacciones en {frequent['category']}",
            "description": "Categoría con la mayor cantidad de movimientos durante el período analizado.",
            "categories": [frequent["category"]],
            "period": analysis_period,
            "evidence": {
                "total_transactions": frequent["total_transactions"],
                "average_transactions_per_month": frequent["average_transactions_per_month"],
                "coverage_percentage": frequent["coverage_percentage"],
            },
            "technical_interpretation": "La recurrencia transaccional es superior a la de las demás categorías del dataset simulado.",
            "predictive_relevance": "La frecuencia aporta observaciones repetidas para estudiar la evolución temporal futura de los gastos.",
        },
        {
            "id": "P03",
            "name": f"Recurrencia y estabilidad relativa en {stable['category']}",
            "description": "Categoría recurrente con la menor variabilidad relativa entre las alternativas de alta cobertura no seleccionadas como dominantes.",
            "categories": [stable["category"]],
            "period": analysis_period,
            "evidence": {
                "coverage_percentage": stable["coverage_percentage"],
                "average_monthly_amount": stable["average_monthly_amount"],
                "standard_deviation_monthly_amount": stable["standard_deviation_monthly_amount"],
                "coefficient_of_variation": stable["coefficient_of_variation"],
            },
            "technical_interpretation": "La presencia mensual elevada y la dispersión relativa reducida muestran un comportamiento comparativamente estable.",
            "predictive_relevance": "La regularidad puede servir como referencia al comparar posteriormente técnicas para estimar gastos futuros.",
        },
    ]


def currency(value):
    return f"${value:,.0f}".replace(",", ".")


def build_report(summary):
    metrics = summary["category_metrics"]
    monthly = summary["monthly_total_metrics"]
    metric_rows = "\n".join(
        f"| {item['category']} | {currency(item['total_amount'])} | {item['total_transactions']} | "
        f"{item['coverage_percentage']:.2f} % | {currency(item['average_monthly_amount'])} | "
        f"{item['coefficient_of_variation']:.4f} | {item['percentage_of_total_spending']:.4f} % |"
        for item in metrics
    )
    pattern_sections = []
    for pattern in summary["selected_patterns"]:
        evidence = "\n".join(f"- `{key}`: {value}" for key, value in pattern["evidence"].items())
        pattern_sections.append(
            f"### {pattern['id']} - {pattern['name']}\n\n"
            f"{pattern['description']}\n\n"
            f"Categoría involucrada: {', '.join(pattern['categories'])}.  \n"
            f"Período: {pattern['period']}.\n\n"
            f"**Evidencia cuantitativa**\n\n{evidence}\n\n"
            f"**Interpretación técnica:** {pattern['technical_interpretation']}\n\n"
            f"**Relevancia predictiva:** {pattern['predictive_relevance']}"
        )

    return f"""# Análisis de patrones habituales de consumo

## 1. Propósito

Este análisis descriptivo utiliza exclusivamente los datos 100 % simulados preparados y validados en T38. Su propósito es identificar patrones cuantificables del escenario sintético, sin interpretar psicológicamente al usuario, afirmar causalidad ni entregar asesoría financiera.

## 2. Fuente de datos

- Período: {summary['analysis_period']} ({summary['total_months']} meses).
- Movimientos: {summary['total_transactions']}.
- Categorías oficiales: {len(metrics)}.
- Monto simulado total: {currency(summary['total_amount'])}.
- Fuentes: `processed_monthly_expenses.csv` y, para frecuencias, `simulated_expenses.csv`.
- Carácter de los datos: completamente sintético, sin información personal, bancaria o financiera real.

## 3. Método de análisis

Por categoría se calcularon monto y transacciones totales, meses con presencia, cobertura, promedio, mediana y desviación estándar mensual, coeficiente de variación, transacciones promedio mensuales y participación en el gasto total. También se calculó la evolución mensual, los promedios por mes calendario y una tendencia descriptiva mediante regresión lineal simple implementada con Python estándar.

## 4. Resultados generales

| Categoría | Monto total | Transacciones | Cobertura | Promedio mensual | Coeficiente de variación | Participación |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{metric_rows}

- Categoría de mayor frecuencia: **{monthly['highest_frequency_category']}**.
- Categoría de mayor participación monetaria: **{monthly['highest_spending_share_category']}**.
- Promedio de gasto total mensual: **{currency(monthly['average_total_monthly_amount'])}**.
- Tendencia lineal descriptiva: **{monthly['trend']['direction']}**, con pendiente de **{currency(monthly['trend']['slope_per_month'])} por mes**.

## 5. Patrones identificados

{(chr(10) * 2).join(pattern_sections)}

## 6. Relación con las variables de la ERS

- **VE-01, monto del gasto:** sustenta totales, promedios, dispersión, participación y evolución monetaria.
- **VE-02, fecha del gasto:** permite ordenar, agrupar por mes, medir cobertura y evaluar tendencias temporales.
- **VE-03, categoría del gasto:** permite comparar frecuencia, recurrencia, estabilidad y participación entre categorías.

Todas las métricas derivan de estas variables y conservan su trazabilidad.

## 7. Utilidad para el modelo predictivo

Los patrones aportan antecedentes empíricos sobre peso monetario, frecuencia y estabilidad temporal que deberán considerarse en una microtarea posterior al evaluar y seleccionar una técnica predictiva. Este análisis no selecciona algoritmos ni entrena modelos.

## 8. Limitaciones

- Los datos son simulados y corresponden a un período controlado.
- Los patrones representan exclusivamente el escenario sintético analizado.
- No se garantiza que usuarios reales presenten el mismo comportamiento.
- Las asociaciones observadas no demuestran causalidad.
- El análisis no constituye asesoría financiera.
"""


def main():
    raw_rows = load_raw_data()
    processed_rows = load_processed_data()
    start_date, end_date, total_months, total_amount, category_metrics, monthly_metrics = calculate_metrics(
        raw_rows, processed_rows
    )
    analysis_period = f"{start_date.isoformat()} a {end_date.isoformat()}"
    selected_patterns = select_patterns(category_metrics, analysis_period)
    if len(selected_patterns) < 3:
        raise ValueError("El análisis no encontró al menos tres patrones respaldados.")

    summary = {
        "analysis_period": analysis_period,
        "total_months": total_months,
        "total_transactions": len(raw_rows),
        "total_amount": rounded(total_amount),
        "category_metrics": category_metrics,
        "monthly_total_metrics": monthly_metrics,
        "selected_patterns": selected_patterns,
    }
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    with SUMMARY_PATH.open("w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, ensure_ascii=False, indent=2)
        json_file.write("\n")
    REPORT_PATH.write_text(build_report(summary), encoding="utf-8")
    print(f"Análisis generado: {len(selected_patterns)} patrones en {ANALYSIS_DIR}")


if __name__ == "__main__":
    main()
