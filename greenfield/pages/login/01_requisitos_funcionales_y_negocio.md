# 01. Requisitos Funcionales y de Negocio
## Módulo de Login / Autenticación — SDD Joli Foods (`SPEC-AUTH-001`)

> **Lenguaje normativo:** este documento usa **DEBE / NO DEBE / DEBERÍA / NO DEBERÍA / PUEDE** con el sentido de RFC 2119. DEBE se reserva para seguridad e integridad.
>
> **Decisión canónica de sesión (resumen):** access token (JWT) **solo en memoria**; refresh token en cookie `HttpOnly; Secure; SameSite=Lax` emitida por `POST /api/v1/auth/login/` y rotada por `POST /api/v1/auth/refresh/` con cabecera CSRF; `POST /api/v1/auth/logout/` borra la cookie e invalida el refresh. Detalle en [`02_arquitectura_y_maquina_estados.md`](./02_arquitectura_y_maquina_estados.md) §4 y [`05_seguridad_auditoria_y_hardening.md`](./05_seguridad_auditoria_y_hardening.md) §2.

---

## 1. Objetivos del Módulo

1. **Garantizar la identidad y trazabilidad** de cada persona que usa las aplicaciones de Joli Foods.
2. **Reducir la fricción operativa** del personal de planta sin comprometer la seguridad.
3. **Gobernar los accesos privilegiados** mediante inicio de sesión único (SSO, *Single Sign-On*) con Microsoft Entra ID y autenticación multifactor (MFA).
4. **Registrar en bitácora** cada intento de acceso, exitoso o fallido, con IP, agente de usuario y marca de tiempo.

---

## 2. Perfiles de Acceso

Los perfiles son **ejemplos funcionales**. Los roles reales se administran en base de datos (tabla `Rol`, ver BP-19 y [`../../../model/roles/spec_model_roles_permisos.md`](../../../model/roles/spec_model_roles_permisos.md)); el mecanismo de autenticación exigido se define por el atributo `exige_sso` del rol, no por un nombre quemado en código.

| Perfil (ejemplo) | Mecanismo de autenticación | MFA |
| :--- | :--- | :--- |
| Operario de planta | Documento + contraseña o, en quiosco autorizado, reconocimiento facial con alternativa manual. | No |
| Vigilante de portería | Documento + contraseña. El ingreso sin contraseña solo PUEDE habilitarse con una decisión registrada (ADR) (ver BR-03). | No |
| Colaborador administrativo | Documento + contraseña o Microsoft SSO. | DEBERÍA |
| Administrador de plataforma | Microsoft SSO (rol con `exige_sso = true`). | DEBE (gestionado por Entra ID) |
| Auditor / invitado externo | Documento + contraseña con fecha de expiración de la cuenta. | DEBERÍA |

---

## 3. Requisitos Funcionales (RF)

| Código | Requisito | Descripción |
| :--- | :--- | :--- |
| **RF-01** | Ingreso por documento | El sistema DEBE aceptar el número de documento sin puntos, guiones ni espacios (`^[0-9]{5,15}$`). |
| **RF-02** | Validación de contraseña | La contraseña DEBE verificarse con el hasher de Django (Argon2id preferido, PBKDF2 como alternativa). NO DEBE implementarse hashing manual (ni bcrypt "a mano", ni SHA). |
| **RF-03** | Microsoft SSO | Botón "Iniciar sesión con Microsoft 365" que inicia el flujo OAuth 2.0 / OIDC (*Authorization Code* + PKCE) contra el tenant configurado en `AZURE_TENANT_ID`. |
| **RF-04** | Pre-chequeo de método | El cliente PUEDE consultar `POST /api/v1/auth/check-user/` para saber si debe mostrar contraseña o SSO. La respuesta NO DEBE revelar si el usuario existe (ver contrato en 03). |
| **RF-05** | "Recordar mi documento" | Casilla opcional que guarda **solo el documento** (nunca contraseña ni tokens) en `localStorage` bajo `STORAGE_KEYS.rememberedDoc`. En quioscos compartidos la casilla NO DEBERÍA mostrarse. |
| **RF-06** | Ver/ocultar contraseña | Botón con ícono de ojo y `aria-label` dinámico que alterna `type="password"`/`type="text"`. |
| **RF-07** | Recuperación de contraseña | Enlace "¿Olvidaste tu contraseña?" hacia el flujo de [`09_flujo_restablecimiento_contrasena.md`](./09_flujo_restablecimiento_contrasena.md). |
| **RF-08** | Sesión expirada | Al vencer la sesión (refresh rechazado), la interfaz DEBE mostrar `SessionExpirationModal` y volver al login conservando la ruta previa (`/login?redirect=...`) (BP-20). |
| **RF-09** | Protección contra fuerza bruta | 5 intentos fallidos en 15 minutos para un mismo documento (exista o no) o 20 desde una misma IP DEBEN producir bloqueo temporal con espera creciente (ver 05 §3). |
| **RF-10** | Usuario inactivo | Si `is_active = false`, el acceso DEBE negarse con HTTP 403 `USER_INACTIVE`, **solo después** de validar la contraseña (para no revelar el estado a quien no la conoce). |
| **RF-11** | Alternativa biométrica | En quioscos con reconocimiento facial, tras 3 intentos fallidos la interfaz DEBERÍA ofrecer el ingreso manual. |
| **RF-12** | Cierre de sesión | `POST /api/v1/auth/logout/` DEBE invalidar el refresh token (lista negra), borrar la cookie y el cliente DEBE descartar el access token de memoria. |

