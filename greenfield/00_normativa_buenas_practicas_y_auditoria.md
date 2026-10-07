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
| **BP-07** | **Rutas 100% Relativas y Cero Rutas Absolutas** | Prohibido terminantemente cablear rutas absolutas de disco (`C:\...`, `/home/...`) o URLs con dominios fijos (`http://localhost:8000/media/...`) en código fuente. | Todo archivo, asset o import debe resolverse de manera relativa o mediante variables de entorno dinámicas (`BASE_DIR / 'media'`). |
| **BP-08** | **Directorio Canónico `backend/media/` para Cargas** | Estandarizar la ubicación de subida para cualquier archivo (firmas, PDFs, evidencias, fotos). | Crear siempre `backend/media/` con `.gitkeep`, montar volumen Docker `./backend/media:/app/media` y exponer mediante `MEDIA_URL = '/media/'` y `MEDIA_ROOT = BASE_DIR / 'media'`. |
| **BP-09** | **Centralización de Endpoints (Cero URLs en Vistas)** | Prohibido terminantemente escribir rutas HTTP quemadas en componentes React o vistas. | Centralizar en `frontend/src/services/endpoints.ts` y registrar en `backend/config/endpoints_registry.json` para validación automatizada en un solo comando. |
| **BP-10** | **Exención de Testing en Modo Mock No-Code** | Prohibido e innecesario exigir pruebas automáticas, Pytest o validadores sobre prototipos de `mock/`. | Los mocks son simulaciones visuales estáticas (HTML/CSS/JS) sin servidor real ni base de datos conectada. El testing aplica exclusivamente a la fase de implementación real en `frontend/` y `backend/`. |
| **BP-11** | **Prohibición de Ciclos `for` Anidados ($O(N^2)$ / $O(N \times M)$)** | Prohibido terminantemente anidar ciclos `for` para cruzar o relacionar colecciones, y ejecutar queries o llamadas API dentro de bucles. | Reemplazar por indexación en memoria con tablas Hash / diccionarios (`dict` / `defaultdict`) con lookup en tiempo constante $O(1)$ (reduciendo complejidad a $O(N + M)$), o resolver el cruce directamente en base de datos (`JOIN`, `prefetch_related`, `annotate`). |
| **BP-12** | **Transaccionalidad Atómica Obligatoria (`transaction.atomic`)** | Prohibido ejecutar mutaciones múltiples dependientes sin control transaccional. | Toda operación de negocio con 2 o más escrituras en base de datos debe envolverse en `with transaction.atomic():` para evitar estados inconsistentes o registros huérfanos. |
| **BP-13** | **Persistencia en Bloque (`bulk_create` / `bulk_update`)** | Prohibido invocar `.save()` o `.create()` individual dentro de bucles para colecciones. | Utilizar operaciones masivas en bloque (`bulk_create(batch_size=500)` y `bulk_update()`) en un único viaje de red SQL. |
| **BP-14** | **Integridad Absoluta de Código (Cero Código Truncado)** | Prohibido truncar código o dejar placeholders tipo `// ... resto del código ...`. | Toda modificación o creación asistida por IA debe entregar el archivo 100% completo, operativo y respetando la lógica previa del módulo. |
| **BP-15** | **Aislamiento Estricto de Entorno (Cero Python Global)** | Prohibido terminantemente ejecutar `pip install` o comandos de Python en el intérprete global del sistema. | Operar exclusivamente dentro del entorno virtual `.venv` (`.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt`). |
| **BP-16** | **Documentación Holística de Capacidades (Cero Changelogs de Micro-Cambios)** | Prohibido redactar bitácoras de cambios puntuales o micro-ediciones. | La carpeta de documentación (`docs/`) y el `README.md` deben documentar a nivel macro cada componente/página realizada, detallando todo lo que realiza la aplicación, su alcance funcional y el destino y visión global de la plataforma. |
| **BP-17** | **Directorio Canónico `pruebas/` en la Raíz (Cero Tests en `backend/`)** | Prohibido terminantemente crear archivos o carpetas de pruebas dentro de `backend/`. | En modo Greenfield, toda suite de pruebas automatizadas (unitarias, integración, endpoints, E2E) debe residir exclusivamente en la carpeta raíz `pruebas/` (`<project-root>/pruebas/`), manteniendo `backend/` completamente limpio. |
| **BP-18** | **Transporte Seguro de Tokens (Cero Tokens de Sesión en URL)** | Prohibido terminantemente usar query params (`?token=`) como método estándar de transporte para sesiones de usuario o llamadas API regulares. | Los tokens de sesión deben transmitirse exclusivamente vía cabecera HTTP `Authorization: Bearer <jwt>` (o `Token <token>`) o Cookies seguras `HttpOnly`. Se admiten solo 2 excepciones auditadas: 1) Fallback controlado para streaming/descargas masivas de reportes o conectores externos (ej. Power BI / Excel en `bi`); 2) Redirecciones de callbacks OAuth2/Azure AD (ej. `tiendita`, `app_tic`), con sanitización inmediata de la URL del navegador vía `window.history.replaceState`. |
| **BP-19** | **Estabilización de Permisos y Roles Desacoplados (Cero Roles Rígidos en Código)** | Prohibido terminarte hardcodear listas de roles en Enums, cablear "Admin/Operador" o preguntar roles rígidos en código. | Implementar tabla propia para roles (`roles` / modelo `Rol`) con `permisos: JSONField`, cruzada con `usuarios` mediante `ManyToManyField`. Compilar permisos en backend mediante el endpoint universal `/api/mis-permisos/`, validar rutas por `permissionKey` (no por nombre de rol) y estabilizar en frontend con sincronización en caliente (`AuthContext` + `RolesAdminSidebar`) sin forzar cierre de sesión. |
| **BP-20** | **Cierre Controlado de Sesión por Token Vencido (Cero Redirecciones Abruptas o Bucles 401)** | Prohibido redirigir bruscamente o dejar la pantalla en blanco ante un token vencido o respuesta 401. | Implementar el motor de doble detección (reactiva por interceptor HTTP 401 que despacha el evento global `session-expired` + proactiva en cliente comparando `Date.now() >= exp * 1000`). Desplegar `SessionExpirationModal` con backdrop blur, bloquear interacción de fondo, purgar de forma idempotente las credenciales y redirigir limpiamente a login preservando la ruta previa. |

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

