# Especificación del Sistema de Variables: `variables.css`
## Sistema Central de Diseño — Ecosistema Greenyard / Jolifoods SDD

El archivo `variables.css` es la **fuente única e inmutable de verdad tipográfica, cromática y de tematización** del ecosistema Jolifoods. Gobierna todos los textos, superficies, bordes, estados y sombras del proyecto, definiendo el comportamiento reactivo de **Modo Noche (Dark Mode)** y **Modo Día (Light Mode)** mediante variables CSS nativas sin dependencias externas.

---

## 1. Mecanismo de Conmutación Día / Noche

- **Modo Noche (Por defecto)**: Activo en `:root`, `[data-theme='dark']` y `[data-bs-theme='dark']` con `color-scheme: dark`.
- **Modo Día**: Se activa dinámicamente mediante el atributo `[data-theme='light']` y `[data-bs-theme='light']` en la etiqueta `<html>`.

```html
<!-- Modo Noche (Oficial) -->
<html lang="es" data-theme="dark" data-bs-theme="dark">

<!-- Modo Día (Oficial) -->
<html lang="es" data-theme="light" data-bs-theme="light">
```

### Función Javascript Estándar para Conmutación
```javascript
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute("data-theme") || html.getAttribute("data-bs-theme") || "dark";
  const next = current === "dark" ? "light" : "dark";
  html.setAttribute("data-theme", next);
  html.setAttribute("data-bs-theme", next);
  html.style.colorScheme = next;
  // Actualizar icono o estado de UI
}
```

---

## 2. Hoja de Estilos Completa en CSS Puro (`variables.css`)

