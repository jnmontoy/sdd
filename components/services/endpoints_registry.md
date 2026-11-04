# Registro Centralizado de Endpoints (`endpoints.ts` y `endpoints_registry.json`)
## Componente de servicio y contratos — Spec-Driven Development (SDD)

Este estándar evita escribir URLs de endpoints directamente dentro de componentes visuales o vistas (p. ej. `fetch('/api/v1/usuarios/')` o `api.get('/api/v1/facturas/')`).

Todas las rutas del sistema se centralizan en un único registro, tanto en el frontend (`frontend/src/services/endpoints.ts`) como en el backend/pruebas (`backend/config/endpoints_registry.json`).

---

## 1. Regla: sin URLs escritas a mano en vistas (BP-09)

- **Regla:** las vistas, páginas, botones y paneles laterales **NO DEBEN** contener cadenas con rutas de endpoints; DEBEN consumir `ENDPOINTS`.
- **Por qué:** un cambio de versión o de ruta se hace en un solo archivo, y el validador automático puede recorrer el mismo catálogo que usa la aplicación.
- **Excepciones:** ninguna en código de aplicación. Las pruebas automáticas PUEDEN usar rutas literales para verificar el contrato.

```typescript
// Incorrecto:
const response = await api.get('/api/v1/usuarios/');

// Correcto:
import { ENDPOINTS } from '@/services/endpoints';
const response = await api.get(ENDPOINTS.USUARIOS.LISTA);
```

---

## 2. Implementación en frontend (`frontend/src/services/endpoints.ts`)

Las rutas son **absolutas desde la raíz del backend** (`/api/v1/...`, `/fast/v1/...`, `/health/...`). Por eso `VITE_API_URL` se configura sin sufijo `/api` (ver [`api_client.md`](./api_client.md)).

```typescript
/**
 * Catálogo centralizado de endpoints.
 * Todas las vistas consumen las rutas exclusivamente desde esta constante tipada.
 */
export const ENDPOINTS = {
  // 1. Diagnóstico y salud (públicos, servidos por FastAPI)
  HEALTH: {
    LIVE: '/health/live',
    READY: '/health/ready',
  },

  // 2. Autenticación y perfil
  AUTH: {
    LOGIN: '/api/v1/auth/login/',       // responde { access, user } + cookie HttpOnly refresh_token
    REFRESH: '/api/v1/auth/refresh/',   // lee la cookie refresh_token; exige X-CSRFToken; responde { access }
    LOGOUT: '/api/v1/auth/logout/',     // borra e invalida la cookie refresh_token
    ME: '/api/v1/auth/me/',
    RECOVERY: '/api/v1/auth/recovery/',
    CHANGE_PASSWORD: '/api/v1/auth/change-password/',
  },

  // 3. Administración y seguridad
  USUARIOS: {
    LISTA: '/api/v1/usuarios/',
    DETALLE: (id: string | number) => `/api/v1/usuarios/${id}/`,
    TOGGLE_STATUS: (id: string | number) => `/api/v1/usuarios/${id}/toggle-status/`,
  },
  ROLES: {
    LISTA: '/api/v1/roles/',
    MATRIZ_RBAC: '/api/v1/roles/matriz-permisos/',
  },
  AUDITORIA: {
    LOGS: '/api/v1/auditoria/',
    EXPORTAR_EXCEL: '/api/v1/auditoria/exportar-excel/',
  },

  // 4. Capa FastAPI (/fast)
  FAST: {
    HEALTH: '/fast/v1/health',
    METRICAS_KPI: '/fast/v1/metricas/kpi',
    TELEMETRIA: '/fast/v1/telemetria/resumen',
  },

  // 5. Telemetría de adopción
  TELEMETRIA: {
    FEEDBACK: '/api/v1/telemetria/feedback/',
    METRICAS_USO: '/api/v1/telemetria/metricas-uso/',
  },
} as const;

export type EndpointsType = typeof ENDPOINTS;
```

---

## 3. Registro para pruebas automáticas (`backend/config/endpoints_registry.json`)

El validador `pruebas/validate_endpoints.py` (fuente en `.sdd/stack/validate_endpoints.py`) lee este manifiesto declarativo en lugar de inspeccionar vistas. La plantilla completa está en `.sdd/stack/endpoints_registry_template.json`; extracto:

```json
{
  "project_name": "mi_proyecto",
  "version": "1.0.0",
  "auth": {
    "login_path": "/api/v1/auth/login/",
    "username_field": "numero_documento",
    "password_field": "password",
    "token_field": "access"
  },
  "endpoints": [
    {
      "name": "Salud: vida",
      "path": "/health/live",
      "method": "GET",
      "expected_status": 200,
      "auth_required": false,
      "max_latency_ms": 200
    },
    {
      "name": "Salud: disponibilidad (BD + Redis)",
      "path": "/health/ready",
      "method": "GET",
      "expected_status": 200,
      "auth_required": false,
      "max_latency_ms": 500
    },
    {
      "name": "Salud: capa FastAPI",
      "path": "/fast/v1/health",
      "method": "GET",
      "expected_status": 200,
      "auth_required": false,
      "max_latency_ms": 200
    },
    {
      "name": "Listado de usuarios",
      "path": "/api/v1/usuarios/",
      "method": "GET",
      "expected_status": 200,
      "auth_required": true
    }
  ]
}
```

Los valores de `max_latency_ms` son metas de partida; cada proyecto DEBERÍA ajustarlos a mediciones reales de su entorno.

---

## 4. Uso en automatización y auditoría

1. **Verificación en un solo comando** (la contraseña de login se lee de la variable de entorno `SDD_LOGIN_PASSWORD`, nunca por argumento):
   ```powershell
   $env:SDD_LOGIN_PASSWORD = "<CONTRASEÑA>"
   .\.venv\Scripts\python.exe pruebas\validate_endpoints.py --base-url http://localhost:8000 --login-user 1000000001
   ```
   En Linux/macOS: `./.venv/bin/python pruebas/validate_endpoints.py --base-url http://localhost:8000`.
2. **Refactorización segura:** si un endpoint cambia de versión (`/api/v1/` a `/api/v2/`), se actualiza `endpoints.ts` y el registro JSON; las vistas no cambian.
3. **Exportación de cURL:** `--export-curls curls.sh` genera los comandos cURL de todos los endpoints registrados, sin secretos (usan `$SDD_TOKEN` y `$SDD_LOGIN_PASSWORD`).
4. **Cobertura:** el validador solo prueba lo que está en el registro; mantenerlo al día es parte de la definición de terminado de cada endpoint nuevo.
