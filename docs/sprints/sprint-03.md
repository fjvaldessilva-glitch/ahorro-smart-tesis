# Sprint 3 - Integración frontend-backend, endpoints, consulta y visualización financiera

## Estado del sprint

**Completado.**

## Objetivo del sprint

Integrar el frontend con el backend mediante los endpoints definidos e implementar la consulta del historial, los filtros por fecha, los cálculos financieros, el dashboard, los gráficos actualizados y el recordatorio diario, junto con las pruebas técnicas y los ajustes de usabilidad necesarios para validar el incremento.

## Relación con la tesis

Este sprint avanzó en la integración y visualización financiera del sistema web responsivo Ahorro Smart. El frontend pasó a utilizar la API REST del backend como fuente de movimientos temporales y se consolidaron las funciones de consulta, análisis y presentación de la información financiera contempladas para esta etapa.

## Ítems del Product Backlog relacionados

- **Ítem 12:** Historial y filtros por fecha.
- **Ítem 13:** Cálculos financieros principales.
- **Ítem 14:** Dashboard y gráficos complementarios.
- **Ítem 15:** Recordatorio diario.
- **Ítem 20:** Pruebas técnicas de API e integración frontend-backend.
- **Ítem 24:** Evidencia y cierre por sprint.

## Entregable del sprint

Frontend conectado al backend mediante los endpoints definidos, historial con filtros por fecha, cálculos financieros principales, dashboard y gráficos actualizados, y recordatorio diario implementado.

## Tabla de microtareas

| ID | Microtarea | Estado | Resultado principal |
| --- | --- | --- | --- |
| T16 | Integrar frontend con la API de movimientos | Completada | Carga, registro y eliminación conectados con la API REST |
| T17 | Implementar historial y filtros por fechas | Completada | Filtros Todos, Día, Semana, Mes y Rango personalizado |
| T18 | Validar y ajustar cálculos financieros según filtros | Completada | Cálculos sincronizados con el período seleccionado |
| T19 | Implementar dashboard y gráficos complementarios | Completada | Tarjetas y gráficos financieros responsivos |
| T20 | Implementar recordatorio diario | Completada | Recordatorio global visible en la aplicación |
| T21 | Realizar pruebas técnicas de API e integración | Completada | Flujo API e integración frontend-backend verificados |
| T22 | Reforzar validación del campo descripción | Completada | Validación de descripción incorporada en frontend y backend |
| T23 | Implementar paginación del historial | Completada | Paginación de 10, 20 y 30 movimientos por página |
| T24 | Realizar ajuste responsivo final | Completada | Aprovechamiento y revisión responsiva en distintos tamaños |
| T25 | Cerrar documentalmente el Sprint 3 | Completada | Cierre, trazabilidad y resultados consolidados |

## Actividades realizadas

- Se configuró la comunicación del frontend con la API REST del backend y CORS para el origen local autorizado.
- Se conectaron la carga mediante `GET /api/movements`, el registro mediante `POST /api/movements` y la eliminación mediante `DELETE /api/movements/:id`.
- Se implementó un historial con filtros para todos los movimientos, día, semana, mes y rango personalizado.
- Se estableció el mes actual del navegador como filtro inicial.
- Se ajustaron los cálculos de ingresos, gastos, balance, gasto sobre ingresos y distribución de gastos para utilizar el período filtrado.
- Se implementó un dashboard con tarjetas de resumen, comparación de ingresos y gastos, gráfico de dona por categoría y evolución de gastos por fecha.
- Se incorporó un recordatorio diario global dentro de la aplicación.
- Se reforzó la validación de la descripción para exigir al menos una letra, tanto en frontend como en backend.
- Se incorporó paginación del historial sin afectar los movimientos utilizados por los cálculos y gráficos.
- Se revisó el diseño responsivo en escritorio amplio, notebook, tablet y teléfono.
- Se ejecutaron pruebas técnicas de los endpoints y de la integración frontend-backend.

## Incremento obtenido

El incremento del Sprint 3 corresponde a una interfaz web integrada con la API REST de movimientos y capaz de consultar, registrar, eliminar, filtrar, paginar y visualizar información financiera temporal. La pestaña Análisis presenta los cálculos del período seleccionado y gráficos complementarios que permiten interpretar ingresos, gastos, distribución por categoría y evolución de gastos por fecha.

Los movimientos continúan almacenándose temporalmente en memoria del backend y se pierden al reiniciar el servidor. La persistencia definitiva se trabajará posteriormente, de acuerdo con la planificación del proyecto; por lo tanto, no constituye una funcionalidad faltante del Sprint 3.

## Pruebas ejecutadas

