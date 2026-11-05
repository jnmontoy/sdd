# Especificación de Contexto Global: Autenticación y Sesión (`AuthContext.tsx`)
## Estado global de sesión, RBAC y tema Día/Noche

El componente `AuthContext` gestiona el ciclo de vida de la sesión del usuario, los privilegios de rol (RBAC, control de acceso basado en roles) y la preferencia de tema (Noche/Día).

Este documento implementa la **decisión canónica de autenticación del frontend** (normativa BP-18 y BP-20 en `greenfield/00_normativa_buenas_practicas_y_auditoria.md`). Forma una cadena con:

| Pieza | Documento |
| :--- | :--- |
| Cliente HTTP, interceptor 401 y refresh único | [`services/api_client.md`](../services/api_client.md) |
| Catálogo de rutas (`ENDPOINTS.AUTH.*`) | [`services/endpoints_registry.md`](../services/endpoints_registry.md) |
| Protección de rutas y permisos | [`routing/protected_route.md`](../routing/protected_route.md) |
| Aviso de sesión vencida | [`modal/session_expiration_modal.md`](../modal/session_expiration_modal.md) |
| Formulario de ingreso | [`login/login_form.md`](../login/login_form.md) |

---

### 1. Reglas de seguridad de la sesión

| Regla | Nivel | Por qué |
| :--- | :--- | :--- |
| El **access token** (JWT de vida corta) se guarda **solo en memoria** (`tokenStore` del cliente HTTP). | DEBE | `localStorage`/`sessionStorage` son legibles por cualquier script inyectado (XSS); la memoria desaparece al cerrar la pestaña. |
| El **refresh token** viaja en una cookie `HttpOnly; Secure; SameSite=Lax` emitida por `POST /api/v1/auth/login/` y rotada por `POST /api/v1/auth/refresh/`. El frontend nunca lo lee ni lo envía en el cuerpo. | DEBE | JavaScript no puede leer una cookie `HttpOnly`; un XSS no puede robar el refresh token. |
| Las llamadas a `/auth/refresh/` y `/auth/logout/` envían la cabecera `X-CSRFToken` (leída de la cookie `csrftoken`, que por eso no es `HttpOnly`). | DEBE | Al autenticar por cookie, el refresh queda expuesto a CSRF (falsificación de peticiones entre sitios) si no se exige el token CSRF. |
| Al cargar la app, `AuthContext` intenta recuperar la sesión con `/auth/refresh/` (`withCredentials: true`). Si falla, el usuario queda como **no autenticado** (sin modal). | DEBE | Es la única forma de recuperar el access token tras recargar, ya que no se persiste. |
| Ningún dato de sesión (tokens, objeto usuario) se guarda en `localStorage`/`sessionStorage`. | DEBE | Evita sesiones "fantasma" y datos personales persistidos en el equipo. |
| `localStorage` solo guarda **preferencias no sensibles** (tema, anchos/visibilidad de columnas, documento recordado si el usuario lo marcó), con claves de `STORAGE_KEYS` (§2.1). | DEBE | Varias apps pueden compartir origen; las claves con prefijo de app evitan colisiones. |
| `logout()` llama a `POST /api/v1/auth/logout/`, que borra la cookie de refresh y lo invalida (blacklist). Es idempotente: si la red falla, el estado local se limpia igual. | DEBE | Cerrar sesión debe revocar el refresh en servidor, no solo olvidar el access token. |

**Requisitos del backend (Django + SimpleJWT o equivalente):** login devuelve en el cuerpo `{ "access": "<jwt>", "user": {...} }` y refresh devuelve `{ "access": "<jwt>" }`; ambos fijan en `Set-Cookie` la cookie `refresh_token` con `Path=/api/v1/auth/`. La raíz del backend se configura con `VITE_API_URL` **sin** sufijo `/api` (p. ej. `http://localhost:8000`), porque `ENDPOINTS` ya incluye `/api/v1/...`, `/fast/v1/...` y `/health/...`. Si frontend y API están en orígenes distintos, se requiere `CORS_ALLOW_CREDENTIALS = True` y un origen explícito en `CORS_ALLOWED_ORIGINS` (no `*`); con `SameSite=Lax` ambos deben ser del mismo sitio.

---

### 2. Dependencias del contexto

#### 2.1. Claves de almacenamiento (`src/config/storageKeys.ts`)

