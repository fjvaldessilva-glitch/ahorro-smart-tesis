"""Evalúa A y una reconstrucción congelada de B3 sobre la reserva de 2026."""

import hashlib
import json
import math
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from statistics import mean, pstdev

import joblib

try:
    from scripts.run_month_end_feature_experiment import _pipeline
    from scripts.run_month_end_feature_experiment_b3 import (
        EXPECTED_FEATURES_A,
        build_experiment_datasets,
        load_experiment_expenses,
        split_development_rows,
    )
    from scripts.train_month_end_model import CATEGORIES, build_scenarios, load_expenses
except ModuleNotFoundError:  # Permite ejecutar directamente desde ia-service/scripts.
    from run_month_end_feature_experiment import _pipeline
    from run_month_end_feature_experiment_b3 import (
        EXPECTED_FEATURES_A,
        build_experiment_datasets,
        load_experiment_expenses,
        split_development_rows,
    )
    from train_month_end_model import CATEGORIES, build_scenarios, load_expenses


BASE_DIR = Path(__file__).resolve().parent.parent
OFFICIAL_MODEL_PATH = BASE_DIR / "models" / "month_end_forecast_model.joblib"
EXPERIMENTAL_MODEL_PATH = (
    BASE_DIR / "models" / "experimental" / "month_end_b3_reserved_evaluation.joblib"
)
RESULT_PATH = BASE_DIR / "analysis" / "month_end_reserved_2026_evaluation.json"
REPORT_PATH = BASE_DIR / "analysis" / "month_end_reserved_2026_evaluation_report.md"

RESERVED_START = "2026-01"
RESERVED_END = "2026-06"
B3_EXTRA_FEATURES = (
    "previous_month_comparable_spend",
    "previous_month_comparable_transactions",
    "category_previous_month_comparable_spend",
)
B3_FEATURES = (*EXPECTED_FEATURES_A, *B3_EXTRA_FEATURES)


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def reconstruct_b3_once():
    """Ajusta B3 una vez con 2024-01–2025-06 o carga la reconstrucción existente."""
    if EXPERIMENTAL_MODEL_PATH.exists():
        artifact = joblib.load(EXPERIMENTAL_MODEL_PATH)
        if (
            not isinstance(artifact, dict)
            or artifact.get("artifact_type") != "experimental_b3_reserved_evaluation"
            or artifact.get("training_period") != "2024-01 a 2025-06"
            or tuple(artifact.get("feature_names", ())) != B3_FEATURES
        ):
            raise ValueError("El artefacto experimental B3 existente no conserva el contrato esperado.")
        return artifact

    datasets = build_experiment_datasets(load_experiment_expenses())
    train_rows = split_development_rows(datasets["B3"])["train"]
    if not train_rows or any(row["period"] > "2025-06" for row in train_rows):
        raise ValueError("La reconstrucción B3 contiene filas fuera del entrenamiento autorizado.")

    pipeline = _pipeline(len(B3_FEATURES))
    pipeline.fit(
        [row["features"] for row in train_rows],
        [row["target"] for row in train_rows],
    )
    artifact = {
        "artifact_type": "experimental_b3_reserved_evaluation",
        "purpose": (
            "Reconstrucción reproducible del experimento T40.3.x para evaluación "
            "reservada; no corresponde a una nueva selección de modelo."
        ),
        "algorithm": "LinearRegression",
        "training_period": "2024-01 a 2025-06",
        "training_rows": len(train_rows),
        "feature_names": list(B3_FEATURES),
        "uses_2026_for_training": False,
        "pipeline": pipeline,
    }
    EXPERIMENTAL_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, EXPERIMENTAL_MODEL_PATH)
    return joblib.load(EXPERIMENTAL_MODEL_PATH)


def previous_comparable_features(expenses, category, cutoff_date):
    """Calcula las tres variables B3 sin utilizar movimientos posteriores al corte."""
    previous_month_end = cutoff_date.replace(day=1) - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)
    equivalent_end = previous_month_end.replace(
        day=min(cutoff_date.day, previous_month_end.day)
    )
    known_expenses = [expense for expense in expenses if expense["date"] <= cutoff_date]
    comparable = [
        expense
        for expense in known_expenses
        if previous_month_start <= expense["date"] <= equivalent_end
    ]
    category_comparable = [
        expense for expense in comparable if expense["category"] == category
    ]
    values = (
        sum(expense["amount"] for expense in comparable),
        len(comparable),
        sum(expense["amount"] for expense in category_comparable),
    )
    if any(not math.isfinite(float(value)) for value in values):
        raise ValueError("Las variables comparables B3 contienen NaN o Infinity.")
    return values


