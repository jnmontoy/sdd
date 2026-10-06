# Stack Tecnológico Canónico y Dockerización — Jolifoods
## Spec-Driven Development (SDD)

Este directorio define la **infraestructura técnica base** para levantar cualquier nuevo proyecto o módulo en el ecosistema **Jolifoods** sin tener que reinstalar, buscar librerías de terceros o resolver dependencias faltantes.

---

## 1. Arquitectura del Stack Técnico

### Backend de Alto Rendimiento (Django + FastAPI Híbrido)
- **Django (ORM, Migraciones y Admin)**:
  - Manejo robusto del modelo de datos relacional y transaccional.
  - Migraciones seguras y administración nativa.
- **FastAPI (ASGI Engine)**:
  - Servidor ASGI montado en `config/asgi.py` ejecutado sobre **Uvicorn Worker**.
  - Entrega de JSON ultra-rápida serializada con esquemas **Pydantic v2**, minimizando drásticamente la latencia en comparación con serializadores tradicionales.
- **Buenas Prácticas Backend & Anti-N+1**:
  - **Mitigación N+1**: Uso mandatorio de `select_related()` (claves foráneas en un único JOIN) y `prefetch_related()` (relaciones Many-to-Many o inversas agrupadas) en todas las consultas de usuarios, roles, sedes y auditoría.
  - Proyección de atributos mínimos con `.only()` y validación estricta de payloads.
  - **Seguridad**: Cookies seguras `HttpOnly`, `SameSite=Lax`, `Secure`, Rate Limiting distribuido con **Redis** y soporte SSO Microsoft 365 con **MSAL**.

### Frontend Moderno y Reactivo
- **React 19 + Vite**: Compilación ultra-rápida, HMR instantáneo y empaquetado optimizado.
- **TypeScript**: Tipado estático completo de contratos de API, payloads de autenticación y estados globales.
- **Bootstrap 5 + CSS Puro (`variables.css`)**:
  - Estructuración ergonómica y responsiva con Bootstrap.
  - Diseño visual corporativo gobernado por [`variables.css`](../components/variables.css) con conmutación nativa de **Modo Noche** y **Modo Día** mediante variables CSS puras.
- **Librerías de Soporte UI**: Lucide React (iconografía moderna), Sonner (toasts de notificación), React Hook Form + Zod (validación estricta de formularios).

---

## 2. Dockerización Completa Multi-Contenedor

El archivo [`docker-compose.yml`](./docker-compose.yml) orquesta la arquitectura completa en 4 servicios aislados y listos para producción o desarrollo:

| Servicio | Imagen / Contexto | Puerto Expuesto | Propósito |
| :--- | :--- | :--- | :--- |
| **`db`** | `postgres:16-alpine` | `5432:5432` | Base de datos relacional principal con volúmenes persistentes y healthchecks automáticos. |
| **`redis`** | `redis:7-alpine` | `6379:6379` | Caché en memoria, listas negras de tokens JWT, control de sesiones y Rate Limiting anti-fuerza bruta. |
| **`backend`** | `./backend/Dockerfile` (`python:3.11-slim`) | `8000:8000` | Motor híbrido Django + FastAPI sirviendo endpoints JSON con recarga en caliente (`uvicorn --reload`). |
| **`frontend`** | `./frontend/Dockerfile` (`node:20-alpine`) | `5173:5173` | Aplicación SPA React + Vite + TypeScript con volúmenes montados para desarrollo ágil. |

---

## 3. Catálogo de Dependencias Pre-Cargadas

### Backend: [`requirements.txt`](./requirements.txt)

> 🚨 **ADVERTENCIA CRÍTICA DE AISLAMIENTO**:  
> **NUNCA ejecutes `pip install` sobre el Python del equipo**. Debes crear y activar primero el entorno virtual `.venv` (`python -m venv .venv`) o utilizar el script automatizado [`init_project.py`](./init_project.py) / [`init_project.ps1`](./init_project.ps1), el cual crea el entorno `.venv` e instala automáticamente las dependencias sin contaminar el sistema operativo del anfitrión.

