# Especificación de Servicio: Cliente HTTP Corporativo (`api.ts`)
## Clientes Axios para Django y FastAPI con renovación de sesión

El cliente HTTP centraliza todas las comunicaciones con el backend. Implementa la parte de red de la **decisión canónica de autenticación** (BP-18/BP-20, ver [`context/auth_context.md`](../context/auth_context.md)): access token en memoria, refresh token en cookie `HttpOnly`, un único refresh concurrente y aviso de sesión vencida por evento.

---

### 1. Reglas

| Regla | Nivel | Por qué |
| :--- | :--- | :--- |
| Toda URL se toma de `ENDPOINTS` ([`endpoints_registry.md`](./endpoints_registry.md)); no hay rutas escritas a mano en vistas. | DEBE | Un cambio de versión de API se hace en un solo archivo. |
| `baseURL` es `import.meta.env.VITE_API_URL` = raíz del backend **sin** `/api` (p. ej. `http://localhost:8000`); vacío = mismo origen / proxy de Vite. | DEBE | `ENDPOINTS` ya incluye `/api/v1/...`, `/fast/v1/...` y `/health/...`; un sufijo duplicaría el prefijo. |
| Los clientes usan `withCredentials: true`, `xsrfCookieName: 'csrftoken'` y `xsrfHeaderName: 'X-CSRFToken'`. | DEBE | Sin credenciales el navegador no envía la cookie `refresh_token`; el refresh exige cabecera CSRF. |
| El access token vive en `tokenStore` (variable de módulo). Nunca en `localStorage`/`sessionStorage`. | DEBE | Reduce el impacto de un XSS. |
| Ante un 401 se intenta **un único** refresh compartido por todas las peticiones concurrentes; cada petición se reintenta **una sola vez**. | DEBE | Evita tormentas de refresh y bucles 401 infinitos. |
| Las rutas de autenticación (`login`, `refresh`, `logout`) no disparan refresh al recibir 401. | DEBE | Un 401 en login significa credenciales inválidas, no sesión vencida. |
| Si el refresh falla, se limpia el token y se emite el evento `session-expired` (lo escucha `AuthContext`, que muestra `SessionExpirationModal`). No se redirige con `window.location`. | DEBE | Se conserva el contexto de trabajo del usuario y se evitan recargas completas. |
| Un 403 se devuelve al llamador para que muestre un aviso; no cierra la sesión. | DEBERÍA | Falta de permiso no es sesión vencida. |

---

### 2. Implementación TypeScript de referencia (`src/services/api.ts`)