---

## 4. Requisitos No Funcionales (RNF)

| Código | Categoría | Criterio verificable |
| :--- | :--- | :--- |
| **RNF-01** | Rendimiento | p95 de `POST /api/v1/auth/login/` < 1,2 s medido en prueba de carga del entorno de pruebas (el hasher es deliberadamente costoso; no bajar su costo para cumplir la métrica). |
| **RNF-02** | Disponibilidad | Objetivo de disponibilidad definido por el equipo de infraestructura y medido con las sondas `/health/live` y `/health/ready` (ver 10). |
| **RNF-03** | Transporte | Todo tráfico DEBE ir por HTTPS (TLS 1.2 mínimo, 1.3 preferido) con HSTS en producción. |
| **RNF-04** | Protección de credenciales | Ninguna contraseña ni token DEBE escribirse en logs, bitácora, base de datos en claro ni mensajes de depuración. |
| **RNF-05** | Accesibilidad | WCAG 2.1 AA en el formulario (ver [`06_ui_ux_diseno_y_accesibilidad.md`](./06_ui_ux_diseno_y_accesibilidad.md)). |
| **RNF-06** | Navegadores | Pruebas E2E en Chromium, Firefox y WebKit (Playwright). |
| **RNF-07** | Responsive | Sin desbordes horizontales entre 360 px y 3840 px de ancho. |
| **RNF-08** | Idioma | Textos y mensajes en español, centralizados para permitir localización futura. |

---

## 5. Criterios de Aceptación (Gherkin)

Los datos son ficticios (`1000000001`, `usuario@ejemplo.com`).

### Escenario 1: Autenticación exitosa con documento y contraseña
```gherkin
Característica: Inicio de sesión con credenciales válidas
  Escenario: Colaborador activo ingresa con documento y contraseña
    Dado que existe un usuario activo con documento "1000000001"
    Cuando ingresa su documento y su contraseña correcta
    Y presiona "Ingresar"
    Entonces el botón muestra un indicador de carga y queda deshabilitado
    Y el backend responde HTTP 200 con el access token en el cuerpo
    Y la respuesta incluye la cabecera Set-Cookie del refresh token con HttpOnly, Secure y SameSite=Lax
    Y el access token NO se guarda en localStorage ni en sessionStorage
    Y el usuario es redirigido a la ruta solicitada o al tablero principal
```

### Escenario 2: Cuenta inactiva
```gherkin
  Escenario: Usuario desactivado intenta ingresar
    Dado que el usuario con documento "1000000002" está inactivo
    Cuando ingresa su documento y su contraseña correcta
    Entonces el backend responde HTTP 403 con error_code "USER_INACTIVE"
    Y la interfaz muestra "Tu cuenta está desactivada. Contacta al administrador."
    Y se registra el evento LOGIN_BLOCKED_INACTIVE en la bitácora de accesos
```

### Escenario 3: Rol que exige SSO
```gherkin
  Escenario: Usuario con rol que exige SSO
    Dado que el usuario con documento "1000000003" tiene un rol con exige_sso = true
    Cuando ingresa su documento
    Entonces check-user responde metodo = "SSO"
    Y la interfaz oculta el campo de contraseña y destaca "Iniciar sesión con Microsoft 365"
    Y si de todas formas se envía una contraseña a /auth/login/, el backend responde 403 "SSO_REQUIRED"
```

### Escenario 4: Documento inexistente
```gherkin
  Escenario: Documento no registrado
    Dado que no existe usuario con documento "1000000099"
    Cuando ingresa ese documento y cualquier contraseña
    Entonces el backend responde HTTP 401 con el mismo cuerpo que una contraseña errada
    Y el tiempo de respuesta no difiere de forma medible del caso "contraseña errada"
```

---

## 6. Reglas de Negocio (BR)

- **BR-01 — Política de contraseñas:** DEBE aplicarse mediante `AUTH_PASSWORD_VALIDATORS` de Django: longitud mínima 8 (DEBERÍA ser 12), `CommonPasswordValidator`, `UserAttributeSimilarityValidator` y `NumericPasswordValidator`. **Por qué:** la longitud y el rechazo de claves comunes protegen más que las reglas de composición (NIST SP 800-63B).
- **BR-02 — SSO por dominio:** los usuarios cuyo correo pertenezca a un dominio listado en `SSO_ALLOWED_DOMAINS` DEBERÍAN tener habilitado Microsoft SSO.
- **BR-03 — Ingreso sin contraseña en portería:** NO DEBERÍA usarse. Si el negocio lo requiere, PUEDE habilitarse solo con un ADR que fije: subred permitida, equipos registrados, token de alcance restringido (solo el módulo de portería) y vida máxima de 8 horas. **Por qué:** una IP de origen no es un factor de autenticación; es suplantable dentro de la red.
- **BR-04 — Vida de los tokens:** access token **15 minutos** (`JWT_ACCESS_MINUTES`); refresh token **12 horas** con rotación en cada uso (`JWT_REFRESH_HOURS`), máximo 7 días. **Por qué:** un access token corto limita el daño si se filtra; el refresh en cookie HttpOnly no es legible por JavaScript.