def build_reserved_datasets(expenses):
    """Construye las mismas filas reservadas para A y B3."""
    canonical_rows, _ = build_scenarios(expenses)
    a_rows = [
        row
        for row in canonical_rows
        if RESERVED_START <= row["period"] <= RESERVED_END
    ]
    b3_rows = []
    for row in a_rows:
        cutoff_date = date.fromisoformat(row["scenario_id"])
        extras = previous_comparable_features(expenses, row["category"], cutoff_date)
        b3_rows.append({**row, "features": [*row["features"], *extras]})

    validate_reserved_datasets(a_rows, b3_rows)
    return {"A": a_rows, "B3": b3_rows}


def validate_reserved_datasets(a_rows, b3_rows):
    if not a_rows or len(a_rows) != len(b3_rows):
        raise ValueError("La reserva no produjo filas equivalentes para A y B3.")
    a_keys = [(row["scenario_id"], row["period"], row["category"]) for row in a_rows]
    b3_keys = [(row["scenario_id"], row["period"], row["category"]) for row in b3_rows]
    if a_keys != b3_keys or len(a_keys) != len(set(a_keys)):
        raise ValueError("A y B3 no conservan las mismas claves únicas.")
    if [row["target"] for row in a_rows] != [row["target"] for row in b3_rows]:
        raise ValueError("A y B3 no conservan los mismos targets.")

    categories_by_scenario = defaultdict(set)
    for row in a_rows:
        categories_by_scenario[row["scenario_id"]].add(row["category"])
    if any(categories != set(CATEGORIES) for categories in categories_by_scenario.values()):
        raise ValueError("La reserva no contiene las diez categorías en cada escenario.")

    for name, rows, expected_features in (
        ("A", a_rows, 16),
        ("B3", b3_rows, 19),
    ):
        for row in rows:
            if not RESERVED_START <= row["period"] <= RESERVED_END:
                raise ValueError(f"{name} contiene filas fuera de la reserva.")
            if len(row["features"]) != expected_features:
                raise ValueError(f"{name} no conserva su número de variables.")
            if any(
                not isinstance(value, (int, float)) or not math.isfinite(value)
                for value in row["features"][1:]
            ):
                raise ValueError(f"{name} contiene NaN, Infinity o valores faltantes.")


def basic_metrics(actual, predicted):
    errors = [real - estimate for real, estimate in zip(actual, predicted)]
    denominator = sum(actual)
    if not actual or len(actual) != len(predicted) or denominator <= 0:
        raise ValueError("No es posible calcular métricas sobre la reserva.")
    return {
        "mae": round(mean(abs(error) for error in errors), 4),
        "rmse": round(math.sqrt(mean(error ** 2 for error in errors)), 4),
        "wape_percentage": round(
            sum(abs(error) for error in errors) / denominator * 100,
            4,
        ),
        "observations": len(actual),
    }


def evaluate_model(model, rows):
    raw_predictions = [
        float(value) for value in model.predict([row["features"] for row in rows])
    ]
    if any(not math.isfinite(value) for value in raw_predictions):
        raise ValueError("El modelo produjo predicciones NaN o Infinity.")

    scenario_actual = defaultdict(float)
    scenario_predicted = defaultdict(float)
    scenario_period = {}
    category_actual = defaultdict(list)
    category_predicted = defaultdict(list)
    for row, raw in zip(rows, raw_predictions):
        scenario_actual[row["scenario_id"]] += row["target"]
        scenario_predicted[row["scenario_id"]] += max(0.0, raw)
        scenario_period[row["scenario_id"]] = row["period"]
        category_actual[row["category"]].append(row["target"])
        category_predicted[row["category"]].append(max(0.0, raw))

    scenario_ids = sorted(scenario_actual)
    global_metrics = basic_metrics(
        [scenario_actual[item] for item in scenario_ids],
        [scenario_predicted[item] for item in scenario_ids],
    )
    global_metrics["negative_raw_predictions"] = sum(
        prediction < 0 for prediction in raw_predictions
    )
    global_metrics["evaluated_scenarios"] = len(scenario_ids)

    by_month = {}
    for period in sorted({scenario_period[item] for item in scenario_ids}):
        ids = [item for item in scenario_ids if scenario_period[item] == period]
        by_month[period] = basic_metrics(
            [scenario_actual[item] for item in ids],
            [scenario_predicted[item] for item in ids],
        )
    by_category = {
        category: basic_metrics(
            category_actual[category], category_predicted[category]
        )
        for category in CATEGORIES
    }
    monthly_wapes = [values["wape_percentage"] for values in by_month.values()]
    return {
        "global": global_metrics,
        "by_month": by_month,
        "by_category": by_category,
        "stability": {
            "monthly_wape_mean": round(mean(monthly_wapes), 4),
            "monthly_wape_standard_deviation": round(pstdev(monthly_wapes), 4),
            "months": len(monthly_wapes),
        },
    }


