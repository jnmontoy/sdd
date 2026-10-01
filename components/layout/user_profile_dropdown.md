# Componente Maestro: Menú Desplegable de Perfil de Usuario (UserProfileDropdown)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)
### Referencia Canónica: Implementaciones de Producción en `vibra` y `tiendita`

El **UserProfileDropdown** es el componente oficial de gestión de sesión y acceso al perfil del colaborador en el **TopHeader**.

Al presionar el botón de perfil (`.user-profile-badge` o `.profile-trigger`), se despliega un menú flotante con efecto *glassmorphism* que presenta la identidad del usuario activo, sus permisos/roles, enlaces de cuenta y el disparador de **Cierre de Sesión Seguro** protegido por el componente **`ConfirmModal`**.

---

## 1. Características Arquitectónicas Clave

1. **Gatillador en TopHeader (`.user-profile-badge` / `.profile-trigger`)**:
   - Muestra el avatar con iniciales o fotografía corporativa.
   - Indicador de estado de conexión verde en línea (*online status dot*).
   - Nombre de pila o nombre completo del usuario y chevron indicador de despliegue (`ChevronDown`).
2. **Encabezado del Menú (`.profile-dropdown-header`)**:
   - Avatar en mayor escala.
   - Nombre completo del colaborador.
   - Correo electrónico corporativo (`@jolifoods.com`).
   - Badge de rol o perfil activo (ej. *ADMINISTRADOR*, *SUPERVISOR*, *OPERADOR*).
3. **Acciones Rápidas del Menú**:
   - **Mi Perfil (`User`)**: Navega a la vista de perfil `/perfil` o abre el panel de edición de datos personales.
   - **Conmutador de Tema Noche / Día**: Acceso rápido alternativo con badge de estado.
4. **Cierre de Sesión Protegido (`.dropdown-item.logout`)**:
   - Ítem resaltado con icono `LogOut` y acento de peligro sutil.
   - **NUNCA cierra la sesión inmediatamente sin confirmación**: Invoca siempre el componente canónico **`ConfirmModal`** de Jolifoods solicitando confirmación explícita para evitar pérdida accidental del trabajo o filtros activos.
5. **Cierre Automático**:
   - Cierre al presionar la tecla `Escape` o al hacer clic fuera del menú (*Click Outside Listener*).

---

## 2. Contrato de Datos e Interfaz TypeScript

```typescript
export interface UserSessionData {
  id: string | number;
  name: string;
  email: string;
  role: string;
  avatarUrl?: string;
  initials?: string;
}

export interface UserProfileDropdownProps {
  user: UserSessionData;
  onLogoutClick: () => void;
  onProfileClick?: () => void;
  onThemeToggle?: () => void;
  currentTheme?: 'light' | 'dark';
}
```

---

## 3. Código JSX / React 19 Canónico (`UserProfileDropdown.tsx`)

