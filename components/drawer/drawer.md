# Especificación de Componente: Panel Lateral Derecho (`Drawer` / Slide-Over)
## Guía de implementación SDD

### Regla de uso: CRUD en el panel lateral derecho

- **Regla:** los formularios de creación (`+ Nuevo`) y edición (`Editar`) de registros CRUD DEBERÍAN abrirse en este panel lateral derecho, no en modales centrados ni en páginas separadas (`/crear`, `/editar/:id`).
- **Por qué:** el usuario conserva a la vista la tabla de contexto, el formulario tiene scroll propio y la experiencia es igual en todos los módulos.
- **Excepciones:** pedido explícito del usuario o decisión registrada (ADR). Los modales se reservan para confirmaciones, firmas, escáneres y sesión expirada (ver [`modal_dialog.md`](../modal/modal_dialog.md)).

---

### 1. Requisitos y estructura visual

1. **Animación:** entra desde el borde derecho (`translateX(100%)` → `translateX(0)`); se desactiva con `prefers-reduced-motion`.
2. **Anchos:** `sm` = 420px (máx. 92vw, detalle breve), `md` = **580px** (máx. 94vw, estándar), `lg` = **820px** (máx. 96vw, formularios extensos o con historial). El usuario los puede **redimensionar y expandir** (§1.1).
3. **Fondo y cierre:** fondo difuminado (`.joli-drawer-overlay`); se cierra con clic en el fondo, con `Escape` o con el botón de la cabecera.
4. **Accesibilidad:** `role="dialog"`, `aria-modal="true"`, `aria-labelledby` al título, foco atrapado y devuelto al disparador (hook `useModalA11y` de [`modal_dialog.md`](../modal/modal_dialog.md) §2). Un `ConfirmModal` abierto encima toma el control del teclado. Mientras está abierto, `body` lleva `overflow: hidden`. *(Deuda en la referencia: el `RightDrawer` de Pandora usa `aria-label` en vez de `aria-labelledby` y aún no atrapa ni devuelve el foco.)*
5. **Cabecera fija** con título, subtítulo, `badge` opcional junto al título (p. ej. el `status-pill` del registro al editar) y botón de cierre (`X` 18 px, «Cerrar panel lateral», `title` «Cerrar (Esc)»; bloqueado mientras se guarda); **cuerpo** con scroll vertical independiente (`.drawer-body`); **pie fijo** con «Cancelar» (`modal-btn-cancel`) y el botón principal (`modal-btn-save`, `type="submit"` con `form="{id}"`) con texto contextual («Guardar cambios» al editar, «Crear colaborador» al crear; mientras guarda, `Loader2` girando + «Guardando...»), no genérico.
6. **Cambios sin guardar:** si `isDirty` es verdadero, cerrar (fondo, Escape o X) DEBERÍA pedir confirmación con `ConfirmModal` antes de descartar. *(Deuda en la referencia: Usuarios aún no lo hace.)*
7. **Controles de formulario:** usar las clases `.drawer-form-field`, `.drawer-input-control` y `.drawer-field-input` definidas en [`variables.css`](../variables.css) §4; no se redefinen aquí. En formularios de captura (crear o editar) cada campo DEBE usar la **etiqueta flotante** de [`form/floating_field.md`](../form/floating_field.md): la caja lleva `campo-flotante` y la `<label className="campo-flotante-label">` va dentro, después del control (§5.1). La etiqueta separada `.drawer-field-label` queda solo para bloques que no son un campo (p. ej. «Repetición», «Historial»).
8. **Opcional:** mini-KPIs del registro (`.drawer-kpi-grid`) al inicio del cuerpo (§1.2).
9. **Detalle de solo lectura (ficha):** cuando el panel muestra un registro sin editarlo, NO DEBERÍA usar inputs `readOnly` uno tras otro (se ve como un formulario deshabilitado y desordenado). Se agrupa en **secciones** con título e ícono (`FichaSeccion`: cabecera con ícono en color de marca, título y dato a la derecha, cuerpo en tarjeta) y los datos en **lista etiqueta → valor de dos columnas** (`<dl>`, `FichaDatos`; en pantallas angostas, una debajo de la otra). Orden: mini-KPIs → secciones de lo más usado a lo menos usado → datos técnicos (códigos internos, fecha de actualización) en letra pequeña al final. Los valores vacíos se muestran como «—». Referencia: ficha de cliente del panel de Pandora (`ClienteDrawer.tsx`).

---

### 1.1. Redimensionar y expandir (`RightDrawer`)

Implementación de referencia: `frontend-admin/src/components/ui/RightDrawer.tsx` + `styles/drawer.css` (Pandora). Props: `isOpen, onClose, title, subtitle?, size: 'sm' | 'md' | 'lg' = 'md', badge?: ReactNode, children, footer`.