```typescript
import axios, {
  AxiosError,
  AxiosHeaders,
  type AxiosInstance,
  type CreateAxiosDefaults,
  type InternalAxiosRequestConfig,
} from 'axios';
import { ENDPOINTS } from './endpoints';

export const SESSION_EXPIRED_EVENT = 'session-expired';

// ---------------------------------------------------------------------------
// 1. Almacén del access token en memoria (con suscripción para reprogramar avisos)
// ---------------------------------------------------------------------------
type TokenListener = (token: string | null) => void;
let accessToken: string | null = null;
const listeners = new Set<TokenListener>();

export const tokenStore = {
  get: (): string | null => accessToken,
  set(token: string | null): void {
    accessToken = token;
    listeners.forEach((listener) => listener(token));
  },
  clear(): void {
    tokenStore.set(null);
  },
  subscribe(listener: TokenListener): () => void {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  },
};

// ---------------------------------------------------------------------------
// 2. CSRF: la cookie `csrftoken` NO es HttpOnly para poder leerla aquí
// ---------------------------------------------------------------------------
function readCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

/** Cabecera explícita: axios solo agrega X-CSRFToken automáticamente en peticiones del mismo origen. */
export function csrfHeaders(): Record<string, string> {
  const token = readCookie('csrftoken');
  return token ? { 'X-CSRFToken': token } : {};
}

// ---------------------------------------------------------------------------
// 3. Instancias
// ---------------------------------------------------------------------------
const baseConfig: CreateAxiosDefaults = {
  baseURL: import.meta.env.VITE_API_URL ?? '',
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
};

/** Django: rutas ENDPOINTS que empiezan por /api/v1/ */
export const api = axios.create(baseConfig);
/** FastAPI: rutas ENDPOINTS.FAST.* (/fast/v1/...). Timeout mayor para reportes y consultas masivas. */
export const fastApi = axios.create({ ...baseConfig, timeout: 60_000 });
/** Cliente sin interceptores, exclusivo para el refresh (evita recursión). */
const refreshClient = axios.create(baseConfig);

// ---------------------------------------------------------------------------
// 4. Refresh único (single-flight): todas las peticiones concurrentes esperan la misma promesa
// ---------------------------------------------------------------------------
let refreshPromise: Promise<string> | null = null;

export function refreshAccessToken(): Promise<string> {
  if (!refreshPromise) {
    refreshPromise = refreshClient
      // Sin cuerpo: el refresh token viaja en la cookie HttpOnly `refresh_token`
      .post<{ access: string }>(ENDPOINTS.AUTH.REFRESH, null, { headers: csrfHeaders() })
      .then(({ data }) => {
        tokenStore.set(data.access);
        return data.access;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

// ---------------------------------------------------------------------------
// 5. Interceptores
// ---------------------------------------------------------------------------
type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean };

const AUTH_PATHS: readonly string[] = [
  ENDPOINTS.AUTH.LOGIN,
  ENDPOINTS.AUTH.REFRESH,
  ENDPOINTS.AUTH.LOGOUT,
];

function isAuthRequest(config: InternalAxiosRequestConfig): boolean {
  const url = config.url ?? '';
  return AUTH_PATHS.some((path) => url.includes(path));
}

function attachInterceptors(instance: AxiosInstance): void {
  instance.interceptors.request.use((config) => {
    const token = tokenStore.get();
    if (token) {
      config.headers = AxiosHeaders.from(config.headers);
      config.headers.set('Authorization', `Bearer ${token}`);
    }
    return config;
  });

  instance.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const original = error.config as RetriableConfig | undefined;

      if (error.response?.status !== 401 || !original || original._retry || isAuthRequest(original)) {
        return Promise.reject(error); // 403, 5xx, red, etc.: los maneja el llamador
      }

      original._retry = true; // una sola reintentada por petición
      try {
        const newAccess = await refreshAccessToken();
        original.headers.set('Authorization', `Bearer ${newAccess}`);
        return instance(original);
      } catch (refreshError) {
        tokenStore.clear();
        // Idempotente: AuthContext solo cambia un booleano, aunque lleguen varios eventos
        window.dispatchEvent(new CustomEvent(SESSION_EXPIRED_EVENT));
        return Promise.reject(refreshError);
      }
    },
  );
}

attachInterceptors(api);
attachInterceptors(fastApi);

export default api;
```

---

### 3. Variables de entorno (`.env.example` del frontend)

```dotenv
# Raíz del backend SIN sufijo /api. Vacío = mismo origen (proxy de Vite en desarrollo).
VITE_API_URL=http://localhost:8000
# Prefijo de las claves de localStorage (ver STORAGE_KEYS)
VITE_APP_SLUG=mi_app
```

---

### 4. Criterios de aceptación verificables

1. Ninguna petición sale sin `withCredentials`; la cookie `refresh_token` aparece solo en peticiones a `/api/v1/auth/` (por su `Path`).
2. Con varias peticiones concurrentes que reciben 401, hay un solo `POST /api/v1/auth/refresh/` y todas se reintentan con el nuevo token.
3. Si el refresh falla, cada petición original se rechaza una sola vez y se emite `session-expired`; no hay nuevas peticiones en bucle.
4. Un 401 en `POST /api/v1/auth/login/` se muestra como "credenciales incorrectas" y no dispara refresh.
