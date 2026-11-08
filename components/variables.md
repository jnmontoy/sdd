# Especificación del Sistema de Variables: `variables.css`
## Sistema central de diseño — SDD Joli Foods

`variables.css` es la **fuente única de tokens** (variables CSS con nombre) de tipografía, color, superficies, bordes, sombras y tema del ecosistema. Define el comportamiento de **Modo Noche** (por defecto) y **Modo Día** con variables CSS nativas, sin dependencias externas.

> **Sincronía:** la sección 3 de este documento reproduce `variables.css` completo. Si cambia un token, se DEBE actualizar el `.css` y copiarlo aquí en el mismo cambio.

> **Marca Joli (decidida en Pandora, nov. 2026):** Pandora ya usa la paleta Joli: morado `#4b3878` (sitio web), amarillo `#eebf31`, naranja `#d4652c` y azul `#67b6d9` (logo). Esa paleta vive en `frontend-admin/src/variables.css` como `--joli-*`, con una «paleta base» con nombre (`--slate-800`, `--red-500`…) de la que salen todos los colores. La hoja de la sección 3 todavía tiene la paleta verde anterior: al llevar la marca Joli a otro proyecto, tome como referencia la de Pandora y actualice esta sección. Las tipografías Gotham y Arvo siguen pendientes (Gotham requiere licencia).

---

## 1. Conmutación Día / Noche

- **Modo Noche (por defecto):** activo en `:root`, `[data-theme='dark']` y `[data-bs-theme='dark']` con `color-scheme: dark`.
- **Modo Día:** se activa con `[data-theme='light']` y `[data-bs-theme='light']` en `<html>`.
- Se DEBEN actualizar ambos atributos a la vez (`data-theme` para los componentes propios y `data-bs-theme` para Bootstrap).

```html
<!-- Modo Noche -->
<html lang="es" data-theme="dark" data-bs-theme="dark">

<!-- Modo Día -->
<html lang="es" data-theme="light" data-bs-theme="light">
```

### Función de conmutación con preferencia persistida

La clave de almacenamiento DEBE llevar el identificador de la app (varias apps pueden compartir dominio). Ver `STORAGE_KEYS` en `src/config/storageKeys.ts`.

```typescript
// src/utils/theme.ts
import { STORAGE_KEYS } from '@/config/storageKeys'; // theme: `${APP}:theme`

export type Theme = 'dark' | 'light';

export function applyTheme(theme: Theme): void {
  const html = document.documentElement;
  html.setAttribute('data-theme', theme);
  html.setAttribute('data-bs-theme', theme);
  html.style.colorScheme = theme;
  try {
    localStorage.setItem(STORAGE_KEYS.theme, theme); // preferencia no sensible
  } catch {
    // Modo privado o almacenamiento bloqueado: el tema aplica solo en esta sesión.
  }
}

export function toggleTheme(): Theme {
  const current = (document.documentElement.getAttribute('data-theme') as Theme) || 'dark';
  const next: Theme = current === 'dark' ? 'light' : 'dark';
  applyTheme(next);
  return next;
}
```

---

## 2. Catálogo de tokens

