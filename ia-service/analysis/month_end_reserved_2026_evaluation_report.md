# Evaluación final reservada 2026 de los modelos A y B3

## 1. Objetivo

Evaluar fuera de muestra el Modelo A oficial y la variante experimental B3 sobre el período reservado 2026-01 a 2026-06, sin utilizar estos resultados para entrenamiento, selección de variables o ajuste de hiperparámetros.

## 2. Período reservado

La reserva comprende enero a junio de 2026. Contiene 35 escenarios y 350 filas por modelo, distribuidas entre las diez categorías oficiales.

## 3. Metodología

A se cargó desde el artefacto productivo congelado. B3 se reconstruyó una sola vez con `LinearRegression`, `OneHotEncoder(handle_unknown="ignore")`, las 16 variables de A y sus tres variables comparables. La reconstrucción utilizó exclusivamente 2024-01 a 2025-06 y se almacenó como artefacto experimental temporal. Las variables de cada escenario reservado utilizaron únicamente información disponible hasta su fecha de corte; el gasto definitivo posterior al corte se empleó solo como target de evaluación.

## 4. Independencia de 2026

El período 2026-01 a 2026-06 no participó en entrenamiento, selección de variables ni ajuste. Su único uso fue calcular las métricas finales fuera de muestra. La reconstrucción de B3 reproduce T40.3.x y no constituye una nueva selección de modelo.

## 5. Resultados globales

| Modelo | MAE | RMSE | WAPE | Predicciones negativas |
| --- | ---: | ---: | ---: | ---: |
| A | 116614.0230 | 169618.7040 | 8.3611 % | 16 |
| B3 | 114614.8072 | 166439.0756 | 8.2177 % | 11 |

## 6. Resultados mensuales

| Mes | WAPE A | WAPE B3 | Diferencia B3 − A |
| --- | ---: | ---: | ---: |
| 2026-01 | 21.7644 % | 21.2979 % | -0.4665 |
| 2026-02 | 4.6414 % | 4.1905 % | -0.4509 |
| 2026-03 | 4.6110 % | 4.3202 % | -0.2908 |
| 2026-04 | 5.6451 % | 4.5453 % | -1.0998 |
| 2026-05 | 4.1231 % | 5.2833 % | +1.1602 |
| 2026-06 | 4.6956 % | 5.1139 % | +0.4183 |

## 7. Comparación

- Diferencia absoluta de WAPE a favor de B3: +0.1434 puntos.
- Diferencia relativa a favor de B3: +1.7151 %.
- Menor WAPE reservado: **B3**.

## 8. Estabilidad temporal

- A: media mensual 7.5801 % y desviación estándar 6.3595.
- B3: media mensual 7.4585 % y desviación estándar 6.2018.

## 9. Resultados por categoría

| Categoría | WAPE A | WAPE B3 | Diferencia B3 − A |
| --- | ---: | ---: | ---: |
| Alimentación | 17.9416 % | 16.3194 % | -1.6222 |
| Transporte | 14.7534 % | 14.6285 % | -0.1249 |
| Vivienda | 6.2908 % | 4.2281 % | -2.0627 |
| Servicios básicos | 14.4601 % | 14.5312 % | +0.0711 |
| Salud | 108.5506 % | 92.5841 % | -15.9665 |
| Educación | 118.2512 % | 120.7816 % | +2.5304 |
| Pago de deudas y créditos | 14.2768 % | 13.3998 % | -0.8770 |
| Entretenimiento | 23.9512 % | 24.5134 % | +0.5622 |
| Mascotas | 77.3435 % | 62.1370 % | -15.2065 |
| Otros gastos | 135.3435 % | 126.6585 % | -8.6850 |

## 10. Conclusión técnica

El modelo **B3** obtuvo el menor WAPE en la reserva. Este resultado describe desempeño fuera de muestra, pero no reemplaza automáticamente el modelo oficial. La evaluación se realiza sobre datos simulados y solo seis meses. Además, A fue ajustado finalmente hasta 2025-12, mientras B3 fue reconstruido únicamente hasta 2025-06 según la autorización, por lo que las ventanas de ajuste no son equivalentes. Cualquier eventual sustitución requiere una decisión posterior explícita; en esta tarea el baseline y FastAPI permanecen intactos.