Reúne exactamente lo que más se usa en los proyectos del ecosistema Jolifoods para que nunca falten librerías al inicializar:

- **Frameworks & ASGI**: `Django`, `djangorestframework`, `djangorestframework_simplejwt`, `fastapi`, `uvicorn[standard]`, `gunicorn`, `asgiref`.
- **Bases de Datos**: `psycopg2-binary`, `PyMySQL`, `sqlparse`.
- **Caché y Tareas**: `redis`, `django-redis`, `celery`.
- **Seguridad e Identidad (Django Core)**: `cryptography`, `bcrypt`, `PyJWT`, `msal` (Microsoft 365 / Azure AD), `django-cors-headers`.
- **Validación y Entrega Ultra Rápida JSON (FastAPI Engine)**: `pydantic>=2.8.0`, `pydantic-settings`, `orjson>=3.10.0` (serialización nativa en C), `msgpack`.
- **Herramientas de Negocio**: `openpyxl` (Excel), `fpdf2` & `weasyprint` (PDFs corporativos), `Pillow` (imágenes y avatares), `httpx` & `requests` (HTTP clients).

### Frontend: [`package.json`](./package.json)
- `react`, `react-dom`, `react-router-dom`, `bootstrap`, `lucide-react`, `sonner`, `zod`, `react-hook-form`, `@hookform/resolvers`, `framer-motion`, `xlsx`.
- Entorno de desarrollo con `typescript`, `@types/*`, `@vitejs/plugin-react` y `vite`.

---

## 4. Herramientas de Automatización y Blindaje de Seguridad

| **[`entrypoint.sh`](./entrypoint.sh)** | Orquestador de arranque del backend: espera PostgreSQL con `pg_isready`, ejecuta migraciones y levanta Uvicorn. |
| **[`seed_data.py`](./seed_data.py)** | Carga de datos semilla idempotente que genera el usuario administrador de desarrollo, roles y sede principal. |
| **[`settings_security_template.py`](./settings_security_template.py)** | Configuración Django que implementa al 100% las 10 Buenas Prácticas evaluadas en auditoría (aislamiento, hosts, CORS, throttling, Deny by Default, cabeceras HTTP, rutas 100% relativas con `BASE_DIR`, carpeta `backend/media/`, centralización de endpoints y exención mock). |
| **[`healthcheck.py`](./healthcheck.py)** | Sondas de Liveness y Readiness para FastAPI que verifican latencia y conectividad con PostgreSQL y Redis. |
| **[`celery_redis_architecture.md`](./celery_redis_architecture.md)** | Arquitectura de tareas asíncronas y llamados constantes en background con Redis y Celery (worker + beat). |
| **[`init_project.py`](./init_project.py)** | Script de inicialización que automatiza el Paso 0, crea el entorno virtual `.venv` con `pip`, la carpeta `backend/media/` con `.gitkeep`, inyecta branding Jolifoods, `.dockerignore`, `.vscode/settings.json`, `endpoints_registry.json` y copia `validate_endpoints.py`. |
| **[`init_project.ps1`](./init_project.ps1)** | Wrapper nativo de PowerShell para ejecutar el scaffolding en Windows con un clic. |
| **[`endpoints_registry_template.json`](./endpoints_registry_template.json)** | Registro centralizado de rutas del sistema (contratos, métodos y roles) para eliminar URLs quemadas en vistas. |
| **[`validate_endpoints.py`](./validate_endpoints.py)** | Validador universal de endpoints autónomo en Python puro, compatible con Windows UTF-8/cp1252, exporta cURLs y genera Quality Gate CI/CD. |
| **[`00_normativa_buenas_practicas_y_auditoria.md`](../greenfield/00_normativa_buenas_practicas_y_auditoria.md)** | Normativa maestra que prescribe los criterios de conformidad para que todo nuevo proyecto obtenga 100/100 en auditorías. |


