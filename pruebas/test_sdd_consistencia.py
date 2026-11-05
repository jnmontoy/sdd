"""Coherencia de la documentación del SDD.

Verifica de forma automática las decisiones de la auditoría del 2026-11-04 para que no se
reintroduzcan: enlaces válidos, tokens fuera del almacenamiento del navegador, rutas canónicas,
sin datos de infraestructura real y sin proyectos presentados como estándar.
"""
import re
import unittest
from pathlib import Path

SDD = Path(__file__).resolve().parent.parent
EXCLUDED_DIRS = {".git", ".venv", "node_modules", "__pycache__", "pruebas"}
TEXT_SUFFIXES = {".md", ".html", ".css", ".py", ".json", ".ts", ".tsx", ".js", ".yml", ".sh", ".ps1", ".example"}
PROJECTS = r"tiendita|vibra|app_tic|contenedores|porter[ií]as|joliverso|proyectovideo"
# Documento cuyo propósito es justamente registrar la procedencia por proyecto.
PROVENANCE_DOC = SDD / "greenfield" / "13_catalogo_innovaciones_y_mejores_practicas_proyectos.md"


def text_files():
    for path in SDD.rglob("*"):
        if path.is_file() and path.suffix in TEXT_SUFFIXES and not (set(path.relative_to(SDD).parts) & EXCLUDED_DIRS):
            yield path, path.read_text(encoding="utf-8", errors="replace")


def offending_lines(pattern, flags=0, skip=lambda path, line: False):
    regex = re.compile(pattern, flags)
    hits = []
    for path, content in text_files():
        for number, line in enumerate(content.splitlines(), 1):
            if regex.search(line) and not skip(path, line):
                hits.append(f"{path.relative_to(SDD)}:{number}: {line.strip()[:140]}")
    return hits


class DocumentationConsistency(unittest.TestCase):
    maxDiff = None

    def assertNoHits(self, hits, why):
        self.assertEqual(hits, [], f"{why}\n" + "\n".join(hits[:40]))

    def test_sin_marcadores_de_conflicto_de_merge(self):
        self.assertNoHits(offending_lines(r"^(<{7}|>{7})( |$)|^={7}$"),
                          "Hay conflictos de merge sin resolver")

    def test_enlaces_relativos_existen(self):
        link = re.compile(r"\]\(([^)\s]+)\)")
        broken = []
        for path, content in text_files():
            if path.suffix != ".md":
                continue
            content = re.sub(r"```.*?```", "", content, flags=re.S)  # ignorar bloques de código
            for target in link.findall(content):
                if re.match(r"^(https?:|mailto:|#|<)", target):
                    continue
                file_part = target.split("#", 1)[0]
                if file_part and not (path.parent / file_part).exists():
                    broken.append(f"{path.relative_to(SDD)} -> {target}")
        self.assertNoHits(broken, "Enlaces relativos rotos")

    def test_tokens_no_van_a_storage_del_navegador(self):
        self.assertNoHits(
            offending_lines(r"(local|session)Storage\.(get|set)Item\(\s*['\"`][^'\"`]*(token|access|refresh|user_info)",
                            re.I),
            "BP-18: ningún token ni dato de sesión en localStorage/sessionStorage",
        )

    def test_sin_residuos_de_otra_empresa(self):
        self.assertNoHits(offending_lines(r"greenyard|\bgy_", re.I), "Quitar 'Greenyard' y el prefijo gy_")

    def test_sin_infraestructura_real(self):
        self.assertNoHits(
            offending_lines(r"129\.213\.95\.33|apptic\.jolifoods\.co|apps\.jolifoods\.co|JoliAdmin2026|ClaveSegura2026|JoliSecure2026"),
            "Ejemplos con IPs, dominios o contraseñas reales",
        )

    def test_rutas_canonicas_de_salud_y_validador(self):
        hits = offending_lines(r"/api/v1/health|/api/health|backend/validate_endpoints\.py|backend/tests/")
        self.assertNoHits(hits, "Rutas canónicas: /health/live, /health/ready y pruebas/validate_endpoints.py")

    def test_orjson_no_es_default(self):
        self.assertNoHits(offending_lines(r"default_response_class\s*=\s*ORJSONResponse"),
                          "ORJSONResponse está obsoleto en FastAPI actual")

    def test_proyectos_no_son_estandar(self):
        pattern = rf"(est[aá]ndar|canónic[oa]|patrón canónico)[^.\n]{{0,25}}\b({PROJECTS}|bi\s*/\s*cartera|bi cartera)\b"
        self.assertNoHits(offending_lines(pattern, re.I), "Un proyecto no es un estándar: usar nombre funcional + nota de Origen")

    def test_nombres_de_proyecto_solo_como_procedencia(self):
        def allowed(path, line):
            return path == PROVENANCE_DOC or re.search(r"origen|procedencia|fuente|extra[ií]do de|tomado de", line, re.I)

        hits = offending_lines(rf"\b({PROJECTS})\b", re.I, skip=allowed)
        self.assertNoHits(hits, "Nombres de proyecto fuera de una nota de Origen")


if __name__ == "__main__":
    unittest.main()
