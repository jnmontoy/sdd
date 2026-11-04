# Especificación de Componente: Grupo de Filtros Superiores Expandibles (`ExpandableFilterGroup`)
## Spec-Driven Development (SDD)

<<<<<<< HEAD
### Regla de uso

- **Regla:** los filtros superiores de tableros analíticos y pantallas operativas DEBERÍAN usar este grupo segmentado en una sola fila (`.expandable-filter-group`), donde cada filtro se expande **horizontalmente en línea** hacia la derecha mostrando su selector y un botón de cierre `✕`, sin modales ni menús flotantes.
- **Por qué:** los filtros quedan visibles junto a los datos, no tapan la tabla y ocupan una sola línea en la barra superior.
- **Excepciones:** más de 6 filtros o filtros complejos (rangos de fechas con calendario) PUEDEN ir en un panel lateral ([`drawer.md`](../drawer/drawer.md)); decisión registrada (ADR).

Accesibilidad: cada disparador expone `aria-expanded` y `aria-controls`; el contenido cerrado queda fuera del orden de tabulación (`visibility: hidden`); cada selector tiene etiqueta accesible; `Escape` cierra el filtro abierto y devuelve el foco a su disparador.
=======
> **REGLA MANDATORIA DE DISEÑO**:
> 1. Los filtros superiores en los tableros analíticos y operacionales de Jolifoods **NO SON MODALES NI DROPDOWNS DESPLEGABLES VERTICALES**.
>    Pertenecen al estándar unificado de filtros en línea: un grupo segmentado en una sola fila (`.expandable-filter-group`) donde cada filtro (ej. `Rol`, `Estado`) **se expande horizontalmente en línea (`inline-flex`) hacia la derecha**, revelando el `<select>` y el botón de cierre `✕` dentro de la misma barra, sin superponer capas flotantes ni abrir ventanas modales.
> 2. **SEPARACIÓN DEL BUSCADOR EN LA BOTONERA DE LOS TRES (TABLA + CARDS + BUSCAR — SOLO ICONOS)**:
>    El buscador (`Buscar`) **no se mezcla con los filtros `<select>`**, sino que se agrupa en la **botonera de los tres (`.view-switcher`)** junto a los selectores de vista **Tabla (`Table2`)** y **Cards (`LayoutGrid`)**, mostrando **únicamente los iconos y ningún texto**. Al hacer clic en el icono de **Buscar (`Search`)**, se despliega con animación horizontal hacia la derecha el `<input class="switcher-search-input">` (ver [`../button/icon_action_group.md`](../button/icon_action_group.md)).
>>>>>>> dfa6d576ff1a43eacc452032a5ce4df42852bd45

---

### 1. Variables del componente

Se derivan de los tokens de [`variables.css`](../variables.css), así que funcionan en ambos temas. Solo la flecha del selector necesita dos versiones, porque un SVG en `background-image` no hereda `currentColor` (excepción válida de SVG).

```css
:root,
[data-theme='dark'] {
  --filter-select-arrow: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
}

[data-theme='light'] {
  --filter-select-arrow: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23475569' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
}

.expandable-filter-group,
.filter-actions-group {
  --filter-badge-bg: var(--status-success-bg);
  --filter-badge-color: var(--text-primary);
  --filter-badge-border: var(--border-card-accent);
  --filter-active-filter-bg: var(--status-success-bg);
  --filter-open-filter-bg: var(--bg-elevated);
  --filter-focus-color: var(--border-focus);
  --filter-focus-glow: var(--input-focus-ring);
  --filter-accent-hover: var(--brand-primary);
  --filter-card-shadow: var(--shadow-card);
}
```

---

<<<<<<< HEAD
### 2. Estructura HTML (filtros + botón limpiar)

```html
<div class="d-flex align-items-center gap-2">
  <div class="expandable-filter-group" role="group" aria-label="Filtros">
=======
### 2. Estructura HTML Canónica (Grupo de Tres: Buscar [Solo Icono] + Filtros + Botón Limpiar)

```html
<div class="d-flex align-items-center gap-2">
  <!-- Grupo Segmentado de Tres: Buscador (Solo Icono) + Filtros Expandibles -->
  <div class="expandable-filter-group">
    <!-- 1. Buscador Expandible hacia la Derecha (SOLO ICONO, SIN TEXTO) -->
    <div class="expandable-filter-item" id="filterSearch">
      <button type="button" class="filter-trigger-btn filter-trigger-icon-only" onclick="toggleExpandableFilter('filterSearch')" title="Buscar registros" aria-label="Buscar registros">
        <i data-lucide="search" class="trigger-icon"></i>
        <span class="trigger-badge" id="badgeFilterSearch" style="display:none;"></span>
      </button>
      <div class="filter-expanded-content">
        <input type="text" class="filter-expanded-input" id="inputFilterSearch" placeholder="Buscar por cédula, nombre, cargo o correo..." />
        <button type="button" class="filter-expanded-close" onclick="closeExpandableFilter('filterSearch')" title="Contraer buscador">
          <i data-lucide="x"></i>
        </button>
      </div>
    </div>

    <!-- 2. Item de Filtro Expandible (Ej. Rol / Zona) -->