```text
portal a <body>
└─ div.joli-drawer-overlay  (role="dialog", aria-modal; clic cierra; fondo slate-950 al 62 % + blur 5px; z-index 2500)
   └─ div.joli-drawer-shell (animación drawerSlideIn .26s)
      ├─ button.drawer-expand-toggle   (círculo de 28 px en left:-14px, borde de marca 2 px)
      ├─ div.drawer-resizer-handle     (role="separator" aria-orientation="vertical")
      └─ aside.joli-drawer-container.size-{size}[.is-resizing]
         ├─ header.drawer-header > .drawer-title-group > .drawer-title-row (h2.drawer-title + badge) + p.drawer-subtitle ; button.drawer-close-btn
         ├─ div.drawer-body
         └─ footer.drawer-footer
```

- **Redimensionar:** arrastrar el borde izquierdo. Mínimo 360 px; máximo = ancho de la ventana menos el borde derecho del menú lateral (`.joli-sidebar`), recalculado con `ResizeObserver` y `resize`. Mientras se arrastra: `cursor: col-resize` y `user-select: none` en `body`. Se guarda **al soltar** en `localStorage['<app>_drawer_ancho_{size}']` con `try/catch`; doble clic restablece y borra la clave.
- **Expandir:** el botón circular lleva el panel hasta el borde del menú lateral y vuelve («Expandir panel lateral» / «Contraer panel lateral», `ChevronLeft` / `ChevronRight`, `title` «Expandir hasta el menú lateral»). Su `top` sigue la altura de la cabecera (`altoHeader − 14`).
- El ancho anima con `transition: width .25s`. En ≤768 px se ocultan el redimensionador y el botón de expandir.
- Todo panel lateral derecho del panel administrativo DEBERÍA usar este componente (no paneles propios).

### 1.2. Patrones del formulario de crear/editar

Referencia: `UserFormDrawer.tsx` + `useFormularioUsuario.ts` (Pandora).

- **Mini-KPIs (solo al editar):** `div.drawer-kpi-grid` (3 columnas fijas, `gap: .65rem`; 1 columna en ≤640 px) con `div.drawer-kpi-card` (`bg-input`, `border-left: 3px` de marca) > `span.drawer-kpi-label` (0.65rem, mayúsculas) + `strong.drawer-kpi-value`. Ej.: Documento (`mono-badge`), Rol actual, Último acceso.
- **Foto de perfil:** caja `div.drawer-avatar-upload-box` (borde punteado) con `button.drawer-avatar-preview` (64 px redondo, foto o iniciales, insignia de cámara), `input type="file" hidden accept="image/png,image/jpeg,image/webp,image/gif"`, la pista «PNG, JPG, WEBP o GIF (Máx. 5 MB)» o «Seleccionado: {archivo}», y los botones «Subir foto» / «Cambiar foto» y «Descartar» (solo con archivo nuevo). Validación de formato y tamaño con toast; vista previa con `createObjectURL`. La foto se sube **después** de guardar los datos; si falla, aviso «Datos guardados sin foto» y el panel se cierra igual.
- **Rejilla del formulario:** `form#{id}.drawer-form-grid` (2 columnas, `gap: 1rem`; 1 columna en ≤640 px). Campos con etiqueta flotante ([`floating_field.md`](../form/floating_field.md) §5.1). La llave primaria (p. ej. documento) queda deshabilitada al editar con la pista `p.drawer-field-hint` «Llave primaria: no se puede modificar».
- **Campo con botón pegado** (`div.drawer-input-group`): el campo (`has-icon has-suffix`) y un `button.drawer-input-addon` de 42 px unido a la derecha (`margin-left: -1px`, radio solo a la derecha; el campo pierde su radio derecho). El botón es un interruptor de ícono con `aria-pressed` y un `aria-label` que dice su estado; `.is-on` en color de marca con fondo `color-mix` 14 %. La explicación va en `title` y en una pista debajo. Ej.: contraseña + llave «Requiere cambio de contraseña» (deshabilitado al crear, porque siempre aplica, y en la propia cuenta).
- **Campo de solo lectura dentro del formulario:** mantiene la etiqueta flotante para no romper la rejilla ([`floating_field.md`](../form/floating_field.md) §1). `input.drawer-field-readonly readOnly tabIndex={-1} aria-readonly="true"`, candado `span.drawer-input-toggle-btn.drawer-input-lock` (`Lock` 14, `aria-hidden`) y `title` con la razón («Solo lo acepta el propio usuario»). Debajo, una línea de estado `p.drawer-agreement-status.is-{neutral|accepted|pending}`.
- **Validación:** errores en línea con `aria-invalid` (normativa 6.7). *(Deuda en la referencia: Usuarios valida a mano y avisa con toasts.)*
- **Al abrir:** la contraseña vuelve a quedar oculta y el formulario se llena con el registro o con los valores por defecto (p. ej. rol ATC al crear).

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
      <button type="button" className="modal-btn-cancel" onClick={close}>Cancelar</button>
      <button type="submit" form="form-usuario" className="modal-btn-save" disabled={isSaving}>
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

.joli-drawer-container.size-sm { width: 420px; max-width: 92vw; }
.joli-drawer-container.size-md { width: 580px; max-width: 94vw; }
.joli-drawer-container.size-lg { width: 820px; max-width: 96vw; }

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
