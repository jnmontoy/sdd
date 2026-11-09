# Tarjeta Corporativa con Header, Body y Footer (`CorporateCard`)
## Spec-Driven Development (SDD)

Este componente define el estándar visual para tarjetas de contenido corporativo, paneles de configuración y resúmenes de módulos. Proporciona una estructura de 3 secciones desacopladas (**Header, Body y Footer**) con soporte total para tema claro/oscuro y bordes sutiles con halo cromático.

> [!IMPORTANT]
> **Regla de interacción: las tarjetas NO DEBEN moverse al pasar el mouse.**
> No se usa hover que "levanta" la tarjeta (`transform: translateY(...)`, `scale(...)` o cualquier desplazamiento)
> en `CorporateCard`, tarjetas KPI y cualquier otra tarjeta del ecosistema. El hover solo puede cambiar el color del borde
> o la sombra. Motivo: el movimiento distrae en pantallas de trabajo con muchas tarjetas y desplaza el contenido bajo el cursor
> (p. ej. selectores o botones dentro de la tarjeta).

---

## 0. Implementación de referencia (Pandora, `CorporateCard`)

> Patrón completo de la pantalla: [`admin_table_screen.md`](../data_table/admin_table_screen.md). Lo de esta sección manda sobre el resto del documento cuando se contradicen; lo marcado **«Deuda en la referencia»** es lo que el código aún no cumple y NO se copia.

- Clases BEM `corp-card` (no `joli-card`): `<article class="corp-card">` con `corp-card__header | __title-group | __icon-box | __heading | __title-row | __title | __badge--{variant} | __subtitle | __header-actions | __body | __plain-grid | __footer | __footer-meta | __footer-actions`. Título `h3`.
- Props usadas por Usuarios: `title`, `subtitle`, `icon`, `elevation` (`flat | raised | glow`, **por defecto `glow`**), `headerActions`, `footerMetadata`, **`footerCustomActions`** (nodo libre en el pie, p. ej. el grupo de acciones de fila), `className`, `id`. Botones de `footerActions` con `btn btn--{variant} btn--sm`.
- CSS: `border-top: 2px` de marca al 48 %, radio 12 px; hover solo cambia borde y sombra (no se mueve). Variante `.is-inactive`: borde superior rosa y `opacity: .9`.
- Cuerpo de datos: `div.corp-card__plain-grid` (2 columnas, `gap: 6px 14px`) con filas etiqueta (ícono 12 px + texto) → valor.

---

## 1. Anatomía Visual y Estructura

```text
┌────────────────────────────────────────────────────────────────────────┐
│ [HEADER]  [Icono] Título de Tarjeta            [Badge Estado] [⋯ Menú] │
│           Subtítulo o descripción breve                                │
├────────────────────────────────────────────────────────────────────────┤
│ [BODY]                                                                 │
│           Contenido principal, formulario, métricas o lista de datos   │
│           (Layout responsivo con auto-scroll interno opcional)         │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│ [FOOTER]  🕒 Última actualización: Hace 5 min    [Cancelar] [Guardar] │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Contrato de Props en TypeScript

```typescript
export interface CorporateCardAction {
  label: string;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  icon?: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
}

export interface CorporateCardProps {
  id?: string;
  /** Nivel del título según la jerarquía de la página (por defecto h2). */
  headingLevel?: 'h2' | 'h3' | 'h4';
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  badge?: {
    text: string;
    variant: BadgeVariant; // ver ../badge/badge_status.md
  };
  headerActions?: React.ReactNode;
  children: React.ReactNode;
  footerMetadata?: React.ReactNode; // Ej. Timestamps, autor o estado de sincronización
  footerActions?: CorporateCardAction[];
  isCollapsible?: boolean;
  defaultCollapsed?: boolean;
  elevation?: 'flat' | 'raised' | 'glow';
  className?: string;
}
```

---

## 3. Estilos CSS Canónicos (`variables.css`)

```css
/* Contenedor Principal de la Tarjeta */
.joli-card {
  display: flex;
  flex-direction: column;
  background-color: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  width: 100%;
}

/* Solo el borde cambia: sin transform (ver la regla de interacción al inicio) */
.joli-card:hover {
  border-color: var(--border-strong);
}

