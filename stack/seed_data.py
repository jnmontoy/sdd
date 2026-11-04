"""
Datos semilla idempotentes (plantilla SDD) — se copia como `backend/seed_data.py`.

Crea el usuario administrador inicial. Reglas:
  - La contraseña NUNCA tiene valor por defecto en el código. Se toma de ADMIN_DEFAULT_PASSWORD;
    si no existe y DEBUG=True se genera una aleatoria y se muestra UNA vez en consola.
    Con DEBUG=False y sin variable, el script se niega a crear el usuario.
  - Se ejecuta solo si SEED_ON_START=true (ver entrypoint.sh); en producción la creación del
    primer administrador es un paso manual y auditado.
  - Los roles se asignan con la tabla propia de roles (BP-19), si el proyecto la tiene.
"""
import os
import secrets
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.auth import get_user_model  # noqa: E402
from django.db import transaction  # noqa: E402


def seed_database() -> int:
    User = get_user_model()
    login_field = User.USERNAME_FIELD
    admin_login = os.getenv("ADMIN_DEFAULT_LOGIN", "1000000001")
    admin_email = os.getenv("ADMIN_DEFAULT_EMAIL", "admin@ejemplo.local")
    admin_pass = os.getenv("ADMIN_DEFAULT_PASSWORD")
    generated = False

    if not admin_pass:
        if not settings.DEBUG:
            print("[ERROR] Defina ADMIN_DEFAULT_PASSWORD; no se crean administradores con clave por defecto.")
            return 1
        admin_pass, generated = secrets.token_urlsafe(16), True

    with transaction.atomic():
        user, created = User.objects.get_or_create(
            **{login_field: admin_login},
            defaults={"email": admin_email, "is_staff": True, "is_superuser": True, "is_active": True},
        )
        if created:
            user.set_password(admin_pass)
            user.save(update_fields=["password"])
            try:  # BP-19: rol en tabla propia, si el modelo existe en el proyecto.
                from apps.auth_core.models import Rol
                rol, _ = Rol.objects.get_or_create(codigo="ADMIN", defaults={"nombre": "Administrador"})
                user.roles.add(rol)
            except (ImportError, AttributeError):
                pass

    if created:
        print(f"[OK] Administrador creado ({login_field}={admin_login}).")
        if generated:
            print(f"     Contraseña temporal generada (solo se muestra ahora): {admin_pass}")
    else:
        print(f"[INFO] El administrador ({login_field}={admin_login}) ya existe; no se modificó.")
    return 0


if __name__ == "__main__":
    sys.exit(seed_database())
