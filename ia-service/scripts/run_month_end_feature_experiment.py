"""Ejecuta el experimento T40.3.2 sin modificar ni guardar el modelo productivo."""

import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from statistics import mean, median, pstdev

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

try:
    from scripts.behavioral_features import FEATURE_NAMES, compute_behavioral_features
    from scripts.train_month_end_model import CATEGORIES, FEATURES, build_scenarios, load_expenses
except ModuleNotFoundError:  # Permite ejecutar directamente desde ia-service/scripts.
    from behavioral_features import FEATURE_NAMES, compute_behavioral_features
    from train_month_end_model import CATEGORIES, FEATURES, build_scenarios, load_expenses


DEVELOPMENT_START = date(2024, 1, 1)
DEVELOPMENT_END = date(2025, 12, 31)
TRAIN_END = "2025-06"
VALIDATION_START = "2025-07"
VALIDATION_END = "2025-12"
RESERVED_PERIOD = "2026-01 a 2026-06 (excluido del experimento)"
ANALYSIS_DIR = Path(__file__).resolve().parent.parent / "analysis"
RESULT_PATH = ANALYSIS_DIR / "month_end_feature_experiment.json"
REPORT_PATH = ANALYSIS_DIR / "month_end_feature_experiment_report.md"
INTERNAL_FOLDS = (
    ("F1", "2024-06", "2024-07", "2024-09"),
    ("F2", "2024-09", "2024-10", "2024-12"),
    ("F3", "2024-12", "2025-01", "2025-03"),
    ("F4", "2025-03", "2025-04", "2025-06"),
)

