# Stack técnico y plantillas de infraestructura

Plantillas que `init_project.py` copia a cada proyecto nuevo para que nazca con la misma base: backend Django + FastAPI, frontend React + Vite, Docker, pruebas y guía para agentes de IA.

---

## 1. Arquitectura

| Capa | Tecnología | Documento |
| :--- | :--- | :--- |
| Seguridad, usuarios, CRUD | Django 5 + Django REST Framework + SimpleJWT | [`settings_security_template.py`](./settings_security_template.py) |
| Lecturas de alto volumen | FastAPI + Pydantic v2 bajo `/fast` | [`asgi_hybrid_architecture.md`](./asgi_hybrid_architecture.md) |
| Tareas en segundo plano | Celery + Redis | [`celery_redis_architecture.md`](./celery_redis_architecture.md) |
| Frontend | React 19 + Vite + TypeScript + Bootstrap 5 + `variables.css` | [`../components/`](../components/README.md) |
| Datos | PostgreSQL 16 | [`../model/`](../model/README.md) |

---

## 2. Archivos

| Archivo | Destino en el proyecto | Qué hace |
| :--- | :--- | :--- |
| [`init_project.py`](./init_project.py) / [`init_project.ps1`](./init_project.ps1) | — | Generador del proyecto: carpetas, plantillas, `settings.py` mínimo, `.env` con secretos aleatorios, `.venv` y andamiaje de pruebas. |
| [`settings_security_template.py`](./settings_security_template.py) | `backend/config/settings_security.py` | BP-01 a BP-08: secretos, hosts, CORS, limitación de tasa, denegar por defecto, cabeceras, cookies, rutas. |
| [`asgi_template.py`](./asgi_template.py) | `backend/config/asgi.py` | Enrutador ASGI: `/fast` y `/health` a FastAPI, el resto a Django. |
| [`healthcheck.py`](./healthcheck.py) | `backend/config/healthcheck.py` | `GET /health/live` y `GET /health/ready` (503 si falla la BD o Redis). |
| [`seed_data.py`](./seed_data.py) | `backend/seed_data.py` | Administrador inicial, sin contraseña por defecto en el código. |
| [`entrypoint.sh`](./entrypoint.sh) | `backend/entrypoint.sh` | Espera la BD, migra, crea la semilla (solo con `SEED_ON_START=true`) y recolecta estáticos. |
| [`Dockerfile.backend`](./Dockerfile.backend) | `backend/Dockerfile` | Imagen en dos etapas, ejecutada con un usuario sin privilegios y con `HEALTHCHECK`. |
| [`Dockerfile.frontend`](./Dockerfile.frontend) | `frontend/Dockerfile` | Etapa `dev` (Vite) y etapa final con Nginx sin privilegios. |
| [`docker-compose.yml`](./docker-compose.yml) | `docker-compose.yml` | Ambiente de **desarrollo** con healthchecks en `db`, `redis` y `backend`. |
| [`requirements.txt`](./requirements.txt) / [`requirements-dev.txt`](./requirements-dev.txt) | `backend/` | Dependencias de producción, y de pruebas y análisis. |
| [`package.json`](./package.json) | `frontend/package.json` | React, Vite, Vitest, ESLint (con reglas de hooks y accesibilidad). |
| [`endpoints_registry_template.json`](./endpoints_registry_template.json) | `backend/config/endpoints_registry.json` | Registro único de endpoints (BP-09). |
| [`validate_endpoints.py`](./validate_endpoints.py) | `pruebas/validate_endpoints.py` | Prueba de humo HTTP del registro, con código de salida para CI. |
| [`e2e_testing_guide.md`](./e2e_testing_guide.md) | — | Cómo escribir pruebas de humo y E2E. |
| [`agent_harness/`](./agent_harness/AGENTS.md) | `AGENTS.md`, `.cursorrules` | Reglas resumidas para asistentes de IA. |

---

## 3. Crear un proyecto

```powershell
python .sdd\stack\init_project.py "Nombre del proyecto"
```

El generador usa solo la librería estándar. El Python del sistema sirve únicamente para ejecutarlo y crear `.venv`; todas las dependencias se instalan **dentro** de `.venv` (BP-15). Después:

```powershell
cd nombre_del_proyecto
docker compose up --build                                   # db, redis, backend, celery y frontend
.\.venv\Scripts\python.exe -m pytest                        # pruebas en pruebas/
.\.venv\Scripts\python.exe pruebas\validate_endpoints.py    # humo HTTP con la app levantada
```

---

## 4. Validador de endpoints

```powershell
# Sin login: salud, deny-by-default y cabeceras de seguridad
.\.venv\Scripts\python.exe pruebas\validate_endpoints.py --base-url http://localhost:8000

# Con login: la contraseña va en una variable de entorno, nunca en la línea de comandos
$env:SDD_LOGIN_PASSWORD = "<contraseña>"
.\.venv\Scripts\python.exe pruebas\validate_endpoints.py --login-user 1000000001 --samples 20 --json-report reporte_endpoints.json
```

| Opción | Efecto |
| :--- | :--- |
| `--samples N` | Repite cada GET N veces y compara el percentil 95 contra `max_latency_ms`. |
| `--sin-puerta-latencia` | Reporta la latencia sin fallar por ella (útil contra servidores remotos). |
| `--incluir-mutaciones` | Ejecuta endpoints con `"mutates": true`. Úselo solo en ambientes de prueba. |
| `--export-curls archivo.sh` | Genera los cURL; los secretos quedan como `$SDD_TOKEN` y `$SDD_LOGIN_PASSWORD`. |

Por cada endpoint con `auth_required: true` el validador verifica además que **sin** token responda 401/403 (BP-05). Termina con código 1 si algo falla.

El validador tiene pruebas propias en [`../pruebas/test_validate_endpoints.py`](../pruebas/test_validate_endpoints.py).

---

## 5. Diferencias entre desarrollo y producción

`docker-compose.yml` es para desarrollo. En producción:

- sin `--reload` y sin montar `./backend` como volumen;
- frontend con la etapa final de `Dockerfile.frontend` (Nginx);
- `db` y `redis` sin puertos publicados;
- `DEBUG=false`, `SEED_ON_START=false` y secretos inyectados por el orquestador, no por un `.env` versionado;
- HSTS con `includeSubDomains`/`preload` solo cuando todo el dominio sirva HTTPS.
