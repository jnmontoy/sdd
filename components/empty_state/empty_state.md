# Especificación de Componente: Estado Vacío (Empty State)
## Guía de implementación SDD

El componente `EmptyState` ofrece una experiencia visual clara, profesional y constructiva cuando una vista, tabla, bandeja o búsqueda no contiene datos, guiando al usuario hacia la siguiente acción a realizar.

---

### 1. Requisitos de Negocio y UX
1. **Claridad Inmediata**: Explica por qué está vacía la pantalla (ej. sin registros iniciales, filtros demasiado restrictivos o error de conexión).
2. **Acción de Retorno / Creación (Call to Action)**: Ofrece un botón de acción principal (ej. "Limpiar filtros", "Crear nuevo registro", "Reintentar").
3. **Variantes Semánticas**:
   - `search`: Cuando los filtros o el buscador no arrojan coincidencias.
   - `inbox`: Cuando la bandeja o listado está vacío por naturaleza.
   - `error`: Cuando ocurrió un fallo recuperable al cargar la información.
4. **Modo Noche / Día**: solo usa tokens de `variables.css`.
5. **Accesibilidad**: `role="status"` (o `role="alert"` en la variante `error`) para que el cambio se anuncie; el ícono es decorativo.
6. **Botones**: `.joli-btn-primary` / `.joli-btn-secondary` de [`icon_action_group.md`](../button/icon_action_group.md) §5. Dentro de una tabla se usa el estado vacío integrado de [`DataTable`](../data_table/data_table.md).

---

### 2. Implementación TypeScript Canónica (`EmptyState.tsx`)

```tsx
import React from 'react';
import { AlertCircle, Inbox, SearchX, type LucideIcon } from 'lucide-react';

export type EmptyStateVariant = 'inbox' | 'search' | 'error';

const VARIANT_ICONS: Record<EmptyStateVariant, LucideIcon> = {
  inbox: Inbox,
  search: SearchX,
  error: AlertCircle,
};

export interface EmptyStateProps {
  variant?: EmptyStateVariant;
  /** Sobrescribe el ícono de la variante. */
  icon?: LucideIcon;
  title: string;
  description: string;
  primaryActionLabel?: string;
  onPrimaryAction?: () => void;
  primaryActionIcon?: LucideIcon;
  secondaryActionLabel?: string;
  onSecondaryAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  variant = 'inbox',
  icon,
  title,
  description,
  primaryActionLabel,
  onPrimaryAction,
  primaryActionIcon: ActionIcon,
  secondaryActionLabel,
  onSecondaryAction,
  className = ''
}) => {
  const Icon = icon ?? VARIANT_ICONS[variant];
  return (
    <div
      className={`joli-empty-state-card is-${variant} ${className}`}
      role={variant === 'error' ? 'alert' : 'status'}
    >
      <div className="empty-state-icon-wrapper" aria-hidden="true">
        <Icon size={44} />
      </div>
      <p className="empty-state-title">{title}</p>
      <p className="empty-state-description">{description}</p>

      {(primaryActionLabel || secondaryActionLabel) && (
        <div className="empty-state-actions">
          {primaryActionLabel && onPrimaryAction && (
            <button
              type="button"
              className="joli-btn-primary"
              onClick={onPrimaryAction}
            >
              {ActionIcon && <ActionIcon size={16} aria-hidden="true" />}
              <span>{primaryActionLabel}</span>
            </button>
          )}

          {secondaryActionLabel && onSecondaryAction && (
            <button
              type="button"
              className="joli-btn-secondary"
              onClick={onSecondaryAction}
            >
              <span>{secondaryActionLabel}</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
};
```

---

### 3. Estilos CSS (`empty_state.css`)

```css
.joli-empty-state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px 24px;
  background-color: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px dashed var(--border-subtle);
  margin: 16px 0;
}

.empty-state-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: var(--radius-full);
  background: var(--bg-elevated);
  color: var(--text-muted);
  margin-bottom: 16px;
}

.joli-empty-state-card.is-error .empty-state-icon-wrapper {
  background: var(--status-error-bg);
  color: var(--status-error);
}

.empty-state-title {
  margin: 0 0 6px;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.empty-state-description {
  max-width: 440px;
  margin: 0 0 20px;
  font-size: var(--font-size-sm);
  line-height: var(--line-height-normal);
  color: var(--text-secondary);
}

.empty-state-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}
```