### 2.2. Entrega JSON Ultra Rápida en FastAPI y Django como Capa de Seguridad
- **FastAPI como capa exclusiva de entrega de datos**: Debe ser **siempre ultra rápido** en la serialización y entrega de respuestas JSON. Para garantizar microsegundos de latencia, se configura `default_response_class=ORJSONResponse` (`orjson>=3.10.0`) junto con **Pydantic v2** (`pydantic>=2.8.0`), omitiendo cualquier overhead de middleware innecesario.
- **Django como capa de seguridad**: Django asume el rol exclusivo de seguridad (autenticación JWT, sesiones seguras, RBAC, permisos de usuario y gobierno del ORM). Los endpoints de datos de FastAPI consumen las validaciones de identidad y permisos garantizadas por Django.
- **Versiones estandarizadas obligatorias**: `fastapi>=0.115.0`, `uvicorn[standard]>=0.30.0`, `pydantic>=2.8.0` y `orjson>=3.10.0`.
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

### 2.4. Prohibición Terminante de Ciclos `for` Anidados (Antipatrón O(N²) y O(N × M))
1. **El Problema**:
   - Anidar bucles `for` (recorrer una colección dentro de otra para cruzar relaciones o buscar coincidencias) degrada drásticamente el rendimiento al disparar una complejidad algorítmica cuadrática o polinomial ($O(N^2)$ o $O(N \times M)$).
   - **Antipatrón Fatal**: Ejecutar consultas SQL/ORM o llamadas HTTP dentro de un ciclo `for` (o ciclos anidados). Esto multiplica de forma inaceptable la latencia y satura el pool de conexiones a la base de datos.
2. **Buenas Prácticas Obligatorias para Evitar Relaciones en Bucles**:
   - **Indexación mediante Diccionarios / Tablas Hash ($O(1)$)**: Convertir la colección secundaria en un mapa hash (`dict` por clave primaria o `defaultdict(list)` por clave foránea). Esto reduce la complejidad global de $O(N \times M)$ a tiempo lineal **$O(N + M)$**, transformando cada búsqueda interna en un acceso instantáneo en tiempo constante $O(1)$.
   - **Uso de Conjuntos (`set`) para Validación de Existencia**: Utilizar `set` para comprobar pertenencia (`if item_id in ids_set`) en tiempo constante $O(1)$ en lugar de buscar dentro de una lista lineal en $O(K)$.
   - **Delegación Directa al Motor de Base de Datos**: Resolver los cruces y agregaciones en la capa de datos (`select_related()`, `prefetch_related()`, `annotate()`, `aggregate()` o `.values()`), aprovechando los índices y optimizaciones de PostgreSQL antes de transferir datos a la memoria de Python.
   - **Comprensiones Directas de Listas y Diccionarios**: Evitar bucles anidados manuales con acumuladores mutables `.append()`; priorizar comprensiones declarativas y limpias.

