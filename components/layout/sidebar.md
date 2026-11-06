# Especificación UI: Barra Lateral de Navegación (`Sidebar` colapsable)
## Spec-Driven Development (SDD)

### Regla de uso: componente opcional

- **Regla:** la barra lateral NO DEBERÍA incluirse por defecto. El layout base es de ancho completo con la barra superior ([`navbar.md`](./navbar.md)); la barra lateral se agrega cuando el usuario la pide o cuando la app tiene muchos módulos (regla práctica: más de 6 destinos de primer nivel).
- **Por qué:** en apps de pocos módulos, una barra lateral fija resta ancho a las tablas sin aportar navegación útil.
- **Excepciones:** decisión registrada (ADR).

La barra lateral ofrece navegación entre módulos con filtrado por rol/permiso (RBAC) y estados expandido/colapsado.

---

## 1. Estados e interacción

- **Expandida (escritorio, 260px):** ícono, etiqueta, badges.
- **Colapsada (76px):** solo íconos; cada enlace conserva su nombre accesible (`aria-label`) y un `title` como tooltip.
- **Botón de colapsar (`.sidebar-collapse-toggle`):** circular, en el borde derecho; `ChevronLeft` (expandida) / `ChevronRight` (colapsada); `aria-expanded` y `aria-controls`. Reemplaza al botón de tres líneas (hamburguesa) en escritorio.
- **Preferencia:** el estado colapsado PUEDE recordarse en `localStorage` con una clave de `STORAGE_KEYS` (prefijo de app).
- **RBAC:** cada ítem declara `permissionKey` o `roles`; los ítems sin permiso no se renderizan. Las rutas siguen protegidas por [`ProtectedRoute`](../routing/protected_route.md) y por el backend.
- **Íconos:** catálogo de Lucide React.
- **Ítems sin enlace (`sinEnlace: true`):** opciones planeadas cuyo módulo aún no existe. Se muestran atenuadas (`.no-link`, `aria-disabled`), no navegan ni abren el menú flotante, y se habilitan quitando la marca. Los subítems sin `to` (o sin acción) siguen la misma regla.
- **Sangría:** los ítems quedan más a la derecha que el título de su categoría (título 1.25rem, ítem 1.75rem) y los subítems de acordeón se desplazan lo mismo, para que su línea guía siga bajo el ícono.

---

## 2. Componente React de referencia (`Sidebar.tsx`)

```tsx
import React from 'react';
import { NavLink } from 'react-router-dom';
import { ChevronLeft, ChevronRight, type LucideIcon } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export interface SidebarItem {
  to: string;
  label: string;
  icon: LucideIcon;
  permissionKey?: string;
  roles?: string[];
  badge?: string;
  sinEnlace?: boolean; // Visible pero sin navegar (módulo aún no construido)
}

interface SidebarProps {
  items: SidebarItem[];
  collapsed: boolean;
  onToggle: () => void;
  logoSrc: string;
  appName: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ items, collapsed, onToggle, logoSrc, appName }) => {
  const { hasPermission, hasRole } = useAuth();
  const visibleItems = items.filter(
    (item) =>
      (!item.permissionKey || hasPermission(item.permissionKey)) &&
      (!item.roles || hasRole(item.roles)),
  );

  return (
    <aside id="main-sidebar" className={`joli-sidebar ${collapsed ? 'collapsed' : ''}`} aria-label="Navegación principal">
      <button
        type="button"
        className="sidebar-collapse-toggle"
        onClick={onToggle}
        aria-expanded={!collapsed}
        aria-controls="main-sidebar"
        aria-label={collapsed ? 'Expandir barra lateral' : 'Colapsar barra lateral'}
        title={collapsed ? 'Expandir barra lateral' : 'Colapsar barra lateral'}
      >
        {collapsed ? <ChevronRight size={18} aria-hidden="true" /> : <ChevronLeft size={18} aria-hidden="true" />}
      </button>

      <div className="joli-sidebar-header">
        <img src={logoSrc} alt={appName} className="joli-sidebar-logo" />
        <span className="joli-sidebar-section-title">Módulos</span>
      </div>

      <nav className="joli-sidebar-nav">
        <ul className="joli-nav-list">
          {visibleItems.map(({ to, label, icon: Icon, badge }) => (
            <li key={to} className="joli-nav-item">
              <NavLink
                to={to}
                className={({ isActive }) => `joli-nav-link ${isActive ? 'active' : ''}`}
                aria-label={collapsed ? label : undefined}
                title={collapsed ? label : undefined}
              >
                <Icon size={20} className="joli-nav-icon" aria-hidden="true" />
                <span className="joli-nav-label">{label}</span>
                {badge && <span className="joli-nav-badge">{badge}</span>}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};
```

