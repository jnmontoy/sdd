# Especificación de Componente: Panel Lateral Derecho (`Drawer` / Slide-Over)
## Guía de implementación SDD

### Regla de uso: CRUD en el panel lateral derecho

- **Regla:** los formularios de creación (`+ Nuevo`) y edición (`Editar`) de registros CRUD DEBERÍAN abrirse en este panel lateral derecho, no en modales centrados ni en páginas separadas (`/crear`, `/editar/:id`).
- **Por qué:** el usuario conserva a la vista la tabla de contexto, el formulario tiene scroll propio y la experiencia es igual en todos los módulos.
- **Excepciones:** pedido explícito del usuario o decisión registrada (ADR). Los modales se reservan para confirmaciones, firmas, escáneres y sesión expirada (ver [`modal_dialog.md`](../modal/modal_dialog.md)).

---

### 1. Requisitos y estructura visual

1. **Animación:** entra desde el borde derecho (`translateX(100%)` → `translateX(0)`); se desactiva con `prefers-reduced-motion`.
2. **Anchos:** `md` = **560px** (estándar), `lg` = **720px** (formularios extensos), `sm` = 400px (detalle breve). En pantallas angostas, hasta 100% del ancho.
3. **Fondo y cierre:** fondo difuminado (`.joli-drawer-overlay`); se cierra con clic en el fondo, con `Escape` o con el botón de la cabecera.
4. **Accesibilidad:** `role="dialog"`, `aria-modal="true"`, `aria-labelledby` al título, foco atrapado y devuelto al disparador (hook `useModalA11y` de [`modal_dialog.md`](../modal/modal_dialog.md) §2). Un `ConfirmModal` abierto encima toma el control del teclado.
5. **Cabecera fija** con título, subtítulo/badge y botón de cierre; **cuerpo** con scroll vertical independiente (`.drawer-body`); **pie fijo** con "Cancelar" y el botón principal con texto contextual ("Guardar usuario", "Crear proveedor"), no genérico.
6. **Cambios sin guardar:** si `isDirty` es verdadero, cerrar (fondo, Escape o X) DEBERÍA pedir confirmación con `ConfirmModal` antes de descartar.
7. **Controles de formulario:** usar las clases `.drawer-form-field`, `.drawer-input-control` y `.drawer-field-input` definidas en [`variables.css`](../variables.css) §4; no se redefinen aquí. En formularios de captura (crear o editar) cada campo DEBE usar la **etiqueta flotante** de [`form/floating_field.md`](../form/floating_field.md): la caja lleva `campo-flotante` y la `<label className="campo-flotante-label">` va dentro, después del control (§5.1). La etiqueta separada `.drawer-field-label` queda solo para bloques que no son un campo (p. ej. «Repetición», «Historial»).
8. **Opcional:** mini-KPIs del registro (`.drawer-kpi-grid`) al inicio del cuerpo.
9. **Detalle de solo lectura (ficha):** cuando el panel muestra un registro sin editarlo, NO DEBERÍA usar inputs `readOnly` uno tras otro (se ve como un formulario deshabilitado y desordenado). Se agrupa en **secciones** con título e ícono (`FichaSeccion`: cabecera con ícono en color de marca, título y dato a la derecha, cuerpo en tarjeta) y los datos en **lista etiqueta → valor de dos columnas** (`<dl>`, `FichaDatos`; en pantallas angostas, una debajo de la otra). Orden: mini-KPIs → secciones de lo más usado a lo menos usado → datos técnicos (códigos internos, fecha de actualización) en letra pequeña al final. Los valores vacíos se muestran como «—». Referencia: ficha de cliente del panel de Pandora (`ClienteDrawer.tsx`).

---

### 2. Implementación TypeScript de referencia (`Drawer.tsx`)

