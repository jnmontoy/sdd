# 01. Especificación del Tablero Principal (Dashboard Operativo)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

Esta especificación describe la vista de aterrizaje (**Home / Dashboard**) presentada al colaborador una vez autenticado a través del módulo de Login y envuelto en el **Layout Maestro (App Shell)**.

Ofrece una visión ejecutiva y operativa instantánea, con indicadores clave de rendimiento (KPIs), gráfico de actividad temporal y bitácora de accesos recientes.

---

## 1. Topología de la Vista

```
+------------------------------------------------------------------------------------------------+
|  ¡Bienvenido de nuevo, [Nombre del Usuario]!                                                   |
|  Panel Operativo • Sede Principal • [Fecha y Hora Actual]                                       |
+------------------------------------------------------------------------------------------------+
|  [ KPI 1: Accesos Hoy ]  [ KPI 2: Sesiones Activas ]  [ KPI 3: Operaciones ]  [ KPI 4: Estado] |
|        1,280 (+12%)              42 en línea                856 completadas       99.9% Óptimo |
+------------------------------------------------------------------------------------------------+
|                                              |                                                 |
|  Gráfica de Actividad por Hora (Canvas/CSS)  |  Bitácora de Accesos Recientes                  |
|  [Curva de demanda y peticiones atendidas]   |  - Joan Montoya (1020405060) • Hace 2 min       |
|                                              |  - Operador Sede (1010203040) • Hace 8 min      |
+------------------------------------------------------------------------------------------------+
```

---

## 2. Anatomía de los Componentes del Dashboard

### 2.1. Tarjetas KPI (KPI Cards)
Cada tarjeta consume los tokens de [`variables.css`](../../../components/variables.css) con elevación suave (`--shadow-md`), borde sutil (`--color-border`) y fondo adaptable (`--color-bg-card`):
- **KPI 1: Accesos Totales**: Contador numérico con indicador de tendencia porcentual en verde esmeralda.
- **KPI 2: Sesiones Simultáneas**: Lectura en tiempo real de sesiones en Redis con pulso animado.
- **KPI 3: Operaciones Realizadas**: Métricas del módulo específico del proyecto (transacciones, registros o despachos).
- **KPI 4: Salud de Infraestructura**: Estado reportado por `/api/v1/health/` (Latencia < 15ms).

---

## 3. Implementación en React 19 + TypeScript (`DashboardPage.tsx`)

```tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { 
  Users, 
  Activity, 
  CheckCircle2, 
  TrendingUp, 
  ShieldCheck, 
  Clock, 
  ArrowUpRight 
} from 'lucide-react';
import '../../styles/variables.css';

interface KPIItem {
  id: string;
  title: string;
  value: string | number;
  change: string;
  isPositive: boolean;
  icon: React.ReactNode;
}

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [currentDate, setCurrentDate] = useState<string>('');

  useEffect(() => {
    const now = new Date();
    setCurrentDate(
      now.toLocaleDateString('es-CO', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })
    );
  }, []);

  const [activeKpiFilter, setActiveKpiFilter] = useState<string | null>(null);

  const kpis = [
    {
      id: 'kpi-accesos',
      label: 'ACCESOS HOY',
      value: '1,280',
      subtext: 'Valor total verificado',
      icon: <Users size={20} />,
      colorClass: 'icon-blue',
      clickable: false
    },
    {
      id: 'kpi-sesiones',
      label: 'SESIONES ACTIVAS',
      value: '42',
      subtext: 'Sesiones concurrentes',
      icon: <Activity size={20} />,
      colorClass: 'icon-emerald',
      clickable: true
    },
    {
      id: 'kpi-mora',
      label: 'INCIDENCIAS O ALERTAS',
      value: '3',
      subtext: 'Intentos fallidos / alertas',
      icon: <AlertCircle size={20} />,
      colorClass: 'icon-pink',
      clickable: true
    },
    {
      id: 'kpi-salud',
      label: 'ESTADO DE INFRAESTRUCTURA',
      value: '99.98%',
      subtext: 'Latencia 2.3ms • Óptimo',
      icon: <ShieldCheck size={20} />,
      colorClass: 'icon-cyan',
      clickable: false
    }
  ];

  return (
    <div className="joli-dashboard-container">
      {/* 1. CABECERA DE BIENVENIDA */}
      <section className="joli-dashboard-hero mb-4">
        <div>
          <h1 className="joli-hero-title">
            ¡Bienvenido de nuevo, {user?.nombre || user?.username || 'Colaborador'}!
          </h1>
          <p className="joli-hero-subtitle">
            Ecosistema Jolifoods &bull; {user?.sede || 'Sede Principal'} &bull; <span className="text-capitalize">{currentDate}</span>
          </p>
        </div>
      </section>

      {/* 2. REJILLA DE TARJETAS KPI (ESTÁNDAR BI CARTERA) */}
      <div className="joli-kpi-row">
        {kpis.map((kpi) => {
          const isFilterActive = activeKpiFilter === kpi.id;
          return (
            <div
              key={kpi.id}
              className={`joli-kpi-card ${kpi.clickable ? 'clickable-kpi-card' : ''} ${isFilterActive ? 'active-filter' : ''}`}
              onClick={() => {
                if (kpi.clickable) {
                  setActiveKpiFilter((prev) => (prev === kpi.id ? null : kpi.id));
                }
              }}
              title={kpi.clickable ? "Clic para filtrar los registros de la bitácora" : undefined}
            >
              <div className="joli-kpi-content">
                <div className="joli-kpi-label-row">
                  <span className="joli-kpi-label">{kpi.label}</span>
                  {isFilterActive && (
                    <span className="joli-kpi-filter-badge">FILTRO ACTIVO</span>
                  )}
                </div>
                <div className="joli-kpi-value">{kpi.value}</div>
                <span className="joli-kpi-subtext">{kpi.subtext}</span>
              </div>
              <div className={`joli-kpi-icon-box ${kpi.colorClass}`}>
                {kpi.icon}
              </div>
            </div>
          );
        })}
      </div>

      {/* 3. SECCIÓN MIXTA: ACTIVIDAD Y BITÁCORA */}
      <div className="row g-4">
        {/* PANEL DE ACTIVIDAD TEMPORAL */}
        <div className="col-12 col-lg-8">
          <div className="joli-panel-card h-100">
            <div className="joli-panel-header">
              <h2 className="joli-panel-title">Monitoreo de Actividad en Vivo</h2>
              <span className="badge bg-success-subtle text-success">Operación Normal</span>
            </div>
            <div className="joli-panel-body d-flex align-items-center justify-content-center" style={{ minHeight: '260px' }}>
              <div className="text-center text-muted">
                <TrendingUp size={48} className="mb-2 text-primary opacity-50" />
                <p className="mb-0">Canal de telemetría activo. Registros en tiempo real conectados vía FastAPI ASGI.</p>
              </div>
            </div>
          </div>
        </div>

        {/* BITÁCORA DE ACCESOS RECIENTES */}
        <div className="col-12 col-lg-4">
          <div className="joli-panel-card h-100">
            <div className="joli-panel-header">
              <h2 className="joli-panel-title">Últimos Inicios de Sesión</h2>
              <Clock size={18} className="text-muted" />
            </div>
            <div className="joli-panel-body p-0">
              <ul className="joli-activity-list">
                <li className="joli-activity-item">
                  <div className="joli-activity-avatar">JM</div>
                  <div className="joli-activity-info">
                    <span className="joli-activity-user">Joan Montoya</span>
                    <span className="joli-activity-meta">Doc. 1020405060 &bull; 190.14.85.120</span>
                  </div>
                  <span className="joli-activity-time">Hace 2m</span>
                </li>
                <li className="joli-activity-item">
                  <div className="joli-activity-avatar">OP</div>
                  <div className="joli-activity-info">
                    <span className="joli-activity-user">Operador Báscula</span>
                    <span className="joli-activity-meta">Doc. 1010203040 &bull; 10.0.1.45</span>
                  </div>
                  <span className="joli-activity-time">Hace 14m</span>
                </li>
                <li className="joli-activity-item">
                  <div className="joli-activity-avatar">AD</div>
                  <div className="joli-activity-info">
                    <span className="joli-activity-user">Auditor Calidad</span>
                    <span className="joli-activity-meta">Doc. 71203040 &bull; 10.0.1.52</span>
                  </div>
                  <span className="joli-activity-time">Hace 32m</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
```

---

## 4. Estilos CSS Canónicos (`dashboard.css`)

```css
.joli-dashboard-container {
  padding: var(--space-2) 0;
}

.joli-hero-title {
  font-size: var(--text-2xl);
  font-weight: var(--weight-extrabold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
  letter-spacing: -0.5px;
}

.joli-hero-subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: 0;
}

/* REJILLA RESPONSIVE INTELIGENTE (ESTÁNDAR BI CARTERA) */
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

/* TARJETAS KPI */
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

/* CAJA DE ICONOS CROMÁTICA */
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

.joli-kpi-icon-box.icon-blue { color: #3b82f6; border-color: rgba(59, 130, 246, 0.25); background: rgba(59, 130, 246, 0.08); }
.joli-kpi-icon-box.icon-amber { color: #f59e0b; border-color: rgba(245, 158, 11, 0.25); background: rgba(245, 158, 11, 0.08); }
.joli-kpi-icon-box.icon-pink { color: #f43f5e; border-color: rgba(244, 63, 94, 0.25); background: rgba(244, 63, 94, 0.08); }
.joli-kpi-icon-box.icon-emerald { color: #10b981; border-color: rgba(16, 185, 129, 0.25); background: rgba(16, 185, 129, 0.08); }
.joli-kpi-icon-box.icon-cyan { color: #06b6d4; border-color: rgba(6, 182, 212, 0.25); background: rgba(6, 182, 212, 0.08); }

/* PANELES DE CONTENIDO */
.joli-panel-card {
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.joli-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.joli-panel-title {
  font-size: var(--text-base);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.joli-panel-body {
  padding: var(--space-5);
}

/* LISTA DE ACTIVIDAD */
.joli-activity-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.joli-activity-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-5);
  border-bottom: 1px solid var(--color-border);
  transition: background-color var(--transition-fast);
}

.joli-activity-item:last-child {
  border-bottom: none;
}

.joli-activity-item:hover {
  background-color: var(--color-bg-card-hover);
}

.joli-activity-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background-color: var(--color-bg-input);
  color: var(--color-text-primary);
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
  border-radius: var(--radius-full);
}

.joli-activity-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.joli-activity-user {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
}

.joli-activity-meta {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.joli-activity-time {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}
```
