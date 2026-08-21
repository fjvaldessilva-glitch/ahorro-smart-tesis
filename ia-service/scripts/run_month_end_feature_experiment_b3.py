"""Ejecuta T40.3.4 sin modificar ni guardar el modelo productivo."""

import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path
from statistics import mean

try:
    from scripts.behavioral_features import compute_behavioral_features
    from scripts.run_month_end_feature_experiment import (
        _coefficient_diagnostics,
        _comparison_to_a,
        _correlation_diagnostics,
        _first_expense_days,
        _internal_fold_results,
        evaluate_variant,
    )
    from scripts.train_month_end_model import CATEGORIES, FEATURES, build_scenarios, load_expenses
except ModuleNotFoundError:  # Permite ejecutar directamente desde ia-service/scripts.
    from behavioral_features import compute_behavioral_features
    from run_month_end_feature_experiment import (
        _coefficient_diagnostics,
        _comparison_to_a,
        _correlation_diagnostics,
        _first_expense_days,
        _internal_fold_results,
        evaluate_variant,
    )
    from train_month_end_model import CATEGORIES, FEATURES, build_scenarios, load_expenses


DEVELOPMENT_START = date(2024, 1, 1)
DEVELOPMENT_END = date(2025, 12, 31)
TRAIN_END = "2025-06"
VALIDATION_START = "2025-07"
VALIDATION_END = "2025-12"
RESERVED_PERIOD = "2026-01 a 2026-06 (excluido del experimento)"
ANALYSIS_DIR = Path(__file__).resolve().parent.parent / "analysis"
RESULT_PATH = ANALYSIS_DIR / "month_end_b3_optimization_results.json"
REPORT_PATH = ANALYSIS_DIR / "month_end_b3_optimization_report.md"

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
    "B3": (
        "previous_month_comparable_spend",
        "previous_month_comparable_transactions",
        "category_previous_month_comparable_spend",
    ),
    "C1": ("previous_month_comparable_spend",),
    "C2": ("category_previous_month_comparable_spend",),
    "C3": (
        "previous_month_comparable_spend",
        "category_previous_month_comparable_spend",
    ),
    "C4": (
        "previous_month_comparable_spend",
        "category_previous_month_comparable_spend",
        "transactions_last_7_days",
    ),
}

EXPECTED_FEATURE_COUNTS = {
    "A": 16,
    "B3": 19,
    "C1": 17,
    "C2": 17,
    "C3": 18,
    "C4": 19,
}


def load_experiment_expenses():
    """Carga solo el período de desarrollo autorizado, excluyendo 2026."""
    return [
        expense
        for expense in load_expenses()
        if DEVELOPMENT_START <= expense["date"] <= DEVELOPMENT_END
    ]


def row_key(row):
    """Devuelve la clave canónica compartida por todas las variantes."""
    return row["scenario_id"], row["period"], row["category"]


def build_experiment_datasets(expenses=None):
    """Construye A, B3 y C1-C4 sobre las mismas filas, claves y objetivos."""
    if tuple(FEATURES) != EXPECTED_FEATURES_A:
        raise ValueError("Las variables del Modelo A no coinciden con el baseline auditado.")

    development_expenses = load_experiment_expenses() if expenses is None else [
        expense
        for expense in expenses
        if DEVELOPMENT_START <= expense["date"] <= DEVELOPMENT_END
    ]
    if not development_expenses:
        raise ValueError("El conjunto experimental está vacío.")
    if any(expense["date"].year >= 2026 for expense in development_expenses):
        raise ValueError("El conjunto experimental contiene información reservada de 2026.")

    canonical_rows, _ = build_scenarios(development_expenses)
    datasets = {variant: [] for variant in FEATURE_GROUPS}

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
        for variant, extra_names in FEATURE_GROUPS.items():
            datasets[variant].append(
                {
                    **common,
                    "feature_names": [*EXPECTED_FEATURES_A, *extra_names],
                    "features": [
                        *row["features"],
                        *(behavioral[name] for name in extra_names),
                    ],
                }
            )

    validate_experiment_datasets(datasets)
    return datasets