`NavLink` agrega `aria-current="page"` al enlace activo.

---

## 3. Estilos CSS

```css
.joli-sidebar {
  position: fixed;
  top: var(--topbar-height);
  bottom: 0;
  left: 0;
  z-index: var(--z-sticky);
  display: flex;
  flex-direction: column;
  width: 260px;
  overflow-x: visible;
  background-color: var(--bg-card);
  border-right: 1px solid var(--border-subtle);
  transition: width var(--transition-base);
}

.sidebar-collapse-toggle {
  position: absolute;
  top: 18px;
  right: -15px;
  z-index: calc(var(--z-sticky) + 1);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  color: var(--text-secondary);
  background: var(--bg-card);
  border: 1.5px solid var(--border-strong);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: border-color var(--transition-fast), color var(--transition-fast), transform var(--transition-fast);
}

.sidebar-collapse-toggle:hover {
  color: var(--brand-primary);
  border-color: var(--brand-primary);
  transform: scale(1.08);
}

.sidebar-collapse-toggle:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 2px;
}

.joli-sidebar.collapsed {
  width: 76px;
}

.joli-sidebar.collapsed .joli-nav-label,
.joli-sidebar.collapsed .joli-nav-badge,
.joli-sidebar.collapsed .joli-sidebar-section-title {
  display: none;
}

.joli-sidebar.collapsed .joli-nav-link {
  justify-content: center;
  padding: 0.75rem 0;
}

.joli-sidebar-header {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem 1.25rem 0.5rem;
}

.joli-sidebar-logo {
  height: 28px;
  width: auto;
}

.joli-sidebar-section-title {
  font-size: var(--font-size-2xs);
  font-weight: var(--font-weight-bold);
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--text-muted);
}

.joli-sidebar-nav {
  flex: 1;
  padding: 0.5rem 0.75rem;
  overflow-y: auto;
}

.joli-nav-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.joli-nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
  text-decoration: none;
  border-left: 3px solid transparent;
  border-radius: var(--radius-lg);
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.joli-nav-link:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.joli-nav-link:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: -2px;
}

.joli-nav-link.active {
  background: var(--status-success-bg);
  color: var(--text-primary);
  font-weight: var(--font-weight-semibold);
  border-left-color: var(--brand-primary);
}

.joli-nav-icon {
  flex-shrink: 0;
}

.joli-nav-badge {
  margin-left: auto;
  padding: 2px 8px;
  font-size: var(--font-size-2xs);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  background-color: var(--status-success-bg);
  border-radius: var(--radius-full);
}

/* El contenido principal se desplaza según el ancho de la barra */
.app-main-with-sidebar { margin-left: 260px; transition: margin-left var(--transition-base); }
.app-main-with-sidebar.sidebar-collapsed { margin-left: 76px; }

@media (max-width: 768px) {
  .joli-sidebar { transform: translateX(-100%); }
  .joli-sidebar.mobile-open { transform: translateX(0); }
  .app-main-with-sidebar,
  .app-main-with-sidebar.sidebar-collapsed { margin-left: 0; }
}
```