def build_result():
    official_model = joblib.load(OFFICIAL_MODEL_PATH)
    b3_artifact = reconstruct_b3_once()
    expenses = load_expenses()
    reserved = build_reserved_datasets(expenses)
    evaluations = {
        "A": evaluate_model(official_model, reserved["A"]),
        "B3": evaluate_model(b3_artifact["pipeline"], reserved["B3"]),
    }
    a_wape = evaluations["A"]["global"]["wape_percentage"]
    b3_wape = evaluations["B3"]["global"]["wape_percentage"]
    absolute_improvement = a_wape - b3_wape
    return {
        "task": "T40.4",
        "purpose": "Evaluación final fuera de muestra sobre la reserva 2026.",
        "reserved_period": "2026-01 a 2026-06",
        "reserved_period_used_for_training": False,
        "reserved_period_used_for_selection": False,
        "target": "category_month_end_total",
        "categories": list(CATEGORIES),
        "models": {
            "A": {
                "role": "Modelo oficial congelado",
                "features": list(EXPECTED_FEATURES_A),
                "artifact": str(OFFICIAL_MODEL_PATH),
                "artifact_sha256": file_sha256(OFFICIAL_MODEL_PATH),
                "final_training_period": "2024-01 a 2025-12",
            },
            "B3": {
                "role": "Reconstrucción experimental congelada de T40.3.x",
                "features": list(B3_FEATURES),
                "artifact": str(EXPERIMENTAL_MODEL_PATH),
                "artifact_sha256": file_sha256(EXPERIMENTAL_MODEL_PATH),
                "training_period": b3_artifact["training_period"],
                "training_rows": b3_artifact["training_rows"],
                "new_model_selection": False,
            },
        },
        "reserved_dataset": {
            "rows_per_model": len(reserved["A"]),
            "scenarios": len({row["scenario_id"] for row in reserved["A"]}),
            "period_start": min(row["period"] for row in reserved["A"]),
            "period_end": max(row["period"] for row in reserved["A"]),
            "same_rows_keys_targets": True,
            "all_official_categories_present": True,
            "features_use_only_information_available_at_cutoff": True,
        },
        "evaluation": evaluations,
        "comparison": {
            "wape_absolute_improvement_points_b3_vs_a": round(absolute_improvement, 4),
            "wape_relative_improvement_percentage_b3_vs_a": round(
                absolute_improvement / a_wape * 100,
                4,
            ),
            "lower_wape_model": "B3" if b3_wape < a_wape else "A",
        },
        "limitations": [
            "Los resultados provienen de datos simulados.",
            "La reserva contiene seis meses y un número limitado de escenarios.",
            "A fue ajustado finalmente con 2024-01 a 2025-12; B3 se reconstruyó exclusivamente con 2024-01 a 2025-06 según la autorización, por lo que sus ventanas de entrenamiento no son equivalentes.",
            "La evaluación reservada no se utiliza para seleccionar variables, ajustar modelos ni modificar el sistema productivo.",
        ],
        "product_model_replaced": False,
    }