| Grupo | Tokens | Cambia con el tema |
| :--- | :--- | :--- |
| Tipografía | `--font-family`, `--font-family-mono`, `--font-size-2xs` … `--font-size-4xl`, `--font-weight-*`, `--line-height-*` | No |
| Espaciado | `--space-1` (4px) … `--space-6` (24px), `--space-8` (32px) | No |
| Radios / layout | `--radius-sm` … `--radius-2xl`, `--radius-full`, `--topbar-height` | No |
| Movimiento y capas | `--transition-fast/base/slow`, `--z-base` … `--z-toast` | No |
| Marca y estados | `--brand-primary`, `--brand-primary-hover`, `--brand-primary-light`, `--brand-glow`, `--status-success/error/warning/info` y sus `-bg` | No |
| Acentos categóricos | `--accent-blue`, `--accent-cyan`, `--accent-indigo`, `--accent-violet`, `--accent-excel`, `--accent-excel-hover` | No |
| Superficies fijas | `--surface-paper`, `--ink-signature`, `--overlay-scrim`, `--overlay-surface`, `--overlay-border`, `--overlay-control-hover`, `--text-on-overlay` | No (van sobre video, PDF o papel) |
| Series de gráficas | `--chart-primary`, `--chart-secondary`, `--chart-warning`, `--chart-danger`, `--chart-accent`, `--chart-purple` | No |
| Superficies | `--bg-viewport`, `--bg-card`, `--bg-elevated`, `--bg-active`, `--bg-hover`, `--bg-input`, `--bg-input-focus`, `--bg-btn-secondary(-hover)` | Sí |
| Texto | `--text-primary`, `--text-secondary`, `--text-muted`, `--text-tertiary`, `--text-on-brand` | Sí |
| Bordes | `--border-subtle`, `--border-strong`, `--border-card-accent`, `--border-focus`, `--border-error` | Sí |
| Sombras / vidrio | `--glass-*`, `--shadow-card`, `--shadow-popover`, `--shadow-modal`, `--shadow-input-focus`, `--shadow-error-focus` | Sí |
| Alertas y halos | `--alert-error-*`, `--orb-color-*` | Sí |
| Gráficas (ejes) | `--chart-grid`, `--chart-text`, `--chart-tooltip-bg`, `--chart-tooltip-border`, `--chart-tooltip-text`, `--chart-tooltip-label` | Sí |
| Formularios | `--input-height`, `--input-bg`, `--input-border`, `--input-border-hover`, `--input-focus-border`, `--input-focus-ring`, `--input-text`, `--input-placeholder`, `--label-color` | Sí |

**Fondos translúcidos de un acento o estado:** en lugar de crear un token por cada opacidad, use `color-mix()` (soportado por los navegadores actuales):

```css
.icono-info { color: var(--accent-blue); background: color-mix(in srgb, var(--accent-blue) 12%, transparent); }
```

### Alias de compatibilidad (obsoletos)

La sección 3b de `variables.css` mapea nombres heredados a los tokens canónicos para que las especificaciones y proyectos anteriores no se queden sin color. El código nuevo NO DEBERÍA usarlos.

| Alias heredado | Token canónico |
| :--- | :--- |
| `--primary`, `--color-primary`, `--accent-color` | `--brand-primary` |
| `--color-primary-light` / `--color-primary-dark` | `--brand-primary-light` / `--brand-primary-hover` |
| `--color-danger`, `--error` / `--color-warning` | `--status-error` / `--status-warning` |
| `--color-text-primary`, `--color-text-main` / `--color-text-secondary` / `--color-text-muted` | `--text-primary` / `--text-secondary` / `--text-muted` |
| `--bg-base`, `--color-bg-base`, `--color-bg-body`, `--color-bg-surface-dim` | `--bg-viewport` |
| `--bg-surface`, `--color-bg-card`, `--color-bg-surface` | `--bg-card` |
| `--color-bg-surface-elevated`, `--bg-secondary`, `--bg-muted` / `--bg-tertiary` | `--bg-elevated` / `--bg-active` |
| `--color-bg-card-hover` / `--color-bg-input` | `--bg-hover` / `--bg-input` |
| `--color-border`, `--color-border-subtle`, `--border-default` / `--color-border-hover` | `--border-subtle` / `--border-strong` |
| `--focus-ring` | `--shadow-input-focus` |
| `--weight-*` / `--text-xs` … `--text-2xl` | `--font-weight-*` / `--font-size-*` |
| `--shadow-sm` / `--shadow-md` / `--shadow-xl` | `--shadow-card` / `--shadow-popover` / `--shadow-modal` |
| `--radius-pill` / `--border-radius-sm/md/lg` | `--radius-full` / `--radius-sm/md/lg` |
| `--transition-normal` / `--topheader-height` | `--transition-base` / `--topbar-height` |

