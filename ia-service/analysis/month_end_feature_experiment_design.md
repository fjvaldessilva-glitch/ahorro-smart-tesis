# Diseño experimental A vs B para proyección de cierre mensual

## Objetivo

T40.3.1 prepara una comparación reproducible entre el Modelo A vigente y un Modelo B enriquecido. No entrena modelos, no selecciona un ganador y no reemplaza `month_end_forecast_model.joblib`.

Ambos conjuntos comparten dataset, escenarios, categorías, fechas de corte, filas, targets y el futuro algoritmo `LinearRegression`. La única diferencia será el conjunto de variables.

## Modelo A

Contiene las 16 variables exactas declaradas en `train_month_end_model.py`: `category`, `month`, `day_of_month`, `days_in_month`, `month_progress`, `category_spend_to_date`, `category_transactions_to_date`, `total_spend_to_date`, `total_transactions_to_date`, `category_average_transaction_to_date`, `overall_average_transaction_to_date`, `month_sin`, `month_cos`, `previous_month_category_total`, `previous_month_total` y `has_previous_month_data`.

El target permanece como `category_month_end_total`.

## Modelo B y ablaciones

Modelo B agrega las nueve variables de `behavioral_features.py`: `spend_last_7_days`, `transactions_last_7_days`, `median_transaction_amount`, `active_spending_days`, `days_since_last_expense`, `has_category_expense_history`, `previous_month_comparable_spend`, `previous_month_comparable_transactions` y `category_previous_month_comparable_spend`. El total es de 25 variables contando `category`.

- B1 agrega ritmo y frecuencia reciente.
- B2 agrega comportamiento transaccional, actividad, recencia e indicador de historial.
- B3 agrega comparación histórica equivalente.
- B agrega las nueve variables.
- B4 se definirá posteriormente solo con variables que demuestren aporte estable.

## Integración y claves

El script reutiliza `load_expenses()`, `build_scenarios()` y `FEATURES` del baseline sin modificarlo. Antes de construir escenarios limita los movimientos a 2024-01–2025-12. Para cada fila canónica llama directamente a `compute_behavioral_features()` y concatena los valores en el orden declarado por `FEATURE_NAMES`.

La clave única es `(scenario_id, period, category)`. `scenario_id` y `cutoff_date` deben coincidir. Cada escenario contiene las diez categorías oficiales. El script detiene la ejecución ante claves duplicadas, filas o targets diferentes, conteos de features incorrectos, valores faltantes, NaN, Infinity o fechas reservadas.

## Separación temporal

- Train: 2024-01 a 2025-06.
- Validación final de desarrollo: 2025-07 a 2025-12.
- Reserva: 2026-01 a 2026-06, completamente excluida de T40.3.1.

La selección posterior de B4 deberá usar validación temporal interna dentro del train. La validación julio–diciembre de 2025 se utilizará una vez después de congelar el conjunto seleccionado.

## Diagnósticos preparados

El resumen previo informa filas, variables, rango temporal, train, validación, categorías y valores faltantes para A, B1, B2, B3 y B. Se reserva espacio explícito para matriz de correlación, número de condición y comparación de coeficientes, que requieren la etapa experimental posterior. No se elimina ninguna variable automáticamente.

## Ejecución T40.3.2

El mismo script ejecuta posteriormente A, B1, B2, B3 y B mediante pipelines experimentales `LinearRegression` en memoria. Registra validación interna, validación final de desarrollo, métricas globales, categóricas, mensuales y por cutoff, además de correlaciones, condición numérica y coeficientes. Los únicos resultados persistidos son `month_end_feature_experiment.json` y `month_end_feature_experiment_report.md`.

## Restricciones

- No se cargan movimientos de 2026 en la construcción experimental.
- Los ajustes y predicciones son exclusivamente experimentales y no se guardan como modelos.
- No se escriben archivos `.joblib` ni metadatos productivos.
- No se modifica el baseline ni el runtime de FastAPI.
- M→M+1 corresponde a un experimento separado y no participa en T40.3.1.
