# Protocolo 07: observabilidad, telemetría y monitoreo en producción

Lineamientos para saber, en producción, **si el sistema funciona, qué tan rápido responde y por qué falla**. Se basa en los tres pilares de la observabilidad (trazas, métricas y registros) y en las prácticas de SRE (*Site Reliability Engineering*, ingeniería de confiabilidad de Google).

Las palabras **DEBE / DEBERÍA / PUEDE** siguen la RFC 2119.

> **Estado de implementación en el SDD**: `stack/healthcheck.py` y `stack/validate_endpoints.py` cubren las sondas de salud. El SDD **no incluye** todavía middleware de identificador de correlación, configuración de OpenTelemetry, exportador de métricas ni configuración de Sentry; cada proyecto los configura siguiendo este protocolo.

---

## 1. Los tres pilares

| Pilar | Responde a | Herramientas de referencia |
|---|---|---|
| **Registros (logs)** | ¿Qué pasó exactamente? | Logs estructurados en JSON (`python-json-logger` o `structlog`). |
| **Métricas** | ¿Cuánto y qué tan rápido? | Prometheus (`django-prometheus`, `prometheus-fastapi-instrumentator`) + Grafana. |
| **Trazas** | ¿Por dónde pasó la petición y dónde tardó? | OpenTelemetry (instrumentaciones para Django, FastAPI, Celery, psycopg, Redis). |

---

## 2. Identificador de correlación y trazas distribuidas

Toda petición HTTP y toda tarea asíncrona DEBERÍA poder seguirse de punta a punta con un identificador común. **Por qué:** sin él, relacionar el error que vio un usuario con la línea de log del backend y con la tarea de Celery que falló es adivinar.

1. **Estándar recomendado**: [W3C Trace Context](https://www.w3.org/TR/trace-context/) (cabecera `traceparent`), que OpenTelemetry propaga automáticamente entre servicios y hacia Celery.
2. **Identificador legible** (convención complementaria): cabecera `X-Correlation-ID`.
   * El *proxy* inverso (Nginx) la genera si no viene (`$request_id`) y la reenvía.
   * Un middleware del backend la toma (o genera un UUID4), la guarda en un `contextvars.ContextVar` y la agrega a cada línea de log.
   * La respuesta HTTP la devuelve al cliente en la misma cabecera, para que el usuario o soporte pueda citarla.
   * Al encolar una tarea de Celery se envía en los `headers` de la tarea y el *worker* la restaura antes de ejecutar.
3. El frontend PUEDE enviar su propio `X-Correlation-ID`; el backend DEBE validar que sea un UUID antes de usarlo (evita inyección en logs).

---

## 3. Sondas de salud

Rutas canónicas del SDD (servidas por FastAPI, públicas y sin datos sensibles en la respuesta):

| Ruta | Propósito | Qué verifica | Respuesta |
|---|---|---|---|
| `GET /health/live` | **Vida** (*liveness*): el proceso responde. | Nada externo (no toca BD). | `200 {"status": "alive"}` |
| `GET /health/ready` | **Disponibilidad** (*readiness*): puede atender tráfico. | `SELECT 1` en PostgreSQL y `PING` a Redis (que también es el broker de Celery). | `200` si todo responde; `503` con el subsistema caído si no. |
| `GET /fast/v1/health` | Salud propia de la capa FastAPI. | Que el router de FastAPI esté montado. | `200` |

Ejemplo de `/health/ready`:

```json
{
  "status": "ready",
  "timestamp": "2026-10-06T15:15:00Z",
  "dependencies": { "database": "ok", "redis": "ok" }
}
```

**Por qué separar vida y disponibilidad:** si la sonda de vida consultara la base de datos, una caída de PostgreSQL haría que el orquestador reiniciara todos los contenedores en bucle sin arreglar nada. La frecuencia de consulta (p. ej. cada 10 s) se configura en el orquestador (`healthcheck` de Docker Compose, `livenessProbe`/`readinessProbe` de Kubernetes), no en la aplicación.

Verificaciones adicionales (espacio en disco, servicios externos) PUEDEN agregarse a `/health/ready` solo si su falla impide atender peticiones; si no, van como métricas con alerta.

---

## 4. Objetivos de nivel de servicio (SLO)

Se monitorean las **cuatro señales doradas** de SRE: latencia, tráfico, errores y saturación.

Los valores siguientes son **objetivos iniciales de referencia**, no mediciones. Cada proyecto DEBERÍA medir 2 a 4 semanas en producción y ajustarlos (registrando el cambio en un ADR).

| Señal | Indicador (SLI) | Objetivo inicial (SLO) | Alerta sugerida |
|---|---|---|---|
| Latencia — lecturas `/fast/v1/` | p95 del tiempo de respuesta | < 300 ms | p95 > 600 ms durante 5 min |
| Latencia — API Django `/api/v1/` | p95 del tiempo de respuesta | < 500 ms | p95 > 1 s durante 5 min |
| Tráfico | Peticiones por minuto por endpoint | Línea base del proyecto | Caída o pico > 3× la línea base |
| Errores | % de respuestas 5xx sobre el total | < 0,5 % mensual (disponibilidad ≥ 99,5 %) | 5xx > 2 % durante 5 min |
| Saturación — base de datos | Conexiones activas / máximas | < 75 % | > 85 % sostenido 10 min |
| Saturación — Celery | Tareas pendientes en la cola | Línea base del proyecto | Crecimiento sostenido 15 min |

**Por qué el percentil 95 y no el promedio:** el promedio oculta a los usuarios que esperan mucho; el p95 dice cuánto espera el 5 % más lento.

---

## 5. Captura centralizada de errores (Sentry u equivalente)

* Integrar el SDK en backend y frontend con `send_default_pii=False`.
* Los datos sensibles DEBEN eliminarse antes de enviar el evento (`before_send`): contraseñas, tokens, cookies, cabecera `Authorization`, números de documento, datos biométricos. **Por qué:** el servicio de errores es un tercero; enviarle datos personales es una transferencia que exige base legal (Ley 1581 de 2012).
* Agrupar por huella (*fingerprint*) de excepción y ubicación para no generar una alerta por cada repetición.
* Registrar la versión desplegada (`release`) para saber qué despliegue introdujo el error.

---

## 6. Registros

* Formato JSON con, como mínimo: `timestamp` (UTC), `level`, `logger`, `message`, `correlation_id`, `user_id` (identificador interno, no nombre ni documento).
* Los registros NO DEBEN contener contraseñas, tokens ni datos personales completos.
* La bitácora de auditoría de negocio (quién hizo qué) es distinta de los logs técnicos y se rige por su propio modelo (`model/auditoria/`).