#### Comparativa Técnica de Código:

❌ **INCORRECTO (Penalizado en auditoría — Ciclo anidado O(N × M) o consultas dentro de bucles)**:
```python
# PÉSIMO RENDIMIENTO: O(N * M) en CPU o saturación si hay consultas internas
resultado = []
for cliente in clientes:
    # Antipatrón fatal si además se hace: Factura.objects.filter(cliente_id=cliente.id)
    for factura in facturas:  # Ciclo dentro de ciclo
        if factura.cliente_id == cliente.id:
            resultado.append({
                "cliente": cliente.nombre,
                "factura": factura.numero,
                "monto": factura.monto
            })
```

✅ **CORRECTO (Estándar SDD — Indexación Hash O(N + M) con Lookup O(1))**:
```python
# ÓPTIMO: Pre-agrupación en diccionario O(M) y búsqueda instantánea O(1)
from collections import defaultdict

facturas_por_cliente = defaultdict(list)
for factura in facturas:
    facturas_por_cliente[factura.cliente_id].append({
        "numero": factura.numero,
        "monto": factura.monto
    })

# Un solo recorrido lineal O(N) sin ciclos anidados
resultado = [
    {
        "cliente": cliente.nombre,
        "facturas": facturas_por_cliente.get(cliente.id, [])
    }
    for cliente in clientes
]
```

✅ **AÚN MEJOR (Delegado en Base de Datos / ORM — 1 Sola Sentencia SQL)**:
```python
# La base de datos resuelve las relaciones de forma nativa e indexada
clientes_con_facturas = (
    Cliente.objects.prefetch_related('facturas')
    .filter(activo=True)
)
```

### 2.5. Transaccionalidad Atómica Obligatoria y Persistencia en Lote (BP-12 y BP-13)
1. **Transacciones Atómicas Obligatorias (`with transaction.atomic():`)**:
   - Toda operación de negocio que involucre dos o más escrituras dependientes en la base de datos (ej. crear factura y sus líneas de detalle, debitar saldo y asentar movimiento, o crear usuario con rol y perfil) debe ejecutarse obligatoriamente dentro de un bloque `transaction.atomic()`.
   - Si se produce una excepción en cualquier paso, se ejecuta un `ROLLBACK` completo automático, impidiendo registros huérfanos o datos corruptos a medio guardar.
2. **Prohibición de `.save()` dentro de Bucles**:
   - Prohibido iterar sobre listas para ejecutar `instancia.save()` o `Model.objects.create()` individualmente. Esto dispara $N$ viajes de ida y vuelta al motor SQL, degradando la latencia y bloqueando transacciones en PostgreSQL.
   - Es obligatorio agrupar en colecciones e invocar `bulk_create(batch_size=500)` o `bulk_update(batch_size=500)`.

#### Comparativa Técnica:

❌ **INCORRECTO (Penalizado en auditoría: escrituras individuales no atómicas)**:
```python
# PÉSIMO: Si falla el ítem 3, la orden queda incompleta y se hicieron 10 transacciones SQL separadas
orden = Orden.objects.create(cliente=cliente, total=total)
for item in items:
    DetalleOrden.objects.create(orden=orden, producto=item.prod, cantidad=item.cant)  # N queries individuales
```

