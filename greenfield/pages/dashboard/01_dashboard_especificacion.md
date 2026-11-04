# 01. Especificación del Tablero Principal (Dashboard Operativo)
## Joli Foods — Spec-Driven Development (SDD)

Vista de inicio que ve el colaborador tras autenticarse, dentro del [Layout Maestro](../layout/01_layout_maestro_especificacion.md). Muestra indicadores clave (KPI), un panel de actividad y los últimos accesos. Ocupa el 100% del ancho del área de contenido (DEBERÍA, ver regla de ancho del layout).

> **Origen:** patrón tomado de bi (tablero de cartera: KPI clicables como filtro). Aquí se describe de forma genérica.

---

## 1. Topología

```
+------------------------------------------------------------------------------------------------+
|  Bienvenido, <nombre>                                                                           |
|  <Nombre del proyecto> • <sede> • <fecha>                                                       |
+------------------------------------------------------------------------------------------------+
|  [ Accesos hoy ]   [ Sesiones activas* ]   [ Alertas de seguridad* ]   [ Estado del servicio ]  |
+------------------------------------------------------------------------------------------------+
|  Actividad por hora (gráfico)                 |  Últimos inicios de sesión                      |
|                                               |  - Usuario Ejemplo (•••••0001) • hace 2 min     |
+------------------------------------------------------------------------------------------------+
  * KPI clicables: filtran la lista de últimos accesos.
```

---

## 2. Datos

| Bloque | Fuente (`ENDPOINTS`) | Permiso requerido |
| :--- | :--- | :--- |
| KPI de accesos, sesiones y alertas | `ENDPOINTS.FAST.METRICAS_KPI` (`GET /fast/v1/metricas/kpi`) | `dashboard.ver` |
| Estado del servicio | `ENDPOINTS.HEALTH.READY` (`GET /health/ready`, 200 = disponible, 503 = degradado) | público |
| Últimos inicios de sesión | `GET /api/v1/auditoria/accesos/?limit=5` | `auditoria.ver` (si no lo tiene, el panel no se muestra) |

Respuesta de ejemplo de `/fast/v1/metricas/kpi`:
```json
{ "accesos_hoy": 128, "sesiones_activas": 42, "alertas_seguridad": 3 }
```

En la lista de accesos el documento se muestra **enmascarado** (últimos 4 dígitos) y no se muestra la IP. **Por qué:** el tablero lo ven muchos perfiles; el detalle completo está en la bitácora, protegida por permiso.

Los KPI se cargan con esqueleto (`loading`) y las peticiones se cancelan al desmontar (`AbortController`).

---

## 3. Implementación (`DashboardPage.tsx`)

Usa el componente [`KPIRow`](../../../components/kpi/kpi_cards.md) (sus estilos ya están definidos ahí; no se duplican).

