# Ecosistema Greenyard / Jolifoods — Especificaciones SDD

Bienvenido al repositorio central de especificaciones de desarrollo guiado por especificaciones (**Spec-Driven Development - SDD**) para el ecosistema de aplicaciones de **Greenyard / Jolifoods**.

## Objetivos del Repositorio `.sdd/`

1. **Estandarización de Arquitectura**: Unificar los patrones de diseño, seguridad y experiencia de usuario de forma **100% agnóstica y portable**, sin suponer rutas fijas ni depender de proyectos locales específicos.
2. **Fuente de la Verdad para Agentes de IA y Desarrolladores**: Permitir que cualquier modelo de lenguaje o ingeniero comprenda la estructura de cada página, sus contratos de API y sus componentes en CSS puro antes de generar o alterar código.
3. **Calidad y Seguridad Continua**: Reducir drásticamente la deuda técnica y vulnerabilidades mediante contratos explícitos de autenticación, validación estricta y protección contra ataques OWASP.

---

## Estructura de Documentación

- **[`SPEC_GUIDE.md`](./SPEC_GUIDE.md)**: Manual y directrices operativas que rigen cómo la IA debe leer, generar e interpretar las especificaciones bajo el principio de portabilidad.
- **[`config_referencia.env.example`](./config_referencia.env.example)**: Plantilla universal de variables de entorno para inicializar proyectos.
- **[`pages/login/`](./pages/login/)**: Suite completa de especificación del módulo de Login (Requisitos, Arquitectura, Contratos API, Seguridad, UI/UX, Plan de QA y Guía para IA).
- **[`model/login/`](../model/login/)**: Especificación formal de modelos de datos (Entidad `Usuario`, `SesionUsuario`, `AuditoriaAcceso`, DDL SQL y Django ORM).
- **[`components/login/`](../components/login/)**: Catálogo de componentes atómicos en **CSS puro** para Login (`logo`, `card`, `input_field`, `button_primary`, `button_microsoft`, `feedback_alerts`, `login_form`).
- **[`components/variables.css`](../components/variables.css)**: Sistema central de variables para el control total de textos y cambio automático entre Modo Noche y Modo Día.
