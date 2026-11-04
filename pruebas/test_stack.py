"""Pruebas de las plantillas de stack/ que no requieren Django instalado.

- Enrutador ASGI: se importa con módulos de Django simulados para verificar el despacho por prefijo.
- Generador de proyectos: crea un proyecto en una carpeta temporal y revisa lo esencial.
"""
import asyncio
import json
import re
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

STACK = Path(__file__).resolve().parent.parent / "stack"
sys.path.insert(0, str(STACK))


def _load_asgi(fastapi_present=True):
    """Importa asgi_template con Django, asgiref y la app FastAPI simulados."""
    calls = {"django": [], "fast": []}

    async def django_app(scope, receive, send):
        calls["django"].append(scope["path"])

    async def fast_app(scope, receive, send):
        calls["fast"].append((scope["path"], scope["root_path"]))

    def sync_to_async(fn):
        async def wrapper(*a, **k):
            return fn(*a, **k)
        return wrapper

    fake = {
        "django": types.ModuleType("django"),
        "django.core": types.ModuleType("django.core"),
        "django.core.asgi": types.SimpleNamespace(get_asgi_application=lambda: django_app),
        "django.db": types.SimpleNamespace(close_old_connections=lambda: None),
        "asgiref": types.ModuleType("asgiref"),
        "asgiref.sync": types.SimpleNamespace(sync_to_async=sync_to_async),
    }
    if fastapi_present:
        fake["config"] = types.ModuleType("config")
        fake["config.fastapi_app"] = types.SimpleNamespace(app=fast_app)
    with mock.patch.dict(sys.modules, fake):
        sys.modules.pop("asgi_template", None)
        import asgi_template  # noqa: F401
        module = sys.modules.pop("asgi_template")
    return module, calls


def _call(module, path, scope_type="http"):
    asyncio.run(module.application({"type": scope_type, "path": path, "root_path": ""}, None, None))


class AsgiRoutingTests(unittest.TestCase):
    def test_prefijo_fast_va_a_fastapi_sin_prefijo(self):
        module, calls = _load_asgi()
        _call(module, "/fast/v1/health/")
        self.assertEqual(calls["fast"], [("/v1/health", "/fast")])

    def test_subcadena_fast_no_se_confunde(self):
        module, calls = _load_asgi()
        for path in ("/api/v1/breakfast/", "/fastidio/", "/api/fast/"):
            _call(module, path)
        self.assertEqual(calls["fast"], [])
        self.assertEqual(len(calls["django"]), 3)

    def test_health_va_a_fastapi_sin_modificar(self):
        module, calls = _load_asgi()
        _call(module, "/health/ready")
        self.assertEqual(calls["fast"], [("/health/ready", "")])

    def test_sin_fastapi_todo_va_a_django(self):
        module, calls = _load_asgi(fastapi_present=False)
        _call(module, "/fast/v1/health")
        self.assertEqual(calls["django"], ["/fast/v1/health"])


class InitProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import init_project
        cls.init_project = init_project
        cls.tmp = tempfile.TemporaryDirectory()
        cls.target = Path(cls.tmp.name) / "gestion_de_turnos"
        with mock.patch.object(init_project.venv, "create"), mock.patch("builtins.print"):
            init_project.scaffold("Gestión de Turnos", cls.target, install=False)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_slug(self):
        self.assertEqual(self.init_project.sanitize_slug("Gestión de Turnos-2"), "gestion_de_turnos_2")

    def test_archivos_esenciales(self):
        for rel in ("backend/manage.py", "backend/config/settings.py", "backend/config/asgi.py",
                    "backend/config/fastapi_app.py", "backend/config/healthcheck.py", "backend/config/celery.py",
                    "backend/config/endpoints_registry.json", "pruebas/validate_endpoints.py",
                    "pruebas/conftest.py", "pytest.ini", "frontend/src/services/endpoints.ts",
                    "frontend/src/config/storageKeys.ts", "docker-compose.yml", ".env", ".env.example",
                    "AGENTS.md", "specs/changes/_plantilla/proposal.md"):
            self.assertTrue((self.target / rel).is_file(), rel)

    def test_no_hay_pruebas_dentro_de_backend(self):
        self.assertEqual([p for p in (self.target / "backend").rglob("test*.py")], [])

    def test_env_sin_secretos_fijos_ni_infraestructura_real(self):
        env = (self.target / ".env").read_text(encoding="utf-8")
        self.assertNotIn("insecure", env)
        self.assertNotIn("jolifoods.co", env)
        ips = set(re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", env))
        self.assertLessEqual(ips, {"127.0.0.1"}, "el .env generado no debe traer IPs de infraestructura")
        secret = re.search(r"^SECRET_KEY=(.+)$", env, re.M).group(1)
        self.assertGreaterEqual(len(secret), 50)

    def test_env_no_se_sobrescribe(self):
        before = (self.target / ".env").read_text(encoding="utf-8")
        with mock.patch.object(self.init_project.venv, "create"), mock.patch("builtins.print"):
            self.init_project.scaffold("Gestión de Turnos", self.target, install=False)
        self.assertEqual((self.target / ".env").read_text(encoding="utf-8"), before)

    def test_endpoints_ts_y_registro_coinciden(self):
        ts = (self.target / "frontend/src/services/endpoints.ts").read_text(encoding="utf-8")
        registry = json.loads((self.target / "backend/config/endpoints_registry.json").read_text(encoding="utf-8"))
        ts_paths = set(re.findall(r"'(/[^']+)'", ts))
        for ep in registry["endpoints"]:
            if "{" not in ep["path"]:
                self.assertIn(ep["path"], ts_paths, f"{ep['path']} no está en endpoints.ts")

    def test_codigo_python_generado_compila(self):
        for py in self.target.rglob("*.py"):
            compile(py.read_text(encoding="utf-8"), str(py), "exec")


class PythonTemplatesCompile(unittest.TestCase):
    def test_plantillas_compilan(self):
        for py in STACK.glob("*.py"):
            compile(py.read_text(encoding="utf-8"), str(py), "exec")


if __name__ == "__main__":
    unittest.main()
