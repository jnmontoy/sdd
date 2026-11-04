#!/bin/sh
# Arranque del contenedor backend (plantilla SDD).
# Variables:
#   RUN_MIGRATIONS=true|false  (por defecto true)  Aplica migraciones al arrancar.
#   SEED_ON_START=true|false   (por defecto false) Crea el administrador inicial. Solo desarrollo/pruebas.
#   COLLECTSTATIC=true|false   (por defecto true)
set -e

echo "-> [1/4] Esperando PostgreSQL en ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}..."
attempts=0
until pg_isready -h "${POSTGRES_HOST:-db}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-postgres}" >/dev/null 2>&1; do
  attempts=$((attempts + 1))
  if [ "$attempts" -ge 30 ]; then
    echo "   PostgreSQL no respondió en 60 s. Abortando." >&2
    exit 1
  fi
  sleep 2
done

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "-> [2/4] Aplicando migraciones..."
  python manage.py migrate --noinput
fi

if [ "${SEED_ON_START:-false}" = "true" ] && [ -f "seed_data.py" ]; then
  echo "-> [3/4] Datos semilla..."
  python seed_data.py
fi

if [ "${COLLECTSTATIC:-true}" = "true" ]; then
  echo "-> [4/4] Archivos estáticos..."
  python manage.py collectstatic --noinput
fi

exec "$@"
