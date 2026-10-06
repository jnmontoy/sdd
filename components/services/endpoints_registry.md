# Registro Centralizado de Endpoints (`endpoints.ts` y `endpoints_registry.json`)
## Componente de Servicio y Contratos — Spec-Driven Development (SDD)

Este estándar erradica la práctica nociva de escribir URLs de endpoints quemadas directamente dentro de los componentes visuales o vistas (ej. `fetch('/api/v1/usuarios/')` o `api.get('/api/v1/facturas/')`). 

Bajo la metodología SDD, **todas las rutas del sistema se centralizan en un único archivo de registro** tanto en el frontend (`src/services/endpoints.ts`) como en el backend/testing (`backend/config/endpoints_registry.json`).

---

## 1. La Regla Inflexible de Cero URLs Quemadas en Vistas

> **PROHIBICIÓN TERMINANTE (BP-09)**:
> Queda estrictamente prohibido escribir cadenas de texto con rutas de endpoints en vistas React, páginas, botones o paneles laterales.
> 
> ```typescript
> // ❌ INCORRECTO - PENALIZADO EN AUDITORÍA:
> const response = await api.get('/api/v1/usuarios/lista/');
> 
> // ✅ CORRECTO - CANÓNICO SDD:
> import { ENDPOINTS } from '@services/endpoints';
> const response = await api.get(ENDPOINTS.USUARIOS.LISTA);
> ```

---

## 2. Implementación Canónica en Frontend (`src/services/endpoints.ts`)

```typescript
/**
 * Catálogo Centralizado de Endpoints — Jolifoods / SDD
 * Todas las vistas deben consumir las rutas exclusivamente desde esta constante tipada.
 */

export const ENDPOINTS = {
  // 1. Diagnóstico y Salud
  HEALTH: {
    LIVE: '/health/live',
    READY: '/health/ready',
  },

  // 2. Autenticación y Perfil
  AUTH: {
    LOGIN: '/api/v1/auth/login/',
    LOGOUT: '/api/v1/auth/logout/',
    REFRESH: '/api/v1/auth/refresh/',
    ME: '/api/v1/auth/me/',
    RECOVERY: '/api/v1/auth/recovery/',
    CHANGE_PASSWORD: '/api/v1/auth/change-password/',
  },

  // 3. Administración y Seguridad
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

  // 4. Capa de Alto Rendimiento ASGI FastAPI (/fast)
  FAST: {
    HEALTH: '/fast/v1/health',
    METRICAS_KPI: '/fast/v1/metricas/kpi',
    TELEMETRIA: '/fast/v1/telemetria/resumen',
  },

  // 5. Telemetría de Adopción y Mejora Continua
  TELEMETRIA: {
    FEEDBACK: '/api/v1/telemetria/feedback/',
    METRICAS_USO: '/api/v1/telemetria/metricas-uso/',
  },
} as const;

export type EndpointsType = typeof ENDPOINTS;
```

---

## 3. Registro Centralizado para Testing Automático (`backend/config/endpoints_registry.json`)

Para que el script `validate_endpoints.py` no tenga que inspeccionar vistas aisladas, se genera este manifiesto JSON con la lista declarativa de todos los endpoints:

```json
{
  "project_name": "jolifoods_core",
  "version": "1.0.0",
  "endpoints": [
    {
      "name": "Health Liveness",
      "path": "/health/live",
      "method": "GET",
      "expected_status": 200,
      "auth_required": false
    },
    {
      "name": "Health Readiness",
      "path": "/health/ready",
      "method": "GET",
      "expected_status": 200,
      "auth_required": false
    },
    {
      "name": "Listado de Usuarios",
      "path": "/api/v1/usuarios/",
      "method": "GET",
      "expected_status": 200,
      "auth_required": true
    },
    {
      "name": "FastAPI Diagnostics",
      "path": "/fast/v1/health",
      "method": "GET",
      "expected_status": 200,
      "max_latency_ms": 45
    }
  ]
}
```

---

## 4. Beneficios para la Automatización y Auditoría
1. **Verificación en un Solo Comando**: `python backend/validate_endpoints.py` lee directamente este archivo y prueba el 100% de las rutas sin necesidad de explorar vistas.
2. **Refactorización Segura**: Si un endpoint cambia de versión (`/api/v1/` a `/api/v2/`), se actualiza en una sola línea en `endpoints.ts` y toda la aplicación queda sincronizada sin errores 404.
3. **Generación Instantánea de cURLs**: Cualquier desarrollador o auditor genera la suite completa de comandos cURL con `--export-curls curls.sh` directamente desde el registro.
