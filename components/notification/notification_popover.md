# Componente Maestro: Panel Desplegable de Multi-Notificaciones (NotificationPopover)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)
### Referencia Canónica: Implementaciones de Producción en `tiendita` y `vibra`

El **NotificationPopover** (o Dropdown de Notificaciones) es el componente oficial de interfaz que se despliega al presionar el botón de la campana (`Bell`) en el **TopHeader**. 

Permite gestionar múltiples flujos de alertas operativas, pedidos, solicitudes o alertas de inventario agrupadas mediante un **control por pestañas (tabs)**, indicando conteos dinámicos en badges y permitiendo acciones rápidas en línea (como aprobar, ver detalle o marcar como leída).

---

## 1. Características Arquitectónicas Clave

1. **Activador en TopHeader**: Botón circular con icono `Bell` y badge pulsante (`.bell-badge-count`) con la sumatoria de elementos no leídos / críticos.
2. **Pestañas de Filtrado Multi-Categoría (`.notif-tabs` / `.notification-toggle-tabs`)**:
   - Permite alternar entre diferentes tipos de notificaciones (ej: *Solicitudes*, *Stock Crítico*, *Novedades*, *Sistema*).
   - Cada pestaña muestra su propio contador numérico dinámico.
3. **Lista Scrollable de Notificaciones (`.notif-list`)**:
   - Scroll vertical independiente con altura máxima (`max-height: 380px`).
   - Estados de lectura (`.unread` con borde de acento sutil).
   - Icono contextual / avatar con halo cromático según severidad (crítico/rojo, advertencia/ámbar, info/azul, éxito/verde).
   - Tiempo relativo de antigüedad (*"Hace 15 min"*, *"Hoy, 09:30 AM"*).
4. **Acciones Rápidas por Notificación**:
   - Botón de aprobación / confirmación rápida (`CheckCircle`).
   - Botón de rechazo o descarte (`XCircle`).
   - Botón de inspección para abrir el registro en el **Right Drawer** (`Eye`).
5. **Estado Óptimo / Vacío (`.notif-empty` / `.notification-ok-state`)**:
   - Cuando no hay alertas pendientes en la pestaña activa, muestra un icono `CheckCircle` verde con mensaje tranquilizador (*"Todo al día / No hay alertas pendientes"*).
6. **Pie Fijo (`.notif-footer`)**:
   - Opciones para *"Marcar todas como leídas"* o enlace de navegación a la vista de auditoría.
7. **Cierre Automático**:
   - Se cierra al presionar la tecla `Escape` o al hacer clic fuera del panel (*Click Outside Listener*).

---

## 2. Contrato de Datos e Interfaz TypeScript

```typescript
export type NotificationSeverity = 'critical' | 'warning' | 'info' | 'success';

export interface NotificationAction {
  label: string;
  type: 'approve' | 'deny' | 'view';
  icon?: string;
  onClick: (notifId: string | number) => void;
}

export interface NotificationItem {
  id: string | number;
  category: string; // ej. 'stock', 'solicitudes', 'alertas'
  title: string;
  detail: string;
  timestamp: string;
  timeAgo: string;
  severity: NotificationSeverity;
  isRead: boolean;
  avatarText?: string;
  actions?: NotificationAction[];
  metadata?: Record<string, any>;
}

export interface NotificationCategoryTab {
  id: string;
  label: string;
  icon?: string;
}

export interface NotificationPopoverProps {
  isOpen: boolean;
  onClose: () => void;
  categories: NotificationCategoryTab[];
  activeCategoryId: string;
  onCategoryChange: (categoryId: string) => void;
  notifications: NotificationItem[];
  onAction?: (notifId: string | number, actionType: 'approve' | 'deny' | 'view') => void;
  onMarkAllAsRead?: () => void;
  onViewAll?: () => void;
}
```

---

## 3. Código JSX / React 19 Canónico (`NotificationPopover.tsx`)

