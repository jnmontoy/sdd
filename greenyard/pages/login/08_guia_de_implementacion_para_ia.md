# 08. Guía de Implementación Paso a Paso para la Inteligencia Artificial
## Módulo de Login / Autenticación — SDD Greenyard (`GY-SPEC-AUTH-001`)

Esta guía instruye a cualquier modelo de Inteligencia Artificial (o desarrollador de software) sobre **cómo generar, estructurar e implementar el código del Login** a partir de los complementos de esta especificación SDD, sin hacer suposiciones sobre rutas locales absolutas.

---

## 0. Paso Previo Obligatorio para la IA: Preguntar el Nombre del Proyecto

> **INSTRUCCIÓN CRÍTICA PARA LA IA**:
> Antes de escribir cualquier archivo de código, la IA **DEBE PREGUNTAR AL USUARIO EL NOMBRE DEL PROYECTO**:
> *"¿Cuál es el nombre del proyecto o módulo que deseas estructurar? (ej. Tiendita, Control Operativo, Porterías, etc.)"*.

### Acciones que debe realizar la IA con el nombre obtenido:
1. **Copiar el Logo Oficial de Jolifoods**:
   - Tomar los archivos desde `.sdd/assets/` (`Jolifoods.svg`, `Joli.svg`, `logoJoli.png`) y ubicarlos en la carpeta de assets del nuevo proyecto (`frontend/src/assets/`).
2. **Configurar el Título del Navegador y Favicon (`index.html`)**:
   ```html
   <title>[Nombre del Proyecto] | Jolifoods</title>
   <link rel="icon" type="image/svg+xml" href="/src/assets/Jolifoods.svg" />
   ```
3. **Inyectar el Nombre en el Encabezado de Login (`LoginPage.tsx`)**:
   - Título H1: `[Nombre del Proyecto]`
   - Subtítulo: `Jolifoods • Acceso Seguro Corporativo`

---

## 1. Blueprint Canónico de Archivos a Generar en el Proyecto Destino

Cuando se ordene a la IA: *"Construye el login según el SDD de Greenyard / Jolifoods"*, debe crear en el espacio de trabajo objetivo la siguiente estructura relativa, aprovechando el stack consolidado en `.sdd/stack/`:

```
./
├── .env                              # Variables de entorno locales configuradas
├── .env.example
├── .gitignore                        # Reglas de exclusión (.venv, node_modules, etc.)
├── .venv/                            # Entorno virtual Python aislado para el IDE y herramientas locales
├── .vscode/                          # Configuración de intérprete Python para el editor
│   └── settings.json
├── docker-compose.yml                # Orquestador multi-contenedor (Postgres, Redis, Backend, Frontend)
│
├── frontend/                         # Stack: React + Vite + Bootstrap 5 + TypeScript
│   ├── Dockerfile
│   ├── package.json                  # Dependencias canónicas consolidadas (.sdd/stack/package.json)
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── assets/
│   │   │   └── Jolifoods.svg         # Copiado desde .sdd/assets/Jolifoods.svg
│   │   ├── styles/
│   │   │   └── variables.css         # Tokens globales y switch modo noche/día (.sdd/components/variables.css)
│   │   ├── schemas/
│   │   │   └── auth.schema.ts        # Zod schema (conforme a 03_contrato_api)
│   │   ├── types/
│   │   │   └── auth.types.ts         # Interfaces TypeScript (User, Session, AuthResponse)
│   │   ├── services/
│   │   │   └── auth.service.ts       # Cliente fetch/axios con credentials: 'include'
│   │   ├── context/
│   │   │   └── AuthContext.tsx       # Estado global tipado de usuario, sesión y tema día/noche
│   │   ├── hooks/
│   │   │   └── useLoginForm.ts       # Lógica del formulario con React Hook Form + Zod
│   │   ├── components/
│   │   │   └── auth/
│   │   │       ├── LoginForm.tsx     # Formulario React + Bootstrap + variables.css
│   │   │       ├── MicrosoftButton.tsx # Botón institucional SSO Microsoft 365
│   │   │       └── RecoveryModal.tsx # Modal de restablecimiento de contraseña
│   │   └── pages/
│   │       └── LoginPage.tsx         # Vista completa con tarjeta centrada y branding
│
└── backend/                          # Stack: Django ORM + FastAPI ASGI Engine (Ultra-rápido, Anti-N+1)
    ├── Dockerfile
    ├── requirements.txt              # Dependencias completas consolidadas (.sdd/stack/requirements.txt)
    ├── config/
    │   ├── asgi.py                   # Enrutamiento ASGI unificado (FastAPI + Django)
    │   ├── settings.py               # Django settings (DB, Redis, CORS, JWT)
    │   └── urls.py                   # Rutas administrativas Django
    └── apps/
        └── auth_core/
            ├── models.py             # Modelos Django ORM (Usuario, Sesion, Auditoria)
            ├── schemas.py            # Modelos Pydantic v2 (Serialización JSON de alto rendimiento)
            ├── api_fastapi.py        # Endpoints FastAPI (/api/v1/auth/login, /me, /recovery)
            ├── queries.py            # Consultas optimizadas con select_related() y prefetch_related() (Anti-N+1)
            ├── security.py           # Rate limiting con Redis, hashers y validación de tokens
            └── middleware.py         # Inyección de cookies HttpOnly seguras
```

