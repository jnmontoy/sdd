# Especificación Canónica de Componente: Grupo de Filtros Superiores Expandibles (`ExpandableFilterGroup`)
## Ecosistema Jolifoods — Estándar Oficial Cartera (`bi/frontend/src/pages/Cartera.css`)

> **REGLA MANDATORIA DE DISEÑO**:
> Los filtros superiores en los tableros analíticos y operacionales de Jolifoods **NO SON MODALES NI DROPDOWNS DESPLEGABLES VERTICALES**.
> Pertenecen al estándar unificado de Cartera BI: un grupo segmentado en una sola fila (`.cartera-btn-group`) donde cada filtro **se expande horizontalmente en línea (`inline-flex`) hacia la derecha**, revelando el `<select>` y el botón de cierre `✕` dentro de la misma barra, sin superponer capas flotantes ni abrir ventanas modales.

---

### 1. Variables de Diseño CSS Canónicas

```css
:root {
  --cartera-select-arrow: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  --cartera-badge-bg: rgba(99, 102, 241, 0.22);
  --cartera-badge-color: #c7d2fe;
  --cartera-badge-border: rgba(99, 102, 241, 0.45);
  --cartera-active-filter-bg: rgba(99, 102, 241, 0.14);
  --cartera-open-filter-bg: var(--surface-elevated, #1b1b36);
  --cartera-focus-color: #6366f1;
  --cartera-focus-glow: rgba(99, 102, 241, 0.28);
  --cartera-accent-hover: #818cf8;
  --cartera-card-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

[data-theme='light'] {
  --cartera-select-arrow: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23475569' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  --cartera-badge-bg: #e0e7ff;
  --cartera-badge-color: #3730a3;
  --cartera-badge-border: #c7d2fe;
  --cartera-active-filter-bg: #eef2ff;
  --cartera-open-filter-bg: #f1f5f9;
  --cartera-focus-color: #4f46e5;
  --cartera-focus-glow: rgba(79, 70, 229, 0.2);
  --cartera-accent-hover: #4f46e5;
  --cartera-card-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
```

---

### 2. Estructura HTML Canónica (Filtros + Botón Limpiar)

```html
<div class="d-flex align-items-center gap-2">
  <!-- Grupo Segmentado de Filtros Expandibles -->
  <div class="cartera-btn-group">
    <!-- Item de Filtro Expandible -->
    <div class="cartera-expandable-filter" id="filterZona">
      <!-- Botón Trigger -->
      <button type="button" class="cartera-filter-trigger" onclick="toggleExpandableFilter('filterZona')">
        <i data-lucide="map-pin" class="trigger-icon"></i>
        <span class="trigger-text">Zona</span>
        <!-- Badge Pill (Se muestra cuando hay valor seleccionado y el filtro está cerrado) -->
        <span class="trigger-badge" id="badgeFilterZona" style="display:none;"></span>
        <i data-lucide="chevron-down" class="trigger-arrow"></i>
      </button>

      <!-- Contenedor de Expansión Horizontal Inline -->
      <div class="cartera-filter-expanded-content">
        <select class="cartera-expanded-select" id="selectFilterZona" onchange="handleSelectFilter('filterZona', this.value)">
          <option value="">Todas</option>
          <option value="Zona Norte">Zona Norte</option>
          <option value="Zona Centro">Zona Centro</option>
          <option value="Zona Sur">Zona Sur</option>
        </select>
        <button type="button" class="cartera-expanded-close" onclick="closeExpandableFilter('filterZona')" title="Cerrar filtro">
          <i data-lucide="x"></i>
        </button>
      </div>
    </div>
  </div>

  <!-- Grupo de Acciones: Botón Limpiar con Expansión Dinámica -->
  <div class="cartera-actions-btn-group">
    <div class="cartera-action-clear-wrapper" id="clearFilterWrapper">
      <button type="button" class="cartera-action-icon-btn cartera-action-btn-clear" onclick="resetAllFilters()" title="Limpiar todos los filtros" aria-label="Limpiar todos los filtros">
        <i data-lucide="filter-x"></i>
      </button>
    </div>
  </div>
</div>
```

