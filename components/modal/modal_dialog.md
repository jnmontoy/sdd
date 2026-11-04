# Componente UI: Diálogo Modal Accesible (Modal Dialog)
## Spec-Driven Development (SDD)

El **Modal Dialog** (`ModalDialog`) es el contenedor base para diálogos centrados: confirmaciones críticas, visualizadores de detalle de solo lectura, comparativas ANTES/DESPUÉS y alertas del sistema.

Objetivo de accesibilidad WCAG 2.1 AA: foco atrapado y devuelto al disparador, cierre con `Escape`, bloqueo de scroll de fondo y nombre accesible enlazado al título. Estilos con tokens de [`variables.css`](../variables.css).

### Regla de uso: formularios CRUD van en el drawer

- **Regla:** la creación (`+ Nuevo`) y edición (`Editar`) de registros CRUD DEBERÍA hacerse en el panel lateral derecho ([`drawer.md`](../drawer/drawer.md)), no en un modal ni en una página separada.
- **Por qué:** el drawer conserva visible la tabla de contexto, admite formularios largos con scroll propio y unifica la experiencia entre módulos.
- **Excepciones:** pedido explícito del usuario o una decisión registrada (ADR). Los modales se reservan para confirmaciones ([`confirm_modal.md`](./confirm_modal.md)), firmas ([`signature_modal.md`](../signature/signature_modal.md)), escáneres, sesión expirada ([`session_expiration_modal.md`](./session_expiration_modal.md)) y vistas de solo lectura.

---

## 1. Variantes y Tamaños

| Variante | Ancho Máximo | Caso de Uso Típico |
| :--- | :--- | :--- |
| **`sm`** | `420px` | Confirmación breve ("¿Está seguro de eliminar?"). |
| **`md`** | `580px` | Mensajes con detalle, cambio de contraseña del propio usuario. |
| **`lg`** | `840px` | Visualizador de detalle de solo lectura con pestañas. |
| **`xl`** | `1140px` | Reportes o comparativas de auditoría ANTES / DESPUÉS. |

---

## 2. Hook compartido de accesibilidad (`src/hooks/useModalA11y.ts`)

Lo usan `ModalDialog`, `ConfirmModal` y el drawer ([`drawer.md`](../drawer/drawer.md)). Soporta diálogos apilados (p. ej. un `ConfirmModal` sobre un drawer): solo el diálogo superior responde a `Escape` y `Tab`.

```ts
import { useEffect, useRef, type RefObject } from 'react';

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), ' +
  'select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

/** Pila de diálogos abiertos: solo el último atiende el teclado. */
const openStack: symbol[] = [];

export interface ModalA11yOptions {
  isOpen: boolean;
  onClose?: () => void;
  /** false mientras hay una operación en curso o en diálogos que no se pueden descartar. */
  closeOnEscape?: boolean;
  lockScroll?: boolean;
  /** Elemento que recibe el foco al abrir; por defecto, el primer enfocable. */
  initialFocusRef?: RefObject<HTMLElement | null>;
}

export function useModalA11y<T extends HTMLElement>(
  containerRef: RefObject<T | null>,
  { isOpen, onClose, closeOnEscape = true, lockScroll = true, initialFocusRef }: ModalA11yOptions,
): void {
  // Refs para leer siempre el valor actual sin reejecutar el efecto (evita robar el foco al cambiar isLoading)
  const onCloseRef = useRef(onClose);
  const closeOnEscapeRef = useRef(closeOnEscape);
  useEffect(() => {
    onCloseRef.current = onClose;
    closeOnEscapeRef.current = closeOnEscape;
  }, [onClose, closeOnEscape]);

  useEffect(() => {
    if (!isOpen) return;
    const container = containerRef.current;
    if (!container) return;

    const id = Symbol('modal');
    openStack.push(id);
    const previouslyFocused = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const previousOverflow = document.body.style.overflow;
    if (lockScroll) document.body.style.overflow = 'hidden';

    const getFocusables = () => Array.from(container.querySelectorAll<HTMLElement>(FOCUSABLE));
    (initialFocusRef?.current ?? getFocusables()[0] ?? container).focus();

    const onKeyDown = (event: KeyboardEvent) => {
      if (openStack[openStack.length - 1] !== id) return; // hay otro diálogo encima

      if (event.key === 'Escape') {
        if (closeOnEscapeRef.current && onCloseRef.current) {
          event.preventDefault();
          onCloseRef.current();
        }
        return;
      }
      if (event.key !== 'Tab') return;

      const items = getFocusables();
      if (items.length === 0) {
        event.preventDefault();
        container.focus();
        return;
      }
      const first = items[0];
      const last = items[items.length - 1];
      const active = document.activeElement;
      const outside = !container.contains(active);
      if (event.shiftKey && (active === first || outside)) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && (active === last || outside)) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      const index = openStack.indexOf(id);
      if (index !== -1) openStack.splice(index, 1);
      if (lockScroll) document.body.style.overflow = previousOverflow;
      previouslyFocused?.focus(); // devolver el foco al disparador
    };
    // Solo depende de isOpen: abrir/cerrar es lo único que reinicia el ciclo de foco.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);
}
```

