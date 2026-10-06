# Protocolo de Pruebas Automáticas, Validación de Endpoints y Calidad Cero-Bugs
## Ecosistema Corporativo Jolifoods / Greenyard — Metodología SDD

Este protocolo establece los lineamientos mandatorios de aseguramiento de calidad automatizado (**Quality Assurance - QA**) para certificar que cualquier servicio, API o interfaz de usuario llegue a producción **libre de errores, regresiones y vulnerabilidades**.

---

## 1. La Pirámide de Testing Obligatoria en SDD

```text
                           ▲
                          / \
                         /   \     E2E / Smoke Tests (Playwright)
                        / E2E \    Flujos críticos de punta a punta (10%)
                       /───────\
                      /         \   Integración & Endpoints (Pytest + TestClient)
                     /   APIs    \  Validación de contratos, status HTTP, Auth (30%)
                    /─────────────\
                   /   Unitarias   \ Unitarias (Pytest / Vitest)
                  /   & Servicios   \ Servicios, validadores Zod/Pydantic, helpers (60%)
                 /───────────────────\
```

---

## 2. Validación Automatizada de Endpoints (Backend Django + FastAPI)

Todo endpoint desarrollado en el ecosistema debe contar con una suite de pruebas de integración usando **Pytest** y los clientes oficiales de prueba.

### 2.1. Matriz de Cobertura Obligatoria por Endpoint
Para que un endpoint se considere aprobado para producción, debe superar 5 casos de prueba automatizados:
1. **Caso Exitoso (200 / 201)**: Payload válido, verificación de persistencia y contrato de retorno JSON.
2. **Caso No Autenticado (401)**: Solicitud sin cabecera `Authorization` o con token expirado.
3. **Caso No Autorizado (403 - RBAC)**: Solicitud de un usuario con rol sin privilegios para esa acción.
4. **Validación de Datos Inválidos (400 / 422)**: Campos faltantes o tipos de datos erróneos validados por Pydantic/Serializers.
5. **Rate Limiting (429)**: Exceso de solicitudes en una ventana de tiempo con verificación de cabecera `Retry-After`.

---

### 2.2. Suite Canónica de Pruebas para Endpoints FastAPI (`TestClient`)

```python
import pytest
from fastapi.testclient import TestClient
from config.asgi import fast_app

client = TestClient(fast_app)

def test_fast_endpoint_health():
    """Verifica respuesta instantánea del microservicio /fast."""
    response = client.get("/fast/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_fast_endpoint_rechaza_sin_token():
    """Valida principio Deny-by-Default (HTTP 401)."""
    response = client.get("/fast/v1/metricas/kpi")
    assert response.status_code == 401

def test_fast_endpoint_validacion_pydantic():
    """Valida que entradas corruptas retornen 422 Unprocessable Entity."""
    headers = {"Authorization": "Bearer token_valido_test"}
    payload_invalido = {"monto": "no_es_un_numero", "fecha": "fecha_invalida"}
    response = client.post("/fast/v1/transacciones", json=payload_invalido, headers=headers)
    assert response.status_code == 422
    assert "detail" in response.json()
```

---

### 2.3. Suite Canónica de Pruebas para Endpoints Django (`APIClient`)

```python
import pytest
from rest_framework.test import APIClient
from apps.auth_core.models import Usuario, Rol

@pytest.mark.django_db
class TestUsuariosEndpoints:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.client = APIClient()
        self.rol_admin = Rol.objects.create(nombre="Administrador", codigo="ADMIN")
        self.usuario_admin = Usuario.objects.create(
            numero_documento="12345678",
            email="admin@jolifoods.co",
            rol=self.rol_admin,
            is_active=True
        )

    def test_listado_usuarios_anti_n_plus_one(self, django_assert_num_queries):
        """Verifica que el listado de usuarios no dispare consultas N+1."""
        self.client.force_authenticate(user=self.usuario_admin)
        
        # Con select_related, el listado debe resolverse en máximo 2 consultas SQL
        with django_assert_num_queries(2):
            response = self.client.get("/api/v1/usuarios/")
            assert response.status_code == 200
            assert "results" in response.json()
```

---

## 3. Pruebas de Extremo a Extremo (E2E) con Playwright

Las pruebas E2E validan la interacción real del usuario en navegadores Chromium, Firefox y WebKit headless:
- Simulación de inicio de sesión y persistencia de cookies seguras.
- Navegación fluida y apertura de formularios en el **Right Sidebar Drawer**.
- Filtrado dinámico en la tabla (`ChecklistPopover`) y ordenamiento interactivo.
- Confirmación visual de acciones destructivas vía `ConfirmModal`.

---

