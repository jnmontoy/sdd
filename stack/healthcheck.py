"""
Módulo Canónico de Monitoreo de Salud (Healthcheck) — Ecosistema Jolifoods
Provee sondas de Liveness y Readiness para FastAPI y Docker Compose.
"""
import time
from typing import Dict, Any
from fastapi import APIRouter, status, Response
from django.db import connection
import redis

router = APIRouter(prefix="/api/v1/health", tags=["Monitoreo e Infraestructura"])

# Configuración de Redis
REDIS_URL = "redis://redis:6379/1"

@router.get(
    "/",
    summary="Sonda de Salud Integral (Readiness Probe)",
    status_code=status.HTTP_200_OK,
    response_model=None
)
async def health_check(response: Response) -> Dict[str, Any]:
    """
    Verifica activamente en tiempo real:
    1. Conectividad y respuesta SQL con la Base de Datos PostgreSQL.
    2. Conectividad y latencia con el clúster de caché Redis.
    3. Estado del motor FastAPI/ASGI.
    
    Si algún servicio crítico falla, responde HTTP 503 Service Unavailable
    para que los balanceadores o Docker reinicien/desvíen tráfico.
    """
    t_start = time.perf_counter()
    report: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {},
        "latency_ms": 0.0
    }
    has_critical_failure = False

    # 1. Verificación de Base de Datos PostgreSQL (Django ORM Connection)
    db_start = time.perf_counter()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            if row and row[0] == 1:
                db_latency = round((time.perf_counter() - db_start) * 1000, 2)
                report["services"]["database"] = {
                    "status": "up",
                    "latency_ms": db_latency,
                    "engine": "PostgreSQL"
                }
            else:
                raise ValueError("Consulta de verificación no retornó el valor esperado.")
    except Exception as exc:
        has_critical_failure = True
        report["services"]["database"] = {
            "status": "down",
            "error": str(exc),
            "engine": "PostgreSQL"
        }

    # 2. Verificación de Caché Redis
    redis_start = time.perf_counter()
    try:
        r = redis.Redis.from_url(REDIS_URL, socket_timeout=1.5)
        if r.ping():
            redis_latency = round((time.perf_counter() - redis_start) * 1000, 2)
            report["services"]["redis"] = {
                "status": "up",
                "latency_ms": redis_latency
            }
        else:
            raise ConnectionError("Redis ping retornó False.")
    except Exception as exc:
        has_critical_failure = True
        report["services"]["redis"] = {
            "status": "down",
            "error": str(exc)
        }

    # 3. Latencia total del reporte
    report["latency_ms"] = round((time.perf_counter() - t_start) * 1000, 2)

    # 4. Evaluación del código HTTP de respuesta
    if has_critical_failure:
        report["status"] = "degraded"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return report


@router.get(
    "/live",
    summary="Sonda de Vida Rápida (Liveness Probe)",
    status_code=status.HTTP_200_OK
)
async def liveness() -> Dict[str, str]:
    """Sonda ultrarrápida (sin consultar BD) para validar que el proceso ASGI esté vivo."""
    return {"status": "alive"}
