# Implementación Canónica: Django ORM (`models.py`)
## Módulo de Login e Identidad — SDD Jolifoods

Este archivo proporciona el código fuente en Python y Django ORM para instanciar directamente los modelos de datos en el backend, cumpliendo con la especificación SDD.

---

## Código Fuente: `backend/apps/auth_core/models.py`

```python
import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator


class UsuarioManager(BaseUserManager):
    """Manager personalizado para la entidad Usuario usando numero_documento como identificador."""

    def create_user(self, numero_documento, email, password=None, **extra_fields):
        if not numero_documento:
            raise ValueError('El número de documento es obligatorio.')
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')

        email = self.normalize_email(email).lower()
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('tipo', 'Colaborador')
        extra_fields.setdefault('empresa', 'Jolifoods')

        user = self.model(numero_documento=numero_documento, email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, numero_documento, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('tipo', 'Administrador')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(numero_documento, email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo principal de usuario e identidad para Jolifoods."""

    TIPO_CHOICES = [
        ('Administrador', 'Administrador'),
        ('Colaborador', 'Colaborador'),
        ('Operario', 'Operario'),
        ('Auditor', 'Auditor'),
    ]

    doc_validator = RegexValidator(
        regex=r'^[0-9]{5,15}$',
        message='El número de documento debe contener exclusivamente entre 5 y 15 dígitos numéricos.'
    )

    numero_documento = models.CharField(
        max_length=15,
        unique=True,
        validators=[doc_validator],
        db_index=True,
        verbose_name='Número de Documento'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        db_index=True,
        verbose_name='Correo Electrónico'
    )
    first_name = models.CharField(max_length=150, verbose_name='Nombres')
    last_name = models.CharField(max_length=150, verbose_name='Apellidos')
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='Colaborador',
        verbose_name='Tipo de Usuario'
    )
    is_active = models.BooleanField(default=True, verbose_name='Cuenta Activa')
    is_staff = models.BooleanField(default=False, verbose_name='Acceso al Panel')
    
    # Control de Fuerza Bruta y Seguridad
    intentos_fallidos = models.PositiveIntegerField(default=0, verbose_name='Intentos Fallidos')
    bloqueado_hasta = models.DateTimeField(null=True, blank=True, verbose_name='Bloqueado Hasta')
    
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Registro')
    avatar_url = models.CharField(max_length=500, null=True, blank=True, verbose_name='URL Avatar')
    cargo = models.CharField(max_length=120, null=True, blank=True, verbose_name='Cargo')
    empresa = models.CharField(max_length=120, default='Jolifoods', verbose_name='Empresa')

    objects = UsuarioManager()

    USERNAME_FIELD = 'numero_documento'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        indexes = [
            models.Index(fields=['is_active', 'tipo'], name='idx_user_active_tipo'),
            models.Index(fields=['bloqueado_hasta'], name='idx_user_lockout'),
        ]

    def __str__(self):
        return f"{self.numero_documento} - {self.first_name} {self.last_name} ({self.tipo})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def is_locked(self) -> bool:
        """Determina si el usuario se encuentra temporalmente bloqueado por intentos fallidos."""
        if self.bloqueado_hasta and timezone.now() < self.bloqueado_hasta:
            return True
        return False

    def register_failed_attempt(self, max_attempts=5, lock_duration_minutes=15):
        """Registra un fallo de contraseña y activa el enfriamiento si se supera el umbral."""
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= max_attempts:
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=lock_duration_minutes)
        self.save(update_fields=['intentos_fallidos', 'bloqueado_hasta'])

    def reset_failed_attempts(self):
        """Reinicia el contador al autenticarse exitosamente."""
        if self.intentos_fallidos > 0 or self.bloqueado_hasta is not None:
            self.intentos_fallidos = 0
            self.bloqueado_hasta = None
            self.save(update_fields=['intentos_fallidos', 'bloqueado_hasta'])


class SesionUsuario(models.Model):
    """Modelo para trazabilidad de sesiones activas y tokens JWT."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sesiones')
    jti = models.CharField(max_length=64, unique=True, db_index=True, verbose_name='JWT JTI Claim')
    ip_origen = models.GenericIPAddressField(verbose_name='IP de Conexión')
    user_agent = models.TextField(verbose_name='User Agent')
    dispositivo = models.CharField(max_length=50, null=True, blank=True)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField()
    is_activa = models.BooleanField(default=True, db_index=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'sesiones_usuario'
        indexes = [
            models.Index(fields=['usuario', 'is_activa'], name='idx_session_user_active'),
        ]

    def __str__(self):
        return f"Sesión {self.usuario.numero_documento} - {self.ip_origen}"


class RegistroAuditoriaAcceso(models.Model):
    """Bitácora inmutable de eventos de seguridad de autenticación."""
    documento_ingresado = models.CharField(max_length=50, db_index=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    evento = models.CharField(max_length=35)
    resultado = models.CharField(max_length=15)  # SUCCESS, FAILURE, BLOCKED
    motivo_fallo = models.CharField(max_length=150, null=True, blank=True)
    ip_origen = models.GenericIPAddressField(db_index=True)
    user_agent = models.TextField()
    fecha_evento = models.DateTimeField(default=timezone.now, db_index=True)
    tiempo_respuesta_ms = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'registro_auditoria_acceso'
        ordering = ['-fecha_evento']

    def __str__(self):
        return f"[{self.fecha_evento}] {self.evento} - {self.documento_ingresado} ({self.resultado})"


class TokenRestablecimientoClave(models.Model):
    """Modelo para tokens efímeros de recuperación de contraseña de un solo uso."""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tokens_restablecimiento')
    token_hash = models.CharField(max_length=64, unique=True, db_index=True, verbose_name='SHA-256 Hash del Token')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField(db_index=True)
    is_used = models.BooleanField(default=False, db_index=True, verbose_name='Token Utilizado')
    ip_solicitud = models.GenericIPAddressField(verbose_name='IP de Solicitud')
    ip_cambio = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP de Confirmación')
    user_agent_solicitud = models.TextField(verbose_name='User Agent Solicitud')

    class Meta:
        db_table = 'tokens_restablecimiento_clave'
        indexes = [
            models.Index(fields=['usuario', 'is_used', 'fecha_expiracion'], name='idx_pwd_token_valid'),
        ]

    def __str__(self):
        return f"Reset Token para {self.usuario.numero_documento} (Usado: {self.is_used})"

    def is_valid(self) -> bool:
        """Comprueba si el token no ha sido consumido y está dentro de los 15 minutos de vigencia."""
        return not self.is_used and timezone.now() <= self.fecha_expiracion
```
