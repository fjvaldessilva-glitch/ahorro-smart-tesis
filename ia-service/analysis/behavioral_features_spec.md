# Variables conductuales para el Modelo B de cierre mensual

## Propósito

Esta capa genera nueve variables conductuales —las ocho candidatas seleccionadas desde T39 y un indicador auxiliar de historial— para comparar posteriormente el Modelo A vigente con un Modelo B enriquecido. No contiene objetivos, no entrena modelos y no modifica el artefacto de T40.

Cada cálculo utiliza únicamente movimientos de tipo Gasto cuya fecha sea menor o igual a `cutoff_date`. Los ingresos, fechas posteriores y registros de 2026 se excluyen. El período 2026-01 a 2026-06 permanece reservado para el Ítem 22.

## Definiciones

| Variable | Fórmula y fuente | Cero o ausencia | Ejemplo con corte 2025-08-15 |
| --- | --- | --- | --- |
| `spend_last_7_days` | Suma global entre corte−6 días y corte, inclusive. Es una ventana calendario y puede cruzar el límite mensual. | `0` sin gastos. | Suma de 2025-08-09 a 2025-08-15. |
| `transactions_last_7_days` | Conteo global en la misma ventana inclusiva. | `0` sin gastos. | Tres movimientos en la ventana. |
| `median_transaction_amount` | Mediana de los gastos de la categoría durante el mes actual hasta el corte. | `0` si la categoría no tiene gastos. | Alimentación: mediana de `$12.000` y `$18.000` = `$15.000`. |
| `active_spending_days` | Número de fechas distintas con algún gasto en el mes actual hasta el corte. | `0` sin actividad. | Tres fechas activas. |
| `days_since_last_expense` | Corte menos la fecha del último gasto histórico de la categoría disponible. | Si nunca hubo gasto, se usa `cutoff_date.day`, que representa los días transcurridos del mes. | Último gasto de Alimentación el día 10: `5`. |
| `has_category_expense_history` | Indicador específico de categoría: `1` si existe al menos un gasto histórico conocido hasta el corte; `0` si nunca existió. | `0` expresa ausencia de historial. | Alimentación con gastos conocidos: `1`. |
| `previous_month_comparable_spend` | Suma global del mes anterior desde el día 1 hasta el mismo día del corte; se limita al último día existente del mes anterior. | `0` sin gastos equivalentes. | Julio 1–15, no julio completo. |
| `previous_month_comparable_transactions` | Conteo global del período anterior equivalente. | `0` sin transacciones. | Conteo de julio 1–15. |
| `category_previous_month_comparable_spend` | Suma de la categoría objetivo durante el período anterior equivalente. | `0` sin gastos de la categoría. | Alimentación acumulada en julio 1–15. |

`days_since_last_expense` y `has_category_expense_history` deben interpretarse conjuntamente. El indicador diferencia una recencia real de un valor controlado numéricamente igual. Por ejemplo, una categoría sin historial y otra cuyo último gasto ocurrió hace 15 días pueden compartir `days_since_last_expense = 15`, pero sus indicadores serán `0` y `1`, respectivamente.

## Alcance de las variables

- Globales del escenario: `spend_last_7_days`, `transactions_last_7_days`, `active_spending_days`, `previous_month_comparable_spend` y `previous_month_comparable_transactions`.
- Específicas de categoría: `median_transaction_amount`, `days_since_last_expense`, `has_category_expense_history` y `category_previous_month_comparable_spend`.
- Todas dependen de `cutoff_date` y se repiten o recalculan para cada escenario según su alcance.

## Diferencia respecto del Modelo A

El Modelo A ya contiene acumulados, conteos y promedios hasta el corte, además de totales completos opcionales del mes anterior. Estas variables agregan ritmo reciente, mediana, días activos, recencia y comparaciones históricas sobre días equivalentes. No se incluye el promedio transaccional porque ya está representado en el baseline.

## Prevención de fuga de información

- El filtro `movement.date <= cutoff_date` se aplica antes de calcular cualquier variable.
- Los períodos comparables solo utilizan el mes anterior, nunca fechas posteriores.
- El generador de filas termina en 2025-12.
- No se consulta el total final del mes ni la variable objetivo.
- El módulo produce exclusivamente features y metadatos del escenario.
- Todos los valores son finitos; las ausencias utilizan valores controlados y no divisiones.

## Reproducibilidad

Las entradas se ordenan por fecha, categoría y monto. Las funciones son deterministas y las pruebas verifican que entradas idénticas producen resultados idénticos.
