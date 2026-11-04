# 02. Arquitectura de Sistema y Máquinas de Estado
## Módulo de Login / Autenticación — SDD Joli Foods (`SPEC-AUTH-001`)

---

## 1. Topología

El frontend es una SPA (*Single Page Application*) en React + Vite. El backend es Django REST Framework (rutas `/api/v1/...`), con FastAPI montado en el mismo ASGI para rutas `/fast/v1/...` y las sondas `/health/live` y `/health/ready`. La identidad federada la provee Microsoft Entra ID.

```mermaid
flowchart TD
    subgraph CLIENTE["Frontend (React SPA)"]
        UI["LoginPage / LoginForm"]
        ZOD["Validación Zod"]
        CTX["AuthContext (access token en memoria)"]
        HTTP["Cliente HTTP (interceptor 401 + cola de refresh)"]
    end

    subgraph RED["Red"]
        NGINX["Nginx (TLS, HSTS)"]
    end

    subgraph BACKEND["Backend Django REST Framework"]
        VIEWS["Vistas /api/v1/auth/*"]
        RATE["Limitador de intentos (Redis)"]
        HASH["Hasher de Django (Argon2id / PBKDF2)"]
        JWT["SimpleJWT + token_blacklist"]
        AUD["Bitácora de accesos (solo inserción)"]
    end

    subgraph DATOS["Identidad y persistencia"]
        ENTRA["Microsoft Entra ID (OIDC)"]
        PG["PostgreSQL"]
        REDIS["Redis"]
    end

    UI --> ZOD --> CTX --> HTTP --> NGINX --> VIEWS
    VIEWS --> RATE --> REDIS
    VIEWS --> HASH
    VIEWS --> JWT --> PG
    VIEWS --> AUD --> PG
    VIEWS -.->|Authorization Code + PKCE| ENTRA
    VIEWS -->|"Body: access token / Set-Cookie: refresh HttpOnly"| HTTP
```

---

## 2. Diagramas de Secuencia

### 2.1. Documento + contraseña

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    participant UI as LoginForm (React)
    participant API as POST /api/v1/auth/login/
    participant RL as Limitador (Redis)
    participant DB as PostgreSQL

    U->>UI: Digita documento y contraseña
    UI->>UI: Valida con Zod
    alt Formato inválido
        UI-->>U: Errores en línea
    else Formato válido
        UI->>API: {numero_documento, password} (withCredentials)
        API->>RL: ¿Documento o IP bloqueados?
        alt Bloqueado
            API-->>UI: 429 + Retry-After
        else Permitido
            API->>DB: Busca usuario por documento
            Note over API: Si no existe, ejecuta el hasher sobre una clave ficticia<br/>para igualar el tiempo de respuesta
            alt No existe o contraseña errada
                API->>RL: Incrementa contadores (documento e IP)
                API->>DB: Inserta evento de bitácora
                API-->>UI: 401 INVALID_CREDENTIALS (mismo cuerpo en ambos casos)
            else Rol exige SSO
                API-->>UI: 403 SSO_REQUIRED
            else Usuario inactivo
                API-->>UI: 403 USER_INACTIVE
            else Válido
                API->>RL: Reinicia contadores del documento
                API->>DB: Crea SesionUsuario, actualiza last_login, inserta bitácora
                API-->>UI: 200 {access, expires_in, user} + Set-Cookie refresh (HttpOnly)
                UI->>UI: AuthContext guarda access en memoria
                UI-->>U: Redirige a ?redirect= o al tablero
            end
        end
    end
