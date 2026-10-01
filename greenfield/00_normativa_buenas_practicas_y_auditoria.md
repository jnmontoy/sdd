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

### 3.4. Regla Inflexible de Maquetación: Layout 100% Horizontal (Prohibido Centrar la Pantalla)
- **PROHIBICIÓN TERMINANTE**: Queda estrictamente prohibido centrar vistas, tablas, módulos o dashboards en el frontend mediante contenedores estrechos (`max-w-xl mx-auto`, `max-w-4xl`, `items-center justify-center` en el contenedor raíz).
- **MAQUETACIÓN A LO LARGO DE LA PANTALLA**: Todo desarrollo frontend debe extenderse **a lo largo de la pantalla en horizontal (`width: 100%`, `w-full`, layout fluido)**, aprovechando de extremo a extremo el ancho del monitor para visualizar tablas masivas, toolbars y KPIs sin scroll horizontal forzado ni espacios vacíos a los costados.
- **Únicas excepciones de centrado**: Solo los diálogos emergentes (`ModalDialog`, `ConfirmModal`) y la tarjeta previa de autenticación (`LoginCard`).

### 3.5. Reutilización Estricta de Componentes y Prohibición de CSS Inventado
- **PROHIBICIÓN TERMINANTE**: Queda estrictamente prohibido crear archivos `.css` aislados o estilos improvisados desde cero para nuevos módulos (ej. inventar `users.css`, `pedidos.css` con selectores arbitrarios).
- **OBLIGACIÓN DE CONSUMO DE COMPONENTES `.sdd/components/`**: Todo desarrollo debe utilizar las clases, estructuras y contratos ya probados y auditados:
  - Tablas: `.joli-table`, `.cartera-table-wrapper-full` de `data_table.md`.
  - Toolbars: `.cartera-compact-action-box` (28px) y `.cartera-row-actions-group` (26px) de `icon_action_group.md`.
  - Filtros: `.cartera-topbar` de `expandable_filter_group.md` y `checklist_popover.md`.
  - Modales: `ConfirmModal` con justificación obligatoria.
  - Paneles: Right Drawer de `drawer.md`.
  - Colores: `variables.css`.
- **Sanción en Auditoría**: Cualquier archivo CSS huérfano que duplique o ignore los componentes auditados de `.sdd` será penalizado como falta grave de consistencia arquitectónica.

### 3.6. Creación y Edición CRUD Exclusiva en Right Sidebar Drawer (Prohibido Modales)
- **PROHIBICIÓN TERMINANTE**: Queda terminantemente prohibido generar formularios de creación (`+ Nuevo`) o edición (`Editar`) de cualquier CRUD en modales flotantes centrados (`ModalDialog`) o navegando a páginas separadas (`/crear`, `/editar`), a menos que la persona lo pida expresamente.
- **OBLIGATORIEDAD DE RIGHT DRAWER**: Todo formulario de captura, edición y detalle debe operar **exclusivamente desde el panel lateral derecho deslizante** ([`drawer.md`](../components/drawer/drawer.md), `.cartera-sidebar-drawer`). Esto preserva el contexto de la tabla en segundo plano, maximiza la ergonomía horizontal y evita la proliferación de modales intrusivos.
- **Uso Exclusivo de Modales**: Los modales centrados quedan reservados estrictamente para confirmaciones (`ConfirmModal`), firmas digitales (`SignatureModal`), lectores biométricos o alerta de sesión expirada.

### 3.7. Agrupación Obligatoria de Botones de Acción en Tablas con Bootstrap (`btn-group`)
- **PROHIBICIÓN TERMINANTE**: Queda terminantemente prohibido dejar botones sueltos o separados por márgenes (`btn me-1`, `btn me-2`) dentro de la celda de acciones/opciones de una tabla.
- **OBLIGATORIEDAD DE BOOTSTRAP `btn-group`**: Siempre que haya 2 o más botones de acción en una fila (ej. Ver en Drawer, Restablecer clave, Anular con ConfirmModal), deben agruparse obligatoriamente dentro de un contenedor `<div class="btn-group btn-group-sm cartera-row-actions-group" role="group">...</div>`, unificando las esquinas redondeadas en los extremos y garantizando una altura uniforme de 26px a 28px.

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
- [ ] ¿Se creó y aisló el entorno virtual `.venv` en la raíz del proyecto y se instaló `requirements.txt` exclusivamente dentro de él? (Cero paquetes instalados en el Python global del equipo).
- [ ] ¿El layout es 100% horizontal a lo largo de la pantalla (full-width) y libre de contenedores centrados tipo blog (`max-w-xl mx-auto`)?
- [ ] ¿Todos los módulos y vistas reutilizan directamente las clases CSS y componentes de `.sdd/components/` (cero archivos `.css` inventados o improvisados desde cero)?
- [ ] ¿La creación y edición de registros CRUD se realiza obligatoriamente desde el Right Drawer lateral (cero modales o páginas separadas para formularios de CRUD)?
- [ ] ¿Si una fila de tabla tiene 2 o más botones de acción, se encuentran agrupados obligatoriamente con Bootstrap `btn-group btn-group-sm` (cero botones sueltos con márgenes)?
- [ ] ¿La sonda `/api/v1/health/` responde HTTP 200 con la latencia de Postgres y Redis?





