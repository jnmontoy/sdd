# Componente UI: Diálogo Modal Accesible (Modal Dialog)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

El **Modal Dialog** es el componente estándar para confirmaciones de acción crítica (eliminaciones, aprobación de cambios), formularios emergentes (creación y edición rápida) y alertas del sistema.

Diseñado con accesibilidad **WCAG 2.1 AA** (atrapamiento de foco, cierre con tecla `Escape`, bloqueo de scroll de fondo) y estética *Glassmorphism* sincronizada con [`variables.css`](../variables.css).

> [!IMPORTANT]
> **RESTRICCIÓN DE USO — PROHIBIDO GENERAR FORMULARIOS CRUD EN MODALES**:
> Por directriz obligatoria de UX en Jolifoods, **la creación (`+ Nuevo`) y edición (`Editar`) de cualquier CRUD se realiza exclusivamente desde el Right Drawer lateral ([`drawer.md`](../drawer/drawer.md))**.
> Los modales quedan reservados para confirmaciones críticas ([`confirm_modal.md`](./confirm_modal.md)), firmas digitales ([`signature_modal.md`](../signature/signature_modal.md)), lectores biométricos o alertas de sesión, **y NUNCA para formularios de CRUD a menos que el usuario lo solicite específicamente**.

---

## 1. Variantes y Tamaños

| Variante | Ancho Máximo | Caso de Uso Típico |
| :--- | :--- | :--- |
| **`modal-sm`** | `400px` | Diálogo de confirmación ("¿Está seguro de eliminar?"). |
| **`modal-md`** | `560px` | Formularios estándar (Cambio de contraseña, creación de entidad simple). |
| **`modal-lg`** | `800px` | Formularios complejos con múltiples pestañas o visualizadores de detalle. |
| **`modal-xl`** | `1140px` | Visualización de reportes o comparativas de auditoría ANTES / DESPUÉS. |

---

## 2. Código JSX / React 19 Canónico (`Modal.tsx`)

```tsx
import React, { useEffect, useRef } from 'react';
import { X, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';
import '../../styles/variables.css';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'danger' | 'warning' | 'success';
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  size = 'md',
  variant = 'default',
  children,
  footer
}) => {
  const modalRef = useRef<HTMLDivElement>(null);

  // Cerrar con Escape y bloquear scroll del body
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };

    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const renderIcon = () => {
    switch (variant) {
      case 'danger':
        return <div className="joli-modal-icon danger"><AlertTriangle size={20} /></div>;
      case 'warning':
        return <div className="joli-modal-icon warning"><AlertTriangle size={20} /></div>;
      case 'success':
        return <div className="joli-modal-icon success"><CheckCircle2 size={20} /></div>;
      default:
        return null;
    }
  };

  return (
    <div className="joli-modal-backdrop" onClick={onClose} role="dialog" aria-modal="true">
      <div 
        className={`joli-modal-dialog joli-modal-${size}`} 
        onClick={(e) => e.stopPropagation()} 
        ref={modalRef}
      >
        {/* CABECERA */}
        <div className="joli-modal-header">
          <div className="d-flex align-items-center gap-3">
            {renderIcon()}
            <div>
              <h3 className="joli-modal-title">{title}</h3>
              {subtitle && <p className="joli-modal-subtitle">{subtitle}</p>}
            </div>
          </div>
          <button 
            type="button" 
            className="joli-modal-close" 
            onClick={onClose}
            aria-label="Cerrar modal"
          >
            <X size={18} />
          </button>
        </div>

        {/* CUERPO */}
        <div className="joli-modal-body">
          {children}
        </div>

        {/* PIE (ACCIONES) */}
        {footer && (
          <div className="joli-modal-footer">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};
```

---

## 3. Estilos CSS Canónicos (`variables.css`)

```css
.joli-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background-color: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  animation: joliModalFadeIn var(--transition-fast) ease-out;
}

.joli-modal-dialog {
  width: 100%;
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 40px);
  overflow: hidden;
  animation: joliModalSlideUp var(--transition-normal) cubic-bezier(0.16, 1, 0.3, 1);
}

.joli-modal-sm { max-width: 420px; }
.joli-modal-md { max-width: 580px; }
.joli-modal-lg { max-width: 840px; }
.joli-modal-xl { max-width: 1140px; }

.joli-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.joli-modal-title {
  font-size: var(--text-base);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.joli-modal-subtitle {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
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
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.joli-modal-close:hover {
  background-color: var(--color-bg-card-hover);
  color: var(--color-text-primary);
}

.joli-modal-body {
  padding: var(--space-5);
  overflow-y: auto;
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

.joli-modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-border);
  background-color: var(--color-bg-base);
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
  background-color: rgba(239, 68, 68, 0.15);
  color: var(--color-danger);
}

.joli-modal-icon.warning {
  background-color: rgba(245, 158, 11, 0.15);
  color: var(--color-warning);
}

.joli-modal-icon.success {
  background-color: rgba(16, 185, 129, 0.15);
  color: var(--color-primary);
}

@keyframes joliModalFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes joliModalSlideUp {
  from { transform: translateY(16px) scale(0.98); opacity: 0; }
  to { transform: translateY(0) scale(1); opacity: 1; }
}
```
