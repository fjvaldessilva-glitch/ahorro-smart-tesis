# T40.3.2 — Evaluación experimental de variables conductuales para la proyección de cierre mensual

## 1. Contexto del experimento

En el marco del desarrollo del componente predictivo de Ahorro Smart, la microtarea T40 estableció un modelo de referencia para estimar el gasto total esperado al cierre del mes en curso. Este modelo utiliza la actividad financiera observada hasta una fecha de corte y genera proyecciones desagregadas por categoría de gasto. Posteriormente, el análisis de patrones de consumo realizado en T39 permitió identificar atributos conductuales relacionados con el ritmo reciente de gasto, la frecuencia transaccional y el comportamiento comparable del período anterior.

La etapa T40.3.2 evaluó si la incorporación controlada de dichos atributos podía mejorar la capacidad predictiva del modelo vigente. El estudio se planteó como un experimento comparativo y no como un reemplazo automático del modelo productivo. Por esta razón, todos los ajustes y predicciones se ejecutaron en memoria, sin modificar el artefacto `month_end_forecast_model.joblib` ni la integración existente con FastAPI.

## 2. Objetivo

El objetivo fue comparar el Modelo A vigente con distintas variantes enriquecidas mediante variables conductuales, manteniendo constantes el algoritmo, la variable objetivo, las observaciones, los escenarios, las fechas de corte y la separación temporal. De este modo, cualquier diferencia de desempeño podía atribuirse principalmente al conjunto de variables incorporado.

## 3. Hipótesis evaluada

La hipótesis de trabajo estableció que la incorporación de información conductual disponible hasta la fecha de corte podría reducir el error de la proyección de cierre mensual frente al modelo de referencia. En particular, se esperaba que el ritmo reciente, la actividad transaccional y la comparación con días equivalentes del mes anterior aportaran información complementaria a los acumulados ya utilizados por el Modelo A.

La hipótesis no implicó que un mayor número de variables produciría necesariamente un mejor resultado. También se evaluaron posibles deterioros asociados con redundancia, colinealidad e inestabilidad temporal.

## 4. Diseño experimental

Se aplicó un diseño de ablación compuesto por cinco variantes: A, B1, B2, B3 y B. Todas utilizaron `LinearRegression`, la misma variable objetivo —`category_month_end_total`— y las mismas filas de escenarios categoría-fecha de corte. El conjunto A actuó como control, mientras que B1, B2 y B3 incorporaron grupos temáticos de variables. La variante B reunió las nueve variables conductuales.

El experimento utilizó cuatro pliegues de validación temporal interna dentro del período de entrenamiento y una validación final de desarrollo entre julio y diciembre de 2025. Se evaluaron métricas globales, mensuales, por categoría y por fecha de corte. También se contabilizaron las predicciones negativas previas al ajuste de salida y se examinaron correlaciones, rango matricial y número de condición.

Los criterios de sustitución se definieron antes de interpretar los resultados. Una variante debía reducir el WAPE y alcanzar una mejora mínima de 0,20 puntos porcentuales o de 5 % relativo; mejorar al menos cuatro de los seis meses de validación; no deteriorar MAE ni RMSE en más de 2 %; no aumentar significativamente las predicciones negativas; y no provocar deterioros graves en categorías de bajo volumen.

## 5. Modelo A

El Modelo A corresponde al baseline vigente de T40. Utiliza 16 variables: `category`, `month`, `day_of_month`, `days_in_month`, `month_progress`, `category_spend_to_date`, `category_transactions_to_date`, `total_spend_to_date`, `total_transactions_to_date`, `category_average_transaction_to_date`, `overall_average_transaction_to_date`, `month_sin`, `month_cos`, `previous_month_category_total`, `previous_month_total` y `has_previous_month_data`.

Este modelo representa la referencia técnica debido a que reproduce el comportamiento previamente validado, con un WAPE total de 4,1554 % en la validación final de desarrollo.

## 6. Variantes B1, B2, B3 y B

- **B1 — ritmo reciente:** añade `spend_last_7_days` y `transactions_last_7_days`.
- **B2 — comportamiento transaccional:** añade `median_transaction_amount`, `active_spending_days`, `days_since_last_expense` y `has_category_expense_history`.
- **B3 — comparación histórica equivalente:** añade `previous_month_comparable_spend`, `previous_month_comparable_transactions` y `category_previous_month_comparable_spend`.
- **B — modelo conductual completo:** añade simultáneamente las nueve variables conductuales de B1, B2 y B3.

