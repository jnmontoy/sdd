# Tarjeta Corporativa con Header, Body y Footer (`CorporateCard`)
## Componente UI Canónico — Spec-Driven Development (SDD)

Este componente define el estándar visual para tarjetas de contenido corporativo, paneles de configuración y resúmenes de módulos. Proporciona una estructura de 3 secciones desacopladas (**Header, Body y Footer**) con soporte total para tema claro/oscuro y bordes sutiles con halo cromático.

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
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  badge?: {
    text: string;
    variant: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
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
.corp-card {
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-surface, #1e293b);
  border: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.08));
  border-radius: 12px;
  overflow: hidden;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  width: 100%;
}

.corp-card:hover {
  border-color: var(--color-border-hover, rgba(16, 185, 129, 0.3));
}

.corp-card--glow {
  box-shadow: 0 4px 20px -2px rgba(16, 185, 129, 0.08);
}

/* Header de la Tarjeta */
.corp-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background-color: var(--color-bg-surface-elevated, rgba(255, 255, 255, 0.02));
  border-bottom: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.06));
}

.corp-card__title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.corp-card__icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(16, 185, 129, 0.12);
  color: var(--color-primary, #10b981);
}

.corp-card__title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-main, #f8fafc);
}

.corp-card__subtitle {
  margin: 2px 0 0 0;
  font-size: 0.8rem;
  color: var(--color-text-muted, #94a3b8);
}

/* Body de la Tarjeta */
.corp-card__body {
  padding: 20px;
  color: var(--color-text-main, #e2e8f0);
  flex: 1 1 auto;
}

/* Footer de la Tarjeta */
.corp-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background-color: var(--color-bg-surface-dim, rgba(0, 0, 0, 0.15));
  border-top: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.06));
  font-size: 0.82rem;
  color: var(--color-text-muted, #94a3b8);
}

.corp-card__footer-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
```

---

## 4. Implementación de Referencia en React / JSX

```tsx
import React, { useState } from 'react';

export const CorporateCard: React.FC<CorporateCardProps> = ({
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

  return (
    <div className={`corp-card corp-card--${elevation} ${className}`}>
      {/* HEADER */}
      <div className="corp-card__header">
        <div className="corp-card__title-group">
          {icon && <div className="corp-card__icon-box">{icon}</div>}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h3 className="corp-card__title">{title}</h3>
              {badge && (
                <span className={`badge badge--${badge.variant}`}>{badge.text}</span>
              )}
            </div>
            {subtitle && <p className="corp-card__subtitle">{subtitle}</p>}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {headerActions}
          {isCollapsible && (
            <button
              type="button"
              className="btn-icon"
              onClick={() => setCollapsed(!collapsed)}
              title={collapsed ? 'Expandir' : 'Colapsar'}
            >
              {collapsed ? '▼' : '▲'}
            </button>
          )}
        </div>
      </div>

      {/* BODY */}
      {!collapsed && <div className="corp-card__body">{children}</div>}

      {/* FOOTER */}
      {!collapsed && (footerMetadata || footerActions) && (
        <div className="corp-card__footer">
          <div className="corp-card__footer-meta">{footerMetadata}</div>
          {footerActions && (
            <div className="corp-card__footer-actions">
              {footerActions.map((action, idx) => (
                <button
                  key={idx}
                  type="button"
                  className={`btn btn--${action.variant || 'secondary'} btn--sm`}
                  onClick={action.onClick}
                  disabled={action.disabled || action.loading}
                >
                  {action.icon}
                  {action.label}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
```
