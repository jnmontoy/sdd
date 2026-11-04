# Especificación de Componente: Calendario Corporativo (`CorporateCalendar`)
## SDD Joli Foods — Spec-Driven Development

> **Origen:** patrón tomado de vibra (novedades y turnos de personal). Aquí se describe de forma genérica.

`CorporateCalendar` muestra una cuadrícula mensual para gestionar visualmente turnos, novedades, permisos, vacaciones e incapacidades. Es un componente de presentación: el filtrado por área/sede y la creación o edición de eventos los hace el contenedor (la edición se abre en el **panel lateral derecho**, no en un modal).

> **Datos sensibles:** una incapacidad médica es información de salud. El calendario DEBERÍA mostrar solo el tipo de novedad ("Incapacidad") y nunca diagnósticos; el backend DEBE limitar quién ve el detalle.

---

### 1. Requisitos técnicos y de negocio

1. **Rejilla mensual**: semanas de lunes a domingo; los días previos al primer día del mes se rellenan con celdas vacías.
2. **Colores por tipo de evento** (tokens de `variables.css`, válidos en ambos temas):
   - `novedad`: azul (`--accent-blue`).
   - `vacacion`: verde (`--status-success`).
   - `incapacidad`: rojo (`--status-error`).
   - `permiso`: ámbar (`--status-warning`).
   - El texto del evento siempre acompaña al color (el color no es el único indicador).
3. **Navegación**: mes anterior (`ChevronLeft`), mes siguiente (`ChevronRight`) y "Hoy".
4. **Interacción**: botón "+" por día para crear (visible al pasar el mouse **o al recibir foco**) y clic en un evento para abrir su detalle.
5. **Fecha de "hoy" en hora local**: se calcula con la fecha local del navegador, no con `toISOString()` (que usa UTC y en Colombia, UTC-5, cambia de día a partir de las 7:00 p. m.).
6. **Rendimiento**: los eventos se agrupan por fecha una sola vez (`useMemo`), no se filtra la lista completa en cada celda.

---

### 2. Implementación React + TypeScript

```tsx
// src/components/ui/CorporateCalendar.tsx
import React, { useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Plus } from 'lucide-react';
import './CorporateCalendar.css';

export type CalendarEventType = 'novedad' | 'vacacion' | 'incapacidad' | 'permiso';

export interface CalendarEvent {
  id: string;
  title: string;
  date: string; // YYYY-MM-DD (fecha local)
  type: CalendarEventType;
  collaboratorName?: string;
}

export interface CorporateCalendarProps {
  events: CalendarEvent[];
  onDateClick?: (dateStr: string) => void;
  onEventClick?: (event: CalendarEvent) => void;
  maxEventsPerDay?: number;
}

const MONTH_NAMES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
const DAYS_OF_WEEK = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

/** YYYY-MM-DD con la fecha LOCAL (no UTC). */
function toLocalDateStr(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

type DayCell = { kind: 'empty'; key: string } | { kind: 'day'; key: string; dayNumber: number; dateStr: string };

export const CorporateCalendar: React.FC<CorporateCalendarProps> = ({
  events,
  onDateClick,
  onEventClick,
  maxEventsPerDay = 3,
}) => {
  const [currentDate, setCurrentDate] = useState(() => new Date());
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const todayStr = toLocalDateStr(new Date());

  const eventsByDate = useMemo(() => {
    const map = new Map<string, CalendarEvent[]>();
    for (const ev of events) {
      const list = map.get(ev.date);
      if (list) list.push(ev);
      else map.set(ev.date, [ev]);
    }
    return map;
  }, [events]);

  const cells = useMemo<DayCell[]>(() => {
    const firstDayIndex = (new Date(year, month, 1).getDay() + 6) % 7; // lunes = 0
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const result: DayCell[] = [];
    for (let i = 0; i < firstDayIndex; i++) result.push({ kind: 'empty', key: `empty-${i}` });
    for (let d = 1; d <= daysInMonth; d++) {
      const dateStr = toLocalDateStr(new Date(year, month, d));
      result.push({ kind: 'day', key: dateStr, dayNumber: d, dateStr });
    }
    return result;
  }, [year, month]);

  const monthLabel = `${MONTH_NAMES[month]} ${year}`;

  return (
    <section className="corp-calendar-card" aria-label={`Calendario de ${monthLabel}`}>
      <div className="corp-cal-header">
        <div className="corp-cal-title-box">
          <CalendarIcon className="corp-cal-title-icon" size={22} aria-hidden="true" />
          <h2 className="corp-cal-title" aria-live="polite">{monthLabel}</h2>
        </div>
        <div className="btn-group btn-group-sm corp-cal-nav-actions" role="group" aria-label="Navegación del calendario">
          <button type="button" className="corp-cal-nav-btn" onClick={() => setCurrentDate(new Date(year, month - 1, 1))} aria-label="Mes anterior" title="Mes anterior">
            <ChevronLeft size={18} aria-hidden="true" />
          </button>
          <button type="button" className="corp-cal-nav-btn corp-cal-btn-today" onClick={() => setCurrentDate(new Date())}>
            Hoy
          </button>
          <button type="button" className="corp-cal-nav-btn" onClick={() => setCurrentDate(new Date(year, month + 1, 1))} aria-label="Mes siguiente" title="Mes siguiente">
            <ChevronRight size={18} aria-hidden="true" />
          </button>
        </div>
      </div>

      <div className="corp-cal-weekdays" aria-hidden="true">
        {DAYS_OF_WEEK.map((dow) => (
          <div key={dow} className="corp-cal-weekday-label">{dow}</div>
        ))}
      </div>

      <div className="corp-cal-grid">
        {cells.map((cell) => {
          if (cell.kind === 'empty') {
            return <div key={cell.key} className="corp-cal-day corp-cal-day-empty" aria-hidden="true" />;
          }
          const dayEvents = eventsByDate.get(cell.dateStr) ?? [];
          const isToday = cell.dateStr === todayStr;
          const hidden = dayEvents.length - maxEventsPerDay;

          return (
            <div key={cell.key} className={`corp-cal-day ${isToday ? 'corp-cal-day-today' : ''}`} aria-current={isToday ? 'date' : undefined}>
              <div className="corp-cal-day-header">
                <span className="corp-cal-day-num">{cell.dayNumber}</span>
                {onDateClick && (
                  <button
                    type="button"
                    className="corp-cal-day-add"
                    title="Añadir novedad"
                    aria-label={`Añadir novedad el ${cell.dayNumber} de ${MONTH_NAMES[month]}`}
                    onClick={() => onDateClick(cell.dateStr)}
                  >
                    <Plus size={12} aria-hidden="true" />
                  </button>
                )}
              </div>

              <div className="corp-cal-events-list">
                {dayEvents.slice(0, maxEventsPerDay).map((ev) => (
                  <button
                    key={ev.id}
                    type="button"
                    className={`corp-cal-badge badge-${ev.type}`}
                    onClick={() => onEventClick?.(ev)}
                    title={ev.collaboratorName ? `${ev.title} — ${ev.collaboratorName}` : ev.title}
                  >
                    <span className="corp-cal-badge-dot" aria-hidden="true" />
                    <span className="corp-cal-badge-title">{ev.title}</span>
                  </button>
                ))}
                {hidden > 0 && <span className="corp-cal-more-tag">+{hidden} más</span>}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
```

