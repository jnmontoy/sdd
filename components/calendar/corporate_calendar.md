# Especificación de Componente: Calendario Corporativo (`CorporateCalendar`)
## Ecosistema Jolifoods — Metodología Spec-Driven Development (SDD)

El componente `CorporateCalendar` ofrece una cuadrícula mensual y agenda interactiva para la gestión visual de turnos operativos, novedades, permisos, vacaciones e incapacidades médicas. Incluye soporte para badges de severidad cromática, filtrado por área/sede y modal de creación/edición de eventos.

> **Origen y validación en producción**: Extraído y simplificado a partir del módulo de novedades y turnos de personal en `vibra`.

---

### 1. Requisitos Técnicos y de Negocio

1. **Rejilla Mensual Inteligente**: Cálculo reactivo de días del mes anterior y siguiente para rellenar las 5 a 6 semanas de la vista mensual.
2. **Badges por Tipo de Evento**:
   - `novedad`: Azul corporativo (`bg-blue-50 text-blue-700`).
   - `vacacion`: Verde esmeralda (`bg-emerald-50 text-emerald-700`).
   - `incapacidad`: Rojo rubí (`bg-rose-50 text-rose-700`).
   - `permiso`: Ámbar cálido (`bg-amber-50 text-amber-700`).
3. **Navegación Fluida**: Botones Mes Anterior (`ChevronLeft`), Mes Siguiente (`ChevronRight`) y selector rápido "Hoy".
4. **Interactividad**: Clic en cualquier celda de fecha para añadir novedad o en un evento para abrir su detalle.

---

### 2. Implementación TypeScript / React

