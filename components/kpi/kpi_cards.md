# Componente UI: Tarjetas de Indicadores KPI (KPI Cards)
## SDD Joli Foods — Spec-Driven Development

> **Origen:** patrón tomado de bi (módulo cartera). Aquí se describe de forma genérica.

Las **KPI Cards** (tarjetas de indicador clave) muestran indicadores operativos, financieros y de desempeño. Admiten **KPIs clicables** que funcionan como **filtros rápidos de la tabla asociada**, estados de carga con esqueleto (*skeleton*: silueta animada mientras llegan los datos), badge de filtro activo y cajas de icono por color. Los colores salen de [`variables.css`](../variables.css), por lo que funcionan en Modo Noche y Modo Día.

---

## 1. Características técnicas

1. **KPI clicable como filtro (`clickable-kpi-card`)**
   - Al activarlo (clic, `Enter` o `Espacio`) se activa o desactiva un filtro de la tabla asociada (ej. *"Ver solo registros con mora"* o *"Ver solo usuarios inactivos"*).
   - Un KPI clicable DEBE renderizarse como `<button>` con `aria-pressed` para que funcione con teclado y lector de pantalla.
   - Muestra el badge `joli-kpi-filter-badge` con el texto `FILTRO ACTIVO` y resalta borde y fondo.
2. **Cajas de icono por color (`joli-kpi-icon-box`)**:
   - `.icon-blue`: total general.
   - `.icon-amber`: vencimientos / advertencias.
   - `.icon-pink`: crítico (mora, bloqueados, errores).
   - `.icon-emerald`: completados, saludables.
   - `.icon-cyan`: en tránsito, en proceso.
   - `.icon-indigo`: categoría adicional.
   - El color NO DEBE ser el único portador del significado: la etiqueta del KPI debe decir qué mide.
3. **Estado esqueleto (`is-skeleton`)**: renderiza siluetas animadas (`joli-skeleton-bone`) mientras el backend responde, con `aria-busy="true"`.

---

## 2. Código React + TypeScript (`KPICards.tsx`)

```tsx
import React from 'react';

export type KPIIconColor = 'icon-blue' | 'icon-amber' | 'icon-pink' | 'icon-emerald' | 'icon-cyan' | 'icon-indigo';

export interface KPICardItem {
  id: string;
  label: string;
  value: string | number;
  subtext?: string;
  icon: React.ReactNode;
  iconColorClass: KPIIconColor;
  isClickable?: boolean;
  isActiveFilter?: boolean;
  onClick?: () => void;
}

export interface KPIRowProps {
  items: KPICardItem[];
  loading?: boolean;
  skeletonCount?: number;
}

const KPICardContent: React.FC<{ kpi: KPICardItem }> = ({ kpi }) => (
  <>
    <div className="joli-kpi-content">
      <div className="joli-kpi-label-row">
        <span className="joli-kpi-label">{kpi.label}</span>
        {kpi.isActiveFilter && <span className="joli-kpi-filter-badge">FILTRO ACTIVO</span>}
      </div>
      <div className="joli-kpi-value">{kpi.value}</div>
      {kpi.subtext && <span className="joli-kpi-subtext">{kpi.subtext}</span>}
    </div>
    <div className={`joli-kpi-icon-box ${kpi.iconColorClass}`} aria-hidden="true">
      {kpi.icon}
    </div>
  </>
);

export const KPIRow: React.FC<KPIRowProps> = ({ items, loading = false, skeletonCount = 4 }) => {
  if (loading) {
    return (
      <div className="joli-kpi-row" aria-busy="true" aria-label="Cargando indicadores">
        {Array.from({ length: skeletonCount }, (_, idx) => (
          <div key={`skeleton-${idx}`} className="joli-kpi-card is-skeleton">
            <div className="joli-kpi-content w-100">
              <div className="joli-skeleton-bone skeleton-title" />
              <div className="joli-skeleton-bone skeleton-value" />
              <div className="joli-skeleton-bone skeleton-sub" />
            </div>
            <div className="joli-skeleton-bone skeleton-icon" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="joli-kpi-row">
      {items.map((kpi) =>
        kpi.isClickable ? (
          // KPI interactivo: <button> nativo => foco, Enter y Espacio sin código extra.
          <button
            key={kpi.id}
            type="button"
            className={`joli-kpi-card clickable-kpi-card ${kpi.isActiveFilter ? 'active-filter' : ''}`}
            onClick={kpi.onClick}
            aria-pressed={Boolean(kpi.isActiveFilter)}
            title={kpi.isActiveFilter ? 'Quitar filtro' : `Filtrar la tabla por: ${kpi.label}`}
          >
            <KPICardContent kpi={kpi} />
          </button>
        ) : (
          <div key={kpi.id} className="joli-kpi-card">
            <KPICardContent kpi={kpi} />
          </div>
        )
      )}
    </div>
  );
};
```

