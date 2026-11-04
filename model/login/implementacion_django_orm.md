# Implementación de Referencia: Django ORM (`models.py`)
## Módulo de Login e Identidad — SDD Joli Foods

Modelos Django equivalentes a [`esquema_sql_canonico.md`](./esquema_sql_canonico.md) (mismos nombres de tabla, tipos, nulabilidad, índices, unicidad y `on_delete`). Requiere Django ≥ 5.1 (`CheckConstraint(condition=...)`), `argon2-cffi` y `djangorestframework-simplejwt` con `token_blacklist`. `Rol` y `Sede` están en [`../roles/spec_model_roles_permisos.md`](../roles/spec_model_roles_permisos.md) (app `organizacion`).

`settings.py`: `AUTH_USER_MODEL = "auth_core.Usuario"` antes de la primera migración.

---

## Código: `backend/apps/auth_core/models.py`

```python
import hashlib
import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import PermissionDenied
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.utils import timezone

from apps.organizacion.models import Rol, Sede
from apps.archivos.validators import validar_imagen_avatar, ruta_avatar

DOCUMENTO_REGEX = r"^[0-9]{5,15}$"


class UsuarioManager(BaseUserManager):
    """Manager con numero_documento como identificador de inicio de sesión."""

    use_in_migrations = True

    def _create_user(self, numero_documento, email, password, **extra_fields):
        if not numero_documento:
            raise ValueError("El número de documento es obligatorio.")
        if not email:
            raise ValueError("El correo electrónico es obligatorio.")
        email = self.normalize_email(email).lower()
        user = self.model(numero_documento=numero_documento, email=email, **extra_fields)
        if password:
            user.set_password(password)  # hasher de Django (PASSWORD_HASHERS)
        else:
            user.set_unusable_password()  # cuentas solo-SSO
        user.full_clean(exclude=["password"])
        user.save(using=self._db)
        return user

    def create_user(self, numero_documento, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(numero_documento, email, password, **extra_fields)

    def create_superuser(self, numero_documento, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("debe_cambiar_clave", False)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")
        return self._create_user(numero_documento, email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Identidad del colaborador. Roles por M2M con Rol (BP-19); sin campo 'rol' de texto."""

    numero_documento = models.CharField(
        "número de documento",
        max_length=15,
        unique=True,
        validators=[RegexValidator(DOCUMENTO_REGEX, "Entre 5 y 15 dígitos, sin puntos ni espacios.")],
    )
    email = models.EmailField("correo electrónico", max_length=254, unique=True)
    first_name = models.CharField("nombres", max_length=150)
    last_name = models.CharField("apellidos", max_length=150)
    is_active = models.BooleanField("activo", default=True, db_index=True)
    is_staff = models.BooleanField("acceso a admin", default=False)
    debe_cambiar_clave = models.BooleanField("debe cambiar clave", default=True)

    intentos_fallidos = models.PositiveIntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True, db_index=True)

    date_joined = models.DateTimeField(default=timezone.now)
    sede = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True, blank=True, related_name="usuarios")
    roles = models.ManyToManyField(Rol, related_name="usuarios", blank=True)
    cargo = models.CharField(max_length=120, null=True, blank=True)
    empresa = models.CharField("unidad de negocio", max_length=120, null=True, blank=True)
    avatar = models.ImageField(
        upload_to=ruta_avatar, max_length=500, null=True, blank=True, validators=[validar_imagen_avatar]
    )

    objects = UsuarioManager()

    USERNAME_FIELD = "numero_documento"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    class Meta:
        db_table = "usuarios"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        constraints = [
            models.UniqueConstraint(Lower("email"), name="uq_usuario_email_ci"),
            models.CheckConstraint(condition=Q(numero_documento__regex=DOCUMENTO_REGEX), name="chk_usuario_documento"),
            models.CheckConstraint(condition=Q(intentos_fallidos__gte=0), name="chk_usuario_intentos"),
        ]

    def __str__(self) -> str:
        return f"{self.numero_documento} - {self.get_full_name()}"

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        return self.first_name

    # --- Roles y permisos (BP-19) ---
    @property
    def exige_sso(self) -> bool:
        return self.roles.filter(is_active=True, exige_sso=True).exists()

    def get_permisos(self) -> set[str]:
        """Unión de claves de permiso de los roles activos. Usar con prefetch_related('roles')."""
        permisos: set[str] = set()
        for rol in self.roles.all():
            if rol.is_active:
                permisos.update(rol.permisos)
        return permisos

    # --- Bloqueo prolongado (el límite de corto plazo vive en Redis) ---
    def is_locked(self) -> bool:
        return self.bloqueado_hasta is not None and timezone.now() < self.bloqueado_hasta

    def register_failed_attempt(self, max_attempts: int = 5, lock_minutes: int = 60) -> None:
        """Incremento atómico: dos intentos simultáneos no pierden conteos."""
        Usuario.objects.filter(pk=self.pk).update(intentos_fallidos=F("intentos_fallidos") + 1)
        self.refresh_from_db(fields=["intentos_fallidos"])
        if self.intentos_fallidos >= max_attempts:
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=lock_minutes)
            Usuario.objects.filter(pk=self.pk).update(bloqueado_hasta=self.bloqueado_hasta)

    def reset_failed_attempts(self) -> None:
        if self.intentos_fallidos or self.bloqueado_hasta:
            Usuario.objects.filter(pk=self.pk).update(intentos_fallidos=0, bloqueado_hasta=None)
            self.intentos_fallidos, self.bloqueado_hasta = 0, None


class SesionUsuario(models.Model):
    """Una fila por inicio de sesión; refresh_jti se actualiza en cada rotación."""

    class Dispositivo(models.TextChoices):
        DESKTOP = "Desktop"
        MOBILE = "Mobile"
        TABLET = "Tablet"
        KIOSK = "Kiosk"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="sesiones")
    refresh_jti = models.CharField(max_length=64, unique=True)
    ip_origen = models.GenericIPAddressField()                 # INET en PostgreSQL
    user_agent = models.CharField(max_length=512, default="", blank=True)
    dispositivo = models.CharField(max_length=10, choices=Dispositivo.choices, null=True, blank=True)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField()
    is_activa = models.BooleanField(default=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "sesiones_usuario"
        indexes = [models.Index(fields=["usuario", "is_activa"], name="idx_sesion_usuario_activa")]
        constraints = [
            models.CheckConstraint(
                condition=Q(dispositivo__isnull=True) | Q(dispositivo__in=["Desktop", "Mobile", "Tablet", "Kiosk"]),
                name="chk_sesion_dispositivo",
            ),
        ]

    def __str__(self) -> str:
        return f"Sesión {self.id} ({'activa' if self.is_activa else 'cerrada'})"


class RegistroAuditoriaAccesoQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise PermissionDenied("La bitácora de accesos es solo-inserción.")

    def delete(self):
        raise PermissionDenied("La bitácora de accesos es solo-inserción.")


class RegistroAuditoriaAcceso(models.Model):
    """Bitácora de accesos. Solo-inserción en la aplicación y en la base de datos (REVOKE UPDATE/DELETE)."""

    class Resultado(models.TextChoices):
        SUCCESS = "SUCCESS"
        FAILURE = "FAILURE"
        BLOCKED = "BLOCKED"

    documento_ingresado = models.CharField(max_length=20, db_index=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="accesos"
    )
    evento = models.CharField(max_length=40)
    resultado = models.CharField(max_length=10, choices=Resultado.choices)
    motivo_fallo = models.CharField(max_length=150, null=True, blank=True)
    ip_origen = models.GenericIPAddressField(db_index=True)
    user_agent = models.CharField(max_length=512, default="", blank=True)
    fecha_evento = models.DateTimeField(default=timezone.now)
    tiempo_respuesta_ms = models.IntegerField(null=True, blank=True)

    objects = RegistroAuditoriaAccesoQuerySet.as_manager()

    class Meta:
        db_table = "registro_auditoria_acceso"
        ordering = ["-fecha_evento"]
        indexes = [
            models.Index(fields=["-fecha_evento"], name="idx_auditoria_fecha"),
            models.Index(fields=["usuario", "-fecha_evento"], name="idx_auditoria_usuario_fecha"),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(resultado__in=["SUCCESS", "FAILURE", "BLOCKED"]), name="chk_auditoria_resultado"),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise PermissionDenied("La bitácora de accesos es solo-inserción.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionDenied("La bitácora de accesos es solo-inserción.")

    def __str__(self) -> str:
        return f"[{self.fecha_evento:%Y-%m-%d %H:%M}] {self.evento} ({self.resultado})"


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class TokenRestablecimientoClave(models.Model):
    """Token de un solo uso para restablecer la clave. Solo se guarda el SHA-256."""

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="tokens_restablecimiento")
    token_hash = models.CharField(max_length=64, unique=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField()
    usado_en = models.DateTimeField(null=True, blank=True)
    ip_solicitud = models.GenericIPAddressField()
    ip_cambio = models.GenericIPAddressField(null=True, blank=True)
    user_agent_solicitud = models.CharField(max_length=512, default="", blank=True)

    class Meta:
        db_table = "tokens_restablecimiento_clave"
        indexes = [
            models.Index(fields=["usuario", "usado_en", "fecha_expiracion"], name="idx_token_pwd_vigencia"),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(fecha_expiracion__gt=F("fecha_creacion")), name="chk_token_pwd_expiracion"),
        ]

    def __str__(self) -> str:
        return f"Token de restablecimiento #{self.pk} ({'usado' if self.usado_en else 'sin usar'})"

    def is_valid(self) -> bool:
        return self.usado_en is None and timezone.now() <= self.fecha_expiracion

    @classmethod
    def generar(cls, usuario: Usuario, ip: str, user_agent: str) -> str:
        """Invalida los tokens vigentes y crea uno nuevo. Devuelve el token en claro (solo para el correo)."""
        token = secrets.token_urlsafe(32)
        ahora = timezone.now()
        minutos = getattr(settings, "PASSWORD_RESET_MINUTES", 15)
        with transaction.atomic():
            cls.objects.filter(usuario=usuario, usado_en__isnull=True).update(usado_en=ahora)
            cls.objects.create(
                usuario=usuario,
                token_hash=_hash_token(token),
                fecha_creacion=ahora,
                fecha_expiracion=ahora + timedelta(minutes=minutos),
                ip_solicitud=ip,
                user_agent_solicitud=user_agent[:512],
            )
        return token

    @classmethod
    def obtener_vigente(cls, token: str, bloquear: bool = False) -> "TokenRestablecimientoClave | None":
        """Busca por hash. Con bloquear=True debe llamarse dentro de transaction.atomic()."""
        qs = cls.objects.select_related("usuario")
        if bloquear:
            qs = qs.select_for_update(of=("self",))
        obj = qs.filter(token_hash=_hash_token(token)).first()
        return obj if obj and obj.is_valid() and obj.usuario.is_active else None
```

