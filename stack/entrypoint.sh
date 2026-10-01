#!/bin/sh
set -e

echo "======================================================================"
echo "  INICIANDO CONTENEDOR BACKEND — JOLIFOODS (FASTAPI + DJANGO ASGI)"
echo "======================================================================"

# 1. Esperar a que PostgreSQL esté completamente disponible
echo "-> [1/4] Verificando conectividad con PostgreSQL..."
until pg_isready -h "${POSTGRES_HOST:-db}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-postgres}"; do
  echo "   Base de datos aún no disponible. Reintentando en 2 segundos..."
  sleep 2
done
echo "   PostgreSQL listo y respondiendo."

# 2. Ejecutar migraciones automáticas de Django ORM
echo "-> [2/4] Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput

# 3. Cargar datos semilla iniciales (Roles y Superusuario de desarrollo)
echo "-> [3/4] Verificando datos semilla iniciales (seed_data.py)..."
if [ -f "seed_data.py" ]; then
  python seed_data.py || echo "   Aviso: seed_data ya ejecutado o no requerido."
fi

# 4. Recolectar archivos estáticos para producción
echo "-> [4/4] Recolectando archivos estáticos..."
python manage.py collectstatic --noinput || true

echo "======================================================================"
echo "  BACKEND LISTO — EJECUTANDO SERVIDOR UVICORN ASGI"
echo "======================================================================"

# Ejecutar el comando pasado como parámetro al contenedor (o Uvicorn por defecto)
exec "$@"
