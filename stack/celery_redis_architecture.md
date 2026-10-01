# Arquitectura Backend: Tareas Asíncronas y Procesamiento Continuo con Celery & Redis
## Ecosistema Jolifoods — Metodología Spec-Driven Development (SDD)

Este documento define la arquitectura canónica para la ejecución de **llamados constantes, tareas pesadas en segundo plano y jobs periódicos** en el backend utilizando **Redis** como intermediario de mensajes (*message broker*) y **Celery** como ejecutor distribuido de tareas (*task worker*).

---

### 1. Justificación Arquitectónica

En aplicaciones operativas (como `app_tic`, `contenedores`, `tiendita`, `vibra`), existen tareas que no deben bloquear el hilo principal de peticiones HTTP (ASGI/WSGI):
- Envío masivo de notificaciones o correos de recuperación de clave.
- Generación y rasterización pesada de reportes PDF y hojas de cálculo Excel.
- Sincronizaciones constantes de bases de datos, verificación de backups y sondas periódicas.
- Procesamiento y descompresión de archivos de video o imágenes.

El uso de **Redis + Celery** desacopla estas operaciones: el endpoint responde en milisegundos (`HTTP 202 Accepted` con `task_id`), mientras Celery procesa la tarea en segundo plano y el frontend monitorea el avance mediante **Polling reactivo**.

---

### 2. Configuración Canónica en Django (`config/celery.py`)

```python
# backend/config/celery.py
import os
from celery import Celery
from celery.schedules import crontab

# Establecer settings de Django por defecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('jolifoods_app')

# Leer configuración prefijada con CELERY_ en settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descubrir tareas en todas las apps instaladas (tasks.py)
app.autodiscover_tasks()

# Configuración de Tareas Periódicas (Celery Beat)
app.conf.beat_schedule = {
    'verificar-alertas-cada-5-minutos': {
        'task': 'apps.auth_core.tasks.verificar_alertas_sistema',
        'schedule': 300.0, # cada 5 minutos
    },
    'limpiar-sesiones-expiradas-medianoche': {
        'task': 'apps.auth_core.tasks.limpiar_sesiones_inactivas',
        'schedule': crontab(hour=0, minute=0),
    },
}
```

---

### 3. Variables de Configuración en `config/settings.py`

```python
# backend/config/settings.py
import os

# --- CELERY & REDIS CONFIGURATION ---
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Bogota'
CELERY_ENABLE_UTC = True

# Evitar acumulación de resultados en memoria Redis
CELERY_RESULT_EXPIRES = 3600  # 1 hora
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutos máx
```

---

### 4. Definición Canónica de Tareas Asíncronas (`apps/*/tasks.py`)

```python
# backend/apps/auth_core/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def procesar_llamado_constante(self, parametro_id: int):
    """
    Tarea en segundo plano reintentable para llamados pesados o continuos.
    """
    try:
        logger.info(f"[Celery] Iniciando procesamiento para ID {parametro_id}...")
        # Lógica de sincronización o procesamiento pesado
        resultado = {"status": "SUCCESS", "id": parametro_id, "processed": True}
        return resultado
    except Exception as exc:
        logger.error(f"[Celery] Error en tarea {parametro_id}: {exc}")
        raise self.retry(exc=exc)

@shared_task
def verificar_alertas_sistema():
    """Ejecutada automáticamente por Celery Beat para telemetría constante."""
    logger.info("[Celery Beat] Evaluando estado de alarmas e indicadores en tiempo real...")
    # Lógica periódica
    return {"checked": True}
```

---

### 5. Orquestación Multi-Contenedor en `docker-compose.yml`

```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: jolifoods_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    environment:
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      redis:
        condition: service_healthy

  celery-worker:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: jolifoods_celery_worker
    restart: unless-stopped
    command: celery -A config worker --loglevel=info --pool=prefork --concurrency=4
    environment:
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - redis
      - backend

  celery-beat:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: jolifoods_celery_beat
    restart: unless-stopped
    command: celery -A config beat --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis
      - backend

volumes:
  redis_data:
```
