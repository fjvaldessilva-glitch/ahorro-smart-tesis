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
| 16 | Preparación de datos e identificación de patrones | En desarrollo |
| 17 | Selección y entrenamiento del modelo | Pendiente |
| 18 | Generación e integración de proyecciones | Pendiente |
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

### T38 - Preparar y validar datos simulados

- Se generó un historial de gastos completamente sintético para el período 2024-01-01 a 2026-06-30 mediante la semilla fija `2026`.
- Los datos originales utilizan `date`, `category` y `amount`, manteniendo trazabilidad con VE-02, VE-03 y VE-01, respectivamente.
- Se validaron fechas, categorías, montos positivos y finitos, y ausencia de campos vacíos antes del procesamiento.
- Se derivaron `year`, `month` y `period`, y se calcularon `monthly_amount` y `transaction_count` mediante agrupación mensual por categoría.
- El resumen de validación registra cero fechas, categorías, montos y valores vacíos inválidos.
- Los datos no contienen información personal o financiera real y se destinan exclusivamente al desarrollo y evaluación académica controlada.
- En T38 no se identificaron formalmente patrones de consumo, no se seleccionó un algoritmo y no se entrenó un modelo.
- El Ítem 16 continúa **En desarrollo** hasta completar la identificación y documentación formal de patrones en T39.

## Pruebas

Las pruebas se documentarán durante las microtareas correspondientes y deberán consolidarse después de integrar el componente predictivo.

| Área | Prueba prevista | Estado |
| --- | --- | --- |
| Datos simulados | Generación reproducible, validación estricta y agregación mensual | Completada en T38 |
| Modelo predictivo | Entrenamiento y resultados controlados | Pendiente |
| Integración | Comunicación Node.js/Express ↔ FastAPI | Pendiente |
| Proyecciones | Generación, persistencia y presentación | Pendiente |
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
