# Componentes del Módulo Login — Spec-Driven Development (SDD)
## Directorio: `.sdd/components/login/`

Este directorio contiene las especificaciones formales y autosuficientes de **todos los componentes visuales y funcionales** que integran la página de Login.

Cada componente está especificado con:
1. **Estructura HTML / JSX declarativa**.
2. **Hoja de estilos en CSS Puro (Vanilla CSS)** con variables nativas, sin suponer frameworks ni preprocesadores.
3. **Contrato estricto de propiedades (TypeScript)**.
4. **Estados de interacción y accesibilidad (WCAG 2.1 AA)**.

---

## Catálogo de Componentes de Login

| Archivo de Especificación | Componente | Responsabilidad |
| :--- | :--- | :--- |
| **[`logo.md`](./logo.md)** | **Logo Corporativo** | Isotipo vectorial en SVG, halo luminoso y tipografía institucional en CSS puro. |
| **[`card.md`](./card.md)** | **Cards & Contenedores** | Estructuras de contenedor con efecto Frosted Glass (`backdrop-filter`) y CSS puro. |
| **[`input_field.md`](./input_field.md)** | **Inputs & Password Toggle** | Campo de documento con icono y campo de contraseña con botón para ver/ocultar clave. |
| **[`button_primary.md`](./button_primary.md)** | **Botón Submit & Loader** | Botón de acción principal con spinner rotativo y gradiente esmeralda en CSS puro. |
| **[`button_microsoft.md`](./button_microsoft.md)** | **Botón Microsoft SSO** | Botón institucional con los 4 colores oficiales y estados interactivos en CSS puro. |
| **[`feedback_alerts.md`](./feedback_alerts.md)** | **Alertas & Feedback** | Banners de error con animación shake y modal de sesión expirada en CSS puro. |
| **[`recovery_form.md`](./recovery_form.md)** | **Restablecimiento de Contraseña** | Formularios de solicitud y confirmación de nueva clave en CSS puro. |
| **[`login_form.md`](./login_form.md)** | **Formulario Ensamblado** | Integración completa de todos los componentes en una vista operativa funcional. |

---

## Variables Globales de CSS Puro Requeridas (`tokens.css`)

Todos los componentes de este directorio consumen este conjunto de variables CSS nativas:

```css
:root {
  /* Fondos y Superficies */
  --login-bg-root: #0b0f19;
  --login-bg-card: rgba(15, 23, 42, 0.75);
  --login-bg-input: rgba(15, 23, 42, 0.6);
  --login-bg-input-focus: rgba(15, 23, 42, 0.95);
  
  /* Marca e Identidad */
  --login-brand-primary: #10b981;
  --login-brand-hover: #059669;
  --login-brand-accent: #34d399;
  --login-brand-glow: rgba(16, 185, 129, 0.35);
  
  /* Textos */
  --login-text-primary: #f8fafc;
  --login-text-secondary: #94a3b8;
  --login-text-muted: #64748b;
  
  /* Estados */
  --login-status-error: #f43f5e;
  --login-status-error-bg: rgba(244, 63, 94, 0.1);
  --login-status-warning: #f59e0b;
  
  /* Bordes */
  --login-border-subtle: rgba(255, 255, 255, 0.08);
  --login-border-focus: #10b981;
  --login-border-error: #f43f5e;
}
```
