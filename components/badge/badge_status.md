# Componente UI: Badges de Estado y Roles (`Badge`)
## Spec-Driven Development (SDD)

Las **badges** son indicadores compactos para comunicar el estado de una entidad (activo, bloqueado), el rol asignado o el estado de un proceso. Son el único lugar donde el color semántico aparece en datos tabulares (ver [`data_table.md`](../data_table/data_table.md) §1).

- **Regla:** el estado NO DEBE comunicarse solo con color: la badge siempre lleva texto (y opcionalmente un punto). **Por qué:** accesibilidad para personas con daltonismo y para impresión en blanco y negro.
- El texto de cada variante mezcla el color de estado con `--text-primary` (`color-mix`) para mantener contraste legible en ambos temas.

---

## 1. Variantes

| Variante (`variant`) | Clase | Tokens | Texto típico |
| :--- | :--- | :--- | :--- |
| `success` | `.joli-badge-success` | `--status-success` / `--status-success-bg` | Activo, Completado, Aprobado |
| `danger` | `.joli-badge-danger` | `--status-error` / `--status-error-bg` | Inactivo, Bloqueado, Rechazado |
| `warning` | `.joli-badge-warning` | `--status-warning` / `--status-warning-bg` | Pendiente, En revisión, Expirado |
| `info` | `.joli-badge-info` | `--status-info` / `--status-info-bg` | Borrador, Sincronizando |
| `admin` | `.joli-badge-admin` | `--brand-primary` con borde de acento | ADMINISTRADOR, SUPERADMIN |
| `operator` | `.joli-badge-operator` | `--brand-primary` suave | OPERADOR |
| `neutral` | `.joli-badge-neutral` | `--bg-active` / `--text-secondary` | CONSULTA, AUDITOR, sin estado |

---

## 2. Código React (`Badge.tsx`)

```tsx
import React from 'react';

export type BadgeVariant = 'success' | 'danger' | 'warning' | 'info' | 'admin' | 'operator' | 'neutral';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  dot?: boolean;
  size?: 'sm' | 'md';
  /** Texto adicional para lectores de pantalla, p. ej. "Estado:". */
  srPrefix?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral', dot = false, size = 'md', srPrefix }) => (
  <span className={`joli-badge joli-badge-${variant} joli-badge-${size}`}>
    {dot && <span className="joli-badge-dot" aria-hidden="true" />}
    {srPrefix && <span className="visually-hidden">{srPrefix} </span>}
    {children}
  </span>
);
```

`visually-hidden` es la clase de Bootstrap 5 para texto solo visible a lectores de pantalla.

---

## 3. Estilos CSS (`badge.css`)

```css
.joli-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  line-height: 1;
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.3px;
  text-transform: uppercase;
  white-space: nowrap;
  border: 1px solid transparent;
  border-radius: var(--radius-full);
}

.joli-badge-md { padding: 4px 10px; font-size: var(--font-size-2xs); }
.joli-badge-sm { padding: 2px 8px; font-size: 0.625rem; }

.joli-badge-dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
  background-color: var(--badge-accent, currentColor);
}

.joli-badge-success { --badge-accent: var(--status-success); background: var(--status-success-bg); }
.joli-badge-danger  { --badge-accent: var(--status-error);   background: var(--status-error-bg); }
.joli-badge-warning { --badge-accent: var(--status-warning); background: var(--status-warning-bg); }
.joli-badge-info    { --badge-accent: var(--status-info);    background: var(--status-info-bg); }
.joli-badge-operator { --badge-accent: var(--brand-primary); background: var(--status-success-bg); }

.joli-badge-admin {
  --badge-accent: var(--brand-primary);
  background: var(--status-success-bg);
  box-shadow: 0 0 8px var(--brand-glow);
}

.joli-badge-success,
.joli-badge-danger,
.joli-badge-warning,
.joli-badge-info,
.joli-badge-operator,
.joli-badge-admin {
  color: color-mix(in srgb, var(--badge-accent) 55%, var(--text-primary));
  border-color: color-mix(in srgb, var(--badge-accent) 40%, transparent);
}

.joli-badge-neutral {
  color: var(--text-secondary);
  background: var(--bg-active);
  border-color: var(--border-subtle);
}
```
