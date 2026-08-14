# Sprint 2 - Backend base y gestión temporal de movimientos

## Estado del sprint

**Completado y cerrado.**

## Objetivo del sprint

Implementar la base del backend y las operaciones temporales de registro, consulta, edición y eliminación de movimientos financieros mediante una API REST.

## Relación con la tesis

Este sprint implementó la base del backend del sistema web responsivo mediante Node.js y Express, junto con una API REST para registrar, consultar, editar y eliminar movimientos financieros utilizando almacenamiento temporal en memoria. La persistencia, autenticación, base de datos e integración con el frontend permanecen fuera del alcance de esta iteración.

## Tabla de microtareas

| ID | Microtarea | Sprint | Estado |
| --- | --- | --- | --- |
| T07 | Crear backend base con Node.js y Express | Sprint 2 | Completada |
| T08 | Crear estructura inicial de rutas para movimientos financieros | Sprint 2 | Completada |
| T09 | Implementar registro y consulta temporal de movimientos financieros en backend | Sprint 2 | Completada |
| T10 | Implementar edición y eliminación temporal de movimientos financieros en backend | Sprint 2 | Completada |
| T11 | Realizar prueba integral del flujo backend de movimientos financieros | Sprint 2 | Completada |
| T12 | Cerrar documentalmente el Sprint 2 | Sprint 2 | Completada |

## Ítems del Product Backlog relacionados

- **Ítem 6:** Backend base y servicios temporales.
- **Ítem 10:** Registro de ingresos y gastos.
- **Ítem 11:** Edición y eliminación de movimientos.
- **Ítem 24:** Evidencia y cierre por sprint.

## Archivos creados o modificados

- `backend/package.json`.
- `backend/package-lock.json`.
- `backend/src/server.js`.
- `backend/src/routes/movements.routes.js`.
- `backend/.gitkeep`, eliminado al incorporar archivos reales.
- `docs/sprints/sprint-02.md`.

## Alcance técnico de T07

- Backend implementado con JavaScript sobre Node.js.
- Express como única dependencia.
- Servidor configurado en el puerto `3001`.
- Ruta técnica `GET /api/health` para verificar disponibilidad.
- Sin rutas funcionales de movimientos.
- Sin TypeScript, MongoDB, Mongoose, JWT, CORS, autenticación, persistencia, variables de entorno ni librerías adicionales.

## Alcance técnico de T08

- Router independiente para el futuro módulo de movimientos financieros.
- Ruta técnica `GET /api/movements` montada desde `backend/src/server.js`.
- Respuesta temporal que confirma que el módulo está preparado.
- Sin creación, edición o eliminación de movimientos.
- Sin datos en memoria, persistencia, base de datos o dependencias adicionales.

## Alcance técnico de T09

- Colección temporal de movimientos almacenada exclusivamente en memoria.
- `GET /api/movements` para consultar los movimientos registrados durante la ejecución actual.
- `POST /api/movements` para registrar ingresos y gastos temporales.
- Validación de campos obligatorios, tipos permitidos, montos positivos y categorías compatibles.
- Identificador numérico temporal asignado por el backend.
- Sin edición, eliminación, base de datos, autenticación, conexión con frontend o dependencias adicionales.
- Los datos se pierden al reiniciar el servidor.

## Alcance técnico de T10

- `PUT /api/movements/:id` para editar un movimiento temporal existente.
- PUT reutiliza las mismas validaciones de campos, tipo, categoría, monto y fecha aplicadas por POST.
- `DELETE /api/movements/:id` para eliminar un movimiento temporal existente.
- Respuesta `404` cuando el identificador solicitado no existe.
- Confirmación JSON después de una eliminación exitosa.
- Sin base de datos, persistencia, autenticación, conexión con frontend o dependencias adicionales.

## Alcance técnico de T11

- Prueba integral de las operaciones `GET`, `POST`, `PUT` y `DELETE` del módulo de movimientos.
- Verificación del registro de un ingreso y un gasto temporal.
- Verificación de la edición y eliminación de movimientos existentes.
- Verificación de respuestas `400` para una categoría incompatible y `404` para identificadores inexistentes.
- Confirmación del estado final de la colección temporal después de las operaciones.
- Sin cambios en el código backend, dependencias, persistencia, autenticación o conexión con frontend.

## Pruebas realizadas

| Prueba | Resultado esperado | Resultado |
| --- | --- | --- |
| `node --check src/server.js` | Validar la sintaxis del servidor | Exitosa; sin errores de sintaxis |
| `npm.cmd start` | Iniciar el servidor en el puerto 3001 | Exitosa; servidor iniciado y detenido después de la prueba |
| `GET /api/health` | Responder `{"status":"ok","service":"Ahorro Smart API"}` | Exitosa; respuesta JSON verificada |
| `node --check src/routes/movements.routes.js` | Validar la sintaxis del router de movimientos | Exitosa; sin errores de sintaxis |
| `GET /api/movements` | Confirmar que el módulo de movimientos está preparado | Exitosa; respuesta JSON temporal verificada |
| `POST /api/movements` con ingreso válido | Crear un ingreso temporal con estado `201` | Exitosa; ingreso creado con identificador temporal |
| `POST /api/movements` con gasto válido | Crear un gasto temporal con estado `201` | Exitosa; gasto creado con identificador temporal |
| `POST /api/movements` con categoría incompatible | Rechazar el movimiento con estado `400` | Exitosa; combinación incompatible rechazada |
| `POST /api/movements` con campos o valores inválidos | Rechazar descripción o fecha vacía, tipo inválido y monto no positivo | Exitosa; todos los casos respondieron con estado `400` |
| `GET /api/movements` con datos temporales | Retornar los movimientos creados durante la ejecución | Exitosa; lista con ingreso y gasto verificada |
| `PUT /api/movements/:id` con datos válidos | Actualizar el movimiento y conservar su identificador | Exitosa; movimiento actualizado con estado `200` e ID conservado |
| `PUT /api/movements/:id` con categoría incompatible | Aplicar las mismas validaciones de POST | Exitosa; actualización rechazada con estado `400` |
| `PUT /api/movements/:id` con ID inexistente | Responder con estado `404` | Exitosa; identificador inexistente rechazado |
| `DELETE /api/movements/:id` con ID existente | Eliminar el movimiento y confirmar en JSON | Exitosa; movimiento eliminado con estado `200` |
| `DELETE /api/movements/:id` con ID inexistente | Responder con estado `404` | Exitosa; identificador inexistente rechazado |
| `GET /api/movements` después de editar y eliminar | Reflejar el resultado final de las operaciones | Exitosa; lista final contiene solo el movimiento actualizado |