```tsx
import React, { useCallback, useId, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { useModalA11y } from '../../hooks/useModalA11y';
import { ConfirmModal } from '../modal/ConfirmModal';

export interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  /** Si hay cambios sin guardar, se pide confirmación antes de cerrar. */
  isDirty?: boolean;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  size = 'md',
  isDirty = false,
  children,
  footer,
}) => {
  const panelRef = useRef<HTMLDivElement>(null);
  const titleId = useId();
  const [confirmDiscard, setConfirmDiscard] = useState(false);

  const requestClose = useCallback(() => {
    if (isDirty) setConfirmDiscard(true);
    else onClose();
  }, [isDirty, onClose]);

  useModalA11y(panelRef, { isOpen, onClose: requestClose });

  if (!isOpen) return null;

  return createPortal(
    <>
      <div
        className="joli-drawer-overlay"
        onMouseDown={(e) => {
          if (e.target === e.currentTarget) requestClose();
        }}
      >
        <div
          ref={panelRef}
          className={`joli-drawer-container size-${size}`}
          role="dialog"
          aria-modal="true"
          aria-labelledby={titleId}
          tabIndex={-1}
          data-testid="sidebar-drawer"
        >
          <div className="drawer-header">
            <div className="drawer-title-group">
              <h2 id={titleId} className="drawer-title">{title}</h2>
              {subtitle && <div className="drawer-subtitle">{subtitle}</div>}
            </div>
            <button type="button" className="drawer-close-btn" onClick={requestClose} aria-label="Cerrar panel">
              <X size={18} aria-hidden="true" />
            </button>
          </div>

          <div className="drawer-body">{children}</div>

          {footer && <div className="drawer-footer">{footer}</div>}
        </div>
      </div>

      <ConfirmModal
        isOpen={confirmDiscard}
        type="warning"
        title="Descartar cambios"
        message="Hay cambios sin guardar. ¿Desea cerrar el panel y descartarlos?"
        confirmText="Descartar"
        emphasizeCancel
        onClose={() => setConfirmDiscard(false)}
        onConfirm={() => {
          setConfirmDiscard(false);
          onClose();
        }}
      />
    </>,
    document.body,
  );
};
```

Ejemplo de pie con texto contextual:

```tsx
<Drawer
  isOpen={isOpen}
  onClose={close}
  title={editing ? 'Editar usuario' : 'Nuevo usuario'}
  isDirty={formState.isDirty}
  footer={
    <>
      <button type="button" className="joli-btn-secondary" onClick={close}>Cancelar</button>
      <button type="submit" form="form-usuario" className="joli-btn-primary" disabled={isSaving}>
        {editing ? 'Guardar usuario' : 'Crear usuario'}
      </button>
    </>
  }
>
  <form id="form-usuario" onSubmit={handleSubmit}>{/* campos .drawer-form-field */}</form>
</Drawer>
```

---

### 3. Estilos CSS (`drawer.css`)

```css
.joli-drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-drawer);
  display: flex;
  justify-content: flex-end;
  background-color: color-mix(in srgb, var(--bg-viewport) 60%, transparent);
  backdrop-filter: blur(4px);
  animation: drawerFadeIn 0.2s ease-out;
}

.joli-drawer-container {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--bg-card);
  color: var(--text-primary);
  border-left: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-modal);
  animation: drawerSlideIn var(--transition-base);
}

.joli-drawer-container:focus {
  outline: none;
}

.joli-drawer-container.size-sm { width: 400px; max-width: 100vw; }
.joli-drawer-container.size-md { width: 560px; max-width: 100vw; }
.joli-drawer-container.size-lg { width: 720px; max-width: 100vw; }

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-card);
}

.drawer-title {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.drawer-subtitle {
  margin: 2px 0 0;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.drawer-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.drawer-close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.drawer-close-btn:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 1px;
}

.drawer-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.drawer-kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
  margin-bottom: 18px;
}

.drawer-kpi-card {
  padding: 10px 12px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.drawer-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 14px 20px;
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-card);
}

@keyframes drawerFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes drawerSlideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

@media (prefers-reduced-motion: reduce) {
  .joli-drawer-overlay,
  .joli-drawer-container { animation: none; }
}
```
