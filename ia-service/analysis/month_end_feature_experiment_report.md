# Experimento de variables conductuales para cierre mensual

## Alcance

Se compararon A, B1, B2, B3 y B con `LinearRegression`, las mismas filas y `category_month_end_total`. Train corresponde a 2024-01–2025-06 y la validación final a 2025-07–2025-12. La reserva 2026-01–2026-06 no fue cargada en el experimento.

## Validación temporal interna

| Variante | WAPE medio | Folds mejores que A | Deltas WAPE por fold frente a A |
| --- | ---: | ---: | --- |
| A | 8.0102 % | 0 | +0.0000, +0.0000, +0.0000, +0.0000 |
| B1 | 8.0742 % | 2 | +0.7166, +0.2587, -0.3421, -0.3772 |
| B2 | 7.2303 % | 2 | -5.7259, +4.0583, -2.0247, +0.5727 |
| B3 | 7.0824 % | 3 | +0.9118, -0.6786, -3.5595, -0.3848 |
| B | 4.3622 % | 3 | -8.6647, -0.2636, -6.1008, +0.4372 |

## Validación final de desarrollo

| Variante | MAE total | RMSE total | WAPE total | Predicciones negativas | Meses mejorados | Aceptada |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| A | 54894.3302 | 67676.8420 | 4.1554 % | 8 | — | Referencia |
| B1 | 53804.9237 | 67278.6005 | 4.0729 % | 8 | 3 | False |
| B2 | 62550.5581 | 73932.7348 | 4.7349 % | 1 | 2 | False |
| B3 | 52647.3167 | 66351.6913 | 3.9853 % | 2 | 5 | False |
| B | 65073.9912 | 76258.7627 | 4.9259 % | 0 | 2 | False |

## Comparación con A

### B1

- Mejora WAPE absoluta: +0.0825 puntos.
- Mejora WAPE relativa: +1.9854 %.
- Cambio MAE / RMSE: -1.9846 % / -0.5884 %.
- Meses mejorados / empeorados: 3 / 3.
- Deterioros graves en categorías de bajo volumen: ninguno.
- Cumple todos los criterios: **No**.
### B2

- Mejora WAPE absoluta: -0.5795 puntos.
- Mejora WAPE relativa: -13.9457 %.
- Cambio MAE / RMSE: +13.9472 % / +9.2438 %.
- Meses mejorados / empeorados: 2 / 4.
- Deterioros graves en categorías de bajo volumen: {'Salud': 34.2823}.
- Cumple todos los criterios: **No**.
### B3

- Mejora WAPE absoluta: +0.1701 puntos.
- Mejora WAPE relativa: +4.0935 %.
- Cambio MAE / RMSE: -4.0933 % / -1.9581 %.
- Meses mejorados / empeorados: 5 / 1.
- Deterioros graves en categorías de bajo volumen: ninguno.
- Cumple todos los criterios: **No**.
### B

- Mejora WAPE absoluta: -0.7705 puntos.
- Mejora WAPE relativa: -18.5421 %.
- Cambio MAE / RMSE: +18.5441 % / +12.6807 %.
- Meses mejorados / empeorados: 2 / 4.
- Deterioros graves en categorías de bajo volumen: {'Salud': 59.0879}.
- Cumple todos los criterios: **No**.

## WAPE por categoría

| Categoría | A | B1 | B2 | B3 | B |
| --- | ---: | ---: | ---: | ---: | ---: |
| Alimentación | 23.4052 | 23.3250 | 23.8156 | 24.1394 | 24.9865 |
| Transporte | 32.3167 | 32.3176 | 34.2524 | 27.1408 | 28.9149 |
| Vivienda | 6.4619 | 6.4382 | 6.4427 | 3.3451 | 3.1224 |
| Servicios básicos | 14.5566 | 14.7888 | 14.4664 | 10.0471 | 10.0578 |
| Salud | 141.3322 | 141.7407 | 175.6145 | 144.6224 | 200.4201 |
| Educación | 112.1973 | 112.7528 | 116.5236 | 113.0225 | 118.1350 |
| Pago de deudas y créditos | 11.6212 | 11.3368 | 11.6825 | 7.4081 | 7.9139 |
| Entretenimiento | 51.6977 | 51.5925 | 51.4399 | 54.1391 | 52.5031 |
| Mascotas | 60.6442 | 63.3470 | 64.2741 | 64.3819 | 66.4551 |
| Otros gastos | 114.1244 | 114.8190 | 115.3807 | 99.3388 | 101.7231 |

El JSON contiene además MAE por categoría, métricas por mes y por cutoff, dispersión mensual y todos los folds.

## Colinealidad y coeficientes

- Condición numérica estandarizada A: 107.3159.
- Condición numérica estandarizada B: 517.8590.
- Rango/columnas B: 24/24.
- Variables constantes B: [].

Pares de B con correlación absoluta igual o superior a 0,95:

- `day_of_month` ↔ `month_progress`: 0.998570
- `day_of_month` ↔ `active_spending_days`: 0.962999
- `month_progress` ↔ `active_spending_days`: 0.959453
- `total_transactions_to_date` ↔ `active_spending_days`: 0.955010
- `category_average_transaction_to_date` ↔ `median_transaction_amount`: 0.999971

No se eliminaron variables ni se aplicó regularización. Los coeficientes de mayor magnitud están registrados en el JSON.

## Resultado y recomendación

Variante con menor WAPE observado: **B3**.

Mantener A. Ninguna variante enriquecida satisface simultáneamente todos los criterios de sustitución.

Los resultados corresponden a datos simulados y no sustituyen la evaluación reservada del Ítem 22. El modelo productivo y FastAPI permanecen intactos.
