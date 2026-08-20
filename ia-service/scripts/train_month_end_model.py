"""Entrena un modelo para estimar el gasto al cierre del mes en curso."""

import calendar
import csv
import json
import math
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import joblib
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "simulated_expenses.csv"
MODEL_PATH = BASE_DIR / "models" / "month_end_forecast_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "month_end_model_metadata.json"
EVALUATION_PATH = BASE_DIR / "analysis" / "month_end_model_evaluation.json"
REPORT_PATH = BASE_DIR / "analysis" / "month_end_model_selection_report.md"

RANDOM_SEED = 2026
TRAIN_END = "2025-06"
VALIDATION_START = "2025-07"
VALIDATION_END = "2025-12"
RESERVED_START = "2026-01"
RESERVED_END = "2026-06"
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
FEATURES = (
    "category",
    "month",
    "day_of_month",
    "days_in_month",
    "month_progress",
    "category_spend_to_date",
    "category_transactions_to_date",
    "total_spend_to_date",
    "total_transactions_to_date",
    "category_average_transaction_to_date",
    "overall_average_transaction_to_date",
    "month_sin",
    "month_cos",
    "previous_month_category_total",
    "previous_month_total",
    "has_previous_month_data",
)


def previous_period(period):
    year, month = map(int, period.split("-"))
    previous = date(year, month, 1).replace(day=1)
    if previous.month == 1:
        return f"{previous.year - 1:04d}-12"
    return f"{previous.year:04d}-{previous.month - 1:02d}"


def load_expenses():
    expenses = []
    with DATA_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames != ["date", "category", "amount"]:
            raise ValueError("El dataset de T38 no conserva la estructura esperada.")
        for row in reader:
            expense_date = datetime.strptime(row["date"], "%Y-%m-%d").date()
            category = row["category"]
            amount = float(row["amount"])
            if category not in CATEGORIES or not math.isfinite(amount) or amount <= 0:
                raise ValueError("El dataset contiene un gasto inválido.")
            expenses.append({"date": expense_date, "category": category, "amount": amount})
    expenses.sort(key=lambda item: (item["date"], item["category"], item["amount"]))
    return expenses


def build_scenarios(expenses):
    by_period = defaultdict(list)
    for expense in expenses:
        by_period[expense["date"].strftime("%Y-%m")].append(expense)

    monthly_category_totals = defaultdict(float)
    monthly_totals = defaultdict(float)
    for period, period_expenses in by_period.items():
        for expense in period_expenses:
            monthly_category_totals[(period, expense["category"])] += expense["amount"]
            monthly_totals[period] += expense["amount"]

    rows = []
    scenario_summaries = []
    for period in sorted(by_period):
        year, month = map(int, period.split("-"))
        days_in_month = calendar.monthrange(year, month)[1]
        first_transaction_day = min(item["date"].day for item in by_period[period])
        cutoff_days = sorted({first_transaction_day, *CUTOFF_DAYS})
        cutoff_days = [day for day in cutoff_days if day < days_in_month]
        previous = previous_period(period)
        has_previous = int(previous in by_period)

        for cutoff_day in cutoff_days:
            observed = [item for item in by_period[period] if item["date"].day <= cutoff_day]
            if not observed:
                continue
            observed_by_category = defaultdict(list)
            for expense in observed:
                observed_by_category[expense["category"]].append(expense["amount"])
            total_spend = sum(item["amount"] for item in observed)
            total_transactions = len(observed)
            month_progress = cutoff_day / days_in_month
            scenario_id = f"{period}-{cutoff_day:02d}"
            scenario_summaries.append(
                {
                    "scenario_id": scenario_id,
                    "period": period,
                    "cutoff_date": f"{period}-{cutoff_day:02d}",
                    "actual_total": monthly_totals[period],
                }
            )
            for category in CATEGORIES:
                category_amounts = observed_by_category[category]
                category_spend = sum(category_amounts)
                category_transactions = len(category_amounts)
                features = [
                    category,
                    month,
                    cutoff_day,
                    days_in_month,
                    month_progress,
                    category_spend,
                    category_transactions,
                    total_spend,
                    total_transactions,
                    category_spend / category_transactions if category_transactions else 0.0,
                    total_spend / total_transactions,
                    math.sin(2 * math.pi * month / 12),
                    math.cos(2 * math.pi * month / 12),
                    monthly_category_totals[(previous, category)] if has_previous else 0.0,
                    monthly_totals[previous] if has_previous else 0.0,
                    has_previous,
                ]
                rows.append(
                    {
                        "scenario_id": scenario_id,
                        "period": period,
                        "category": category,
                        "features": features,
                        "target": monthly_category_totals[(period, category)],
                        "naive_prediction": category_spend / month_progress,
                    }
                )
    return rows, scenario_summaries


