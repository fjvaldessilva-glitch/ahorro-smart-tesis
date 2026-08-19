# Sprint 05 - Modelo predictivo, integración final y documentación

## Estado del sprint

**En desarrollo.**

## Objetivo del sprint

Desarrollar e integrar el componente predictivo de Ahorro Smart, preparando y analizando datos simulados, identificando patrones habituales de consumo, seleccionando y entrenando un modelo predictivo mediante Scikit-learn, exponiéndolo mediante FastAPI e integrándolo con el backend Node.js/Express y el frontend.

El sprint también contempla la generación y presentación de proyecciones, la evaluación de su margen de error, las pruebas finales funcionales, responsivas y de usabilidad, la corrección de errores, la integración general del sistema y la documentación técnica y de usuario.

Las proyecciones tendrán carácter informativo y no constituyen asesoría financiera.

## Relación con la tesis

Este sprint corresponde a la etapa de desarrollo del componente predictivo, su integración con los componentes existentes de Ahorro Smart y la validación final del sistema. El trabajo debe mantener trazabilidad con las variables predictivas definidas en la ERS, los objetivos específicos del proyecto y los ítems oficiales del Product Backlog, sin incorporar funcionalidades ajenas al alcance de la tesis.

## Ítems del Product Backlog asociados

| Ítem | Descripción | Estado inicial |
| --- | --- | --- |
| 16 | Preparación de datos e identificación de patrones | Completado |
| 17 | Selección y entrenamiento del modelo | Completado |
| 18 | Generación e integración de proyecciones | Completado |
| 19 | Presentación de las proyecciones | Pendiente |
| 21 | Pruebas funcionales, responsivas y de usabilidad | Pendiente |
| 22 | Evaluación del margen de error | Pendiente |
| 23 | Integración general y corrección de errores | Pendiente |
| 24 | Evidencia y cierre por sprint | Pendiente |
| 25 | Documentación técnica y de usuario | Pendiente |

El Ítem 21 pertenece oficialmente al Sprint 05. Aunque se realizaron pruebas durante el Sprint 04, deberá ejecutarse una nueva validación final del sistema completo después de integrar el componente predictivo.

## Criterios de aceptación principales

### Ítem 16 - Preparación de datos e identificación de patrones

- Datos simulados creados.
- Limpieza, transformación y estructuración realizadas.
- Conjunto de datos documentado.
- Sin valores inválidos.
- Variables requeridas disponibles.
- Al menos tres patrones habituales de consumo identificados y documentados.

### Ítem 17 - Selección y entrenamiento del modelo

- Técnica predictiva evaluada y seleccionada.
- Selección justificada.
- Modelo entrenado con los datos preparados.
- Modelo ejecutable.
- Generación de resultados de prueba.

### Ítem 18 - Generación e integración de proyecciones

- Servicio predictivo capaz de generar proyecciones.
- Backend capaz de enviar información al servicio predictivo.
- Backend capaz de recibir la proyección.
- Proyección integrada en la aplicación.
- Proyección almacenable y asociada al usuario.

### Ítem 19 - Presentación de las proyecciones

- Proyección presentada de manera comprensible.
- Indicación de monto o tendencia.
- Indicación del período proyectado.

### Ítem 21 - Pruebas funcionales, responsivas y de usabilidad

- Pruebas finales funcionales, responsivas y de usabilidad ejecutadas.
- Validación en computador.
- Validación en tableta.
- Validación en teléfono móvil.
- Al menos 80 % de casos aprobados.
- Sin errores críticos en los flujos principales.

### Ítem 22 - Evaluación del margen de error

- Proyecciones comparadas con valores esperados.
- Evaluación en un entorno controlado con datos simulados.
- Margen de error objetivo menor o igual al 20 %.

### Ítem 23 - Integración general y corrección de errores

- Componentes integrados.
- Errores críticos corregidos.
- Funcionamiento coordinado del sistema.

### Ítem 24 - Evidencia y cierre por sprint

- Evidencias verificables.
- Registro de pruebas.
- Decisiones técnicas registradas.
- Cierre formal del sprint.

### Ítem 25 - Documentación técnica y de usuario

- Documentación de arquitectura.
- Documentación de instalación.
- Documentación de funcionamiento.
- Documentación de utilización básica del sistema.

Ninguno de estos criterios se considera cumplido al inicio del Sprint 05.

## Variables predictivas definidas en la ERS

### Variables de entrada

| ID | Variable | Tipo | Descripción |
| --- | --- | --- | --- |
| VE-01 | Monto del gasto | Numérica | Valor monetario correspondiente a un movimiento financiero de tipo gasto. |
| VE-02 | Fecha del gasto | Temporal | Fecha correspondiente al movimiento financiero de tipo gasto. |
| VE-03 | Categoría del gasto | Categórica | Categoría asociada al movimiento financiero de tipo gasto. |

