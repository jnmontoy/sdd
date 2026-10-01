# Especificación de Componente: Notificaciones Flotantes (Toast Notification)
## Ecosistema Jolifoods — Guía de Implementación SDD

El componente `ToastNotification` proporciona retroalimentación instantánea, no intrusiva y accesible tras acciones asíncronas (creación, edición, eliminación, sincronización y errores de red). Está alineado con la paleta de tokens Jolifoods y diseñado para integrarse con `sonner` o un despachador nativo React.

---

### 1. Requisitos de Negocio y UX
1. **No bloqueante**: No interrumpe la navegación ni el flujo del usuario.
2. **Auto-cierre inteligente**:
   - `success`: 3500 ms.
   - `info`: 4000 ms.
   - `warning`: 5000 ms.
   - `error`: Persistente con botón de cierre manual (o 7000 ms) para permitir lectura de detalles.
3. **Acción opcional (Undo / Reintentar)**: Permite deshacer operaciones reversibles o reintentar peticiones fallidas.
4. **Posicionamiento**: Esquina inferior derecha (`bottom-right`) en escritorio, superior central (`top-center`) en móviles.
5. **Cero `alert()` nativo**: Está estrictamente prohibido utilizar funciones de alerta nativas del navegador.

---

### 2. Implementación TypeScript / React

```tsx
// src/components/ui/ToastNotification.tsx
import React from 'react';
import { toast, Toaster } from 'sonner';
import { CheckCircle2, AlertTriangle, AlertCircle, Info, X } from 'lucide-react';

export interface ToastOptions {
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  duration?: number;
}

export const showToast = {
  success: (title: string, options?: ToastOptions) => {
    toast.custom((t) => (
      <div className="joli-toast toast-success" role="status" aria-live="polite">
        <div className="toast-icon-box">
          <CheckCircle2 size={18} className="toast-icon" />
        </div>
        <div className="toast-content">
          <div className="toast-title">{title}</div>
          {options?.description && <div className="toast-desc">{options.description}</div>}
        </div>
        {options?.actionLabel && options?.onAction && (
          <button
            className="toast-action-btn"
            onClick={() => {
              options.onAction?.();
              toast.dismiss(t);
            }}
          >
            {options.actionLabel}
          </button>
        )}
        <button className="toast-close-btn" onClick={() => toast.dismiss(t)} aria-label="Cerrar">
          <X size={14} />
        </button>
      </div>
    ), { duration: options?.duration || 3500 });
  },

  error: (title: string, options?: ToastOptions) => {
    toast.custom((t) => (
      <div className="joli-toast toast-error" role="alert" aria-live="assertive">
        <div className="toast-icon-box">
          <AlertCircle size={18} className="toast-icon" />
        </div>
        <div className="toast-content">
          <div className="toast-title">{title}</div>
          {options?.description && <div className="toast-desc">{options.description}</div>}
        </div>
        {options?.actionLabel && options?.onAction && (
          <button
            className="toast-action-btn"
            onClick={() => {
              options.onAction?.();
              toast.dismiss(t);
            }}
          >
            {options.actionLabel}
          </button>
        )}
        <button className="toast-close-btn" onClick={() => toast.dismiss(t)} aria-label="Cerrar">
          <X size={14} />
        </button>
      </div>
    ), { duration: options?.duration || 7000 });
  },

  warning: (title: string, options?: ToastOptions) => {
    toast.custom((t) => (
      <div className="joli-toast toast-warning" role="status" aria-live="polite">
        <div className="toast-icon-box">
          <AlertTriangle size={18} className="toast-icon" />
        </div>
        <div className="toast-content">
          <div className="toast-title">{title}</div>
          {options?.description && <div className="toast-desc">{options.description}</div>}
        </div>
        <button className="toast-close-btn" onClick={() => toast.dismiss(t)} aria-label="Cerrar">
          <X size={14} />
        </button>
      </div>
    ), { duration: options?.duration || 5000 });
  },

  info: (title: string, options?: ToastOptions) => {
    toast.custom((t) => (
      <div className="joli-toast toast-info" role="status" aria-live="polite">
        <div className="toast-icon-box">
          <Info size={18} className="toast-icon" />
        </div>
        <div className="toast-content">
          <div className="toast-title">{title}</div>
          {options?.description && <div className="toast-desc">{options.description}</div>}
        </div>
        <button className="toast-close-btn" onClick={() => toast.dismiss(t)} aria-label="Cerrar">
          <X size={14} />
        </button>
      </div>
    ), { duration: options?.duration || 4000 });
  }
};

export const CorporateToaster: React.FC = () => {
  return (
    <Toaster
      position="bottom-right"
      toastOptions={{
        unstyled: true,
        className: 'joli-toaster-container',
      }}
    />
  );
};
```

---

### 3. Estilos CSS (`toast.css`)

```css
.joli-toast {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-width: 320px;
  max-width: 440px;
  padding: 12px 16px;
  border-radius: var(--radius-md, 8px);
  background: var(--bg-surface, #FFFFFF);
  border: 1px solid var(--border-default, #E5E7EB);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.12), 0 8px 10px -6px rgba(0, 0, 0, 0.08);
  font-family: inherit;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  animation: toastSlideIn 0.25s ease-out;
}

[data-theme="dark"] .joli-toast {
  background: var(--bg-surface, #1E293B);
  border-color: var(--border-default, #334155);
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.toast-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 1px;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-primary, #111827);
  line-height: 1.35;
}

.toast-desc {
  font-size: 12px;
  color: var(--text-secondary, #6B7280);
  margin-top: 2px;
  line-height: 1.4;
  word-break: break-word;
}

.toast-action-btn {
  background: transparent;
  border: none;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-primary, #2D6A4F);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.15s;
}

.toast-action-btn:hover {
  background: rgba(45, 106, 79, 0.08);
}

.toast-close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted, #9CA3AF);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-close-btn:hover {
  color: var(--text-primary, #111827);
  background: rgba(0, 0, 0, 0.05);
}

/* Variantes Cromáticas */
.toast-success {
  border-left: 4px solid var(--color-primary, #2D6A4F);
}
.toast-success .toast-icon-box {
  background: #E8F5E9;
  color: #2D6A4F;
}

.toast-error {
  border-left: 4px solid var(--color-danger, #C53030);
}
.toast-error .toast-icon-box {
  background: #FEE2E2;
  color: #DC2626;
}

.toast-warning {
  border-left: 4px solid #D97706;
}
.toast-warning .toast-icon-box {
  background: #FEF3C7;
  color: #D97706;
}

.toast-info {
  border-left: 4px solid #2563EB;
}
.toast-info .toast-icon-box {
  background: #EFF6FF;
  color: #2563EB;
}
```
