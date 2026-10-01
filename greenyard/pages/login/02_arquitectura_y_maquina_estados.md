# 02. Arquitectura de Sistema y Máquinas de Estado
## Módulo de Login / Autenticación — SDD Greenyard (`GY-SPEC-AUTH-001`)

---

## 1. Topología Arquitectónica del Sistema

El sistema de autenticación de Greenyard opera bajo un modelo de desacoplamiento entre el cliente frontend (SPA en React / Vite) y la capa de servicios backend (Django REST Framework / Python) conectada a la infraestructura corporativa de identidad (Microsoft Azure AD / Entra ID).

```mermaid
flowchart TD
    subgraph CLIENTE["Frontend (React / Single Page Application)"]
        UI["Vista Login / GreenyardLoginForm"]
        ZOD["Validador de Esquemas (Zod)"]
        CTX["Contexto de Auth (AuthContext)"]
        INTER["Interceptor Axios / Fetch"]
        COOKIE_STORE["Almacén de Cookies / Storage"]
    end

    subgraph GATEWAY["Capa de Red y Seguridad"]
        NGINX["Nginx Reverse Proxy / SSL Termination"]
        RATE["Rate Limiter (Redis / Cache Jail)"]
    end

    subgraph BACKEND["Capa Backend (Django REST Framework)"]
        AUTH_VIEW["Controlador de Auth (Views)"]
        AUTH_BACKEND["Custom Auth Backend (Hashers)"]
        AUDIT["Middleware de Auditoría (RegistroActividad)"]
        JWT_SVC["Servicio SimpleJWT / RefreshTokens"]
    end

    subgraph IDP["Identidad Externa & Persistencia"]
        MS_AZURE["Microsoft Entra ID (Azure AD OAuth2)"]
        PG_DB["Base de Datos PostgreSQL (Usuarios & Roles)"]
    end

    UI --> ZOD
    ZOD --> CTX
    CTX --> INTER
    INTER --> NGINX
    NGINX --> RATE
    RATE --> AUTH_VIEW
    AUTH_VIEW --> AUTH_BACKEND
    AUTH_VIEW --> AUDIT
    AUTH_VIEW --> JWT_SVC
    AUTH_VIEW -.->|Verificación SSO| MS_AZURE
    AUTH_BACKEND --> PG_DB
    AUTH_VIEW -->|Set-Cookie HttpOnly| COOKIE_STORE
```

---

## 2. Diagramas de Secuencia de Autenticación

### 2.1. Flujo Canónico con Credenciales (Cédula + Contraseña)

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    participant UI as Formulario Login (React)
    participant API as Backend Auth API (Django)
    participant SEC as Motor de Seguridad (RateLimit & Hash)
    participant DB as Base de Datos

    U->>UI: Digita Documento y Contraseña
    UI->>UI: Valida formato con esquema Zod
    alt Formato Inválido
        UI-->>U: Muestra errores en línea (ej. solo números)
    else Formato Válido
        UI->>UI: Activa estado isSubmitting (Spinner)
        UI->>API: POST /api/auth/login/ {documento, password}
        API->>SEC: Verifica tasa de intentos por IP (Jail)
        alt IP Bloqueada
            SEC-->>UI: 429 Too Many Requests (Retry-After)
            UI-->>U: Notificación de bloqueo temporal
        else IP Confiable
            API->>DB: Consulta usuario por número de documento
            alt Usuario No Existe
                API-->>UI: 401 Unauthorized ("Credenciales inválidas")
                UI-->>U: Notificación de error
            else Usuario Existe
                API->>SEC: Compara hash de contraseña (PBKDF2/Bcrypt)
                alt Contraseña Incorrecta
                    SEC->>DB: Registra intento fallido
                    API-->>UI: 401 Unauthorized ("Credenciales inválidas")
                    UI-->>U: Notificación de error
                else Contraseña Válida
                    API->>DB: Valida estado activo (is_active = True)
                    alt Usuario Inactivo
                        API-->>UI: 403 Forbidden ("Cuenta inactiva")
                        UI-->>U: Alerta de contacto con soporte
                    else Usuario Activo
                        API->>API: Genera par de tokens JWT (Access / Refresh)
                        API->>DB: Registra acceso exitoso e IP
                        API-->>UI: 200 OK + Set-Cookie: HttpOnly jwt + Payload Usuario
                        UI->>UI: Actualiza estado global (AuthContext)
                        UI->>UI: Ejecuta animación de éxito (fade-out)
                        UI-->>U: Redirecciona al Dashboard corporativo
                    end
                end
            end
        end
    end
