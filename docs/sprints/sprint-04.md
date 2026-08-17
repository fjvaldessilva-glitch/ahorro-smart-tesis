# Sprint 04 - Persistencia, usuarios y seguridad

## Estado del sprint

**Completado.**

## Objetivo del sprint

Incorporar persistencia de información mediante MongoDB y Mongoose, gestión de usuarios, autenticación y control de acceso, clasificación de movimientos mediante las categorías definidas, gestión del presupuesto personal y validación funcional y responsiva de las funcionalidades implementadas.

## Relación con la tesis

Este sprint continúa la evolución del sistema web responsivo Ahorro Smart desde el incremento integrado del Sprint 03 hacia una etapa con almacenamiento persistente, gestión de usuarios y protección básica de rutas. También contempla la clasificación de los movimientos mediante las categorías oficiales, la gestión del presupuesto personal y la validación funcional, responsiva y de usabilidad del incremento.

## Ítems del Product Backlog asociados

- **Ítem 7:** Autenticación y control de acceso. **Completado.**
- **Ítem 8:** Clasificación por categorías. **Completado.**
- **Ítem 9:** Gestión del presupuesto. **Completado.**
- **Ítem 21:** Pruebas funcionales, responsivas y de usabilidad. **Completado.**
- **Ítem 24:** Evidencia y cierre por sprint. **Completado.**
- **Ítem 26:** Base de datos y persistencia. **Completado.**

## Entregable comprometido

Base de datos operativa, persistencia de movimientos, clasificación de movimientos mediante las categorías definidas, gestión del presupuesto con cálculo de su porcentaje de ejecución, gestión de usuarios, autenticación y protección básica de rutas.

## Estado inicial heredado del Sprint 03

- El frontend se encuentra integrado con la API REST del backend.
- La API permite consultar, registrar, editar y eliminar movimientos financieros temporales.
- El historial, los filtros por fecha, los cálculos financieros, el dashboard, los gráficos, el recordatorio diario, la validación de descripción y la paginación se encuentran implementados.
- Los movimientos se almacenan temporalmente en memoria del backend y se pierden al reiniciar el servidor.
- MongoDB y Mongoose todavía no están operativos.
- No existe persistencia definitiva.
- No están implementados usuarios, autenticación ni JWT.
- No existe presupuesto persistente.
- No están implementados el modelo predictivo, FastAPI, Scikit-learn ni las proyecciones con inteligencia artificial.

Este estado corresponde al punto de partida correcto del Sprint 04 y no implica que las funcionalidades comprometidas para este sprint ya se encuentren desarrolladas.

## Resultado funcional del sprint

### Persistencia

- MongoDB quedó operativo mediante Mongoose sobre la base de datos `ahorro-smart`.
- Se implementó persistencia de usuarios, movimientos y presupuestos.
- Los datos permanecen disponibles después de reiniciar el backend.

### Usuarios y seguridad

- Se implementaron registro de usuarios, login y almacenamiento de contraseñas mediante hash.
- Se incorporaron JWT, rutas protegidas, sesión integrada en el frontend y cierre de sesión.
- Se incorporó manejo de JWT inválido o vencido.
- Los movimientos y presupuestos quedaron aislados por usuario.

### Movimientos

- Cada movimiento quedó asociado al propietario autenticado.
- Las operaciones GET, POST, PUT y DELETE de movimientos quedaron protegidas.
- La propiedad del movimiento no se expone al cliente como mecanismo de autorización; el propietario se determina desde la sesión autenticada.

### Presupuesto

- Se implementó un presupuesto personal único por usuario, con registro, actualización y persistencia en MongoDB.
- El monto debe ser mayor que cero.
- La gestión editable se ubicó en la pestaña Ingresos/Gastos y el seguimiento informativo en Análisis.
- El presupuesto se entiende como el monto planificado para gastos.
- El porcentaje de ejecución se calcula mediante `gastos del período / presupuesto * 100` y puede superar el 100 %.
- No se implementaron presupuestos por categoría ni múltiples presupuestos por período.

