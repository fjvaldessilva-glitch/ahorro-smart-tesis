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
| T08 | Crear estructura inicial de rutas para movimientos financieros | Sprint 2 | En revisión |

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

## Pruebas realizadas

| Prueba | Resultado esperado | Resultado |
| --- | --- | --- |
| `node --check src/server.js` | Validar la sintaxis del servidor | Exitosa; sin errores de sintaxis |
| `npm.cmd start` | Iniciar el servidor en el puerto 3001 | Exitosa; servidor iniciado y detenido después de la prueba |
| `GET /api/health` | Responder `{"status":"ok","service":"Ahorro Smart API"}` | Exitosa; respuesta JSON verificada |
| `node --check src/routes/movements.routes.js` | Validar la sintaxis del router de movimientos | Exitosa; sin errores de sintaxis |
| `GET /api/movements` | Confirmar que el módulo de movimientos está preparado | Exitosa; respuesta JSON temporal verificada |

## Evidencia sugerida

- Captura de la estructura de `backend/`.
- Captura del servidor ejecutándose con `npm.cmd start`.
- Captura de la respuesta JSON de `GET /api/health`.
- Captura de la respuesta JSON de `GET /api/movements`.
- Captura de `git status --short`.

## Commit sugerido

`feat: crear estructura inicial de rutas de movimientos`
