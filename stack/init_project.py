#!/usr/bin/env python3
"""
Generador de proyectos a partir del SDD.

Crea la estructura base de un proyecto (backend Django + FastAPI, frontend React + Vite,
pruebas, especificaciones y memoria) en la carpeta hermana de `.sdd/`.

Uso (solo librería estándar; se puede ejecutar con el Python del sistema porque NO instala
nada fuera del entorno virtual que crea):
    python .sdd/stack/init_project.py "Nombre del proyecto"
    python .sdd/stack/init_project.py --name "Nombre" --sin-instalar
"""
from __future__ import annotations

import argparse
import re
import secrets
import shutil
import subprocess
import sys
import venv
from pathlib import Path

SDD_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = SDD_DIR.parent
STACK_DIR = SDD_DIR / "stack"


def sanitize_slug(name: str) -> str:
    """'Gestión de Turnos' -> 'gestion_de_turnos' (apto para carpetas y contenedores)."""
    replacements = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")
    clean = re.sub(r"[^a-zA-Z0-9_\-\s]", "", name.translate(replacements)).strip().lower()
    return re.sub(r"[\s\-]+", "_", clean)


def copy(src: Path, dest: Path, overwrite: bool = True) -> None:
    if not src.exists():
        print(f"   [AVISO] No existe la plantilla {src.relative_to(SDD_DIR)}; se omite.")
        return
    if dest.exists() and not overwrite:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def write(path: Path, content: str, overwrite: bool = True) -> None:
    if path.exists() and not overwrite:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_tree_files(src_dir: Path, dest_dir: Path) -> None:
    if not src_dir.exists():
        return
    for item in src_dir.rglob("*"):
        if item.is_file():
            copy(item, dest_dir / item.relative_to(src_dir), overwrite=False)


# ----------------------------------------------------------------------------- contenidos
ENDPOINTS_TS = """/**
 * Catálogo centralizado de endpoints (BP-09). Las vistas importan rutas desde aquí;
 * deben coincidir con backend/config/endpoints_registry.json.
 */
export const ENDPOINTS = {
  HEALTH: { LIVE: '/health/live', READY: '/health/ready' },
  AUTH: {
    LOGIN: '/api/v1/auth/login/',
    REFRESH: '/api/v1/auth/refresh/',
    LOGOUT: '/api/v1/auth/logout/',
    ME: '/api/v1/auth/me/',
    MIS_PERMISOS: '/api/v1/mis-permisos/',
  },
  USUARIOS: {
    LISTA: '/api/v1/usuarios/',
    DETALLE: (id: string | number) => `/api/v1/usuarios/${id}/`,
  },
  ROLES: { LISTA: '/api/v1/roles/' },
  AUDITORIA: { LISTA: '/api/v1/auditoria/' },
  FAST: { HEALTH: '/fast/v1/health' },
  TELEMETRIA: { FEEDBACK: '/api/v1/telemetria/feedback/' },
} as const;
"""

STORAGE_KEYS_TS = """/**
 * Claves de almacenamiento del navegador. Llevan el slug de la app porque varias apps
 * pueden compartir origen (mismo dominio, distinta ruta) y pisarse las preferencias.
 * Solo preferencias no sensibles: los tokens NUNCA van a localStorage/sessionStorage.
 */
const APP = import.meta.env.VITE_APP_SLUG ?? 'app';

export const STORAGE_KEYS = {
  theme: `${APP}:theme`,
  rememberedDoc: `${APP}:remembered_doc`,
  columnWidths: (modulo: string) => `${APP}:${modulo}:col_widths`,
  visibleColumns: (modulo: string) => `${APP}:${modulo}:visible_columns`,
  pwaDismissed: `${APP}:pwa_dismissed`,
} as const;

/** Acceso tolerante a fallos (modo privado o almacenamiento bloqueado). */
export function readStorage(key: string): string | null {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

export function writeStorage(key: string, value: string | null): void {
  try {
    if (value === null) window.localStorage.removeItem(key);
    else window.localStorage.setItem(key, value);
  } catch {
    /* sin almacenamiento disponible: la preferencia no se recuerda */
  }
}
"""

