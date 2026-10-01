# Especificación de Componente: Estado Vacío (Empty State)
## Ecosistema Jolifoods — Guía de Implementación SDD

El componente `EmptyState` ofrece una experiencia visual clara, profesional y constructiva cuando una vista, tabla, bandeja o búsqueda no contiene datos, guiando al usuario hacia la siguiente acción a realizar.

---

### 1. Requisitos de Negocio y UX
1. **Claridad Inmediata**: Explica por qué está vacía la pantalla (ej. sin registros iniciales, filtros demasiado restrictivos o error de conexión).
2. **Acción de Retorno / Creación (Call to Action)**: Ofrece un botón de acción principal (ej. "Limpiar filtros", "Crear nuevo registro", "Reintentar").
3. **Variantes Semánticas**:
   - `search`: Cuando los filtros o el buscador no arrojan coincidencias.
   - `inbox`: Cuando la bandeja o listado está vacío por naturaleza.
   - `error`: Cuando ocurrió un fallo recuperable al cargar la información.
4. **Modo Noche / Día**: Se adapta automáticamente a los tokens corporativos.

---

### 2. Implementación TypeScript Canónica (`EmptyState.tsx`)

```tsx
import React from 'react';
import { LucideIcon, Inbox, SearchX, AlertCircle, Plus, RotateCcw } from 'lucide-react';

export interface EmptyStateProps {
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
  icon: Icon = Inbox,
  title,
  description,
  primaryActionLabel,
  onPrimaryAction,
  primaryActionIcon: ActionIcon,
  secondaryActionLabel,
  onSecondaryAction,
  className = ''
}) => {
  return (
    <div className={`joli-empty-state-card ${className}`}>
      <div className="empty-state-icon-wrapper">
        <Icon size={44} className="empty-state-icon" />
      </div>
      <h5 className="empty-state-title">{title}</h5>
      <p className="empty-state-description">{description}</p>

      {(primaryActionLabel || secondaryActionLabel) && (
        <div className="empty-state-actions">
          {primaryActionLabel && onPrimaryAction && (
            <button
              type="button"
              className="joli-btn-primary"
              onClick={onPrimaryAction}
            >
              {ActionIcon && <ActionIcon size={16} className="me-1" />}
              <span>{primaryActionLabel}</span>
            </button>
          )}

          {secondaryActionLabel && onSecondaryAction && (
            <button
              type="button"
              className="joli-btn-outline"
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
  background-color: var(--color-bg-card, #FFFFFF);
  border-radius: var(--radius-xl, 12px);
  border: 1px dashed var(--color-border, #E5E7EB);
  margin: 16px 0;
}

[data-theme="dark"] .joli-empty-state-card {
  background-color: var(--color-bg-card, #1E293B);
  border-color: var(--color-border, #334155);
}

.empty-state-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--color-bg-input, #F3F4F6);
  color: var(--color-text-muted, #9CA3AF);
  margin-bottom: 16px;
}

[data-theme="dark"] .empty-state-icon-wrapper {
  background: #0F172A;
  color: #64748B;
}

.empty-state-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
  margin-bottom: 6px;
}

[data-theme="dark"] .empty-state-title {
  color: #F8FAFC;
}

.empty-state-description {
  font-size: 13.5px;
  color: var(--color-text-secondary, #6B7280);
  max-width: 440px;
  margin-bottom: 20px;
  line-height: 1.5;
}

[data-theme="dark"] .empty-state-description {
  color: #94A3B8;
}

.empty-state-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}
```