### Variable de salida

| ID | Variable | Tipo | Descripción |
| --- | --- | --- | --- |
| VS-01 | Gasto proyectado | Numérica | Valor estimado del gasto futuro generado por el modelo predictivo para un período determinado. |

Durante la preparación de datos podrán generarse variables derivadas cuando resulte necesario para el entrenamiento, siempre manteniendo trazabilidad con las variables iniciales. La definición de esas variables derivadas corresponde al análisis técnico posterior del Ítem 16 y no se establece en esta microtarea.

## Tecnologías oficiales del componente predictivo

- Python.
- Scikit-learn.
- FastAPI.
- Servicio predictivo independiente.
- Comunicación Backend Node.js/Express ↔ FastAPI.

Estas tecnologías se registran como parte del alcance previsto, pero no se instalan ni configuran durante T37.

## Estado heredado al inicio del sprint

- Frontend React operativo.
- Vite utilizado para ejecución y compilación.
- TypeScript utilizado como apoyo técnico.
- Backend Node.js/Express operativo.
- MongoDB y Mongoose operativos.
- Usuarios persistentes.
- Registro e inicio de sesión implementados.
- Contraseñas almacenadas mediante hash.
- JWT implementado.
- Rutas protegidas.
- Movimientos persistentes y aislados por usuario.
- Registro, consulta, edición y eliminación de movimientos implementados.
- Categorías oficiales controladas.
- Historial y filtros implementados.
- Paginación implementada.
- Cálculos financieros implementados.
- Dashboard y gráficos implementados.
- Recordatorio diario implementado.
- Presupuesto mensual por usuario, año y mes implementado.
- Interfaz responsiva validada previamente.
- Pestaña Proyección IA disponible como base visual.
- Servicio predictivo aún no implementado.
- Dataset predictivo aún no preparado.
- Modelo predictivo aún no entrenado.
- FastAPI aún no integrado.
- Proyecciones reales aún no generadas.
- Persistencia de proyecciones aún no implementada.

T35 completó la edición de movimientos desde el frontend y T36 regularizó el presupuesto como presupuesto mensual independiente por usuario, año y mes.

## Orden técnico previsto del sprint

1. Preparación de datos simulados.
2. Limpieza, transformación y estructuración.
3. Identificación de al menos tres patrones habituales de consumo.
4. Selección justificada de la técnica predictiva.
5. Entrenamiento y evaluación inicial del modelo.
6. Implementación del servicio predictivo con FastAPI.
7. Integración Node.js/Express ↔ FastAPI.
8. Generación de proyecciones.
9. Persistencia de las proyecciones asociadas al usuario.
10. Presentación de proyecciones en frontend.
11. Evaluación del margen de error.
12. Pruebas funcionales, responsivas y de usabilidad finales.
13. Integración general y corrección de errores.
14. Documentación técnica y de usuario.
15. Evidencias y cierre del Sprint 05.

Este orden puede ajustarse dentro del sprint cuando exista una necesidad técnica justificada, sin ampliar el alcance definido.

## Restricciones y elementos fuera del alcance

- No se proporciona asesoría financiera profesional.
- No se generan recomendaciones de inversión.
- No se toman decisiones automáticamente por el usuario.
- No existe conexión con bancos.
- No se realiza importación automática de movimientos bancarios.
- No se procesa información bancaria externa.
- No se desarrolla una aplicación móvil nativa.
- No se incorporan modelos generativos.
- No se incorporan funcionalidades distintas de las definidas en la tesis.
- Las proyecciones dependen de la cantidad, calidad y continuidad de los datos disponibles.

## Métricas del proyecto relacionadas

### OE1

- Identificación posterior de al menos tres patrones habituales de consumo a partir de los datos preparados.

### OE3

- Integración del modelo predictivo.
- Endpoints operativos.
- Al menos 85 % de las funcionalidades prioritarias implementadas.
- Sin errores críticos en los flujos principales.

### OE4

- Al menos 80 % de casos de prueba aprobados.
- Pruebas en computador, tableta y teléfono móvil.
- Margen de error de las proyecciones menor o igual al 20 % en escenarios controlados con datos simulados.

## Riesgos relevantes para el sprint

| ID | Riesgo relacionado |
| --- | --- |
| R03 | Registros incompletos o incorrectos. |
| R04 | Margen de error superior al 20 %. |
| R05 | Problemas de integración Node.js/Express - FastAPI. |
| R09 | Dificultades técnicas con el modelo predictivo. |

## Registro de microtareas

Las microtareas se incorporarán individualmente cuando sean definidas y autorizadas.