```

### 2.2. Microsoft SSO (sin tokens en la URL)

```mermaid
sequenceDiagram
    autonumber
    actor U as Colaborador
    participant UI as LoginPage
    participant API as Backend /api/v1/auth/microsoft/*
    participant MS as Microsoft Entra ID
    participant DB as PostgreSQL

    U->>UI: Clic en "Iniciar sesión con Microsoft 365"
    UI->>API: Navega a GET /api/v1/auth/microsoft/login/
    API->>API: Genera state + code_verifier (PKCE), los guarda en sesión de servidor
    API-->>U: 302 a login.microsoftonline.com
    U->>MS: Autenticación + MFA
    MS-->>API: 302 a GET /api/v1/auth/microsoft/callback/?code=...&state=...
    API->>API: Valida state, intercambia code por id_token, valida firma, aud, iss y nonce
    API->>DB: Busca colaborador por oid/email (no crea administradores automáticamente)
    API-->>U: 302 a /auth/callback del frontend + Set-Cookie refresh (HttpOnly)
    UI->>API: POST /api/v1/auth/refresh/ (cookie + X-CSRFToken)
    API-->>UI: 200 {access, expires_in}
    UI-->>U: Redirige al tablero
```

**Por qué:** el `code` de OAuth lo consume el backend; al frontend solo llega la cookie HttpOnly. Ningún token viaja en la URL (BP-18).

---

## 3. Máquina de Estados de la Interfaz

```mermaid
stateDiagram-v2
    [*] --> IDLE : Montaje (precarga documento recordado si existe)
    IDLE --> VALIDATING_LOCAL : Enviar
    VALIDATING_LOCAL --> FIELD_ERROR : Zod falla
    FIELD_ERROR --> IDLE : Usuario corrige
    VALIDATING_LOCAL --> SUBMITTING : Formato válido (inputs y botón deshabilitados)

    SUBMITTING --> AUTH_SUCCESS : 200
    SUBMITTING --> AUTH_FAILED : 401
    SUBMITTING --> SSO_REQUIRED : 403 SSO_REQUIRED
    SUBMITTING --> FORBIDDEN_INACTIVE : 403 USER_INACTIVE
    SUBMITTING --> RATE_LIMITED : 429
    SUBMITTING --> NETWORK_ERROR : Error de red / 5xx

    AUTH_FAILED --> IDLE : Alerta en línea
    SSO_REQUIRED --> IDLE : Se destaca el botón de Microsoft
    FORBIDDEN_INACTIVE --> IDLE : Alerta de cuenta desactivada
    RATE_LIMITED --> COUNTDOWN_LOCK : Cuenta regresiva según Retry-After
    COUNTDOWN_LOCK --> IDLE : Temporizador en cero
    NETWORK_ERROR --> IDLE : Botón "Reintentar"

    AUTH_SUCCESS --> REDIRECTING : navigate(redirect)
    REDIRECTING --> [*]
```

El temporizador de `COUNTDOWN_LOCK` DEBE limpiarse (`clearInterval`) al desmontar el componente.

---

## 4. Ciclo de Vida de la Sesión (decisión canónica)

| Paso | Comportamiento |
| :--- | :--- |
| **Emisión** | `POST /api/v1/auth/login/` devuelve el **access token** (15 min) en el cuerpo JSON y fija el **refresh token** (12 h, rotativo) en la cookie `refresh_token` con `HttpOnly; Secure; SameSite=Lax; Path=/api/v1/auth/`. También fija la cookie `csrftoken` (no HttpOnly, para que el cliente la lea). |
| **Almacenamiento en cliente** | El access token vive **solo en memoria** (estado de `AuthContext` o variable de módulo del cliente HTTP). NO DEBE guardarse en `localStorage` ni `sessionStorage`. |
| **Uso** | Cada petición API envía `Authorization: Bearer <access>`. |
| **Recuperación al recargar** | Al montar la app, `AuthContext` llama `POST /api/v1/auth/refresh/` con `withCredentials: true` y `X-CSRFToken`. Si responde 200, hay sesión; si no, el usuario queda no autenticado (sin modal). |
| **Renovación** | El interceptor ante un 401 intenta **un** refresh; las peticiones concurrentes esperan en cola el mismo refresh; si el refresh falla, despacha `session-expired` y se muestra `SessionExpirationModal`. No hay reintentos en bucle. |
| **Aviso proactivo** | El cliente PUEDE decodificar `exp` del access token en memoria para renovar o avisar antes del vencimiento (BP-20). |
| **Rotación** | Cada refresh emite un nuevo refresh token y pone el anterior en lista negra (`ROTATE_REFRESH_TOKENS = True`, `BLACKLIST_AFTER_ROTATION = True`). |
| **Cierre** | `POST /api/v1/auth/logout/` pone el refresh en lista negra, marca la `SesionUsuario` como inactiva y responde con `Set-Cookie: refresh_token=; Max-Age=0`. El cliente borra el access de memoria. |
| **Revocación global** | Cambiar o restablecer la contraseña DEBE invalidar todos los refresh tokens del usuario. |

**Por qué este diseño:** el access token en memoria no es persistente ni accesible a otras pestañas o extensiones a través del almacenamiento; el refresh en cookie HttpOnly no es legible por JavaScript (mitiga robo por XSS) y el CSRF en `/refresh/` evita que otro sitio lo use.