```tsx
import { useEffect, useMemo, useState } from 'react';
import { Users, Activity, AlertCircle, ShieldCheck, Clock, TrendingUp } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { apiClient } from '../services/apiClient';
import { ENDPOINTS } from '../services/endpoints';
import { KPIRow, type KPICardItem } from '../components/kpi/KPICards';
import './dashboard.css';

interface KpiResumen { accesos_hoy: number; sesiones_activas: number; alertas_seguridad: number }
interface AccesoReciente {
  id: number;
  nombre: string;
  documento_enmascarado: string;
  evento: string;
  resultado: 'SUCCESS' | 'FAILURE' | 'BLOCKED';
  fecha_evento: string;
}
type FiltroAccesos = 'todos' | 'exitosos' | 'alertas';

const formatoNumero = new Intl.NumberFormat('es-CO');
const formatoRelativo = new Intl.RelativeTimeFormat('es', { numeric: 'auto' });

function haceCuanto(iso: string): string {
  const minutos = Math.round((new Date(iso).getTime() - Date.now()) / 60000);
  return Math.abs(minutos) < 60
    ? formatoRelativo.format(minutos, 'minute')
    : formatoRelativo.format(Math.round(minutos / 60), 'hour');
}

function iniciales(nombre: string): string {
  return nombre.split(' ').filter(Boolean).slice(0, 2).map((p) => p[0]).join('').toUpperCase();
}

export function DashboardPage() {
  const { user, hasPermission } = useAuth();
  const puedeVerAuditoria = hasPermission('auditoria.ver');
  const [kpi, setKpi] = useState<KpiResumen | null>(null);
  const [servicioListo, setServicioListo] = useState<boolean | null>(null);
  const [accesos, setAccesos] = useState<AccesoReciente[]>([]);
  const [filtro, setFiltro] = useState<FiltroAccesos>('todos');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const { signal } = controller;

    apiClient
      .get<KpiResumen>(ENDPOINTS.FAST.METRICAS_KPI, { signal })
      .then((r) => setKpi(r.data))
      .catch(() => { if (!signal.aborted) setError('No fue posible cargar los indicadores.'); });

    apiClient
      .get(ENDPOINTS.HEALTH.READY, { signal, validateStatus: () => true })
      .then((r) => setServicioListo(r.status === 200))
      .catch(() => { if (!signal.aborted) setServicioListo(false); });

    if (puedeVerAuditoria) {
      apiClient
        .get<AccesoReciente[]>(`${ENDPOINTS.AUDITORIA.ACCESOS}?limit=5`, { signal })
        .then((r) => setAccesos(r.data))
        .catch(() => { /* el panel muestra estado vacío */ });
    }

    return () => controller.abort();
  }, [puedeVerAuditoria]);

  const fechaHoy = useMemo(
    () => new Date().toLocaleDateString('es-CO', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }),
    []
  );

  const alternarFiltro = (siguiente: FiltroAccesos) => setFiltro((actual) => (actual === siguiente ? 'todos' : siguiente));

  const items: KPICardItem[] = kpi
    ? [
        { id: 'kpi-accesos', label: 'Accesos hoy', value: formatoNumero.format(kpi.accesos_hoy),
          icon: <Users size={20} />, iconColorClass: 'icon-blue' },
        { id: 'kpi-sesiones', label: 'Sesiones activas', value: formatoNumero.format(kpi.sesiones_activas),
          subtext: 'Ver solo accesos exitosos', icon: <Activity size={20} />, iconColorClass: 'icon-emerald',
          isClickable: puedeVerAuditoria, isActiveFilter: filtro === 'exitosos', onClick: () => alternarFiltro('exitosos') },
        { id: 'kpi-alertas', label: 'Alertas de seguridad', value: formatoNumero.format(kpi.alertas_seguridad),
          subtext: 'Intentos fallidos o bloqueados', icon: <AlertCircle size={20} />, iconColorClass: 'icon-pink',
          isClickable: puedeVerAuditoria, isActiveFilter: filtro === 'alertas', onClick: () => alternarFiltro('alertas') },
        { id: 'kpi-servicio', label: 'Estado del servicio',
          value: servicioListo === null ? '—' : servicioListo ? 'Disponible' : 'Degradado',
          subtext: 'Base de datos y caché', icon: <ShieldCheck size={20} />, iconColorClass: servicioListo === false ? 'icon-amber' : 'icon-cyan' },
      ]
    : [];

  const accesosFiltrados = accesos.filter((a) =>
    filtro === 'todos' ? true : filtro === 'exitosos' ? a.resultado === 'SUCCESS' : a.resultado !== 'SUCCESS'
  );

  return (
    <div className="joli-dashboard">
      <section className="joli-dashboard-hero">
        <h1 className="joli-dashboard-title">Bienvenido, {user?.nombre ?? 'colaborador'}</h1>
        <p className="joli-dashboard-subtitle">
          {import.meta.env.VITE_APP_NAME ?? 'Aplicación'} &bull; <span className="text-capitalize">{fechaHoy}</span>
        </p>
      </section>

      {error && <div className="alert alert-warning" role="alert">{error}</div>}

      <KPIRow items={items} loading={kpi === null && error === null} />

      <div className="row g-4">
        <div className={puedeVerAuditoria ? 'col-12 col-xl-8' : 'col-12'}>
          <section className="joli-panel-card h-100" aria-labelledby="panel-actividad">
            <header className="joli-panel-header">
              <h2 id="panel-actividad" className="joli-panel-title">Actividad por hora</h2>
            </header>
            <div className="joli-panel-body joli-panel-body--chart">
              {/* Reemplazar por el gráfico de .sdd/components/charts/ con datos de /fast/v1/telemetria/resumen */}
              <TrendingUp size={40} aria-hidden="true" />
              <p className="mb-0">Gráfico de actividad</p>
            </div>
          </section>
        </div>

        {puedeVerAuditoria && (
          <div className="col-12 col-xl-4">
            <section className="joli-panel-card h-100" aria-labelledby="panel-accesos">
              <header className="joli-panel-header">
                <h2 id="panel-accesos" className="joli-panel-title">Últimos inicios de sesión</h2>
                <Clock size={18} aria-hidden="true" />
              </header>
              {accesosFiltrados.length === 0 ? (
                <p className="joli-panel-body mb-0">Sin registros para el filtro seleccionado.</p>
              ) : (
                <ul className="joli-activity-list">
                  {accesosFiltrados.map((a) => (
                    <li key={a.id} className="joli-activity-item">
                      <span className="joli-activity-avatar" aria-hidden="true">{iniciales(a.nombre)}</span>
                      <span className="joli-activity-info">
                        <span className="joli-activity-user">{a.nombre}</span>
                        <span className="joli-activity-meta">Doc. {a.documento_enmascarado} &bull; {a.evento}</span>
                      </span>
                      <time className="joli-activity-time" dateTime={a.fecha_evento}>{haceCuanto(a.fecha_evento)}</time>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </div>
        )}
      </div>
    </div>
  );
}
```

