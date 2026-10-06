# Protocolo de Observabilidad, Telemetría y APM en Producción
## Ecosistema Corporativo Jolifoods / Greenyard — Metodología SDD

Este protocolo establece los lineamientos de monitorización proactiva, trazabilidad distribuida, métricas de rendimiento y verificación del estado de salud de todos los microservicios y aplicaciones del ecosistema.

---

## 1. Los Tres Pilares de la Observabilidad en SDD

```text
                  ┌──────────────────────────────────────────────┐
                  │             OBSERVABILIDAD TOTAL             │
                  └───────┬──────────────┬──────────────┬────────┘
                          │              │              │
                          ▼              ▼              ▼
                    ┌───────────┐  ┌───────────┐  ┌───────────┐
                    │  Trazas   │  │  Métricas │  │   Logs    │
                    │  (APM)    │  │  (Prom)   │  │ (Audit)   │
                    └───────────┘  └───────────┘  └───────────┘
```

---

## 2. Trazabilidad Distribuida (Correlation ID & OpenTelemetry)

Toda petición HTTP entrante o tarea asíncrona debe portar un identificador unívoco de correlación (`X-Correlation-ID`).

### 2.1. Ciclo de Vida del Correlation ID
1. **Frontend**: Genera un UUIDv4 o propaga el existente en el encabezado `X-Correlation-ID` en cada llamada Axios.
2. **Reverse Proxy / Nginx**: Si la cabecera no existe, la genera y la inyecta al backend.
3. **Backend ASGI (Django/FastAPI)**:
   - Middleware intercepta el ID y lo asigna al contexto de ejecución (`contextvars`).
   - Todos los logs generados durante la petición imprimen automáticamente el `correlation_id`.
   - Si la petición delega trabajo a **Celery**, el `correlation_id` viaja dentro de los `headers` de la tarea de Redis.
4. **Respuesta HTTP**: El backend retorna siempre la cabecera `X-Correlation-ID: <uuid>` al cliente.

---

## 3. Contratos de Salud: Healthchecks Profundos (*Deep vs Shallow*)

Para evitar caídas silenciosas en entornos orquestados por Docker Compose o Kubernetes, todo servicio expone dos endpoints de diagnóstico:

### 3.1. Endpoint de Liveness (`/health/live`)
- **Propósito**: Verifica que el servidor web ASGI esté vivo y aceptando conexiones.
- **Respuesta**: HTTP 200 `{ "status": "alive" }`.
- **Frecuencia**: Cada 10 segundos.

### 3.2. Endpoint de Readiness (`/health/ready`)
- **Propósito**: Verifica la conectividad real con dependencias críticas.
- **Verificaciones obligatorias**:
  1. Consulta trivial a PostgreSQL (`SELECT 1;`).
  2. Ping a Redis (`PING` -> `PONG`).
  3. Estado del socket de Celery Broker.
  4. Espacio disponible en disco (mínimo > 10% libre).
- **Respuesta esperada**:
  ```json
  {
    "status": "ready",
    "timestamp": "2026-10-06T10:15:00Z",
    "dependencies": {
      "database": "connected",
      "redis": "connected",
      "celery_broker": "connected",
      "disk_storage": "healthy"
    }
  }
  ```
- **Código de error**: Si alguna dependencia falla, retornar HTTP 503 con detalle del subsistema caído.

---

## 4. Objetivos de Nivel de Servicio (SLOs) y Métricas de Rendimiento

El sistema se monitorea bajo el estándar de **Las 4 Señales Doradas de Google SRE**:

| Métrica | Descripción | Umbral Objetivo (SLO) | Alerta Disparada |
| :--- | :--- | :--- | :--- |
| **Latencia /fast/** | Endpoints asíncronos Pydantic en FastAPI | **p95 < 45 ms** | p95 > 100 ms durante 3 min |
| **Latencia CRUD** | Vistas y transacciones Django ORM | **p95 < 200 ms** | p95 > 500 ms durante 3 min |
| **Tasa de Errores** | Respuestas HTTP 5xx sobre total de peticiones | **< 0.05%** | Errores 5xx > 0.5% en 5 min |
| **Saturación DB** | Porcentaje de conexiones activas en el pool | **< 75%** | Uso del pool > 85% sostenido |
| **Cola de Celery** | Mensajes acumulados sin procesar en Redis | **< 50 tareas** | Cola > 200 tareas acumuladas |

---

## 5. Captura Centralizada de Errores (Sentry)

- Integrar el SDK de Sentry tanto en backend como frontend.
- **Sanitización Obligatoria de Datos Sensibles (Data Scrubbing)**:
  - Censurar contraseñas, tokens JWT, números de tarjetas de crédito y hashes biométricos antes de que el evento salga del servidor.
- Agrupación por huella (*Fingerprinting*): Agrupar excepciones por `exception_class` y línea de código para evitar tormentas de alertas duplicadas.