FASTAPI_APP_PY = '''"""App FastAPI montada bajo /fast por config/asgi.py (ver .sdd/stack/asgi_template.py)."""
from fastapi import FastAPI
from pydantic import BaseModel

from config.healthcheck import router as health_router

# Declare siempre el tipo de respuesta (modelo Pydantic o anotación de retorno): FastAPI serializa
# entonces directamente con Pydantic, que es lo más rápido. No hace falta ORJSONResponse (obsoleto).
app = FastAPI(title="API de lectura", docs_url="/docs")
app.include_router(health_router)  # /health/live y /health/ready


class Salud(BaseModel):
    status: str


@app.get("/v1/health", tags=["Salud"])
async def fast_health() -> Salud:
    return Salud(status="ok")
'''

MANAGE_PY = '''#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
'''

SETTINGS_PY = '''"""Configuración Django mínima. Seguridad en settings_security.py (BP-01..BP-08)."""
import os

from .settings_security import *  # noqa: F401,F403
from .settings_security import BASE_DIR

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "apps.auth_core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "app_db"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
        "CONN_HEALTH_CHECKS": True,
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2")
CELERY_TIMEZONE = TIME_ZONE
'''

URLS_PY = '''from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("api/v1/", include("apps.auth_core.urls")),
]
'''

CELERY_PY = '''import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
'''

CONFIG_INIT_PY = '''from .celery import app as celery_app

__all__ = ("celery_app",)
'''

AUTH_CORE_APPS_PY = '''from django.apps import AppConfig


class AuthCoreConfig(AppConfig):
    name = "apps.auth_core"
    verbose_name = "Autenticación y usuarios"
'''

PYTEST_INI = """[pytest]
# Las pruebas viven en pruebas/ (BP-17); el código de producción en backend/.
testpaths = pruebas
pythonpath = backend
DJANGO_SETTINGS_MODULE = config.settings
# Por defecto se excluyen las E2E (necesitan la app levantada); `pytest -m e2e` las ejecuta,
# porque el -m de la línea de comandos reemplaza al de addopts.
addopts = -ra --strict-markers -m "not e2e"
markers =
    e2e: pruebas de extremo a extremo (requieren la app levantada)
"""

CONFTEST_PY = '''"""Fixtures compartidas. Ver .sdd/greenfield/11_protocolo_pruebas_automaticas_y_testing_e2e.md"""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()
'''

TEST_SALUD_PY = '''"""Prueba de ejemplo: la sonda de vida responde sin consultar dependencias."""
from fastapi.testclient import TestClient


def test_health_live_responde_200():
    from config.fastapi_app import app

    respuesta = TestClient(app).get("/health/live")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "alive"}
'''

GITIGNORE = """.venv/
__pycache__/
*.py[cod]
.env
*.log
node_modules/
dist/
.coverage
htmlcov/
.pytest_cache/
.ruff_cache/
playwright-report/
test-results/
reporte_endpoints.json
.DS_Store
Thumbs.db
"""

BACKEND_DOCKERIGNORE = """__pycache__/
*.py[cod]
.env
.git
.venv/
*.log
.coverage
htmlcov/
media/
"""

FRONTEND_DOCKERIGNORE = """node_modules/
dist/
.git
.env
*.log
playwright-report/
test-results/
"""


def env_content(project_name: str, slug: str) -> str:
    return f"""# Variables de entorno — {project_name}
# Generado con secretos aleatorios. NO versionar este archivo (.gitignore lo excluye).
APP_NAME="{project_name}"
APP_SLUG={slug}
ENVIRONMENT=development
DEBUG=true
SECRET_KEY={secrets.token_urlsafe(50)}

ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

POSTGRES_DB={slug}_db
POSTGRES_USER={slug}_user
POSTGRES_PASSWORD={secrets.token_urlsafe(24)}
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/1

# Primer administrador (solo desarrollo; ver backend/seed_data.py)
SEED_ON_START=true
ADMIN_DEFAULT_LOGIN=1000000001
ADMIN_DEFAULT_PASSWORD={secrets.token_urlsafe(16)}

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-responder@ejemplo.local

VITE_API_URL=http://localhost:8000
"""


