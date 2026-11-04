#!/usr/bin/env python3
"""
Validador de endpoints y generador de cURLs (SDD)
==================================================

Prueba de humo automatizable contra una instancia local o desplegada. NO reemplaza
las pruebas de integración con Pytest (ver greenfield/11): verifica desde fuera,
por HTTP, que lo registrado en `endpoints_registry.json` responda como se declaró.

Qué verifica por cada endpoint del registro:
  1. Código HTTP esperado.
  2. Deny-by-default (BP-05): si `auth_required` es true, sin credenciales debe responder 401/403.
  3. Cabeceras de seguridad: X-Frame-Options, X-Content-Type-Options y HSTS (solo en HTTPS).
  4. Latencia contra `max_latency_ms`. Con `--samples N` (solo GET) se usa el percentil 95.

Características:
  - Solo librería estándar de Python (sin dependencias).
  - Autenticación por JWT: lee el access token de la respuesta del login y conserva las
    cookies (refresh HttpOnly y csrftoken) para enviar `X-CSRFToken` en métodos inseguros.
  - Por seguridad, los endpoints con `"mutates": true` se omiten salvo `--incluir-mutaciones`.
  - Los cURL exportados nunca contienen secretos: usan las variables $SDD_TOKEN y $SDD_LOGIN_PASSWORD.
  - Código de salida 0 si todo pasa, 1 si algo falla (sirve como Quality Gate en CI/CD).

Uso (siempre con el Python del entorno virtual del proyecto):
  Windows : .\\.venv\\Scripts\\python.exe pruebas\\validate_endpoints.py --base-url http://localhost:8000
  Linux   : ./.venv/bin/python pruebas/validate_endpoints.py --base-url http://localhost:8000

  Con login (la contraseña se toma de la variable de entorno, nunca de un argumento):
    $env:SDD_LOGIN_PASSWORD = "<contraseña>"      # PowerShell
    export SDD_LOGIN_PASSWORD="<contraseña>"       # bash
    python pruebas/validate_endpoints.py --base-url https://app.ejemplo.local --login-user 1000000001
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import math
import os
import shlex
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

_USE_COLOR = sys.stdout.isatty() and not os.getenv("NO_COLOR")


def _c(code: str) -> str:
    return code if _USE_COLOR else ""


RESET, BOLD, GREEN, RED, YELLOW, CYAN = (
    _c("\033[0m"), _c("\033[1m"), _c("\033[32m"), _c("\033[31m"), _c("\033[33m"), _c("\033[36m"),
)

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
DEFAULT_AUTH = {
    "login_path": "/api/v1/auth/login/",
    "username_field": "numero_documento",
    "password_field": "password",
    "token_field": "access",
}
# Suite mínima cuando el proyecto aún no tiene registro de endpoints.
STANDARD_SUITE: List[Dict[str, Any]] = [
    {"name": "Salud: vida", "path": "/health/live", "max_latency_ms": 200},
    {"name": "Salud: disponibilidad (BD + Redis)", "path": "/health/ready", "max_latency_ms": 500},
    {"name": "Salud: capa FastAPI", "path": "/fast/v1/health", "max_latency_ms": 200},
    {"name": "Usuarios (requiere sesión)", "path": "/api/v1/usuarios/", "auth_required": True},
]


def percentile_95(values: List[float]) -> float:
    """Percentil 95 por rango más cercano (nearest-rank)."""
    ordered = sorted(values)
    rank = max(1, math.ceil(0.95 * len(ordered)))
    return ordered[rank - 1]


def extract_field(data: Any, dotted: str) -> Optional[str]:
    """Obtiene un campo anidado, p. ej. 'data.tokens.access'."""
    current = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current if isinstance(current, str) else None


class EndpointValidator:
    def __init__(self, base_url: str, token: Optional[str] = None, timeout: float = 5.0,
                 samples: int = 1, latency_gate: bool = True, include_mutations: bool = False):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.samples = max(1, samples)
        self.latency_gate = latency_gate
        self.include_mutations = include_mutations
        self.cookies = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookies))
        self.results: List[Dict[str, Any]] = []
        self.curls: List[str] = []

    # ------------------------------------------------------------------ HTTP
    def _csrf_token(self) -> Optional[str]:
        for cookie in self.cookies:
            if cookie.name == "csrftoken":
                return cookie.value
        return None

    def _send(self, method: str, url: str, headers: Dict[str, str],
              payload: Optional[Any]) -> Dict[str, Any]:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        start = time.perf_counter()
        out: Dict[str, Any] = {"status": None, "headers": {}, "body": "", "error": None}
        try:
            with self.opener.open(req, timeout=self.timeout) as resp:
                out["status"], out["headers"] = resp.status, dict(resp.headers)
                out["body"] = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            out["status"], out["headers"] = exc.code, dict(exc.headers or {})
            out["body"] = exc.read().decode("utf-8", errors="replace")
        except urllib.error.URLError as exc:
            out["error"] = f"Fallo de conexión: {exc.reason}"
        except Exception as exc:  # timeout de socket, etc.
            out["error"] = f"Error inesperado: {exc}"
        out["elapsed_ms"] = (time.perf_counter() - start) * 1000.0
        return out

    def _build_headers(self, method: str, use_auth: bool, has_payload: bool) -> Dict[str, str]:
        headers = {"Accept": "application/json", "User-Agent": "SDD-Endpoint-Validator/2.0"}
        if has_payload:
            headers["Content-Type"] = "application/json"
        if use_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if method in UNSAFE_METHODS:
            csrf = self._csrf_token()
            if csrf:
                headers["X-CSRFToken"] = csrf
        return headers

    def _curl(self, method: str, url: str, headers: Dict[str, str], payload: Optional[Any]) -> str:
        parts = [f"curl -sS -X {method} {shlex.quote(url)}"]
        for key, value in headers.items():
            if key == "Authorization":
                parts.append('-H "Authorization: Bearer $SDD_TOKEN"')
            elif key == "X-CSRFToken":
                parts.append('-H "X-CSRFToken: $SDD_CSRF"')
            else:
                parts.append(f"-H {shlex.quote(f'{key}: {value}')}")
        if payload is not None:
            parts.append(f"-d {shlex.quote(json.dumps(payload, ensure_ascii=False))}")
        return " \\\n  ".join(parts)

    # -------------------------------------------------------------- checks
    def check(self, name: str, path: str, method: str = "GET", expected_status: Any = 200,
              payload: Optional[Any] = None, use_auth: bool = False,
              max_latency_ms: float = 500.0, record_curl: bool = True) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        expected = set(expected_status) if isinstance(expected_status, (list, tuple, set)) else {expected_status}
        headers = self._build_headers(method, use_auth, payload is not None)
        if record_curl:
            self.curls.append(f"# {name} ({method} {path})\n{self._curl(method, url, headers, payload)}\n")

        runs = self.samples if method == "GET" else 1
        responses = [self._send(method, url, headers, payload) for _ in range(runs)]
        last = responses[-1]
        latencies = [r["elapsed_ms"] for r in responses]
        latency = percentile_95(latencies) if runs > 1 else latencies[0]

        problems: List[str] = []
        if last["error"]:
            problems.append(last["error"])
        elif last["status"] not in expected:
            problems.append(f"HTTP {last['status']}, se esperaba {sorted(expected)}")
        if any(r["status"] != last["status"] for r in responses):
            problems.append("respuestas inconsistentes entre muestras")

        warnings: List[str] = []
        lower = {k.lower(): v for k, v in last["headers"].items()}
        if last["status"] is not None:
            if lower.get("x-frame-options", "").upper() not in ("DENY", "SAMEORIGIN"):
                warnings.append("falta X-Frame-Options (DENY)")
            if lower.get("x-content-type-options", "").lower() != "nosniff":
                warnings.append("falta X-Content-Type-Options: nosniff")
            if self.base_url.startswith("https://") and "strict-transport-security" not in lower:
                warnings.append("falta Strict-Transport-Security (HSTS)")
        problems.extend(f"seguridad: {w}" for w in warnings)

        latency_ok = latency <= max_latency_ms
        if not latency_ok and self.latency_gate and not last["error"]:
            label = "p95" if runs > 1 else "latencia"
            problems.append(f"{label} {latency:.0f} ms > límite {max_latency_ms:.0f} ms")

        result = {
            "name": name, "method": method, "path": path, "url": url,
            "expected_status": sorted(expected), "actual_status": last["status"],
            "latency_ms": round(latency, 2), "latency_metric": "p95" if runs > 1 else "single",
            "samples": runs, "latency_ok": latency_ok, "outcome": "pass" if not problems else "fail",
            "problems": problems, "body": last["body"],
        }
        self.results.append(result)
        self._print(result)
        return result

    def skip(self, name: str, method: str, path: str, reason: str, counts_as_failure: bool) -> None:
        result = {"name": name, "method": method, "path": path,
                  "outcome": "fail" if counts_as_failure else "skip", "problems": [reason]}
        self.results.append(result)
        self._print(result)

    def _print(self, r: Dict[str, Any]) -> None:
        badge = {"pass": f"{GREEN}[ OK ]{RESET}", "fail": f"{RED}[FALLA]{RESET}",
                 "skip": f"{YELLOW}[OMITE]{RESET}"}[r["outcome"]]
        status = r.get("actual_status") or "-"
        lat = f"{r['latency_ms']:7.1f} ms" if "latency_ms" in r else "         "
        print(f" {badge} {r['method']:<6} {r['path']:<40} {str(status):>4} {lat}  {r['name']}")
        for problem in r["problems"]:
            color = YELLOW if r["outcome"] == "skip" else RED
            print(f"          {color}-> {problem}{RESET}")

    # --------------------------------------------------------------- flujo
    def login(self, auth_cfg: Dict[str, str], username: str, password: str) -> bool:
        payload = {auth_cfg["username_field"]: username, auth_cfg["password_field"]: password}
        url = f"{self.base_url}/{auth_cfg['login_path'].lstrip('/')}"
        headers = self._build_headers("POST", False, True)
        safe_payload = {auth_cfg["username_field"]: username, auth_cfg["password_field"]: "$SDD_LOGIN_PASSWORD"}
        self.curls.append(f"# Login\n{self._curl('POST', url, headers, safe_payload)}\n")
        resp = self._send("POST", url, headers, payload)
        token = None
        if resp["status"] == 200:
            try:
                token = extract_field(json.loads(resp["body"]), auth_cfg["token_field"])
            except ValueError:
                token = None
        ok = token is not None
        problems = [] if ok else [
            resp["error"] or f"HTTP {resp['status']} o la respuesta no trae el campo '{auth_cfg['token_field']}'"
        ]
        result = {"name": "Login y obtención de token", "method": "POST", "path": auth_cfg["login_path"],
                  "actual_status": resp["status"], "latency_ms": round(resp["elapsed_ms"], 2),
                  "outcome": "pass" if ok else "fail", "problems": problems}
        self.results.append(result)
        self._print(result)
        if ok:
            self.token = token
        return ok

    def run(self, endpoints: List[Dict[str, Any]], title: str) -> None:
        print("\n" + "=" * 96)
        print(f"{BOLD}{CYAN} VALIDACIÓN DE ENDPOINTS — {title}{RESET}")
        print(f" Servidor: {self.base_url}   Muestras GET: {self.samples}   "
              f"Puerta de latencia: {'sí' if self.latency_gate else 'no'}")
        print("=" * 96)
        for ep in endpoints:
            path = ep["path"]
            method = ep.get("method", "GET").upper()
            name = ep.get("name", path)
            if "{" in path and "example_path" not in ep:
                self.skip(name, method, path, "ruta con parámetros: declare 'example_path' en el registro", False)
                continue
            if ep.get("mutates") and not self.include_mutations:
                self.skip(name, method, path, "modifica datos: use --incluir-mutaciones (solo en ambientes de prueba)", False)
                continue
            auth_required = bool(ep.get("auth_required", False))
            target = ep.get("example_path", path)
            if auth_required:
                # BP-05: sin credenciales debe negar el acceso.
                self.check(f"{name} · sin sesión", target, method, [401, 403],
                           ep.get("payload"), use_auth=False, max_latency_ms=ep.get("max_latency_ms", 500),
                           record_curl=False)
                if not self.token:
                    self.skip(name, method, target, "requiere sesión y no hay token (use --token o --login-user)", True)
                    continue
            self.check(name, target, method, ep.get("expected_status", 200), ep.get("payload"),
                       use_auth=auth_required, max_latency_ms=float(ep.get("max_latency_ms", 500)))

    # -------------------------------------------------------------- salida
    def summary(self) -> int:
        counts = {k: sum(1 for r in self.results if r["outcome"] == k) for k in ("pass", "fail", "skip")}
        print("\n" + "=" * 96)
        print(f" Aprobados: {GREEN}{counts['pass']}{RESET}   Fallidos: {RED if counts['fail'] else GREEN}"
              f"{counts['fail']}{RESET}   Omitidos: {YELLOW}{counts['skip']}{RESET}")
        if counts["fail"]:
            print(f" {BOLD}{RED}RECHAZADO: corrija los fallos antes de desplegar.{RESET}\n")
            return 1
        print(f" {BOLD}{GREEN}APROBADO.{RESET}" + (" (revise los omitidos)" if counts["skip"] else "") + "\n")
        return 0

    def export_curls(self, filepath: str) -> None:
        header = ("#!/usr/bin/env bash\n# Generado por validate_endpoints.py (SDD)\n"
                  "# Antes de ejecutar: export SDD_TOKEN=... SDD_CSRF=... SDD_LOGIN_PASSWORD=...\n\n")
        Path(filepath).write_text(header + "\n".join(self.curls), encoding="utf-8")
        print(f"-> cURLs exportados a: {filepath}")

    def export_json(self, filepath: str) -> None:
        report = {
            "base_url": self.base_url,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "passed": sum(1 for r in self.results if r["outcome"] == "pass"),
            "failed": sum(1 for r in self.results if r["outcome"] == "fail"),
            "skipped": sum(1 for r in self.results if r["outcome"] == "skip"),
            "results": [{k: v for k, v in r.items() if k != "body"} for r in self.results],
        }
        Path(filepath).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"-> Reporte JSON exportado a: {filepath}")


def find_registry() -> Optional[Path]:
    """Busca el registro del proyecto (nunca la plantilla del SDD)."""
    project_root = Path(__file__).resolve().parent.parent
    candidates = [
        Path("backend/config/endpoints_registry.json"),
        Path("config/endpoints_registry.json"),
        project_root / "backend" / "config" / "endpoints_registry.json",
    ]
    return next((c for c in candidates if c.is_file()), None)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validador de endpoints y generador de cURLs (SDD)")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--endpoints-file", help="Ruta a endpoints_registry.json (por defecto se busca en backend/config/)")
    parser.add_argument("--token", default=os.getenv("SDD_TOKEN"), help="Access token JWT (o variable SDD_TOKEN)")
    parser.add_argument("--login-user", help="Usuario para el login; la contraseña se lee de SDD_LOGIN_PASSWORD")
    parser.add_argument("--timeout", type=float, default=5.0, help="Segundos por petición")
    parser.add_argument("--samples", type=int, default=1, help="Repeticiones por GET para calcular p95")
    parser.add_argument("--sin-puerta-latencia", action="store_true", help="Reporta la latencia sin fallar por ella")
    parser.add_argument("--incluir-mutaciones", action="store_true", help="Ejecuta endpoints marcados mutates=true")
    parser.add_argument("--export-curls", help="Archivo .sh con los cURL (sin secretos)")
    parser.add_argument("--json-report", help="Archivo JSON con el reporte")
    args = parser.parse_args(argv)

    validator = EndpointValidator(args.base_url, token=args.token, timeout=args.timeout, samples=args.samples,
                                  latency_gate=not args.sin_puerta_latencia,
                                  include_mutations=args.incluir_mutaciones)

    registry_path = Path(args.endpoints_file) if args.endpoints_file else find_registry()
    if registry_path and not registry_path.is_file():
        print(f"{RED}No existe el registro: {registry_path}{RESET}")
        return 1
    if registry_path:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        endpoints = registry.get("endpoints", [])
        auth_cfg = {**DEFAULT_AUTH, **registry.get("auth", {})}
        title = f"{registry.get('project_name', 'proyecto')} ({registry_path})"
    else:
        endpoints, auth_cfg, title = STANDARD_SUITE, dict(DEFAULT_AUTH), "suite estándar (sin registro)"

    if args.login_user and not validator.token:
        password = os.getenv("SDD_LOGIN_PASSWORD")
        if not password:
            print(f"{RED}Defina la variable de entorno SDD_LOGIN_PASSWORD para usar --login-user.{RESET}")
            return 1
        validator.login(auth_cfg, args.login_user, password)

    validator.run(endpoints, title)
    if args.export_curls:
        validator.export_curls(args.export_curls)
    if args.json_report:
        validator.export_json(args.json_report)
    return validator.summary()


if __name__ == "__main__":
    sys.exit(main())
