# Especificación UI: Interruptor Conmutador (Toggle Switch)
## Spec-Driven Development (SDD)

El **Toggle Switch** (interruptor) es el control para activar o desactivar estados binarios en tiempo real (por ejemplo, habilitar/deshabilitar colaboradores en el módulo de usuarios, activar notificaciones o alternar configuraciones del sistema).

Sustituye a la casilla de verificación cuando la acción tiene efecto inmediato (se guarda al cambiar). En formularios que se guardan con un botón, DEBERÍA usarse una casilla normal.

Accesibilidad: `role="switch"` con `aria-checked`; el **nombre accesible describe qué se activa** (p. ej. "Acceso de Ana Pérez"), no el estado; el estado lo anuncia `aria-checked`. Mientras guarda, el control sigue enfocable con `aria-disabled` y `aria-busy` (un `disabled` real haría perder el foco).

---

## 1. Anatomía Visual y Estados

```text
[ESTADO ACTIVO]                  [ESTADO INACTIVO]               [ESTADO CARGANDO]
(===========)                   (===========)                   (===========)
(        (O))  Activo           ((O)        )  Inactivo         ((*)        )  Guardando...
(===========)                   (===========)                   (===========)
  --brand-primary                 --border-strong                 Spinner en la perilla
```

1. **Pista (`toggle-track`)**: Cápsula redondeada (`border-radius: 9999px`) con transición suave de color (`transition: background-color 0.2s ease`).
2. **Perilla (`toggle-thumb`)**: Círculo deslizante claro (`--text-on-brand`) con sombra `--shadow-card`.
3. **Etiqueta Contextual (`toggle-label`)**: Texto descriptivo opcional ("Activo" / "Inactivo") ubicado a la derecha con badge cromático.

---

## 2. Código HTML / JSX Canónico (React 19 + TypeScript)

```tsx
import React from 'react';
import './toggle_switch.css';

export interface ToggleSwitchProps {
  /** Nombre accesible: qué controla el interruptor. */
  label: string;
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
  label,
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
  // Un <button> ya activa onClick con Enter y Espacio: no se agrega onKeyDown (evita doble cambio)
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // no dispara el clic de la fila de la tabla
    if (disabled || loading) return;
    onChange(!checked);
  };

  return (
    <div className={`joli-toggle-wrapper joli-toggle-${size}`}>
      <button
        type="button"
        id={id}
        name={name}
        role="switch"
        aria-checked={checked}
        aria-label={label}
        aria-disabled={loading || undefined}
        aria-busy={loading || undefined}
        disabled={disabled}
        className={`joli-toggle-track ${checked ? 'is-checked' : 'is-unchecked'} ${loading ? 'is-loading' : ''}`}
        onClick={handleClick}
      >
        <span className="joli-toggle-thumb" aria-hidden="true">
          {loading && <span className="joli-toggle-spinner" />}
        </span>
      </button>

      {showLabel && (
        <span className={`joli-toggle-text ${checked ? 'is-on' : 'is-off'}`} aria-hidden="true">
          {checked ? labelActive : labelInactive}
        </span>
      )}
    </div>
  );
};
```

---

## 3. Hoja de Estilos CSS Canónica (`toggle_switch.css`)
Solo tokens de [`../variables.css`](../variables.css):

```css
/* ==========================================================================
   INTERRUPTOR (TOGGLE SWITCH)
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
  border-radius: var(--radius-full);
  background-color: var(--border-strong);
  cursor: pointer;
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1),
              border-color 0.2s ease,
              box-shadow 0.2s ease;
}

.joli-toggle-track:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
  border-color: var(--border-focus);
}

/* Estado activo */
.joli-toggle-track.is-checked {
  background-color: var(--brand-primary);
}

/* Estado Deshabilitado */
.joli-toggle-track:disabled,
.joli-toggle-track[aria-disabled='true'] {
  opacity: 0.55;
  cursor: not-allowed;
}

/* Thumb (Perilla Deslizante) */
.joli-toggle-thumb {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background-color: var(--text-on-brand);
  box-shadow: var(--shadow-card);
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
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  transition: color 0.2s ease;
}

.joli-toggle-text.is-on {
  color: var(--text-primary);
}

.joli-toggle-text.is-off {
  color: var(--text-muted);
}

/* Spinner miniatura de carga */
.joli-toggle-spinner {
  width: 10px;
  height: 10px;
  border: 2px solid var(--status-success-bg);
  border-top-color: var(--brand-primary);
  border-radius: var(--radius-full);
  animation: joli-spin 0.6s linear infinite;
}

@keyframes@keyframes joli-spin {
  to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
  .joli-toggle-track,
  .joli-toggle-thumb { transition: none; }
}
```

---

## 4. Confirmación al desactivar
Cuando el interruptor **desactiva una cuenta de usuario** (u otra acción con impacto), DEBE abrirse [`ConfirmModal`](../modal/confirm_modal.md) con `requiresJustification`; reactivar PUEDE ser inmediato. Ejemplo de uso en una fila: `<ToggleSwitch size="sm" label={`Acceso de ${user.nombre_completo}`} checked={user.is_active} loading={savingId === user.id} onChange={() => handleToggleUser(user)} />`.

```tsx
const handleToggleUser = (user: UsuarioRow) => {
  if (user.is_active) {
    // Si está ACTIVO y se va a DESACTIVAR: Exigir ConfirmModal con motivo
    setConfirmDialog({
      isOpen: true,
      user,
      action: 'deactivate',
      title: `Suspender acceso de ${user.nombre_completo}`,
      message: '¿Está seguro de suspender este usuario? Perderá acceso inmediato a todos los módulos.'
    });
  } else {
    // Si está INACTIVO y se va a ACTIVAR: Disparar reactivación inmediata
    executeToggleUser(user.id, true);
  }
};
```
