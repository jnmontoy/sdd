# Especificación de Enrutamiento: Rutas Protegidas y RBAC (`ProtectedRoute.tsx`)
## Ecosistema Jolifoods — Control de Acceso Declarativo en React Router

El componente `ProtectedRoute` intercepta la navegación para garantizar que solo usuarios con credenciales vigentes y roles autorizados puedan acceder a vistas sensibles o administrativas.

---

### 1. Requisitos de Negocio y Seguridad
1. **Prevención de Pantallazos en Blanco / Flash**: Durante la comprobación inicial de credenciales (`isLoading`), renderiza un loader corporativo centrado.
2. **Redirección Segura a Login**: Si no hay sesión activa, redirige a `/login` preservando la ruta solicitada en el estado de navegación (`state: { from: location }`) para redirigir al usuario tras identificarse con éxito.
3. **Control RBAC Granular**: Propiedad opcional `allowedRoles: string[]`. Si el usuario está autenticado pero su rol no está autorizado, redirige automáticamente a la página `/403` (Acceso Denegado).
4. **Soporte para Layouts Anidados**: Admite renderizar tanto elementos hijos directos (`children`) como componentes de ruta anidados vía `<Outlet />`.

---

### 2. Implementación TypeScript Canónica (`src/components/routing/ProtectedRoute.tsx`)

```tsx
import React from 'react';
import { Navigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Loader2 } from 'lucide-react';

export interface ProtectedRouteProps {
  children?: React.ReactNode;
  allowedRoles?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { isAuthenticated, isLoading, user, hasRole } = useAuth();
  const location = useLocation();

  // 1. Estado de carga inicial (Evita parpadeos o falsas redirecciones)
  if (isLoading) {
    return (
      <div className="joli-route-loader-screen">
        <div className="route-loader-content">
          <Loader2 size={36} className="route-spinner text-primary" />
          <p className="route-loader-text">Validando credenciales...</p>
        </div>
      </div>
    );
  }

  // 2. Comprobar si el usuario está autenticado
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 3. Comprobar permisos RBAC
  if (allowedRoles && allowedRoles.length > 0) {
    const isAuthorized = hasRole(allowedRoles);
    if (!isAuthorized) {
      return <Navigate to="/403" state={{ deniedFrom: location.pathname }} replace />;
    }
  }

  // 4. Renderizar contenido autorizado
  return children ? <>{children}</> : <Outlet />;
};
```

---

### 3. Estilos CSS (`route_loader.css`)

```css
.joli-route-loader-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100vw;
  height: 100vh;
  background-color: var(--color-bg-body, #0F172A);
  color: var(--color-text-primary, #F8FAFC);
}

.route-loader-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.route-spinner {
  animation: spin 1s linear infinite;
  color: var(--color-primary, #2D6A4F);
}

.route-loader-text {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--color-text-secondary, #94A3B8);
  letter-spacing: 0.2px;
}
```
