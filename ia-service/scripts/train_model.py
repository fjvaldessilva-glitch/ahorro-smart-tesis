"""Evalúa, selecciona y entrena el modelo predictivo de gastos mensuales."""

import csv
import json
import math
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
PROCESSED_PATH = BASE_DIR / "data" / "processed_monthly_expenses.csv"
MODELS_DIR = BASE_DIR / "models"
ANALYSIS_DIR = BASE_DIR / "analysis"
MODEL_PATH = MODELS_DIR / "expense_forecast_model.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"
EVALUATION_PATH = ANALYSIS_DIR / "model_evaluation.json"
REPORT_PATH = ANALYSIS_DIR / "model_selection_report.md"

RANDOM_SEED = 2026
START_PERIOD = "2024-01"
END_PERIOD = "2026-06"
TEST_START_PERIOD = "2026-01"
FEATURES = (
    "category",
    "month",
    "trend_index",
    "lag_1",
    "lag_2",
    "lag_3",
    "rolling_mean_3",
    "month_sin",
    "month_cos",
)
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


def month_sequence(start_period, end_period):
    start_year, start_month = map(int, start_period.split("-"))
    end_year, end_month = map(int, end_period.split("-"))
    periods = []
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        periods.append(f"{year:04d}-{month:02d}")
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return periods


def load_monthly_amounts():
    expected = ["year", "month", "period", "category", "monthly_amount", "transaction_count"]
    amounts = {}
    with PROCESSED_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames != expected:
            raise ValueError("El dataset procesado no corresponde a la estructura validada en T38.")
        for row in reader:
            category = row["category"]
            if category not in CATEGORIES:
                raise ValueError(f"Categoría no oficial detectada: {category}")
            amounts[(row["period"], category)] = float(row["monthly_amount"])
    return amounts


def build_supervised_dataset(amounts):
    periods = month_sequence(START_PERIOD, END_PERIOD)
    panel = {
        category: [amounts.get((period, category), 0.0) for period in periods]
        for category in CATEGORIES
    }
    rows = []
    for category in CATEGORIES:
        values = panel[category]
        for index in range(3, len(periods)):
            month = int(periods[index][5:7])
            previous = values[index - 3:index]
            rows.append(
                {
                    "period": periods[index],
                    "features": [
                        category,
                        month,
                        index,
                        values[index - 1],
                        values[index - 2],
                        values[index - 3],
                        sum(previous) / 3,
                        math.sin(2 * math.pi * month / 12),
                        math.cos(2 * math.pi * month / 12),
                    ],
                    "target": values[index],
                }
            )
    rows.sort(key=lambda row: (row["period"], row["features"][0]))
    return rows, panel


