# Normativa Maestra de Buenas Prácticas y Auditoría de Seguridad
## Ecosistema Corporativo Jolifoods — Spec-Driven Development (SDD)
### Estándar de Conformidad Pre-Auditoría (Score Objetivo: 100 / 100)

Esta normativa formaliza **todos los criterios de evaluación, hardening y buenas prácticas validados en los procesos de auditoría del ecosistema Jolifoods** (Paso 01 al Paso 06, Pentesting OWASP y Docker).

Cualquier proyecto o módulo creado a partir de `.sdd` **debe nacer blindado bajo estos lineamientos técnicos desde el primer commit**, garantizando que supere cualquier auditoría sin requerir remediaciones posteriores.

---

## 1. Matriz de Conformidad Técnica (Las 6 Buenas Prácticas Obligatorias)

| # | Dimensión | Regla Inflexible para el Proyecto | Implementación Técnica Obligatoria |
|---|---|---|---|
| **BP-01** | **Aislamiento de Entorno (`DEBUG`)** | Nunca ejecutar `DEBUG=True` en producción. Los secretos jamás se cablean en código. | Leer estrictamente de variables de entorno (`.env`). Lanzar excepción fatal en el arranque si `DEBUG=False` y falta `SECRET_KEY` o credenciales de BD. |
| **BP-02** | **Blindaje de Hosts (`ALLOWED_HOSTS`)** | Prohibido terminantemente el uso del comodín `ALLOWED_HOSTS = ['*']`. | Lista explícita de dominios e IPs autorizadas: `ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')`. |
| **BP-03** | **Política de Orígenes Cruzados (`CORS`)** | Prohibido `CORS_ALLOW_ALL_ORIGINS = True`. | `CORS_ALLOWED_ORIGINS` restringido únicamente a los dominios y puertos del frontend institucional (`http://localhost:5173`, `https://*.jolifoods.com`). |
| **BP-04** | **Limitación de Tasa (`Throttling / Rate Limiting`)** | Proteger todos los endpoints contra fuerza bruta y DoS. | Rate Limiting distribuido respaldado en **Redis**: 5 req/min en login, 30 req/min para clientes anónimos y 120 req/min para usuarios autenticados. Retornar cabecera `Retry-After`. |
| **BP-05** | **Principio de Mínimo Privilegio (`Deny by Default`)** | Todo endpoint es privado y protegido por defecto, salvo excepción explícita. | `DEFAULT_PERMISSION_CLASSES = ['rest_framework.permissions.IsAuthenticated']` en Django y dependencias de autenticación mandatorias en FastAPI. El login es la única ruta pública autorizada. |
| **BP-06** | **Hardening Perimetral de Cabeceras HTTP & Cookies** | Forzar directivas de protección contra Clickjacking, MIME-Sniffing y XSS. | `X_FRAME_OPTIONS = 'DENY'`, `SECURE_CONTENT_TYPE_NOSNIFF = True`, `SESSION_COOKIE_HTTPONLY = True`, `CSRF_COOKIE_HTTPONLY = True`, directiva `SameSite = 'Lax'`. |

---

## 2. Buenas Prácticas de Arquitectura Backend (Django + FastAPI)

### 2.1. Erradicación Absoluta de Consultas N+1 (Django ORM)
1. **Relaciones Foráneas y Uno a Uno (`ForeignKey` / `OneToOne`)**:
   - Mandatorio el uso de `.select_related()` en todas las consultas que involucren roles, sedes, perfiles o departamentos en una única sentencia `JOIN` SQL:
     ```python
     # CORRECTO (1 Consulta SQL):
     usuario = Usuario.objects.select_related('rol', 'sede', 'perfil').get(numero_documento=doc)
     
     # INCORRECTO - PENALIZADO EN AUDITORÍA (N+1 Consultas SQL):
     usuario = Usuario.objects.get(numero_documento=doc)
     nombre_rol = usuario.rol.nombre  # Dispara una query adicional por cada registro
     ```
2. **Relaciones Muchos a Muchos y Relaciones Inversas (`ManyToManyField` / `Reverse FK`)**:
   - Mandatorio el uso de `.prefetch_related()` para precargar colecciones agrupadas mediante lotes indexados:
     ```python
     usuarios = Usuario.objects.prefetch_related('groups', 'user_permissions').filter(is_active=True)
     ```
3. **Proyección Estricta de Columnas (`.only()` y `.values()`)**:
   - Si solo se requieren atributos de identidad (cédula, nombre), proyectar únicamente esos campos para no consumir ancho de banda de red ni memoria en el pool de conexiones.

### 2.2. Entrega JSON de Alto Rendimiento en FastAPI
- Utilizar serialización con **Pydantic v2** (`TypeAdapter` y modelos validados) para entregar respuestas JSON en microsegundos, evitando serializadores pesados en endpoints de lectura intensiva.
- Implementar pooling de conexiones persistentes con PostgreSQL (`CONN_MAX_AGE = 600` en Django y pools asíncronos en async engines).