| ID | Microtarea | Estado | Resultado principal |
| --- | --- | --- | --- |
| T37 | Iniciar documentalmente el Sprint 05 | Completada | Alcance, objetivo, backlog y estructura documental inicial registrados. |
| T38 | Preparar y validar datos simulados | Completada | Dataset sintético reproducible generado, validado y agregado mensualmente. |
| T39 | Analizar datos e identificar patrones habituales de consumo | Completada | Tres patrones cuantificables identificados y documentados de forma reproducible. |
| T40 | Seleccionar y entrenar el modelo predictivo | Completada | Tres técnicas evaluadas; GradientBoostingRegressor seleccionado, reentrenado y guardado. |
| T41 | Crear el servicio predictivo con FastAPI | Completada | Servicio independiente operativo con carga del modelo y endpoints `/health` y `/predict`. |
| T42 | Integrar Node/Express con FastAPI y persistir proyecciones | Completada | Flujo autenticado MongoDB → Express → FastAPI → Express → MongoDB operativo. |

### T38 - Preparar y validar datos simulados

- Se generó un historial de gastos completamente sintético para el período 2024-01-01 a 2026-06-30 mediante la semilla fija `2026`.
- Los datos originales utilizan `date`, `category` y `amount`, manteniendo trazabilidad con VE-02, VE-03 y VE-01, respectivamente.
- Se validaron fechas, categorías, montos positivos y finitos, y ausencia de campos vacíos antes del procesamiento.
- Se derivaron `year`, `month` y `period`, y se calcularon `monthly_amount` y `transaction_count` mediante agrupación mensual por categoría.
- El resumen de validación registra cero fechas, categorías, montos y valores vacíos inválidos.
- Los datos no contienen información personal o financiera real y se destinan exclusivamente al desarrollo y evaluación académica controlada.
- En T38 no se identificaron formalmente patrones de consumo, no se seleccionó un algoritmo y no se entrenó un modelo.
- El Ítem 16 continuó **En desarrollo** al finalizar T38, a la espera de la identificación y documentación formal de patrones en T39.

### T39 - Analizar datos e identificar patrones habituales de consumo

- Se analizaron los 787 movimientos simulados y las 250 filas mensuales procesadas de T38, correspondientes a 30 meses y 10 categorías oficiales.
- Por categoría se calcularon monto y transacciones totales, presencia mensual, cobertura, promedio, mediana, desviación estándar, coeficiente de variación, frecuencia media y participación en el gasto total.
- El análisis temporal incluyó evolución mensual, promedios por mes calendario y tendencia descriptiva mediante regresión lineal simple.
- Se identificaron y documentaron tres patrones respaldados: participación monetaria dominante de Vivienda, alta frecuencia de Alimentación y recurrencia con estabilidad relativa de Pago de deudas y créditos.
- Se generaron `patterns_summary.json` y `patterns_report.md`; la repetición del análisis sobre los mismos datos produce resultados idénticos.
- T38 cubrió la generación, limpieza, transformación, estructuración y validación; T39 cubrió el análisis y la identificación formal de al menos tres patrones.
- Con ambos resultados, el Ítem 16 quedó **Completado**. Al finalizar T39, el Ítem 17 todavía permanecía pendiente y no se había seleccionado ni entrenado un algoritmo.

### T40 - Seleccionar y entrenar el modelo predictivo

- Se construyó internamente un panel mensual completo con las 10 categorías oficiales y montos cero cuando no existían movimientos, sin modificar los datasets de T38.
- Se generaron características sin fuga futura: categoría, mes, índice temporal, tres rezagos, promedio móvil de los tres meses anteriores y representación cíclica del mes.
- Se utilizó una división cronológica: 210 filas de entrenamiento entre 2024-04 y 2025-12, y 60 filas de prueba entre 2026-01 y 2026-06.
- Se evaluaron LinearRegression, RandomForestRegressor y GradientBoostingRegressor con idénticos datos, variables y preprocesamiento.
- GradientBoostingRegressor fue seleccionado por obtener el menor WAPE (`20,1277 %`), respaldado por MAE y RMSE, y posteriormente se reentrenó con las 270 filas supervisadas disponibles hasta 2026-06.
- El pipeline final fue guardado, cargado nuevamente y produjo una predicción técnica finita para julio de 2026.
- Las métricas de T40 constituyen una evaluación inicial para seleccionar el modelo. El resultado no cumple por sí solo el objetivo de error menor o igual al 20 % y el Ítem 22 permanece **Pendiente** para su evaluación formal.
- Se generaron `model_evaluation.json`, `model_selection_report.md`, `model_metadata.json` y `expense_forecast_model.joblib` de forma reproducible.
- Al cumplirse la evaluación de tres técnicas, selección justificada, entrenamiento, almacenamiento, carga y prueba del modelo, el Ítem 17 queda **Completado**. Los Ítems 18 y 22 no se iniciaron ni completaron.