EXPECTED_FEATURES_A = (
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
FEATURE_GROUPS = {
    "A": (),
    "B1": ("spend_last_7_days", "transactions_last_7_days"),
    "B2": (
        "median_transaction_amount",
        "active_spending_days",
        "days_since_last_expense",
        "has_category_expense_history",
    ),
    "B3": (
        "previous_month_comparable_spend",
        "previous_month_comparable_transactions",
        "category_previous_month_comparable_spend",
    ),
    "B": FEATURE_NAMES,
}


def load_experiment_expenses():
    """Carga solamente 2024-01 a 2025-12 antes de construir escenarios."""
    return [
        expense for expense in load_expenses()
        if DEVELOPMENT_START <= expense["date"] <= DEVELOPMENT_END
    ]


def row_key(row):
    return row["scenario_id"], row["period"], row["category"]


def _feature_vector(base_features, behavioral, extra_names):
    return [*base_features, *(behavioral[name] for name in extra_names)]


def build_experiment_datasets(expenses=None):
    """Construye A, B1, B2, B3 y B sobre las mismas filas y targets."""
    if tuple(FEATURES) != EXPECTED_FEATURES_A:
        raise ValueError("Las variables del Modelo A ya no coinciden con el baseline auditado.")
    if len(EXPECTED_FEATURES_A) != 16 or len(FEATURE_NAMES) != 9:
        raise ValueError("El conteo declarado de variables A/B no es el esperado.")

    development_expenses = load_experiment_expenses() if expenses is None else [
        expense for expense in expenses
        if DEVELOPMENT_START <= expense["date"] <= DEVELOPMENT_END
    ]
    if not development_expenses or any(expense["date"].year >= 2026 for expense in development_expenses):
        raise ValueError("El conjunto experimental está vacío o contiene información de 2026.")

    canonical_rows, _ = build_scenarios(development_expenses)
    datasets = {name: [] for name in FEATURE_GROUPS}
    for row in canonical_rows:
        cutoff_date = date.fromisoformat(row["scenario_id"])
        behavioral = compute_behavioral_features(
            development_expenses,
            row["category"],
            cutoff_date,
        )
        common = {
            "scenario_id": row["scenario_id"],
            "period": row["period"],
            "cutoff_date": cutoff_date.isoformat(),
            "category": row["category"],
            "target": row["target"],
        }
        for model_name, extra_names in FEATURE_GROUPS.items():
            datasets[model_name].append({
                **common,
                "feature_names": [*EXPECTED_FEATURES_A, *extra_names],
                "features": _feature_vector(row["features"], behavioral, extra_names),
            })

    validate_experiment_datasets(datasets)
    return datasets


def validate_experiment_datasets(datasets):
    """Detiene la ejecución ante diferencias de filas, targets o valores inválidos."""
    if set(datasets) != set(FEATURE_GROUPS):
        raise ValueError("Falta una variante experimental.")
    baseline = datasets["A"]
    baseline_keys = [row_key(row) for row in baseline]
    if len(baseline_keys) != len(set(baseline_keys)):
        raise ValueError("Las claves del Modelo A no son únicas.")

    expected_categories = set(CATEGORIES)
    scenario_categories = defaultdict(set)
    for row in baseline:
        scenario_categories[row["scenario_id"]].add(row["category"])
    if not scenario_categories or any(categories != expected_categories for categories in scenario_categories.values()):
        raise ValueError("Cada escenario debe contener exactamente las diez categorías oficiales.")

    for model_name, rows in datasets.items():
        expected_count = len(EXPECTED_FEATURES_A) + len(FEATURE_GROUPS[model_name])
        keys = [row_key(row) for row in rows]
        if len(rows) != len(baseline) or keys != baseline_keys or len(keys) != len(set(keys)):
            raise ValueError(f"Las filas o claves de {model_name} no coinciden con A.")
        for baseline_row, row in zip(baseline, rows):
            if row["target"] != baseline_row["target"]:
                raise ValueError(f"Los targets de {model_name} no coinciden con A.")
            if row["scenario_id"] != row["cutoff_date"] or row["period"] >= "2026-01":
                raise ValueError(f"{model_name} contiene fechas inconsistentes o reservadas.")
            if row["category"] not in expected_categories:
                raise ValueError(f"{model_name} contiene una categoría no oficial.")
            if len(row["features"]) != expected_count or len(row["feature_names"]) != expected_count:
                raise ValueError(f"{model_name} no tiene el número esperado de variables.")
            numeric = row["features"][1:]
            if any(value is None or not isinstance(value, (int, float)) or not math.isfinite(value) for value in numeric):
                raise ValueError(f"{model_name} contiene NaN, Infinity o valores faltantes.")


def split_development_rows(rows):
    """Separa train y validación final; 2026 nunca forma parte de la entrada."""
    train = [row for row in rows if row["period"] <= TRAIN_END]
    validation = [row for row in rows if VALIDATION_START <= row["period"] <= VALIDATION_END]
    if len(train) + len(validation) != len(rows):
        raise ValueError("Existen filas fuera de train y validación de desarrollo.")
    return {"train": train, "validation": validation}


def build_pretraining_diagnostics(datasets):
    """Resume estructura y reserva espacio explícito para análisis posteriores."""
    diagnostics = {
        "reserved_period": RESERVED_PERIOD,
        "models": {},
        "pending_diagnostics": {
            "correlation_matrix": "no ejecutada en T40.3.1",
            "condition_number": "no ejecutado en T40.3.1",
            "coefficient_comparison": "requiere entrenamiento experimental posterior",
        },
    }
    for model_name, rows in datasets.items():
        split = split_development_rows(rows)
        periods = sorted({row["period"] for row in rows})
        missing_values = sum(
            value is None for row in rows for value in row["features"]
        )
        diagnostics["models"][model_name] = {
            "rows": len(rows),
            "features": len(rows[0]["features"]),
            "period_start": periods[0],
            "period_end": periods[-1],
            "train_rows": len(split["train"]),
            "validation_rows": len(split["validation"]),
            "categories": sorted(Counter(row["category"] for row in rows)),
            "missing_values": missing_values,
        }
    return diagnostics


def _pipeline(feature_count):
    preprocessing = ColumnTransformer([
        ("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), [0]),
        ("numeric", "passthrough", list(range(1, feature_count))),
    ])
    return Pipeline([
        ("preprocessing", preprocessing),
        ("regressor", LinearRegression()),
    ])


def _wape(actual, predicted):
    denominator = sum(actual)
    return sum(abs(real - estimate) for real, estimate in zip(actual, predicted)) / denominator * 100 if denominator else None


def _basic_metrics(actual, predicted):
    if not actual or len(actual) != len(predicted):
        raise ValueError("Las métricas requieren listas no vacías y equivalentes.")
    errors = [real - estimate for real, estimate in zip(actual, predicted)]
    values = {
        "mae": mean(abs(error) for error in errors),
        "rmse": math.sqrt(mean(error ** 2 for error in errors)),
        "wape_percentage": _wape(actual, predicted),
        "observations": len(actual),
    }
    return {key: round(float(value), 4) if value is not None else None for key, value in values.items()}


def _scenario_predictions(rows, raw_predictions):
    actual, predicted = defaultdict(float), defaultdict(float)
    metadata = {}
    for row, raw in zip(rows, raw_predictions):
        if not math.isfinite(float(raw)):
            raise ValueError("El experimento produjo NaN o Infinity.")
        scenario = row["scenario_id"]
        actual[scenario] += row["target"]
        predicted[scenario] += max(0.0, float(raw))
        metadata[scenario] = {"period": row["period"], "cutoff_date": row["cutoff_date"]}
    return [
        {"scenario_id": scenario, **metadata[scenario], "actual": actual[scenario], "predicted": predicted[scenario]}
        for scenario in sorted(actual)
    ]


def _category_metrics(rows, raw_predictions):
    grouped_actual, grouped_predicted = defaultdict(list), defaultdict(list)
    for row, raw in zip(rows, raw_predictions):
        grouped_actual[row["category"]].append(row["target"])
        grouped_predicted[row["category"]].append(max(0.0, float(raw)))
    return {
        category: _basic_metrics(grouped_actual[category], grouped_predicted[category])
        for category in CATEGORIES
    }


def _grouped_scenario_metrics(scenarios, key_function):
    grouped = defaultdict(list)
    for scenario in scenarios:
        for key in key_function(scenario):
            grouped[key].append(scenario)
    return {
        key: _basic_metrics(
            [item["actual"] for item in values],
            [item["predicted"] for item in values],
        )
        for key, values in sorted(grouped.items())
    }


def _first_expense_days(expenses):
    result = {}
    for expense in expenses:
        period = expense["date"].strftime("%Y-%m")
        result[period] = min(result.get(period, expense["date"].day), expense["date"].day)
    return result


def evaluate_variant(train_rows, validation_rows, first_days):
    model = _pipeline(len(train_rows[0]["features"]))
    model.fit([row["features"] for row in train_rows], [row["target"] for row in train_rows])
    raw = [float(value) for value in model.predict([row["features"] for row in validation_rows])]
    scenarios = _scenario_predictions(validation_rows, raw)
    global_metrics = _basic_metrics(
        [item["actual"] for item in scenarios],
        [item["predicted"] for item in scenarios],
    )
    global_metrics["negative_raw_predictions"] = sum(value < 0 for value in raw)
    global_metrics["evaluated_scenarios"] = len(scenarios)
    by_month = _grouped_scenario_metrics(scenarios, lambda item: [item["period"]])

    def cutoff_groups(item):
        day = date.fromisoformat(item["cutoff_date"]).day
        groups = []
        if day == first_days[item["period"]]:
            groups.append("first_expense_day")
        if day in (5, 10, 15, 20, 25):
            groups.append(f"day_{day}")
        return groups

    by_cutoff = _grouped_scenario_metrics(scenarios, cutoff_groups)
    monthly_wape = [metrics["wape_percentage"] for metrics in by_month.values()]
    return model, {
        "global": global_metrics,
        "by_category": _category_metrics(validation_rows, raw),
        "by_month": by_month,
        "by_cutoff": by_cutoff,
        "stability": {
            "monthly_wape_mean": round(mean(monthly_wape), 4),
            "monthly_wape_standard_deviation": round(pstdev(monthly_wape), 4),
        },
    }


def _internal_fold_results(rows, first_days):
    results = []
    for fold, train_end, validation_start, validation_end in INTERNAL_FOLDS:
        train = [row for row in rows if row["period"] <= train_end]
        validation = [row for row in rows if validation_start <= row["period"] <= validation_end]
        _, metrics = evaluate_variant(train, validation, first_days)
        results.append({
            "fold": fold,
            "train_period": f"2024-01 a {train_end}",
            "validation_period": f"{validation_start} a {validation_end}",
            "train_rows": len(train),
            "validation_rows": len(validation),
            "metrics": metrics["global"],
        })
    return results


def _correlation_diagnostics(rows):
    names = rows[0]["feature_names"][1:]
    matrix = np.asarray([row["features"][1:] for row in rows], dtype=float)
    standard_deviation = matrix.std(axis=0)
    constant_names = [name for name, deviation in zip(names, standard_deviation) if deviation == 0]
    variable_indices = [index for index, deviation in enumerate(standard_deviation) if deviation > 0]
    variable_matrix = matrix[:, variable_indices]
    variable_names = [names[index] for index in variable_indices]
    correlation = np.corrcoef(variable_matrix, rowvar=False)
    pairs = []
    for left in range(len(variable_names)):
        for right in range(left + 1, len(variable_names)):
            value = float(correlation[left, right])
            if math.isfinite(value) and abs(value) >= 0.95:
                pairs.append({"left": variable_names[left], "right": variable_names[right], "correlation": round(value, 6)})
    standardized = (variable_matrix - variable_matrix.mean(axis=0)) / variable_matrix.std(axis=0)
    return {
        "numeric_features": len(names),
        "constant_features": constant_names,
        "high_correlation_threshold": 0.95,
        "high_correlation_pairs": pairs,
        "standardized_matrix_rank": int(np.linalg.matrix_rank(standardized)),
        "standardized_matrix_columns": int(standardized.shape[1]),
        "standardized_condition_number": round(float(np.linalg.cond(standardized)), 4),
    }


def _coefficient_diagnostics(model, limit=12):
    transformed_names = model.named_steps["preprocessing"].get_feature_names_out()
    coefficients = model.named_steps["regressor"].coef_
    ranked = sorted(
        ({"feature": str(name), "coefficient": round(float(value), 6)} for name, value in zip(transformed_names, coefficients)),
        key=lambda item: abs(item["coefficient"]),
        reverse=True,
    )
    regressor = model.named_steps["regressor"]
    return {
        "matrix_rank": int(regressor.rank_),
        "transformed_features": len(transformed_names),
        "largest_absolute_coefficients": ranked[:limit],
    }


def _comparison_to_a(name, metrics, baseline_metrics, validation_rows):
    current, baseline = metrics["global"], baseline_metrics["global"]
    absolute_improvement = baseline["wape_percentage"] - current["wape_percentage"]
    relative_improvement = absolute_improvement / baseline["wape_percentage"] * 100
    month_deltas = {
        period: round(values["wape_percentage"] - baseline_metrics["by_month"][period]["wape_percentage"], 4)
        for period, values in metrics["by_month"].items()
    }
    months_improved = sum(value < 0 for value in month_deltas.values())
    actual_by_category = defaultdict(float)
    for row in validation_rows:
        actual_by_category[row["category"]] += row["target"]
    volume_median = median(actual_by_category.values())
    low_volume = sorted(category for category, total in actual_by_category.items() if total <= volume_median)
    severe_category_deterioration = {
        category: round(
            metrics["by_category"][category]["wape_percentage"]
            - baseline_metrics["by_category"][category]["wape_percentage"], 4
        )
        for category in low_volume
        if metrics["by_category"][category]["wape_percentage"]
        - baseline_metrics["by_category"][category]["wape_percentage"] > 10
    }
    mae_change = (current["mae"] / baseline["mae"] - 1) * 100
    rmse_change = (current["rmse"] / baseline["rmse"] - 1) * 100
    criteria = {
        "wape_lower": current["wape_percentage"] < baseline["wape_percentage"],
        "minimum_wape_improvement": absolute_improvement >= 0.20 or relative_improvement >= 5,
        "improves_at_least_four_months": months_improved >= 4,
        "mae_not_worse_than_two_percent": mae_change <= 2,
        "rmse_not_worse_than_two_percent": rmse_change <= 2,
        "negative_predictions_not_significantly_higher": current["negative_raw_predictions"] <= baseline["negative_raw_predictions"] + 2,
        "no_severe_low_volume_category_deterioration": not severe_category_deterioration,
    }
    return {
        "variant": name,
        "wape_absolute_improvement_points": round(absolute_improvement, 4),
        "wape_relative_improvement_percentage": round(relative_improvement, 4),
        "mae_change_percentage": round(mae_change, 4),
        "rmse_change_percentage": round(rmse_change, 4),
        "months_improved": months_improved,
        "months_worsened": sum(value > 0 for value in month_deltas.values()),
        "monthly_wape_delta_vs_a": month_deltas,
        "low_volume_categories": low_volume,
        "severe_category_deterioration_points": severe_category_deterioration,
        "acceptance_criteria": criteria,
        "accepted": all(criteria.values()),
    }


def run_feature_experiment():
    expenses = load_experiment_expenses()
    datasets = build_experiment_datasets(expenses)
    first_days = _first_expense_days(expenses)
    final_results, internal_results, models = {}, {}, {}
    for name, rows in datasets.items():
        split = split_development_rows(rows)
        internal_results[name] = _internal_fold_results(split["train"], first_days)
        model, final_results[name] = evaluate_variant(split["train"], split["validation"], first_days)
        models[name] = model

    comparisons = {
        name: _comparison_to_a(name, final_results[name], final_results["A"], split_development_rows(datasets[name])["validation"])
        for name in ("B1", "B2", "B3", "B")
    }
    internal_summary = {}
    for name, folds in internal_results.items():
        wapes = [fold["metrics"]["wape_percentage"] for fold in folds]
        baseline_wapes = [fold["metrics"]["wape_percentage"] for fold in internal_results["A"]]
        internal_summary[name] = {
            "mean_wape_percentage": round(mean(wapes), 4),
            "folds_better_than_a": sum(current < baseline for current, baseline in zip(wapes, baseline_wapes)),
            "fold_wape_delta_vs_a": [round(current - baseline, 4) for current, baseline in zip(wapes, baseline_wapes)],
        }

    best_name = min(final_results, key=lambda name: final_results[name]["global"]["wape_percentage"])
    return {
        "task": "T40.3.2",
        "algorithm": "LinearRegression",
        "target": "category_month_end_total",
        "development_period": "2024-01 a 2025-12",
        "training_period": "2024-01 a 2025-06",
        "final_validation_period": "2025-07 a 2025-12",
        "reserved_period": RESERVED_PERIOD,
        "uses_reserved_2026": False,
        "dataset_diagnostics": build_pretraining_diagnostics(datasets),
        "feature_groups": {name: [*EXPECTED_FEATURES_A, *extra] for name, extra in FEATURE_GROUPS.items()},
        "internal_temporal_validation": internal_results,
        "internal_summary": internal_summary,
        "final_validation": final_results,
        "comparisons_to_a": comparisons,
        "diagnostics": {
            "A": {
                "correlation_and_condition": _correlation_diagnostics(split_development_rows(datasets["A"])["train"]),
                "coefficients": _coefficient_diagnostics(models["A"]),
            },
            "B": {
                "correlation_and_condition": _correlation_diagnostics(split_development_rows(datasets["B"])["train"]),
                "coefficients": _coefficient_diagnostics(models["B"]),
            },
        },
        "best_observed_variant_by_final_wape": best_name,
        "product_model_replaced": False,
    }


def _number(value):
    return "—" if value is None else f"{value:.4f}"


def build_experiment_report(result):
    rows = []
    for name, metrics in result["final_validation"].items():
        global_metrics = metrics["global"]
        comparison = result["comparisons_to_a"].get(name)
        rows.append(
            f"| {name} | {global_metrics['mae']:.4f} | {global_metrics['rmse']:.4f} | "
            f"{global_metrics['wape_percentage']:.4f} % | {global_metrics['negative_raw_predictions']} | "
            f"{comparison['months_improved'] if comparison else '—'} | {comparison['accepted'] if comparison else 'Referencia'} |"
        )
    internal_rows = "\n".join(
        f"| {name} | {values['mean_wape_percentage']:.4f} % | {values['folds_better_than_a']} | "
        f"{', '.join(f'{delta:+.4f}' for delta in values['fold_wape_delta_vs_a'])} |"
        for name, values in result["internal_summary"].items()
    )
    comparison_sections = []
    for name, comparison in result["comparisons_to_a"].items():
        comparison_sections.append(
            f"### {name}\n\n"
            f"- Mejora WAPE absoluta: {comparison['wape_absolute_improvement_points']:+.4f} puntos.\n"
            f"- Mejora WAPE relativa: {comparison['wape_relative_improvement_percentage']:+.4f} %.\n"
            f"- Cambio MAE / RMSE: {comparison['mae_change_percentage']:+.4f} % / {comparison['rmse_change_percentage']:+.4f} %.\n"
            f"- Meses mejorados / empeorados: {comparison['months_improved']} / {comparison['months_worsened']}.\n"
            f"- Deterioros graves en categorías de bajo volumen: {comparison['severe_category_deterioration_points'] or 'ninguno'}.\n"
            f"- Cumple todos los criterios: **{'Sí' if comparison['accepted'] else 'No'}**."
        )
    category_rows = "\n".join(
        f"| {category} | " + " | ".join(
            _number(result["final_validation"][name]["by_category"][category]["wape_percentage"])
            for name in FEATURE_GROUPS
        ) + " |"
        for category in CATEGORIES
    )
    high_pairs = result["diagnostics"]["B"]["correlation_and_condition"]["high_correlation_pairs"]
    pair_text = "\n".join(
        f"- `{item['left']}` ↔ `{item['right']}`: {item['correlation']:.6f}"
        for item in high_pairs
    ) or "- No se detectaron pares sobre el umbral."
    best = result["best_observed_variant_by_final_wape"]
    accepted = result["comparisons_to_a"].get(best, {}).get("accepted", False)
    recommendation = (
        f"{best} obtuvo el menor WAPE observado y cumple todos los criterios; sigue siendo un candidato experimental."
        if best != "A" and accepted else
        "Mantener A. Ninguna variante enriquecida satisface simultáneamente todos los criterios de sustitución."
    )
    return f"""# Experimento de variables conductuales para cierre mensual

## Alcance

Se compararon A, B1, B2, B3 y B con `LinearRegression`, las mismas filas y `category_month_end_total`. Train corresponde a 2024-01–2025-06 y la validación final a 2025-07–2025-12. La reserva 2026-01–2026-06 no fue cargada en el experimento.

## Validación temporal interna

| Variante | WAPE medio | Folds mejores que A | Deltas WAPE por fold frente a A |
| --- | ---: | ---: | --- |
{internal_rows}

## Validación final de desarrollo

| Variante | MAE total | RMSE total | WAPE total | Predicciones negativas | Meses mejorados | Aceptada |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
{chr(10).join(rows)}

## Comparación con A

{chr(10).join(comparison_sections)}

## WAPE por categoría

| Categoría | A | B1 | B2 | B3 | B |
| --- | ---: | ---: | ---: | ---: | ---: |
{category_rows}

El JSON contiene además MAE por categoría, métricas por mes y por cutoff, dispersión mensual y todos los folds.

## Colinealidad y coeficientes

- Condición numérica estandarizada A: {result['diagnostics']['A']['correlation_and_condition']['standardized_condition_number']:.4f}.
- Condición numérica estandarizada B: {result['diagnostics']['B']['correlation_and_condition']['standardized_condition_number']:.4f}.
- Rango/columnas B: {result['diagnostics']['B']['correlation_and_condition']['standardized_matrix_rank']}/{result['diagnostics']['B']['correlation_and_condition']['standardized_matrix_columns']}.
- Variables constantes B: {result['diagnostics']['B']['correlation_and_condition']['constant_features']}.

Pares de B con correlación absoluta igual o superior a 0,95:

{pair_text}

No se eliminaron variables ni se aplicó regularización. Los coeficientes de mayor magnitud están registrados en el JSON.

## Resultado y recomendación

Variante con menor WAPE observado: **{best}**.

{recommendation}

Los resultados corresponden a datos simulados y no sustituyen la evaluación reservada del Ítem 22. El modelo productivo y FastAPI permanecen intactos.
"""


def write_experiment_artifacts(result):
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    REPORT_PATH.write_text(build_experiment_report(result), encoding="utf-8", newline="\n")


def main():
    result = run_feature_experiment()
    write_experiment_artifacts(result)
    summary = {
        name: values["global"] for name, values in result["final_validation"].items()
    }
    print(json.dumps({
        "best_observed_variant": result["best_observed_variant_by_final_wape"],
        "final_validation": summary,
        "artifacts": [str(RESULT_PATH), str(REPORT_PATH)],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