def build_report(result):
    evaluation = result["evaluation"]
    global_rows = "\n".join(
        f"| {name} | {values['global']['mae']:.4f} | "
        f"{values['global']['rmse']:.4f} | "
        f"{values['global']['wape_percentage']:.4f} % | "
        f"{values['global']['negative_raw_predictions']} |"
        for name, values in evaluation.items()
    )
    month_rows = "\n".join(
        f"| {period} | {evaluation['A']['by_month'][period]['wape_percentage']:.4f} % | "
        f"{evaluation['B3']['by_month'][period]['wape_percentage']:.4f} % | "
        f"{evaluation['B3']['by_month'][period]['wape_percentage'] - evaluation['A']['by_month'][period]['wape_percentage']:+.4f} |"
        for period in evaluation["A"]["by_month"]
    )
    category_rows = "\n".join(
        f"| {category} | {evaluation['A']['by_category'][category]['wape_percentage']:.4f} % | "
        f"{evaluation['B3']['by_category'][category]['wape_percentage']:.4f} % | "
        f"{evaluation['B3']['by_category'][category]['wape_percentage'] - evaluation['A']['by_category'][category]['wape_percentage']:+.4f} |"
        for category in CATEGORIES
    )
    comparison = result["comparison"]
    lower = comparison["lower_wape_model"]
    return f"""# Evaluación final reservada 2026 de los modelos A y B3

## 1. Objetivo

Evaluar fuera de muestra el Modelo A oficial y la variante experimental B3 sobre el período reservado 2026-01 a 2026-06, sin utilizar estos resultados para entrenamiento, selección de variables o ajuste de hiperparámetros.

## 2. Período reservado

La reserva comprende enero a junio de 2026. Contiene {result['reserved_dataset']['scenarios']} escenarios y {result['reserved_dataset']['rows_per_model']} filas por modelo, distribuidas entre las diez categorías oficiales.

## 3. Metodología

A se cargó desde el artefacto productivo congelado. B3 se reconstruyó una sola vez con `LinearRegression`, `OneHotEncoder(handle_unknown=\"ignore\")`, las 16 variables de A y sus tres variables comparables. La reconstrucción utilizó exclusivamente 2024-01 a 2025-06 y se almacenó como artefacto experimental temporal. Las variables de cada escenario reservado utilizaron únicamente información disponible hasta su fecha de corte; el gasto definitivo posterior al corte se empleó solo como target de evaluación.

## 4. Independencia de 2026

El período 2026-01 a 2026-06 no participó en entrenamiento, selección de variables ni ajuste. Su único uso fue calcular las métricas finales fuera de muestra. La reconstrucción de B3 reproduce T40.3.x y no constituye una nueva selección de modelo.

## 5. Resultados globales

| Modelo | MAE | RMSE | WAPE | Predicciones negativas |
| --- | ---: | ---: | ---: | ---: |
{global_rows}

## 6. Resultados mensuales

| Mes | WAPE A | WAPE B3 | Diferencia B3 − A |
| --- | ---: | ---: | ---: |
{month_rows}

## 7. Comparación

- Diferencia absoluta de WAPE a favor de B3: {comparison['wape_absolute_improvement_points_b3_vs_a']:+.4f} puntos.
- Diferencia relativa a favor de B3: {comparison['wape_relative_improvement_percentage_b3_vs_a']:+.4f} %.
- Menor WAPE reservado: **{lower}**.

## 8. Estabilidad temporal

- A: media mensual {evaluation['A']['stability']['monthly_wape_mean']:.4f} % y desviación estándar {evaluation['A']['stability']['monthly_wape_standard_deviation']:.4f}.
- B3: media mensual {evaluation['B3']['stability']['monthly_wape_mean']:.4f} % y desviación estándar {evaluation['B3']['stability']['monthly_wape_standard_deviation']:.4f}.

## 9. Resultados por categoría

| Categoría | WAPE A | WAPE B3 | Diferencia B3 − A |
| --- | ---: | ---: | ---: |
{category_rows}

## 10. Conclusión técnica

El modelo **{lower}** obtuvo el menor WAPE en la reserva. Este resultado describe desempeño fuera de muestra, pero no reemplaza automáticamente el modelo oficial. La evaluación se realiza sobre datos simulados y solo seis meses. Además, A fue ajustado finalmente hasta 2025-12, mientras B3 fue reconstruido únicamente hasta 2025-06 según la autorización, por lo que las ventanas de ajuste no son equivalentes. Cualquier eventual sustitución requiere una decisión posterior explícita; en esta tarea el baseline y FastAPI permanecen intactos.
"""


def write_results(result):
    RESULT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    REPORT_PATH.write_text(build_report(result), encoding="utf-8", newline="\n")


def main():
    result = build_result()
    write_results(result)
    print(
        json.dumps(
            {
                "evaluation": {
                    name: values["global"]
                    for name, values in result["evaluation"].items()
                },
                "comparison": result["comparison"],
                "experimental_b3_artifact": str(EXPERIMENTAL_MODEL_PATH),
                "product_model_replaced": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
