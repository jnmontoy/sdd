# Componente UI: Modal de Confirmación Corporativo (`ConfirmModal`)
## Spec-Driven Development (SDD)

> **Origen:** patrón tomado de bi (módulo de cartera). Aquí se describe de forma genérica.

`ConfirmModal` reemplaza las funciones nativas del navegador (`window.confirm()` / `window.alert()`) con un diálogo accesible, con tema Noche/Día, estado de carga asíncrona (`isLoading`), inversión de peso visual para acciones destructivas (`emphasizeCancel`) y campo opcional de justificación para trazabilidad.

---

## 1. Regla de uso

- **Regla:** las acciones destructivas o sensibles (eliminar, desactivar, cerrar sesión con cambios sin guardar, aprobar cambios) DEBEN pedir confirmación con `ConfirmModal`; el código NO DEBE usar `window.confirm()` ni `window.alert()`.
- **Por qué:** los diálogos nativos bloquean el hilo principal, no respetan el tema, no se pueden probar con E2E de forma confiable y no permiten capturar una justificación auditable.
- **Excepciones:** ninguna en código de aplicación.

---

## 2. Código JSX / React de referencia (`ConfirmModal.tsx`)

Usa el hook compartido `useModalA11y` definido en [`modal_dialog.md`](./modal_dialog.md) §2 (foco atrapado, Escape, foco devuelto al disparador, bloqueo de scroll y soporte para diálogos apilados).

```tsx
import React, { useEffect, useId, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { AlertOctagon, AlertTriangle, CheckCircle2, Info, Loader2, X } from 'lucide-react';
import { useModalA11y } from '../../hooks/useModalA11y';

export type ConfirmModalType = 'danger' | 'warning' | 'info' | 'primary' | 'success';

export interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (justification?: string) => void | Promise<void>;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: ConfirmModalType;
  isLoading?: boolean;
  /** Invierte el peso visual: Cancelar resalta y recibe el foco; Confirmar queda neutro.
   *  Evita confirmaciones accidentales por hábito en acciones destructivas. */
  emphasizeCancel?: boolean;
  /** Exige una justificación escrita (se envía a onConfirm para el registro de auditoría). */
  requiresJustification?: boolean;
  /** Caracteres mínimos de la justificación (por defecto 10). */
  justificationMinLength?: number;
  justificationLabel?: string;
  justificationPlaceholder?: string;
}

const ICONS: Record<ConfirmModalType, React.ReactNode> = {
  danger: <AlertOctagon size={36} aria-hidden="true" />,
  warning: <AlertTriangle size={36} aria-hidden="true" />,
  info: <Info size={36} aria-hidden="true" />,
  primary: <Info size={36} aria-hidden="true" />,
  success: <CheckCircle2 size={36} aria-hidden="true" />,
};

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  type = 'danger',
  isLoading = false,
  emphasizeCancel = false,
  requiresJustification = false,
  justificationMinLength = 10,
  justificationLabel = 'Motivo o justificación',
  justificationPlaceholder = 'Describa el motivo de esta acción...',
}) => {
  const [justification, setJustification] = useState('');
  const dialogRef = useRef<HTMLDivElement>(null);
  const cancelBtnRef = useRef<HTMLButtonElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const titleId = useId();
  const messageId = useId();
  const justificationId = useId();
  const counterId = useId();

  // Foco inicial: justificación si se exige; si no, Cancelar (acción segura por defecto)
  useModalA11y(dialogRef, {
    isOpen,
    onClose,
    closeOnEscape: !isLoading,
    initialFocusRef: requiresJustification ? textareaRef : cancelBtnRef,
  });

  // Reiniciar la justificación al cerrar
  useEffect(() => {
    if (!isOpen) setJustification('');
  }, [isOpen]);

  if (!isOpen) return null;

  const currentLength = justification.trim().length;
  const isJustificationValid = !requiresJustification || currentLength >= justificationMinLength;

  const cancelClassName = emphasizeCancel ? `joli-btn-modal-primary ${type}` : 'joli-btn-modal-secondary';
  const confirmClassName = emphasizeCancel ? 'joli-btn-modal-secondary' : `joli-btn-modal-primary ${type}`;

  const handleConfirmClick = () => {
    if (!isJustificationValid || isLoading) return;
    void onConfirm(requiresJustification ? justification.trim() : undefined);
  };

  return createPortal(
    <div className="joli-modal-overlay">
      <div
        ref={dialogRef}
        className="joli-confirm-modal-container joli-modal-fade-in"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={messageId}
        aria-busy={isLoading}
        tabIndex={-1}
        data-testid="confirm-modal"
      >
        <button
          type="button"
          className="joli-modal-close-icon"
          onClick={onClose}
          disabled={isLoading}
          aria-label="Cerrar"
        >
          <X size={20} aria-hidden="true" />
        </button>

        <div className={`joli-modal-icon-wrapper ${type}`}>{ICONS[type]}</div>

        <div className="joli-confirm-modal-content">
          <h2 id={titleId} className="joli-confirm-modal-title">{title}</h2>
          <p id={messageId} className="joli-confirm-modal-message">{message}</p>
        </div>

        {requiresJustification && (
          <div className="joli-modal-justification-box">
            <div className="joli-modal-justification-label">
              <label htmlFor={justificationId}>{justificationLabel}</label>
              <span
                id={counterId}
                className={`joli-modal-justification-counter ${isJustificationValid ? 'is-valid' : ''}`}
              >
                {currentLength} / {justificationMinLength} mín.
              </span>
            </div>
            <textarea
              ref={textareaRef}
              id={justificationId}
              className="joli-modal-textarea"
              placeholder={justificationPlaceholder}
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              disabled={isLoading}
              required
              aria-describedby={counterId}
              aria-invalid={!isJustificationValid}
              rows={3}
            />
          </div>
        )}

        <div className="joli-confirm-modal-actions">
          {cancelText && (
            <button
              type="button"
              ref={cancelBtnRef}
              className={cancelClassName}
              onClick={onClose}
              disabled={isLoading}
            >
              {cancelText}
            </button>
          )}
          <button
            type="button"
            className={confirmClassName}
            onClick={handleConfirmClick}
            disabled={!isJustificationValid || isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 size={16} className="joli-spin me-2" aria-hidden="true" />
                <span>Procesando...</span>
              </>
            ) : (
              confirmText
            )}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
};
```