Estas variantes permitieron determinar el aporte de cada grupo sin confundirlo con el efecto de incorporar todas las variables de manera conjunta.

## 7. Variables utilizadas

Las variables conductuales fueron calculadas exclusivamente con información conocida hasta `cutoff_date`, evitando el uso de gastos posteriores al corte. `spend_last_7_days` y `transactions_last_7_days` describen intensidad y frecuencia recientes. `median_transaction_amount`, `active_spending_days`, `days_since_last_expense` y `has_category_expense_history` representan características del comportamiento transaccional y permiten distinguir una categoría sin historial de otra cuya última operación presenta una recencia equivalente al valor controlado. Finalmente, las tres variables comparables del mes anterior restringen la observación histórica a la misma cantidad de días transcurridos en el mes actual, en lugar de utilizar el mes anterior completo.

La actividad parcial del mes continuó siendo la fuente principal de información. El presupuesto mensual no participó como variable predictiva y se mantuvo reservado para la comparación posterior entre proyección y planificación financiera.

## 8. Dataset y separación temporal

El conjunto experimental comprendió datos entre enero de 2024 y diciembre de 2025. Cada variante utilizó 1.420 filas: 1.060 para entrenamiento y 360 para validación final, correspondientes a las diez categorías oficiales de gasto. No se detectaron valores faltantes.

La separación temporal fue la siguiente:

- entrenamiento: enero de 2024 a junio de 2025;
- validación final de desarrollo: julio de 2025 a diciembre de 2025;
- reserva: enero de 2026 a junio de 2026.

El período de reserva 2026-01 a 2026-06 fue excluido completamente del ajuste, selección y análisis de T40.3.2, con el propósito de conservarlo para la evaluación posterior definida en el Ítem 22.

## 9. Métricas utilizadas

Se utilizaron el error absoluto medio (MAE), la raíz del error cuadrático medio (RMSE) y el error porcentual absoluto ponderado (WAPE). El MAE representa la magnitud promedio del error en unidades monetarias; el RMSE incrementa la penalización de errores de mayor magnitud; y el WAPE expresa el error absoluto total en relación con el gasto real agregado.

La evaluación incluyó WAPE y MAE por categoría, métricas mensuales y por fecha de corte, cantidad de predicciones negativas antes de aplicar controles de salida y estabilidad temporal mediante la dispersión del WAPE mensual. Esta combinación evitó seleccionar una variante únicamente por una mejora global que ocultara deterioros relevantes en períodos o categorías específicos.

## 10. Resultados comparativos

| Variante | MAE | RMSE | WAPE | Predicciones negativas | Meses mejorados frente a A | Decisión |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| A | 54.894,3302 | 67.676,8420 | 4,1554 % | 8 | — | Referencia |
| B1 | 53.804,9237 | 67.278,6005 | 4,0729 % | 8 | 3 | No aceptada |
| B2 | 62.550,5581 | 73.932,7348 | 4,7349 % | 1 | 2 | No aceptada |
| B3 | 52.647,3167 | 66.351,6913 | 3,9853 % | 2 | 5 | No aceptada |
| B | 65.073,9912 | 76.258,7627 | 4,9259 % | 0 | 2 | No aceptada |

B3 obtuvo el menor WAPE observado. Frente a A, redujo el indicador en 0,1701 puntos porcentuales, equivalente a una mejora relativa de 4,0935 %. También disminuyó el MAE en 4,0933 % y el RMSE en 1,9581 %, y mejoró cinco de los seis meses de validación. No obstante, la reducción no alcanzó el umbral mínimo predefinido de 0,20 puntos o 5 % relativo.

En la validación temporal interna, los WAPE medios fueron 8,0102 % para A, 8,0742 % para B1, 7,2303 % para B2, 7,0824 % para B3 y 4,3622 % para B. B3 y B mejoraron tres de cuatro pliegues frente a A. Sin embargo, el buen promedio interno de B no se sostuvo en la validación final, donde su WAPE aumentó a 4,9259 %.

## 11. Análisis de mejoras y deterioros