```tsx
import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Bell, 
  CheckCircle, 
  XCircle, 
  Eye, 
  AlertTriangle, 
  Info, 
  CheckCheck,
  PackageX,
  ExternalLink 
} from 'lucide-react';
import './NotificationPopover.css';

export const NotificationBellPopover: React.FC<{
  notifications: NotificationItem[];
  categories: { id: string; label: string }[];
  onActionClick?: (notif: NotificationItem, action: 'approve' | 'deny' | 'view') => void;
}> = ({ notifications, categories, onActionClick }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(categories[0]?.id || 'todas');
  const containerRef = useRef<HTMLDivElement>(null);

  // Conteo total de pendientes no leídas
  const unreadCount = useMemo(() => {
    return notifications.filter(n => !n.isRead).length;
  }, [notifications]);

  // Filtrado por categoría activa
  const filteredNotifications = useMemo(() => {
    if (activeTab === 'todas') return notifications;
    return notifications.filter(n => n.category === activeTab);
  }, [notifications, activeTab]);

  // Conteo por cada tab
  const getTabCount = (catId: string) => {
    if (catId === 'todas') return unreadCount;
    return notifications.filter(n => n.category === catId && !n.isRead).length;
  };

  // Cierre por Click Outside y tecla Escape
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  return (
    <div className="joli-notification-wrapper" ref={containerRef}>
      {/* Botón de la Campanita en TopHeader */}
      <button 
        type="button" 
        className={`joli-bell-btn ${isOpen ? 'active' : ''} ${unreadCount > 0 ? 'has-unread' : ''}`}
        onClick={() => setIsOpen(prev => !prev)}
        title="Centro de Alertas y Notificaciones"
        aria-label="Notificaciones"
      >
        <Bell size={18} />
        {unreadCount > 0 && (
          <span className="bell-badge-count">{unreadCount > 99 ? '99+' : unreadCount}</span>
        )}
      </button>

      {/* Popover Desplegable */}
      {isOpen && (
        <div className="joli-notification-popover fade-in">
          {/* Cabecera */}
          <div className="joli-notif-header">
            <div className="joli-notif-title-row">
              <span className="joli-notif-title">Centro de Notificaciones</span>
              {unreadCount > 0 && (
                <span className="joli-notif-counter-pill">{unreadCount} pendientes</span>
              )}
            </div>

            {/* Pestañas de Categoría (Multi-Notificaciones) */}
            <div className="joli-notif-tabs">
              {categories.map(cat => {
                const count = getTabCount(cat.id);
                return (
                  <button
                    key={cat.id}
                    type="button"
                    className={`joli-notif-tab-btn ${activeTab === cat.id ? 'active' : ''}`}
                    onClick={() => setActiveTab(cat.id)}
                  >
                    <span>{cat.label}</span>
                    {count > 0 && <span className="joli-tab-badge">{count}</span>}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Lista de Notificaciones */}
          <div className="joli-notif-body">
            {filteredNotifications.length === 0 ? (
              <div className="joli-notif-empty-state">
                <CheckCircle size={32} className="joli-empty-icon-ok" />
                <p className="joli-empty-title">Todo está al día</p>
                <span className="joli-empty-desc">No tienes notificaciones pendientes en esta categoría.</span>
              </div>
            ) : (
              <div className="joli-notif-list">
                {filteredNotifications.map(item => (
                  <div key={item.id} className={`joli-notif-item ${item.isRead ? 'read' : 'unread'}`}>
                    {/* Icono de Severidad */}
                    <div className={`joli-notif-icon-box severity-${item.severity}`}>
                      {item.severity === 'critical' && <PackageX size={16} />}
                      {item.severity === 'warning' && <AlertTriangle size={16} />}
                      {item.severity === 'info' && <Info size={16} />}
                      {item.severity === 'success' && <CheckCircle size={16} />}
                    </div>

                    {/* Contenido */}
                    <div className="joli-notif-content">
                      <div className="joli-notif-topline">
                        <span className="joli-notif-item-title">{item.title}</span>
                        <span className="joli-notif-time">{item.timeAgo}</span>
                      </div>
                      <p className="joli-notif-detail">{item.detail}</p>
                    </div>

                    {/* Acciones Rápidas */}
                    <div className="joli-notif-actions">
                      <button 
                        type="button" 
                        className="joli-notif-action-btn btn-view" 
                        title="Ver en detalle"
                        onClick={() => onActionClick?.(item, 'view')}
                      >
                        <Eye size={14} />
                      </button>
                      <button 
                        type="button" 
                        className="joli-notif-action-btn btn-approve" 
                        title="Aprobar / Confirmar"
                        onClick={() => onActionClick?.(item, 'approve')}
                      >
                        <CheckCircle size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Pie */}
          <div className="joli-notif-footer">
            <button 
              type="button" 
              className="joli-notif-link-btn"
              onClick={() => setIsOpen(false)}
            >
              <CheckCheck size={14} />
              <span>Cerrar</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
```

---

## 4. Estilos CSS Canónicos (`NotificationPopover.css`)