✅ **CORRECTO (Estándar SDD: Atómico y en 1 sola sentencia SQL masiva)**:
```python
from django.db import transaction

with transaction.atomic():
    orden = Orden.objects.create(cliente=cliente, total=total)
    detalles = [
        DetalleOrden(orden=orden, producto=item.prod, cantidad=item.cant)
        for item in items
    ]
    DetalleOrden.objects.bulk_create(detalles, batch_size=500)  # 1 sola query SQL
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
  - Tablas: `.joli-table`, `.table-wrapper-full` de `data_table.md`.
  - Toolbars: `.compact-action-box` (28px) y `.row-actions-group` (26px) de `icon_action_group.md`.
  - Filtros: `.filter-topbar` de `expandable_filter_group.md` y `checklist_popover.md`.
  - Modales: `ConfirmModal` con justificación obligatoria.
  - Paneles: Right Drawer (`.joli-drawer-container`) de `drawer.md`.
  - Colores: `variables.css`.
- **Sanción en Auditoría**: Cualquier archivo CSS huérfano que duplique o ignore los componentes auditados de `.sdd` será penalizado como falta grave de consistencia arquitectónica.

### 3.6. Creación y Edición CRUD Exclusiva en Right Sidebar Drawer (Prohibido Modales)
- **PROHIBICIÓN TERMINANTE**: Queda terminantemente prohibido generar formularios de creación (`+ Nuevo`) o edición (`Editar`) de cualquier CRUD en modales flotantes centrados (`ModalDialog`) o navegando a páginas separadas (`/crear`, `/editar`), a menos que la persona lo pida expresamente.
- **OBLIGATORIEDAD DE RIGHT DRAWER**: Todo formulario de captura, edición y detalle debe operar **exclusivamente desde el panel lateral derecho deslizante** ([`drawer.md`](../components/drawer/drawer.md), `.joli-drawer-container`). Esto preserva el contexto de la tabla en segundo plano, maximiza la ergonomía horizontal y evita la proliferación de modales intrusivos.
- **Uso Exclusivo de Modales**: Los modales centrados quedan reservados estrictamente para confirmaciones (`ConfirmModal`), firmas digitales (`SignatureModal`), lectores biométricos o alerta de sesión expirada.

### 3.7. Agrupación Obligatoria de Botones de Acción en Tablas con Bootstrap (`btn-group`)
- **PROHIBICIÓN TERMINANTE**: Queda terminantemente prohibido dejar botones sueltos o separados por márgenes (`btn me-1`, `btn me-2`) dentro de la celda de acciones/opciones de una tabla.
- **OBLIGATORIEDAD DE BOOTSTRAP `btn-group`**: Siempre que haya 2 o más botones de acción en una fila (ej. Ver en Drawer, Restablecer clave, Anular con ConfirmModal), deben agruparse obligatoriamente dentro de un contenedor `<div class="btn-group btn-group-sm row-actions-group" role="group">...</div>`, unificando las esquinas redondeadas en los extremos y garantizando una altura uniforme de 26px a 28px.

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
- [ ] ¿El código está libre de ciclos `for` anidados ($O(N^2)$ / $O(N \times M)$) y se implementó indexación con diccionarios $O(1)$ o cruces directos en BD (BP-11)?
- [ ] ¿Toda operación compuesta de 2 o más escrituras está blindada con `with transaction.atomic():` (BP-12)?
- [ ] ¿Las inserciones o actualizaciones masivas usan `bulk_create` o `bulk_update` en vez de `.save()` en bucles (BP-13)?
- [ ] ¿El código entregado está 100% completo, sin truncamientos ni comentarios tipo `// ... resto del código ...` (BP-14)?
- [ ] ¿La documentación en `docs/` y el `README.md` describe todo lo que realiza el módulo/aplicación de forma holística, omitiendo micro-cambios y dando contexto del destino de la plataforma (BP-16)?
- [ ] ¿Los archivos y suites de pruebas se ubicaron exclusivamente en la carpeta raíz `pruebas/` y el directorio `backend/` quedó libre de archivos de test (BP-17)?
- [ ] ¿Los tokens de sesión viajan exclusivamente por cabeceras `Authorization` o cookies `HttpOnly` y se sanitiza la URL de inmediato ante callbacks OAuth (BP-18)?
- [ ] ¿Los roles y permisos cuentan con tabla propia (`roles` / `Rol` con `JSONField`) cruzada mediante `ManyToManyField`, validando por `permissionKey` en vez de roles quemados (BP-19)?
- [ ] ¿El vencimiento de tokens se gestiona con doble detección proactiva/reactiva y modal no intrusivo `SessionExpiredModal` con purga total (BP-20)?
- [ ] ¿La sonda `/api/v1/health/` responde HTTP 200 con la latencia de Postgres y Redis?

---

## 6. Decálogo Anti-Caos para Asistentes y Agentes de IA

Para evitar que una Inteligencia Artificial introduzca deuda técnica, rompa código en producción o degrade el rendimiento del ecosistema, **todo modelo o agente de IA que opere sobre este repositorio debe cumplir inflexiblemente el siguiente decálogo**:

1. **Cero Código Truncado (`BP-14`)**:
   - Prohibido reemplazar o generar archivos dejando comentarios del tipo `// ... resto del código ...` o `# [Mantener funciones anteriores]`. Todo archivo o bloque editado debe conservar el 100% de su funcionalidad y contexto sin omisiones destructivas.