```css
/* ==========================================================================
   SISTEMA DE VARIABLES DE DISEÑO (CSS PURO) — GREENYARD / JOLIFOODS SDD
   Control Central de Textos, Superficies y Tematización Día/Noche
   ========================================================================== */

/* --------------------------------------------------------------------------
   1. TOKENS GLOBALES Y TIPOGRAFÍA COMPARTIDA
   -------------------------------------------------------------------------- */
:root {
  /* --- Familia Tipográfica y Escala de Texto --- */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  --font-family-mono: 'SFMono-Regular', Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  --font-size-root: 16px;
  
  --font-size-2xs: 0.6875rem; /* 11px */
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */

  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;

  --line-height-tight: 1.2;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.625;

  /* --- Espaciado, Layout y Radios --- */
  --topbar-height: 60px;
  --radius-sm: 0.375rem;      /* 6px */
  --radius-md: 0.5rem;        /* 8px */
  --radius-lg: 0.75rem;       /* 12px */
  --radius-xl: 1rem;          /* 16px */
  --radius-2xl: 1.5rem;       /* 24px */
  --radius-full: 9999px;

  /* --- Transiciones y Z-Index --- */
  --transition-fast: 150ms cubic-bezier(0.16, 1, 0.3, 1);
  --transition-base: 250ms cubic-bezier(0.16, 1, 0.3, 1);
  --transition-slow: 400ms cubic-bezier(0.16, 1, 0.3, 1);

  --z-base: 1;
  --z-card: 10;
  --z-sticky: 100;
  --z-drawer: 1000;
  --z-popover: 1050;
  --z-modal: 10000;
  --z-toast: 10010;

  /* --- Colores de Marca y Estados (Inmutables) --- */
  --brand-primary: #10b981;
  --brand-primary-hover: #059669;
  --brand-primary-light: #34d399;
  --brand-glow: rgba(16, 185, 129, 0.35);

  --status-success: #10b981;
  --status-error: #f43f5e;
  --status-warning: #f59e0b;
  --status-info: #0ea5e9;

  --status-success-bg: rgba(16, 185, 129, 0.15);
  --status-error-bg: rgba(244, 63, 94, 0.15);
  --status-warning-bg: rgba(245, 158, 11, 0.15);
  --status-info-bg: rgba(14, 165, 233, 0.15);
}

/* --------------------------------------------------------------------------
   2. TEMA MODO NOCHE (DARK MODE - POR DEFECTO)
   -------------------------------------------------------------------------- */
:root,
[data-theme='dark'],
[data-bs-theme='dark'] {
  color-scheme: dark;

  /* Superficies y Fondos */
  --bg-viewport: #0f121d;
  --bg-card: #151928;
  --bg-elevated: #1e2438;
  --bg-active: #29304a;
  --bg-hover: rgba(255, 255, 255, 0.06);
  --bg-input: #1a2032;
  --bg-input-focus: #151928;
  --bg-btn-secondary: rgba(30, 36, 56, 0.85);
  --bg-btn-secondary-hover: rgba(41, 48, 74, 0.95);

  /* Jerarquía de Texto */
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-muted: #94a3b8;
  --text-tertiary: #64748b;
  --text-on-brand: #ffffff;

  /* Bordes y Separadores */
  --border-subtle: rgba(255, 255, 255, 0.09);
  --border-strong: rgba(255, 255, 255, 0.18);
  --border-card-accent: rgba(16, 185, 129, 0.35);
  --border-focus: var(--brand-primary);
  --border-error: var(--status-error);

  /* Sombras y Glassmorphism */
  --glass-blur: blur(20px);
  --glass-bg: rgba(21, 25, 40, 0.88);
  --glass-border: rgba(255, 255, 255, 0.09);
  --glass-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.75), 0 0 20px -5px var(--brand-glow);
  --shadow-card: 0 4px 20px rgba(0, 0, 0, 0.35);
  --shadow-popover: 0 14px 35px rgba(0, 0, 0, 0.55);
  --shadow-modal: 0 25px 60px rgba(0, 0, 0, 0.75);
  --shadow-input-focus: 0 0 0 3px rgba(16, 185, 129, 0.25);
  --shadow-error-focus: 0 0 0 3px rgba(244, 63, 94, 0.25);

  /* Halos de Fondo */
  --orb-color-primary: rgba(16, 185, 129, 0.22);
  --orb-color-secondary: rgba(5, 150, 105, 0.18);

  /* Alertas */
  --alert-error-bg: rgba(244, 63, 94, 0.12);
  --alert-error-border: rgba(244, 63, 94, 0.3);
  --alert-error-text: #fecdd3;

  /* --- Aliases Canónicos de Compatibilidad --- */
  --background: var(--bg-viewport);
  --surface: var(--bg-viewport);
  --surface-card: var(--bg-card);
  --surface-elevated: var(--bg-elevated);
  --surface-active: var(--bg-active);
  --border-color: var(--border-subtle);
}

/* --------------------------------------------------------------------------
   3. TEMA MODO DÍA (LIGHT MODE)
   -------------------------------------------------------------------------- */
[data-theme='light'],
[data-bs-theme='light'] {
  color-scheme: light;

  /* Superficies y Fondos */
  --bg-viewport: #f4f6fa;
  --bg-card: #ffffff;
  --bg-elevated: #f8fafc;
  --bg-active: #e2e8f0;
  --bg-hover: rgba(0, 0, 0, 0.04);
  --bg-input: #ffffff;
  --bg-input-focus: #ffffff;
  --bg-btn-secondary: #ffffff;
  --bg-btn-secondary-hover: #f1f5f9;

  /* Jerarquía de Texto */
  --text-primary: #0f172a;
  --text-secondary: #334155;
  --text-muted: #64748b;
  --text-tertiary: #94a3b8;
  --text-on-brand: #ffffff;

  /* Bordes y Separadores */
  --border-subtle: #e2e8f0;
  --border-strong: #cbd5e1;
  --border-card-accent: rgba(16, 185, 129, 0.5);
  --border-focus: var(--brand-primary);
  --border-error: var(--status-error);

  /* Sombras y Glassmorphism */
  --glass-blur: blur(16px);
  --glass-bg: rgba(255, 255, 255, 0.94);
  --glass-border: rgba(0, 0, 0, 0.08);
  --glass-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.08), 0 0 15px -3px rgba(16, 185, 129, 0.15);
  --shadow-card: 0 2px 10px rgba(0, 0, 0, 0.05);
  --shadow-popover: 0 12px 30px rgba(0, 0, 0, 0.12);
  --shadow-modal: 0 20px 50px rgba(0, 0, 0, 0.2);
  --shadow-input-focus: 0 0 0 3px rgba(16, 185, 129, 0.25);
  --shadow-error-focus: 0 0 0 3px rgba(244, 63, 94, 0.18);

  /* Halos de Fondo */
  --orb-color-primary: rgba(16, 185, 129, 0.1);
  --orb-color-secondary: rgba(5, 150, 105, 0.06);

  /* Alertas */
  --alert-error-bg: rgba(254, 226, 226, 0.7);
  --alert-error-border: #fca5a5;
  --alert-error-text: #991b1b;

  /* --- Aliases Canónicos de Compatibilidad --- */
  --background: var(--bg-viewport);
  --surface: var(--bg-viewport);
  --surface-card: var(--bg-card);
  --surface-elevated: var(--bg-elevated);
  --surface-active: var(--bg-active);
  --border-color: var(--border-subtle);

  /* Controles de Formulario e Inputs (Estándar bi/cartera) */
  --input-height: 38px;
  --input-bg: #ffffff;
  --input-border: #cbd5e1;
  --input-border-hover: #94a3b8;
  --input-focus-border: var(--brand-primary);
  --input-focus-ring: rgba(16, 185, 129, 0.2);
  --input-text: #0f172a;
  --input-placeholder: #94a3b8;
  --label-color: #475569;
}
```

