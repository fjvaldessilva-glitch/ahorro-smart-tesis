# Ahorro Smart

**Ahorro Smart: Sistema Web Responsivo para la Optimización de las Finanzas Personales mediante un Modelo Predictivo de Inteligencia Artificial.**

## Descripción breve

Ahorro Smart es un proyecto de tesis orientado al desarrollo de un sistema web responsivo para apoyar la gestión de finanzas personales. El sistema busca permitir que los usuarios registren ingresos y gastos, consulten su historial financiero, analicen su comportamiento de consumo y, en una etapa posterior, reciban proyecciones basadas en inteligencia artificial.

## Enfoque del proyecto

Este proyecto corresponde a un **sistema web responsivo**, accesible desde navegador en:

- computador;
- tablet;
- teléfono móvil.

No corresponde a una aplicación móvil nativa ni híbrida. Por lo tanto, no se utilizarán tecnologías como React Native, Expo, Flutter o Ionic.

## Tecnologías y herramientas del proyecto

### Tecnología principal del frontend

- React.

### Herramientas de apoyo utilizadas en el frontend

- Vite, utilizado para crear y ejecutar el entorno de desarrollo.
- TypeScript, utilizado como apoyo técnico para mejorar el orden y mantenimiento del código.

Vite y TypeScript apoyan la implementación del frontend y no modifican el alcance funcional definido para el proyecto.

### Backend pendiente

- Node.js.
- Express.

El backend todavía no está implementado. Su desarrollo se iniciará en una microtarea posterior y no incorporará tecnologías o configuraciones adicionales sin justificación en la tesis o en el Product Backlog acordado.

### Servicio predictivo futuro

El servicio predictivo corresponde a una etapa futura del proyecto. No está implementado actualmente.

### Herramientas generales de apoyo

- Git.
- GitHub.
- Postman para futuras pruebas de API.
- Navegador web para pruebas responsivas.

## Estructura actual del monorepo

```txt
AhorroSmart_Tesis/
├─ frontend/
├─ backend/
├─ ia-service/
├─ docs/
│  └─ sprints/
│     └─ sprint-01.md
├─ README.md
└─ .gitignore
```

El frontend contiene la base implementada durante el Sprint 1. Las carpetas `backend/` e `ia-service/` permanecen sin implementación.

## Metodología de trabajo

El desarrollo se organiza bajo Scrum adaptado a un proyecto individual. Cada avance se trabaja como una microtarea documentable, con cambios pequeños, pruebas claras, evidencia sugerida y un mensaje de commit específico.

## Estado actual

Sprint 1 completado: configuración inicial, estructura del monorepo y frontend base del proyecto.

El backend aún no ha sido iniciado.
