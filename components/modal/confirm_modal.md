# Componente UI: Modal de Confirmación Corporativo (Confirm Modal)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)
### Patrón Canónico de Referencia: Módulo BI / UI

El **Confirm Modal** es el estándar obligatorio para reemplazar todas las llamadas a las funciones nativas del navegador (`window.confirm()` o `window.alert()`). 

Provee un diálogo modal seguro, accesible, enfocado en el usuario y con soporte para **estados de carga asíncrona (`isLoading`)**, inversión de peso visual para acciones destructivas (`emphasizeCancel`) e iconos cromáticos enmarcados con halo.

---

## 1. Regla Inflexible de Usabilidad y Seguridad

> **PROHIBIDO EL USO DE `window.confirm()` O `window.alert()`**:
> Los diálogos nativos del navegador bloquean el hilo principal de JavaScript, no respetan el tema Modo Noche/Día y ofrecen una experiencia de usuario deficiente.
> **Toda acción destructiva, cierre de sesión, eliminación de registros o confirmación de cambios sensibles debe invocar obligatoriamente a `ConfirmModal`**.

---

## 2. Código JSX / React 19 Canónico (`ConfirmModal.tsx`)

```tsx
import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { 
  AlertTriangle, 
  X, 
  Loader2, 
  Info, 
  CheckCircle2, 
  AlertOctagon 
} from 'lucide-react';
import '../../styles/variables.css';

export interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (justification?: string) => void | Promise<void>;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'danger' | 'warning' | 'info' | 'primary' | 'success';
  isLoading?: boolean;
  /** Invierte el peso visual: Cancelar resalta (color + foco), Confirmar queda neutro.
   *  Evita clics accidentales por hábito en acciones destructivas. */
  emphasizeCancel?: boolean;
  /** Habilita el campo obligatorio de justificación para trazabilidad y auditoría */
  requiresJustification?: boolean;
  /** Cantidad mínima de caracteres exigida para habilitar la confirmación (por defecto 10) */
  justificationMinLength?: number;
  justificationLabel?: string;
  justificationPlaceholder?: string;
  zIndex?: number;
}

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
  justificationLabel = 'Motivo o Justificación Obligatoria',
  justificationPlaceholder = 'Escriba detalladamente el motivo de esta acción...',
  zIndex = 100005
}) => {
  const [justification, setJustification] = React.useState('');
  const cancelBtnRef = useRef<HTMLButtonElement>(null);

  // Reiniciar justificación al abrir o cerrar
  useEffect(() => {
    if (!isOpen) setJustification('');
  }, [isOpen]);

  // Cerrar con Escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !isLoading) onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleEscape);
    }
    return () => {
      window.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose, isLoading]);

  // Si se resalta Cancelar, recibe el foco por defecto (Enter accidental no dispara la acción)
  useEffect(() => {
    if (isOpen && emphasizeCancel) cancelBtnRef.current?.focus();
  }, [isOpen, emphasizeCancel]);

  if (!isOpen) return null;

  const currentLength = justification.trim().length;
  const isJustificationValid = !requiresJustification || currentLength >= justificationMinLength;

  const cancelClassName = emphasizeCancel ? `joli-btn-modal-primary ${type}` : 'joli-btn-modal-secondary';
  const confirmClassName = emphasizeCancel ? 'joli-btn-modal-secondary' : `joli-btn-modal-primary ${type}`;

  const renderIcon = () => {
    switch (type) {
      case 'danger':
        return <AlertOctagon size={36} />;
      case 'warning':
        return <AlertTriangle size={36} />;
      case 'info':
        return <Info size={36} />;
      case 'success':
        return <CheckCircle2 size={36} />;
      default:
        return <AlertTriangle size={36} />;
    }
  };

  const handleConfirmClick = () => {
    if (!isJustificationValid || isLoading) return;
    onConfirm(requiresJustification ? justification.trim() : undefined);
  };

  return createPortal(
    <div className="joli-modal-overlay" style={{ zIndex }}>
      <div className="joli-confirm-modal-container joli-modal-fade-in" role="dialog" aria-modal="true">
        {/* BOTÓN X SUPERIOR */}
        <button 
          type="button" 
          className="joli-modal-close-icon" 
          onClick={onClose} 
          disabled={isLoading}
          aria-label="Cerrar modal"
        >
          <X size={20} />
        </button>

        {/* ÍCONO CON WRAPPER DE COLOR */}
        <div className={`joli-modal-icon-wrapper ${type}`}>
          {renderIcon()}
        </div>

        {/* CONTENIDO TEXTUAL */}
        <div className="joli-confirm-modal-content">
          <h3 className="joli-confirm-modal-title">{title}</h3>
          <p className="joli-confirm-modal-message">{message}</p>
        </div>

        {/* CAMPO DE JUSTIFICACIÓN DE AUDITORÍA (OBLIGATORIO) */}
        {requiresJustification && (
          <div className="joli-modal-justification-box">
            <label className="joli-modal-justification-label">
              <span>{justificationLabel}</span>
              <span className={`joli-modal-justification-counter ${isJustificationValid ? 'is-valid' : ''}`}>
                {currentLength} / {justificationMinLength} mín.
              </span>
            </label>
            <textarea
              className="joli-modal-textarea"
              placeholder={justificationPlaceholder}
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              disabled={isLoading}
              rows={3}
            />
          </div>
        )}

        {/* ACCIONES (BOTONES) */}
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
            title={!isJustificationValid ? `Debe ingresar al menos ${justificationMinLength} caracteres de motivo` : undefined}
          >
            {isLoading ? (
              <>
                <Loader2 size={16} className="joli-spin me-2" />
                <span>Procesando...</span>
              </>
            ) : (
              confirmText
            )}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
};
```