def create_pipeline(regressor):
    preprocessing = ColumnTransformer(
        [
            ("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), [0]),
            ("numeric", "passthrough", list(range(1, len(FEATURES)))),
        ]
    )
    return Pipeline([("preprocessing", preprocessing), ("regressor", regressor)])


def candidate_factories():
    return {
        "LinearRegression": lambda: create_pipeline(LinearRegression()),
        "RandomForestRegressor": lambda: create_pipeline(
            RandomForestRegressor(random_state=RANDOM_SEED)
        ),
        "GradientBoostingRegressor": lambda: create_pipeline(
            GradientBoostingRegressor(random_state=RANDOM_SEED)
        ),
    }


def aggregate_total_metrics(rows, raw_predictions):
    actual_by_scenario = defaultdict(float)
    projected_by_scenario = defaultdict(float)
    negative_count = 0
    for row, raw_value in zip(rows, raw_predictions):
        prediction = float(raw_value)
        if not math.isfinite(prediction):
            raise ValueError("Se obtuvo una predicción NaN o Infinity.")
        negative_count += int(prediction < 0)
        actual_by_scenario[row["scenario_id"]] += row["target"]
        projected_by_scenario[row["scenario_id"]] += max(0.0, prediction)
    scenario_ids = sorted(actual_by_scenario)
    actual = [actual_by_scenario[item] for item in scenario_ids]
    predicted = [projected_by_scenario[item] for item in scenario_ids]
    absolute_error = sum(abs(real - estimate) for real, estimate in zip(actual, predicted))
    return {
        "mae_total": round(float(mean_absolute_error(actual, predicted)), 4),
        "rmse_total": round(math.sqrt(float(mean_squared_error(actual, predicted))), 4),
        "wape_total_percentage": round(absolute_error / sum(actual) * 100, 4),
        "negative_raw_predictions": negative_count,
        "nonnegative_adjustments": negative_count,
        "evaluated_scenarios": len(scenario_ids),
    }


def category_wape(rows, raw_predictions):
    actual = defaultdict(float)
    errors = defaultdict(float)
    for row, raw_value in zip(rows, raw_predictions):
        actual[row["category"]] += row["target"]
        errors[row["category"]] += abs(row["target"] - max(0.0, float(raw_value)))
    return {
        category: round(errors[category] / actual[category] * 100, 4)
        if actual[category] else None
        for category in CATEGORIES
    }


def evaluate_predictions(rows, raw_predictions):
    metrics = aggregate_total_metrics(rows, raw_predictions)
    metrics["wape_by_category_percentage"] = category_wape(rows, raw_predictions)
    return metrics


def evaluate_candidates(train_rows, validation_rows):
    x_train = [row["features"] for row in train_rows]
    y_train = [row["target"] for row in train_rows]
    x_validation = [row["features"] for row in validation_rows]
    results = {}
    for name, factory in candidate_factories().items():
        model = factory()
        model.fit(x_train, y_train)
        results[name] = evaluate_predictions(validation_rows, model.predict(x_validation))
    baseline = evaluate_predictions(
        validation_rows,
        [row["naive_prediction"] for row in validation_rows],
    )
    return results, baseline


def select_model(candidate_metrics):
    return min(
        candidate_metrics,
        key=lambda name: (
            candidate_metrics[name]["wape_total_percentage"],
            candidate_metrics[name]["mae_total"],
            candidate_metrics[name]["rmse_total"],
            name,
        ),
    )


def technical_scenario_prediction(model, scenario_rows):
    raw_predictions = [float(value) for value in model.predict(
        [row["features"] for row in scenario_rows]
    )]
    if len(raw_predictions) != len(CATEGORIES) or not all(
        math.isfinite(value) for value in raw_predictions
    ):
        raise ValueError("La prueba técnica no produjo diez predicciones finitas.")
    return {
        "scenario_id": scenario_rows[0]["scenario_id"],
        "has_previous_month_data": int(scenario_rows[0]["features"][-1]),
        "category_predictions": len(raw_predictions),
        "total_projected_amount": round(sum(max(0.0, value) for value in raw_predictions), 4),
        "is_finite": True,
    }


def build_report(metadata):
    candidate_rows = "\n".join(
        f"| {name} | {values['mae_total']:.4f} | {values['rmse_total']:.4f} | "
        f"{values['wape_total_percentage']:.4f} % | {values['negative_raw_predictions']} |"
        for name, values in metadata["candidate_metrics"].items()
    )
    baseline = metadata["baseline_metrics"]
    return f"""# Modelo predictivo para proyección de cierre mensual

## 1. Propósito del modelo

Ahorro Smart utiliza un modelo predictivo para estimar el gasto total esperado al cierre del mes en curso a partir de los gastos registrados hasta una fecha de corte dentro del mismo período. La actividad parcial del mes constituye la principal fuente de información y el historial anterior es complementario y opcional.

## 2. Objetivo predictivo

Estimar por categoría el gasto total al cierre del mismo mes en curso. La suma de las diez categorías produce `total_month_end_projection`. El modelo puede generar una estimación desde el primer mes cuando existe al menos un gasto válido y no exige meses anteriores. El presupuesto mensual no se utiliza como variable predictiva.

## 3. Datos utilizados

Se utilizaron exclusivamente las {metadata['source_transactions']} transacciones simuladas de `simulated_expenses.csv`, desde 2024-01 hasta 2026-06. No se utilizaron ingresos ni presupuesto y el dataset original no fue modificado.

## 4. Construcción de escenarios parciales

Por cada mes se generaron fotografías acumuladas en los días 5, 10, 15, 20 y 25, además del primer día con movimientos cuando aportaba un corte diferente. Solo se conservaron cortes con actividad observada y anteriores al último día. Se generaron {metadata['supervised_scenarios']} escenarios y {metadata['supervised_rows']} filas por categoría. Los movimientos posteriores al corte se usaron únicamente como objetivo histórico final, evitando fuga de información.

## 5. Variables utilizadas

Se utilizaron: {', '.join(f'`{feature}`' for feature in metadata['input_features'])}. Los promedios hasta la fecha se incorporaron como señales simples y justificables.

## 6. Historial anterior opcional

`previous_month_category_total` y `previous_month_total` toman cero cuando no existe mes anterior, mientras `has_previous_month_data` distingue esa ausencia de un total real igual a cero. El historial anterior no es requisito.

## 7. División temporal

- Entrenamiento para selección: {metadata['training_period']} ({metadata['training_rows']} filas).
- Validación para selección: {metadata['validation_period']} ({metadata['validation_rows']} filas).
- Reserva independiente para el Ítem 22: {metadata['reserved_evaluation_period']}, no usada para entrenar, seleccionar ni informar el rendimiento de T40.

## 8. Técnicas evaluadas

LinearRegression, RandomForestRegressor y GradientBoostingRegressor utilizaron las mismas filas y variables. La categoría se procesó con `OneHotEncoder(handle_unknown="ignore")`; los modelos de ensamble usaron `random_state=2026`.

## 9. Baseline de ritmo de gasto

La referencia ingenua extrapoló `category_spend_to_date / month_progress`. En el total mensual obtuvo MAE {baseline['mae_total']:.4f}, RMSE {baseline['rmse_total']:.4f} y WAPE {baseline['wape_total_percentage']:.4f} %.

## 10. Métricas obtenidas

| Candidato | MAE total | RMSE total | WAPE total | Ajustes negativos |
| --- | ---: | ---: | ---: | ---: |
{candidate_rows}

Las predicciones negativas se conservaron como `raw_prediction` para evaluación y se ajustaron mediante `max(0, raw_prediction)` en el resultado funcional agregado. El JSON de evaluación incluye también WAPE por categoría.

## 11. Modelo seleccionado

**{metadata['model_name']}**, por obtener el menor WAPE del total mensual en la validación cronológica. {metadata['selection_reason']}

## 12. Entrenamiento final

Una instancia limpia se entrenó con {metadata['final_training_rows']} filas entre 2024-01 y 2025-12. El nuevo artefacto se guardó por separado y se recargó correctamente. No se utilizaron los meses reservados de 2026.

## 13. Relación con la ERS

- VE-01 origina acumulados, conteos, promedios y totales históricos opcionales.
- VE-02 origina mes, día, días del mes, progreso y representación cíclica.
- VE-03 se utiliza directamente como categoría.
- VS-01 corresponde al gasto estimado al cierre del mismo mes en curso.

## 14. Reserva para evaluación del Ítem 22

Los meses 2026-01 a 2026-06 quedaron completamente excluidos de entrenamiento, selección e hiperparámetros. El Ítem 22 permanece pendiente y no se declara todavía cumplimiento del objetivo de error.

## 15. Limitaciones

- El modelo se entrenó con datos simulados y su rendimiento puede diferir con datos reales.
- Los cortes representan momentos específicos del mes y no todas las fechas posibles.
- Una sola transacción permite producir una estimación, pero implica mayor incertidumbre.
- La estacionalidad y el historial opcional se apoyan en un período temporal reducido.
- La proyección es informativa y no constituye asesoría financiera.
"""


def main():
    expenses = load_expenses()
    rows, scenarios = build_scenarios(expenses)
    train_rows = [row for row in rows if row["period"] <= TRAIN_END]
    validation_rows = [
        row for row in rows if VALIDATION_START <= row["period"] <= VALIDATION_END
    ]
    reserved_rows = [
        row for row in rows if RESERVED_START <= row["period"] <= RESERVED_END
    ]
    final_training_rows = [row for row in rows if row["period"] <= VALIDATION_END]
    if not all((train_rows, validation_rows, reserved_rows, final_training_rows)):
        raise ValueError("La división temporal no produjo todos los conjuntos requeridos.")

    candidate_metrics, baseline_metrics = evaluate_candidates(train_rows, validation_rows)
    selected_name = select_model(candidate_metrics)
    final_model = candidate_factories()[selected_name]()
    final_model.fit(
        [row["features"] for row in final_training_rows],
        [row["target"] for row in final_training_rows],
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVALUATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, MODEL_PATH)
    reloaded_model = joblib.load(MODEL_PATH)
    no_history_id = next(
        row["scenario_id"] for row in final_training_rows if row["features"][-1] == 0
    )
    with_history_id = next(
        row["scenario_id"] for row in final_training_rows if row["features"][-1] == 1
    )
    no_history_test = technical_scenario_prediction(
        reloaded_model,
        [row for row in final_training_rows if row["scenario_id"] == no_history_id],
    )
    with_history_test = technical_scenario_prediction(
        reloaded_model,
        [row for row in final_training_rows if row["scenario_id"] == with_history_id],
    )

    selected = candidate_metrics[selected_name]
    selection_reason = (
        f"{selected_name} alcanzó el menor WAPE total ({selected['wape_total_percentage']:.4f} %) "
        "sobre los mismos escenarios de validación; MAE y RMSE totales respaldan la selección."
    )
    scenario_ids = {row["scenario_id"] for row in rows}
    metadata = {
        "model_name": selected_name,
        "model_library": "scikit-learn",
        "sklearn_version": sklearn.__version__,
        "random_seed": RANDOM_SEED,
        "prediction_objective": "Estimación del gasto al cierre del mes en curso",
        "target": "category_month_end_total",
        "aggregate_target": "total_month_end_projection",
        "input_features": list(FEATURES),
        "source_variables": {
            "VE-01": "Monto: origina acumulados, conteos, promedios y totales históricos opcionales.",
            "VE-02": "Fecha: origina month, day_of_month, days_in_month, month_progress, month_sin y month_cos.",
            "VE-03": "Categoría: utilizada directamente como variable categórica.",
            "VS-01": "Gasto proyectado: gasto estimado al cierre del mismo mes en curso.",
        },
        "training_period": "2024-01 a 2025-06",
        "validation_period": "2025-07 a 2025-12",
        "reserved_evaluation_period": "2026-01 a 2026-06",
        "final_training_period": "2024-01 a 2025-12",
        "candidate_metrics": candidate_metrics,
        "baseline_metrics": baseline_metrics,
        "selection_metric": "Menor WAPE del total mensual; MAE y RMSE totales como respaldo.",
        "selection_reason": selection_reason,
        "source_transactions": len(expenses),
        "supervised_scenarios": len(scenario_ids),
        "supervised_rows": len(rows),
        "training_rows": len(train_rows),
        "validation_rows": len(validation_rows),
        "reserved_rows": len(reserved_rows),
        "final_training_rows": len(final_training_rows),
        "cutoff_strategy": ["primer día con movimientos", "día 5", "día 10", "día 15", "día 20", "día 25"],
        "categories": list(CATEGORIES),
        "requires_previous_month_history": False,
        "minimum_current_month_expenses": 1,
        "uses_budget": False,
        "negative_adjustment_rule": "projected_amount = max(0, raw_prediction)",
        "selected_model_negative_adjustments": selected["nonnegative_adjustments"],
        "created_for": "T40 de Ahorro Smart: selección y entrenamiento del modelo predictivo de cierre mensual.",
        "technical_tests": {
            "without_previous_history": no_history_test,
            "with_previous_history": with_history_test,
        },
        "limitations": [
            "Datos simulados; el desempeño con datos reales puede diferir.",
            "Los cortes no representan todos los días posibles del mes.",
            "Una predicción con una sola transacción presenta mayor incertidumbre.",
            "Los meses 2026-01 a 2026-06 quedan reservados para el Ítem 22.",
            "La proyección no constituye asesoría financiera.",
        ],
    }
    evaluation = {
        "prediction_objective": metadata["prediction_objective"],
        "training_period": metadata["training_period"],
        "validation_period": metadata["validation_period"],
        "reserved_evaluation_period": metadata["reserved_evaluation_period"],
        "training_rows": len(train_rows),
        "validation_rows": len(validation_rows),
        "reserved_rows_not_evaluated": len(reserved_rows),
        "candidate_metrics": candidate_metrics,
        "baseline_metrics": baseline_metrics,
        "selection_metric": "wape_total_percentage",
        "selected_model": selected_name,
        "reserved_period_used_for_selection": False,
    }
    METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    EVALUATION_PATH.write_text(
        json.dumps(evaluation, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(build_report(metadata), encoding="utf-8")
    print(
        f"Modelo seleccionado: {selected_name}; escenarios={len(scenario_ids)}; "
        f"train={len(train_rows)}; validation={len(validation_rows)}; "
        f"reserved={len(reserved_rows)}; WAPE_total={selected['wape_total_percentage']:.4f}%"
    )


if __name__ == "__main__":
    main()
