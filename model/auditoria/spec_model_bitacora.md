# Especificación de Modelo: Bitácora de Auditoría de Operaciones
## Directorio: `.sdd/model/auditoria/spec_model_bitacora.md`

Este documento define la entidad de persistencia para el registro inmutable de transacciones y cambios de estado en las aplicaciones del ecosistema **Jolifoods**.

---

## 1. Atributos de la Entidad `RegistroBitacoraAuditoria`

| Campo | Tipo SQL | Python / Django | Restricciones / Índices | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `models.UUIDField` | `primary_key=True, default=uuid.uuid4, editable=False` | Identificador universal único inmutable |
| `usuario_id` | `BIGINT` | `models.ForeignKey` | `null=True, blank=True, on_delete=SET_NULL, related_name='logs_auditoria'` | Colaborador que ejecutó la acción (o null si es sistema) |
| `numero_documento`| `VARCHAR(20)`| `models.CharField` | `db_index=True, max_length=20` | Documento del usuario guardado de forma redundante |
| `tipo_evento` | `VARCHAR(50)`| `models.CharField` | `db_index=True, max_length=50` | `LOGIN_SUCCESS`, `CREATE`, `UPDATE`, `DELETE`, etc. |
| `modulo` | `VARCHAR(50)`| `models.CharField` | `db_index=True, max_length=50` | Módulo afectado (`USUARIOS`, `INVENTARIO`, `AUTENTICACION`) |
| `ip_origen` | `VARCHAR(45)`| `models.GenericIPAddressField` | `null=True, blank=True` | IPv4 o IPv6 desde donde se ejecutó la petición |
| `user_agent` | `TEXT` | `models.TextField` | `blank=True` | Agente de navegador del cliente |
| `payload_antes` | `JSONB` | `models.JSONField` | `null=True, blank=True` | Estado de la entidad ANTES de la modificación |
| `payload_despues`| `JSONB` | `models.JSONField` | `null=True, blank=True` | Estado de la entidad DESPUÉS de la modificación |
| `resultado` | `VARCHAR(20)`| `models.CharField` | `max_length=20, default='EXITO'` | `EXITO` o `FALLO` |
| `detalles` | `TEXT` | `models.TextField` | `blank=True` | Descripción humana legible del evento |
| `fecha_hora` | `TIMESTAMPTZ`| `models.DateTimeField` | `auto_now_add=True, db_index=True` | Timestamp UTC inmutable de ocurrencia |

---

## 2. Implementación en Django ORM

```python
import uuid
from django.db import models
from django.conf import settings

class RegistroBitacoraAuditoria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs_auditoria",
        db_index=True
    )
    numero_documento = models.CharField(max_length=20, db_index=True)
    tipo_evento = models.CharField(max_length=50, db_index=True)
    modulo = models.CharField(max_length=50, db_index=True)
    ip_origen = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    payload_antes = models.JSONField(null=True, blank=True)
    payload_despues = models.JSONField(null=True, blank=True)
    resultado = models.CharField(max_length=20, default="EXITO")
    detalles = models.TextField(blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "auditoria_bitacora"
        ordering = ["-fecha_hora"]
        indexes = [
            models.Index(fields=["modulo", "tipo_evento"]),
            models.Index(fields=["numero_documento", "fecha_hora"]),
        ]

    def __str__(self):
        return f"[{self.fecha_hora}] {self.tipo_evento} - {self.numero_documento} ({self.modulo})"
```