ENV_EXAMPLE = """# Copie este archivo como .env y complete los valores. Nunca versione el .env real.
APP_NAME=
APP_SLUG=
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=<generar con: python -c "import secrets; print(secrets.token_urlsafe(50))">
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/1
SEED_ON_START=false
ADMIN_DEFAULT_LOGIN=
ADMIN_DEFAULT_PASSWORD=
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=
VITE_API_URL=http://localhost:8000
"""


# ----------------------------------------------------------------------------- pasos
def scaffold(project_name: str, target: Path, install: bool) -> None:
    slug = sanitize_slug(project_name)

    print("[1/6] Estructura de carpetas")
    for rel in (
        "backend/config", "backend/apps/auth_core", "backend/media",
        "frontend/src/assets", "frontend/src/components", "frontend/src/config", "frontend/src/context",
        "frontend/src/hooks", "frontend/src/pages", "frontend/src/schemas", "frontend/src/services",
        "frontend/src/styles", "frontend/src/types",
        "pruebas/unitarias", "pruebas/integracion", "pruebas/e2e",
        "specs/changes", "memory/adrs", "memory/learnings", "docs",
    ):
        (target / rel).mkdir(parents=True, exist_ok=True)
    (target / "backend" / "media" / ".gitkeep").touch(exist_ok=True)

    print("[2/6] Identidad visual y tokens de diseño")
    for asset in (SDD_DIR / "assets").glob("*"):
        if asset.is_file():
            copy(asset, target / "frontend" / "src" / "assets" / asset.name)
    copy(SDD_DIR / "components" / "variables.css", target / "frontend" / "src" / "styles" / "variables.css")

    print("[3/6] Backend, Docker y dependencias")
    copy(STACK_DIR / "requirements.txt", target / "backend" / "requirements.txt")
    copy(STACK_DIR / "requirements-dev.txt", target / "backend" / "requirements-dev.txt")
    copy(STACK_DIR / "Dockerfile.backend", target / "backend" / "Dockerfile")
    copy(STACK_DIR / "entrypoint.sh", target / "backend" / "entrypoint.sh")
    copy(STACK_DIR / "seed_data.py", target / "backend" / "seed_data.py")
    copy(STACK_DIR / "settings_security_template.py", target / "backend" / "config" / "settings_security.py")
    copy(STACK_DIR / "asgi_template.py", target / "backend" / "config" / "asgi.py")
    copy(STACK_DIR / "healthcheck.py", target / "backend" / "config" / "healthcheck.py")
    write(target / "backend" / "config" / "fastapi_app.py", FASTAPI_APP_PY, overwrite=False)
    write(target / "backend" / "manage.py", MANAGE_PY, overwrite=False)
    write(target / "backend" / "config" / "__init__.py", CONFIG_INIT_PY, overwrite=False)
    write(target / "backend" / "config" / "settings.py", SETTINGS_PY, overwrite=False)
    write(target / "backend" / "config" / "urls.py", URLS_PY, overwrite=False)
    write(target / "backend" / "config" / "celery.py", CELERY_PY, overwrite=False)
    write(target / "backend" / "apps" / "__init__.py", "", overwrite=False)
    write(target / "backend" / "apps" / "auth_core" / "__init__.py", "", overwrite=False)
    write(target / "backend" / "apps" / "auth_core" / "apps.py", AUTH_CORE_APPS_PY, overwrite=False)
    copy(STACK_DIR / "endpoints_registry_template.json", target / "backend" / "config" / "endpoints_registry.json",
         overwrite=False)
    write(target / "backend" / ".dockerignore", BACKEND_DOCKERIGNORE)
    copy(STACK_DIR / "docker-compose.yml", target / "docker-compose.yml")

    print("[4/6] Frontend")
    copy(STACK_DIR / "Dockerfile.frontend", target / "frontend" / "Dockerfile")
    write(target / "frontend" / ".dockerignore", FRONTEND_DOCKERIGNORE)
    pkg = (STACK_DIR / "package.json").read_text(encoding="utf-8").replace('"app-frontend"', f'"{slug}-frontend"')
    write(target / "frontend" / "package.json", pkg)
    write(target / "frontend" / "src" / "services" / "endpoints.ts", ENDPOINTS_TS, overwrite=False)
    write(target / "frontend" / "src" / "config" / "storageKeys.ts", STORAGE_KEYS_TS, overwrite=False)
    write(target / "frontend" / ".env.development",
          f"VITE_API_URL=http://localhost:8000\nVITE_APP_SLUG={slug}\n", overwrite=False)
    write(target / "frontend" / "index.html", f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/src/assets/Joli.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
""", overwrite=False)

    print("[5/6] Pruebas, especificaciones, memoria y guía para agentes")
    copy(STACK_DIR / "validate_endpoints.py", target / "pruebas" / "validate_endpoints.py")
    write(target / "pytest.ini", PYTEST_INI, overwrite=False)
    write(target / "pruebas" / "conftest.py", CONFTEST_PY, overwrite=False)
    write(target / "pruebas" / "integracion" / "test_salud.py", TEST_SALUD_PY, overwrite=False)
    copy_tree_files(SDD_DIR / "changes_template", target / "specs" / "changes" / "_plantilla")
    copy_tree_files(SDD_DIR / "memory", target / "memory")
    copy(STACK_DIR / "agent_harness" / "AGENTS.md", target / "AGENTS.md", overwrite=False)
    copy(STACK_DIR / "agent_harness" / ".cursorrules", target / ".cursorrules", overwrite=False)

    # El .env con secretos nunca se sobrescribe: regenerarlo cambiaría claves de una BD existente.
    write(target / ".env", env_content(project_name, slug), overwrite=False)
    write(target / ".env.example", ENV_EXAMPLE)
    write(target / ".gitignore", GITIGNORE, overwrite=False)
    interpreter = "${workspaceFolder}/.venv/Scripts/python.exe" if sys.platform == "win32" \
        else "${workspaceFolder}/.venv/bin/python"
    write(target / ".vscode" / "settings.json",
          '{\n  "python.defaultInterpreterPath": "' + interpreter + '",\n'
          '  "python.terminal.activateEnvironment": true\n}\n', overwrite=False)

    print("[6/6] Entorno virtual .venv")
    venv_dir = target / ".venv"
    venv_python = venv_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if not venv_python.exists():
        venv.create(venv_dir, with_pip=True)
    if install:
        dev_reqs = target / "backend" / "requirements-dev.txt"
        result = subprocess.run([str(venv_python), "-m", "pip", "install", "-r", str(dev_reqs)], check=False)
        if result.returncode != 0:
            print(f"   [AVISO] Falló la instalación. Reintente con: {venv_python} -m pip install -r {dev_reqs}")
    else:
        print(f"   Instale luego con: {venv_python} -m pip install -r backend/requirements-dev.txt")

    print(f"""
Proyecto '{project_name}' listo en {target}

Siguientes pasos:
  1. Revise .env (tiene secretos aleatorios de desarrollo).
  2. docker compose up --build
  3. {venv_python} -m pytest                      # pruebas
  4. {venv_python} pruebas/validate_endpoints.py   # validación HTTP con la app levantada
""")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Crea un proyecto nuevo a partir del SDD")
    parser.add_argument("name", nargs="?", help="Nombre legible del proyecto")
    parser.add_argument("--name", "-n", dest="name_opt", help="Nombre legible del proyecto")
    parser.add_argument("--destino", help="Carpeta destino (por defecto: hermana de .sdd con el slug)")
    parser.add_argument("--sin-instalar", action="store_true", help="Crea .venv pero no instala dependencias")
    args = parser.parse_args(argv)

    project_name = (args.name_opt or args.name or "").strip()
    while not project_name:
        project_name = input("Nombre del nuevo proyecto: ").strip()

    slug = sanitize_slug(project_name)
    if not slug:
        print("El nombre debe contener letras o números.")
        return 1
    target = Path(args.destino).resolve() if args.destino else WORKSPACE_DIR / slug

    print(f"Proyecto: {project_name}\nSlug: {slug}\nDestino: {target}")
    if target.exists() and any(target.iterdir()):
        answer = input("La carpeta ya existe y no está vacía. Se agregarán los archivos que falten y se "
                       "actualizarán las plantillas (el .env no se toca). ¿Continuar? (s/N): ").strip().lower()
        if answer != "s":
            print("Cancelado.")
            return 1

    scaffold(project_name, target, install=not args.sin_instalar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