---

## 3. Estilos CSS Canónicos (`variables.css`)

```css
.joli-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.72);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100005;
}

.joli-confirm-modal-container {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  padding: 2.25rem;
  width: 90%;
  max-width: 460px;
  position: relative;
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.joli-modal-close-icon {
  position: absolute;
  top: 1.25rem;
  right: 1.25rem;
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: color var(--transition-fast);
}

.joli-modal-close-icon:hover {
  color: var(--color-text-primary);
}

.joli-modal-icon-wrapper {
  width: 76px;
  height: 76px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
}

.joli-modal-icon-wrapper.danger {
  background: rgba(239, 68, 68, 0.12);
  color: var(--color-danger);
  border: 1px solid rgba(239, 68, 68, 0.25);
}

.joli-modal-icon-wrapper.warning {
  background: rgba(245, 158, 11, 0.12);
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.joli-modal-icon-wrapper.info {
  background: rgba(14, 165, 233, 0.12);
  color: #0ea5e9;
  border: 1px solid rgba(14, 165, 233, 0.25);
}

.joli-modal-icon-wrapper.primary {
  background: rgba(16, 185, 129, 0.12);
  color: var(--color-primary);
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.joli-modal-icon-wrapper.success {
  background: rgba(34, 197, 94, 0.12);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.25);
}

.joli-confirm-modal-content {
  margin-bottom: 1.75rem;
}

.joli-confirm-modal-title {
  font-size: var(--text-xl);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.joli-confirm-modal-message {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: 1.6;
  max-height: 220px;
  overflow-y: auto;
  padding-right: 4px;
}

/* ==========================================================================
   CAMPO DE JUSTIFICACIÓN DE AUDITORÍA (OBLIGATORIO PARA ACCIONES DELICADAS)
   Garantiza ancho al 100%, textarea estilizado con tokens y contador en vivo
   ========================================================================== */
.joli-modal-justification-box {
  width: 100%;
  margin: 0.5rem 0 1.5rem 0;
  text-align: left;
  box-sizing: border-box;
}

.joli-modal-justification-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-secondary, #94a3b8);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.4rem;
  user-select: none;
}

.joli-modal-justification-counter {
  font-size: 0.7rem;
  font-family: var(--font-family-mono, monospace);
  color: var(--text-muted, #64748b);
  transition: color 0.2s ease;
}

.joli-modal-justification-counter.is-valid {
  color: var(--status-success, #10b981);
  font-weight: 700;
}

.joli-modal-textarea {
  width: 100%;
  box-sizing: border-box;
  min-height: 84px;
  max-height: 160px;
  background: var(--input-bg, var(--bg-card, #151928));
  border: 1px solid var(--input-border, var(--border-subtle, rgba(255, 255, 255, 0.1)));
  border-radius: var(--radius-md, 8px);
  padding: 0.65rem 0.85rem;
  font-family: inherit;
  font-size: 0.84rem;
  color: var(--input-text, var(--text-primary, #f8fafc));
  line-height: 1.45;
  resize: vertical;
  outline: none !important;
  transition: border-color var(--transition-fast, 150ms ease), box-shadow var(--transition-fast, 150ms ease);
}

.joli-modal-textarea:focus {
  border-color: var(--brand-primary, #6366f1);
  box-shadow: 0 0 0 3px var(--input-focus-ring, rgba(16, 185, 129, 0.25));
}

.joli-modal-textarea::placeholder {
  color: var(--input-placeholder, var(--text-muted, #64748b));
  opacity: 0.75;
}

.joli-modal-textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.joli-confirm-modal-actions {
  display: flex;
  gap: var(--space-3);
  width: 100%;
}

.joli-btn-modal-secondary {
  flex: 1;
  background: var(--color-bg-input);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-lg);
  font-weight: var(--weight-semibold);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.joli-btn-modal-secondary:hover {
  background: var(--color-bg-card-hover);
  border-color: var(--color-text-muted);
}

.joli-btn-modal-primary {
  flex: 1;
  color: #ffffff;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-lg);
  font-weight: var(--weight-semibold);
  font-size: var(--text-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.joli-btn-modal-primary.danger {
  background: #ef4444;
  box-shadow: 0 4px 14px rgba(239, 68, 68, 0.35);
}

.joli-btn-modal-primary.danger:hover:not(:disabled) {
  background: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(239, 68, 68, 0.45);
}

.joli-btn-modal-primary.warning {
  background: #f59e0b;
  box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35);
}

.joli-btn-modal-primary.warning:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-1px);
}

.joli-btn-modal-primary.primary {
  background: var(--color-primary);
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
}

.joli-btn-modal-primary.primary:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
}

.joli-btn-modal-primary:disabled,
.joli-btn-modal-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.joli-spin {
  animation: joliSpin 1s linear infinite;
}

@keyframes joliSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.joli-modal-fade-in {
  animation: joliModalZoom 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes joliModalZoom {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```