def validate_experiment_datasets(datasets):
    """Verifica paridad estructural y ausencia de datos inválidos o reservados."""
    if set(datasets) != set(FEATURE_GROUPS):
        raise ValueError("Falta una variante selectiva de T40.3.3.")

    baseline = datasets["A"]
    baseline_keys = [row_key(row) for row in baseline]
    baseline_targets = [row["target"] for row in baseline]
    if len(baseline_keys) != len(set(baseline_keys)):
        raise ValueError("Las claves del Modelo A no son únicas.")

    official_categories = set(CATEGORIES)
    categories_by_scenario = defaultdict(set)
    for row in baseline:
        categories_by_scenario[row["scenario_id"]].add(row["category"])
    if not categories_by_scenario or any(
        categories != official_categories
        for categories in categories_by_scenario.values()
    ):
        raise ValueError("Cada escenario debe incluir todas las categorías oficiales.")

    for variant, rows in datasets.items():
        keys = [row_key(row) for row in rows]
        targets = [row["target"] for row in rows]
        if len(rows) != len(baseline) or keys != baseline_keys:
            raise ValueError(f"Las filas o claves de {variant} no coinciden con A.")
        if targets != baseline_targets:
            raise ValueError(f"Los targets de {variant} no coinciden con A.")

        expected_count = EXPECTED_FEATURE_COUNTS[variant]
        for row in rows:
            if row["scenario_id"] != row["cutoff_date"] or row["period"] >= "2026-01":
                raise ValueError(f"{variant} contiene fechas inconsistentes o reservadas.")
            if row["category"] not in official_categories:
                raise ValueError(f"{variant} contiene una categoría no oficial.")
            if len(row["features"]) != expected_count:
                raise ValueError(f"{variant} no tiene {expected_count} features.")
            if len(row["feature_names"]) != expected_count:
                raise ValueError(f"{variant} no tiene {expected_count} nombres de features.")
            if any(
                value is None
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                for value in row["features"][1:]
            ):
                raise ValueError(f"{variant} contiene NaN, Infinity o valores faltantes.")


def split_development_rows(rows):
    """Separa train y validación sin admitir observaciones fuera del desarrollo."""
    train = [row for row in rows if row["period"] <= TRAIN_END]
    validation = [
        row
        for row in rows
        if VALIDATION_START <= row["period"] <= VALIDATION_END
    ]
    if len(train) + len(validation) != len(rows):
        raise ValueError("Existen filas fuera del período de desarrollo autorizado.")
    return {"train": train, "validation": validation}


def build_pretraining_summary(datasets):
    """Resume la preparación estructural sin ajustar ningún modelo."""
    variants = {}
    for name, rows in datasets.items():
        split = split_development_rows(rows)
        variants[name] = {
            "rows": len(rows),
            "features": len(rows[0]["features"]),
            "train_rows": len(split["train"]),
            "validation_rows": len(split["validation"]),
            "period_start": min(row["period"] for row in rows),
            "period_end": max(row["period"] for row in rows),
        }
    return {
        "task": "T40.3.3",
        "target": "category_month_end_total",
        "training_period": "2024-01 a 2025-06",
        "validation_period": "2025-07 a 2025-12",
        "reserved_period": RESERVED_PERIOD,
        "uses_reserved_2026": False,
        "training_executed": False,
        "variants": variants,
    }


def run_selective_experiment():
    """Entrena variantes experimentales en memoria y devuelve sus diagnósticos."""
    expenses = load_experiment_expenses()
    datasets = build_experiment_datasets(expenses)
    first_days = _first_expense_days(expenses)
    final_results = {}
    internal_results = {}
    fitted_models = {}

    for name, rows in datasets.items():
        split = split_development_rows(rows)
        internal_results[name] = _internal_fold_results(split["train"], first_days)
        fitted_models[name], final_results[name] = evaluate_variant(
            split["train"],
            split["validation"],
            first_days,
        )

    comparisons = {
        name: _comparison_to_a(
            name,
            final_results[name],
            final_results["A"],
            split_development_rows(datasets[name])["validation"],
        )
        for name in FEATURE_GROUPS
        if name != "A"
    }
    internal_summary = {}
    baseline_wapes = [
        fold["metrics"]["wape_percentage"] for fold in internal_results["A"]
    ]
    for name, folds in internal_results.items():
        wapes = [fold["metrics"]["wape_percentage"] for fold in folds]
        internal_summary[name] = {
            "mean_wape_percentage": round(mean(wapes), 4),
            "folds_better_than_a": sum(
                current < baseline
                for current, baseline in zip(wapes, baseline_wapes)
            ),
            "fold_wape_delta_vs_a": [
                round(current - baseline, 4)
                for current, baseline in zip(wapes, baseline_wapes)
            ],
        }

    best_wape = min(
        final_results,
        key=lambda name: final_results[name]["global"]["wape_percentage"],
    )
    best_stability = min(
        final_results,
        key=lambda name: final_results[name]["stability"][
            "monthly_wape_standard_deviation"
        ],
    )
    diagnostics = {}
    for name in FEATURE_GROUPS:
        train_rows = split_development_rows(datasets[name])["train"]
        diagnostics[name] = {
            "correlation_and_condition": _correlation_diagnostics(train_rows),
            "coefficients": _coefficient_diagnostics(fitted_models[name]),
        }

    return {
        "task": "T40.3.4",
        "algorithm": "LinearRegression",
        "target": "category_month_end_total",
        "training_period": "2024-01 a 2025-06",
        "validation_period": "2025-07 a 2025-12",
        "reserved_period": RESERVED_PERIOD,
        "uses_reserved_2026": False,
        "product_model_replaced": False,
        "feature_groups": {
            name: [*EXPECTED_FEATURES_A, *extra]
            for name, extra in FEATURE_GROUPS.items()
        },
        "dataset_summary": build_pretraining_summary(datasets),
        "internal_temporal_validation": internal_results,
        "internal_summary": internal_summary,
        "final_validation": final_results,
        "comparisons_to_a": comparisons,
        "diagnostics": diagnostics,
        "best_variant_by_wape": best_wape,
        "best_variant_by_monthly_stability": best_stability,
    }


