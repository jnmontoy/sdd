# Especificación UI: Interruptor Conmutador (Toggle Switch)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

El **Toggle Switch** (conmutador/interruptor) es el control oficial de Jolifoods para activar o desactivar estados binarios en tiempo real (por ejemplo, habilitar/deshabilitar colaboradores en el módulo de usuarios, activar notificaciones o alternar configuraciones del sistema).

Sustituye a los checkboxes convencionales cuando la acción tiene un efecto operacional inmediato.

---

## 1. Anatomía Visual y Estados

```text
[ESTADO ACTIVO]                  [ESTADO INACTIVO]               [ESTADO CARGANDO]
(===========)                   (===========)                   (===========)
(        (O))  Activo           ((O)        )  Inactivo         ((*)        )  Guardando...
(===========)                   (===========)                   (===========)
  Esmeralda (#059669)             Gris Pizarra (#64748b)          Halo con spinner
```

1. **Pista (`toggle-track`)**: Cápsula redondeada (`border-radius: 9999px`) con transición suave de color (`transition: background-color 0.2s ease`).
2. **Perilla (`toggle-thumb`)**: Círculo deslizante blanco con sombra tenue (`box-shadow: 0 1px 3px rgba(0,0,0,0.2)`).
3. **Etiqueta Contextual (`toggle-label`)**: Texto descriptivo opcional ("Activo" / "Inactivo") ubicado a la derecha con badge cromático.

---

## 2. Código HTML / JSX Canónico (React 19 + TypeScript)

```tsx
import React from 'react';
import './toggle_switch.css';

export interface ToggleSwitchProps {
  id?: string;
  checked: boolean;
  onChange: (nextState: boolean) => void;
  disabled?: boolean;
  loading?: boolean;
  size?: 'sm' | 'md' | 'lg';
  labelActive?: string;
  labelInactive?: string;
  showLabel?: boolean;
  name?: string;
}

export const ToggleSwitch: React.FC<ToggleSwitchProps> = ({
  id,
  checked,
  onChange,
  disabled = false,
  loading = false,
  size = 'md',
  labelActive = 'Activo',
  labelInactive = 'Inactivo',
  showLabel = true,
  name
}) => {
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (disabled || loading) return;
    onChange(!checked);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      if (disabled || loading) return;
      onChange(!checked);
    }
  };

  return (
    <div className={`joli-toggle-wrapper joli-toggle-${size}`}>
      <button
        type="button"
        id={id}
        name={name}
        role="switch"
        aria-checked={checked}
        aria-label={checked ? labelActive : labelInactive}
        disabled={disabled || loading}
        className={`joli-toggle-track ${checked ? 'is-checked' : 'is-unchecked'} ${loading ? 'is-loading' : ''}`}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
      >
        <span className="joli-toggle-thumb">
          {loading && <span className="joli-toggle-spinner" />}
        </span>
      </button>

      {showLabel && (
        <span className={`joli-toggle-text ${checked ? 'text-success' : 'text-muted'}`}>
          {checked ? labelActive : labelInactive}
        </span>
      )}
    </div>
  );
};
```

---

## 3. Hoja de Estilos CSS Canónica (`toggle_switch.css`)
Consumiendo estrictamente [`../variables.css`](../variables.css):

```css
/* ==========================================================================
   INTERRUPTOR CONMUTADOR (TOGGLE SWITCH) — JOLIFOODS SDD
   ========================================================================== */

.joli-toggle-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  user-select: none;
}

/* Track Base */
.joli-toggle-track {
  position: relative;
  display: inline-flex;
  align-items: center;
  padding: 2px;
  border: 1px solid transparent;
  border-radius: 9999px;
  background-color: var(--border-color, #cbd5e1);
  cursor: pointer;
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1),
              border-color 0.2s ease,
              box-shadow 0.2s ease;
  outline: none;
}

.joli-toggle-track:focus-visible {
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.35);
  border-color: var(--color-primary, #059669);
}

/* Estado Activo (Esmeralda Jolifoods) */
.joli-toggle-track.is-checked {
  background-color: var(--color-primary, #059669);
}

/* Estado Deshabilitado */
.joli-toggle-track:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

/* Thumb (Perilla Deslizante) */
.joli-toggle-thumb {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: #ffffff;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.2);
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
}

/* Tamaños */
/* Pequeño (Especial para celdas de DataTable) */
.joli-toggle-sm .joli-toggle-track {
  width: 32px;
  height: 18px;
}
.joli-toggle-sm .joli-toggle-thumb {
  width: 14px;
  height: 14px;
}
.joli-toggle-sm .joli-toggle-track.is-checked .joli-toggle-thumb {
  transform: translateX(14px);
}

/* Mediano (Estándar para formularios y Drawers) */
.joli-toggle-md .joli-toggle-track {
  width: 42px;
  height: 24px;
}
.joli-toggle-md .joli-toggle-thumb {
  width: 18px;
  height: 18px;
}
.joli-toggle-md .joli-toggle-track.is-checked .joli-toggle-thumb {
  transform: translateX(18px);
}

/* Grande */
.joli-toggle-lg .joli-toggle-track {
  width: 52px;
  height: 28px;
}
.joli-toggle-lg .joli-toggle-thumb {
  width: 22px;
  height: 22px;
}
.joli-toggle-lg .joli-toggle-track.is-checked .joli-toggle-thumb {
  transform: translateX(24px);
}

/* Etiqueta de Texto */
.joli-toggle-text {
  font-size: 0.8125rem;
  font-weight: 500;
  transition: color 0.2s ease;
}

.joli-toggle-text.text-success {
  color: var(--color-primary, #059669) !important;
}

.joli-toggle-text.text-muted {
  color: var(--text-secondary, #64748b) !important;
}

/* Spinner miniatura de carga */
.joli-toggle-spinner {
  width: 10px;
  height: 10px;
  border: 2px solid rgba(5, 150, 105, 0.2);
  border-top-color: var(--color-primary, #059669);
  border-radius: 50%;
  animation: joli-spin 0.6s linear infinite;
}

@keyframes joli-spin {
  to { transform: rotate(360deg); }
}
```

---

## 4. Patrón de Confirmación Obligatoria en Desactivación
Cuando el toggle se utiliza para **desactivar una cuenta de usuario**, se debe disparar el [`confirm_modal.md`](../modal/confirm_modal.md) con justificación obligatoria:

```tsx
const handleToggleUser = (user: UsuarioRow) => {
  if (user.is_active) {
    // Si está ACTIVO y se va a DESACTIVAR: Exigir ConfirmModal con motivo
    setConfirmDialog({
      isOpen: true,
      user,
      action: 'deactivate',
      title: `Suspender Acceso a ${user.nombre_completo}`,
      message: '¿Está seguro de suspender este usuario? Perderá acceso inmediato a todos los módulos.'
    });
  } else {
    // Si está INACTIVO y se va a ACTIVAR: Disparar reactivación inmediata
    executeToggleUser(user.id, true);
  }
};
```
