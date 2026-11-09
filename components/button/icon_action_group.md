# Especificación de Componente: Acciones Compactas Agrupadas (`IconActionGroup`)
## Guía de implementación SDD

Este documento define cuatro piezas de botones:
1. **Caja de acciones de tabla** (`.compact-action-box`): crear, exportar, refrescar.
2. **Acciones por fila** (`btn-group btn-group-sm row-actions-group`).
3. **Botones de formulario** (`.joli-btn-primary`, `.joli-btn-secondary`) usados en el pie del drawer y en estados vacíos.
4. **Selector de vista con búsqueda** (`.view-switcher`, §6).

---

## 0. Implementación de referencia (Pandora, módulo Usuarios)

> Patrón completo de la pantalla: [`admin_table_screen.md`](../data_table/admin_table_screen.md). Lo de esta sección manda sobre el resto del documento cuando se contradicen; lo marcado **«Deuda en la referencia»** es lo que el código aún no cumple y NO se copia.

- **Caja compacta** `div.compact-action-box role="toolbar"`: 36 px de alto (32 en móvil), `radius-md`, `bg-input`; botones `btn-icon-compact` de 36 px. Orden: crear (`btn-icon-add`, `UserPlus` 15, en `--brand-primary`) → acciones del módulo (`--text-secondary`, hover de marca) → `span.compact-divider` (18 px, `aria-hidden`) → recargar (`btn-icon-refresh`, `RotateCcw` 14 con `spin-antihorario` mientras carga). **Exportar no va en la caja:** es un botón con texto en la zona izquierda.
- **Botonera de los tres** (`.view-switcher`, vista tabla / tarjetas / buscar): 38 px de alto, botones de 32 px; la búsqueda se despliega hasta 340 px. Detalle en [`admin_table_screen.md`](../data_table/admin_table_screen.md) §2.1.
- **Acciones de fila** `div.row-actions-group role="group"`: 28 px de alto, botones `action-btn {map|edit|toggle danger|toggle success}` de 30 × 28 separados por `border-right` (no `btn-group btn-group-sm` ni `btn-row-*`). Detalle en §4.7 del patrón.
- **Deuda en la referencia:** los botones de vista no tienen `aria-pressed`, la búsqueda no tiene `aria-label` ni `type="search"`, y el botón recargar no se deshabilita ni lleva `aria-busy` mientras carga.

---

### Regla 1: acciones secundarias de tabla en caja compacta

- **Regla:** las acciones secundarias de una tabla (agregar, exportar a Excel, refrescar, limpiar filtros) DEBERÍAN presentarse como botones solo-ícono agrupados en una caja compacta de 26–28px de alto, con divisores y `aria-label` + `title` en cada botón.
- **Por qué:** ocupan poco espacio en la barra superior (que también aloja búsqueda y paginador) y se reconocen igual en todos los módulos.
- **Excepciones:** pantallas donde la acción principal necesita texto por claridad (p. ej. un asistente de primera vez) o decisión registrada (ADR).

### Regla 2: acciones de fila agrupadas

- **Regla:** si una fila tiene 2 o más botones de acción, DEBERÍAN agruparse en `<div class="btn-group btn-group-sm row-actions-group" role="group" aria-label="Acciones de fila">`, sin márgenes entre botones (`me-1`, `me-2`). Con más de 3 acciones, las secundarias van en un `dropdown-toggle` dentro del mismo grupo.
- **Por qué:** una sola zona de acción por fila, ancho constante de la columna y lectura más rápida.
- **Excepciones:** decisión registrada (ADR).

---

### 1. Caja de acciones de tabla (HTML para mocks)

```html
<div class="compact-action-box" role="toolbar" aria-label="Acciones de tabla">
  <button type="button" class="btn-icon-compact btn-icon-add" title="Nuevo registro (abre el panel lateral)" aria-label="Nuevo registro">
    <i data-lucide="plus" aria-hidden="true" style="width: 14px; height: 14px;"></i>
  </button>
  <span class="compact-divider" aria-hidden="true"></span>
  <button type="button" class="btn-icon-compact btn-icon-excel" title="Descargar en Excel (.xlsx)" aria-label="Descargar en Excel" data-testid="btn-export-excel">
    <i data-lucide="file-spreadsheet" aria-hidden="true" style="width: 14px; height: 14px;"></i>
  </button>
  <span class="compact-divider" aria-hidden="true"></span>
  <button type="button" class="btn-icon-compact btn-icon-refresh" title="Actualizar datos" aria-label="Actualizar datos">
    <i data-lucide="refresh-cw" aria-hidden="true" style="width: 13px; height: 13px;"></i>
  </button>
</div>
```

### 2. Componente React (`IconActionGroup.tsx`)