---

## 2. Instrucciones de Implementación Frontend (Paso a Paso)

### Paso F-1: Definir los Esquemas Zod (`src/schemas/auth.schema.ts`)
- Implementar validación de número de cédula numérico (`^[0-9]+$`) entre 5 y 15 caracteres.
- Implementar validación de contraseña con mensajes amigables en español.

### Paso F-2: Configurar el Servicio de Red (`src/services/auth.service.ts`)
- **Regla Crítica**: Todas las peticiones `fetch` o `axios` dirigidas a `/api/auth/` deben incluir obligatoriamente la opción `credentials: 'include'` (o `withCredentials: true`) para permitir el intercambio transparente de la cookie segura `HttpOnly`.
- En caso de recibir código HTTP 401 o 403, mapear el payload de error JSON y propagarlo limpiamente a la UI.

### Paso F-3: Construir el Formulario con Ergonomía Visual (`src/components/auth/LoginForm.tsx`)
- Utilizar los tokens de diseño de `06_ui_ux_diseno_y_accesibilidad.md` (fondo oscuro slate, acentos verde esmeralda y glassmorphism).
- Añadir el toggle de visibilidad de contraseña (íconos `Eye` / `EyeOff` de `lucide-react`).
- Implementar la casilla "Recordar mi documento" leyendo y guardando en `localStorage` con la clave parametrizable `gy_remembered_doc`.
- Asegurar que durante el estado `submitting`, el botón de envío se desactive y muestre un spinner giratorio (`Loader2 animate-spin`).

---

## 3. Instrucciones de Implementación Backend (Paso a Paso)

### Paso B-1: Modelo de Usuario y Auditoría en Django ORM (`backend/apps/auth_core/models.py`)
- Modelo `Usuario` heredado de `AbstractBaseUser` con campo `numero_documento` indexado y único.
- Relaciones con Roles, Sedes y Permisos definidas con ForeignKeys apropiadas.
- Modelo `RegistroAuditoriaAcceso` y `TokenRestablecimientoClave` efímero indexado.

### Paso B-2: Prevención de Problemas N+1 y Optimización ORM (`backend/apps/auth_core/queries.py`)
- **Regla Anti-N+1 Estricta**: Toda consulta de usuario que requiera relaciones debe precargarse explícitamente:
  - Usar `.select_related('rol', 'sede', 'perfil')` para relaciones Foreign Key y One-to-One en un único `JOIN` SQL.
  - Usar `.prefetch_related('groups', 'user_permissions')` para relaciones Many-to-Many o inversas en lotes indexados.
  - Proyectar únicamente los campos necesarios con `.only()` o serializadores Pydantic livianos para evitar overhead de memoria.

### Paso B-3: Motor de Endpoints de Alta Velocidad FastAPI (`backend/apps/auth_core/api_fastapi.py`)
- Montado como sub-aplicación ASGI en `config/asgi.py` (`uvicorn config.asgi:application`).
- Serialización nativa con esquemas Pydantic v2 para máxima velocidad en la entrega de JSON (reduciendo latencias de serialización DRF).
- Rate Limiting distribuido con Redis antes de tocar la base de datos (HTTP 429 con `Retry-After: 900`).
- Emisión de tokens JWT con directivas de cookies seguras:
  - `httponly=True`
  - `secure=not settings.DEBUG`
  - `samesite='Lax'`
  - `path='/'`

---

## 4. Reglas Inflexibles para la IA (Guardrails)

1. **PROHIBIDO inventar campos de payload**: Los nombres de los atributos de entrada y salida deben coincidir al 100% con `03_contrato_api_y_modelos_datos.md`.
2. **PROHIBIDO guardar contraseñas o tokens en texto claro**: Ni en frontend (`localStorage`), ni en logs de backend, ni en la base de datos.
3. **PROHIBIDO usar rutas absolutas de disco local**: Toda referencia en el código debe ser relativa al proyecto o parametrizada vía variables de entorno (`import.meta.env` en Vite o `settings.py` / `os.getenv` en Django).
4. **TODOS los mensajes al usuario deben ser en español neutro**, comprensible y respetuoso.