### Uso en la confirmación del restablecimiento (servicio)

```python
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


def confirmar_restablecimiento(token: str, nueva_clave: str, ip: str) -> bool:
    with transaction.atomic():
        registro = TokenRestablecimientoClave.obtener_vigente(token, bloquear=True)
        if registro is None:
            return False
        usuario = registro.usuario
        validate_password(nueva_clave, user=usuario)  # lanza ValidationError → 400 PASSWORD_POLICY
        usuario.set_password(nueva_clave)
        usuario.debe_cambiar_clave = False
        usuario.save(update_fields=["password", "debe_cambiar_clave"])
        registro.usado_en = timezone.now()
        registro.ip_cambio = ip
        registro.save(update_fields=["usado_en", "ip_cambio"])
        # Revocar todas las sesiones del usuario
        pendientes = OutstandingToken.objects.filter(user=usuario, blacklistedtoken__isnull=True)
        BlacklistedToken.objects.bulk_create(
            [BlacklistedToken(token=t) for t in pendientes], ignore_conflicts=True  # BP-13
        )
        SesionUsuario.objects.filter(usuario=usuario, is_activa=True).update(
            is_activa=False, fecha_cierre=timezone.now()
        )
    return True
```

> `apps.archivos.validators` (`validar_imagen_avatar`, `ruta_avatar`) se define en [`../archivos/spec_model_archivos_media.md`](../archivos/spec_model_archivos_media.md).
