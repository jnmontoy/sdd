# Protocolo 08: migraciones de base de datos sin interrupción y recuperación ante desastres

Reglas para cambiar la estructura de bases de datos PostgreSQL en producción **sin detener el servicio ni bloquear tablas por tiempo prolongado**, y la política de respaldo y recuperación (**RPO/RTO**).

Las palabras **DEBE / DEBERÍA / PUEDE** siguen la RFC 2119.

> **Alcance**: aplica a tablas con tráfico en producción. En desarrollo, o en tablas pequeñas sin uso concurrente, una migración directa es aceptable.
> **Estado de implementación en el SDD**: este protocolo es normativo; el SDD no incluye scripts de respaldo/restauración ni configuración de archivado WAL.

---

## 1. Patrón *Expand & Contract* (ampliar y luego contraer)

Los cambios destructivos (renombrar o eliminar columnas, cambiar tipos, volver obligatorio un campo existente) NO DEBEN aplicarse en un solo despliegue. **Por qué:** durante un despliegue conviven la versión vieja y la nueva del código; si la base de datos cambia de golpe, la versión vieja falla.

```text
 1. EXPANDIR          2. ESCRIBIR EN AMBAS     3. RELLENAR           4. LEER LO NUEVO       5. CONTRAER
 Agregar columna  ->  El código escribe en ->  Copiar datos      ->  El código lee y   ->  Migración posterior
 nueva (nula).        la vieja y la nueva.     históricos por        escribe solo la       elimina la columna
                                               lotes.                nueva.                vieja.
```

Cada paso es un despliegue separado y reversible hasta el paso 5. Ejemplo: renombrar `nombre` a `razon_social` implica 4–5 despliegues, no una migración `RenameField`.

---

## 2. Reglas técnicas para PostgreSQL con Django

1. **Índices sin bloqueo de escritura.** En tablas grandes o con escritura frecuente, los índices DEBERÍAN crearse con `CONCURRENTLY`. En Django se usa `AddIndexConcurrently` y la migración debe declararse no atómica, porque `CREATE INDEX CONCURRENTLY` no puede ejecutarse dentro de una transacción:

   ```python
   from django.contrib.postgres.operations import AddIndexConcurrently
   from django.db import migrations, models


   class Migration(migrations.Migration):
       atomic = False
       dependencies = [("core", "0012_previa")]
       operations = [
           AddIndexConcurrently(
               model_name="usuario",
               index=models.Index(fields=["numero_documento"], name="idx_usuario_documento"),
           ),
       ]
   ```

   Si la creación concurrente falla, deja un índice marcado `INVALID` que hay que eliminar (`DROP INDEX CONCURRENTLY`) antes de reintentar.

2. **Columnas con valor por defecto.** Desde PostgreSQL 11, `ADD COLUMN ... DEFAULT <constante>` no reescribe la tabla si el valor por defecto no es volátil. Con un valor volátil (p. ej. `now()` o `gen_random_uuid()`), la columna DEBE nacer nula y rellenarse por lotes.

3. **Volver obligatoria una columna existente (`NOT NULL`).** `SET NOT NULL` recorre toda la tabla con bloqueo exclusivo. Alternativa sin bloqueo prolongado (PostgreSQL 12+):
   1. `ADD CONSTRAINT ... CHECK (col IS NOT NULL) NOT VALID;`
   2. `VALIDATE CONSTRAINT ...;` (no bloquea escrituras)
   3. `ALTER COLUMN col SET NOT NULL;` (usa la restricción validada y no recorre la tabla)
   4. Eliminar la restricción `CHECK` auxiliar.

4. **Tiempo máximo de espera de bloqueo.** Las migraciones sobre tablas con tráfico DEBERÍAN fijar `lock_timeout` para no encolar a los usuarios detrás de un `ALTER TABLE` que espera. En Django, como primera operación de la migración (las migraciones son transaccionales en PostgreSQL, así que `SET LOCAL` aplica solo a ella):

   ```python
   migrations.RunSQL("SET LOCAL lock_timeout = '3s';", reverse_sql=migrations.RunSQL.noop),
   ```

   Si no obtiene el bloqueo en 3 s, la migración falla y se reintenta en un momento de menos tráfico (el reintento es manual o del *pipeline*; Django no reintenta solo).

5. **Probar la migración** con un volumen de datos similar al de producción en staging antes de aplicarla.

---

## 3. Migración de datos por lotes

Para actualizar muchos registros NO DEBE usarse un único `UPDATE` sobre toda la tabla. **Por qué:** una transacción gigante mantiene bloqueos, genera mucho WAL (registro de escritura anticipada) y retrasa réplicas.

Se usa un comando de gestión o una tarea de Celery que recorra por clave primaria, con una transacción por lote:

```python
import time

from django.db import transaction
from django.db.models import F

from core.models import Modelo


def migrar_en_lotes(batch_size: int = 1000, pausa_s: float = 0.1) -> int:
    """Copia columna_vieja -> columna_nueva por lotes. Idempotente: se puede relanzar."""
    ultimo_id = 0
    total = 0
    while True:
        ids = list(
            Modelo.objects.filter(id__gt=ultimo_id, columna_nueva__isnull=True)
            .order_by("id")
            .values_list("id", flat=True)[:batch_size]
        )
        if not ids:
            return total
        with transaction.atomic():
            total += Modelo.objects.filter(id__in=ids).update(columna_nueva=F("columna_vieja"))
        ultimo_id = ids[-1]
        time.sleep(pausa_s)  # deja respirar a la base de datos y a las réplicas
```

---

## 4. Respaldo y recuperación ante desastres

Cada base de datos de producción DEBE tener objetivos definidos y probados:

| Parámetro | Definición | Meta de referencia | Mecanismo necesario |
|---|---|---|---|
| **RPO** (*Recovery Point Objective*) | Máxima pérdida de datos aceptable, medida en tiempo. | ≤ 15 minutos | Archivado continuo del WAL (p. ej. con pgBackRest o WAL-G) a almacenamiento externo, además del respaldo completo. |
| **RTO** (*Recovery Time Objective*) | Tiempo máximo para restablecer el servicio. | ≤ 4 horas (ajustar según criticidad del sistema) | Respaldo completo diario automatizado + procedimiento de restauración documentado y ensayado. |

Las metas son **objetivos**, no garantías: solo se consideran cumplidas cuando un simulacro lo demuestra. Cada proyecto DEBE acordarlas con el dueño del proceso de negocio y con infraestructura.

### Simulacro de restauración
* Al menos cada trimestre, restaurar en un entorno aislado y medir el tiempo real (RTO observado) y el punto de recuperación alcanzado (RPO observado).
* Verificar integridad: conteos por tabla, restricciones de integridad referencial y una muestra de registros recientes.
* Registrar el resultado (fecha, tiempos, problemas) como evidencia; si no se cumple la meta, se abre una acción correctiva.