### Prueba integral de T11

| Prueba | Estado HTTP | Resultado |
| --- | --- | --- |
| `node --check src/routes/movements.routes.js` | No aplica | Exitosa; sin errores de sintaxis |
| `GET /api/health` | `200` | Exitosa; servicio disponible |
| `GET /api/movements` inicial | `200` | Exitosa; lista inicial vacía |
| `POST /api/movements` con ingreso válido | `201` | Exitosa; ingreso creado con ID 1 |
| `POST /api/movements` con gasto válido | `201` | Exitosa; gasto creado con ID 2 |
| `PUT /api/movements/1` con datos válidos | `200` | Exitosa; ingreso actualizado y su ID conservado |
| `PUT /api/movements/999` | `404` | Exitosa; identificador inexistente rechazado |
| `POST /api/movements` con categoría incompatible | `400` | Exitosa; combinación entre tipo y categoría rechazada |
| `DELETE /api/movements/2` | `200` | Exitosa; gasto eliminado y confirmado en JSON |
| `DELETE /api/movements/999` | `404` | Exitosa; identificador inexistente rechazado |
| `GET /api/movements` final | `200` | Exitosa; lista final contiene únicamente el ingreso actualizado |
| Detención del servidor | No aplica | Exitosa; puerto 3001 cerrado después de las pruebas |

## Cierre del Sprint 2

### Resumen del trabajo realizado

- Se creó el backend base de Ahorro Smart con Node.js, Express y JavaScript.
- Se creó la estructura de rutas del módulo de movimientos financieros.
- Se implementó el registro y la consulta temporal de ingresos y gastos.
- Se implementó la edición y eliminación temporal de movimientos.
- Se realizó una prueba integral del flujo backend con operaciones `GET`, `POST`, `PUT` y `DELETE`.

### Commits asociados

- `079a1d0` — `feat: crear backend base con Node.js y Express`.
- `1257512` — `feat: crear estructura inicial de rutas de movimientos`.
- `56f6727` — `feat: implementar registro temporal de movimientos en backend`.
- `4516589` — `feat: implementar edición y eliminación temporal de movimientos`.
- `30eac0a` — `test: realizar prueba integral del flujo backend de movimientos`.
- `e9273af` - `docs: cerrar sprint 2`.

### Evidencias generadas

- Estructura técnica del backend y del módulo de rutas.
- Ejecución del servidor en el puerto `3001`.
- Respuesta de disponibilidad de `GET /api/health`.
- Lista inicial vacía de movimientos.
- Registro temporal de un ingreso y un gasto.
- Edición y eliminación exitosa de movimientos.
- Rechazo de categorías incompatibles e identificadores inexistentes.
- Estado final de la colección temporal y salida de `git status --short`.

### Pruebas realizadas

- Validación de sintaxis de `server.js` y `movements.routes.js`.
- Inicio y detención controlada del servidor.
- Verificación de respuestas `200` y `201` en operaciones válidas.
- Verificación de respuestas `400` y `404` en operaciones inválidas.
- Confirmación del resultado final mediante `GET /api/movements`.

### Alcance logrado

El Sprint 2 dejó disponible y validada una API REST mínima para registrar, consultar, editar y eliminar movimientos financieros almacenados temporalmente en memoria. El trabajo cubre la base técnica del backend y la administración básica de ingresos y gastos prevista para esta etapa.

En este sprint todavía **no se implementaron**:

- Base de datos.
- Persistencia.
- MongoDB.
- Mongoose.
- JWT.
- Autenticación.
- Inteligencia artificial.
- Conexión con el frontend.
- CORS.

### Pendientes para el siguiente sprint

- Iniciar el Sprint 3 de acuerdo con la planificación vigente, orientado a la integración frontend-backend, consulta y visualización financiera.
- Mantener fuera del alcance del Sprint 3 la persistencia, la autenticación, la seguridad y la inteligencia artificial, de acuerdo con la planificación vigente.

## Evidencia sugerida

- Captura de la estructura de `backend/`.
- Captura del servidor ejecutándose con `npm.cmd start`.
- Captura de la respuesta JSON de `GET /api/health`.
- Captura de la respuesta JSON de `GET /api/movements`.
- Captura de los resultados de `POST /api/movements` con ingreso y gasto válidos.
- Captura del rechazo de una categoría incompatible.
- Captura de la edición exitosa y del caso PUT con ID inexistente.
- Captura de la eliminación exitosa y del caso DELETE con ID inexistente.
- Captura de la lista inicial vacía y del estado final de la colección durante T11.
- Captura conjunta de los códigos HTTP obtenidos en la prueba integral de T11.
- Captura de `git status --short`.

## Commit sugerido

`docs: cerrar sprint 2`