## Categorías oficiales

### Ingresos

- Sueldo.
- Otros ingresos.

### Gastos

- Alimentación.
- Transporte.
- Vivienda.
- Servicios básicos.
- Salud.
- Educación.
- Pago de deudas y créditos.
- Entretenimiento.
- Mascotas.
- Otros gastos.

No se incorpora la categoría `Ahorro/Inversión`.

La compatibilidad entre tipo y categoría se valida en el frontend y en el backend. Las categorías se mantienen como un catálogo controlado persistido en cada movimiento; no se creó un CRUD ni una colección independiente de categorías.

## Elementos fuera del alcance de esta etapa

Durante el Sprint 04 no se implementaron:

- Preparación de datos para inteligencia artificial.
- Entrenamiento de modelos.
- Selección de modelo predictivo.
- FastAPI.
- Scikit-learn.
- Proyecciones predictivas.
- Evaluación del modelo.
- Margen de error predictivo.

Estos elementos corresponden al Sprint 05.

## Registro de microtareas

| ID | Microtarea | Estado | Resultado principal |
| --- | --- | --- | --- |
| T26 | Inicio documental del Sprint 04 | Completada | Sprint 04 iniciado y alcance documentado. |
| T27 | Configuración MongoDB y Mongoose | Completada | Conexión base con MongoDB operativa mediante Mongoose. |
| T28 | Usuarios y autenticación base | Completada | Registro, login, hash de contraseñas y JWT implementados. |
| T29 | Persistencia y protección de movimientos por usuario | Completada | Movimientos persistentes, protegidos y aislados por usuario. |
| T30 | Integración de autenticación JWT en frontend | Completada | Sesión autenticada integrada entre frontend y backend. |
| T31 | Consolidación de clasificación por categorías | Completada | Categorías oficiales y compatibilidad por tipo validadas. |
| T32 | Gestión y seguimiento del presupuesto personal | Completada | Presupuesto único persistente y porcentaje de ejecución implementados. |
| T33 | Pruebas funcionales, responsivas y de usabilidad | Completada | Validación final completada con 15 de 15 casos aprobados. |

## Pruebas

| Área | Prueba realizada | Resultado |
| --- | --- | --- |
| Autenticación y seguridad | Login válido e inválido, JWT, rutas protegidas, cierre de sesión y aislamiento por usuario. | Aprobada |
| Persistencia | Usuarios, movimientos y presupuestos disponibles después de reiniciar el backend. | Aprobada |
| Movimientos y categorías | Operaciones protegidas y rechazo de combinaciones incompatibles entre tipo y categoría. | Aprobada |
| Presupuesto | Registro, actualización, unicidad, aislamiento y cálculo del porcentaje de ejecución. | Aprobada |
| Responsividad y usabilidad | Revisión en escritorio de 1440 px, tableta de 820 px y móvil de 390 px. | Aprobada después de corrección |

Resultado consolidado de T33:

- Casos totales: **15**.
- Casos aprobados: **15**.
- Casos fallidos: **0**.
- Porcentaje de aprobación: **100 %**.
- Errores críticos: **0**.

Durante la validación manual se detectó inicialmente una incidencia no crítica de responsividad en la navegación superior. Antes del cierre se corrigió mediante `flex-wrap`, eliminación del desplazamiento horizontal y adaptación del encabezado de sesión. La validación final confirmó navegación completamente visible y ausencia de desbordamiento horizontal general en 1440 px, 820 px y 390 px.

## Evidencias