```tsx
// src/components/ui/CorporateCalendar.tsx
import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Plus } from 'lucide-react';
import './CorporateCalendar.css';

export interface CalendarEvent {
  id: string;
  title: string;
  date: string; // Formato YYYY-MM-DD
  type: 'novedad' | 'vacacion' | 'incapacidad' | 'permiso';
  collaboratorName?: string;
}

export interface CorporateCalendarProps {
  events: CalendarEvent[];
  onDateClick?: (dateStr: string) => void;
  onEventClick?: (event: CalendarEvent) => void;
}

export const CorporateCalendar: React.FC<CorporateCalendarProps> = ({
  events,
  onDateClick,
  onEventClick,
}) => {
  const [currentDate, setCurrentDate] = useState(new Date());

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const monthNames = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  const daysOfWeek = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

  const prevMonth = () => setCurrentDate(new Date(year, month - 1, 1));
  const nextMonth = () => setCurrentDate(new Date(year, month + 1, 1));
  const goToToday = () => setCurrentDate(new Date());

  // Cálculo de días del mes
  const firstDayIndex = (new Date(year, month, 1).getDay() + 6) % 7; // Lunes = 0
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const days = [];
  for (let i = 0; i < firstDayIndex; i++) {
    days.push({ dayNumber: '', dateStr: '', isCurrentMonth: false });
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const dStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    days.push({ dayNumber: d, dateStr: dStr, isCurrentMonth: true });
  }

  const todayStr = new Date().toISOString().split('T')[0];

  return (
    <div className="corp-calendar-card">
      {/* Cabecera del Calendario */}
      <div className="corp-cal-header">
        <div className="corp-cal-title-box">
          <CalendarIcon className="text-emerald-600" size={22} />
          <h2 className="corp-cal-title">{monthNames[month]} {year}</h2>
        </div>
        <div className="corp-cal-nav-actions">
          <button type="button" className="corp-cal-btn-today" onClick={goToToday}>
            Hoy
          </button>
          <button type="button" className="corp-cal-nav-btn" onClick={prevMonth} aria-label="Mes anterior">
            <ChevronLeft size={18} />
          </button>
          <button type="button" className="corp-cal-nav-btn" onClick={nextMonth} aria-label="Mes siguiente">
            <ChevronRight size={18} />
          </button>
        </div>
      </div>

      {/* Días de la Semana */}
      <div className="corp-cal-weekdays">
        {daysOfWeek.map((dow) => (
          <div key={dow} className="corp-cal-weekday-label">{dow}</div>
        ))}
      </div>

      {/* Rejilla de Días */}
      <div className="corp-cal-grid">
        {days.map((item, idx) => {
          if (!item.isCurrentMonth) {
            return <div key={`empty-${idx}`} className="corp-cal-day corp-cal-day-empty" />;
          }

          const dayEvents = events.filter((ev) => ev.date === item.dateStr);
          const isToday = item.dateStr === todayStr;

          return (
            <div
              key={item.dateStr}
              className={`corp-cal-day ${isToday ? 'corp-cal-day-today' : ''}`}
              onClick={() => onDateClick?.(item.dateStr)}
            >
              <div className="corp-cal-day-header">
                <span className="corp-cal-day-num">{item.dayNumber}</span>
                <button
                  type="button"
                  className="corp-cal-day-add"
                  title="Añadir evento"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDateClick?.(item.dateStr);
                  }}
                >
                  <Plus size={12} />
                </button>
              </div>

              <div className="corp-cal-events-list">
                {dayEvents.slice(0, 3).map((ev) => (
                  <button
                    key={ev.id}
                    type="button"
                    className={`corp-cal-badge badge-${ev.type}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      onEventClick?.(ev);
                    }}
                    title={`${ev.title} - ${ev.collaboratorName || ''}`}
                  >
                    <span className="corp-cal-badge-dot" />
                    <span className="corp-cal-badge-title">{ev.title}</span>
                  </button>
                ))}
                {dayEvents.length > 3 && (
                  <span className="corp-cal-more-tag">+{dayEvents.length - 3} más</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
```

---

### 3. Estilos CSS (`CorporateCalendar.css`)

```css
.corp-calendar-card {
  background: var(--bg-card, #FFFFFF);
  border: 1px solid var(--border-subtle, #E2E8F0);
  border-radius: var(--radius-xl, 14px);
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
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

.corp-cal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary, #0F172A);
  margin: 0;
}

.corp-cal-nav-actions {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.corp-cal-btn-today {
  background: var(--bg-surface, #F1F5F9);
  border: 1px solid var(--border-subtle, #E2E8F0);
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary, #475569);
  cursor: pointer;
}

.corp-cal-nav-btn {
  background: var(--bg-surface, #F1F5F9);
  border: 1px solid var(--border-subtle, #E2E8F0);
  padding: 0.35rem 0.5rem;
  border-radius: 6px;
  color: var(--text-secondary, #475569);
  cursor: pointer;
}

.corp-cal-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  margin-bottom: 0.5rem;
  text-align: center;
}

.corp-cal-weekday-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted, #64748B);
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
  background: var(--bg-surface, #F8FAFC);
  border: 1px solid var(--border-subtle, #E2E8F0);
  border-radius: 8px;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  transition: all 0.15s ease;
  cursor: pointer;
}

.corp-cal-day:hover {
  background: #F1F5F9;
  border-color: #CBD5E1;
}

.corp-cal-day-empty {
  background: transparent;
  border: 1px dashed transparent;
  cursor: default;
}

.corp-cal-day-today {
  border-color: var(--color-primary, #10B981);
  background: rgba(16, 185, 129, 0.04);
}

.corp-cal-day-today .corp-cal-day-num {
  background: var(--color-primary, #10B981);
  color: #FFFFFF;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.corp-cal-day-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.35rem;
}

.corp-cal-day-num {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-primary, #1E293B);
}

.corp-cal-day-add {
  background: transparent;
  border: none;
  opacity: 0;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
}

.corp-cal-day:hover .corp-cal-day-add {
  opacity: 0.6;
}

.corp-cal-events-list {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}

.corp-cal-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  border: none;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 0.7rem;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.corp-cal-badge-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  flex-shrink: 0;
}

.badge-novedad { background: #EFF6FF; color: #1D4ED8; }
.badge-novedad .corp-cal-badge-dot { background: #2563EB; }

.badge-vacacion { background: #ECFDF5; color: #047857; }
.badge-vacacion .corp-cal-badge-dot { background: #10B981; }

.badge-incapacidad { background: #FFF1F2; color: #BE123C; }
.badge-incapacidad .corp-cal-badge-dot { background: #F43F5E; }

.badge-permiso { background: #FFFBEB; color: #B45309; }
.badge-permiso .corp-cal-badge-dot { background: #F59E0B; }

.corp-cal-more-tag {
  font-size: 0.65rem;
  color: var(--text-muted, #64748B);
  font-weight: 600;
  margin-top: 1px;
}
```
