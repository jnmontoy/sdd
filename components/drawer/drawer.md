# Especificación de Componente: Panel Deslizable Lateral Derecho (Right Drawer / Slide-Over)
## Ecosistema Jolifoods — Guía de Implementación SDD (Estándar Cartera)

> [!CAUTION]
> **REGLA DE ORO DE EXPERIENCIA DE USUARIO (UX) — JOLIFOODS**:
> **TODO FORMULARIO DE CREACIÓN O EDICIÓN CRUD DEBE ABRIRSE EN EL SIDEBAR DERECHO (RIGHT DRAWER)**.
> Queda **TERMINANTEMENTE PROHIBIDO** abrir formularios de captura o edición en modales flotantes centrados o redirigir a páginas separadas (`/crear`, `/editar`), a menos que la persona o el requerimiento lo pida específicamente.
> El Right Drawer (`.cartera-sidebar-drawer`) garantiza que el usuario nunca pierda el contexto visual de la tabla principal mientras crea o edita información.

---

### 1. Requisitos de Negocio y Estructura Visual
1. **Animación y Posición**: Deslizamiento suave desde el borde derecho mediante `transform: translateX(100%)` a `translateX(0)` con `cubic-bezier(0.16, 1, 0.3, 1)`.
2. **Backdrop Blur y Cierre por Teclado**: Fondo difuminado `backdrop-filter: blur(4px)` (`.cartera-sidebar-backdrop`) que se cierra con clic exterior o con la tecla `Escape (Esc)`.
3. **Botón de Cierre**: Botón cuadrado con flecha hacia la derecha (`<ChevronRight size={20} />`) ubicado en la cabecera.
4. **Mini-Kpis Contextuales**: Cabecera o cuerpo con mini rejilla de tarjetas (`.cartera-sidebar-kpi-grid` y `.cartera-sidebar-kpi-card`) con datos clave del registro seleccionado.
5. **Cuerpo Scrollable Independiente**: `.cartera-sidebar-body` con `overflow-y: auto`.
6. **Pie de Acción Fijo**: `.cartera-sidebar-footer` con botones de acción agrupados a la derecha ("Cancelar" y "Guardar / Confirmar").


---

### 2. Implementación TypeScript Canónica (`Drawer.tsx`)

```tsx
import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';

export interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  size = 'md',
  children,
  footer
}) => {
  // Cierre con la tecla Escape y bloqueo del scroll corporal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return createPortal(
    <div className="joli-drawer-overlay" onClick={onClose} aria-modal="true" role="dialog">
      <div 
        className={`joli-drawer-container size-${size}`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Cabecera del Drawer */}
        <div className="drawer-header">
          <div className="drawer-title-group">
            <h5 className="drawer-title">{title}</h5>
            {subtitle && <p className="drawer-subtitle">{subtitle}</p>}
          </div>
          <button 
            type="button" 
            className="drawer-close-btn" 
            onClick={onClose}
            aria-label="Cerrar panel"
          >
            <X size={18} />
          </button>
        </div>

        {/* Cuerpo del Drawer */}
        <div className="drawer-body">
          {children}
        </div>

        {/* Pie del Drawer */}
        {footer && (
          <div className="drawer-footer">
            {footer}
          </div>
        )}
      </div>
    </div>,
    document.body
  );
};
```

---

### 3. Estilos CSS (`drawer.css`)

```css
.joli-drawer-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(4px);
  z-index: 1050;
  display: flex;
  justify-content: flex-end;
  animation: drawerFadeIn 0.2s ease-out;
}

.joli-drawer-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--color-bg-card, #FFFFFF);
  color: var(--color-text-primary, #111827);
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.25);
  animation: drawerSlideIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
}

[data-theme="dark"] .joli-drawer-container {
  background-color: var(--color-bg-card, #1E293B);
  color: #F8FAFC;
  box-shadow: -10px 0 35px rgba(0, 0, 0, 0.6);
}

.joli-drawer-container.size-sm { width: 400px; max-width: 90vw; }
.joli-drawer-container.size-md { width: 600px; max-width: 92vw; }
.joli-drawer-container.size-lg { width: 840px; max-width: 95vw; }

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 22px;
  border-bottom: 1px solid var(--color-border, #E5E7EB);
  background: var(--bg-surface, #FFFFFF);
}

[data-theme="dark"] .drawer-header {
  background: var(--bg-surface, #1E293B);
  border-bottom-color: var(--color-border, #334155);
}

.drawer-title-group .drawer-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: var(--color-text-primary, #111827);
}

[data-theme="dark"] .drawer-title-group .drawer-title {
  color: #F8FAFC;
}

.drawer-title-group .drawer-subtitle {
  font-size: 12.5px;
  color: var(--color-text-secondary, #6B7280);
  margin: 2px 0 0 0;
}

.drawer-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--color-text-muted, #9CA3AF);
  cursor: pointer;
  transition: all 0.15s;
}

.drawer-close-btn:hover {
  background: rgba(0, 0, 0, 0.06);
  color: var(--color-text-primary, #111827);
}

[data-theme="dark"] .drawer-close-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #FFFFFF;
}

.drawer-body {
  flex: 1;
  padding: 22px;
  overflow-y: auto;
}

/* ==========================================================================
   ESTRUCTURA DE CONTROLES DE FORMULARIO DENTRO DEL DRAWER (OBLIGATORIA)
   Prohibido usar inputs nativos sin estilizar
   ========================================================================== */
.drawer-form-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 1.15rem;
  width: 100%;
}

.drawer-field-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-secondary, #94a3b8);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  user-select: none;
  margin-bottom: 0.25rem;
}

.drawer-input-control {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--bg-card, #0f172a);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  border-radius: var(--radius-md, 8px);
  min-height: 38px;
  width: 100%;
  box-sizing: border-box;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-input-control:hover:not(:focus-within) {
  border-color: rgba(99, 102, 241, 0.35);
}

.drawer-input-control:focus-within {
  border-color: var(--brand-primary, #6366f1);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2), 0 2px 8px rgba(0, 0, 0, 0.15);
}

.drawer-field-input {
  width: 100%;
  background: transparent !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  padding: 0.5rem 0.75rem;
  font-size: 0.84rem;
  color: var(--text-primary, #f8fafc) !important;
  font-family: inherit;
  box-sizing: border-box;
  height: 38px;
}

.drawer-input-control.has-icon .drawer-field-input {
  padding-left: 2.35rem;
}

.drawer-input-icon {
  position: absolute;
  left: 0.75rem;
  color: var(--text-muted, #64748b);
  pointer-events: none;
  flex-shrink: 0;
  transition: color 0.2s ease, transform 0.2s ease;
}

.drawer-input-control:focus-within .drawer-input-icon {
  color: var(--brand-primary, #6366f1);
  transform: scale(1.08);
}

.drawer-field-input::placeholder {
  color: var(--text-muted, #64748b);
  opacity: 0.75;
}

.drawer-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 22px;
  border-top: 1px solid var(--color-border, #E5E7EB);
  background: var(--bg-surface, #FFFFFF);
}

[data-theme="dark"] .drawer-footer {
  background: var(--bg-surface, #1E293B);
  border-top-color: var(--color-border, #334155);
}

/* 
 * REGLA DE TEXTO EN EL BOTÓN PRINCIPAL DEL FOOTER:
 * El botón debe llevar el texto contextual correspondiente a la entidad (ej. "Guardar Registro", "Guardar Partido", "Crear Usuario").
 * Queda PROHIBIDO dejar textos incongruentes fijos como "Guardar Notas".
 */

@keyframes drawerFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes drawerSlideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
```