`ENDPOINTS.AUDITORIA.ACCESOS` (`/api/v1/auditoria/accesos/`) DEBE agregarse al registro de endpoints si el proyecto no lo tiene.

---

## 4. Estilos (`dashboard.css`)

Solo tokens de [`variables.css`](../../../components/variables.css). Los estilos de KPI están en `kpi_cards.md`.

```css
.joli-dashboard { width: 100%; }

.joli-dashboard-hero { margin-bottom: var(--space-6); }
.joli-dashboard-title {
  margin: 0 0 var(--space-1);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-extrabold);
  color: var(--text-primary);
}
.joli-dashboard-subtitle { margin: 0; font-size: var(--font-size-sm); color: var(--text-secondary); }

.joli-panel-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}
.joli-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-muted);
}
.joli-panel-title { margin: 0; font-size: var(--font-size-base); font-weight: var(--font-weight-bold); color: var(--text-primary); }
.joli-panel-body { padding: var(--space-5); color: var(--text-secondary); }
.joli-panel-body--chart {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: var(--space-2); min-height: 260px; color: var(--text-muted);
}

.joli-activity-list { list-style: none; margin: 0; padding: 0; }
.joli-activity-item {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-3) var(--space-5);
  border-bottom: 1px solid var(--border-subtle);
}
.joli-activity-item:last-child { border-bottom: none; }
.joli-activity-item:hover { background-color: var(--bg-hover); }
.joli-activity-avatar {
  display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;
  width: 36px; height: 36px; border-radius: var(--radius-full);
  background-color: var(--bg-elevated); color: var(--text-primary);
  font-size: var(--font-size-xs); font-weight: var(--font-weight-bold);
}
.joli-activity-info { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.joli-activity-user { font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold); color: var(--text-primary); }
.joli-activity-meta, .joli-activity-time { font-size: var(--font-size-xs); color: var(--text-muted); }
```