**Contrato con el backend:** si `requiresJustification` está activo, el texto DEBE enviarse en la petición (p. ej. `{ "justificacion": "..." }`) y el backend DEBE validarlo y guardarlo en el registro de auditoría; la validación del frontend es solo de experiencia de usuario.

---

## 3. Estilos CSS (`confirm_modal.css`)

Los estilos del campo de justificación (`.joli-modal-justification-*`, `.joli-modal-textarea`) viven en [`variables.css`](../variables.css) §5 y no se duplican aquí.

```css
.joli-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: color-mix(in srgb, var(--bg-viewport) 75%, transparent);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.joli-confirm-modal-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 90%;
  max-width: 460px;
  padding: 2.25rem;
  text-align: center;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-modal);
}

.joli-confirm-modal-container:focus {
  outline: none;
}

.joli-modal-close-icon {
  position: absolute;
  top: 1.25rem;
  right: 1.25rem;
  background: none;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: color var(--transition-fast);
}

.joli-modal-close-icon:hover {
  color: var(--text-primary);
}

.joli-modal-close-icon:focus-visible,
.joli-btn-modal-primary:focus-visible,
.joli-btn-modal-secondary:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 2px;
}

.joli-modal-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 76px;
  height: 76px;
  margin-bottom: 1.25rem;
  border-radius: var(--radius-xl);
  border: 1px solid transparent;
}

.joli-modal-icon-wrapper.danger {
  background: var(--status-error-bg);
  color: var(--status-error);
  border-color: var(--status-error);
}

.joli-modal-icon-wrapper.warning {
  background: var(--status-warning-bg);
  color: var(--status-warning);
  border-color: var(--status-warning);
}

.joli-modal-icon-wrapper.info {
  background: var(--status-info-bg);
  color: var(--status-info);
  border-color: var(--status-info);
}

.joli-modal-icon-wrapper.primary {
  background: var(--status-success-bg);
  color: var(--brand-primary);
  border-color: var(--border-card-accent);
}

.joli-modal-icon-wrapper.success {
  background: var(--status-success-bg);
  color: var(--status-success);
  border-color: var(--status-success);
}

.joli-confirm-modal-content {
  margin-bottom: 1.75rem;
}

.joli-confirm-modal-title {
  margin: 0 0 0.5rem;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.joli-confirm-modal-message {
  max-height: 220px;
  margin: 0;
  padding-right: 4px;
  overflow-y: auto;
  font-size: var(--font-size-sm);
  line-height: var(--line-height-relaxed);
  color: var(--text-secondary);
}

.joli-confirm-modal-actions {
  display: flex;
  gap: 0.75rem;
  width: 100%;
}

.joli-btn-modal-secondary {
  flex: 1;
  padding: 0.75rem 1rem;
  background: var(--bg-btn-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: background-color var(--transition-fast), border-color var(--transition-fast);
}

.joli-btn-modal-secondary:hover:not(:disabled) {
  background: var(--bg-btn-secondary-hover);
}

.joli-btn-modal-primary {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1rem;
  color: var(--text-on-brand);
  border: none;
  border-radius: var(--radius-lg);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: filter var(--transition-fast), transform var(--transition-fast);
}

.joli-btn-modal-primary:hover:not(:disabled) {
  filter: brightness(0.92);
  transform: translateY(-1px);
}

.joli-btn-modal-primary.danger  { background: var(--status-error); }
.joli-btn-modal-primary.warning { background: var(--status-warning); }
.joli-btn-modal-primary.info    { background: var(--status-info); }
.joli-btn-modal-primary.primary { background: var(--brand-primary); }
.joli-btn-modal-primary.success { background: var(--status-success); }
/* Pendiente de paleta: texto blanco sobre --status-warning / --brand-primary no alcanza 4.5:1.
   Se propone un token --text-on-status (texto oscuro) en variables.css. */

.joli-btn-modal-primary:disabled,
.joli-btn-modal-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.joli-spin {
  animation: joliSpin 1s linear infinite;
}

@keyframes joliSpin {
  to { transform: rotate(360deg); }
}

.joli-modal-fade-in {
  animation: joliModalZoom 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes joliModalZoom {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@media (prefers-reduced-motion: reduce) {
  .joli-modal-fade-in,
  .joli-spin { animation: none; }
}
```
