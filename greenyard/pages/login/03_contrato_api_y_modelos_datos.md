# 03. Contratos de API, Modelos de Datos y OpenAPI Specs
## Módulo de Login / Autenticación — SDD Greenyard (`GY-SPEC-AUTH-001`)

Este documento constituye la **fuente formal e inmutable de especificación técnica** para la comunicación cliente-servidor en el módulo de login. Cualquier implementación (sea en Django, FastAPI, Node, Go o cualquier otro backend) y cualquier cliente (React, Vue, Flutter, iOS, Android) debe adherirse estrictamente a estos esquemas.

---

## 1. Esquema de Modelos de Datos Canónicos

### 1.1. Modelo Conceptual de Usuario (`UserEntity`)

```typescript
export interface UserEntity {
  /** Identificador único autonumérico */
  id: number;
  /** Número de cédula o documento de identidad oficial (único) */
  documento: string;
  /** Nombre completo de la persona */
  nombre: string;
  /** Apellidos de la persona */
  apellidos?: string;
  /** Correo corporativo (@jolifoods.com o @greenyard.com) */
  email: string;
  /** Rol jerárquico principal */
  tipo: 'Administrador' | 'Colaborador' | 'Operario' | 'Auditor';
  /** Lista de permisos o grupos funcionales */
  roles: string[];
  /** Cargo formal según nómina/HR */
  cargo?: string;
  /** Sede, planta o unidad de negocio */
  sede?: string;
  /** Estado de habilitación del usuario en la plataforma */
  is_active: boolean;
  /** URL o URI del avatar corporativo */
  avatar_url?: string | null;
  /** Marca temporal del último inicio de sesión exitoso */
  last_login?: string | null;
}
```

---

## 2. Especificación Formal de Endpoints (OpenAPI 3.1)

### 2.1. `POST /api/auth/login/` (Autenticación Principal)

- **Propósito**: Validar credenciales de usuario (documento + contraseña) y emitir sesión segura.
- **Autenticación**: Pública (no requiere token previo).
- **Control de Tasa (Rate Limit)**: Máximo 5 peticiones por minuto por IP.

#### Request Body
- **Content-Type**: `application/json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "LoginCredentialsPayload",
  "type": "object",
  "properties": {
    "documento": {
      "type": "string",
      "pattern": "^[0-9]{5,15}$",
      "description": "Número de cédula sin espacios ni caracteres especiales"
    },
    "password": {
      "type": "string",
      "minLength": 1,
      "description": "Contraseña en texto claro enviada bajo túnel seguro TLS"
    },
    "rememberMe": {
      "type": "boolean",
      "default": false,
      "description": "Indica si el cliente debe recordar el documento en el equipo"
    }
  },
  "required": ["documento"]
}
```

#### Respuestas HTTP

##### 200 OK (Autenticación Exitosa)
- **Cabeceras de Respuesta**:
  - `Set-Cookie: greenyard_auth_token=<JWT_TOKEN>; Path=/; HttpOnly; SameSite=Lax; Max-Age=86400`
- **Body**:
```json
{
  "success": true,
  "message": "Autenticación exitosa. Bienvenido al sistema.",
  "user": {
    "id": 101,
    "documento": "1037645123",
    "nombre": "Joan Montoya",
    "email": "joan.montoya@jolifoods.com",
    "tipo": "Administrador",
    "roles": ["TI_LEAD", "SECURITY_ADMIN"],
    "cargo": "Líder de TI & Arquitectura",
    "sede": "Planta Principal",
    "avatar_url": "/media/avatars/user_101.webp"
  },
  "token_type": "Bearer",
  "expires_in": 86400
}
```

##### 400 Bad Request (Payload Inválido)
```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "message": "Datos de entrada inválidos",
  "details": {
    "documento": ["El documento debe contener exclusivamente dígitos numéricos."]
  }
}
```

##### 401 Unauthorized (Credenciales Incorrectas)
```json
{
  "success": false,
  "error_code": "INVALID_CREDENTIALS",
  "message": "El documento o la contraseña ingresada son incorrectos."
}
```

