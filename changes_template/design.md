# Diseño técnico y contratos: [Nombre breve del cambio]

## 1. Componentes involucrados

### Componentes de interfaz reutilizados (`.sdd/components/`)
> Se DEBERÍA ensamblar con componentes existentes y tokens de `variables.css`. Si hace falta un estilo nuevo, se justifica aquí y se propone como mejora del componente, no como CSS suelto del módulo.

* **Tabla**: `components/data_table/data_table.md` (si aplica)
* **Acciones**: `components/button/icon_action_group.md` (barra 28 px / fila 26 px con `btn-group`)
* **Formulario / detalle**: `components/drawer/drawer.md` (tamaño `md` por defecto)
* **Confirmaciones**: `components/modal/confirm_modal.md` (motivo mínimo 10 caracteres)
* **Avisos**: `components/toast/toast_notification.md`

---

## 2. Contratos de endpoints

### Registro en `backend/config/endpoints_registry.json`
> Todo endpoint nuevo o modificado se registra; el validador `pruebas/validate_endpoints.py` lo lee. Ver la plantilla en `.sdd/stack/endpoints_registry_template.json` para el formato exacto de campos.

```json
{
  "name": "Recursos: crear",
  "module": "ejemplo",
  "path": "/api/v1/ejemplo/recurso/",
  "method": "POST",
  "expected_status": 201,
  "auth_required": true,
  "mutates": true,
  "max_latency_ms": 500,
  "description": "Crea un nuevo registro validado. Roles: ADMIN, SUPERVISOR."
}
```

> `mutates: true` hace que el validador lo omita salvo que se ejecute con `--incluir-mutaciones` (hacerlo solo contra un entorno de pruebas).

### Esquema de entrada (Pydantic v2 o serializador DRF)
```python
from pydantic import BaseModel, Field


class RecursoCreateRequest(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=120)
    cantidad: int = Field(..., ge=1)
    activo: bool = True
```

### Esquema de salida
```python
from datetime import datetime

from pydantic import BaseModel


class RecursoResponse(BaseModel):
    id: int
    nombre: str
    cantidad: int
    activo: bool
    creado_en: datetime  # se serializa en ISO 8601
```

### ¿Es un cambio que rompe compatibilidad?
> Si elimina o renombra campos, cambia tipos o vuelve obligatorio un parámetro, sigue el protocolo 09 (nueva versión o deprecación con cabeceras `Deprecation`/`Sunset`).

* [Sí / No — justificación]

---

## 3. Impacto en base de datos
> Si hay migración en producción con tablas grandes o tráfico, seguir el patrón *Expand & Contract* del [protocolo 08](../greenfield/08_protocolo_migraciones_zero_downtime.md).

* **Tabla afectada**: `ejemplo_recurso`
* **Campos nuevos**: `codigo_lote` (CharField 50, nulo en la primera migración)
* **Transacciones (BP-12)**: operaciones con 2 o más escrituras dependientes dentro de `transaction.atomic()`.
* **Escritura en bloque (BP-13)**: colecciones con `bulk_create` / `bulk_update`, no `.save()` en bucles.
* **Consultas**: relaciones con `select_related` / `prefetch_related` para evitar N+1 (una consulta por fila).

---

## 4. Casos de borde
| Escenario | Comportamiento esperado | Código HTTP / resultado |
| :--- | :--- | :--- |
| Usuario sin permiso | Mensaje claro sin trazas internas | `403 Forbidden` |
| Sesión vencida | Interceptor intenta 1 refresh; si falla, `SessionExpirationModal` | `401 Unauthorized` |
| Duplicado por concurrencia | Capturar `IntegrityError`, aviso claro | `409 Conflict` |
| Datos inválidos | Detalle por campo | `400` (DRF) / `422` (FastAPI) |
| Sin registros | `EmptyState` con acción sugerida | `200 OK` con lista vacía |
| Red caída o tiempo agotado | Toast persistente con "Reintentar" | Error de interfaz |

## 5. Riesgos y reversión
* **Riesgo principal**: [...]
* **Cómo se revierte**: [revert del commit / feature flag / migración inversa]