---

## 3. Hoja de estilos completa (`variables.css`)

```css
/* ==========================================================================
   SISTEMA DE VARIABLES DE DISEÑO (CSS PURO) — SDD JOLI FOODS
   Fuente única de tokens: textos, superficies, estados y tema Día/Noche.
   La especificación y el catálogo de tokens están en variables.md.
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

  /* --- Escala de espaciado --- */
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-5: 1.25rem;  /* 20px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */

  /* --- Acentos categóricos (iconos de KPI, series de gráficas, categorías) ---
     Uso: color de icono/serie. Para fondos translúcidos use
     color-mix(in srgb, var(--accent-*) 12%, transparent). */
  --accent-blue: #3b82f6;
  --accent-cyan: #06b6d4;
  --accent-indigo: #6366f1;
  --accent-violet: #8b5cf6;
  --accent-excel: #107c41;        /* Botón "Exportar a Excel" (color reconocible de la herramienta) */
  --accent-excel-hover: #0e6835;

  /* --- Superficies que NO cambian con el tema ---
     Papel de documentos (PDF, firma) y capas sobre video/cámara o visores. */
  --surface-paper: #ffffff;
  --ink-signature: #0f172a;       /* Trazo de firma: debe verse sobre papel blanco impreso */
  --overlay-scrim: rgba(15, 23, 42, 0.72);     /* Fondo de modales y cortinas sobre video */
  --overlay-surface: rgba(15, 23, 42, 0.85);   /* Píldoras/controles flotantes sobre video o PDF */
  --overlay-border: rgba(255, 255, 255, 0.12);
  --overlay-control-hover: rgba(255, 255, 255, 0.2);
  --text-on-overlay: #f8fafc;

  /* --- Series de gráficas (colores de datos) --- */
  --chart-primary: var(--brand-primary);
  --chart-secondary: var(--accent-blue);
  --chart-warning: var(--status-warning);
  --chart-danger: var(--status-error);
  --chart-accent: var(--accent-cyan);
  --chart-purple: var(--accent-violet);
}

/* --------------------------------------------------------------------------
   2. TEMA MODO NOCHE (DARK MODE - POR DEFECTO)
   Soporte simultáneo para :root, [data-theme='dark'] y [data-bs-theme='dark']
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

  /* Gráficas: rejilla, ejes y tooltip */
  --chart-grid: rgba(51, 65, 85, 0.5);
  --chart-text: #94a3b8;
  --chart-tooltip-bg: rgba(30, 41, 59, 0.95);
  --chart-tooltip-border: rgba(255, 255, 255, 0.1);
  --chart-tooltip-text: #f8fafc;
  --chart-tooltip-label: #94a3b8;

  /* --- Aliases Canónicos de Compatibilidad --- */
  --background: var(--bg-viewport);
  --surface: var(--bg-viewport);
  --surface-card: var(--bg-card);
  --surface-elevated: var(--bg-elevated);
  --surface-active: var(--bg-active);
  --border-color: var(--border-subtle);

  /* Controles de formulario e inputs */
  --input-height: 38px;
  --input-bg: var(--bg-card);
  --input-border: var(--border-subtle);
  --input-border-hover: var(--border-strong);
  --input-focus-border: var(--brand-primary);
  --input-focus-ring: rgba(16, 185, 129, 0.25);
  --input-text: var(--text-primary);
  --input-placeholder: var(--text-muted);
  --label-color: var(--text-secondary);
}

/* --------------------------------------------------------------------------
   3. TEMA MODO DÍA (LIGHT MODE)
   Soporte simultáneo para [data-theme='light'] y [data-bs-theme='light']
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

  /* Gráficas: rejilla, ejes y tooltip */
  --chart-grid: rgba(203, 213, 225, 0.8);
  --chart-text: #64748b;
  --chart-tooltip-bg: rgba(15, 23, 42, 0.92);
  --chart-tooltip-border: rgba(255, 255, 255, 0.15);
  --chart-tooltip-text: #f8fafc;
  --chart-tooltip-label: #cbd5e1;

  /* --- Aliases Canónicos de Compatibilidad --- */
  --background: var(--bg-viewport);
  --surface: var(--bg-viewport);
  --surface-card: var(--bg-card);
  --surface-elevated: var(--bg-elevated);
  --surface-active: var(--bg-active);
  --border-color: var(--border-subtle);

  /* Controles de formulario e inputs */
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

/* --------------------------------------------------------------------------
   3b. ALIAS DE COMPATIBILIDAD (OBSOLETOS)
   Nombres heredados que aparecen en especificaciones y proyectos anteriores.
   Se resuelven contra los tokens canónicos para que nada quede sin color.
   El código nuevo NO DEBERÍA usarlos: use el token canónico de la derecha.
   Se declaran sobre cada contenedor con tema para que se recalculen si el
   atributo data-theme se aplica en un elemento distinto de <html>.
   -------------------------------------------------------------------------- */
:root,
[data-theme],
[data-bs-theme] {
  /* Marca y estados */
  --primary: var(--brand-primary);
  --color-primary: var(--brand-primary);
  --color-primary-light: var(--brand-primary-light);
  --color-primary-dark: var(--brand-primary-hover);
  --accent-color: var(--brand-primary);
  --color-danger: var(--status-error);
  --color-warning: var(--status-warning);
  --error: var(--status-error);

  /* Texto */
  --color-text-primary: var(--text-primary);
  --color-text-main: var(--text-primary);
  --color-text-secondary: var(--text-secondary);
  --color-text-muted: var(--text-muted);

  /* Superficies */
  --bg-base: var(--bg-viewport);
  --color-bg-base: var(--bg-viewport);
  --color-bg-body: var(--bg-viewport);
  --color-bg-surface-dim: var(--bg-viewport);
  --bg-surface: var(--bg-card);
  --color-bg-card: var(--bg-card);
  --color-bg-surface: var(--bg-card);
  --color-bg-surface-elevated: var(--bg-elevated);
  --bg-secondary: var(--bg-elevated);
  --bg-muted: var(--bg-elevated);
  --bg-tertiary: var(--bg-active);
  --color-bg-card-hover: var(--bg-hover);
  --color-bg-input: var(--bg-input);

  /* Bordes y foco */
  --color-border: var(--border-subtle);
  --color-border-subtle: var(--border-subtle);
  --border-default: var(--border-subtle);
  --color-border-hover: var(--border-strong);
  --focus-ring: var(--shadow-input-focus);

  /* Tipografía */
  --weight-regular: var(--font-weight-regular);
  --weight-medium: var(--font-weight-medium);
  --weight-semibold: var(--font-weight-semibold);
  --weight-bold: var(--font-weight-bold);
  --weight-extrabold: var(--font-weight-extrabold);
  --text-xs: var(--font-size-xs);
  --text-sm: var(--font-size-sm);
  --text-base: var(--font-size-base);
  --text-lg: var(--font-size-lg);
  --text-xl: var(--font-size-xl);
  --text-2xl: var(--font-size-2xl);

  /* Sombras, radios, tiempos y layout */
  --shadow-sm: var(--shadow-card);
  --shadow-md: var(--shadow-popover);
  --shadow-xl: var(--shadow-modal);
  --radius-pill: var(--radius-full);
  --border-radius-sm: var(--radius-sm);
  --border-radius-md: var(--radius-md);
  --border-radius-lg: var(--radius-lg);
  --transition-normal: var(--transition-base);
  --topheader-height: var(--topbar-height);
}

/* ==========================================================================
   4. CLASES DE UTILIDAD PARA CONTROLES DE FORMULARIO (MODALES Y DRAWERS)
   Garantiza que ningún input, select o textarea quede con estilo nativo
   ========================================================================== */
.form-field,
.drawer-form-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 1.1rem;
  width: 100%;
  box-sizing: border-box;
}

.form-label,
.drawer-field-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--label-color, var(--text-secondary));
  text-transform: uppercase;
  letter-spacing: 0.04em;
  user-select: none;
  margin-bottom: 0.25rem;
}

.input-control,
.form-input-control,
.drawer-input-control {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  background: var(--input-bg, var(--bg-card));
  border: 1px solid var(--input-border, var(--border-subtle));
  border-radius: var(--radius-md, 8px);
  min-height: var(--input-height, 38px);
  box-sizing: border-box;
  transition: border-color var(--transition-fast, 150ms ease), box-shadow var(--transition-fast, 150ms ease), background-color var(--transition-fast, 150ms ease);
}

.input-control:hover:not(:focus-within),
.form-input-control:hover:not(:focus-within),
.drawer-input-control:hover:not(:focus-within) {
  border-color: var(--input-border-hover, var(--border-strong));
}

.input-control:focus-within,
.form-input-control:focus-within,
.drawer-input-control:focus-within {
  border-color: var(--input-focus-border, var(--brand-primary));
  box-shadow: 0 0 0 3px var(--input-focus-ring, rgba(16, 185, 129, 0.2));
}

.form-control,
.drawer-field-input,
.input-control input,
.input-control select,
.input-control textarea {
  width: 100%;
  height: 100%;
  min-height: calc(var(--input-height, 38px) - 2px);
  background: transparent !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  padding: 0.45rem 0.75rem;
  font-family: inherit;
  font-size: 0.84rem;
  color: var(--input-text, var(--text-primary)) !important;
  box-sizing: border-box;
}

.input-control.has-icon .form-control,
.input-control.has-icon input,
.drawer-input-control.has-icon .drawer-field-input {
  padding-left: 2.35rem;
}

.input-control .input-icon,
.drawer-input-control .drawer-input-icon {
  position: absolute;
  left: 0.75rem;
  color: var(--text-muted);
  pointer-events: none;
  flex-shrink: 0;
  transition: color 0.2s ease, transform 0.2s ease;
}

.input-control:focus-within .input-icon,
.drawer-input-control:focus-within .drawer-input-icon {
  color: var(--input-focus-border, var(--brand-primary));
  transform: scale(1.05);
}

.form-control::placeholder,
.drawer-field-input::placeholder,
.input-control input::placeholder {
  color: var(--input-placeholder, var(--text-muted));
  opacity: 0.75;
}

/* ==========================================================================
   5. CONTROLES PARA DIÁLOGOS Y MODALES DE CONFIRMACIÓN (CONFIRM MODAL)
   Estilos corporativos para campo de justificación de auditoría obligatorio
   ========================================================================== */
.joli-modal-justification-box {
  width: 100%;
  margin: 0.5rem 0 1.35rem 0;
  text-align: left;
  box-sizing: border-box;
}

.joli-modal-justification-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--label-color, var(--text-secondary));
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.4rem;
  user-select: none;
}

.joli-modal-justification-counter {
  font-size: 0.7rem;
  font-family: var(--font-family-mono, monospace);
  color: var(--text-muted);
  transition: color var(--transition-fast, 150ms ease);
}

.joli-modal-justification-counter.is-valid {
  color: var(--status-success);
  font-weight: 700;
}

.joli-modal-textarea {
  width: 100% !important;
  box-sizing: border-box !important;
  min-height: 84px;
  max-height: 160px;
  background: var(--input-bg, var(--bg-card)) !important;
  border: 1px solid var(--input-border, var(--border-subtle)) !important;
  border-radius: var(--radius-md, 8px) !important;
  padding: 0.65rem 0.85rem;
  font-family: inherit;
  font-size: 0.84rem;
  color: var(--input-text, var(--text-primary)) !important;
  line-height: 1.45;
  resize: vertical;
  outline: none !important;
  transition: border-color var(--transition-fast, 150ms ease), box-shadow var(--transition-fast, 150ms ease);
}

.joli-modal-textarea:focus {
  border-color: var(--brand-primary) !important;
  box-shadow: 0 0 0 3px var(--input-focus-ring, rgba(16, 185, 129, 0.25)) !important;
}

.joli-modal-textarea::placeholder {
  color: var(--input-placeholder, var(--text-muted));
  opacity: 0.75;
}

.joli-modal-textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
```

