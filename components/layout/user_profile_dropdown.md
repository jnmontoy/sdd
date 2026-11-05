# Componente: Menú de Perfil de Usuario (`UserProfileDropdown`)
## Spec-Driven Development (SDD)

> **Origen:** patrón tomado de vibra y tiendita (menú de perfil del encabezado). Aquí se describe de forma genérica.

`UserProfileDropdown` es el menú de sesión del encabezado ([`navbar.md`](./navbar.md)). Al pulsar el botón de perfil se despliega un panel con la identidad del usuario, su rol, accesos de cuenta y el cierre de sesión, que siempre pasa por [`ConfirmModal`](../modal/confirm_modal.md).

---

## 1. Características

1. **Disparador** con avatar (foto o iniciales), punto de estado, primer nombre y chevron. Patrón *disclosure*: `aria-expanded` y `aria-controls`.
2. **Encabezado del panel:** avatar grande, nombre completo, correo y badge de rol (*ADMINISTRADOR*, *SUPERVISOR*, *OPERADOR*).
3. **Acciones:** "Mi perfil" y, opcionalmente, cambio de tema Noche/Día.
4. **Cerrar sesión:** nunca cierra de inmediato; abre `ConfirmModal` y, al confirmar, llama a `logout()` de [`AuthContext`](../context/auth_context.md) (revoca la cookie de refresh en el servidor).
5. **Cierre del panel** con `Escape` (devuelve el foco al disparador) o clic fuera.

---

## 2. Contrato TypeScript

```typescript
export interface UserSessionData {
  id: string | number;
  name: string;
  email: string;
  role: string;
  avatarUrl?: string;
}

export interface UserProfileDropdownProps {
  user: UserSessionData;
  onLogout: () => void | Promise<void>;
  onProfileClick?: () => void;
  onThemeToggle?: () => void;
  currentTheme?: 'light' | 'dark';
}
```

---

## 3. Código JSX / React de referencia (`UserProfileDropdown.tsx`)

```tsx
import React, { useEffect, useId, useRef, useState } from 'react';
import { ChevronDown, LogOut, Moon, ShieldCheck, Sun, User } from 'lucide-react';
import { ConfirmModal } from '../modal/ConfirmModal';
import type { UserProfileDropdownProps } from './types';

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/);
  return ((parts[0]?.[0] ?? '') + (parts[1]?.[0] ?? '')).toUpperCase() || '?';
}

export const UserProfileDropdown: React.FC<UserProfileDropdownProps> = ({
  user,
  onLogout,
  onProfileClick,
  onThemeToggle,
  currentTheme = 'dark',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const panelId = useId();
  const initials = getInitials(user.name);

  useEffect(() => {
    if (!isOpen) return;
    const onMouseDown = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) setIsOpen(false);
    };
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
        triggerRef.current?.focus();
      }
    };
    document.addEventListener('mousedown', onMouseDown);
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('mousedown', onMouseDown);
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [isOpen]);

  const avatar = (className: string) => (
    <span className={className} aria-hidden="true">
      {user.avatarUrl ? <img src={user.avatarUrl} alt="" className="avatar-img-fit" /> : initials}
    </span>
  );

  const handleConfirmLogout = async () => {
    setIsLoggingOut(true);
    try {
      await onLogout();
    } finally {
      setIsLoggingOut(false);
      setShowLogoutConfirm(false);
    }
  };

  return (
    <>
      <div className="user-profile-menu-container" ref={containerRef}>
        <button
          ref={triggerRef}
          type="button"
          className={`user-profile-badge ${isOpen ? 'active' : ''}`}
          onClick={() => setIsOpen((prev) => !prev)}
          aria-expanded={isOpen}
          aria-controls={panelId}
          aria-label={`Menú de usuario: ${user.name}`}
        >
          <span className="user-avatar-circle">
            {avatar('user-avatar-content')}
            <span className="status-indicator-dot online" aria-hidden="true" />
          </span>
          <span className="d-none d-sm-inline user-display-name">{user.name.split(' ')[0]}</span>
          <ChevronDown size={14} className={`chevron-icon ${isOpen ? 'rotate' : ''}`} aria-hidden="true" />
        </button>

        {isOpen && (
          <div id={panelId} className="profile-dropdown-menu">
            <div className="profile-dropdown-header">
              {avatar('dropdown-avatar-lg')}
              <div className="dropdown-user-info">
                <span className="dropdown-user-name">{user.name}</span>
                <span className="dropdown-user-email">{user.email}</span>
                <span className="dropdown-user-role-badge">
                  <ShieldCheck size={11} aria-hidden="true" />
                  <span>{user.role}</span>
                </span>
              </div>
            </div>

            <div className="dropdown-divider" />

            <div className="profile-dropdown-items">
              {onProfileClick && (
                <button
                  type="button"
                  className="dropdown-item"
                  onClick={() => {
                    setIsOpen(false);
                    onProfileClick();
                  }}
                >
                  <User size={16} aria-hidden="true" />
                  <span>Mi perfil</span>
                </button>
              )}

              {onThemeToggle && (
                <button type="button" className="dropdown-item" onClick={onThemeToggle}>
                  {currentTheme === 'dark' ? <Sun size={16} aria-hidden="true" /> : <Moon size={16} aria-hidden="true" />}
                  <span>Modo {currentTheme === 'dark' ? 'claro' : 'oscuro'}</span>
                </button>
              )}
            </div>

            <div className="dropdown-divider" />

            <div className="profile-dropdown-footer">
              <button
                type="button"
                className="dropdown-item logout"
                onClick={() => {
                  setIsOpen(false);
                  setShowLogoutConfirm(true);
                }}
              >
                <LogOut size={16} aria-hidden="true" />
                <span>Cerrar sesión</span>
              </button>
            </div>
          </div>
        )}
      </div>

      <ConfirmModal
        isOpen={showLogoutConfirm}
        onClose={() => setShowLogoutConfirm(false)}
        onConfirm={handleConfirmLogout}
        isLoading={isLoggingOut}
        title="Cerrar sesión"
        message="¿Desea cerrar la sesión? Deberá iniciar sesión nuevamente para continuar."
        confirmText="Cerrar sesión"
        cancelText="Permanecer conectado"
        type="warning"
      />
    </>
  );
};
```