.joli-card--glow {
  box-shadow: var(--shadow-card), 0 0 0 1px var(--border-card-accent);
}

/* Header de la Tarjeta */
.joli-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background-color: var(--bg-elevated);
  border-bottom: 1px solid var(--border-subtle);
}

.joli-card__title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.joli-card__icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: var(--status-success-bg);
  color: var(--brand-primary);
}

.joli-card__title {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.joli-card__subtitle {
  margin: 2px 0 0 0;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

/* Body de la Tarjeta */
.joli-card__body {
  padding: 20px;
  color: var(--text-primary);
  flex: 1 1 auto;
}

/* Footer de la Tarjeta */
.joli-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background-color: var(--bg-elevated);
  border-top: 1px solid var(--border-subtle);
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.joli-card__footer-actions,
.joli-card__header-actions,
.joli-card__title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.joli-card__collapse-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  color: var(--text-muted);
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.joli-card__collapse-btn:hover { background: var(--bg-hover); color: var(--text-primary); }
.joli-card__collapse-btn:focus-visible { outline: 2px solid var(--border-focus); outline-offset: 1px; }
```

---

## 4. Implementación de Referencia en React / JSX

```tsx
import React, { useId, useState } from 'react';
import { ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { Badge, type BadgeVariant } from '../badge/Badge';

export const CorporateCard: React.FC<CorporateCardProps> = ({
  id,
  headingLevel: Heading = 'h2',
  title,
  subtitle,
  icon,
  badge,
  headerActions,
  children,
  footerMetadata,
  footerActions,
  isCollapsible = false,
  defaultCollapsed = false,
  elevation = 'flat',
  className = '',
}) => {
  const [collapsed, setCollapsed] = useState(defaultCollapsed);
  const titleId = useId();
  const contentId = useId();

  return (
    <section id={id} className={`joli-card joli-card--${elevation} ${className}`} aria-labelledby={titleId}>
      {/* HEADER */}
      <div className="joli-card__header">
        <div className="joli-card__title-group">
          {icon && <div className="joli-card__icon-box" aria-hidden="true">{icon}</div>}
          <div>
            <div className="joli-card__title-row">
              <Heading id={titleId} className="joli-card__title">{title}</Heading>
              {badge && <Badge variant={badge.variant} size="sm">{badge.text}</Badge>}
            </div>
            {subtitle && <p className="joli-card__subtitle">{subtitle}</p>}
          </div>
        </div>
        <div className="joli-card__header-actions">
          {headerActions}
          {isCollapsible && (
            <button
              type="button"
              className="joli-card__collapse-btn"
              onClick={() => setCollapsed((prev) => !prev)}
              aria-expanded={!collapsed}
              aria-controls={contentId}
              aria-label={collapsed ? `Expandir ${title}` : `Colapsar ${title}`}
              title={collapsed ? 'Expandir' : 'Colapsar'}
            >
              {collapsed ? <ChevronDown size={16} aria-hidden="true" /> : <ChevronUp size={16} aria-hidden="true" />}
            </button>
          )}
        </div>
      </div>

      {/* BODY */}
      <div id={contentId} hidden={collapsed}>
      <div className="joli-card__body">{children}</div>

      {/* FOOTER */}
      {(footerMetadata || footerActions) && (
        <div className="joli-card__footer">
          <div className="joli-card__footer-meta">{footerMetadata}</div>
          {footerActions && (
            <div className="joli-card__footer-actions">
              {footerActions.map((action) => (
                <button
                  key={action.label}
                  type="button"
                  className={action.variant === 'primary' ? 'joli-btn-primary' : 'joli-btn-secondary'}
                  onClick={action.onClick}
                  disabled={action.disabled || action.loading}
                  aria-busy={action.loading || undefined}
                >
                  {action.loading ? <Loader2 size={14} className="joli-spin" aria-hidden="true" /> : action.icon}
                  {action.label}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
      </div>
    </section>
  );
};
```

Los botones `.joli-btn-primary` / `.joli-btn-secondary` y `.joli-spin` se definen en [`icon_action_group.md`](../button/icon_action_group.md). La variante `danger` DEBERÍA confirmar con [`ConfirmModal`](../modal/confirm_modal.md) antes de ejecutar.
