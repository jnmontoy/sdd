# Especificación de Modelo: Bitácora de Auditoría de Operaciones
## Directorio: `.sdd/model/auditoria/spec_model_bitacora.md`

Registro **solo-inserción** de operaciones y cambios de estado (crear, editar, eliminar, exportar, cambios de permisos) en las aplicaciones de Joli Foods. Los intentos de acceso se registran aparte en `RegistroAuditoriaAcceso` ([`../login/spec_model_sesion_auditoria.md`](../login/spec_model_sesion_auditoria.md)).

---

## 1. Atributos de `RegistroBitacoraAuditoria`

| Campo | Tipo SQL | Django | Nulo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `UUIDField(primary_key=True, default=uuid4, editable=False)` | No | Identificador. |
| `usuario_id` | `BIGINT` | `ForeignKey(AUTH_USER_MODEL, on_delete=SET_NULL)` | Sí | Quién ejecutó la acción (nulo = proceso del sistema). |
| `numero_documento` | `VARCHAR(15)` | `CharField(max_length=15, blank=True)` | No (puede ser `''`) | Copia del documento del actor, para conservar la traza si el usuario cambia. |
| `tipo_evento` | `VARCHAR(50)` | `CharField(max_length=50)` | No | `CREATE`, `UPDATE`, `DELETE`, `EXPORT`, `ROLE_PERMISSIONS_UPDATED`, `CONFIG_UPDATED`… |
| `modulo` | `VARCHAR(50)` | `CharField(max_length=50)` | No | Módulo afectado (`usuarios`, `roles`, `configuracion`…). |
| `entidad_id` | `VARCHAR(64)` | `CharField(max_length=64, blank=True)` | No (puede ser `''`) | Identificador del registro afectado. |
| `ip_origen` | `INET` | `GenericIPAddressField(null=True)` | Sí | IP del cliente. |
| `user_agent` | `VARCHAR(512)` | `CharField(max_length=512, blank=True)` | No | Navegador (truncado). |
| `payload_antes` | `JSONB` | `JSONField(null=True)` | Sí | Estado previo, **sin campos sensibles**. |
| `payload_despues` | `JSONB` | `JSONField(null=True)` | Sí | Estado posterior, **sin campos sensibles**. |
| `resultado` | `VARCHAR(10)` | `CharField(max_length=10, choices)` | No | `EXITO` o `FALLO`. |
| `detalles` | `TEXT` | `TextField(blank=True)` | No | Descripción legible. |
| `fecha_hora` | `TIMESTAMPTZ` | `DateTimeField(auto_now_add=True)` | No | Momento del evento (UTC). |

**Datos sensibles:** antes de guardar `payload_antes`/`payload_despues` se DEBEN quitar `password`, tokens, hashes y secretos (lista `CAMPOS_EXCLUIDOS`). **Por qué:** la bitácora la leen auditores y se exporta a Excel/PDF.

---

## 2. DDL (PostgreSQL)

```sql
CREATE TABLE auditoria_bitacora (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id       BIGINT       NULL REFERENCES usuarios(id) ON DELETE SET NULL,
    numero_documento VARCHAR(15)  NOT NULL DEFAULT '',
    tipo_evento      VARCHAR(50)  NOT NULL,
    modulo           VARCHAR(50)  NOT NULL,
    entidad_id       VARCHAR(64)  NOT NULL DEFAULT '',
    ip_origen        INET         NULL,
    user_agent       VARCHAR(512) NOT NULL DEFAULT '',
    payload_antes    JSONB        NULL,
    payload_despues  JSONB        NULL,
    resultado        VARCHAR(10)  NOT NULL DEFAULT 'EXITO',
    detalles         TEXT         NOT NULL DEFAULT '',
    fecha_hora       TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_bitacora_resultado CHECK (resultado IN ('EXITO', 'FALLO'))
);

CREATE INDEX idx_bitacora_fecha          ON auditoria_bitacora (fecha_hora DESC);
CREATE INDEX idx_bitacora_modulo_evento  ON auditoria_bitacora (modulo, tipo_evento);
CREATE INDEX idx_bitacora_doc_fecha      ON auditoria_bitacora (numero_documento, fecha_hora DESC);
CREATE INDEX idx_bitacora_usuario        ON auditoria_bitacora (usuario_id);

-- Solo-inserción para el rol de la aplicación
REVOKE UPDATE, DELETE, TRUNCATE ON auditoria_bitacora FROM app_user;
GRANT  SELECT, INSERT ON auditoria_bitacora TO app_user;
```

---

## 3. Django ORM (`backend/apps/auditoria/models.py`)

```python
import uuid

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q

CAMPOS_EXCLUIDOS = {"password", "token", "token_hash", "refresh", "access", "secret", "api_key"}


def limpiar_payload(datos: dict | None) -> dict | None:
    """Quita campos sensibles antes de registrar el estado de una entidad."""
    if datos is None:
        return None
    return {k: v for k, v in datos.items() if k.lower() not in CAMPOS_EXCLUIDOS}


class BitacoraQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise PermissionDenied("La bitácora es solo-inserción.")

    def delete(self):
        raise PermissionDenied("La bitácora es solo-inserción.")


class RegistroBitacoraAuditoria(models.Model):
    class Resultado(models.TextChoices):
        EXITO = "EXITO", "Éxito"
        FALLO = "FALLO", "Fallo"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs_auditoria",
    )
    numero_documento = models.CharField(max_length=15, blank=True, default="")
    tipo_evento = models.CharField(max_length=50)
    modulo = models.CharField(max_length=50)
    entidad_id = models.CharField(max_length=64, blank=True, default="")
    ip_origen = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default="")
    payload_antes = models.JSONField(null=True, blank=True)
    payload_despues = models.JSONField(null=True, blank=True)
    resultado = models.CharField(max_length=10, choices=Resultado.choices, default=Resultado.EXITO)
    detalles = models.TextField(blank=True, default="")
    fecha_hora = models.DateTimeField(auto_now_add=True)

    objects = BitacoraQuerySet.as_manager()

    class Meta:
        db_table = "auditoria_bitacora"
        ordering = ["-fecha_hora"]
        indexes = [
            models.Index(fields=["-fecha_hora"], name="idx_bitacora_fecha"),
            models.Index(fields=["modulo", "tipo_evento"], name="idx_bitacora_modulo_evento"),
            models.Index(fields=["numero_documento", "-fecha_hora"], name="idx_bitacora_doc_fecha"),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(resultado__in=["EXITO", "FALLO"]), name="chk_bitacora_resultado"),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise PermissionDenied("La bitácora es solo-inserción.")
        self.payload_antes = limpiar_payload(self.payload_antes)
        self.payload_despues = limpiar_payload(self.payload_despues)
        self.user_agent = self.user_agent[:512]
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionDenied("La bitácora es solo-inserción.")

    def __str__(self) -> str:
        return f"[{self.fecha_hora:%Y-%m-%d %H:%M}] {self.tipo_evento} {self.modulo} ({self.resultado})"
```

El índice de `usuario_id` lo crea Django automáticamente por ser `ForeignKey`. La retención (p. ej. depurar registros de más de N años) la ejecuta un rol de base de datos de mantenimiento, no la aplicación.