Integración con la sesión:

```tsx
const { user, logout, theme, toggleTheme } = useAuth();

{user && (
  <UserProfileDropdown
    user={{ id: user.id, name: `${user.nombre} ${user.apellidos}`, email: user.email, role: user.roles[0] ?? '', avatarUrl: user.avatar_url ?? undefined }}
    onLogout={() => logout()}
    onProfileClick={() => navigate('/perfil')}
    onThemeToggle={toggleTheme}
    currentTheme={theme}
  />
)}
```

---

## 4. Estilos CSS (`UserProfileDropdown.css`)

```css
.user-profile-menu-container {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.user-profile-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px 4px 5px;
  font-family: inherit;
  color: var(--text-primary);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: background-color var(--transition-fast), border-color var(--transition-fast);
}

.user-profile-badge:hover,
.user-profile-badge.active {
  background: var(--bg-active);
  border-color: var(--border-card-accent);
}

.user-profile-badge:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 2px;
}

.user-avatar-circle,
.dropdown-avatar-lg {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  border-radius: var(--radius-full);
  background: var(--status-success-bg);
  color: var(--text-primary);
  font-weight: var(--font-weight-bold);
}

.user-avatar-circle {
  width: 28px;
  height: 28px;
  overflow: visible;
  font-size: var(--font-size-2xs);
}

.dropdown-avatar-lg {
  width: 40px;
  height: 40px;
  font-size: var(--font-size-sm);
}

.avatar-img-fit {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--radius-full);
}

.status-indicator-dot {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  border: 2px solid var(--bg-card);
}

.status-indicator-dot.online {
  background: var(--status-success);
}

.user-display-name {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--text-secondary);
}

.chevron-icon {
  color: var(--text-muted);
  transition: transform var(--transition-fast);
}

.chevron-icon.rotate {
  transform: rotate(180deg);
}

.profile-dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  z-index: var(--z-popover);
  display: flex;
  flex-direction: column;
  width: 260px;
  overflow: hidden;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-popover);
  backdrop-filter: var(--glass-blur);
  animation: profileFadeSlide 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

.profile-dropdown-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--bg-elevated);
}

.dropdown-user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.dropdown-user-name,
.dropdown-user-email {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.dropdown-user-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.dropdown-user-email {
  margin-bottom: 4px;
  font-size: var(--font-size-2xs);
  color: var(--text-muted);
}

.dropdown-user-role-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  width: fit-content;
  padding: 1px 6px;
  font-size: var(--font-size-2xs);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-primary);
  background: var(--status-success-bg);
  border-radius: var(--radius-sm);
}

.dropdown-divider {
  height: 1px;
  margin: 0;
  background: var(--border-subtle);
}

.profile-dropdown-items,
.profile-dropdown-footer {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 6px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 12px;
  text-align: left;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.dropdown-item:hover,
.dropdown-item:focus-visible {
  background: var(--bg-active);
  color: var(--text-primary);
  outline: none;
}

.dropdown-item.logout {
  color: var(--status-error);
}

.dropdown-item.logout:hover,
.dropdown-item.logout:focus-visible {
  background: var(--status-error-bg);
  color: var(--status-error);
}

@keyframes profileFadeSlide {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (prefers-reduced-motion: reduce) {
  .profile-dropdown-menu { animation: none; }
}
```