>>>>>>> dfa6d576ff1a43eacc452032a5ce4df42852bd45
    <div class="expandable-filter-item" id="filterZona">
      <button type="button" class="filter-trigger-btn"
              aria-expanded="false" aria-controls="filterZonaContent"
              onclick="toggleExpandableFilter('filterZona')">
        <i data-lucide="map-pin" class="trigger-icon" aria-hidden="true"></i>
        <span class="trigger-text">Zona</span>
        <!-- Se muestra con el valor elegido cuando el filtro está cerrado -->
        <span class="trigger-badge" id="badgeFilterZona" hidden></span>
        <i data-lucide="chevron-down" class="trigger-arrow" aria-hidden="true"></i>
      </button>

      <div class="filter-expanded-content" id="filterZonaContent">
        <select class="filter-expanded-select" id="selectFilterZona" aria-label="Filtrar por zona"
                onchange="handleSelectFilter('filterZona', this)">
          <option value="">Todas</option>
          <option value="norte">Zona Norte</option>
          <option value="centro">Zona Centro</option>
          <option value="sur">Zona Sur</option>
        </select>
        <button type="button" class="filter-expanded-close" aria-label="Cerrar filtro de zona" title="Cerrar filtro"
                onclick="closeExpandableFilter('filterZona', true)">
          <i data-lucide="x" aria-hidden="true"></i>
        </button>
      </div>
    </div>
  </div>

  <div class="filter-actions-group">
    <div class="filter-action-clear-wrapper" id="clearFilterWrapper">
      <button type="button" class="filter-action-icon-btn filter-action-btn-clear"
              onclick="resetAllFilters()" title="Limpiar todos los filtros" aria-label="Limpiar todos los filtros">
        <i data-lucide="filter-x" aria-hidden="true"></i>
      </button>
    </div>
  </div>
</div>
```

---

### 3. Estilos CSS (`expandable_filter_group.css`)

```css
.expandable-filter-group {
  display: inline-flex;
  align-items: stretch;
  overflow: hidden;
  vertical-align: middle;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  box-shadow: var(--filter-card-shadow);
}

.expandable-filter-item {
  position: relative;
  display: inline-flex;
  align-items: stretch;
  margin: 0;
  overflow: hidden;
  background: transparent;
  border-right: 1px solid var(--border-subtle);
  transition: background-color 0.2s ease;
}

.expandable-filter-item:last-child {
  border-right: none;
}

.expandable-filter-item:hover:not(.is-open) {
  background: var(--bg-hover);
}

.expandable-filter-item.has-active-val {
  background: var(--filter-active-filter-bg);
}

.expandable-filter-item.is-open {
  background: var(--filter-open-filter-bg);
}

.filter-trigger-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.48rem 0.8rem;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  white-space: nowrap;
  cursor: pointer;
  transition: color 0.2s ease;
}

.filter-trigger-btn:hover {
  color: var(--text-primary);
}

.filter-trigger-btn:focus-visible {
  outline: 2px solid var(--filter-focus-color);
  outline-offset: -2px;
}

.filter-trigger-btn:hover .trigger-icon {
  color: var(--filter-accent-hover);
}

.trigger-icon {
  color: var(--text-muted);
  transition: color 0.2s ease;
}

.trigger-text {
  color: var(--text-primary);
}

.trigger-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.15rem 0.65rem;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  line-height: 1.2;
  letter-spacing: 0.02em;
  white-space: nowrap;
  background: var(--filter-badge-bg);
  color: var(--filter-badge-color);
  border: 1px solid var(--filter-badge-border);
  border-radius: var(--radius-full);
}

.trigger-badge[hidden] {
  display: none;
}

.trigger-arrow {
  color: var(--text-muted);
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), color 0.2s ease;
}

.expandable-filter-item.is-open .trigger-arrow {
  transform: rotate(180deg);
  color: var(--filter-accent-hover);
}

/* Expansión horizontal en línea. visibility: hidden saca los controles del orden de tabulación al cerrar. */
.filter-expanded-content {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  max-width: 0;
  padding: 0;
  overflow: hidden;
  opacity: 0;
  visibility: hidden;
  transition: max-width 0.32s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.22s ease, padding 0.3s ease, visibility 0s linear 0.32s;
}

.expandable-filter-item.is-open .filter-expanded-content {
  max-width: 480px;
  padding: 0.25rem 0.55rem 0.25rem 0.4rem;
  opacity: 1;
  visibility: visible;
  border-left: 1px solid var(--border-subtle);
  transition: max-width 0.32s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.22s ease, padding 0.3s ease, visibility 0s;
}

