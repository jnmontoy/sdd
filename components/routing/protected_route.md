# Especificación de Enrutamiento: Rutas Protegidas y RBAC (`ProtectedRoute.tsx`)
## Control de acceso declarativo en React Router

El componente `ProtectedRoute` intercepta la navegación para que solo usuarios con sesión vigente y rol o permiso autorizado accedan a vistas sensibles o administrativas. Consume `useAuth()` de [`context/auth_context.md`](../context/auth_context.md).

> **Importante:** esta protección es de experiencia de usuario. La autorización real DEBE validarse en el backend en cada endpoint; ocultar una ruta en el frontend no impide llamar a la API.

---

### 1. Requisitos

1. **Sin parpadeos:** mientras `AuthContext` recupera la sesión (`isLoading`), se muestra un loader a pantalla completa (es un estado de carga, no una vista de trabajo).
2. **Redirección a login:** sin sesión, redirige a `/login` guardando la ruta solicitada en `state.from`, para volver a ella tras autenticarse.
3. **Control RBAC:** propiedades opcionales `allowedRoles`, `permissionKey` y `adminOnly`. Si el usuario está autenticado pero no autorizado, redirige a `/403`.
4. **Rutas anidadas:** admite hijos directos (`children`) o `<Outlet />`.

---

### 2. Implementación TypeScript de referencia (`src/components/routing/ProtectedRoute.tsx`)

```tsx
import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export interface ProtectedRouteProps {
  children?: React.ReactNode;
  /** Códigos de rol permitidos (comparación sin distinguir mayúsculas). */
  allowedRoles?: string[];
  /** Clave de permiso requerida, p. ej. 'usuarios.ver'. */
  permissionKey?: string;
  /** Solo roles administrativos (ver ADMIN_ROLES en AuthContext). */
  adminOnly?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles,
  permissionKey,
  adminOnly = false,
}) => {
  const { isAuthenticated, isLoading, hasRole, hasPermission, isAdmin } = useAuth();
  const location = useLocation();

  // 1. Recuperando sesión: evita redirecciones falsas a /login
  if (isLoading) {
    return (
      <div className="joli-route-loader-screen" role="status" aria-live="polite">
        <Loader2 size={36} className="joli-route-spinner" aria-hidden="true" />
        <p className="joli-route-loader-text">Validando sesión...</p>
      </div>
    );
  }

  // 2. Sin sesión
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 3. Autorización: todas las condiciones declaradas deben cumplirse
  const denied =
    (adminOnly && !isAdmin()) ||
    (permissionKey !== undefined && !hasPermission(permissionKey)) ||
    (allowedRoles !== undefined && allowedRoles.length > 0 && !hasRole(allowedRoles));

  if (denied) {
    return <Navigate to="/403" state={{ deniedFrom: location.pathname }} replace />;
  }

  // 4. Contenido autorizado
  return children ? <>{children}</> : <Outlet />;
};
```

Ejemplo de uso:

```tsx
<Route element={<ProtectedRoute />}>
  <Route element={<AppLayout />}>
    <Route path="/home" element={<HomePage />} />
    <Route
      path="/admin/usuarios"
      element={<ProtectedRoute permissionKey="usuarios.ver"><UsuariosPage /></ProtectedRoute>}
    />
  </Route>
</Route>
```

En `LoginPage`, tras un `login()` exitoso: `navigate(location.state?.from?.pathname ?? '/home', { replace: true })`.

---

### 3. Estilos CSS (`route_loader.css`)

```css
.joli-route-loader-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  width: 100%;
  min-height: 100vh;
  background-color: var(--bg-viewport);
  color: var(--text-primary);
}

.joli-route-spinner {
  color: var(--brand-primary);
  animation: joli-route-spin 1s linear infinite;
}

.joli-route-loader-text {
  margin: 0;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
}

@keyframes joli-route-spin {
  to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
  .joli-route-spinner { animation: none; }
}
```