---

## 4. Reglas de conformidad

1. **Tokens en lugar de colores fijos.** El CSS de los componentes DEBE usar `var(--token)` en `background`, `color`, `border` y `box-shadow`; NO DEBE quemar hexadecimales ni `rgba()` de color.
   - **Por qué:** un color fijo no cambia con el tema (rompe el Modo Día o el Noche) y obliga a buscar y reemplazar en todo el código si cambia la marca.
   - **Excepciones:** este archivo; los SVG de marca; la plantilla autocontenida de mock si replica los tokens en un único bloque `:root`; y el color que exige una API de Canvas (`strokeStyle`, `fillStyle`), que DEBERÍA leerse de un token con `getComputedStyle`.
1b. **Desde JavaScript, colores por clases.** Los componentes (JSX/TSX) NO DEBEN escribir colores: ni hexadecimales, ni `rgba()`, ni `style={{ color: 'var(--x)' }}`, ni `fill="var(--x)"`. Se aplica una clase (`className="texto-exito"`, `` `avatar-color-${n}` ``, `` `doc-${tipo}` ``) cuyo CSS usa los tokens de este archivo. Si el color depende de un dato, el código elige la clase, no el color.
   - **Por qué:** así todos los colores quedan unidos a `variables.css` y se controlan desde su CSS; un color escrito en el componente no cambia con el tema ni con la marca, y no aparece al buscar en los CSS.
   - **Única excepción:** un formato que no entiende CSS (por ejemplo el XML de Excel o un Canvas) lee el valor del token con `getComputedStyle(document.documentElement).getPropertyValue('--token')` en el momento de usarlo.
   - **Apps móviles (React Native, sin CSS):** el equivalente de `variables.css` es `constants/theme.ts` (`PALETA` y `COLORS`); los componentes usan solo esas constantes, nunca colores escritos.
