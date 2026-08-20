# Modelo predictivo para proyección de cierre mensual

## 1. Propósito del modelo

Ahorro Smart utiliza un modelo predictivo para estimar el gasto total esperado al cierre del mes en curso a partir de los gastos registrados hasta una fecha de corte dentro del mismo período. La actividad parcial del mes constituye la principal fuente de información; el historial de meses anteriores funciona únicamente como señal complementaria y opcional.

## 2. Objetivo predictivo

Estimar por categoría el gasto total al cierre del mismo mes en curso. La suma de las diez categorías produce `total_month_end_projection`. El modelo puede generar una estimación desde el primer mes cuando existe al menos un gasto válido y no exige meses anteriores. El presupuesto mensual no se utiliza como variable de entrada: posteriormente podrá compararse con la proyección para calcular la desviación presupuestaria esperada. El gasto del mes anterior también podrá utilizarse como información complementaria de tendencia cuando exista.

## 3. Datos utilizados

Se utilizaron exclusivamente las 787 transacciones simuladas de `simulated_expenses.csv`, desde 2024-01 hasta 2026-06. No se utilizaron ingresos ni presupuesto y el dataset original no fue modificado.

## 4. Construcción de escenarios parciales

Por cada mes se generaron fotografías acumuladas en los días 5, 10, 15, 20 y 25, además del primer día con movimientos cuando aportaba un corte diferente. Solo se conservaron cortes con actividad observada y anteriores al último día. Se generaron 177 escenarios y 1770 filas por categoría. Los movimientos posteriores al corte se usaron únicamente como objetivo histórico final, evitando fuga de información.

## 5. Variables utilizadas

Se utilizaron: `category`, `month`, `day_of_month`, `days_in_month`, `month_progress`, `category_spend_to_date`, `category_transactions_to_date`, `total_spend_to_date`, `total_transactions_to_date`, `category_average_transaction_to_date`, `overall_average_transaction_to_date`, `month_sin`, `month_cos`, `previous_month_category_total`, `previous_month_total`, `has_previous_month_data`. Los promedios hasta la fecha se incorporaron como señales simples y justificables.

## 6. Historial anterior opcional

`previous_month_category_total` y `previous_month_total` toman cero cuando no existe mes anterior, mientras `has_previous_month_data` distingue esa ausencia de un total real igual a cero. El historial anterior no es requisito.

## 7. División temporal

- Entrenamiento para selección: 2024-01 a 2025-06 (1060 filas).
- Validación para selección: 2025-07 a 2025-12 (360 filas).
- Reserva independiente para el Ítem 22: 2026-01 a 2026-06, no usada para entrenar, seleccionar ni informar el rendimiento de T40.

## 8. Técnicas evaluadas

LinearRegression, RandomForestRegressor y GradientBoostingRegressor utilizaron las mismas filas y variables. La categoría se procesó con `OneHotEncoder(handle_unknown="ignore")`; los modelos de ensamble usaron `random_state=2026`.

## 9. Baseline de ritmo de gasto

La referencia ingenua extrapoló `category_spend_to_date / month_progress`. En el total mensual obtuvo MAE 727786.6042, RMSE 970399.3407 y WAPE 55.0917 %.

## 10. Métricas obtenidas

| Candidato | MAE total | RMSE total | WAPE total | Ajustes negativos |
| --- | ---: | ---: | ---: | ---: |
| LinearRegression | 54894.3302 | 67676.8420 | 4.1554 % | 8 |
| RandomForestRegressor | 110484.1978 | 130701.8034 | 8.3634 % | 0 |
| GradientBoostingRegressor | 63809.6382 | 78832.2399 | 4.8302 % | 0 |

Las predicciones negativas se conservaron como `raw_prediction` para evaluación y se ajustaron mediante `max(0, raw_prediction)` en el resultado funcional agregado. El JSON de evaluación incluye también WAPE por categoría.

## 11. Modelo seleccionado

**LinearRegression**, por obtener el menor WAPE del total mensual en la validación cronológica. LinearRegression alcanzó el menor WAPE total (4.1554 %) sobre los mismos escenarios de validación; MAE y RMSE totales respaldan la selección.

## 12. Entrenamiento final

Una instancia limpia se entrenó con 1420 filas entre 2024-01 y 2025-12. El nuevo artefacto se guardó por separado y se recargó correctamente. No se utilizaron los meses reservados de 2026.

## 13. Relación con la ERS

- VE-01 origina acumulados, conteos, promedios y totales históricos opcionales.
- VE-02 origina mes, día, días del mes, progreso y representación cíclica.
- VE-03 se utiliza directamente como categoría.
- VS-01 corresponde al gasto estimado al cierre del mismo mes en curso.

## 14. Reserva para evaluación del Ítem 22

Los meses 2026-01 a 2026-06 quedaron completamente excluidos de entrenamiento, selección e hiperparámetros. El Ítem 22 permanece pendiente y no se declara todavía cumplimiento del objetivo de error.

## 15. Limitaciones

- El modelo se entrenó con datos simulados y su rendimiento puede diferir con datos reales.
- Los cortes representan momentos específicos del mes y no todas las fechas posibles.
- Una sola transacción permite producir una estimación, pero implica mayor incertidumbre.
- La estacionalidad y el historial opcional se apoyan en un período temporal reducido.
- La proyección es informativa y no constituye asesoría financiera.
