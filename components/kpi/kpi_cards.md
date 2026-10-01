# Componente UI: Tarjetas de Indicadores KPI (KPI Cards)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)
### Patrón Canónico de Referencia: Módulo BI Cartera

Las **KPI Cards** son el componente estándar de visualización de indicadores operativos, financieros y métricas de desempeño en Jolifoods.

Inspirado en el estándar de mayor fidelidad de **BI Cartera**, este componente admite **KPIs interactivos / clickeables** que actúan como **filtros rápidos de tabla**, estados de carga esqueleto (*Skeleton Loaders*), badges de filtro activo y cajas de iconos cromáticas con soporte nativo de Modo Noche y Día gobernadas por [`variables.css`](../variables.css).

---

## 1. Características Técnicas

1. **KPI Clickeable como Filtro (`clickable-kpi-card`)**:
   - Al hacer clic en la tarjeta, activa o desactiva un filtro global en la tabla asociada (ej. *"Ver solo registros con mora"* o *"Ver solo usuarios inactivos"*).
   - Muestra un badge pulsante `kpi-filter-badge` con el texto `FILTRO ACTIVO`.
   - Modifica el borde y fondo de la tarjeta con un resplandor (*glow*) identificativo.
2. **Cajas de Iconos Cromáticas (`kpi-icon-box`)**:
   - Iconos enmarcados en contenedores con esquinas redondeadas (`border-radius: 10px`), fondo elevado y bordes con colores institucionales:
     - `.icon-blue`: Azul corporativo (Total general).
     - `.icon-amber`: Ámbar preventivo (Vencimientos / Advertencias).
     - `.icon-pink` / `.icon-danger`: Rojo / Carmesí crítico (Mora, Bloqueados, Errores).
     - `.icon-emerald` / `.icon-success`: Verde esmeralda (Completados, Saludables).
     - `.icon-cyan`: Cian (En tránsito, En proceso).
3. **Soporte de Estado Esqueleto (`is-skeleton`)**:
   - Renderiza esqueletos animados (`cartera-skeleton-bone`) mientras el backend resuelve las consultas.

---

## 2. Código JSX / React 19 Canónico (`KPICards.tsx`)

```tsx
import React from 'react';
import { 
  TrendingUp, 
  Clock, 
  AlertCircle, 
  ShieldCheck, 
  Activity, 
  ArrowUpRight 
} from 'lucide-react';
import '../../styles/variables.css';

export interface KPICardItem {
  id: string;
  label: string;
  value: string | number;
  subtext?: string;
  icon: React.ReactNode;
  iconColorClass: 'icon-blue' | 'icon-amber' | 'icon-pink' | 'icon-emerald' | 'icon-cyan' | 'icon-indigo';
  isClickable?: boolean;
  isActiveFilter?: boolean;
  onClick?: () => void;
}

export interface KPIRowProps {
  items: KPICardItem[];
  loading?: boolean;
}

export const KPIRow: React.FC<KPIRowProps> = ({ items, loading = false }) => {
  if (loading) {
    return (
      <div className="joli-kpi-row" aria-busy="true">
        {[1, 2, 3, 4].map((idx) => (
          <div key={idx} className="joli-kpi-card is-skeleton">
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
      {items.map((kpi) => (
        <div
          key={kpi.id}
          className={`joli-kpi-card ${kpi.isClickable ? 'clickable-kpi-card' : ''} ${kpi.isActiveFilter ? 'active-filter' : ''}`}
          onClick={kpi.isClickable ? kpi.onClick : undefined}
          role={kpi.isClickable ? 'button' : undefined}
          tabIndex={kpi.isClickable ? 0 : undefined}
        >
          <div className="joli-kpi-content">
            <div className="joli-kpi-label-row">
              <span className="joli-kpi-label">{kpi.label}</span>
              {kpi.isActiveFilter && (
                <span className="joli-kpi-filter-badge">FILTRO ACTIVO</span>
              )}
            </div>
            <div className="joli-kpi-value">{kpi.value}</div>
            {kpi.subtext && <span className="joli-kpi-subtext">{kpi.subtext}</span>}
          </div>
          <div className={`joli-kpi-icon-box ${kpi.iconColorClass}`}>
            {kpi.icon}
          </div>
        </div>
      ))}
    </div>
  );
};
```

---

## 3. Estilos CSS Canónicos (`variables.css`)

```css
/* REJILLA RESPONSIVE INTELIGENTE */
.joli-kpi-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

@media (max-width: 1200px) {
  .joli-kpi-row {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .joli-kpi-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 480px) {
  .joli-kpi-row {
    grid-template-columns: 1fr;
  }
}

/* TARJETA KPI */
.joli-kpi-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 1rem 1.25rem;
  box-shadow: var(--shadow-sm);
  min-width: 0;
  transition: transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.joli-kpi-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-text-muted);
  box-shadow: var(--shadow-md);
}

/* KPI INTERACTIVO / CLICKEABLE */
.joli-kpi-card.clickable-kpi-card {
  cursor: pointer;
  position: relative;
}

.joli-kpi-card.clickable-kpi-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.2);
}

.joli-kpi-card.clickable-kpi-card.active-filter {
  border-color: var(--color-primary);
  background: rgba(16, 185, 129, 0.08);
  box-shadow: 0 0 16px rgba(16, 185, 129, 0.35);
}

.joli-kpi-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.joli-kpi-filter-badge {
  font-size: 9px;
  font-weight: 800;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  animation: pulseFilter 2s infinite;
}

@keyframes pulseFilter {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.joli-kpi-content {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.joli-kpi-label {
  font-size: 11px;
  font-weight: var(--weight-bold);
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.joli-kpi-value {
  font-size: var(--text-2xl);
  font-weight: var(--weight-extrabold);
  color: var(--color-text-primary);
  line-height: 1.2;
  margin: 0.2rem 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.joli-kpi-subtext {
  font-size: 11px;
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* CAJA DE ICONOS */
.joli-kpi-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-lg);
  background: var(--color-bg-input);
  border: 1px solid var(--color-border);
  flex-shrink: 0;
  margin-left: 0.5rem;
}

.joli-kpi-icon-box.icon-blue {
  color: #3b82f6;
  border-color: rgba(59, 130, 246, 0.25);
  background: rgba(59, 130, 246, 0.08);
}

.joli-kpi-icon-box.icon-amber {
  color: #f59e0b;
  border-color: rgba(245, 158, 11, 0.25);
  background: rgba(245, 158, 11, 0.08);
}

.joli-kpi-icon-box.icon-pink {
  color: #f43f5e;
  border-color: rgba(244, 63, 94, 0.25);
  background: rgba(244, 63, 94, 0.08);
}

.joli-kpi-icon-box.icon-emerald {
  color: #10b981;
  border-color: rgba(16, 185, 129, 0.25);
  background: rgba(16, 185, 129, 0.08);
}

.joli-kpi-icon-box.icon-cyan {
  color: #06b6d4;
  border-color: rgba(6, 182, 212, 0.25);
  background: rgba(6, 182, 212, 0.08);
}

.joli-kpi-icon-box.icon-indigo {
  color: #6366f1;
  border-color: rgba(99, 102, 241, 0.25);
  background: rgba(99, 102, 241, 0.08);
}

/* SKELETON LOADERS */
.joli-kpi-card.is-skeleton {
  pointer-events: none;
}

.joli-skeleton-bone {
  background: linear-gradient(90deg, var(--color-border) 25%, var(--color-bg-card-hover) 50%, var(--color-border) 75%);
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