---

## 3. Estilos CSS del componente

Los estilos consumen solo tokens de `variables.css`. Los fondos translúcidos se derivan con `color-mix()` en lugar de quemar `rgba()`.

```css
/* REJILLA RESPONSIVE */
.joli-kpi-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

@media (max-width: 1200px) {
  .joli-kpi-row { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

@media (max-width: 768px) {
  .joli-kpi-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 480px) {
  .joli-kpi-row { grid-template-columns: 1fr; }
}

/* TARJETA KPI */
.joli-kpi-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  text-align: left;
  font: inherit;
  color: inherit;
  background-color: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 1rem 1.25rem;
  box-shadow: var(--shadow-card);
  min-width: 0;
  transition: transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
}

/* Sin transform: ninguna tarjeta se mueve al pasar el mouse (regla en card/corporate_card.md) */
.joli-kpi-card:hover {
<<<<<<< HEAD
  transform: translateY(-2px);
  border-color: var(--border-strong);
  box-shadow: var(--shadow-popover);
=======
  border-color: var(--color-text-muted);
  box-shadow: var(--shadow-md);
>>>>>>> dfa6d576ff1a43eacc452032a5ce4df42852bd45
}

/* KPI CLICABLE */
.joli-kpi-card.clickable-kpi-card {
  cursor: pointer;
  position: relative;
}

.joli-kpi-card.clickable-kpi-card:hover {
  border-color: var(--brand-primary);
  box-shadow: 0 6px 20px color-mix(in srgb, var(--brand-primary) 20%, transparent);
}

.joli-kpi-card.clickable-kpi-card:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
  border-color: var(--border-focus);
}

.joli-kpi-card.clickable-kpi-card.active-filter {
  border-color: var(--brand-primary);
  background: color-mix(in srgb, var(--brand-primary) 8%, var(--bg-card));
  box-shadow: 0 0 16px var(--brand-glow);
}

.joli-kpi-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.joli-kpi-filter-badge {
  font-size: 9px;
  font-weight: var(--font-weight-extrabold);
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  background: var(--status-success-bg);
  color: var(--status-success);
  border: 1px solid color-mix(in srgb, var(--status-success) 40%, transparent);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  animation: pulseFilter 2s infinite;
}

@keyframes pulseFilter {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

@media (prefers-reduced-motion: reduce) {
  .joli-kpi-filter-badge, .joli-skeleton-bone { animation: none; }
  .joli-kpi-card:hover { transform: none; }
}

.joli-kpi-content {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.joli-kpi-label {
  font-size: var(--font-size-2xs);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.05em;
  color: var(--text-muted);
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.joli-kpi-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-extrabold);
  color: var(--text-primary);
  line-height: var(--line-height-tight);
  margin: 0.2rem 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.joli-kpi-subtext {
  font-size: var(--font-size-2xs);
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* CAJA DE ICONO */
.joli-kpi-icon-box {
  --kpi-accent: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-lg);
  color: var(--kpi-accent);
  background: color-mix(in srgb, var(--kpi-accent) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--kpi-accent) 25%, transparent);
  flex-shrink: 0;
  margin-left: 0.5rem;
}

.joli-kpi-icon-box.icon-blue    { --kpi-accent: var(--accent-blue); }
.joli-kpi-icon-box.icon-amber   { --kpi-accent: var(--status-warning); }
.joli-kpi-icon-box.icon-pink    { --kpi-accent: var(--status-error); }
.joli-kpi-icon-box.icon-emerald { --kpi-accent: var(--status-success); }
.joli-kpi-icon-box.icon-cyan    { --kpi-accent: var(--accent-cyan); }
.joli-kpi-icon-box.icon-indigo  { --kpi-accent: var(--accent-indigo); }

/* ESQUELETOS DE CARGA */
.joli-kpi-card.is-skeleton {
  pointer-events: none;
}

.joli-skeleton-bone {
  background: linear-gradient(90deg, var(--border-subtle) 25%, var(--bg-hover) 50%, var(--border-subtle) 75%);
  background-size: 200% 100%;
  animation: joliSkeletonLoading 1.5s infinite;
  border-radius: var(--radius-sm);
}

.skeleton-title { width: 60%; height: 10px; margin-bottom: 8px; }
.skeleton-value { width: 80%; height: 24px; margin-bottom: 6px; }
.skeleton-sub { width: 45%; height: 10px; }
.skeleton-icon { width: 44px; height: 44px; border-radius: var(--radius-lg); flex-shrink: 0; }

@keyframes joliSkeletonLoading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

> `--kpi-accent` es una variable local del componente (no un color nuevo): solo apunta a un token de `variables.css` según la clase.
