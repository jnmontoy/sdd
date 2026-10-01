# 10. Monitoreo de Infraestructura y Sondas de Salud (Healthcheck)
## Módulo de Login / Autenticación — SDD Greenyard (`GY-SPEC-AUTH-001`)

Esta especificación describe el estándar corporativo para las **sondas de disponibilidad, salud y rendimiento (Liveness y Readiness)** en el backend híbrido FastAPI + Django de **Jolifoods**.

---

## 1. Justificación de Ingeniería

En arquitecturas desacopladas con contenedores Docker y orquestadores (Docker Compose, Swarm, Kubernetes o Nginx):
1. **Evitar tráfico a contenedores no listos**: No se debe enviar peticiones de login al backend si PostgreSQL aún está iniciando sus sockets.
2. **Detección temprana de caídas**: Si Redis se satura o se cae, el sistema de Rate Limiting fallaría o bloquearía peticiones legítimas. La sonda debe marcar el estado en `degraded` con HTTP 503.
3. **Métricas de latencia**: Medir en milisegundos el tiempo de respuesta de la base de datos y la caché en cada ciclo de vida.

---

## 2. Contrato de Endpoints de Salud

### 2.1. Sonda de Vida Rápida (`Liveness Probe`)
- **Ruta**: `GET /api/v1/health/live`
- **Frecuencia**: Cada 5 a 10 segundos.
- **Propósito**: Verificar si el proceso Python/Uvicorn está respondiendo en el bucle de eventos.
- **Respuesta Exitosa (HTTP 200)**:
  ```json
  {
    "status": "alive"
  }
  ```

---

### 2.2. Sonda de Disponibilidad y Dependencias (`Readiness Probe`)
- **Ruta**: `GET /api/v1/health/`
- **Frecuencia**: Cada 15 a 30 segundos.
- **Propósito**: Validar conectividad activa con PostgreSQL y Redis antes de declarar el contenedor saludable.

#### Respuesta Exitosa (HTTP 200 OK):
```json
{
  "status": "healthy",
  "timestamp": 1790874600.12,
  "services": {
    "database": {
      "status": "up",
      "latency_ms": 1.45,
      "engine": "PostgreSQL"
    },
    "redis": {
      "status": "up",
      "latency_ms": 0.82
    }
  },
  "latency_ms": 2.38
}
```

#### Respuesta de Degradación / Fallo Crítico (HTTP 503 Service Unavailable):
```json
{
  "status": "degraded",
  "timestamp": 1790874600.12,
  "services": {
    "database": {
      "status": "down",
      "error": "could not connect to server: Connection refused",
      "engine": "PostgreSQL"
    },
    "redis": {
      "status": "up",
      "latency_ms": 0.91
    }
  },
  "latency_ms": 1002.5
}
```

---

## 3. Integración en `docker-compose.yml`

Para que el backend informe su estado de salud nativamente a Docker, se define la siguiente directiva en el servicio `backend`:

```yaml
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: jolifoods_backend
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/api/v1/health/live || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
```

---

## 4. Archivo de Implementación Canónica

El código Python completo listo para producción se encuentra disponible en:
- [`.sdd/stack/healthcheck.py`](../../../stack/healthcheck.py)