```tsx
import React, { useState, useRef, useEffect } from 'react';
import { User, LogOut, ChevronDown, Sun, Moon, ShieldCheck } from 'lucide-react';
import { ConfirmModal } from '../modal/ConfirmModal';
import './UserProfileDropdown.css';

export const UserProfileDropdown: React.FC<UserProfileDropdownProps> = ({
  user,
  onLogoutClick,
  onProfileClick,
  onThemeToggle,
  currentTheme = 'dark',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const initials = user.initials || user.name.slice(0, 2).toUpperCase();

  // Cerrar al hacer clic fuera
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

  const handleLogoutTrigger = () => {
    setIsOpen(false);
    setShowLogoutConfirm(true);
  };

  return (
    <>
      <div className="user-profile-menu-container" ref={containerRef}>
        {/* Gatillador en TopHeader */}
        <button
          type="button"
          className={`user-profile-badge ${isOpen ? 'active' : ''}`}
          onClick={() => setIsOpen(prev => !prev)}
          aria-haspopup="true"
          aria-expanded={isOpen}
        >
          <div className="user-avatar-circle">
            {user.avatarUrl ? (
              <img src={user.avatarUrl} alt={user.name} className="avatar-img-fit" />
            ) : (
              initials
            )}
            <span className="status-indicator-dot online"></span>
          </div>
          <span className="d-none d-sm-inline font-sm fw-medium user-display-name">
            {user.name.split(' ')[0]}
          </span>
          <ChevronDown size={14} className={`chevron-icon ${isOpen ? 'rotate' : ''}`} />
        </button>

        {/* Menú Desplegable Flotante */}
        {isOpen && (
          <div className="profile-dropdown-menu fade-in">
            {/* Encabezado con información del Colaborador */}
            <div className="profile-dropdown-header">
              <div className="dropdown-avatar-lg">
                {user.avatarUrl ? (
                  <img src={user.avatarUrl} alt={user.name} className="avatar-img-fit" />
                ) : (
                  initials
                )}
              </div>
              <div className="dropdown-user-info">
                <span className="dropdown-user-name">{user.name}</span>
                <span className="dropdown-user-email">{user.email}</span>
                <span className="dropdown-user-role-badge">
                  <ShieldCheck size={11} />
                  <span>{user.role}</span>
                </span>
              </div>
            </div>

            <div className="dropdown-divider"></div>

            {/* Opciones */}
            <div className="profile-dropdown-items">
              <button
                type="button"
                className="dropdown-item"
                onClick={() => {
                  setIsOpen(false);
                  onProfileClick?.();
                }}
              >
                <User size={16} />
                <span>Mi Perfil</span>
              </button>

              {onThemeToggle && (
                <button
                  type="button"
                  className="dropdown-item theme-toggle-item"
                  onClick={onThemeToggle}
                >
                  {currentTheme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
                  <span>Modo {currentTheme === 'dark' ? 'Claro' : 'Oscuro'}</span>
                </button>
              )}
            </div>

            <div className="dropdown-divider"></div>

            {/* Botón de Cerrar Sesión */}
            <div className="profile-dropdown-footer">
              <button
                type="button"
                className="dropdown-item logout"
                onClick={handleLogoutTrigger}
              >
                <LogOut size={16} />
                <span>Cerrar Sesión</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal Canónico de Confirmación de Cierre de Sesión */}
      <ConfirmModal
        isOpen={showLogoutConfirm}
        onClose={() => setShowLogoutConfirm(false)}
        onConfirm={() => {
          setShowLogoutConfirm(false);
          onLogoutClick();
        }}
        title="Cerrar Sesión"
        message="¿Estás seguro de que deseas salir del ecosistema Jolifoods? Deberás iniciar sesión nuevamente para acceder."
        confirmText="Confirmar Salida"
        cancelText="Permanecer Conectado"
        type="warning"
      />
    </>
  );
};
```

---

## 4. Estilos CSS Canónicos (`UserProfileDropdown.css`)

```css
/* ==========================================================================
   USER PROFILE DROPDOWN — ESTÁNDAR JOLIFOODS (VIBRA / TIENDITA)
   ========================================================================== */

.user-profile-menu-container {
  position: relative;
  display: inline-flex;
  align-items: center;
}

/* Gatillador en TopHeader */
.user-profile-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px 4px 5px;
  background: var(--surface-card, #14142b);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.09));
  border-radius: 9999px;
  cursor: pointer;
  color: var(--text-primary, #ffffff);
  transition: all 0.18s ease;
  font-family: inherit;
}

.user-profile-badge:hover,
.user-profile-badge.active {
  background: var(--surface-active, #2b2b55);
  border-color: rgba(16, 185, 129, 0.4);
}

.user-avatar-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  font-weight: 700;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.status-indicator-dot {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 2px solid var(--surface-card, #14142b);
}

.status-indicator-dot.online {
  background: #10b981;
}

.user-display-name {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-secondary, rgba(255, 255, 255, 0.85));
}

.chevron-icon {
  color: var(--text-muted, rgba(255, 255, 255, 0.5));
  transition: transform 0.2s ease;
}

.chevron-icon.rotate {
  transform: rotate(180deg);
}

/* Panel Desplegable Flotante */
.profile-dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 260px;
  background: var(--surface-card, #14142b);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.12));
  border-radius: 14px;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(16px);
  z-index: 1050;
  overflow: hidden;
  animation: notifFadeSlide 0.18s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
}

/* Encabezado */
.profile-dropdown-header {
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.15);
}

.dropdown-avatar-lg {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  font-weight: 800;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dropdown-user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.dropdown-user-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary, #ffffff);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-user-email {
  font-size: 11px;
  color: var(--text-muted, rgba(255, 255, 255, 0.6));
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.dropdown-user-role-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 9.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  padding: 1px 6px;
  border-radius: 4px;
  width: fit-content;
}

.dropdown-divider {
  height: 1px;
  background: var(--border-color, rgba(255, 255, 255, 0.08));
  margin: 0;
}

/* Ítems del Menú */
.profile-dropdown-items,
.profile-dropdown-footer {
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-secondary, rgba(255, 255, 255, 0.8));
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.dropdown-item:hover {
  background: var(--surface-active, #2b2b55);
  color: var(--text-primary, #ffffff);
}

/* Botón de Cerrar Sesión */
.dropdown-item.logout {
  color: #ef4444;
}

.dropdown-item.logout:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}
```