```tsx
import React from 'react';
import { FileSpreadsheet, Plus, RefreshCw } from 'lucide-react';

interface IconActionGroupProps {
  onAdd?: () => void;
  onExportExcel?: () => void;
  onRefresh?: () => void;
  isRefreshing?: boolean;
  isExporting?: boolean;
}

export const IconActionGroup: React.FC<IconActionGroupProps> = ({
  onAdd,
  onExportExcel,
  onRefresh,
  isRefreshing = false,
  isExporting = false,
}) => {
  const buttons: React.ReactNode[] = [];

  if (onAdd) {
    buttons.push(
      <button key="add" type="button" className="btn-icon-compact btn-icon-add" onClick={onAdd}
        title="Nuevo registro (abre el panel lateral)" aria-label="Nuevo registro">
        <Plus size={14} aria-hidden="true" />
      </button>,
    );
  }
  if (onExportExcel) {
    buttons.push(
      <button key="excel" type="button" className="btn-icon-compact btn-icon-excel" onClick={onExportExcel}
        disabled={isExporting} aria-busy={isExporting}
        title="Descargar en Excel (.xlsx)" aria-label="Descargar en Excel" data-testid="btn-export-excel">
        <FileSpreadsheet size={14} aria-hidden="true" />
      </button>,
    );
  }
  if (onRefresh) {
    buttons.push(
      <button key="refresh" type="button" className="btn-icon-compact btn-icon-refresh" onClick={onRefresh}
        disabled={isRefreshing} aria-busy={isRefreshing}
        title="Actualizar datos" aria-label="Actualizar datos">
        <RefreshCw size={13} className={isRefreshing ? 'joli-spin' : ''} aria-hidden="true" />
      </button>,
    );
  }

  return (
    <div className="compact-action-box" role="toolbar" aria-label="Acciones de tabla">
      {buttons.map((button, index) => (
        <React.Fragment key={index}>
          {index > 0 && <span className="compact-divider" aria-hidden="true" />}
          {button}
        </React.Fragment>
      ))}
    </div>
  );
};
```

### 3. Estilos de la caja de acciones

```css
.compact-action-box {
  display: inline-flex;
  align-items: center;
  height: 28px;
  overflow: hidden;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-card);
}

.btn-icon-compact {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.btn-icon-compact:hover:not(:disabled) {
  background: var(--bg-hover);
}

.btn-icon-compact:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: -2px;
}

.btn-icon-compact:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon-add { color: var(--status-info); }
.btn-icon-add:hover:not(:disabled) { background: var(--status-info-bg); }

.btn-icon-excel { color: var(--status-success); }
.btn-icon-excel:hover:not(:disabled) { background: var(--status-success-bg); }

.btn-icon-refresh { color: var(--text-muted); }
.btn-icon-refresh:hover:not(:disabled) { color: var(--text-primary); }

.compact-divider {
  width: 1px;
  height: 16px;
  background: var(--border-subtle);
}

.joli-spin {
  animation: joliSpin 1s linear infinite;
}

@keyframes joliSpin {
  to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
  .joli-spin { animation: none; }
}
```

---

### 4. Acciones por fila (`row-actions-group`)

#### 4.1. Con Bootstrap 5 (`btn-group btn-group-sm`)

```html
<div class="btn-group btn-group-sm row-actions-group" role="group" aria-label="Acciones de fila">
  <button type="button" class="btn btn-outline-secondary btn-row-view" title="Ver / editar en panel lateral" aria-label="Ver o editar registro" onclick="openDrawerForDetail(id)">
    <i data-lucide="eye" aria-hidden="true" style="width: 13px; height: 13px;"></i>
  </button>
  <button type="button" class="btn btn-outline-warning btn-row-key" title="Restablecer contraseña" aria-label="Restablecer contraseña" onclick="openResetPassword(id)">
    <i data-lucide="key-round" aria-hidden="true" style="width: 13px; height: 13px;"></i>
  </button>
  <button type="button" class="btn btn-outline-danger btn-row-delete" title="Desactivar registro" aria-label="Desactivar registro" onclick="openConfirmAction(id)">
    <i data-lucide="trash-2" aria-hidden="true" style="width: 13px; height: 13px;"></i>
  </button>
</div>
```

#### 4.2. Alternativa en CSS puro con divisores

```html
<div class="row-actions-group" role="group" aria-label="Acciones de fila">
  <button type="button" class="btn-row-action btn-row-view" title="Ver detalle en panel lateral" aria-label="Ver detalle" onclick="openDrawerForDetail(id)">
    <i data-lucide="eye" aria-hidden="true" style="width: 13px; height: 13px;"></i>
  </button>
  <span class="row-action-divider" aria-hidden="true"></span>
  <button type="button" class="btn-row-action btn-row-delete" title="Desactivar registro" aria-label="Desactivar registro" onclick="openConfirmAction(id)">
    <i data-lucide="trash-2" aria-hidden="true" style="width: 13px; height: 13px;"></i>
  </button>
</div>
```

#### 4.3. Estilos de fila

