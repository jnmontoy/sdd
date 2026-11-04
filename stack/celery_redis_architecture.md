# Tareas en segundo plano con Celery y Redis

Celery ejecuta fuera de la petición HTTP el trabajo que tarda o que se repite. Redis cumple dos papeles: lleva la cola de mensajes (*broker*) y guarda los resultados.

> **Origen:** patrón usado en varios proyectos internos para correos masivos, reportes PDF/Excel y sincronizaciones periódicas. Aquí se describe de forma genérica.

---

## 1. Cuándo usarlo

Use una tarea de Celery cuando la operación:

- tarda más de 1 o 2 segundos (reportes, procesamiento de archivos, envíos masivos);
- depende de un servicio externo lento o poco confiable (ERP, correo, API de terceros);
- debe repetirse según un horario (Celery Beat).

El endpoint responde `202 Accepted` con un `task_id` y el frontend consulta el avance (ver [`realtime/js_polling_architecture.md`](../components/realtime/js_polling_architecture.md)).

No la use para operaciones cortas: agrega latencia, infraestructura y puntos de falla.

---

## 2. Bases de Redis por propósito

| Base | Uso | Variable |
| :--- | :--- | :--- |
| `0` | Cola de Celery | `CELERY_BROKER_URL=redis://redis:6379/0` |
| `1` | Caché de Django y limitación de tasa | `REDIS_URL=redis://redis:6379/1` |
| `2` | Resultados de Celery | `CELERY_RESULT_BACKEND=redis://redis:6379/2` |

**Por qué separarlas:** borrar la caché (`FLUSHDB`) no debe borrar tareas pendientes ni resultados.

---

## 3. Configuración

`backend/config/celery.py` (lo crea `init_project.py`):

```python
import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "verificar-alertas-cada-5-min": {
        "task": "apps.auth_core.tasks.verificar_alertas_sistema",
        "schedule": 300.0,
    },
    "limpiar-tokens-vencidos-medianoche": {
        "task": "apps.auth_core.tasks.limpiar_tokens_vencidos",
        "schedule": crontab(hour=0, minute=0),
    },
}
```

`backend/config/settings.py`:

```python
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Bogota"
CELERY_RESULT_EXPIRES = 3600             # 1 h: evita que Redis acumule resultados
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60         # corte duro
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60    # aviso para cerrar ordenadamente
CELERY_TASK_ACKS_LATE = True             # si el worker muere, la tarea vuelve a la cola
CELERY_WORKER_PREFETCH_MULTIPLIER = 1    # reparto justo de tareas largas
```

---

## 4. Cómo escribir una tarea

Reglas:

1. Una tarea DEBE ser **idempotente**: ejecutarla dos veces deja el mismo resultado. Con `acks_late` y los reintentos, una tarea puede correr más de una vez.
2. Los argumentos DEBEN ser IDs y valores simples, no objetos del ORM. El objeto pudo cambiar entre que se encoló la tarea y que se ejecuta.
3. Reintente solo los errores transitorios (red, tiempo de espera), con espera exponencial. Un error de datos no se arregla reintentando.

```python
import logging

import httpx
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(httpx.TransportError, httpx.TimeoutException),
    retry_backoff=True,          # 1 s, 2 s, 4 s, ...
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
)
def sincronizar_cliente(self, cliente_id: int) -> dict:
    logger.info("Sincronizando cliente %s (intento %s)", cliente_id, self.request.retries + 1)
    # 1. Leer el estado actual por ID.  2. Calcular.  3. Escribir con update_or_create (idempotente).
    return {"cliente_id": cliente_id, "ok": True}


@shared_task
def verificar_alertas_sistema() -> dict:
    return {"checked": True}
```

---

## 5. Orquestación

Los servicios `celery-worker` y `celery-beat` ya están en [`docker-compose.yml`](./docker-compose.yml). Reglas:

- Debe haber **un solo** `celery-beat` por ambiente. Con dos, cada tarea periódica se ejecuta dos veces.
- Worker y beat usan la misma imagen que el backend, pero sin el `entrypoint` de migraciones.
- En producción, supervise la cola: por ejemplo con `celery -A config inspect active` o con Flower, protegido con autenticación.