---

### 3. Hojas de Estilo CSS Oficiales (`bi/frontend/src/pages/Cartera.css`)

```css
/* Contenedor Segmentado */
.cartera-btn-group {
  display: inline-flex;
  align-items: stretch;
  background: var(--bg-card, var(--surface-card, #131325));
  border: 1px solid var(--border-color, #2d2d48);
  border-radius: var(--radius-md, 8px);
  box-shadow: var(--cartera-card-shadow);
  overflow: hidden;
  vertical-align: middle;
}

/* Cada Filtro Segmentado */
.cartera-expandable-filter {
  display: inline-flex;
  align-items: stretch;
  position: relative;
  border-radius: 0;
  background: transparent;
  border: none;
  border-right: 1px solid var(--border-color, #2d2d48);
  box-shadow: none;
  margin: 0;
  overflow: hidden;
  transition: background-color 0.2s ease, width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.cartera-expandable-filter:last-child {
  border-right: none;
}

.cartera-expandable-filter:hover:not(.is-open) {
  background: var(--bg-hover, rgba(255, 255, 255, 0.05));
}

.cartera-expandable-filter.has-active-val {
  background: var(--cartera-active-filter-bg);
}

.cartera-expandable-filter.is-open {
  background: var(--cartera-open-filter-bg);
}

/* Botón Trigger */
.cartera-filter-trigger {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.48rem 0.8rem;
  background: transparent;
  border: none;
  color: var(--text-secondary, #94a3b8);
  font-size: var(--font-size-sm, 0.82rem);
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  outline: none;
  transition: color 0.2s ease;
}

.cartera-filter-trigger:hover {
  color: var(--text-primary, #f8fafc);
}

.cartera-filter-trigger:hover .trigger-icon {
  color: var(--cartera-accent-hover);
}

.trigger-icon {
  color: var(--text-muted, #64748b);
  transition: color 0.2s ease;
}

.trigger-text {
  color: var(--text-primary, #f8fafc);
}

/* Badge Pill Redondeado 9999px */
.trigger-badge {
  display: inline-flex;
  align-items: center;
  background: var(--cartera-badge-bg);
  color: var(--cartera-badge-color);
  border: 1px solid var(--cartera-badge-border);
  font-size: var(--font-size-xs, 0.72rem);
  font-weight: 600;
  padding: 0.15rem 0.65rem;
  border-radius: 9999px;
  max-width: none;
  white-space: nowrap;
  letter-spacing: 0.02em;
  line-height: 1.2;
}

/* Flecha Indicadora Giratoria */
.trigger-arrow {
  color: var(--text-muted, #64748b);
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), color 0.2s ease;
}

.trigger-arrow.open,
.cartera-expandable-filter.is-open .trigger-arrow {
  transform: rotate(180deg);
  color: var(--cartera-accent-hover);
}

/* EXPANSIÓN HORIZONTAL EN LÍNEA (NO ES MODAL NI POPOVER FLOTANTE) */
.cartera-filter-expanded-content {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  max-width: 0;
  opacity: 0;
  transform: scaleX(0.85);
  transform-origin: left center;
  overflow: hidden;
  pointer-events: none;
  transition: max-width 0.32s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.22s ease,
              transform 0.28s cubic-bezier(0.4, 0, 0.2, 1),
              padding 0.3s ease;
  padding: 0;
  border-left: 0 solid transparent;
}

.cartera-expandable-filter.is-open .cartera-filter-expanded-content {
  max-width: 480px;
  opacity: 1;
  transform: scaleX(1);
  pointer-events: auto;
  padding: 0.25rem 0.55rem 0.25rem 0.4rem;
  border-left: 1px solid var(--border-color, #2d2d48);
}

/* Select Estilizado */
.cartera-expanded-select {
  appearance: none;
  -webkit-appearance: none;
  background-color: var(--bg-input, var(--surface, #1e1e38));
  background-image: var(--cartera-select-arrow);
  background-repeat: no-repeat;
  background-position: right 0.6rem center;
  border: 1px solid var(--border-color, #2d2d48);
  border-radius: var(--radius-sm, 6px);
  padding: 0.32rem 1.8rem 0.32rem 0.65rem;
  font-size: var(--font-size-sm, 0.82rem);
  font-weight: 500;
  color: var(--text-primary, #f8fafc);
  cursor: pointer;
  min-width: 140px;
  max-width: 320px;
  outline: none !important;
  box-shadow: none !important;
  color-scheme: light dark;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.cartera-expanded-select:hover {
  border-color: var(--text-muted, #64748b);
}

.cartera-expanded-select:focus,
.cartera-expanded-select:focus-visible,
.cartera-expanded-select:active {
  outline: none !important;
  border-color: var(--cartera-focus-color) !important;
  box-shadow: 0 0 0 2px var(--cartera-focus-glow) !important;
}

.cartera-expanded-select option {
  background-color: var(--surface-card, #131325);
  color: var(--text-primary, #f8fafc);
}

/* Botón Cerrar Filtro Individual */
.cartera-expanded-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: var(--radius-sm, 5px);
  border: none;
  background: var(--bg-hover, rgba(255, 255, 255, 0.08));
  color: var(--text-muted, #64748b);
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.cartera-expanded-close:hover {
  background: rgba(239, 68, 68, 0.18);
  color: var(--error, #ef4444);
}

/* Botones de Acción (Limpiar Filtros) */
.cartera-actions-btn-group {
  display: inline-flex;
  align-items: stretch;
  background: var(--bg-card, var(--surface-card, #131325));
  border: 1px solid var(--border-color, #2d2d48);
  border-radius: var(--radius-md, 8px);
  box-shadow: var(--cartera-card-shadow);
  overflow: hidden;
  vertical-align: middle;
}

.cartera-action-clear-wrapper {
  display: inline-flex;
  align-items: stretch;
  max-width: 0;
  opacity: 0;
  transform: scaleX(0.7);
  transform-origin: left center;
  overflow: hidden;
  pointer-events: none;
  transition: max-width 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.25s ease,
              transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.cartera-action-clear-wrapper.is-visible {
  max-width: 45px;
  opacity: 1;
  transform: scaleX(1);
  pointer-events: auto;
}

.cartera-action-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 34px;
  padding: 0;
  background: transparent;
  border: none;
  color: var(--text-secondary, #94a3b8);
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.cartera-action-btn-clear {
  color: var(--error, #ef4444);
  background: rgba(239, 68, 68, 0.08);
}

.cartera-action-btn-clear:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}
```