2. **No inventar variables.** Un componente NO DEBE declarar variables de color propias (tampoco con nombres como `--chat-*` o `--serie-*` en su CSS). Si falta un token, se agrega aquí (en ambos temas si depende del tema) y se documenta en este archivo.
   - **Por qué:** los tokens dispersos producen paletas paralelas que no respetan el tema.
3. **Conmutación dual.** Al cambiar de tema se DEBEN actualizar `data-theme` y `data-bs-theme` a la vez.
   - **Por qué:** Bootstrap lee `data-bs-theme`; los componentes propios leen `data-theme`. Si solo cambia uno, quedan colores mezclados.
4. **Controles de formulario con estilo.** Los `<input>`, `<select>` y `<textarea>` DEBERÍAN usar `.form-field` / `.drawer-form-field`, etiqueta `.form-label` asociada con `htmlFor`, y contenedor `.input-control` / `.drawer-input-control`.
   - **Por qué:** el estilo nativo del navegador no respeta el tema oscuro y varía entre navegadores.
5. **Jerarquía de texto.**
   - Datos principales, códigos y títulos: `var(--text-primary)`.
   - Subtítulos y encabezados de columna: `var(--text-secondary)`.
   - Ayudas y textos secundarios: `var(--text-muted)`.
   - Verde, rojo y ámbar se reservan para estados (badges, indicadores de variación), no para texto genérico.
   - **Por qué:** el color comunica estado; usarlo como decoración le resta significado y puede bajar el contraste.
6. **Contraste.** Toda combinación texto/fondo DEBERÍA cumplir WCAG 2.1 AA (4.5:1 en texto normal) en ambos temas. Verifíquelo al agregar o cambiar un token.
