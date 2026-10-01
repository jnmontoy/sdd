# Especificación de Contexto Global: Autenticación y Sesión (`AuthContext.tsx`)
## Ecosistema Jolifoods — Estado Global de Sesión, RBAC y Tema Día/Noche

El componente `AuthContext` gestiona el ciclo de vida de la sesión del usuario, la persistencia de credenciales seguras, los privilegios de rol (RBAC) y la sincronización del tema corporativo (Noche/Día).

---

### 1. Requisitos de Negocio
1. **Tipado Estricto de Usuario**:
   - `id`, `cedula`, `nombre`, `email`, `rol` (código, nombre y nivel de acceso), `avatar_url`.
2. **Ciclo de Vida de Sesión**:
   - Inicialización asíncrona validando la presencia de tokens en almacenamiento local.
   - Función `login(tokens, user)` que almacena los tokens e hidrata el estado global en memoria.
   - Función `logout()` idempotente que revoca tokens y limpia almacenamiento.
3. **Control de Acceso Basado en Roles (RBAC)**:
   - Métodos utilitarios rápidos: `hasRole(roles: string[])`, `isAdmin()`.
4. **Persistencia del Tema Corporativo**:
   - Alternancia fluida entre Modo Noche (`:root`) y Modo Día (`[data-theme="light"]`) persistido en `localStorage` con clave `joli_theme`.

---

### 2. Implementación TypeScript Canónica (`src/context/AuthContext.tsx`)

```tsx
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { showToast } from '../components/ui/ToastNotification';

export interface UserRole {
  id: number;
  codigo: string;       // 'ADMINISTRADOR', 'OPERADOR', 'CONSULTOR', etc.
  nombre: string;
}

export interface AuthUser {
  id: number | string;
  cedula: string;
  nombre: string;
  email: string;
  rol: UserRole;
  avatar_url?: string;
  ultimo_acceso?: string;
}

export interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  theme: 'dark' | 'light';
  login: (access: string, refresh: string, userData: AuthUser) => void;
  logout: (reason?: string) => void;
  hasRole: (allowedRoles: string[]) => boolean;
  isAdmin: () => boolean;
  toggleTheme: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    const savedTheme = localStorage.getItem('joli_theme');
    return savedTheme === 'light' ? 'light' : 'dark';
  });

  // 1. Aplicar tema en el DOM
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('joli_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  // 2. Inicializar estado desde LocalStorage al arrancar la aplicación
  useEffect(() => {
    const initializeAuth = () => {
      try {
        const token = localStorage.getItem('access_token');
        const savedUserStr = localStorage.getItem('user_info');

        if (token && savedUserStr) {
          const parsedUser = JSON.parse(savedUserStr) as AuthUser;
          setUser(parsedUser);
        }
      } catch (err) {
        console.error('Error restaurando sesión:', err);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_info');
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // 3. Inicio de sesión
  const login = useCallback((access: string, refresh: string, userData: AuthUser) => {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user_info', JSON.stringify(userData));
    setUser(userData);
  }, []);

  // 4. Cierre de sesión
  const logout = useCallback((reason?: string) => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_info');
    setUser(null);

    if (reason) {
      showToast.info('Sesión cerrada', { description: reason });
    }

    // Redirigir a login si no estamos allí
    if (!window.location.pathname.includes('/login')) {
      window.location.href = '/login';
    }
  }, []);

  // 5. Utilidades RBAC
  const hasRole = useCallback((allowedRoles: string[]): boolean => {
    if (!user || !user.rol) return false;
    return allowedRoles.includes(user.rol.codigo.toUpperCase());
  }, [user]);

  const isAdmin = useCallback((): boolean => {
    return hasRole(['ADMIN', 'ADMINISTRADOR', 'SUPERADMIN']);
  }, [hasRole]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        theme,
        login,
        logout,
        hasRole,
        isAdmin,
        toggleTheme
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth debe ser utilizado dentro de un AuthProvider');
  }
  return context;
};
```