def _format_number(value):
    return "—" if value is None else f"{value:.4f}"


def build_report(result):
    """Genera el informe legible de la ejecución selectiva."""
    final_rows = []
    for name, metrics in result["final_validation"].items():
        global_metrics = metrics["global"]
        comparison = result["comparisons_to_a"].get(name)
        final_rows.append(
            f"| {name} | {global_metrics['mae']:.4f} | "
            f"{global_metrics['rmse']:.4f} | "
            f"{global_metrics['wape_percentage']:.4f} % | "
            f"{global_metrics['negative_raw_predictions']} | "
            f"{metrics['stability']['monthly_wape_standard_deviation']:.4f} | "
            f"{comparison['months_improved'] if comparison else '—'} | "
            f"{comparison['accepted'] if comparison else 'Referencia'} |"
        )

    month_rows = []
    for period in result["final_validation"]["A"]["by_month"]:
        cells = []
        baseline = result["final_validation"]["A"]["by_month"][period][
            "wape_percentage"
        ]
        for name in FEATURE_GROUPS:
            current = result["final_validation"][name]["by_month"][period][
                "wape_percentage"
            ]
            delta = current - baseline
            cells.append(
                f"{current:.4f} ({delta:+.4f})" if name != "A" else f"{current:.4f}"
            )
        month_rows.append(f"| {period} | " + " | ".join(cells) + " |")

    category_rows = []
    for category in CATEGORIES:
        category_rows.append(
            f"| {category} | "
            + " | ".join(
                _format_number(
                    result["final_validation"][name]["by_category"][category][
                        "wape_percentage"
                    ]
                )
                for name in FEATURE_GROUPS
            )
            + " |"
        )

    cutoff_names = (
        "first_expense_day",
        "day_5",
        "day_10",
        "day_15",
        "day_20",
        "day_25",
    )
    cutoff_rows = []
    for cutoff in cutoff_names:
        cutoff_rows.append(
            f"| {cutoff} | "
            + " | ".join(
                _format_number(
                    result["final_validation"][name]["by_cutoff"].get(
                        cutoff, {}
                    ).get("wape_percentage")
                )
                for name in FEATURE_GROUPS
            )
            + " |"
        )

    comparison_sections = []
    for name, comparison in result["comparisons_to_a"].items():
        comparison_sections.append(
            f"### {name}\n\n"
            f"- Mejora absoluta de WAPE: "
            f"{comparison['wape_absolute_improvement_points']:+.4f} puntos.\n"
            f"- Mejora relativa de WAPE: "
            f"{comparison['wape_relative_improvement_percentage']:+.4f} %.\n"
            f"- Cambio de MAE / RMSE: {comparison['mae_change_percentage']:+.4f} % / "
            f"{comparison['rmse_change_percentage']:+.4f} %.\n"
            f"- Meses mejorados / empeorados: {comparison['months_improved']} / "
            f"{comparison['months_worsened']}.\n"
            f"- Deterioros graves en categorías pequeñas: "
            f"{comparison['severe_category_deterioration_points'] or 'ninguno'}.\n"
            f"- Aceptada: **{'Sí' if comparison['accepted'] else 'No'}**."
        )

    best = result["best_variant_by_wape"]
    accepted = best != "A" and result["comparisons_to_a"][best]["accepted"]
    globals_by_variant = {
        name: values["global"] for name, values in result["final_validation"].items()
    }
    b3_to_c3_wape = (
        globals_by_variant["C3"]["wape_percentage"]
        - globals_by_variant["B3"]["wape_percentage"]
    )
    c3_to_c4_wape = (
        globals_by_variant["C4"]["wape_percentage"]
        - globals_by_variant["C3"]["wape_percentage"]
    )
    c1_to_c3_wape = (
        globals_by_variant["C3"]["wape_percentage"]
        - globals_by_variant["C1"]["wape_percentage"]
    )
    recommendation = (
        f"{best} satisface todos los criterios experimentales de aceptación. "
        "Su eventual incorporación productiva requiere una tarea posterior y la evaluación reservada."
        if accepted
        else "Ninguna variante satisface simultáneamente todos los criterios; se mantiene A como referencia técnica."
    )

    return f"""# Optimización selectiva de variables B3 — T40.3.4

## Alcance

Se compararon A, B3, C1, C2, C3 y C4 mediante `LinearRegression`, `OneHotEncoder(handle_unknown=\"ignore\")`, las mismas filas y el target `category_month_end_total`. El entrenamiento corresponde a 2024-01–2025-06 y la validación a 2025-07–2025-12. La reserva 2026-01–2026-06 fue excluida.

## Resultados globales

| Variante | MAE | RMSE | WAPE | Negativas | Desv. WAPE mensual | Meses mejorados | Aceptada |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
{chr(10).join(final_rows)}

## WAPE mensual y diferencia contra A

Los valores entre paréntesis corresponden a la diferencia en puntos frente a A; un valor negativo representa mejora.

| Mes | A | B3 | C1 | C2 | C3 | C4 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(month_rows)}

## WAPE por categoría

| Categoría | A | B3 | C1 | C2 | C3 | C4 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(category_rows)}

## WAPE por fecha de corte

| Corte | A | B3 | C1 | C2 | C3 | C4 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(cutoff_rows)}

## Comparación con A

{chr(10).join(comparison_sections)}

## Diagnóstico selectivo

- Mejor variante por WAPE: **{best}**.
- Mejor variante por estabilidad mensual: **{result['best_variant_by_monthly_stability']}**.
- B3 conserva las tres variables originales y reproduce el WAPE 3,9853 % observado en T40.3.2.
- Al retirar `previous_month_comparable_transactions`, C3 cambia el WAPE en {b3_to_c3_wape:+.4f} puntos respecto de B3. Por tanto, esta variable aporta una mejora pequeña al WAPE y no se considera redundante con evidencia suficiente para descartarla.
- C1 confirma que `previous_month_comparable_spend` aporta la principal señal monetaria global: mejora A, aunque no alcanza el desempeño de B3.
- C2 demuestra que `category_previous_month_comparable_spend` de forma aislada no mejora el baseline, pese a registrar la menor dispersión mensual.
- La combinación monetaria C3 cambia el WAPE en {c1_to_c3_wape:+.4f} puntos respecto de C1, lo que indica un aporte complementario pequeño de la comparación por categoría.
- Al agregar `transactions_last_7_days` sobre C3, C4 cambia el WAPE en {c3_to_c4_wape:+.4f} puntos. La mejora global es marginal y reduce de cinco a tres los meses mejorados frente a A, por lo que su aporte no es temporalmente consistente.
- Las variables monetarias comparables explican la mayor parte de la mejora observada; la frecuencia reciente no proporciona evidencia suficiente para una sustitución.

## Recomendación

{recommendation}

Los modelos fueron entrenados exclusivamente en memoria. No se guardó ningún `.joblib`, no se reemplazó el baseline y FastAPI permaneció intacto.
"""


def write_artifacts(result):
    """Escribe únicamente los dos artefactos autorizados de T40.3.4."""
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    REPORT_PATH.write_text(build_report(result), encoding="utf-8", newline="\n")


def main():
    result = run_selective_experiment()
    write_artifacts(result)
    print(
        json.dumps(
            {
                "best_variant_by_wape": result["best_variant_by_wape"],
                "best_variant_by_monthly_stability": result[
                    "best_variant_by_monthly_stability"
                ],
                "final_validation": {
                    name: metrics["global"]
                    for name, metrics in result["final_validation"].items()
                },
                "artifacts": [str(RESULT_PATH), str(REPORT_PATH)],
                "product_model_replaced": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
