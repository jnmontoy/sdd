# Especificación UI: Barra de Navegación Superior (`TopNavbar`)
## Spec-Driven Development (SDD)

La **barra superior** es la cabecera persistente de todas las vistas autenticadas: marca, título de la página, cambio de tema Noche/Día ([`variables.css`](../variables.css)), notificaciones y menú de perfil con cierre de sesión.

---

## Reglas de cabecera (convenciones de diseño, nivel DEBERÍA)

1. **Sin barra lateral por defecto.** La barra superior ocupa el 100% del ancho; la [barra lateral](./sidebar.md) se agrega solo cuando se pide o la app tiene muchos módulos. **Por qué:** maximiza el ancho para tablas.
2. **Título de la página en la barra, a la izquierda.** El título de la vista actual va junto al logo, separado por `/`, con un badge de contexto opcional; no se repite como `<h1>` grande dentro del cuerpo. **Por qué:** ahorra espacio vertical.
3. **Sin migas de pan (breadcrumbs)** salvo pedido explícito. **Por qué:** en apps de 1–2 niveles no aportan y ocupan espacio. **Excepción:** apps con jerarquías profundas (3+ niveles).
4. **Títulos en color neutro** (`--text-primary`); el verde de marca se reserva para estados y acentos. **Por qué:** el color debe significar algo.
5. **Lado derecho solo para controles de sesión:** tema, notificaciones y perfil.

Todas se pueden desviar con pedido explícito del usuario o una decisión registrada (ADR).

---

## 1. Anatomía

```
+------------------------------------------------------------------------------------------------+
| [Logo]  /  [Título de la página] [BADGE]                 (espacio)      [☀/🌙]  [🔔 3]  [(AP) Ana v] |
+------------------------------------------------------------------------------------------------+
```

1. **Izquierda (`.topheader-left`):** logo, divisor `/`, título (`.topheader-page-title`, es el `<h1>` de la página) y badge opcional (`.topheader-page-badge`, p. ej. "PRODUCCIÓN").
2. **Derecha (`.topheader-right`):** botón de tema, campana de notificaciones ([`notification_popover.md`](../notification/notification_popover.md)) y [`UserProfileDropdown`](./user_profile_dropdown.md).

---

## 2. Componente React de referencia (`TopNavbar.tsx`)

```tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Moon, Sun } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { UserProfileDropdown } from './UserProfileDropdown';
import { NotificationBellPopover } from '../notification/NotificationBellPopover';

interface TopNavbarProps {
  pageTitle: string;
  pageBadge?: string;
  logoSrc: string;
  appName: string;
}

export const TopNavbar: React.FC<TopNavbarProps> = ({ pageTitle, pageBadge, logoSrc, appName }) => {
  const { user, logout, theme, toggleTheme } = useAuth();
  const navigate = useNavigate();
  const nextThemeLabel = theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';

  return (
    <header className="top-header">
      <div className="topheader-left">
        <img src={logoSrc} alt={appName} className="topheader-logo" />
        <span className="topheader-brand-divider" aria-hidden="true">/</span>
        <div className="topheader-title-box">
          <h1 className="topheader-page-title">{pageTitle}</h1>
          {pageBadge && <span className="topheader-page-badge">{pageBadge}</span>}
        </div>
      </div>

      <div className="topheader-right">
        <button
          type="button"
          className="icon-btn-header"
          onClick={toggleTheme}
          aria-label={nextThemeLabel}
          title={nextThemeLabel}
        >
          {theme === 'dark' ? <Sun size={18} aria-hidden="true" /> : <Moon size={18} aria-hidden="true" />}
        </button>

        <NotificationBellPopover />

        {user && (
          <UserProfileDropdown
            user={{ id: user.id, name: `${user.nombre} ${user.apellidos}`, email: user.email, role: user.roles[0] ?? '', avatarUrl: user.avatar_url ?? undefined }}
            onLogout={() => logout()}
            onProfileClick={() => navigate('/perfil')}
          />
        )}
      </div>
    </header>
  );
};
```

En mocks HTML se usa la misma estructura con `<i data-lucide="...">` y un nombre de ejemplo ficticio (p. ej. "Ana Pérez", `usuario@ejemplo.com`).

---

## 3. Estilos CSS

```css
.top-header {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
  height: var(--topbar-height);
  padding: 0 1.5rem;
  background: var(--glass-bg);
  border-bottom: 1px solid var(--glass-border);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
}

.topheader-left,
.topheader-right {
  display: flex;
  align-items: center;
  min-width: 0;
}

.topheader-left { gap: 0.75rem; }
.topheader-right { gap: 0.85rem; flex-shrink: 0; }

.topheader-logo {
  height: 30px;
  width: auto;
}

.topheader-brand-divider {
  color: var(--text-muted);
  font-weight: var(--font-weight-regular);
}

.topheader-title-box {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  min-width: 0;
  padding: 0.35rem 0.75rem;
  background: var(--bg-hover);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.topheader-page-title {
  margin: 0;
  overflow: hidden;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  letter-spacing: -0.01em;
  white-space: nowrap;
  text-overflow: ellipsis;
  color: var(--text-primary);
}

.topheader-page-badge {
  padding: 2px 7px;
  font-size: var(--font-size-2xs);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  color: var(--text-primary);
  background: var(--status-success-bg);
  border: 1px solid var(--border-card-accent);
  border-radius: var(--radius-full);
}

.icon-btn-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  color: var(--text-secondary);
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.icon-btn-header:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.icon-btn-header:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 2px;
}

@media (max-width: 640px) {
  .top-header { padding: 0 0.75rem; }
  .topheader-brand-divider,
  .topheader-page-badge { display: none; }
}
```