##### 403 Forbidden (Cuenta Desactivada o Forzado a SSO)
```json
{
  "success": false,
  "error_code": "USER_INACTIVE",
  "message": "Tu cuenta de usuario se encuentra desactivada. Contacta al administrador del sistema."
}
```

##### 429 Too Many Requests (Exceso de Intentos / Brute Force)
- **Cabecera**: `Retry-After: 900`
```json
{
  "success": false,
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Has excedido el número máximo de intentos fallidos. Intenta nuevamente en 15 minutos.",
  "retry_after_seconds": 900
}
```

---

### 2.2. `POST /api/auth/check-user/` (Pre-chequeo Inteligente de Rol)

- **Propósito**: Consultar rápidamente si la cédula corresponde a un usuario con requerimientos especiales (por ejemplo, exigir inicio de sesión exclusivo vía Microsoft SSO para administradores) antes de solicitar contraseñas locales.
- **Autenticación**: Pública.

#### Request Body
```json
{
  "documento": "1037645123"
}
```

#### Response 200 OK
```json
{
  "exists": true,
  "is_active": true,
  "tipo": "Administrador",
  "requires_sso": true,
  "provider": "MICROSOFT_365",
  "display_name": "Joan Montoya"
}
```

---

### 2.3. `POST /api/auth/refresh/` (Rotación Silenciosa de Sesión)

- **Propósito**: Renovar el Access Token antes de su expiración utilizando la cookie de sesión o el Refresh Token.
- **Cabeceras**: Requiere cookie `HttpOnly` previa o cabecera `Authorization: Bearer <refresh_token>`.

#### Response 200 OK
```json
{
  "success": true,
  "message": "Sesión renovada con éxito",
  "expires_in": 86400
}
```

---

### 2.4. `POST /api/auth/logout/` (Cierre de Sesión Seguro)

- **Propósito**: Invalidar tokens en backend (blacklist) y eliminar las cookies de autenticación en el cliente.
- **Efecto de Red**:
  - `Set-Cookie: greenyard_auth_token=; Path=/; HttpOnly; Max-Age=0`

#### Response 200 OK
```json
{
  "success": true,
  "message": "Sesión finalizada correctamente."
}
```

---

## 3. Endpoints de Restablecimiento de Contraseña

### 3.1. `POST /api/auth/password-reset/request/` (Solicitud de Enlace)
- **Propósito**: Iniciar el flujo de recuperación generando un token de 15 minutos y enviando un correo al colaborador.
- **Seguridad**: Respuesta idéntica exista o no la cuenta para prevenir enumeración.

#### Request Body
```json
{
  "identificador": "1037645123"
}
```

#### Response 200 OK
```json
{
  "success": true,
  "message": "Si los datos corresponden a un usuario activo en Jolifoods, recibirás un enlace de recuperación en tu correo corporativo."
}
```

---

### 3.2. `POST /api/auth/password-reset/validate/` (Comprobación de Vigencia)
- **Propósito**: Verificar si el token sigue vigente antes de renderizar el formulario de nueva clave.

#### Request Body
```json
{
  "token": "token_efimero_32_bytes_base64"
}
```

#### Response 200 OK
```json
{
  "valid": true,
  "email_enmascarado": "j***a@jolifoods.com"
}
```

---

### 3.3. `POST /api/auth/password-reset/confirm/` (Cambio Efectivo de Contraseña)
- **Propósito**: Fijar la nueva clave, consumir el token e invalidar todas las sesiones activas del usuario.

#### Request Body
```json
{
  "token": "token_efimero_32_bytes_base64",
  "new_password": "NuevaPasswordSegura!2026",
  "confirm_password": "NuevaPasswordSegura!2026"
}
```

#### Response 200 OK
```json
{
  "success": true,
  "message": "Contraseña actualizada exitosamente. Inicia sesión con tus nuevas credenciales."
}
```
