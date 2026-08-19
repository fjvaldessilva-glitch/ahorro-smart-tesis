# Selección y entrenamiento del modelo predictivo

## 1. Propósito

Evaluar técnicas predictivas reproducibles y seleccionar un modelo para estimar `monthly_amount` de una categoría en un período mensual futuro. Esta estimación operacionaliza VS-01, gasto proyectado.

## 2. Datos utilizados

Se utilizó exclusivamente el panel mensual derivado de los gastos 100 % simulados de T38: 30 meses, desde 2024-01 hasta 2026-06, y las 10 categorías oficiales. Las combinaciones sin movimientos se representaron internamente con monto cero, sin modificar los datasets de origen.

## 3. Variables utilizadas

Las características fueron `category`, `month`, `trend_index`, `lag_1`, `lag_2`, `lag_3`, `rolling_mean_3`, `month_sin` y `month_cos`. Los lags y la media móvil utilizan exclusivamente los tres meses anteriores al objetivo.

## 4. División temporal

- Entrenamiento de evaluación: 2024-04 a 2025-12 (210 filas).
- Prueba: 2026-01 a 2026-06 (60 filas).
- División cronológica, sin selección aleatoria.

## 5. Técnicas evaluadas

- LinearRegression.
- RandomForestRegressor (`random_state=2026`).
- GradientBoostingRegressor (`random_state=2026`).

Los tres candidatos utilizaron las mismas características, preprocesamiento, filas de entrenamiento y filas de prueba. `category` se codificó con `OneHotEncoder(handle_unknown="ignore")`.

## 6. Métricas obtenidas

| Candidato | MAE | RMSE | WAPE | MAPE sobre objetivos > 0 |
| --- | ---: | ---: | ---: | ---: |
| LinearRegression | 30204.3980 | 41416.2289 | 21.6617 % | 29.3406 % |
| RandomForestRegressor | 29789.9538 | 39860.6669 | 21.3645 % | 24.8029 % |
| GradientBoostingRegressor | 28065.3463 | 40147.3019 | 20.1277 % | 22.8749 % |

WAPE se calculó sobre todos los objetivos; MAPE solo sobre los 49 objetivos de prueba mayores que cero.

## 7. Modelo seleccionado

**GradientBoostingRegressor**, por obtener el menor WAPE en la prueba temporal.

## 8. Justificación de la selección

GradientBoostingRegressor obtuvo el menor WAPE (20.1277 %) sobre el mismo conjunto de prueba cronológico. MAE y RMSE respaldan la comparación. La alternativa representa relaciones no lineales, mantiene una complejidad razonable para el panel reducido, es reproducible y puede mantenerse dentro de un pipeline único; su capacidad descriptiva se limita al escenario sintético evaluado.

Las métricas son una evaluación inicial para seleccionar el modelo. La comprobación formal del margen de error corresponde al Ítem 22 y no se cierra en T40.

## 9. Entrenamiento final

Una instancia limpia del candidato seleccionado fue reentrenada con las 270 filas supervisadas disponibles entre 2024-04 a 2026-06. El artefacto se guardó, volvió a cargarse y produjo para la prueba técnica de julio de 2026 un valor finito de $351.528 en la categoría Alimentación.

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