---

### 4. Lógica de Interacción JavaScript Canónica

```javascript
function toggleExpandableFilter(filterId) {
  const el = document.getElementById(filterId);
  if (!el) return;
  const isOpen = el.classList.contains('is-open');

  // Cerrar todos los demás filtros
  document.querySelectorAll('.cartera-expandable-filter').forEach(f => {
    f.classList.remove('is-open');
    const badge = f.querySelector('.trigger-badge');
    if (badge && f.classList.contains('has-active-val')) {
      badge.style.display = 'inline-flex';
    }
  });

  if (!isOpen) {
    el.classList.add('is-open');
    // Ocultar temporalmente el badge del filtro que se está editando
    const badge = el.querySelector('.trigger-badge');
    if (badge) badge.style.display = 'none';
  }
}

function closeExpandableFilter(filterId) {
  const el = document.getElementById(filterId);
  if (!el) return;
  el.classList.remove('is-open');
  const badge = el.querySelector('.trigger-badge');
  if (badge && el.classList.contains('has-active-val')) {
    badge.style.display = 'inline-flex';
  }
}

// Cerrar al hacer clic fuera del grupo
document.addEventListener('click', (e) => {
  if (!e.target.closest('.cartera-expandable-filter')) {
    document.querySelectorAll('.cartera-expandable-filter').forEach(f => {
      f.classList.remove('is-open');
      const badge = f.querySelector('.trigger-badge');
      if (badge && f.classList.contains('has-active-val')) {
        badge.style.display = 'inline-flex';
      }
    });
  }
});
```
