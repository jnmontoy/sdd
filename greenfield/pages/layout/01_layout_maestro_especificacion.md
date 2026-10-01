# 01. Especificación del Layout Maestro Corporativo (App Shell)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

Esta especificación describe la estructura envolvente (**App Shell / Layout Maestro**) en la que residen todas las vistas de la aplicación una vez superado el proceso de autenticación.

Garantiza una experiencia de usuario consistente, persistencia del **Modo Noche / Modo Día**, control de sesión activa y manejo centralizado de expiración de sesión (HTTP 401).

---

## 1. Topología del Layout Maestro

```
+-----------------------------------------------------------------------------+
| Top Navbar (64px Fija) - Logo, Título Proyecto, Tema Noche/Día, Perfil/Salir|
+------------------------------------+----------------------------------------+
|                                    |                                        |
| Sidebar de Módulos (260px o 76px)  |  Área de Contenido Dinámico (<main>)   |
| - Tablero Principal                |  - Vistas de Negocio                   |
| - Operaciones                      |  - Tablas, Formularios, Gráficos       |
| - Reportes                         |                                        |
| - Auditoría                        |                                        |
|                                    |                                        |
+------------------------------------+----------------------------------------+
```

---

## 2. Gestión Centralizada del Tema (Noche / Día)

El tema visual se almacena en `localStorage` bajo la clave `jolifoods_theme` (`dark` o `light`).

### Script de Inicialización Anti-Parpadeo (en `index.html` o `main.tsx`):
```javascript
(function() {
  const savedTheme = localStorage.getItem('jolifoods_theme') || 'dark';
  if (savedTheme === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
})();
```

---

## 3. Manejo de Sesión Expirada (Interceptor Axios / Fetch)

Cuando cualquier petición al backend retorne código de estado HTTP 401:
1. El interceptor intercepta el error.
2. Abre automáticamente el modal accesible de sesión expirada especificado en [`feedback_alerts.md`](../../components/login/feedback_alerts.md).
3. Inicia un contador de 5 segundos tras el cual limpia el estado de autenticación y redirige a la vista de Login.

---

## 4. Implementación en React + TypeScript (`AppLayout.tsx`)

```tsx
import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { SessionExpiredModal } from '../components/auth/SessionExpiredModal';
import '../styles/variables.css';

export const AppLayout: React.FC = () => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('jolifoods_theme') as 'dark' | 'light') || 'dark';
  });
  const [isSessionExpired, setIsSessionExpired] = useState<boolean>(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Conmutador de tema
  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('jolifoods_theme', newTheme);
    if (newTheme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="joli-app-shell">
      {/* 1. TOP NAVBAR */}
      <Navbar 
        onToggleSidebar={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        currentTheme={theme}
        onToggleTheme={toggleTheme}
        user={user}
        onLogout={handleLogout}
      />

      <div className="joli-app-body">
        {/* 2. SIDEBAR NAVEGACIÓN */}
        <Sidebar 
          isCollapsed={isSidebarCollapsed}
          userRole={user?.rol || 'CONSULTA'}
        />

        {/* 3. CONTENIDO PRINCIPAL */}
        <main className={`joli-main-content ${isSidebarCollapsed ? 'expanded' : ''}`}>
          <div className="container-fluid p-4">
            <Outlet />
          </div>
        </main>
      </div>

      {/* 4. MODAL DE SESIÓN EXPIRADA */}
      {isSessionExpired && (
        <SessionExpiredModal onConfirm={() => navigate('/login')} />
      )}
    </div>
  );
};
```

---

## 5. Estilos Estructurales del Layout

```css
.joli-app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-base);
  color: var(--color-text-primary);
}

.joli-app-body {
  display: flex;
  flex: 1;
  position: relative;
}

.joli-main-content {
  flex: 1;
  margin-left: 260px;
  min-height: calc(100vh - 64px);
  background-color: var(--color-bg-base);
  transition: margin-left var(--transition-normal);
}

.joli-main-content.expanded {
  margin-left: 76px;
}

@media (max-width: 768px) {
  .joli-main-content {
    margin-left: 0 !important;
  }
}
```
