"""Pruebas del validador de endpoints contra un servidor HTTP falso en memoria.

Ejecutar desde .sdd/:  .\\.venv\\Scripts\\python.exe -m unittest discover -s pruebas -v
"""
import io
import json
import os
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "stack"))
import validate_endpoints as ve  # noqa: E402

TOKEN = "token-de-prueba"
SECURE_HEADERS = {"X-Frame-Options": "DENY", "X-Content-Type-Options": "nosniff"}


class FakeApi(BaseHTTPRequestHandler):
    """Simula un backend que cumple la normativa, salvo en /inseguro y /lento."""

    def log_message(self, *args):  # silencio
        pass

    def _reply(self, status, body=None, headers=None, extra=None):
        payload = json.dumps(body or {}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for k, v in (headers if headers is not None else SECURE_HEADERS).items():
            self.send_header(k, v)
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(payload)

    def _authorized(self):
        return self.headers.get("Authorization") == f"Bearer {TOKEN}"

    def do_GET(self):
        if self.path in ("/health/live", "/health/ready", "/fast/v1/health"):
            return self._reply(200, {"status": "ok"})
        if self.path == "/inseguro":
            return self._reply(200, headers={})
        if self.path == "/lento":
            import time
            time.sleep(0.15)
            return self._reply(200)
        if self.path == "/api/v1/abierto-por-error/":
            return self._reply(200)  # viola deny-by-default
        if self.path.startswith("/api/v1/"):
            return self._reply(200, {"results": []}) if self._authorized() else self._reply(401)
        return self._reply(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/api/v1/auth/login/":
            if body.get("numero_documento") == "1000000001" and body.get("password") == "clave":
                return self._reply(200, {"access": TOKEN},
                                   extra={"Set-Cookie": "csrftoken=abc123; Path=/"})
            return self._reply(400)
        if self.path == "/api/v1/eco-csrf/":
            ok = self._authorized() and self.headers.get("X-CSRFToken") == "abc123"
            return self._reply(201 if ok else 403)
        return self._reply(404)


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeApi)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def run_validator(self, endpoints, *args, env=None):
        with tempfile.TemporaryDirectory() as tmp:
            registry = Path(tmp) / "registry.json"
            registry.write_text(json.dumps({"project_name": "prueba", "endpoints": endpoints}), encoding="utf-8")
            report = Path(tmp) / "reporte.json"
            curls = Path(tmp) / "curls.sh"
            old_env = dict(os.environ)
            os.environ.update(env or {})
            try:
                with redirect_stdout(io.StringIO()):
                    code = ve.main(["--base-url", self.base, "--endpoints-file", str(registry),
                                    "--json-report", str(report), "--export-curls", str(curls), *args])
            finally:
                os.environ.clear()
                os.environ.update(old_env)
            return code, json.loads(report.read_text(encoding="utf-8")), curls.read_text(encoding="utf-8")

    def test_endpoints_publicos_correctos_aprueban(self):
        code, report, _ = self.run_validator([{"path": "/health/live"}, {"path": "/fast/v1/health"}])
        self.assertEqual(code, 0)
        self.assertEqual(report["passed"], 2)

    def test_login_obtiene_token_y_prueba_endpoints_privados(self):
        endpoints = [{"name": "usuarios", "path": "/api/v1/usuarios/", "auth_required": True}]
        code, report, curls = self.run_validator(endpoints, "--login-user", "1000000001",
                                                 env={"SDD_LOGIN_PASSWORD": "clave"})
        self.assertEqual(code, 0, report)
        nombres = [r["name"] for r in report["results"]]
        self.assertIn("usuarios · sin sesión", nombres)  # verificó deny-by-default
        self.assertNotIn(TOKEN, curls)                    # los cURL no filtran el token
        self.assertNotIn("clave", curls)                  # ni la contraseña

    def test_privado_sin_token_falla_en_lugar_de_pasar_en_silencio(self):
        code, report, _ = self.run_validator([{"path": "/api/v1/usuarios/", "auth_required": True}])
        self.assertEqual(code, 1)
        self.assertEqual(report["failed"], 1)

    def test_endpoint_privado_abierto_viola_deny_by_default(self):
        endpoints = [{"path": "/api/v1/abierto-por-error/", "auth_required": True}]
        code, report, _ = self.run_validator(endpoints, "--token", TOKEN)
        self.assertEqual(code, 1)
        self.assertTrue(any("se esperaba [401, 403]" in p for r in report["results"] for p in r["problems"]))

    def test_cabeceras_de_seguridad_ausentes_fallan(self):
        code, _, _ = self.run_validator([{"path": "/inseguro"}])
        self.assertEqual(code, 1)

    def test_latencia_es_puerta_y_se_puede_desactivar(self):
        lento = [{"path": "/lento", "max_latency_ms": 50}]
        self.assertEqual(self.run_validator(lento)[0], 1)
        self.assertEqual(self.run_validator(lento, "--sin-puerta-latencia")[0], 0)

    def test_p95_con_muestras(self):
        code, report, _ = self.run_validator([{"path": "/health/live"}], "--samples", "5")
        self.assertEqual(code, 0)
        self.assertEqual(report["results"][0]["latency_metric"], "p95")
        self.assertEqual(report["results"][0]["samples"], 5)

    def test_mutaciones_se_omiten_por_defecto(self):
        endpoints = [{"path": "/api/v1/eco-csrf/", "method": "POST", "payload": {}, "auth_required": True,
                      "expected_status": 201, "mutates": True}]
        code, report, _ = self.run_validator(endpoints, "--token", TOKEN)
        self.assertEqual((code, report["skipped"]), (0, 1))

    def test_csrf_de_cookie_se_envia_en_post(self):
        endpoints = [{"path": "/api/v1/eco-csrf/", "method": "POST", "payload": {}, "auth_required": True,
                      "expected_status": 201, "mutates": True}]
        code, report, _ = self.run_validator(endpoints, "--login-user", "1000000001", "--incluir-mutaciones",
                                             env={"SDD_LOGIN_PASSWORD": "clave"})
        self.assertEqual(code, 0, report)

    def test_ruta_con_parametros_usa_example_path(self):
        endpoints = [{"path": "/api/v1/usuarios/{id}/", "example_path": "/api/v1/usuarios/1/",
                      "auth_required": True}]
        code, _, _ = self.run_validator(endpoints, "--token", TOKEN)
        self.assertEqual(code, 0)

    def test_login_sin_variable_de_contrasena_aborta(self):
        from unittest import mock
        with mock.patch.dict(os.environ):
            os.environ.pop("SDD_LOGIN_PASSWORD", None)
            os.environ.pop("SDD_TOKEN", None)
            with redirect_stdout(io.StringIO()):
                code = ve.main(["--base-url", self.base, "--login-user", "x"])
        self.assertEqual(code, 1)

    def test_plantilla_del_registro_es_valida(self):
        template = Path(ve.__file__).with_name("endpoints_registry_template.json")
        data = json.loads(template.read_text(encoding="utf-8"))
        for ep in data["endpoints"]:
            self.assertTrue(ep["path"].startswith("/"), ep)
            if "{" in ep["path"]:
                self.assertIn("example_path", ep)
            if ep.get("method", "GET") != "GET" and ep.get("expected_status") != 400:
                self.assertTrue(ep.get("mutates"), f"POST sin 'mutates': {ep['path']}")

    def test_percentil_95(self):
        self.assertEqual(ve.percentile_95([float(i) for i in range(1, 101)]), 95.0)
        self.assertEqual(ve.percentile_95([7.0]), 7.0)


if __name__ == "__main__":
    unittest.main()