| ID de evidencia | Descripción | Estado | Observaciones |
| --- | --- | --- | --- |
| T26-01 | `T26-01-inicio-documental-sprint-04.png` | Registrada | Inicio documental del Sprint 04. |
| T27-01 | `T27-01-conexion-mongodb-mongoose-operativa.png` | Registrada | Conexión MongoDB y Mongoose operativa. |
| T28-01 | `T28-01-login-jwt-funcionando.png` | Registrada | Login y emisión de JWT. |
| T28-02 | `T28-02-usuario-persistido-password-hash-mongodb.png` | Registrada | Usuario persistido con contraseña almacenada mediante hash. |
| T29-01 | `T29-01-persistencia-movimientos-despues-reinicio.png` | Registrada | Persistencia de movimientos después del reinicio. |
| T29-02 | `T29-02-aislamiento-movimientos-entre-usuarios.png` | Registrada | Aislamiento de movimientos por usuario. |
| T30-01 | `T30-01-login-y-movimientos-autenticados-web.png` | Registrada | Login y movimientos autenticados en la aplicación web. |
| T30-02 | `T30-02-cierre-sesion-y-aislamiento-web.png` | Registrada | Cierre de sesión y aislamiento en frontend. |
| T31-01 | `T31-01-categorias-gasto-oficiales.png` | Registrada | Categorías oficiales de gasto. |
| T31-02 | `T31-02-backend-rechaza-categoria-incompatible.png` | Registrada | Rechazo de categoría incompatible en backend. |
| T32-01 | `T32-01-presupuesto-y-porcentaje-ejecucion-web.png` | Registrada | Presupuesto y porcentaje de ejecución en frontend. |
| T32-02 | `T32-02-aislamiento-presupuesto-entre-usuarios-web.png` | Registrada | Aislamiento del presupuesto por usuario. |
| T33-01 | `T33-01-responsive-tablet-820px.png` | Registrada | Validación responsiva en tableta. |
| T33-02 | `T33-02-responsive-movil-390px.png` | Registrada | Validación responsiva en móvil. |

## Commits

| Orden | Commit | Microtarea relacionada |
| --- | --- | --- |
| 1 | `d4471b0` - docs: iniciar sprint 4 | T26 |
| 2 | `409fec4` - feat: configurar conexion mongodb con mongoose | T27 |
| 3 | `fef72c8` - feat: implementar usuarios y autenticacion base | T28 |
| 4 | `16900e8` - feat: persistir y proteger movimientos por usuario | T29 |
| 5 | `0b3da79` - feat: integrar autenticacion jwt en frontend | T30 |
| 6 | `c709878` - feat: validar categorias por tipo de movimiento | T31 |
| 7 | `ad0dd82` - feat: implementar gestion de presupuesto personal | T32 |
| 8 | `bec7338` - fix: corregir navegacion responsive | T33 |

## Sprint Review

El objetivo del Sprint 04 se cumplió. La aplicación pasó de manejar movimientos temporalmente en memoria a utilizar persistencia en MongoDB mediante Mongoose. Se incorporaron usuarios, autenticación JWT y protección básica de rutas; los movimientos y presupuestos quedaron aislados por usuario. También se consolidaron las categorías oficiales y se incorporó un presupuesto personal persistente con seguimiento de su porcentaje de ejecución.

La validación final alcanzó 15 de 15 casos aprobados. La incidencia no crítica detectada en la navegación responsive fue corregida antes del cierre y no quedaron errores críticos conocidos. Este resultado corresponde al entorno de desarrollo del proyecto y no representa un despliegue productivo, seguridad avanzada ni inteligencia artificial funcional.

## Retrospectiva

### Aspectos positivos

- La persistencia y la seguridad se integraron incrementalmente.
- Las pruebas por microtarea permitieron comprobar los componentes antes del cierre.
- La revisión manual responsive permitió detectar una incidencia no advertida inicialmente.

### Aspecto a mejorar

- Revisar la ubicación y comprensión funcional de las nuevas características antes de implementarlas en la interfaz, como ocurrió con la ubicación inicial del presupuesto.

### Acción para el siguiente sprint

- Revisar previamente la integración funcional y visual antes de desarrollar cada componente del Sprint 05.
