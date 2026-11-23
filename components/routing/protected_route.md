# Especificación de Enrutamiento: Rutas Protegidas y RBAC (`ProtectedRoute.tsx`)
## Control de acceso declarativo en React Router

El componente `ProtectedRoute` intercepta la navegación para que solo usuarios con sesión vigente y rol o permiso autorizado accedan a vistas sensibles o administrativas. Consume `useAuth()` de [`context/auth_context.md`](../context/auth_context.md).

> **Importante:** esta protección es de experiencia de usuario. La autorización real DEBE validarse en el backend en cada endpoint; ocultar una ruta en el frontend no impide llamar a la API.

---

### 1. Requisitos

1. **Sin parpadeos:** mientras `AuthContext` recupera la sesión (`isLoading`), se muestra la cortinilla común `PageLoader variant="curtain"` con mensaje visible ("Verificando sesión"), definida en [`page_loader.md`](../loader/page_loader.md). No se arma una pantalla de carga propia ni un texto suelto.
2. **Redirección a login:** sin sesión, redirige a `/login` guardando la ruta solicitada en `state.from`, para volver a ella tras autenticarse.
3. **Control RBAC:** propiedades opcionales `allowedRoles`, `permissionKey` y `adminOnly`. Si el usuario está autenticado pero no autorizado, redirige a `/403`.
4. **Cambio de clave obligatorio:** si `user.debe_cambiar_clave` es verdadero, toda ruta protegida redirige a `/primer-ingreso` (excepto esa misma ruta).
5. **Rutas anidadas:** admite hijos directos (`children`) o `<Outlet />`.

---

### 2. Implementación TypeScript de referencia (`src/components/routing/ProtectedRoute.tsx`)

```tsx
import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { PageLoader } from '../ui/PageLoader';

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
  const { user, isAuthenticated, isLoading, hasRole, hasPermission, isAdmin } = useAuth();
  const location = useLocation();

  // 1. Recuperando sesión: evita redirecciones falsas a /login
  if (isLoading) {
    return <PageLoader variant="curtain" message="Verificando sesión" />;
  }

  // 2. Sin sesión
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 2b. Clave temporal o primer ingreso: forzar el cambio antes de usar la app
  if (user?.debe_cambiar_clave && location.pathname !== '/primer-ingreso') {
    return <Navigate to="/primer-ingreso" replace />;
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

En `LoginPage`, tras un `login()` exitoso: `navigate(user.debe_cambiar_clave ? '/primer-ingreso' : location.state?.from?.pathname ?? '/home', { replace: true })`.

---

### 3. Estilos

El estado de carga no tiene estilos propios: usa los de la cortinilla (`PageLoader.css`, en [`page_loader.md`](../loader/page_loader.md)), que ya respeta `prefers-reduced-motion`, `role="status"` y el tema claro y oscuro. La antigua pantalla `.joli-route-loader-screen` con ícono `Loader2` queda reemplazada.
