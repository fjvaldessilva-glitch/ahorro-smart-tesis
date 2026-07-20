# Sprint 1 - Configuración inicial y diseño base

## Objetivo del sprint

Crear la base técnica inicial del proyecto Ahorro Smart, estableciendo una estructura limpia, documentada y coherente con el stack definido en la tesis.

## Relación con la tesis

Este sprint inicia la construcción del sistema web responsivo propuesto en el proyecto de título. Su propósito es preparar el entorno de trabajo, la documentación técnica inicial y la estructura sobre la cual se desarrollarán posteriormente el frontend, el backend y el servicio predictivo.

## Tabla de microtareas

| ID  | Microtarea | Estado | Evidencia | Commit |
| --- | --- | --- | --- | --- |
| T01 | Crear carpeta oficial del proyecto | Pendiente de confirmación | Pendiente | Pendiente |
| T02 | Inicializar repositorio Git y crear archivos base mínimos | En desarrollo | Pendiente | Pendiente |
| T03 | Crear estructura base del monorepo oficial | En revisión | Captura de estructura de carpetas y `git status` | `chore: crear estructura base del monorepo` |
| T05 | Crear frontend base con React, Vite y TypeScript | En revisión | Capturas de Ingresos/Gastos con movimientos temporales y Análisis con tarjetas, comparación de ingresos/gastos y gastos por categoría; resultado exitoso de `npm run build` y salida de `git status --short` | `feat: crear frontend base con React, Vite y TypeScript` |

### Trazabilidad de T05

- **Relación con Sprint 1:** configuración inicial y diseño base del sistema web responsivo.
- **Objetivo específico relacionado:** base técnica inicial del frontend responsivo.
- **Product Backlog relacionado:** Ítem 5 - Configuración inicial del proyecto/frontend web; inicio preparatorio del Ítem 10 - Registro de ingresos y gastos; Ítem 13 - Cálculos financieros principales; e Ítem 14 - Dashboard y gráficos complementarios, solo a nivel frontend temporal.
- **Alcance de interfaz:** estructura inicial con pestañas Ingresos/Gastos, Análisis y Proyección IA; movimientos temporales en memoria; cálculos de ingresos, gastos, balance y gasto sobre ingresos; barras comparativas y distribución de gastos por categoría.
- **Categorías controladas:** categorías separadas según tipo de movimiento. Ingreso permite Sueldo y Otros ingresos; Gasto utiliza una lista específica que incorpora Mascotas. Al cambiar el tipo se reinicia la categoría y la validación frontend impide combinaciones incompatibles.
- **Ajustes de categorías:** se eliminaron Ahorro/Inversión y Honorarios como categorías independientes.
- **Backend:** no aplica en T05 porque aún no está implementado; el manejo continúa exclusivamente en memoria del frontend.

## Espacio para evidencias

| ID de evidencia | Descripción | Ruta o archivo | Observaciones |
| --- | --- | --- | --- |
| E01 | Captura de carpeta oficial creada | Pendiente | Asociada a T01 |
| E02 | Captura de archivos base creados | Pendiente | Asociada a T02 |

## Espacio para commits

| ID | Mensaje de commit | Microtarea relacionada | Fecha |
| --- | --- | --- | --- |
| C01 | Pendiente | T02 | Pendiente |

## Espacio para pruebas

| ID | Prueba | Resultado esperado | Resultado obtenido |
| --- | --- | --- | --- |
| P01 | Verificar estado de Git con `git status` | Mostrar archivos base sin confirmar | Pendiente |
| P02 | Verificar estructura con listado de archivos | Confirmar README, .gitignore y sprint-01.md | Pendiente |

## Decisiones técnicas

| ID | Decisión | Justificación |
| --- | --- | --- |
| D01 | Usar monorepo simple | Facilita organizar frontend, backend e IA futura en un solo repositorio para la tesis. |
| D02 | Documentar por sprints | Permite mantener trazabilidad del avance bajo Scrum adaptado a un proyecto individual. |
| D03 | No crear frontend ni backend todavía | Respeta el trabajo por microtareas y evita mezclar responsabilidades antes de tiempo. |