### T41 - Crear el servicio predictivo con FastAPI

- Se instalaron FastAPI y Uvicorn, y se creó un servicio predictivo independiente que reutiliza el modelo de T40 sin reentrenarlo.
- El servicio carga una sola vez el pipeline Joblib y sus metadatos, e informa su disponibilidad mediante `GET /health`.
- `POST /predict` recibe gastos históricos, rechaza información del período objetivo o posterior, agrega por mes y categoría y replica las variables temporales de T40 sin fuga de información futura.
- Se generan diez proyecciones por categoría y un total mensual; cualquier valor negativo se conserva como predicción original y se ajusta explícitamente a cero solo en la salida funcional.
- Se validaron historial vacío o insuficiente, categorías, fechas, montos y períodos inválidos, además de predicciones finitas y disponibilidad del modelo.
- La prueba controlada para julio de 2026 utilizó 30 meses históricos, produjo un total proyectado de `$1.346.211,81` y no requirió ajustes por valores negativos.
- Las pruebas automáticas y las comprobaciones manuales de `/health`, `/docs` y `/predict` finalizaron correctamente.
- T41 queda **Completada**. El Ítem 18 pasa a **En desarrollo** porque todavía faltan la integración con Node.js/Express, la persistencia y el flujo completo. Los Ítems 19 y 22 permanecen **Pendientes**.

### T42 - Integrar Node/Express con FastAPI y persistir proyecciones

- Se creó el modelo Mongoose `Projection` con usuario, período objetivo, modelo, diez resultados por categoría, total proyectado, meses históricos y fecha de generación.
- Se incorporó un índice único compuesto por `user + targetPeriod` y persistencia mediante upsert para actualizar una proyección sin generar duplicados.
- El backend utiliza `IA_SERVICE_URL` y `fetch` nativo con timeout para comunicarse con FastAPI, sin agregar dependencias Node.js.
- `POST /api/projections/generate` obtiene exclusivamente movimientos `Gasto` del usuario autenticado anteriores al período objetivo, llama a FastAPI, valida su respuesta y persiste el resultado.
- `GET /api/projections?targetPeriod=YYYY-MM` recupera únicamente la proyección del usuario autenticado y devuelve 404 ante otro usuario o un período inexistente.
- Las rutas utilizan el middleware JWT existente y nunca aceptan un identificador de usuario desde el body como autoridad.
- Las pruebas aisladas verificaron autenticación, validación del período, FastAPI no disponible, generación real, persistencia, recuperación, upsert, índice único y aislamiento entre usuarios.
- La prueba integral para septiembre de 2026 envió tres gastos históricos desde MongoDB, excluyó un ingreso, persistió diez categorías y un total proyectado de `$382.250,18`.
- Los usuarios y movimientos aislados de prueba fueron eliminados al finalizar; los conteos previos de users, movements y budgets se mantuvieron intactos.
- T42 queda **Completada** y el Ítem 18 queda **Completado** al estar operativas la generación, integración entre servicios, persistencia y recuperación. Los Ítems 19 y 22 permanecen **Pendientes**.

## Pruebas

Las pruebas se documentarán durante las microtareas correspondientes y deberán consolidarse después de integrar el componente predictivo.

| Área | Prueba prevista | Estado |
| --- | --- | --- |
| Datos simulados | Generación reproducible, validación estricta y agregación mensual | Completada en T38 |
| Análisis de patrones | Métricas descriptivas, selección respaldada y reproducibilidad | Completada en T39 |
| Modelo predictivo | Comparación temporal de tres técnicas, entrenamiento, carga y resultado controlado | Completada en T40 |
| Servicio predictivo | Carga del modelo, endpoints, validaciones y proyección controlada | Completada en T41 |
| Integración | Comunicación Node.js/Express ↔ FastAPI | Completada en T42 |
| Proyecciones | Generación y persistencia | Completada en T42; presentación pendiente en Ítem 19 |
| Margen de error | Comparación con valores esperados | Pendiente |
| Sistema completo | Pruebas funcionales, responsivas y de usabilidad | Pendiente |

## Evidencias

Las evidencias se incorporarán por microtarea y durante el cierre formal del Sprint 05.

| ID de evidencia | Descripción | Estado | Observaciones |
| --- | --- | --- | --- |
| Por registrar | Pendiente de generación | Pendiente | Sin evidencias nuevas al inicio del sprint. |

## Commits

Los commits se registrarán cronológicamente después de completar y revisar cada microtarea.

| Orden | Commit | Microtarea relacionada |
| --- | --- | --- |
| Por registrar | Pendiente | Pendiente |

## Sprint Review

Pendiente hasta completar y validar el incremento comprometido para el Sprint 05.

## Retrospectiva

Pendiente hasta el cierre del Sprint 05.