---

### 3. Estilos CSS (`CorporateCalendar.css`)

```css
.corp-calendar-card {
  width: 100%;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 1.5rem;
  box-shadow: var(--shadow-card);
}

.corp-cal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.corp-cal-title-box {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.corp-cal-title-icon {
  color: var(--brand-primary);
}

.corp-cal-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin: 0;
}

.corp-cal-nav-btn {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  padding: 0.35rem 0.5rem;
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
}

.corp-cal-nav-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.corp-cal-btn-today {
  padding: 0.35rem 0.75rem;
}

.corp-cal-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  margin-bottom: 0.5rem;
  text-align: center;
}

.corp-cal-weekday-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--text-muted);
  text-transform: uppercase;
  padding: 0.5rem 0;
}

.corp-cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
}

.corp-cal-day {
  min-height: 100px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  transition: background var(--transition-fast), border-color var(--transition-fast);
}

.corp-cal-day:hover {
  background: var(--bg-hover);
  border-color: var(--border-strong);
}

.corp-cal-day-empty,
.corp-cal-day-empty:hover {
  background: transparent;
  border: 1px dashed transparent;
}

.corp-cal-day-today {
  border-color: var(--brand-primary);
  background: color-mix(in srgb, var(--brand-primary) 6%, var(--bg-elevated));
}

.corp-cal-day-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.35rem;
}

.corp-cal-day-num {
  font-size: 0.8rem;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.corp-cal-day-today .corp-cal-day-num {
  background: var(--brand-primary);
  color: var(--text-on-brand);
  border-radius: var(--radius-full);
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.corp-cal-day-add {
  background: transparent;
  border: none;
  color: var(--text-muted);
  opacity: 0;
  cursor: pointer;
  padding: 2px;
  border-radius: var(--radius-sm);
}

/* Visible con mouse y con teclado */
.corp-cal-day:hover .corp-cal-day-add,
.corp-cal-day-add:focus-visible {
  opacity: 1;
}

.corp-cal-day-add:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
}

.corp-cal-events-list {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}

.corp-cal-badge {
  --ev: var(--accent-blue);
  display: flex;
  align-items: center;
  gap: 4px;
  border: none;
  border-radius: var(--radius-sm);
  padding: 2px 6px;
  font-size: 0.7rem;
  font-weight: var(--font-weight-semibold);
  text-align: left;
  cursor: pointer;
  overflow: hidden;
  white-space: nowrap;
  color: var(--text-primary);
  background: color-mix(in srgb, var(--ev) 16%, transparent);
}

.corp-cal-badge-title {
  overflow: hidden;
  text-overflow: ellipsis;
}

.corp-cal-badge-dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
  background: var(--ev);
}

.badge-novedad     { --ev: var(--accent-blue); }
.badge-vacacion    { --ev: var(--status-success); }
.badge-incapacidad { --ev: var(--status-error); }
.badge-permiso     { --ev: var(--status-warning); }

.corp-cal-more-tag {
  font-size: 0.65rem;
  color: var(--text-muted);
  font-weight: var(--font-weight-semibold);
  margin-top: 1px;
}
```