```css
/* ==========================================================================
   NOTIFICATION POPOVER — ESTÁNDAR JOLIFOODS (TIENDITA / VIBRA)
   ========================================================================== */

.joli-notification-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}

/* Botón Circular de la Campanita */
.joli-bell-btn {
  position: relative;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--surface-card, #14142b);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.09));
  color: var(--text-secondary, rgba(255, 255, 255, 0.8));
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.18s ease;
  padding: 0;
}

.joli-bell-btn:hover,
.joli-bell-btn.active {
  background: var(--surface-active, #2b2b55);
  color: #ffffff;
  border-color: rgba(16, 185, 129, 0.5);
}

.joli-bell-btn.has-unread {
  color: #f59e0b;
  border-color: rgba(245, 158, 11, 0.4);
}

/* Insignia Roja Pulsante Circular */
.bell-badge-count {
  position: absolute;
  top: -3px;
  right: -3px;
  width: 18px;
  height: 18px;
  min-width: 18px;
  border-radius: 50%;
  background: #ef4444;
  color: #ffffff;
  font-size: 10px;
  font-weight: 800;
  display: grid;
  place-items: center;
  border: 2px solid var(--background, #16162a);
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.5);
  line-height: 1;
  animation: notifPulse 2.5s infinite ease-in-out;
}

@keyframes notifPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

/* Contenedor Flotante Popover */
.joli-notification-popover {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  width: 380px;
  max-width: calc(100vw - 32px);
  background: var(--surface-card, #14142b);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.12));
  border-radius: 16px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(16px);
  z-index: 1050;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: notifFadeSlide 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes notifFadeSlide {
  from {
    opacity: 0;
    transform: translateY(-8px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Cabecera y Tabs */
.joli-notif-header {
  padding: 14px 16px 10px;
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.08));
  background: rgba(0, 0, 0, 0.15);
}

.joli-notif-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.joli-notif-title {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-primary, #ffffff);
}

.joli-notif-counter-pill {
  font-size: 10.5px;
  font-weight: 700;
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 2px 8px;
  border-radius: 999px;
}

/* Segmented Tabs Control */
.joli-notif-tabs {
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.06));
  border-radius: 10px;
  padding: 3px;
  gap: 3px;
}

.joli-notif-tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 6px 10px;
  border-radius: 7px;
  background: transparent;
  border: none;
  color: var(--text-muted, rgba(255, 255, 255, 0.6));
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.joli-notif-tab-btn:hover {
  color: var(--text-primary, #ffffff);
  background: rgba(255, 255, 255, 0.04);
}

.joli-notif-tab-btn.active {
  background: var(--surface-active, #2b2b55);
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.joli-tab-badge {
  font-size: 9.5px;
  background: #ef4444;
  color: #ffffff;
  padding: 1px 5px;
  border-radius: 8px;
  font-weight: 800;
}

/* Cuerpo y Lista */
.joli-notif-body {
  max-height: 360px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.joli-notif-list {
  display: flex;
  flex-direction: column;
}

.joli-notif-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.05));
  transition: background 0.15s ease;
}

.joli-notif-item:hover {
  background: rgba(255, 255, 255, 0.03);
}

.joli-notif-item.unread {
  background: rgba(59, 130, 246, 0.03);
  border-left: 3px solid #3b82f6;
}

/* Iconos de Severidad con Halos */
.joli-notif-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.severity-critical { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.severity-warning  { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.severity-info     { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.severity-success  { background: rgba(16, 185, 129, 0.15); color: #10b981; }

.joli-notif-content {
  flex: 1;
  min-width: 0;
}

.joli-notif-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  margin-bottom: 3px;
}

.joli-notif-item-title {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text-primary, #ffffff);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.joli-notif-time {
  font-size: 10.5px;
  color: var(--text-muted, rgba(255, 255, 255, 0.5));
  white-space: nowrap;
}

.joli-notif-detail {
  font-size: 12px;
  color: var(--text-secondary, rgba(255, 255, 255, 0.75));
  margin: 0;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Acciones Rápidas en Fila */
.joli-notif-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 2px;
}

.joli-notif-action-btn {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.08));
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-muted, rgba(255, 255, 255, 0.6));
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
}

.joli-notif-action-btn.btn-view:hover {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  border-color: rgba(59, 130, 246, 0.4);
}

.joli-notif-action-btn.btn-approve:hover {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border-color: rgba(16, 185, 129, 0.4);
}

/* Estado Vacío */
.joli-notif-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 36px 20px;
  text-align: center;
}

.joli-empty-icon-ok {
  color: #10b981;
  margin-bottom: 10px;
  background: rgba(16, 185, 129, 0.1);
  padding: 6px;
  border-radius: 50%;
}

.joli-empty-title {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-primary, #ffffff);
  margin: 0 0 4px;
}

.joli-empty-desc {
  font-size: 12px;
  color: var(--text-muted, rgba(255, 255, 255, 0.6));
  max-width: 240px;
}

/* Pie */
.joli-notif-footer {
  padding: 10px 16px;
  background: rgba(0, 0, 0, 0.15);
  border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.08));
  display: flex;
  align-items: center;
  justify-content: center;
}

.joli-notif-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  color: var(--text-muted, rgba(255, 255, 255, 0.7));
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.15s ease;
}

.joli-notif-link-btn:hover {
  color: #ffffff;
}
```