| Área | Prueba realizada | Resultado |
| --- | --- | --- |
| API | `GET /api/health` | Respuesta de disponibilidad verificada |
| API | `GET /api/movements` | Consulta temporal verificada |
| API | `POST /api/movements` | Registro y validaciones verificados |
| API | `PUT /api/movements/:id` | Actualización temporal verificada a nivel de API |
| API | `DELETE /api/movements/:id` | Eliminación temporal verificada |
| Integración | Carga, registro y eliminación desde frontend | Comunicación frontend-backend verificada |
| Historial | Filtros Todos, Día, Semana, Mes y Rango | Resultados por período verificados |
| Cálculos | Ingresos, gastos, balance y distribución | Coherencia con el filtro seleccionado verificada |
| Dashboard | Tarjetas y gráficos con distintos períodos | Actualización automática verificada |
| Validación | Descripciones válidas e inválidas | Regla aplicada en frontend y backend |
| Paginación | Tamaños 10, 20 y 30; primera y última página | Navegación y reinicio por filtro verificados |
| Responsividad | Escritorio amplio, notebook, tablet y teléfono | Distribución y ausencia de desbordamiento general verificadas |
| Frontend | `npm.cmd run build` | Builds completados sin errores de TypeScript o compilación |

## Evidencias disponibles

- Respuestas de los endpoints de salud y movimientos.
- Registro y eliminación de movimientos desde la interfaz integrada.
- Historial con cada modalidad de filtro y mes actual como vista inicial.
- Resultados de cálculos financieros para distintos períodos.
- Dashboard con tarjetas, comparación, dona por categoría y evolución por fecha.
- Validación visible de descripciones inválidas y rechazo de la API.
- Paginación con diferentes cantidades de movimientos por página.
- Recordatorio diario global en las secciones principales.
- Vistas responsivas en escritorio amplio, tablet y teléfono.
- Salidas exitosas del build del frontend y trazabilidad mediante Git/GitHub.

## Commits principales

| Orden | Commit | Microtarea relacionada |
| --- | --- | --- |
| 1 | `f096bf5 feat: integrar frontend con API de movimientos` | T16 |
| 2 | `9f7064a feat: implementar filtros por fecha en historial` | T17 |
| 3 | `b5dee25 feat: ajustar calculos financieros segun filtros` | T18 |
| 4 | `74d0fde feat: implementar dashboard y graficos financieros` | T19 |
| 5 | `b9f567b feat: implementar recordatorio diario` | T20 |
| 6 | `7d5839c fix: reforzar validacion de descripcion de movimientos` | T22 |
| 7 | `17b454b feat: implementar paginacion del historial` | T23 |
| 8 | `2f9aa52 style: mejorar aprovechamiento responsivo en pantallas grandes` | T24 |

T21 no generó un commit independiente porque correspondió exclusivamente a pruebas técnicas de API e integración.

## Sprint Review

El incremento cumple el entregable definido para el Sprint 3. El frontend quedó conectado con los endpoints del backend y permite trabajar con movimientos temporales desde la interfaz. El historial incorpora filtros por período y paginación; los cálculos y gráficos responden al mismo conjunto filtrado; y el recordatorio diario y los ajustes responsivos mejoran la experiencia de uso sin ampliar el alcance funcional acordado.

La revisión confirmó el funcionamiento de la integración, los endpoints, las validaciones, los cálculos, las visualizaciones y el comportamiento responsivo previsto para el sprint.

## Retrospectiva

- La validación conjunta de frontend y backend fue necesaria para comprobar el flujo completo y evitar depender únicamente de validaciones de interfaz.
- El trabajo mediante microtareas, pruebas y evidencias facilitó identificar ajustes concretos sin adelantar funcionalidades posteriores.
- Las pruebas permitieron detectar y reforzar la validación de descripciones que no contenían letras.
- Los filtros, la paginación y los ajustes responsivos mejoraron la consulta y usabilidad del historial sin alterar los cálculos financieros.
- La revisión en diferentes tamaños de pantalla permitió ajustar el aprovechamiento del espacio manteniendo la experiencia en tablet y teléfono.

## Alcance no implementado en este sprint

Durante el Sprint 3 no se implementaron:

- MongoDB ni Mongoose.
- Persistencia definitiva.
- Usuarios, autenticación ni JWT.
- Presupuesto.
- Modelo predictivo, FastAPI, Scikit-learn ni inteligencia artificial.

Estos elementos permanecen reservados para etapas posteriores según la planificación del proyecto.

## Estado final

El Sprint 3 queda completado con el incremento integrado, probado y documentado. Se cumplieron los ítems 12, 13, 14, 15, 20 y 24 del Product Backlog dentro del alcance definido, manteniendo el almacenamiento temporal en memoria y dejando la persistencia definitiva para una fase posterior.

## Commit sugerido

`docs: cerrar sprint 3`
