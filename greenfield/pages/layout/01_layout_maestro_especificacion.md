# 01. Especificación del Layout Maestro (App Shell)
## Joli Foods — Spec-Driven Development (SDD)

Estructura envolvente (*App Shell*) de todas las vistas tras iniciar sesión: barra superior, menú lateral, área de contenido, tema noche/día y manejo de sesión vencida.

---

## 1. Topología

```
+-----------------------------------------------------------------------------+
| Barra superior (var(--topbar-height), 100% del ancho)                        |
| [☰] Logo + nombre del proyecto                  [Tema] [Menú de perfil ▾]   |
+------------------------------+----------------------------------------------+
| Menú lateral (260px / 76px)  | Área de contenido <main> (ocupa el resto)    |
| - Tablero                    | - Tablas, filtros, KPIs y gráficos al 100%   |
| - Módulos según permisos     |   del ancho disponible                       |
+------------------------------+----------------------------------------------+
```

### Regla de ancho (DEBERÍA)
- Las vistas autenticadas DEBERÍAN ocupar el 100% del ancho disponible (`container-fluid`, `width: 100%`), sin contenedores estrechos centrados (`max-w-*`, `mx-auto` como contenedor principal).
- **Por qué:** las pantallas operativas son tablas y tableros con muchas columnas; un contenedor angosto obliga a desplazarse horizontalmente y desperdicia el monitor.
- **Excepciones:** modales, el diálogo de sesión vencida, la tarjeta de login y páginas de error PUEDEN centrarse. Otras desviaciones se registran en un ADR o por pedido explícito del usuario.
- La barra superior abarca el 100% del ancho: marca a la izquierda, controles de sesión a la derecha.

---

## 2. Tema Noche / Día

`AuthContext` expone `theme` y `toggleTheme()`; la preferencia se guarda en `localStorage` con la clave `STORAGE_KEYS.theme` (`<slug-app>:theme`, ver `frontend/src/config/storageKeys.ts`). El slug evita choques entre aplicaciones que comparten dominio. Todo acceso a `localStorage` va en `try/catch` (modo privado o almacenamiento bloqueado).

### Script anti-parpadeo (en `index.html`, antes de cargar la app)
Vite reemplaza `%VITE_APP_SLUG%` en `index.html` al compilar.
```html
<script>
  (function () {
    var theme = 'dark';
    try { theme = localStorage.getItem('%VITE_APP_SLUG%:theme') || 'dark'; } catch (e) { /* storage bloqueado */ }
    document.documentElement.setAttribute('data-theme', theme === 'light' ? 'light' : 'dark');
  })();
</script>
```

---

## 3. Sesión Vencida

El manejo es el de BP-20 y la decisión canónica de sesión (access en memoria, refresh en cookie HttpOnly):
1. El cliente HTTP, ante un 401, intenta **un** refresh; si falla, despacha `window.dispatchEvent(new Event('session-expired'))`.
2. `AuthContext` escucha ese evento y muestra [`SessionExpirationModal`](../../../components/modal/session_expiration_modal.md) (ver [`auth_context.md`](../../../components/context/auth_context.md)).
3. Al confirmar, `logout()` limpia el estado y navega a `/login?redirect=<ruta actual>`.

El layout **no** monta un segundo modal ni su propio listener. **Por qué:** dos manejadores del mismo evento producen modales duplicados o redirecciones en carrera.

---

## 4. Implementación (`AppLayout.tsx`)

```tsx
import { useCallback, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';

export function AppLayout() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  // El tema (lectura/escritura en STORAGE_KEYS.theme y atributo data-theme) lo gestiona AuthContext
  const { user, logout, theme, toggleTheme } = useAuth();
  const navigate = useNavigate();

  const handleLogout = useCallback(async () => {
    await logout();
    navigate('/login', { replace: true });
  }, [logout, navigate]);

  return (
    <div className="joli-app-shell">
      <Navbar
        onToggleSidebar={() => setIsSidebarCollapsed((v) => !v)}
        currentTheme={theme}
        onToggleTheme={toggleTheme}
        user={user}
        onLogout={handleLogout}
      />

      <div className="joli-app-body">
        {/* El menú muestra solo los módulos para los que el usuario tiene permiso "<modulo>.ver" (BP-19) */}
        <Sidebar isCollapsed={isSidebarCollapsed} permisos={user?.permisos ?? []} />

        <main className={`joli-main-content ${isSidebarCollapsed ? 'is-expanded' : ''}`}>
          <div className="container-fluid p-4">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
```

---

## 5. Estilos Estructurales

```css
.joli-app-shell {
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-viewport);
  color: var(--text-primary);
}

.joli-app-body {
  display: flex;
  flex: 1;
  position: relative;
}

.joli-main-content {
  flex: 1;
  min-width: 0; /* permite que tablas anchas hagan scroll interno en vez de desbordar */
  margin-left: 260px;
  min-height: calc(100vh - var(--topbar-height));
  background-color: var(--bg-viewport);
  transition: margin-left var(--transition-base);
}

.joli-main-content.is-expanded {
  margin-left: 76px;
}

@media (max-width: 768px) {
  .joli-main-content,
  .joli-main-content.is-expanded {
    margin-left: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .joli-main-content { transition: none; }
}
```

Componentes: [`navbar.md`](../../../components/layout/navbar.md), [`sidebar.md`](../../../components/layout/sidebar.md), [`user_profile_dropdown.md`](../../../components/layout/user_profile_dropdown.md).
