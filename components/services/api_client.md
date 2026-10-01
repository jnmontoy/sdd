# Especificación de Servicio: Cliente HTTP Corporativo (`api.ts`)
## Ecosistema Jolifoods — Doble Instancia Django & FastAPI con Interceptores

El cliente HTTP estandarizado centraliza todas las comunicaciones hacia el backend. Implementa una **arquitectura de doble cliente Axios** (`api` para Django y `fastApi` para FastAPI con `/fast/`), auto-inyección de token Bearer en los encabezados, y manejo centralizado de respuestas y errores HTTP 401/403.

---

### 1. Requisitos de Negocio y Seguridad
1. **Doble Instancia Axios**:
   - `api`: Base URL configurada para endpoints Django clásicos (`/api/`).
   - `fastApi`: Base URL configurada para endpoints FastAPI de alto rendimiento (`/api/fast/`).
2. **Inyección Automática de Bearer Token**: Interceptor de request que obtiene `access_token` de `localStorage` (o memoria) y lo adjunta en `Authorization: Bearer <token>`.
3. **Manejo de Expiración de Sesión (401 Unauthorized)**:
   - Limpieza automática de tokens locales.
   - Redirección controlada a la página de login preservando la ruta previa (`?redirect=/...`) para reanudar el trabajo tras autenticarse.
4. **Manejo de Accesos Denegados (403 Forbidden)**: Notificación de falta de privilegios sin romper el ciclo de vida de la aplicación.
5. **Portabilidad Total**: Base URL configurable mediante variable de entorno `VITE_API_BASE_URL`.

---

### 2. Implementación TypeScript Canónica (`src/services/api.ts`)

```typescript
import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// 1. Obtener URL base de variables de entorno o fallback a ruta relativa del proxy Vite
const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

// 2. Cliente para Django Core (Auth, CRUD administrativo, migraciones)
export const api = axios.create({
  baseURL: `${API_BASE}/api/`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// 3. Cliente para FastAPI (Consultas masivas JSON, dashboards, reportes, Anti-N+1)
export const fastApi = axios.create({
  baseURL: `${API_BASE}/api/fast/`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// 4. Interceptor de Solicitud (Inyección de Token Bearer)
const authRequestInterceptor = (config: any) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

api.interceptors.request.use(authRequestInterceptor, (error: AxiosError) => Promise.reject(error));
fastApi.interceptors.request.use(authRequestInterceptor, (error: AxiosError) => Promise.reject(error));

// 5. Interceptor de Respuesta y Errores (401 Token Expirado / 403 No Autorizado)
const responseInterceptor = (response: AxiosResponse) => response;

const errorInterceptor = async (error: AxiosError) => {
  if (error.response) {
    const status = error.response.status;

    // Token inválido o expirado
    if (status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_info');

      // Evitar bucle si ya estamos en /login
      if (!window.location.pathname.includes('/login')) {
        const currentPath = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/login?redirect=${currentPath}`;
      }
    }

    // Permisos insuficientes (RBAC)
    if (status === 403) {
      console.warn('Acceso denegado a recurso protegido:', error.config?.url);
    }
  }

  return Promise.reject(error);
};

api.interceptors.response.use(responseInterceptor, errorInterceptor);
fastApi.interceptors.response.use(responseInterceptor, errorInterceptor);

export default api;
```
