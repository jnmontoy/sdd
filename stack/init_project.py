#!/usr/bin/env python3
"""
Script de Scaffolding Automatizado — Ecosistema Jolifoods (SDD)
Permite inicializar un nuevo proyecto o módulo corporativo a partir de las especificaciones SDD.

Uso:
    python init_project.py
    python init_project.py "Tiendita Operativa"
"""

import os
import sys
import shutil
import re
from pathlib import Path

def sanitize_slug(name: str) -> str:
    """Convierte el nombre legible en un identificador seguro para carpetas y nombres Docker."""
    clean = re.sub(r'[^a-zA-Z0-9_\-\s]', '', name).strip().lower()
    return re.sub(r'[\s\-]+', '_', clean)

def main():
    print("=" * 70)
    print("  INICIALIZADOR DE PROYECTO CORPORATIVO — JOLIFOODS (SDD)")
    print("=" * 70)

    # 1. Obtener el nombre del proyecto (Paso 0 Mandatorio de la especificación)
    project_name = None
    if len(sys.argv) > 1:
        if sys.argv[1] in ("--name", "-n") and len(sys.argv) > 2:
            project_name = sys.argv[2].strip()
        elif not sys.argv[1].startswith("-"):
            project_name = sys.argv[1].strip()

    if not project_name:
        project_name = input("\n[Paso 0] Ingrese el nombre del nuevo proyecto o módulo: ").strip()

    while not project_name:
        project_name = input("El nombre no puede estar vacío. Ingrese el nombre: ").strip()

    project_slug = sanitize_slug(project_name)
    base_dir = Path(__file__).resolve().parent.parent.parent  # Directorio raíz del workspace
    target_dir = base_dir / project_slug
    SDD_dir = base_dir / ".sdd"

    print(f"\n-> Nombre del Proyecto : {project_name}")
    print(f"-> Identificador Slug  : {project_slug}")
    print(f"-> Directorio Destino  : {target_dir}")

    if target_dir.exists():
        resp = input(f"\n[ALERTA] La carpeta '{project_slug}' ya existe. ¿Deseas sobreescribirla? (s/N): ").strip().lower()
        if resp != 's':
            print("Operación cancelada.")
            return

    # 2. Crear estructura de carpetas
    print("\n[1/5] Creando árbol de directorios...")
    dirs_to_create = [
        target_dir / "backend" / "config",
        target_dir / "backend" / "apps" / "auth_core",
        target_dir / "backend" / "media",  # Carpeta canónica para almacenamiento de subidas (firmas, PDFs, fotos)
        target_dir / "frontend" / "src" / "assets",
        target_dir / "frontend" / "src" / "components" / "auth",
        target_dir / "frontend" / "src" / "context",
        target_dir / "frontend" / "src" / "hooks",
        target_dir / "frontend" / "src" / "pages",
        target_dir / "frontend" / "src" / "schemas",
        target_dir / "frontend" / "src" / "services",
        target_dir / "frontend" / "src" / "styles",
        target_dir / "frontend" / "src" / "types",
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)

    # Iniciar archivo .gitkeep dentro de backend/media
    (target_dir / "backend" / "media" / ".gitkeep").touch(exist_ok=True)

    # 3. Copiar assets corporativos oficiales
    print("[2/5] Inyectando assets oficiales de Jolifoods...")
    assets_src = SDD_dir / "assets"
    if assets_src.exists():
        for asset in assets_src.iterdir():
            if asset.is_file():
                shutil.copy2(asset, target_dir / "frontend" / "src" / "assets" / asset.name)

    # 4. Copiar tokens CSS globales (variables.css)
    print("[3/5] Inyectando tokens de diseño CSS (variables.css con Noche/Día)...")
    variables_css = SDD_dir / "components" / "variables.css"
    if variables_css.exists():
        shutil.copy2(variables_css, target_dir / "frontend" / "src" / "styles" / "variables.css")

    # 5. Generar archivos de infraestructura (Docker, requirements, package.json, .env)
    print("[4/5] Configurando orquestación Docker y dependencias canónicas...")
    stack_dir = SDD_dir / "stack"

    # requirements.txt
    if (stack_dir / "requirements.txt").exists():
        shutil.copy2(stack_dir / "requirements.txt", target_dir / "backend" / "requirements.txt")

    # Dockerfile backend
    if (stack_dir / "Dockerfile.backend").exists():
        shutil.copy2(stack_dir / "Dockerfile.backend", target_dir / "backend" / "Dockerfile")

    # Dockerfile frontend
    if (stack_dir / "Dockerfile.frontend").exists():
        shutil.copy2(stack_dir / "Dockerfile.frontend", target_dir / "frontend" / "Dockerfile")

    # healthcheck.py
    if (stack_dir / "healthcheck.py").exists():
        shutil.copy2(stack_dir / "healthcheck.py", target_dir / "backend" / "apps" / "auth_core" / "healthcheck.py")

    # settings_security_template.py (Normativa de Auditoría)
    if (stack_dir / "settings_security_template.py").exists():
        shutil.copy2(stack_dir / "settings_security_template.py", target_dir / "backend" / "config" / "settings_security.py")

    # entrypoint.sh (Orquestación de inicio con migraciones automáticas)
    if (stack_dir / "entrypoint.sh").exists():
        shutil.copy2(stack_dir / "entrypoint.sh", target_dir / "backend" / "entrypoint.sh")

    # seed_data.py (Datos iniciales idempotentes)
    if (stack_dir / "seed_data.py").exists():
        shutil.copy2(stack_dir / "seed_data.py", target_dir / "backend" / "seed_data.py")

    # asgi_template.py (Enrutador híbrido ASGI Django + FastAPI)
    if (stack_dir / "asgi_template.py").exists():
        shutil.copy2(stack_dir / "asgi_template.py", target_dir / "backend" / "config" / "asgi.py")

    # validate_endpoints.py (Validador universal de endpoints y generador de cURLs)
    if (stack_dir / "validate_endpoints.py").exists():
        shutil.copy2(stack_dir / "validate_endpoints.py", target_dir / "backend" / "validate_endpoints.py")

    # endpoints_registry.json (Catálogo centralizado de rutas para auditoría)
    if (stack_dir / "endpoints_registry_template.json").exists():
        shutil.copy2(stack_dir / "endpoints_registry_template.json", target_dir / "backend" / "config" / "endpoints_registry.json")

    # endpoints.ts (Constantes centralizadas para frontend - Cero URLs quemadas en vistas)
    endpoints_ts_content = """/**
 * Catálogo Centralizado de Endpoints — Jolifoods / SDD
 * Regla Inflexible BP-09: Toda vista debe importar sus rutas desde aquí.
 */
export const ENDPOINTS = {
  HEALTH: {
    LIVE: '/health/live',
    READY: '/health/ready',
  },
  AUTH: {
    LOGIN: '/api/v1/auth/login/',
    REFRESH: '/api/v1/auth/refresh/',
    LOGOUT: '/api/v1/auth/logout/',
    ME: '/api/v1/auth/me/',
  },
  USUARIOS: {
    LISTA: '/api/v1/usuarios/',
    DETALLE: (id: string | number) => `/api/v1/usuarios/${id}/`,
  },
  FAST: {
    HEALTH: '/fast/v1/health',
  },
  TELEMETRIA: {
    FEEDBACK: '/api/v1/telemetria/feedback/',
  },
} as const;
"""
    (target_dir / "frontend" / "src" / "services" / "endpoints.ts").write_text(endpoints_ts_content, encoding="utf-8")

    # .dockerignore para Backend y Frontend
    backend_dockerignore = """__pycache__/
*.py[cod]
*$py.class
*.so
.env
.git
.gitignore
.venv/
env/
venv/
*.log
.coverage
htmlcov/
"""
    (target_dir / "backend" / ".dockerignore").write_text(backend_dockerignore, encoding="utf-8")

    frontend_dockerignore = """node_modules/
dist/
.git
.gitignore
.env
*.log
npm-debug.log*
"""
    (target_dir / "frontend" / ".dockerignore").write_text(frontend_dockerignore, encoding="utf-8")

    # package.json personalizado con el nombre del proyecto
    if (stack_dir / "package.json").exists():
        pkg_content = (stack_dir / "package.json").read_text(encoding="utf-8")
        pkg_content = pkg_content.replace('"jolifoods-frontend"', f'"{project_slug}-frontend"')
        (target_dir / "frontend" / "package.json").write_text(pkg_content, encoding="utf-8")

    # index.html con título inyectado y Favicon Jolifoods
    index_html_content = f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/src/assets/Jolifoods.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name} | Jolifoods</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""
    (target_dir / "frontend" / "index.html").write_text(index_html_content, encoding="utf-8")

    # docker-compose.yml personalizado
    if (stack_dir / "docker-compose.yml").exists():
        dc_content = (stack_dir / "docker-compose.yml").read_text(encoding="utf-8")
        dc_content = dc_content.replace("jolifoods_db", f"{project_slug}_db")
        dc_content = dc_content.replace("jolifoods_redis", f"{project_slug}_redis")
        dc_content = dc_content.replace("jolifoods_backend", f"{project_slug}_backend")
        dc_content = dc_content.replace("jolifoods_frontend", f"{project_slug}_frontend")
        (target_dir / "docker-compose.yml").write_text(dc_content, encoding="utf-8")

    # .env.example y .env (Cumple 100% las 6 Buenas Prácticas de Auditoría)
    env_content = f"""# ==============================================================================
# VARIABLES DE ENTORNO — PROYECTO: {project_name} (JOLIFOODS)
# Conforme a la Normativa de Seguridad y Auditoría (Score 100/100)
# ==============================================================================
APP_NAME="{project_name}"
APP_SLUG="{project_slug}"
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=joli-secret-{project_slug}-insecure-dev-key-2026

# --- 2. BLINDAJE DE HOSTS (SIN COMODÍN '*') ---
ALLOWED_HOSTS=localhost,127.0.0.1,apps.jolifoods.co,129.213.95.33

# --- BASE DE DATOS POSTGRESQL ---
POSTGRES_DB={project_slug}_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_secure_2026
POSTGRES_HOST=db
POSTGRES_PORT=5432

# --- 4. CACHE Y RATE LIMITING DISTRIBUIDO (REDIS) ---
REDIS_URL=redis://redis:6379/1

# --- 3. URLs Y CORS RESTRINGIDO ---
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# --- CREDENCIALES CORREO (RESTABLECIMIENTO DE CLAVE) ---
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=seguridad@jolifoods.com
"""
    (target_dir / ".env.example").write_text(env_content, encoding="utf-8")
    (target_dir / ".env").write_text(env_content, encoding="utf-8")

    # .gitignore en la raíz del proyecto
    gitignore_content = """.venv/
__pycache__/
*.py[cod]
*$py.class
*.so
.env
*.log
node_modules/
dist/
.DS_Store
Thumbs.db
"""
    (target_dir / ".gitignore").write_text(gitignore_content, encoding="utf-8")

    # Configuración de VS Code (.vscode/settings.json) para vincular .venv
    vscode_dir = target_dir / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)
    vscode_settings = """{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true
}
"""
    (vscode_dir / "settings.json").write_text(vscode_settings, encoding="utf-8")

    # 6. Crear entorno virtual Python (.venv) e instalar requerimientos aislados
    print("[5/5] Creando entorno virtual aislado (.venv) en el proyecto...")
    venv_dir = target_dir / ".venv"
    import subprocess

    venv_created = False
    try:
        import venv
        venv.create(venv_dir, with_pip=True)
        venv_created = True
        print(f"   [OK] Entorno .venv creado exitosamente con pip en: {venv_dir}")
    except Exception as exc:
        # Fallback a sys.executable -m venv .venv
        try:
            res_venv = subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=False)
            if res_venv.returncode == 0:
                venv_created = True
                print(f"   [OK] Entorno .venv creado vía subproceso en: {venv_dir}")
        except Exception:
            pass

    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python"

    if venv_python.exists():
        req_file = target_dir / "backend" / "requirements.txt"
        if req_file.exists():
            print("   [Aislamiento Seguro] Instalando backend/requirements.txt exclusivamente dentro de .venv...")
            subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "-q"], check=False)
            install_res = subprocess.run([str(venv_python), "-m", "pip", "install", "-r", str(req_file)], check=False)
            if install_res.returncode == 0:
                print("   [OK] Dependencias instaladas al 100% dentro del entorno virtual.")
            else:
                print(f"   [AVISO] Puedes completar la instalación de librerías con: {venv_python} -m pip install -r backend/requirements.txt")
    else:
        print(f"   [ALERTA CRÍTICA] No se pudo inicializar .venv automáticamente. DEBES crearlo antes de instalar requerimientos:")
        print(f"   cd {target_dir} && python -m venv .venv")

    # 7. Generar script seguro de inicio rápido (start_dev.ps1)
    start_dev_content = f"""# ==============================================================================
# Script de Inicio Rápido Seguro — {project_name} (SDD Jolifoods)
# Garantiza aislamiento estricto en .venv (Cero contaminación del Python del sistema)
# ==============================================================================

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  INICIANDO PLATAFORMA {project_name.upper()} — JOLIFOODS SDD" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Validar / Crear entorno virtual .venv
$VenvPython = ".\\.venv\\Scripts\\python.exe"
if (-not (Test-Path $VenvPython)) {{
    Write-Host "[1/3] Entorno virtual .venv no encontrado. Creando entorno aislado..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "Instalando backend\\requirements.txt en .venv..." -ForegroundColor Yellow
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -r backend\\requirements.txt
}} else {{
    Write-Host "[1/3] Entorno virtual .venv verificado OK." -ForegroundColor Green
}}

# 2. Instrucciones de ejecución segura
Write-Host "`n[2/3] Comandos de ejecución (ejecutando en .venv aislado):" -ForegroundColor Cyan
Write-Host "  -> Backend ASGI:" -ForegroundColor White
Write-Host "     .\\.venv\\Scripts\\python.exe -m uvicorn config.asgi:application --app-dir backend --host 127.0.0.1 --port 8000 --reload`n" -ForegroundColor Gray
Write-Host "  -> Frontend React:" -ForegroundColor White
Write-Host "     npm --prefix frontend run dev`n" -ForegroundColor Gray
Write-Host "  -> O mediante Docker Multi-Contenedor:" -ForegroundColor White
Write-Host "     docker compose up --build -d`n" -ForegroundColor Gray
"""
    (target_dir / "start_dev.ps1").write_text(start_dev_content, encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"  ¡PROYECTO '{project_name}' INICIALIZADO CORRECTAMENTE!")
    print("=" * 70)
    print(f"\nUbicación       : {target_dir}")
    print(f"Entorno Virtual : {venv_dir}")
    print(f"Python Aislado  : {venv_python}")
    print(f"\nPara iniciar el desarrollo ejecuta de forma segura:")
    print(f"  cd {project_slug}")
    print(f"  .\\start_dev.ps1")
    print("\nEndpoints listos:")
    print("  - Frontend : http://localhost:5173")
    print("  - Backend  : http://localhost:8000")
    print("  - Health   : http://localhost:8000/api/v1/health/\n")

if __name__ == "__main__":
    main()

