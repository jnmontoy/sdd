# Componentes del Módulo Login — Spec-Driven Development (SDD)
## Directorio: `.sdd/components/login/`

Este directorio contiene las especificaciones formales y autosuficientes de **todos los componentes visuales y funcionales** que integran la página de Login.

Cada componente está especificado con:
1. **Estructura HTML / JSX declarativa**.
2. **Hoja de estilos en CSS Puro (Vanilla CSS)** con variables nativas, sin suponer frameworks ni preprocesadores.
3. **Contrato estricto de propiedades (TypeScript)**.
4. **Estados de interacción y criterios de accesibilidad (objetivo WCAG 2.1 AA)**.

---

## Catálogo de Componentes de Login

| Archivo de Especificación | Componente | Responsabilidad |
| :--- | :--- | :--- |
| **[`logo.md`](./logo.md)** | **Logo Corporativo** | Isotipo vectorial en SVG, halo luminoso y tipografía institucional en CSS puro. |
| **[`card.md`](./card.md)** | **Cards & Contenedores** | Estructuras de contenedor con efecto Frosted Glass (`backdrop-filter`) y CSS puro. |
| **[`input_field.md`](./input_field.md)** | **Inputs & Password Toggle** | Campo «outlined» con etiqueta flotante animada (placeholder que sube al borde), campo de documento con icono y contraseña con ver/ocultar y aviso de Bloq Mayús. |
| **[`button_primary.md`](./button_primary.md)** | **Botón Submit & Loader** | Botón de acción principal con spinner rotativo y gradiente esmeralda en CSS puro. |
| **[`button_microsoft.md`](./button_microsoft.md)** | **Botón Microsoft SSO** | Botón institucional con los 4 colores oficiales y estados interactivos en CSS puro. |
| **[`feedback_alerts.md`](./feedback_alerts.md)** | **Alertas & Feedback** | Banners de error con animación shake y estilos del aviso de sesión expirada (el componente React vive en `modal/session_expiration_modal.md`). |
| **[`recovery_form.md`](./recovery_form.md)** | **Restablecimiento de Contraseña** | Formularios de solicitud y confirmación de nueva clave en CSS puro. |
| **[`login_form.md`](./login_form.md)** | **Formulario Ensamblado** | Integración completa de todos los componentes en una vista operativa funcional. |
| **[`email_recovery_template.md`](./email_recovery_template.md)** | **Correo de Recuperación** | Plantilla HTML de correo con enlace de un solo uso para restablecer la contraseña. |

---

## Variables CSS requeridas

Todos los componentes de este directorio consumen exclusivamente los tokens de [`../variables.css`](../variables.css) (`--bg-viewport`, `--bg-card`, `--brand-primary`, `--text-primary`, `--alert-error-*`, `--orb-color-*`, etc.), con soporte Noche/Día por `data-theme`. No se define una paleta paralela `--login-*`.

## Comportamiento de sesión

El login no guarda tokens: llama a `login()` de [`AuthContext`](../context/auth_context.md), que deja el access token en memoria y el refresh token en una cookie `HttpOnly` fijada por el backend. El aviso de sesión vencida es [`SessionExpirationModal`](../modal/session_expiration_modal.md).