---

## 3. Código JSX / React de referencia (`ModalDialog.tsx`)

```tsx
import React, { useId, useRef } from 'react';
import { createPortal } from 'react-dom';
import { X, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { useModalA11y } from '../../hooks/useModalA11y';

export interface ModalDialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'danger' | 'warning' | 'success';
  /** Cerrar al hacer clic fuera del diálogo (por defecto true). */
  closeOnBackdrop?: boolean;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export const ModalDialog: React.FC<ModalDialogProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  size = 'md',
  variant = 'default',
  closeOnBackdrop = true,
  children,
  footer,
}) => {
  const dialogRef = useRef<HTMLDivElement>(null);
  const titleId = useId();
  const subtitleId = useId();

  useModalA11y(dialogRef, { isOpen, onClose });

  if (!isOpen) return null;

  const icon =
    variant === 'danger' || variant === 'warning' ? <AlertTriangle size={20} aria-hidden="true" /> :
    variant === 'success' ? <CheckCircle2 size={20} aria-hidden="true" /> : null;

  return createPortal(
    <div
      className="joli-modal-backdrop"
      onMouseDown={(e) => {
        // mousedown (no click) evita cerrar al soltar una selección de texto fuera del diálogo
        if (closeOnBackdrop && e.target === e.currentTarget) onClose();
      }}
    >
      <div
        ref={dialogRef}
        className={`joli-modal-dialog joli-modal-${size}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={subtitle ? subtitleId : undefined}
        tabIndex={-1}
      >
        <div className="joli-modal-header">
          <div className="d-flex align-items-center gap-3">
            {icon && <div className={`joli-modal-icon ${variant}`}>{icon}</div>}
            <div>
              <h2 id={titleId} className="joli-modal-title">{title}</h2>
              {subtitle && <p id={subtitleId} className="joli-modal-subtitle">{subtitle}</p>}
            </div>
          </div>
          <button type="button" className="joli-modal-close" onClick={onClose} aria-label="Cerrar">
            <X size={18} aria-hidden="true" />
          </button>
        </div>

        <div className="joli-modal-body">{children}</div>

        {footer && <div className="joli-modal-footer">{footer}</div>}
      </div>
    </div>,
    document.body,
  );
};
```

---

## 4. Estilos CSS (`modal_dialog.css`)

```css
.joli-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background-color: color-mix(in srgb, var(--bg-viewport) 75%, transparent);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  animation: joliModalFadeIn var(--transition-fast);
}

.joli-modal-dialog {
  width: 100%;
  background-color: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-modal);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 40px);
  overflow: hidden;
  animation: joliModalSlideUp var(--transition-base);
}

.joli-modal-dialog:focus {
  outline: none;
}

.joli-modal-sm { max-width: 420px; }
.joli-modal-md { max-width: 580px; }
.joli-modal-lg { max-width: 840px; }
.joli-modal-xl { max-width: 1140px; }

.joli-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-subtle);
}

.joli-modal-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin: 0;
}

.joli-modal-subtitle {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin: 2px 0 0 0;
}

.joli-modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  cursor: pointer;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.joli-modal-close:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.joli-modal-close:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 1px;
}

.joli-modal-body {
  padding: 1.25rem;
  overflow-y: auto;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.joli-modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border-subtle);
  background-color: var(--bg-elevated);
}

.joli-modal-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-full);
}

.joli-modal-icon.danger {
  background-color: var(--status-error-bg);
  color: var(--status-error);
}

.joli-modal-icon.warning {
  background-color: var(--status-warning-bg);
  color: var(--status-warning);
}

.joli-modal-icon.success {
  background-color: var(--status-success-bg);
  color: var(--status-success);
}

@keyframes joliModalFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes joliModalSlideUp {
  from { transform: translateY(16px) scale(0.98); opacity: 0; }
  to { transform: translateY(0) scale(1); opacity: 1; }
}

@media (prefers-reduced-motion: reduce) {
  .joli-modal-backdrop,
  .joli-modal-dialog { animation: none; }
}
```
