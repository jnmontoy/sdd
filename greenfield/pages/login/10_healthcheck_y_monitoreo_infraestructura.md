# 10. Sondas de Salud y Monitoreo de Infraestructura
## Módulo de Login / Autenticación — SDD Joli Foods (`SPEC-AUTH-001`)

Estándar de las sondas de vida (*liveness*) y disponibilidad (*readiness*) del backend híbrido Django + FastAPI. El login depende de PostgreSQL (usuarios, sesiones) y de Redis (límite de intentos); si alguno falla, el login no debe recibir tráfico.

---

## 1. Por qué

1. **No enviar tráfico a contenedores no listos:** mientras PostgreSQL arranca, el login fallaría.
2. **Fallar cerrado sin Redis:** sin Redis no hay límite de intentos; la sonda de disponibilidad DEBE marcar 503 para que el orquestador o el balanceador dejen de enrutar.
3. **Medir latencia** de base de datos y caché en cada verificación.

---

## 2. Rutas canónicas

Ambas son públicas, las sirve FastAPI y NO DEBEN exponer versiones de software, cadenas de conexión ni mensajes de error internos.

| Ruta | Tipo | Verifica | Respuesta |
| :--- | :--- | :--- | :--- |
| `GET /health/live` | Vida | Que el proceso responde (no toca BD ni Redis). | 200 `{ "status": "alive" }` |
| `GET /health/ready` | Disponibilidad | `SELECT 1` en PostgreSQL y `PING` en Redis, con tiempo límite de 2 s cada uno. | 200 si ambos responden; **503** si alguno falla. |
| `GET /fast/v1/health` | Salud de la capa FastAPI | Estado propio de la sub-aplicación FastAPI. | 200 |

### 2.1. `GET /health/ready` — 200
```json
{
  "status": "ready",
  "timestamp": "2026-11-04T13:00:00Z",
  "checks": {
    "database": { "status": "up", "latency_ms": 1.45 },
    "redis":    { "status": "up", "latency_ms": 0.82 }
  }
}
```

### 2.2. `GET /health/ready` — 503
```json
{
  "status": "degraded",
  "timestamp": "2026-11-04T13:00:00Z",
  "checks": {
    "database": { "status": "down" },
    "redis":    { "status": "up", "latency_ms": 0.91 }
  }
}
```
El detalle del error (excepción) se escribe en el log del servidor, no en la respuesta.

---

## 3. `docker-compose.yml`

```yaml
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://localhost:8000/health/ready || exit 1"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 20s
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
```

`/health/live` se usa para reinicios (el proceso está colgado); `/health/ready` para decidir si recibe tráfico. En Docker Compose, que solo tiene un `healthcheck`, se usa `/health/ready`. La imagen DEBE incluir `curl` (o usar un script Python equivalente).

---

## 4. Implementación de referencia

[`.sdd/stack/healthcheck.py`](../../../stack/healthcheck.py). Las llamadas al ORM de Django desde la vista `async` de FastAPI DEBEN envolverse en `sync_to_async` (o usar `connection` en un hilo) para no bloquear el bucle de eventos.
