# Especificación de Componente: Caja de Acciones Compactas de Iconos Agrupados (`IconActionGroup`)
## Ecosistema Jolifoods — Guía de Implementación SDD

> **REGLA DE DISEÑO CORPORATIVO**:
> En los aplicativos oficiales de Jolifoods, las acciones secundarias de las tablas (Exportar a Excel, Refrescar datos, Agregar registro rápido, Limpiar filtros) **NO se presentan como botones grandes con texto plano suelto** (como "Exportar a Excel" o "+ Agregar").
> **DEBEN PRESENTARSE AGRUPADAS EN UNA CAJA COMPACTA DE ICONOS DE 26PX A 28PX DE ALTO** (`.compact-action-box` o `.actions-btn-group`), con fondo sutil, divisores verticales y tooltips descriptivos accesibles (`aria-label`).

---

### 1. Estructura Visual Canónica

```html
<div class="compact-action-box">
  <!-- 1. Acción Crear / Agregar (Icono Plus en Azul) -->
  <button type="button" class="btn-icon-compact btn-icon-add" title="Nuevo registro (Abrir panel lateral)" aria-label="Nuevo registro">
    <i data-lucide="plus" style="width: 14px; height: 14px;"></i>
  </button>

  <span class="compact-divider"></span>

  <!-- 2. Acción Exportar a Excel (Icono FileSpreadsheet en Verde #10b981) -->
  <button type="button" class="btn-icon-compact btn-icon-excel" title="Descargar datos en Excel (.xlsx)" aria-label="Descargar Excel">
    <i data-lucide="file-spreadsheet" style="width: 14px; height: 14px;"></i>
  </button>

  <span class="compact-divider"></span>

  <!-- 3. Acción Recargar / Refrescar (Icono RefreshCw en Gris) -->
  <button type="button" class="btn-icon-compact btn-icon-refresh" title="Actualizar datos de la tabla" aria-label="Actualizar datos">
    <i data-lucide="refresh-cw" style="width: 13px; height: 13px;"></i>
  </button>
</div>
```

---

### 2. Estilos CSS Requeridos

```css
.compact-action-box {
  display: inline-flex;
  align-items: center;
  height: 28px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm, 6px);
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.btn-icon-compact {
  height: 28px;
  width: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: background-color 150ms ease, color 150ms ease;
}

.btn-icon-compact:hover {
  background: var(--bg-hover);
}

.btn-icon-add { color: #3b82f6; }
.btn-icon-add:hover { color: #60a5fa; background: rgba(59, 130, 246, 0.15); }

.btn-icon-excel { color: #10b981; }
.btn-icon-excel:hover { color: #34d399; background: rgba(16, 185, 129, 0.15); }

.btn-icon-refresh { color: var(--text-muted); }
.btn-icon-refresh:hover { color: var(--text-primary); }

.compact-divider {
  width: 1px;
  height: 16px;
  background: var(--border-color);
  opacity: 0.8;
}
```

---

### 3. Componente React Oficial (`IconActionGroup.tsx`)

```tsx
import React from 'react';
import { Plus, FileSpreadsheet, RefreshCw } from 'lucide-react';

interface IconActionGroupProps {
  onAdd?: () => void;
  onExportExcel?: () => void;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const IconActionGroup: React.FC<IconActionGroupProps> = ({
  onAdd,
  onExportExcel,
  onRefresh,
  isRefreshing = false
}) => {
  return (
    <div className="compact-action-box" role="toolbar" aria-label="Acciones de tabla">
      {onAdd && (
        <>
          <button
            type="button"
            className="btn-icon-compact btn-icon-add"
            onClick={onAdd}
            title="Agregar nuevo registro (Abrir panel lateral)"
            aria-label="Agregar nuevo registro"
          >
            <Plus size={14} />
          </button>
          <span className="compact-divider" />
        </>
      )}

      {onExportExcel && (
        <>
          <button
            type="button"
            className="btn-icon-compact btn-icon-excel"
            onClick={onExportExcel}
            title="Descargar datos en Excel (.xlsx)"
            aria-label="Descargar en Excel"
          >
            <FileSpreadsheet size={14} />
          </button>
          <span className="compact-divider" />
        </>
      )}

      {onRefresh && (
        <button
          type="button"
          className="btn-icon-compact btn-icon-refresh"
          onClick={onRefresh}
          disabled={isRefreshing}
          title="Actualizar datos"
          aria-label="Actualizar datos"
        >
          <RefreshCw size={13} className={isRefreshing ? 'spin-icon' : ''} />
        </button>
      )}
    </div>
  );
};
```

---

### 4. Variante 2: Acciones por Fila Agrupadas en Tabla (`.row-actions-group` / Bootstrap `btn-group`)

> [!IMPORTANT]
> **REGLA MANDATORIA DE TABLAS — MÚLTIPLES BOTONES SIEMPRE AGRUPADOS**:
> Si una fila contiene **2 o más botones de acción** en su columna de opciones (ej. Ver/Editar en Right Drawer, Clave, Imprimir, Eliminar con ConfirmModal):
> **DEBEN AGRUPARSE OBLIGATORIAMENTE UTILIZANDO EL COMPONENTE `btn-group btn-group-sm` DE BOOTSTRAP** o la clase canónica `.row-actions-group`.
> Queda terminantemente prohibido dejar botones sueltos, aislados o separados por márgenes (`btn me-1`, `btn me-2`).

#### Estructura Canónica con Bootstrap 5 (`btn-group btn-group-sm`):
```html
<div class="btn-group btn-group-sm row-actions-group" role="group" aria-label="Acciones de fila">
  <button type="button" class="btn btn-outline-secondary btn-row-view" title="Editar en Sidebar Derecho" onclick="openDrawerForDetail(id)">
    <i data-lucide="eye" style="width: 13px; height: 13px;"></i>
  </button>
  <button type="button" class="btn btn-outline-warning btn-row-key" title="Restablecer contraseña" onclick="openResetPassword(id)">
    <i data-lucide="key-round" style="width: 13px; height: 13px;"></i>
  </button>
  <button type="button" class="btn btn-outline-danger btn-row-delete" title="Desactivar registro" onclick="openConfirmAction(codigo)">
    <i data-lucide="trash-2" style="width: 13px; height: 13px;"></i>
  </button>
</div>
```

#### Estructura Canónica Alternativa (CSS Puro con Divisores):
```html
<div class="row-actions-group" role="group" aria-label="Acciones de fila">
  <button type="button" class="btn-row-action btn-row-view" title="Ver detalle en panel lateral" onclick="openDrawerForDetail(id)">
    <i data-lucide="eye" style="width: 13px; height: 13px;"></i>
  </button>
  <span class="row-action-divider"></span>
  <button type="button" class="btn-row-action btn-row-delete" title="Desactivar registro" onclick="openConfirmAction(codigo)">
    <i data-lucide="trash-2" style="width: 13px; height: 13px;"></i>
  </button>
</div>
```

#### Estilos CSS para Filas:
```css
.row-actions-group {
  display: inline-flex;
  align-items: center;
  height: 26px;
  background: var(--surface-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm, 6px);
  overflow: hidden;
}

.btn-row-action {
  height: 26px;
  width: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0;
  transition: all 150ms ease;
}

.btn-row-action:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-row-view:hover {
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.12);
}

.btn-row-delete:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.12);
}

.row-action-divider {
  width: 1px;
  height: 14px;
  background: var(--border-color);
}
```