B1 produjo una mejora global limitada: redujo el WAPE en 0,0825 puntos y mejoró tres meses, pero no evidenció una ganancia suficientemente amplia ni consistente. B2 empeoró el WAPE en 0,5795 puntos, incrementó MAE y RMSE, y registró un deterioro de 34,2823 puntos de WAPE en Salud, categoría de bajo volumen. La variante completa B presentó el mayor deterioro global, con un WAPE 0,7705 puntos superior al baseline y una degradación de 59,0879 puntos en Salud.

B3 mostró el comportamiento más favorable. Respecto de A, mejoró el WAPE de Otros gastos en 14,7856 puntos, Transporte en 5,1759, Servicios básicos en 4,5095, Pago de deudas y créditos en 4,2131 y Vivienda en 3,1168. En contraste, deterioró Mascotas en 3,7377 puntos, Salud en 3,2902, Entretenimiento en 2,4414, Educación en 0,8252 y Alimentación en 0,7342. Estos resultados muestran que las comparaciones históricas equivalentes aportan señal predictiva, pero su beneficio no es uniforme entre categorías.

La diferencia entre el desempeño interno de B y su resultado final sugiere sensibilidad al período de validación y un riesgo de generalización. Asimismo, la disminución de predicciones negativas no fue suficiente por sí sola para justificar una variante con mayores errores globales.

## 12. Análisis de colinealidad

El Modelo A presentó un número de condición estandarizado de 107,3159 y una correlación de 0,998570 entre `day_of_month` y `month_progress`. En la variante completa B, el número de condición aumentó a 517,8590. Aunque la matriz numérica mantuvo rango completo —24 columnas y rango 24—, el incremento indica una mayor sensibilidad derivada de relaciones lineales fuertes entre variables.

En B se identificaron cinco pares con correlación absoluta igual o superior a 0,95: `day_of_month` con `month_progress` (0,998570); `day_of_month` con `active_spending_days` (0,962999); `month_progress` con `active_spending_days` (0,959453); `total_transactions_to_date` con `active_spending_days` (0,955010); y `category_average_transaction_to_date` con `median_transaction_amount` (0,999971).

La última asociación demuestra una redundancia prácticamente total entre el promedio y la mediana transaccional en el dataset experimental. En conjunto, estos resultados explican por qué añadir todas las variables no produjo una mejora acumulativa y justifican futuras pruebas de ablación o regularización antes de ampliar el modelo.

## 13. Decisión técnica final

Se decidió mantener el Modelo A como modelo oficial de Ahorro Smart. Ninguna variante enriquecida cumplió simultáneamente todos los criterios de sustitución. B3 fue la alternativa con mejor desempeño observado y evidenció que la comparación histórica equivalente constituye una línea de investigación prometedora; sin embargo, su mejora quedó por debajo del umbral mínimo establecido.

Una iteración futura podrá tomar B3 como base y evaluar individualmente sus variables, así como incorporar de forma selectiva atributos de B1. No se recomienda adoptar B2 ni el conjunto completo B sin nuevas pruebas, debido al deterioro de la validación final y al aumento de colinealidad. Esta decisión conserva la trazabilidad metodológica y evita sustituir el modelo por una mejora insuficiente o inestable.

## 14. Conclusión

El experimento T40.3.2 permitió evaluar de manera controlada el aporte de variables conductuales derivadas de los patrones de consumo. Los resultados indican que la información comparable del mes anterior mejora la proyección en la mayoría de los meses de validación y en varias categorías relevantes. No obstante, la magnitud global de esta mejora no alcanzó el criterio preestablecido para reemplazar el modelo vigente.

La evaluación también demostró que una mayor cantidad de variables no garantiza una mejor capacidad de generalización. La variante completa obtuvo resultados internos favorables, pero presentó un deterioro sustantivo en la validación final y una condición numérica considerablemente superior. Por tanto, la selección conservadora del Modelo A se sustenta tanto en las métricas predictivas como en criterios de estabilidad y parsimonia.

En términos académicos, T40.3.2 aporta evidencia empírica para orientar la evolución del componente predictivo de Ahorro Smart. La principal contribución consiste en identificar las comparaciones históricas equivalentes como una señal potencialmente útil, al mismo tiempo que se documentan los riesgos de redundancia e inestabilidad asociados con un enriquecimiento indiscriminado. Estos hallazgos proporcionan una base reproducible para futuras evaluaciones sin comprometer la reserva temporal destinada a la validación final del sistema.