---

## 3. Regla Estricta de Conformidad de Variables CSS (SDD Core Mandate)

> **Mandato Arquitectónico**:
> 1. **Prohibido Inventar Variables Ad-Hoc**: Ningún componente, vista o mock puede declarar nombres de variables CSS inventadas al margen de las descritas en esta especificación.
> 2. **Prohibido Hardcodear Colores**: Queda terminantemente prohibido utilizar códigos de color directos (ej. `#16162a`, `#ffffff`, `rgba(0,0,0,...)`) en propiedades de `background`, `color`, `border` o `box-shadow` de componentes estructurales. Todo elemento debe vincularse a su token correspondiente (`var(--bg-card)`, `var(--text-primary)`, `var(--border-subtle)`, etc.).
> 3. **Conmutación Universal Dual**: Al alternar entre Modo Noche y Modo Día, se deben actualizar simultáneamente `data-theme` y `data-bs-theme` para sincronizar componentes nativos Jolifoods y librerías externas sin desalineaciones cromáticas.
> 4. **Respeto a Sombras y Elevaciones**: En Modo Día, las sombras deben ser sutiles y los bordes claramente contrastados (`--border-subtle: #e2e8f0`); en Modo Noche, las superficies se elevan mediante opacidades oscuras y halos sutiles.
> 5. **Estilo Obligatorio en Controles de Formulario**: Queda estrictamente prohibido renderizar `<input>`, `<select>` o `<textarea>` con estilos nativos del navegador. Todo campo dentro de modales, drawers o vistas debe utilizar el envoltorio `.form-field` / `.drawer-form-field`, etiqueta `.form-label` (uppercase 0.72rem, `--text-secondary`) y contenedor `.input-control` / `.drawer-input-control` con altura de 38px, fondo `var(--input-bg)`, borde `var(--input-border)` y halo de foco de acento corporativo.
> 6. **Taxonomía Estricta de Colores de Texto**:
>    - **Datos Principales, Códigos y Títulos**: Usan siempre `var(--text-primary)` (`#f8fafc` noche / `#0f172a` día). Prohibido colorear códigos de filas con azul o verde arbitrario.
>    - **Subtítulos y Encabezados de Columna**: Usan `var(--text-secondary)` (`#cbd5e1` noche / `#334155` día).
>    - **Placeholders y Ayudas**: Usan `var(--text-muted)` (`#94a3b8` noche / `#64748b` día).
>    - **Color Verde / Rojo / Ámbar**: Exclusivo para estados semánticos en badges (`.badge-status-*`) o indicadores de cambio positivo/negativo, jamás en textos planos genéricos.
