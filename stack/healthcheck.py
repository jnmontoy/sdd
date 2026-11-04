"""
Sondas de salud (liveness / readiness) — plantilla SDD.

Rutas canónicas (públicas, sin autenticación, servidas por FastAPI):
  GET /health/live   -> el proceso responde. No consulta dependencias (lo usa Docker/orquestador
                        para decidir si reinicia el contenedor).
  GET /health/ready  -> PostgreSQL y Redis responden. 503 si alguno falla (el balanceador deja de
                        enviar tráfico, pero no reinicia).

Montaje: `app.include_router(router)` en la app FastAPI del proyecto; `config/asgi.py` enruta
`/health/*` hacia FastAPI.

Notas de diseño:
  - El ORM de Django es síncrono: dentro de `async def` se llama con `sync_to_async`; si no,
    Django lanza `SynchronousOnlyOperation`.
  - La respuesta pública no expone el texto de las excepciones (puede revelar hosts, usuarios o
    versiones). El detalle va al log.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict

import redis.asyncio as aioredis
from asgiref.sync import sync_to_async
from django.db import connection
from fastapi import APIRouter, Response, status

logger = logging.getLogger("health")
router = APIRouter(prefix="/health", tags=["Salud"])

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/1")
REDIS_TIMEOUT_S = float(os.getenv("HEALTH_REDIS_TIMEOUT_S", "1.5"))


def _ping_database() -> None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        row = cursor.fetchone()
    if not row or row[0] != 1:
        raise RuntimeError("SELECT 1 no devolvió 1")


async def _ping_redis() -> None:
    client = aioredis.from_url(REDIS_URL, socket_timeout=REDIS_TIMEOUT_S,
                               socket_connect_timeout=REDIS_TIMEOUT_S)
    try:
        if not await client.ping():
            raise RuntimeError("PING devolvió False")
    finally:
        await client.aclose()


async def _timed(name: str, check) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        await check()
        return {"status": "up", "latency_ms": round((time.perf_counter() - start) * 1000, 2)}
    except Exception:
        logger.exception("Sonda de salud: %s no disponible", name)
        return {"status": "down"}


@router.get("/live", summary="Sonda de vida (liveness)")
async def liveness() -> Dict[str, str]:
    return {"status": "alive"}


@router.get("/ready", summary="Sonda de disponibilidad (readiness)")
async def readiness(response: Response) -> Dict[str, Any]:
    start = time.perf_counter()
    services = {
        "database": await _timed("database", sync_to_async(_ping_database, thread_sensitive=True)),
        "redis": await _timed("redis", _ping_redis),
    }
    healthy = all(s["status"] == "up" for s in services.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if healthy else "degraded",
        "services": services,
        "latency_ms": round((time.perf_counter() - start) * 1000, 2),
    }