```ts
const APP = import.meta.env.VITE_APP_SLUG ?? 'app';

export const STORAGE_KEYS = {
  theme: `${APP}:theme`,
  rememberedDoc: `${APP}:remembered_doc`,
  columnWidths: (modulo: string) => `${APP}:${modulo}:col_widths`,
  visibleColumns: (modulo: string) => `${APP}:${modulo}:visible_columns`,
  pwaDismissed: `${APP}:pwa_dismissed`,
} as const;

/** Acceso a localStorage tolerante a modo privado o storage bloqueado. */
export const safeStorage = {
  get(key: string): string | null {
    try {
      return window.localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  set(key: string, value: string): void {
    try {
      window.localStorage.setItem(key, value);
    } catch {
      /* storage no disponible: la preferencia solo dura la sesión */
    }
  },
  remove(key: string): void {
    try {
      window.localStorage.removeItem(key);
    } catch {
      /* noop */
    }
  },
};
```

#### 2.2. Cliente HTTP

`api`, `tokenStore`, `refreshAccessToken`, `csrfHeaders` y `SESSION_EXPIRED_EVENT` se exportan desde `src/services/api.ts` (ver [`api_client.md`](../services/api_client.md)).

---

### 3. Implementación TypeScript de referencia (`src/context/AuthContext.tsx`)

> `AuthProvider` DEBE montarse dentro de `<BrowserRouter>`: al quedar `user = null`, `ProtectedRoute` redirige a `/login` conservando la ruta de origen.