### 2.3. Manejo Seguro de Errores y Fugas de Información
- **Nunca exponer `stack traces` ni nombres internos de tablas en respuestas de error HTTP**.
- Capturar excepciones y mapearlas a un contrato de error estándar en español con código de correlación UUID:
  ```json
  {
    "status": "error",
    "error_code": "ERR_DATABASE_UNAVAILABLE",
    "message": "En este momento no es posible procesar la solicitud. Intente nuevamente en unos minutos.",
    "correlation_id": "c8b417ef-5769-42b8-935a-4933a30c5e7b"
  }
  ```

---

## 3. Buenas Prácticas de Frontend (React 19 + Vite + Bootstrap 5 + TypeScript)

### 3.1. Cero Almacenamiento de Tokens Críticos en `localStorage`
- **Regla Estricta contra XSS**: Ni el Access Token JWT ni el Refresh Token deben almacenarse en `localStorage` o `sessionStorage`.
- La autenticación debe manejarse mediante **Cookies Seguras `HttpOnly`**. En el almacenamiento local del navegador únicamente está permitido guardar preferencias cosméticas:
  - `jolifoods_theme`: `'dark'` | `'light'`
  - `gy_remembered_doc`: número de documento recordado (si el usuario marcó la casilla voluntariamente).

### 3.2. Optimización de Renderizado y Memoria en React
- Utilizar `useMemo` y `useCallback` en componentes con listas grandes o tablas de datos para evitar re-renderizados fantasmas.
- Desacoplar la lógica de formularios mediante hooks personalizados (`useLoginForm`, `useRecoveryForm`) usando **React Hook Form + Zod** para evitar renders en cada pulsación de tecla (`onBlur` o validación por esquema).
- Manejo limpio de suscripciones y temporizadores en `useEffect` con función de limpieza (`cleanup return () => clearInterval(...)`).

### 3.3. Estilizado Puro con `variables.css`
- Prohibido el uso de valores hexadecimales o RGB fijos quemados dentro de los estilos locales. Todo color, espaciado, radio de borde y fuente debe consumir las variables CSS corporativas (`var(--color-primary)`, `var(--color-bg-base)`, etc.) garantizando la conmutación instantánea entre **Modo Noche** y **Modo Día**.

---

## 4. Buenas Prácticas de Contenedores Docker e Infraestructura

1. **Usuarios No-Root (`Non-Root User`)**:
   - Los contenedores de producción deben ejecutarse bajo un usuario con privilegios mínimos (`appuser`), nunca como `root`.
2. **Imágenes Base Ligeras y Seguras**:
   - Usar `python:3.11-slim` o `alpine` y `node:20-alpine`, reduciendo la superficie de ataque y el tiempo de arranque.
3. **Higiene de Archivos (`.dockerignore`)**:
   - Omitir de forma mandatoria: `.git`, `node_modules`, `__pycache__`, `*.pyc`, `.env`, carpetas `.vscode`, archivos de log y temporales.
4. **Healthchecks Declarados en Orquestación**:
   - Todos los servicios críticos (`db`, `redis`, `backend`) deben contar con directiva `healthcheck` en `docker-compose.yml` utilizando las sondas de [`.sdd/stack/healthcheck.py`](../stack/healthcheck.py).
5. **Volúmenes Persistentes Nombrados**:
   - Separar el almacenamiento de base de datos (`postgres_data`), caché (`redis_data`) y archivos de medios (`media_volume`) del ciclo de vida de los contenedores.

---

## 5. Lista de Chequeo Rápida para la Creación de Proyectos (Pre-Flight Checklist)

Antes de dar por finalizada la creación de cualquier nuevo módulo, verificar:

- [ ] ¿El archivo `.env` está en `.gitignore` y existe un `.env.example` completo?
- [ ] ¿`ALLOWED_HOSTS` contiene únicamente los nombres de dominio de Jolifoods y localhost?
- [ ] ¿Las cabeceras de seguridad (`X_FRAME_OPTIONS`, `NOSNIFF`, `HttpOnly`, `SameSite`) están activas?
- [ ] ¿Todas las consultas ORM de usuario y entidades relacionadas usan `select_related` o `prefetch_related` (Anti-N+1)?
- [ ] ¿Las cookies de sesión tienen directiva `HttpOnly=True`?
- [ ] ¿El frontend lee los tokens de diseño desde `variables.css` con soporte noche/día?
- [ ] ¿El script `init_project.py` inyectó el nombre y logo de Jolifoods dinámicamente?
- [ ] ¿La sonda `/api/v1/health/` responde HTTP 200 con la latencia de Postgres y Redis?
