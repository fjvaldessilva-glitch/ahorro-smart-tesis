# Sprint 1 - Análisis, diseño y configuración inicial

## Estado del sprint

**Completado y cerrado.**

## Objetivo del sprint

Documentar los requisitos y las variables iniciales del modelo predictivo, definir el diseño general de la solución y preparar la configuración inicial del frontend del sistema web responsivo Ahorro Smart.

## Relación con la tesis

Este sprint estuvo orientado al análisis, diseño y configuración inicial de Ahorro Smart, considerando la documentación de requisitos, la definición inicial de variables para el modelo predictivo, el diseño general de la solución y la preparación del entorno frontend del sistema web responsivo.

## Tabla de microtareas

| ID | Microtarea | Estado | Evidencia | Commit |
| --- | --- | --- | --- | --- |
| T01 | Crear carpeta oficial del proyecto | Completada | Carpeta oficial verificada | Incluida en la preparación inicial |
| T02 | Inicializar repositorio Git y crear archivos base mínimos | Completada | Evidencia almacenada externamente en `Evidencias/Sprint 01` | `23fc8fa chore: inicializar repositorio y documentación base del proyecto` |
| T03 | Crear estructura base del monorepo oficial | Completada | Estructura de carpetas y estado de Git verificados | `1a3b0ad chore: crear estructura base del monorepo` |
| T05 | Crear frontend base con React, Vite y TypeScript | Completada | Interfaz, movimientos temporales, análisis, build y estado de Git verificados | `ff56cd9 feat: crear frontend base con React, Vite y TypeScript` |

## Trazabilidad de T05

- **Relación con Sprint 1:** análisis, diseño y configuración inicial del sistema web responsivo.
- **Objetivo específico relacionado:** OE2 – preparación del entorno frontend para materializar el diseño de la interfaz web responsiva.
- **Product Backlog relacionado:** Ítem 5 - Configuración inicial del entorno frontend; inicio preparatorio del Ítem 10 - Registro de ingresos y gastos; Ítem 13 - Cálculos financieros principales; e Ítem 14 - Dashboard y gráficos complementarios, solo a nivel frontend temporal.
- **Alcance de interfaz:** pestañas Ingresos/Gastos, Análisis y Proyección IA; movimientos temporales en memoria; cálculos de ingresos, gastos, balance y gasto sobre ingresos; barras comparativas y distribución de gastos por categoría.
- **Categorías controladas:** categorías separadas según el tipo de movimiento, con validación frontend para impedir combinaciones incompatibles.
- **Tecnología principal del frontend:** React.
- **Herramientas utilizadas en el frontend:** Vite se utilizó para la configuración de la estructura del frontend, su ejecución local y compilación; TypeScript se empleó para incorporar tipado estático, mejorar la organización del código y facilitar su mantenimiento.
- **Backend:** no fue implementado durante el Sprint 1. Su inicio queda reservado para una microtarea posterior con Node.js y Express.

## Evidencias

| ID de evidencia | Descripción | Estado | Observaciones |
| --- | --- | --- | --- |
| E01 | Verificación de la carpeta oficial | Completada | Asociada a T01 |
| E02 | Repositorio y archivos base | Completada | Asociada a T02; almacenada fuera del repositorio |
| E03 | Estructura base del monorepo | Completada | Asociada a T03 |
| E05 | Frontend base y build exitoso | Completada | Asociada a T05 |

## Commits

| ID | Commit | Microtarea relacionada |
| --- | --- | --- |
| C01 | `23fc8fa chore: inicializar repositorio y documentación base del proyecto` | T02 |
| C02 | `1a3b0ad chore: crear estructura base del monorepo` | T03 |
| C03 | `ff56cd9 feat: crear frontend base con React, Vite y TypeScript` | T05 |

## Pruebas realizadas

| ID | Prueba | Resultado esperado | Resultado obtenido |
| --- | --- | --- | --- |
| P01 | Verificar estado del repositorio | Confirmar los cambios correspondientes a cada microtarea | Completada |
| P02 | Verificar estructura del monorepo | Confirmar frontend, backend, ia-service y documentación | Completada |
| P03 | Ejecutar `npm.cmd run build` en el frontend | Generar el build sin errores | Completada |
| P04 | Revisar la interfaz en navegador | Confirmar diseño responsivo y comportamiento temporal | Completada |

## Decisiones técnicas

| ID | Decisión | Justificación |
| --- | --- | --- |
| D01 | Usar un monorepo simple | Facilita organizar frontend, backend e IA futura en un solo repositorio para la tesis. |
| D02 | Documentar por sprints | Permite mantener trazabilidad del avance bajo Scrum adaptado a un proyecto individual. |
| D03 | Implementar primero la base del frontend | Permitió cerrar el Sprint 1 sin adelantar backend, persistencia o inteligencia artificial. |
| D04 | Utilizar Vite y TypeScript en el frontend | Vite permite configurar, ejecutar y compilar el frontend; TypeScript aporta tipado estático, organización y mantenibilidad del código. |

## Cierre

El Sprint 1 quedó completado con el repositorio inicial, la estructura del monorepo y el frontend base. No se inició Sprint 2 ni se implementó backend en este cierre.

## Actualización documental posterior al cierre

Con fecha 13-08-2026 se incorporó la ERS del Sprint 1 como regularización documental de los ítems 1 y 2 del Product Backlog. El documento consolida los requisitos funcionales y no funcionales del sistema, la definición inicial de las variables de entrada y salida requeridas para el futuro modelo predictivo y su trazabilidad con los objetivos específicos del proyecto.

Documento incorporado:
`docs/ers/ERS_Ahorro_Smart_Sprint_1_Items_1_y_2.docx`

Esta actualización no modifica el incremento técnico desarrollado originalmente durante el Sprint 1 ni altera sus commits históricos.
