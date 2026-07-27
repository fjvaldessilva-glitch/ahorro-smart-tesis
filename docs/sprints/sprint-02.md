# Sprint 2 - Base técnica y gestión de movimientos financieros

## Estado del sprint

**Iniciado.**

## Objetivo del sprint

Construir la base técnica del backend y preparar la futura gestión de movimientos financieros de Ahorro Smart, respetando el alcance definido en la tesis y el Product Backlog acordado.

## Relación con la tesis

Este sprint inicia la capa backend del sistema web responsivo. La microtarea T07 establece una base mínima ejecutable con Node.js y Express para preparar la futura API REST, sin implementar todavía movimientos financieros, persistencia, autenticación, base de datos ni integración con el frontend.

## Tabla de microtareas

| ID | Microtarea | Sprint | Estado |
| --- | --- | --- | --- |
| T07 | Crear backend base con Node.js y Express | Sprint 2 | Completada |
| T08 | Crear estructura inicial de rutas para movimientos financieros | Sprint 2 | Completada |
| T09 | Implementar registro y consulta temporal de movimientos financieros en backend | Sprint 2 | Completada |
| T10 | Implementar edición y eliminación temporal de movimientos financieros en backend | Sprint 2 | En revisión |

## Ítems del Product Backlog relacionados

- **Ítem 6:** Base de datos y servicios principales.
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

## Evidencia sugerida

- Captura de la estructura de `backend/`.
- Captura del servidor ejecutándose con `npm.cmd start`.
- Captura de la respuesta JSON de `GET /api/health`.
- Captura de la respuesta JSON de `GET /api/movements`.
- Captura de los resultados de `POST /api/movements` con ingreso y gasto válidos.
- Captura del rechazo de una categoría incompatible.
- Captura de la edición exitosa y del caso PUT con ID inexistente.
- Captura de la eliminación exitosa y del caso DELETE con ID inexistente.
- Captura de `git status --short`.

## Commit sugerido

`feat: implementar edición y eliminación temporal de movimientos`