## 4. Umbrales de Calidad Obligatorios (Quality Gates)

| Indicador | Requisito Mínimo | Consecuencia de Incumplimiento |
| :--- | :--- | :--- |
| **Cobertura de Código (Coverage)** | **Mínimo 80%** en lógica de negocio, servicios y endpoints. | Pipeline CI bloqueado de forma inmediata. |
| **Consultas N+1** | **0 consultas redundantes** detectadas por `django_assert_num_queries`. | Pull Request rechazado en revisión técnica. |
| **Vulnerabilidades en Dependencias** | **0 fallos Altos/Críticos** en `pip-audit` y `npm audit`. | Despliegue abortado. |
| **Pruebas E2E de Humo** | **100% de tests aprobados** en ambiente estéril. | Prohibición de pase a producción. |

---

## 5. Validador Universal de Endpoints y Generador de cURLs (`validate_endpoints.py`)

Para no tener que programar scripts de prueba desde cero en cada proyecto o complemento, el SDD incluye en `.sdd/stack/validate_endpoints.py` una herramienta automatizada (sin dependencias externas) que audita cualquier instancia desplegada o local:

### 5.1. Ejecución Rápida
```bash
# 1. Validación básica de salud y seguridad contra servidor local
python backend/validate_endpoints.py --base-url http://localhost:8000

# 2. Validación completa con autenticación y exportación de cURLs ejecutables
python backend/validate_endpoints.py \
  --base-url https://apptic.jolifoods.co \
  --login-doc "12345678" \
  --login-pass "ClaveSegura2026!" \
  --export-curls test_curls.sh \
  --json-report reporte_auditoria.json
```

### 5.2. Capacidades Automáticas
- **Healthchecks**: `/health/live` y `/health/ready` (valida conexión activa a PostgreSQL y Redis).
- **Seguridad Perimetral**: Verifica presencia de `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` y HSTS en HTTPS.
- **SLO de Latencia**: Falla si un endpoint `/fast/v1/` excede los 45ms o si un endpoint estándar excede 500ms.
- **Generación de cURLs**: Crea comandos `curl -X ...` reproducibles para pruebas manuales o Postman.
- **Retorno para CI/CD**: Devuelve `exit code 0` si todos los tests pasan, o `exit code 1` para frenar el despliegue automático si se detecta un bug.

### 5.3. Lectura Automática desde el Registro Centralizado (`endpoints_registry.json`)
Para evitar tener que apuntar el verificador de endpoints manualmente por diferentes vistas del proyecto:
1. Las vistas de frontend **nunca queman URLs**; importan desde `src/services/endpoints.ts`.
2. El backend y los pipelines consumen `backend/config/endpoints_registry.json`.
3. Al ejecutar `python backend/validate_endpoints.py`, el validador **lee automáticamente el manifiesto JSON** y prueba todas las rutas de la plataforma en una sola pasada:
```bash
python backend/validate_endpoints.py --endpoints-file backend/config/endpoints_registry.json --base-url https://apptic.jolifoods.co
```

---

## 6. Exención Absoluta: Modo Mock No-Code (`mock/`)

> [!IMPORTANT]
> **REGLA DE ORO SDD**: En el **Modo Mock (`mock/`)**, queda **TERMINANTEMENTE PROHIBIDO Y ES TOTALMENTE INNECESARIO** exigir o ejecutar pruebas automáticas, testing unitario, suites E2E (Playwright), Pytest o validaciones con `validate_endpoints.py`.

### 6.1. Justificación Técnica y de Negocio
1. **Naturaleza del Prototipo**: Un mock es **única y exclusivamente una simulación visual e interactiva** construida en HTML, CSS y JavaScript ligero, pensada para usuarios de negocio, gerentes o líderes de área que **no son programadores**.
2. **Cero Backend Real**: En el modo mock no existe un servidor Django/FastAPI encendido, ni base de datos PostgreSQL, ni servicios de autenticación JWT reales. Exigir pruebas de endpoints o assertions automatizados contra un mock es un error conceptual que contradice la filosofía de agilidad No-Code.
3. **Objetivo Único del Mock**:
   - Validar la disposición visual, ergonomía y flujos de pantalla con el cliente interno.
   - Definir con precisión el contrato de datos JSON (`datos_[pantalla].md`) que el backend requerirá posteriormente.
4. **¿Cuándo se Aplica el Testing?**:
   - El protocolo de pruebas automáticas (Playwright, Pytest, `validate_endpoints.py`, CI/CD Quality Gates) se activa **únicamente cuando el desarrollador toma el mock aprobado y comienza la implementación real en código de producción** dentro de `frontend/` y `backend/`.