```tsx
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import {
  api,
  csrfHeaders,
  refreshAccessToken,
  SESSION_EXPIRED_EVENT,
  tokenStore,
} from '../services/api';
import { ENDPOINTS } from '../services/endpoints';
import { STORAGE_KEYS, safeStorage } from '../config/storageKeys';
import { SessionExpirationModal } from '../components/modal/SessionExpirationModal';
import { showToast } from '../components/ui/ToastNotification';

/** Alineado con model/login/spec_model_usuario.md y el contrato de greenfield/pages/login/03. */
export interface AuthUser {
  id: number;
  numero_documento: string;
  nombre: string;
  apellidos: string;
  email: string;
  roles: string[];      // códigos de rol: 'ADMINISTRADOR', 'OPERADOR', ...
  permisos: string[];   // claves de permiso: 'usuarios.ver', 'dashboard.ver', ... (GET /api/v1/mis-permisos/)
  cargo?: string | null;
  sede?: string | null;
  is_active: boolean;
  debe_cambiar_clave: boolean;
  avatar_url: string | null;
  last_login?: string | null;
}

export interface LoginCredentials {
  numero_documento: string; // mismo campo que usa auth.username_field en endpoints_registry.json
  password: string;
}

interface LoginResponse {
  access: string;
  token_type: 'Bearer';
  expires_in: number;
  user: AuthUser;
}

export type Theme = 'dark' | 'light';

export interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  theme: Theme;
  login: (credentials: LoginCredentials) => Promise<AuthUser>;
  logout: (reason?: string) => Promise<void>;
  hasRole: (allowedRoles: string[]) => boolean;
  hasPermission: (permissionKey: string) => boolean;
  isAdmin: () => boolean;
  toggleTheme: () => void;
}

const ADMIN_ROLES = ['ADMIN', 'ADMINISTRADOR', 'SUPERADMIN'];
/** Margen para renovar el access token antes de que venza (ms). */
const REFRESH_MARGIN_MS = 60_000;

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/** Lee `exp` (segundos) del payload del JWT en memoria. No valida la firma: solo sirve para planificar. */
function getTokenExpiryMs(token: string): number | null {
  try {
    const payload = token.split('.')[1];
    if (!payload) return null;
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4);
    const { exp } = JSON.parse(atob(padded)) as { exp?: number };
    return typeof exp === 'number' ? exp * 1000 : null;
  } catch {
    return null;
  }
}

function readInitialTheme(): Theme {
  return safeStorage.get(STORAGE_KEYS.theme) === 'light' ? 'light' : 'dark';
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSessionExpired, setIsSessionExpired] = useState(false);
  const [theme, setTheme] = useState<Theme>(readInitialTheme);

  // 1. Tema: aplicar en el DOM (variables.css y Bootstrap) y persistir como preferencia
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-bs-theme', theme);
    safeStorage.set(STORAGE_KEYS.theme, theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  }, []);

  // 2. Arranque: recuperar sesión desde la cookie de refresh (sin storage)
  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        await refreshAccessToken(); // single-flight: seguro ante el doble montaje de StrictMode
        const { data } = await api.get<AuthUser>(ENDPOINTS.AUTH.ME);
        if (!cancelled) setUser(data);
      } catch {
        // Sin cookie válida = visitante no autenticado. No se muestra el modal.
        tokenStore.clear();
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  // 3. Detección reactiva: el interceptor 401 emite `session-expired` cuando el refresh falla
  useEffect(() => {
    const onExpired = () => setIsSessionExpired(true);
    window.addEventListener(SESSION_EXPIRED_EVENT, onExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, onExpired);
  }, []);

  // 4. Detección proactiva (BP-20): renovar antes de que venza el access token.
  //    Si la renovación falla, se avisa al usuario antes de que pierda trabajo.
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;

    const schedule = (token: string | null) => {
      if (timer) clearTimeout(timer);
      timer = undefined;
      if (!token) return;
      const expiresAt = getTokenExpiryMs(token);
      if (!expiresAt) return;
      const delay = Math.max(expiresAt - Date.now() - REFRESH_MARGIN_MS, 0);
      timer = setTimeout(() => {
        refreshAccessToken().catch(() => {
          tokenStore.clear();
          window.dispatchEvent(new CustomEvent(SESSION_EXPIRED_EVENT));
        });
      }, delay);
    };

    schedule(tokenStore.get());
    const unsubscribe = tokenStore.subscribe(schedule); // se reprograma en cada rotación

    return () => {
      unsubscribe();
      if (timer) clearTimeout(timer);
    };
  }, []);

  // 5. Inicio de sesión: el backend responde { access, user } y fija la cookie de refresh
  const login = useCallback(async (credentials: LoginCredentials): Promise<AuthUser> => {
    const { data } = await api.post<LoginResponse>(ENDPOINTS.AUTH.LOGIN, credentials);
    tokenStore.set(data.access);
    setUser(data.user);
    setIsSessionExpired(false);
    return data.user;
  }, []);

  // 6. Cierre de sesión idempotente (revoca en servidor y limpia memoria)
  const logout = useCallback(async (reason?: string): Promise<void> => {
    try {
      await api.post(ENDPOINTS.AUTH.LOGOUT, null, { headers: csrfHeaders() });
    } catch {
      /* Si la red falla, igual se limpia el estado local */
    } finally {
      tokenStore.clear();
      setUser(null);
      setIsSessionExpired(false);
    }
    if (reason) showToast.info('Sesión cerrada', { description: reason });
    // No se usa window.location: ProtectedRoute redirige a /login al quedar user = null.
  }, []);

  // 7. Utilidades RBAC
  const hasRole = useCallback(
    (allowedRoles: string[]): boolean => {
      const userRoles = new Set((user?.roles ?? []).map((r) => r.toUpperCase()));
      return allowedRoles.some((rol) => userRoles.has(rol.toUpperCase()));
    },
    [user],
  );

  const hasPermission = useCallback(
    (permissionKey: string): boolean => Boolean(user?.permisos?.includes(permissionKey)),
    [user],
  );

  const isAdmin = useCallback((): boolean => hasRole(ADMIN_ROLES), [hasRole]);

  const value = useMemo<AuthContextType>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading,
      theme,
      login,
      logout,
      hasRole,
      hasPermission,
      isAdmin,
      toggleTheme,
    }),
    [user, isLoading, theme, login, logout, hasRole, hasPermission, isAdmin, toggleTheme],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
      <SessionExpirationModal
        isOpen={isSessionExpired && user !== null}
        onConfirm={() => void logout()}
      />
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth debe utilizarse dentro de un AuthProvider');
  }
  return context;
};
```

---

### 4. Criterios de aceptación verificables

1. Tras iniciar sesión, `localStorage` y `sessionStorage` no contienen ningún token ni el objeto usuario (verificable en DevTools > Application).
2. Al recargar la página con la cookie de refresh vigente, el usuario sigue autenticado sin volver a escribir credenciales.
3. Con 5 peticiones simultáneas que reciben 401, se observa **un solo** `POST /api/v1/auth/refresh/` en la pestaña Red.
4. Si el refresh responde 401/403, aparece `SessionExpirationModal` una sola vez y no hay bucle de peticiones.
5. Tras `logout()`, `POST /api/v1/auth/refresh/` responde 401 (la cookie fue borrada e invalidada).
6. Al desmontar el `AuthProvider` no quedan listeners de `session-expired` ni temporizadores activos.
