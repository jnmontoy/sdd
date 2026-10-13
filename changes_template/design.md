# Diseño Técnico y Contratos: [Nombre Breve del Cambio]

## 🏗️ 1. Arquitectura y Componentes Involucrados

### Componentes UI Reutilizados (`.sdd/components/`)
> Prohibido inventar CSS ad-hoc. Especificar qué suites oficiales se integran:
* **Tabla / Data Table**: `components/data_table/data_table.md` (si aplica)
* **Acciones / Toolbars**: `components/button/icon_action_group.md` (28px / 26px)
* **Formularios / Detalle**: `components/drawer/drawer.md` (Right Drawer 560px)
* **Modales de Seguridad**: `components/modal/confirm_modal.md` (con justificación >= 10 caracteres)
* **Notificaciones**: `components/toast/toast_notification.md` (Sonner tokens Jolifoods)

---

## 🔌 2. Contratos de Endpoints (API)

### Registro en `endpoints_registry.json`
> Todo endpoint nuevo o modificado debe registrarse formalmente aquí:

```json
{
  "path": "/api/v1/ejemplo/recurso/",
  "method": "POST",
  "name": "ejemplo:crear_recurso",
  "auth_required": true,
  "roles_allowed": ["ADMIN", "SUPERVISOR"],
  "rate_limit": "120/m",
  "description": "Crea un nuevo registro validado."
}
```

### Esquema Pydantic / Serializer de Entrada (Request)
```python
from pydantic import BaseModel, Field

class RecursoCreateRequest(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=120)
    cantidad: int = Field(..., ge=1)
    activo: bool = True
```

### Esquema de Salida (Response)
```python
class RecursoResponse(BaseModel):
    id: int
    nombre: str
    cantidad: int
    activo: bool
    creado_en: str
```

---

## 🗄️ 3. Impacto en Base de Datos y Modelos
> Especificar si requiere migración de base de datos (`makemigrations` con Zero-Downtime Expand & Contract - BP-08 de Greenfield).

* **Tabla Afectada**: `ejemplo_recurso`
* **Nuevos Campos**:
  * `codigo_lote` (CharField 50 nullable inicial)
* **Transaccionalidad (BP-12)**:
  * Toda mutación que afecte más de una tabla debe envolverse en `with transaction.atomic():`.
* **Persistencia en Bloque (BP-13)**:
  * Prohibido `.save()` individual en bucles; usar `bulk_create` / `bulk_update`.

---

## 🛡️ 4. Casos de Borde y Manejo de Errores (Edge Cases)
> Respuestas a preguntas clave (*Grill-Me*) previas a la codificación:

| Escenario / Caso de Borde | Comportamiento Esperado | Código HTTP / Error |
| :--- | :--- | :--- |
| **Usuario sin permisos RBAC** | Denegar acceso con mensaje informativo sin exponer trazas internas. | `403 Forbidden` |
| **Registro duplicado por concurrencia** | Capturar `IntegrityError` y retornar aviso claro al usuario. | `409 Conflict` |
| **Payload corrupto o campos vacíos** | Validación inmediata con detalle de campo fallido. | `422 Unprocessable Entity` |
| **Tabla sin registros (Estado Vacío)** | Renderizar `EmptyState` con botón CTA constructivo. | `200 OK []` |
| **Conexión de red caída (Offline/Timeout)** | Mostrar toast Sonner persistente con botón "Reintentar". | Error UI |
