# Análisis de patrones habituales de consumo

## 1. Propósito

Este análisis descriptivo utiliza exclusivamente los datos 100 % simulados preparados y validados en T38. Su propósito es identificar patrones cuantificables del escenario sintético, sin interpretar psicológicamente al usuario, afirmar causalidad ni entregar asesoría financiera.

## 2. Fuente de datos

- Período: 2024-01-01 a 2026-06-30 (30 meses).
- Movimientos: 787.
- Categorías oficiales: 10.
- Monto simulado total: $40.360.354.
- Fuentes: `processed_monthly_expenses.csv` y, para frecuencias, `simulated_expenses.csv`.
- Carácter de los datos: completamente sintético, sin información personal, bancaria o financiera real.

## 3. Método de análisis

Por categoría se calcularon monto y transacciones totales, meses con presencia, cobertura, promedio, mediana y desviación estándar mensual, coeficiente de variación, transacciones promedio mensuales y participación en el gasto total. También se calculó la evolución mensual, los promedios por mes calendario y una tendencia descriptiva mediante regresión lineal simple implementada con Python estándar.

## 4. Resultados generales

| Categoría | Monto total | Transacciones | Cobertura | Promedio mensual | Coeficiente de variación | Participación |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Alimentación | $10.158.614 | 323 | 100.00 % | $338.620 | 0.2083 | 25.1698 % |
| Educación | $1.159.419 | 14 | 46.67 % | $82.816 | 0.3001 | 2.8727 % |
| Entretenimiento | $3.078.896 | 83 | 100.00 % | $102.630 | 0.4425 | 7.6285 % |
| Mascotas | $661.947 | 23 | 76.67 % | $28.780 | 0.3492 | 1.6401 % |
| Otros gastos | $815.894 | 21 | 63.33 % | $42.942 | 0.4251 | 2.0215 % |
| Pago de deudas y créditos | $3.940.192 | 30 | 100.00 % | $131.340 | 0.0776 | 9.7625 % |
| Salud | $830.479 | 14 | 46.67 % | $59.320 | 0.3488 | 2.0577 % |
| Servicios básicos | $2.702.426 | 30 | 100.00 % | $90.081 | 0.1418 | 6.6957 % |
| Transporte | $4.283.787 | 219 | 100.00 % | $142.793 | 0.2089 | 10.6138 % |
| Vivienda | $12.728.700 | 30 | 100.00 % | $424.290 | 0.0293 | 31.5376 % |

- Categoría de mayor frecuencia: **Alimentación**.
- Categoría de mayor participación monetaria: **Vivienda**.
- Promedio de gasto total mensual: **$1.345.345**.
- Tendencia lineal descriptiva: **estable**, con pendiente de **$1.193 por mes**.

## 5. Patrones identificados

### P01 - Participación monetaria dominante de Vivienda

Categoría con la mayor proporción del gasto total del escenario simulado.

Categoría involucrada: Vivienda.  
Período: 2024-01-01 a 2026-06-30.

**Evidencia cuantitativa**

- `percentage_of_total_spending`: 31.5376
- `total_amount`: 12728700.0
- `coverage_percentage`: 100.0

**Interpretación técnica:** La categoría concentra la mayor participación monetaria observada; se describe una asociación cuantitativa, no una causa.

**Relevancia predictiva:** Su peso relativo justifica considerar categoría, período y monto al evaluar posteriormente técnicas predictivas.

### P02 - Alta frecuencia de transacciones en Alimentación

Categoría con la mayor cantidad de movimientos durante el período analizado.

Categoría involucrada: Alimentación.  
Período: 2024-01-01 a 2026-06-30.

**Evidencia cuantitativa**

- `total_transactions`: 323
- `average_transactions_per_month`: 10.77
- `coverage_percentage`: 100.0

**Interpretación técnica:** La recurrencia transaccional es superior a la de las demás categorías del dataset simulado.

**Relevancia predictiva:** La frecuencia aporta observaciones repetidas para estudiar la evolución temporal futura de los gastos.

### P03 - Recurrencia y estabilidad relativa en Pago de deudas y créditos

Categoría recurrente con la menor variabilidad relativa entre las alternativas de alta cobertura no seleccionadas como dominantes.

Categoría involucrada: Pago de deudas y créditos.  
Período: 2024-01-01 a 2026-06-30.

**Evidencia cuantitativa**

- `coverage_percentage`: 100.0
- `average_monthly_amount`: 131339.73
- `standard_deviation_monthly_amount`: 10198.41
- `coefficient_of_variation`: 0.0776

**Interpretación técnica:** La presencia mensual elevada y la dispersión relativa reducida muestran un comportamiento comparativamente estable.

**Relevancia predictiva:** La regularidad puede servir como referencia al comparar posteriormente técnicas para estimar gastos futuros.

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
