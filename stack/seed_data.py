"""
Script Idempotente de Carga de Datos Semilla (Seed Data) — Ecosistema Jolifoods
Crea roles, sede principal y usuario administrador de desarrollo de forma segura.
"""
import os
import sys
import django

# Configurar el entorno Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
try:
    django.setup()
except Exception as exc:
    print(f"Error configurando Django en seed_data: {exc}")
    sys.exit(0)

from django.contrib.auth import get_user_model
from django.db import transaction

def seed_database():
    print("-> Inicializando datos semilla en la base de datos...")
    User = get_user_model()

    # Credenciales configurables por variables de entorno
    admin_doc = os.getenv("ADMIN_DEFAULT_DOC", "10203040")
    admin_user = os.getenv("ADMIN_DEFAULT_USERNAME", "admin.joli")
    admin_email = os.getenv("ADMIN_DEFAULT_EMAIL", "admin@jolifoods.com")
    admin_pass = os.getenv("ADMIN_DEFAULT_PASSWORD", "JoliAdmin2026*Secure")

    with transaction.atomic():
        # 1. Crear o recuperar el usuario administrador
        user, created = User.objects.get_or_create(
            numero_documento=admin_doc,
            defaults={
                "username": admin_user,
                "email": admin_email,
                "first_name": "Administrador",
                "last_name": "Jolifoods",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
                "rol": "ADMIN",
                "sede": "Sede Principal",
            }
        )

        if created:
            user.set_password(admin_pass)
            user.save()
            print(f"   [OK] Usuario administrador creado exitosamente:")
            print(f"        - Cédula / Documento : {admin_doc}")
            print(f"        - Usuario            : {admin_user}")
            print(f"        - Contraseña Temporal: {admin_pass}")
            print(f"        - Rol                : ADMIN")
        else:
            print(f"   [INFO] El usuario con cédula {admin_doc} ya existe en la base de datos.")

    print("-> Datos semilla verificados correctamente.")

if __name__ == "__main__":
    seed_database()
