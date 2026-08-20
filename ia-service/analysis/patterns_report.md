# Análisis ampliado de patrones habituales de consumo

## Alcance temporal

El dataset contiene 787 gastos simulados entre 2024-01-01 y 2026-06-30 (30 meses). Patrones y variables candidatas usan exclusivamente 624 transacciones de 2024-01 a 2025-12. La reserva 2026-01 a 2026-06 no se utilizó para seleccionar variables, ajustar umbrales, comparar modelos ni evaluar rendimiento predictivo.

## Métricas generales de desarrollo

- Gasto total: **$31.994.153**; transacciones: **624**.
- Gasto promedio diario: **$43.768**.
- Promedio / mediana / máximo por transacción: **$51.273 / $30.419 / $445.804**.
- Días con gasto / sin gasto: **432 / 299**.
- Transacciones por día calendario / día activo: **0.8536 / 1.4444**.

## Ventanas, ritmo y correlación

- Corte 2025-12-31: últimos 14 días $290.487 y 11 transacciones.
- Siete días anteriores → últimos 7 días, gasto: $157.549 → $132.938; variación -15.62 %.
- Siete días anteriores → últimos 7 días, transacciones: 5 → 6; variación 20.0 %.
- Siete días anteriores → últimos 7 días, monto promedio: $31.510 → $22.156; variación -29.68 %.
- Primer 50 % vs segundo 50 %: **desaceleración**. Umbrales: aceleración > 10 %, desaceleración < -10 %, estabilidad entre -10 % y 10 %.
- Pendiente acumulada: $39.033 diarios.
- Pearson: **0.563125**; Spearman: **0.916852**; observaciones: **731 días**.

**Una correlación estadística no permite establecer causalidad.** Los resultados muestran correlación/asociación y no demuestran causalidad.

## Descomposición de aumentos

- Anterior (2024-03-19 a 2024-03-25) → actual (2024-03-26 a 2024-04-01): $203.558 → $445.154; asociación principal: **mayor frecuencia**; transacciones 5 → 13; monto medio $40.712 → $34.243.
- Anterior (2025-03-29 a 2025-04-04) → actual (2025-04-05 a 2025-04-11): $113.227 → $635.378; asociación principal: **mayor monto promedio**; transacciones 6 → 6; monto medio $18.871 → $105.896.
- Anterior (2024-09-27 a 2024-10-03) → actual (2024-10-04 a 2024-10-10): $79.713 → $789.992; asociación principal: **ambos factores**; transacciones 2 → 10; monto medio $39.856 → $78.999.

La descomposición usa gasto = frecuencia × monto medio y no constituye recomendación financiera.

## Comparación mensual equivalente

- Anterior: **2025-11-01 a 2025-11-30**.
- Actual: **2025-12-01 a 2025-12-30**.
- Gasto anterior → actual: $1.362.303 → $1.203.254; variación -11.68 %.
- Transacciones anteriores → actuales: 28 → 24; variación -14.29 %.
- Promedio diario anterior → actual: $45.410 → $40.108; variación -11.68 %.

Se comparan 30 días en cada período; no se compara un mes parcial con uno completo.

## Categorías

| Categoría | Gasto | Transacciones | Promedio | Mediana | Participación | Ritmo reciente |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Alimentación | $8.048.917 | 257 | $31.319 | $31.926 | 25.16 % | desaceleración |
| Transporte | $3.371.467 | 171 | $19.716 | $19.318 | 10.54 % | aceleración |
| Vivienda | $10.132.105 | 24 | $422.171 | $421.610 | 31.67 % | sin base suficiente |
| Servicios básicos | $2.126.011 | 24 | $88.584 | $90.378 | 6.64 % | sin base suficiente |
| Salud | $627.495 | 11 | $57.045 | $60.351 | 1.96 % | sin base suficiente |
| Educación | $833.635 | 11 | $75.785 | $75.515 | 2.61 % | sin base suficiente |
| Pago de deudas y créditos | $3.141.153 | 24 | $130.881 | $132.435 | 9.82 % | sin base suficiente |
| Entretenimiento | $2.446.232 | 66 | $37.064 | $37.720 | 7.65 % | desaceleración |
| Mascotas | $573.072 | 19 | $30.162 | $30.020 | 1.79 % | sin base suficiente |
| Otros gastos | $694.066 | 17 | $40.827 | $34.940 | 2.17 % | sin base suficiente |

El JSON incluye ventanas, cambio, frecuencia, recencia, peso histórico, variabilidad y comparación mensual equivalente por categoría.

## Patrones definitivos

### P01 - Participación monetaria dominante de Vivienda

- Métrica: `spending_share_percentage` = `31.67`.
- Período: 2024-01-01 a 2025-12-31.
- Interpretación: Mayor peso monetario del período de desarrollo.
- Limitación: Escenario simulado.

### P02 - Frecuencia dominante de Alimentación

- Métrica: `transactions` = `257`.
- Período: 2024-01-01 a 2025-12-31.
- Interpretación: Mayor cantidad de transacciones.
- Limitación: Frecuencia no equivale a gasto total.

### P03 - Estabilidad mensual relativa de Pago de deudas y créditos

- Métrica: `monthly_coefficient_of_variation` = `0.0749`.
- Período: 2024-01-01 a 2025-12-31.
- Interpretación: Menor dispersión relativa entre categorías no dominantes.
- Limitación: Puede no repetirse fuera del dataset.

### P04 - Asociación entre frecuencia diaria y gasto diario

- Métrica: `pearson` = `0.563125`.
- Período: 2024-01-01 a 2025-12-31.
- Interpretación: Asociación estadística cuantificada.
- Limitación: Una correlación estadística no permite establecer causalidad.

### P05 - Ritmo reciente: desaceleración

- Métrica: `spend_change_last_7_vs_previous_7` = `-15.62`.
- Período: corte 2025-12-31.
- Interpretación: Cambio entre ventanas equivalentes.
- Limitación: Sensible a gastos puntuales.

## Variables candidatas para T40

`spend_last_7_days`, `spend_last_14_days`, `transactions_last_7_days`, `transactions_last_14_days`, `spend_change_last_7_vs_previous_7`, `transaction_count_change_last_7_vs_previous_7`, `recent_daily_spend_rate`, `average_transaction_amount`, `median_transaction_amount`, `max_transaction_amount`, `active_spending_days`, `days_since_last_expense`, `category_share`, `previous_month_comparable_spend`, `previous_month_comparable_transactions`, `category_previous_month_comparable_spend`, `transaction_frequency_spend_correlation`, `cumulative_spend_slope`.

Disponibilidad buena en desarrollo. Redundancias: gasto 7 días con su tasa diaria; gasto 14 días con dos ventanas de 7; `category_share` con peso histórico. Frecuencia, estadísticas de monto, recencia, comparación mensual, categoría y pendiente aportan señales conceptualmente distintas. T39 no incorpora variables ni decide un modelo.

## Auditoría M→M+1

- Meses consecutivos: **30**; transiciones globales: **29**; pares categoría-transición: **290**.
- Desarrollo: **23** transiciones. División posible: objetivos 2024-02 a 2025-06 para desarrollo, 2025-07 a 2025-12 para validación y 2026-01 a 2026-06 reservados para el Ítem 22.
- Es una auditoría de viabilidad; no se entrenó un modelo M+1. La cantidad de transiciones independientes es limitada.

## Limitaciones

Datos simulados, ventanas sensibles a gastos puntuales, asociaciones sin causalidad y sin recomendaciones financieras.