.filter-expanded-select {
  min-width: 140px;
  max-width: 320px;
  padding: 0.32rem 1.8rem 0.32rem 0.65rem;
  appearance: none;
  -webkit-appearance: none;
  background-color: var(--input-bg);
  background-image: var(--filter-select-arrow);
  background-repeat: no-repeat;
  background-position: right 0.6rem center;
  border: 1px solid var(--input-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--input-text);
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.filter-expanded-select:hover {
  border-color: var(--input-border-hover);
}

.filter-expanded-select:focus-visible {
  outline: none;
  border-color: var(--filter-focus-color);
  box-shadow: 0 0 0 2px var(--filter-focus-glow);
}

.filter-expanded-select option {
  background-color: var(--bg-card);
  color: var(--text-primary);
}

.filter-expanded-close {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--bg-hover);
  color: var(--text-muted);
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.filter-expanded-close:hover {
  background: var(--status-error-bg);
  color: var(--status-error);
}

.filter-expanded-close:focus-visible,
.filter-action-icon-btn:focus-visible {
  outline: 2px solid var(--filter-focus-color);
  outline-offset: 1px;
}

.filter-actions-group {
  display: inline-flex;
  align-items: stretch;
  overflow: hidden;
  vertical-align: middle;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  box-shadow: var(--filter-card-shadow);
}

.filter-action-clear-wrapper {
  display: inline-flex;
  align-items: stretch;
  max-width: 0;
  overflow: hidden;
  opacity: 0;
  visibility: hidden;
  transition: max-width 0.3s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.25s ease, visibility 0s linear 0.3s;
}

.filter-action-clear-wrapper.is-visible {
  max-width: 45px;
  opacity: 1;
  visibility: visible;
  transition: max-width 0.3s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.25s ease, visibility 0s;
}

.filter-action-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 34px;
  padding: 0;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.filter-action-btn-clear {
  color: var(--status-error);
  background: var(--status-error-bg);
}

.filter-action-btn-clear:hover {
  filter: brightness(1.15);
}

@media (prefers-reduced-motion: reduce) {
  .filter-expanded-content,
  .filter-action-clear-wrapper,
  .trigger-arrow { transition: none; }
}
```

---

### 4. Lógica de interacción (JavaScript para mocks)

```javascript
const activeFilters = {}; // { filterZona: 'norte', ... }

function setBadge(item) {
  const badge = item.querySelector('.trigger-badge');
  if (!badge) return;
  const hasValue = item.classList.contains('has-active-val');
  badge.hidden = !(hasValue && !item.classList.contains('is-open'));
}

function setOpen(item, open) {
  item.classList.toggle('is-open', open);
  item.querySelector('.filter-trigger-btn')?.setAttribute('aria-expanded', String(open));
  setBadge(item);
}

function toggleExpandableFilter(filterId) {
  const el = document.getElementById(filterId);
  if (!el) return;
  const willOpen = !el.classList.contains('is-open');
  document.querySelectorAll('.expandable-filter-item.is-open').forEach((f) => setOpen(f, false));
  if (willOpen) {
    setOpen(el, true);
    el.querySelector('.filter-expanded-select')?.focus();
  }
}

function closeExpandableFilter(filterId, returnFocus = false) {
  const el = document.getElementById(filterId);
  if (!el) return;
  setOpen(el, false);
  if (returnFocus) el.querySelector('.filter-trigger-btn')?.focus();
}

function updateClearButton() {
  const anyActive = Object.values(activeFilters).some(Boolean);
  document.getElementById('clearFilterWrapper')?.classList.toggle('is-visible', anyActive);
}

function handleSelectFilter(filterId, select) {
  const el = document.getElementById(filterId);
  if (!el) return;
  activeFilters[filterId] = select.value;
  el.classList.toggle('has-active-val', select.value !== '');
  const badge = el.querySelector('.trigger-badge');
  if (badge) badge.textContent = select.value ? select.options[select.selectedIndex].text : '';
  updateClearButton();
  applyFilters(activeFilters); // función del módulo que recarga la tabla
}

function resetAllFilters() {
  document.querySelectorAll('.expandable-filter-item').forEach((item) => {
    const select = item.querySelector('.filter-expanded-select');
    if (select) select.value = '';
    item.classList.remove('has-active-val');
    activeFilters[item.id] = '';
    setOpen(item, false);
  });
  updateClearButton();
  applyFilters(activeFilters);
}

// Cerrar al hacer clic fuera o con Escape
document.addEventListener('click', (e) => {
  if (!e.target.closest('.expandable-filter-item')) {
    document.querySelectorAll('.expandable-filter-item.is-open').forEach((f) => setOpen(f, false));
  }
});

document.addEventListener('keydown', (e) => {
  if (e.key !== 'Escape') return;
  const open = document.querySelector('.expandable-filter-item.is-open');
  if (open) closeExpandableFilter(open.id, true);
});
```

En React, el mismo comportamiento se implementa con un estado `openFilterId` y efectos con limpieza para los listeners de `click` y `keydown`.