```css
.row-actions-group {
  display: inline-flex;
  align-items: center;
  height: 26px;
  overflow: hidden;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
}

/* Con Bootstrap: unificar altura y unir bordes de 1px */
.row-actions-group.btn-group > .btn {
  height: 26px;
  padding: 0 7px;
  display: inline-flex;
  align-items: center;
}

.btn-row-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 26px;
  padding: 0;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.btn-row-action:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-row-action:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: -2px;
}

.btn-row-view:hover {
  color: var(--status-info);
  background: var(--status-info-bg);
}

.btn-row-delete:hover {
  color: var(--status-error);
  background: var(--status-error-bg);
}

.row-action-divider {
  width: 1px;
  height: 14px;
  background: var(--border-subtle);
}
```

---

### 5. Botones de formulario (`.joli-btn-primary` / `.joli-btn-secondary`)

Usados en el pie del [`drawer`](../drawer/drawer.md), estados vacíos y barras de herramientas que requieren texto.

```css
.joli-btn-primary,
.joli-btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 34px;
  padding: 0 14px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color var(--transition-fast), border-color var(--transition-fast), color var(--transition-fast);
}

.joli-btn-primary {
  background: var(--brand-primary);
  border: 1px solid var(--brand-primary);
  color: var(--text-on-brand);
}

.joli-btn-primary:hover:not(:disabled) {
  background: var(--brand-primary-hover);
  border-color: var(--brand-primary-hover);
}

.joli-btn-secondary {
  background: var(--bg-btn-secondary);
  border: 1px solid var(--border-strong);
  color: var(--text-secondary);
}

.joli-btn-secondary:hover:not(:disabled) {
  background: var(--bg-btn-secondary-hover);
  color: var(--text-primary);
}

.joli-btn-primary:focus-visible,
.joli-btn-secondary:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 2px;
}

.joli-btn-primary:disabled,
.joli-btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
```

Variante compacta para barras de herramientas: añadir `height: 28px; font-size: var(--font-size-xs);`.

---

### 6. Variante: selector de vista con búsqueda (`.view-switcher`)

Para módulos que ofrecen la misma información como tabla o como tarjetas (p. ej. gestión de usuarios), los botones **Tabla** (`Table2`), **Tarjetas** (`LayoutGrid`) y **Buscar** (`Search`) DEBERÍAN agruparse en un bloque segmentado de solo íconos. Al pulsar Buscar, el campo de búsqueda se despliega horizontalmente dentro del mismo bloque y recibe el foco; `Escape` lo contrae.

- **Por qué:** la búsqueda queda junto al cambio de vista y no se mezcla con los filtros de selección ([`expandable_filter_group.md`](../dropdown/expandable_filter_group.md)).
- Los botones de vista usan `aria-pressed`; el campo de búsqueda lleva `aria-label`.

```html
<div class="view-switcher" role="group" aria-label="Vista y búsqueda">
  <button type="button" class="switcher-btn is-active" aria-pressed="true" title="Vista en tabla" aria-label="Vista en tabla">
    <i data-lucide="table-2" aria-hidden="true"></i>
  </button>
  <button type="button" class="switcher-btn" aria-pressed="false" title="Vista en tarjetas" aria-label="Vista en tarjetas">
    <i data-lucide="layout-grid" aria-hidden="true"></i>
  </button>
  <span class="switcher-divider" aria-hidden="true"></span>
  <div class="switcher-search-item" id="switcherSearch">
    <button type="button" class="switcher-btn" aria-expanded="false" aria-controls="switcherSearchBox"
            title="Buscar" aria-label="Buscar">
      <i data-lucide="search" aria-hidden="true"></i>
    </button>
    <div class="switcher-search-expanded" id="switcherSearchBox">
      <input type="search" class="switcher-search-input" aria-label="Buscar registros"
             placeholder="Buscar por documento, nombre o correo..." />
    </div>
  </div>
</div>
```

```css
.view-switcher {
  display: inline-flex;
  align-items: center;
  height: 28px;
  overflow: hidden;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
}

.switcher-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}

.switcher-btn:hover { background: var(--bg-hover); color: var(--text-primary); }
.switcher-btn.is-active { background: var(--status-success-bg); color: var(--text-primary); }
.switcher-btn:focus-visible { outline: 2px solid var(--border-focus); outline-offset: -2px; }

.switcher-divider { width: 1px; height: 16px; background: var(--border-subtle); }

.switcher-search-item { display: inline-flex; align-items: center; }

.switcher-search-expanded {
  max-width: 0;
  overflow: hidden;
  visibility: hidden;
  transition: max-width var(--transition-base), visibility 0s linear 0.25s;
}

.switcher-search-item.is-open .switcher-search-expanded {
  max-width: 320px;
  visibility: visible;
  transition: max-width var(--transition-base), visibility 0s;
}

.switcher-search-input {
  width: 280px;
  height: 24px;
  margin-right: 4px;
  padding: 0 8px;
  font-size: var(--font-size-xs);
  color: var(--input-text);
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: var(--radius-sm);
}

.switcher-search-input:focus { outline: none; border-color: var(--input-focus-border); box-shadow: var(--shadow-input-focus); }
```