2. **Aislamiento Total del Entorno (`BP-15`)**:
   - NUNCA ejecutar comandos `pip install` o `python` en el intérprete global del anfitrión. Las ejecuciones deben realizarse únicamente invocando el binario del entorno virtual local (`.\.venv\Scripts\python.exe`).
3. **Transaccionalidad Atómica Innegociable (`BP-12`)**:
   - Si una operación crea o modifica múltiples tablas relacionadas, debe envolverse obligatoriamente en `with transaction.atomic():`. Cero registros huérfanos ante excepciones imprevistas.
4. **Persistencia en Bloque vs Bucles Lentos (`BP-13`)**:
   - Prohibido llamar a `.save()` o `.create()` individual dentro de bucles `for`. Usar siempre `bulk_create` o `bulk_update` por lotes (`batch_size=500`).
5. **Cero Ciclos `for` Anidados ($O(N^2)$) (`BP-11`)**:
   - Prohibido iterar colecciones dentro de bucles para cruzar relaciones o buscar coincidencias. Emplear diccionarios de búsqueda rápida Hash ($O(1)$) o resolver el cruce directamente en el motor de base de datos con SQL (`JOIN` / `prefetch_related`).
6. **Prohibición de CSS Inventado**:
   - Prohibido inventar archivos CSS (`custom.css`, `module.css`) o selectores ad-hoc con colores hexadecimales fijos. Reutilizar estrictamente los componentes auditados de `.sdd/components/` y las variables de diseño de `variables.css`.
7. **Diseño 100% Horizontal (Prohibido Centrar Pantallas)**:
   - Prohibido centrar dashboards o tablas masivas con contenedores estrechos (`max-w-xl mx-auto`). Toda interfaz debe ocupar el 100% del ancho de la pantalla (`w-full`) para maximizar la legibilidad de columnas y datos.
8. **Rutas 100% Relativas y Centralizadas (`BP-07` y `BP-09`)**:
   - Cero URLs fijas (`http://localhost:8000`) o rutas absolutas de Windows/Linux (`C:\Users\...`). Las rutas se resuelven relativamente con `BASE_DIR` en backend y se centralizan en `endpoints.ts` en frontend.
9. **Tipado Estricto (Prohibido `any` en TypeScript)**:
   - No ocultar errores de tipado con `any`. Definir contratos rigurosos de interfaces en TypeScript, esquemas de validación Zod en cliente y esquemas Pydantic v2 en FastAPI.
10. **Cero Alucinación de Librerías o Métodos**:
    - Usar exclusivamente las dependencias aprobadas en `requirements.txt` y `package.json`. No asumir métodos inexistentes de frameworks; verificar siempre contra la sintaxis oficial y documentada.
11. **Documentación Viva de Capacidades y Destino de la Plataforma (`BP-16`)**:
    - Prohibido redactar bitácoras de cambios puntuales ("se agregó campo x"). Documentar todo lo que realiza la aplicación por módulo en `docs/` y mantener actualizado el `README.md` con el alcance global y visión destino del software.
12. **Ubicación Exclusiva de Pruebas en `pruebas/` (`BP-17`)**:
    - NUNCA crear archivos o carpetas de pruebas dentro de `backend/`. En modo Greenfield, toda suite de pruebas debe crearse y ejecutarse estrictamente en la carpeta `pruebas/` en la raíz del proyecto (`<project-root>/pruebas/`), manteniendo limpio el código de producción.
13. **Seguridad Absoluta de Tokens (`BP-18`)**:
    - Prohibido transmitir tokens de sesión en query params (`?token=`). Utilizar cabeceras `Authorization` o cookies `HttpOnly`. Si se recibe un token por redirección OAuth/SSO, el frontend debe sanitizar la URL inmediatamente con `window.history.replaceState`.
14. **Estabilización de Permisos Desacoplada (`BP-19`)**:
    - Prohibido preguntar qué roles fijos tiene una plataforma o quemar Enums de roles. Implementar la tabla `roles` con `JSONField` cruzada por `ManyToManyField` con `usuarios`, compilando mediante `/api/mis-permisos/` y validando por `permissionKey`.
15. **Cierre Controlado por Token Vencido (`BP-20`)**:
    - Prohibido dejar la pantalla en blanco o redirigir bruscamente ante errores 401 o token expirado. Implementar la doble detección proactiva/reactiva con `SessionExpiredModal`, purga limpia de almacenamiento y redirección controlada preservando el contexto.






