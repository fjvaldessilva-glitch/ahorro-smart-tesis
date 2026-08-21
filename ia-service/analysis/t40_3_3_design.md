# T40.3.3 — Diseño del experimento selectivo basado en B3

## Motivo de la iteración

T40.3.2 comparó el Modelo A con grupos de variables conductuales. B3 fue la variante con mejor desempeño observado: obtuvo un WAPE de validación de 3,9853 %, frente al 4,1554 % del Modelo A, mejoró cinco de seis meses y redujo MAE y RMSE. Sin embargo, su mejora absoluta de 0,1701 puntos y relativa de 4,0935 % no alcanzó el criterio mínimo de aceptación predefinido.

T40.3.3 prepara una iteración de ablación selectiva para identificar qué variables de B3 aportan la señal útil y si la frecuencia transaccional reciente complementa esa información. Esta etapa construye y valida los datasets, pero no entrena modelos ni genera resultados definitivos.

## Hipótesis

La comparación del gasto acumulado con días equivalentes del mes anterior puede aportar una señal suficiente por sí sola o combinada con su equivalente por categoría. La cantidad comparable de transacciones podría ser redundante, mientras que `transactions_last_7_days` podría complementar las variables monetarias con una señal reciente de frecuencia.

## Variantes preparadas

Todas las variantes conservan las 16 variables originales del Modelo A.

| Variante | Variables adicionales | Total de features |
| --- | --- | ---: |
| A | Ninguna | 16 |
| B3 | `previous_month_comparable_spend`, `previous_month_comparable_transactions`, `category_previous_month_comparable_spend` | 19 |
| C1 | `previous_month_comparable_spend` | 17 |
| C2 | `category_previous_month_comparable_spend` | 17 |
| C3 | `previous_month_comparable_spend`, `category_previous_month_comparable_spend` | 18 |
| C4 | `previous_month_comparable_spend`, `category_previous_month_comparable_spend`, `transactions_last_7_days` | 19 |

El target permanece como `category_month_end_total`. Todas las variantes comparten exactamente las mismas filas, objetivos y claves `(scenario_id, period, category)`.

## Dataset y separación temporal

- Entrenamiento: 2024-01 a 2025-06.
- Validación final de desarrollo: 2025-07 a 2025-12.
- Reserva excluida: 2026-01 a 2026-06.

La preparación filtra el dataset antes de construir escenarios y rechaza fechas reservadas, claves duplicadas, categorías no oficiales, diferencias de targets, valores faltantes, NaN o Infinity.

## Restricciones

- No se ejecuta `fit`, predicción ni selección de modelo en T40.3.3.
- No se crean archivos `.joblib` ni resultados definitivos.
- No se modifica el baseline, su metadata ni el predictor productivo.
- No se modifica `run_month_end_feature_experiment.py`.
- No se utiliza información de 2026.
- Las variables conductuales se calculan únicamente con movimientos conocidos hasta `cutoff_date`.
- FastAPI, backend y frontend permanecen fuera del alcance.

## Criterio de aceptación para la ejecución posterior

La futura ejecución deberá comparar cada variante con A utilizando MAE, RMSE y WAPE global, resultados mensuales y por categoría, predicciones negativas, estabilidad temporal y diagnóstico de colinealidad. Para sustituir A, una variante deberá:

1. obtener un WAPE inferior al baseline;
2. alcanzar una mejora mínima de 0,20 puntos porcentuales o de 5 % relativo;
3. mejorar al menos cuatro de los seis meses de validación;
4. no deteriorar MAE ni RMSE en más de 2 %;
5. no aumentar significativamente las predicciones negativas;
6. no producir deterioros graves en categorías de bajo volumen;
7. mantener un comportamiento consistente en la validación temporal interna.

Hasta ejecutar y revisar esas comparaciones, el Modelo A continúa como modelo oficial y ninguna variante C se considera seleccionada.