def create_pipeline(regressor):
    preprocessing = ColumnTransformer(
        transformers=[
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


def calculate_metrics(actual, predicted):
    if not all(math.isfinite(float(value)) for value in predicted):
        raise ValueError("Un candidato produjo predicciones NaN o Infinity.")
    absolute_errors = [abs(real - estimate) for real, estimate in zip(actual, predicted)]
    positive_errors = [
        abs((real - estimate) / real) * 100
        for real, estimate in zip(actual, predicted)
        if real > 0
    ]
    actual_sum = sum(actual)
    return {
        "mae": round(float(mean_absolute_error(actual, predicted)), 4),
        "rmse": round(math.sqrt(float(mean_squared_error(actual, predicted))), 4),
        "wape_percentage": round(sum(absolute_errors) / actual_sum * 100, 4) if actual_sum else 0.0,
        "mape_positive_targets_percentage": round(sum(positive_errors) / len(positive_errors), 4)
        if positive_errors
        else None,
        "positive_target_rows_for_mape": len(positive_errors),
        "negative_predictions": sum(1 for value in predicted if value < 0),
    }


def evaluate_candidates(train_rows, test_rows):
    x_train = [row["features"] for row in train_rows]
    y_train = [row["target"] for row in train_rows]
    x_test = [row["features"] for row in test_rows]
    y_test = [row["target"] for row in test_rows]
    results = {}
    for name, factory in candidate_factories().items():
        pipeline = factory()
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        results[name] = calculate_metrics(y_test, predictions)
    return results


def select_model(candidate_metrics):
    return min(
        candidate_metrics,
        key=lambda name: (
            candidate_metrics[name]["wape_percentage"],
            candidate_metrics[name]["mae"],
            candidate_metrics[name]["rmse"],
            name,
        ),
    )


def build_future_features(panel, category):
    values = panel[category]
    month = 7
    return [
        category,
        month,
        len(values),
        values[-1],
        values[-2],
        values[-3],
        sum(values[-3:]) / 3,
        math.sin(2 * math.pi * month / 12),
        math.cos(2 * math.pi * month / 12),
    ]


def format_currency(value):
    return f"${value:,.0f}".replace(",", ".")


def build_report(evaluation, metadata):
    rows = "\n".join(
        f"| {name} | {values['mae']:.4f} | {values['rmse']:.4f} | "
        f"{values['wape_percentage']:.4f} % | {values['mape_positive_targets_percentage']:.4f} % |"
        for name, values in evaluation["candidate_metrics"].items()
    )
    return f"""# Selección y entrenamiento del modelo predictivo

## 1. Propósito

Evaluar técnicas predictivas reproducibles y seleccionar un modelo para estimar `monthly_amount` de una categoría en un período mensual futuro. Esta estimación operacionaliza VS-01, gasto proyectado.

## 2. Datos utilizados

Se utilizó exclusivamente el panel mensual derivado de los gastos 100 % simulados de T38: 30 meses, desde 2024-01 hasta 2026-06, y las 10 categorías oficiales. Las combinaciones sin movimientos se representaron internamente con monto cero, sin modificar los datasets de origen.

## 3. Variables utilizadas

Las características fueron `category`, `month`, `trend_index`, `lag_1`, `lag_2`, `lag_3`, `rolling_mean_3`, `month_sin` y `month_cos`. Los lags y la media móvil utilizan exclusivamente los tres meses anteriores al objetivo.

## 4. División temporal

- Entrenamiento de evaluación: {metadata['training_period']} ({metadata['training_rows']} filas).
- Prueba: {metadata['evaluation_period']} ({metadata['test_rows']} filas).
- División cronológica, sin selección aleatoria.

## 5. Técnicas evaluadas

- LinearRegression.
- RandomForestRegressor (`random_state=2026`).
- GradientBoostingRegressor (`random_state=2026`).

Los tres candidatos utilizaron las mismas características, preprocesamiento, filas de entrenamiento y filas de prueba. `category` se codificó con `OneHotEncoder(handle_unknown="ignore")`.

## 6. Métricas obtenidas

| Candidato | MAE | RMSE | WAPE | MAPE sobre objetivos > 0 |
| --- | ---: | ---: | ---: | ---: |
{rows}

WAPE se calculó sobre todos los objetivos; MAPE solo sobre los {evaluation['positive_test_targets']} objetivos de prueba mayores que cero.

## 7. Modelo seleccionado

**{metadata['model_name']}**, por obtener el menor WAPE en la prueba temporal.

## 8. Justificación de la selección

{metadata['selection_reason']}

Las métricas son una evaluación inicial para seleccionar el modelo. La comprobación formal del margen de error corresponde al Ítem 22 y no se cierra en T40.

## 9. Entrenamiento final

Una instancia limpia del candidato seleccionado fue reentrenada con las {metadata['final_training_rows']} filas supervisadas disponibles entre {metadata['final_training_period']}. El artefacto se guardó, volvió a cargarse y produjo para la prueba técnica de julio de 2026 un valor finito de {format_currency(metadata['reload_test_prediction']['predicted_monthly_amount'])} en la categoría {metadata['reload_test_prediction']['category']}.

## 10. Relación con la ERS

- VE-01, monto: origina `monthly_amount`, los tres lags y `rolling_mean_3`.
- VE-02, fecha: origina `month`, `trend_index`, `month_sin` y `month_cos`.
- VE-03, categoría: se utiliza directamente como variable categórica.
- VS-01, gasto proyectado: corresponde al `monthly_amount` estimado para un período mensual futuro.

## 11. Limitaciones

- El entrenamiento utiliza datos simulados y un período controlado reducido.
- Las métricas no garantizan el mismo desempeño con datos reales.
- La prueba temporal contiene solo seis meses.
- Los montos cero de categorías sin movimientos afectan especialmente las métricas porcentuales.
- Una proyección no constituye asesoría financiera.
"""


def main():
    amounts = load_monthly_amounts()
    supervised_rows, panel = build_supervised_dataset(amounts)
    train_rows = [row for row in supervised_rows if row["period"] < TEST_START_PERIOD]
    test_rows = [row for row in supervised_rows if row["period"] >= TEST_START_PERIOD]
    if not train_rows or not test_rows:
        raise ValueError("La división temporal no produjo conjuntos de entrenamiento y prueba válidos.")

    candidate_metrics = evaluate_candidates(train_rows, test_rows)
    selected_name = select_model(candidate_metrics)
    selected_pipeline = candidate_factories()[selected_name]()
    selected_pipeline.fit(
        [row["features"] for row in supervised_rows],
        [row["target"] for row in supervised_rows],
    )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(selected_pipeline, MODEL_PATH)
    reloaded_model = joblib.load(MODEL_PATH)
    test_category = CATEGORIES[0]
    test_features = build_future_features(panel, test_category)
    test_prediction = float(reloaded_model.predict([test_features])[0])
    if not math.isfinite(test_prediction):
        raise ValueError("El modelo recargado no produjo una predicción finita.")

    selection_reason = (
        f"{selected_name} obtuvo el menor WAPE ({candidate_metrics[selected_name]['wape_percentage']:.4f} %) "
        "sobre el mismo conjunto de prueba cronológico. MAE y RMSE respaldan la comparación. "
        "La alternativa representa relaciones no lineales, mantiene una complejidad razonable para el panel reducido, "
        "es reproducible y puede mantenerse dentro de un pipeline único; su capacidad descriptiva se limita al "
        "escenario sintético evaluado."
    )
    metadata = {
        "model_name": selected_name,
        "model_library": "scikit-learn",
        "sklearn_version": sklearn.__version__,
        "random_seed": RANDOM_SEED,
        "target": "monthly_amount",
        "input_features": list(FEATURES),
        "source_variables": {
            "VE-01": "Monto: origina monthly_amount, lag_1, lag_2, lag_3 y rolling_mean_3.",
            "VE-02": "Fecha: origina month, trend_index, month_sin y month_cos.",
            "VE-03": "Categoría: utilizada directamente como variable categórica.",
            "VS-01": "Gasto proyectado: monthly_amount estimado para un período mensual futuro.",
        },
        "training_period": f"{train_rows[0]['period']} a {train_rows[-1]['period']}",
        "evaluation_period": f"{test_rows[0]['period']} a {test_rows[-1]['period']}",
        "final_training_period": f"{supervised_rows[0]['period']} a {supervised_rows[-1]['period']}",
        "candidate_metrics": candidate_metrics,
        "selection_metric": "Menor WAPE; MAE y RMSE como respaldo.",
        "selection_reason": selection_reason,
        "training_rows": len(train_rows),
        "test_rows": len(test_rows),
        "final_training_rows": len(supervised_rows),
        "categories": list(CATEGORIES),
        "created_for": "T40 de Ahorro Smart: entrenamiento académico con datos 100 % simulados.",
        "reload_test_prediction": {
            "period": "2026-07",
            "category": test_category,
            "predicted_monthly_amount": round(test_prediction, 4),
            "is_finite": True,
            "is_negative": test_prediction < 0,
        },
        "limitations": [
            "Datos completamente simulados y período controlado de 30 meses.",
            "Evaluación temporal inicial limitada a seis meses.",
            "El desempeño con usuarios reales puede diferir.",
            "El criterio formal de margen de error se evaluará en el Ítem 22.",
            "Las proyecciones no constituyen asesoría financiera.",
        ],
    }
    evaluation = {
        "training_period": metadata["training_period"],
        "evaluation_period": metadata["evaluation_period"],
        "training_rows": len(train_rows),
        "test_rows": len(test_rows),
        "positive_test_targets": sum(1 for row in test_rows if row["target"] > 0),
        "candidate_metrics": candidate_metrics,
        "selection_metric": "wape_percentage",
        "selected_model": selected_name,
    }

    with METADATA_PATH.open("w", encoding="utf-8") as json_file:
        json.dump(metadata, json_file, ensure_ascii=False, indent=2, allow_nan=False)
        json_file.write("\n")
    with EVALUATION_PATH.open("w", encoding="utf-8") as json_file:
        json.dump(evaluation, json_file, ensure_ascii=False, indent=2, allow_nan=False)
        json_file.write("\n")
    REPORT_PATH.write_text(build_report(evaluation, metadata), encoding="utf-8")
    print(
        f"Modelo seleccionado: {selected_name}; train={len(train_rows)}, test={len(test_rows)}, "
        f"final={len(supervised_rows)}, predicción_prueba={test_prediction:.4f}"
    )


if __name__ == "__main__":
    main()