```

---

### 2.2. Flujo Institucional Single Sign-On (Microsoft 365 Azure AD)

```mermaid
sequenceDiagram
    autonumber
    actor U as Colaborador
    participant UI as Login Page (Greenyard)
    participant MS as Microsoft Login (login.microsoftonline.com)
    participant API as Backend /api/auth/microsoft/
    participant DB as Base de Datos

    U->>UI: Clic en "Iniciar sesión con Microsoft 365"
    UI->>MS: Redirección con ClientID, Scope y RedirectURI
    MS->>U: Despliega login corporativo / MFA institucional
    U->>MS: Aprueba acceso con credenciales Office 365
    MS->>UI: Redirecciona a /auth/callback?code=AUTH_CODE
    UI->>API: POST /api/auth/microsoft/callback/ {code}
    API->>MS: Intercambia code por id_token y access_token de Graph
    MS-->>API: Retorna perfil (email @jolifoods.com, nombres, oid)
    API->>DB: Sincroniza o busca colaborador por email/oid
    API->>API: Emite JWT de sesión Greenyard
    API-->>UI: 200 OK con Set-Cookie HttpOnly y datos de sesión
    UI-->>U: Notificación toast "¡Bienvenido!" y redirección
```

---

## 3. Máquina de Estados Finitos (FSM) de la Interfaz

```mermaid
stateDiagram-v2
    [*] --> UNMOUNTED
    UNMOUNTED --> IDLE : Componente montado (Precarga si hay "Recuérdame")
    
    IDLE --> TYPING : Usuario modifica campos
    TYPING --> IDLE : Usuario deja de tipear
    
    IDLE --> VALIDATING_LOCAL : Usuario presiona "Iniciar Sesión"
    VALIDATING_LOCAL --> FIELD_ERROR : Validación Zod falla (mensajes en rojo)
    FIELD_ERROR --> TYPING : Usuario corrige campos
    
    VALIDATING_LOCAL --> SUBMITTING : Formato válido -> Deshabilita inputs + Spinner
    
    SUBMITTING --> AUTH_SUCCESS : HTTP 200 OK (Tokens recibidos)
    SUBMITTING --> AUTH_FAILED : HTTP 401 Unauthorized
    SUBMITTING --> FORBIDDEN_INACTIVE : HTTP 403 Forbidden (Cuenta inactiva)
    SUBMITTING --> RATE_LIMITED : HTTP 429 Too Many Requests
    SUBMITTING --> NETWORK_ERROR : Fallo de conexión / 500 Server Error
    
    AUTH_FAILED --> IDLE : Alerta toast, inputs re-habilitados
    FORBIDDEN_INACTIVE --> IDLE : Modal de cuenta desactivada
    RATE_LIMITED --> COUNTDOWN_LOCK : Bloqueo con cuenta regresiva
    COUNTDOWN_LOCK --> IDLE : Temporizador llega a cero
    NETWORK_ERROR --> IDLE : Botón "Reintentar"
    
    AUTH_SUCCESS --> EXITING_ANIMATION : Transición visual suave (0.4s)
    EXITING_ANIMATION --> REDIRECTING : Navegación a ruta protegida
    REDIRECTING --> [*]
```

---

## 4. Ciclo de Vida del Token de Sesión

1. **Emisión**: Se genera un Access Token (vida útil: 1 hora) y un Refresh Token (vida útil: 24 horas a 7 días).
2. **Transporte Seguro**: El Access Token se envía preferentemente en una cookie `HttpOnly`, `Secure`, `SameSite=Lax`.
3. **Validación en Vuelo**: En cada petición entrante, el middleware de backend valida la firma criptográfica RSA/HMAC y verifica que el usuario no haya sido revocado en la base de datos.
4. **Rotación Silenciosa (Silent Refresh)**: Si el access token expira, el interceptor del cliente dispara una petición a `/api/auth/refresh/` para obtener un nuevo par sin interrumpir al usuario.
5. **Revocación**: Al presionar "Cerrar Sesión", el Refresh Token se añade a una lista negra (Blacklist) en la base de datos y la cookie del navegador es eliminada (`Max-Age=0`).
