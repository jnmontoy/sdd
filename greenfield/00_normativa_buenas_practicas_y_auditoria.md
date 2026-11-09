# Normativa de buenas prácticas de ingeniería (BP-01 a BP-23)

Esta es la **fuente única** de las buenas prácticas del SDD. Los demás documentos citan el código (por ejemplo, "BP-12") en lugar de copiar la regla.

> **Origen:** reúne los criterios que se revisaron en las auditorías de los proyectos internos (buenas prácticas, pruebas de penetración OWASP, endpoints, dependencias y contenedores Docker). Cada regla se justifica con la práctica de industria correspondiente, no con el proyecto donde se detectó.

## Cómo leer las reglas

| Palabra | Significado |
| :--- | :--- |
| **DEBE / NO DEBE** | Obligatorio. Incumplirlo es un hallazgo de auditoría. Se reserva para seguridad e integridad de datos. |
| **DEBERÍA / NO DEBERÍA** | Recomendado. Se puede desviar si la razón queda registrada en un ADR (`memory/adrs/`) o si el usuario lo pide expresamente. |
| **PUEDE** | Opcional. |

Cada regla trae su **por qué**. Si el por qué no aplica a su caso, documente la excepción en lugar de forzar la regla.

---

## 1. Resumen

| Código | Tema | Nivel |
| :--- | :--- | :--- |
| BP-01 | Secretos y `DEBUG` por ambiente | DEBE |
| BP-02 | Hosts permitidos explícitos | DEBE |
| BP-03 | CORS restringido | DEBE |
| BP-04 | Limitación de tasa | DEBE |
| BP-05 | Denegar por defecto | DEBE |
| BP-06 | Cabeceras HTTP y cookies seguras | DEBE |
| BP-07 | Sin rutas absolutas ni URLs fijas | DEBE |
| BP-08 | Carpeta `backend/media/` para archivos subidos | DEBERÍA |
| BP-09 | Registro centralizado de endpoints | DEBERÍA |
| BP-10 | Los prototipos (mock) no llevan pruebas automatizadas | — |
| BP-11 | Sin cruces cuadráticos ni consultas dentro de ciclos | DEBE / DEBERÍA |
| BP-12 | Transacciones atómicas | DEBE |
| BP-13 | Escrituras en lote | DEBERÍA |
| BP-14 | Código completo, sin truncar | DEBE |
| BP-15 | Dependencias aisladas en `.venv` | DEBE |
| BP-16 | Documentación del estado actual del sistema | DEBERÍA |
| BP-17 | Ubicación de las pruebas | DEBERÍA |
| BP-18 | Transporte y almacenamiento de tokens | DEBE |
| BP-19 | Roles y permisos en datos, no en código | DEBE / DEBERÍA |
| BP-20 | Vencimiento de sesión controlado | DEBE |
| BP-21 | Cambios de nivel 2 con propuesta y evidencia | DEBERÍA |
| BP-22 | Memoria de decisiones y errores conocidos | DEBERÍA |
| BP-23 | Archivos de tamaño manejable: desacoplar en componentes y funciones | DEBERÍA |

---

## 2. Seguridad y configuración (BP-01 a BP-09)

Implementación de referencia: [`stack/settings_security_template.py`](../stack/settings_security_template.py).

**BP-01. Secretos y `DEBUG`.** `DEBUG` NO DEBE estar activo en producción. Los secretos (`SECRET_KEY`, credenciales de BD, claves de API) NO DEBEN estar en el código ni en archivos versionados: se leen de variables de entorno. Con `DEBUG=False`, si falta `SECRET_KEY` la aplicación DEBE negarse a arrancar.
*Por qué:* `DEBUG=True` muestra trazas con variables y configuración; un secreto en git queda en el historial aunque se borre después.

**BP-02. Hosts permitidos.** `ALLOWED_HOSTS` NO DEBE contener `'*'` en producción; se lee de la variable de entorno como lista explícita.
*Por qué:* evita ataques de cabecera `Host` (envenenamiento de enlaces de restablecimiento y de caché).

**BP-03. CORS.** `CORS_ALLOW_ALL_ORIGINS` NO DEBE ser `True`. Los orígenes se listan en `CORS_ALLOWED_ORIGINS`. Ese ajuste no acepta comodines: para subdominios se usa `CORS_ALLOWED_ORIGIN_REGEXES`. Con credenciales (`CORS_ALLOW_CREDENTIALS=True`) el origen nunca puede ser `*`, y esto aplica también a FastAPI.
*Por qué:* con CORS abierto y cookies, cualquier sitio puede hacer peticiones autenticadas en nombre del usuario.

**BP-04. Limitación de tasa.** El login, el restablecimiento de contraseña y las APIs DEBEN tener límites de peticiones respaldados en Redis, compartidos entre procesos, y responder `429` con `Retry-After`. Valores iniciales sugeridos y configurables: login 5/min, recuperación 3/min, anónimos 30/min, autenticados 120/min.
*Por qué:* frena la fuerza bruta y el abuso. Si el contador vive en la memoria de un proceso, cada réplica tiene el suyo y el límite real se multiplica.

**BP-05. Denegar por defecto.** Todo endpoint DEBE requerir autenticación salvo que se declare público de forma explícita (login, refresh, restablecimiento, `/health/*`). En DRF: `IsAuthenticated` como permiso por defecto. En FastAPI: routers con `dependencies=[Depends(usuario_actual)]`.
*Por qué:* un endpoint nuevo que se olvida de proteger queda cerrado, no abierto.

**BP-06. Cabeceras y cookies.** DEBE enviarse `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy` y HSTS en producción. Las cookies de sesión y de refresh DEBEN ser `HttpOnly`, `Secure` (en HTTPS) y `SameSite=Lax` o `Strict`. La cookie `csrftoken` NO es `HttpOnly`, porque la SPA debe leerla para enviar `X-CSRFToken`. `SECURE_BROWSER_XSS_FILTER` no se usa: Django lo retiró y los navegadores ignoran esa cabecera.
*Por qué:* evita el clickjacking y la interpretación errónea de tipos de archivo, y que JavaScript lea las credenciales.

**BP-07. Rutas y URLs.** El código NO DEBE contener rutas absolutas de disco (`C:\...`, `/home/...`) ni URLs fijas de servidores. Backend: `BASE_DIR / "media"`. Frontend: base desde `VITE_API_URL` y rutas desde `ENDPOINTS`.
*Por qué:* el mismo código debe correr en cualquier equipo, contenedor y ambiente.

**BP-08. Archivos subidos.** Los archivos subidos DEBERÍAN guardarse bajo `MEDIA_ROOT = BASE_DIR / "media"` (`backend/media/` con `.gitkeep`) y montarse como volumen en Docker. Los archivos sensibles (firmas, documentos de identidad) NO DEBEN servirse por URL pública adivinable: se entregan por una vista que verifica permisos. Ver [`model/archivos/`](../model/archivos/spec_model_archivos_media.md).

**BP-09. Endpoints centralizados.** Las vistas de React NO DEBERÍAN escribir rutas HTTP: las importan de `frontend/src/services/endpoints.ts`. Cada endpoint se declara también en `backend/config/endpoints_registry.json`, que usa el [validador](../stack/validate_endpoints.py).
*Por qué:* un cambio de ruta se hace en un solo lugar y la validación automática sabe qué probar.

---

## 3. Calidad del código (BP-10 a BP-17)

**BP-10. Prototipos.** Los prototipos en `mock/` (HTML/CSS/JS estático, sin servidor) no llevan pruebas automatizadas ni validación de endpoints. Las pruebas empiezan cuando el prototipo aprobado se implementa en `frontend/` y `backend/`.
*Por qué:* un prototipo es descartable y sirve para validar la pantalla y el contrato de datos con el negocio; probarlo no reduce ningún riesgo.

**BP-11. Cruces de colecciones y consultas en ciclos.**
- NO DEBE ejecutarse una consulta a la BD ni una llamada HTTP dentro de un ciclo que recorre datos (el problema N+1). DEBE precargarse en lote (`filter(id__in=...)`, `select_related`, `prefetch_related`).
- NO DEBERÍA cruzarse dos colecciones con ciclos anidados cuando su tamaño depende de los datos. Se indexa una en un diccionario (`dict`/`defaultdict`) y el costo baja de O(N×M) a O(N+M), o se resuelve en SQL (`JOIN`, `annotate`).
- *Excepción:* ciclos anidados sobre conjuntos pequeños y de tamaño fijo (por ejemplo 7 días × 3 turnos) son legibles y no tienen costo apreciable.
*Por qué:* con 1 000 clientes y 10 000 facturas, el cruce anidado hace 10 millones de comparaciones; el indexado, 11 000.

```python
from collections import defaultdict

facturas_por_cliente = defaultdict(list)
for f in facturas:                                # O(M)
    facturas_por_cliente[f.cliente_id].append(f)
resultado = [                                     # O(N)
    {"cliente": c.nombre, "facturas": facturas_por_cliente.get(c.id, [])}
    for c in clientes
]
# Mejor aún, si las relaciones están en el ORM:
clientes = Cliente.objects.filter(activo=True).prefetch_related("facturas")
```

Para N+1 en Django:
- `select_related()` para claves foráneas y uno a uno (un `JOIN`).
- `prefetch_related()` para muchos a muchos y relaciones inversas (una consulta adicional por relación, no por fila).
- `.only()` o `.values()` cuando se necesitan pocas columnas.
- En las pruebas, `django_assert_max_num_queries` fija el número máximo de consultas de cada listado.

**BP-12. Transacciones atómicas.** Una operación de negocio con dos o más escrituras dependientes DEBE ejecutarse dentro de `transaction.atomic()`.
*Por qué:* si falla un paso, se revierte todo y no quedan registros huérfanos ni a medias.

```python
from django.db import transaction

with transaction.atomic():
    orden = Orden.objects.create(cliente=cliente, total=total)
    DetalleOrden.objects.bulk_create(
        [DetalleOrden(orden=orden, producto=i.producto, cantidad=i.cantidad) for i in items],
        batch_size=500,
    )
```

**BP-13. Escrituras en lote.** Para insertar o actualizar colecciones DEBERÍA usarse `bulk_create`/`bulk_update` (con `batch_size`) en lugar de `.save()` dentro de un ciclo.
*Por qué:* una consulta por lote en vez de una por fila.
*Atención:* `bulk_create` y `bulk_update` no llaman a `save()`, no emiten señales (`pre_save`/`post_save`) y no ejecutan `full_clean()`. Si el modelo depende de eso, como auditoría por señales o campos calculados en `save()`, valide antes o use `save()` dentro de la transacción y justifíquelo.

**BP-14. Código completo.** Ningún cambio, humano o de IA, DEBE dejar código truncado ni marcadores como `// ... resto del código ...`.
*Por qué:* el código omitido se pierde al guardar el archivo.

**BP-15. Entorno virtual.** Las dependencias de Python NO DEBEN instalarse en el intérprete global: se instalan en `.venv` en la raíz del proyecto y se invocan con su ejecutable (`.\.venv\Scripts\python.exe -m pip ...` en Windows, `./.venv/bin/python -m pip ...` en Linux/macOS). El Python del sistema PUEDE usarse para crear el `.venv` o ejecutar scripts que solo usan la librería estándar, como `init_project.py`.
*Por qué:* las instalaciones globales mezclan versiones entre proyectos y hacen que "en mi equipo funciona" no se pueda reproducir.

**BP-16. Documentación.** `README.md` y `docs/` DEBERÍAN describir el **estado actual** del sistema: qué hace cada módulo, su alcance, cómo se ejecuta y hacia dónde va la plataforma. El historial de cambios vive en git y en un `CHANGELOG.md` por versión (ver [protocolo 06](./06_protocolo_devops_cicd_y_calidad.md)), no en la documentación funcional.
*Por qué:* una documentación hecha de bitácoras ("se agregó el campo X") obliga a reconstruir el estado leyendo la historia.

**BP-17. Ubicación de las pruebas.**
- Backend: `pruebas/unitarias/`, `pruebas/integracion/` y `pruebas/e2e/` en la raíz del proyecto, con `pytest.ini` (`testpaths = pruebas`, `pythonpath = backend`). NO DEBERÍAN crearse pruebas dentro de `backend/`.
- Frontend: las pruebas de componentes y hooks van junto al archivo (`X.test.tsx`), según la convención de Vite/Vitest.
*Por qué:* la imagen de producción del backend se construye solo con `backend/` y queda sin código de pruebas, y todas las pruebas de Python se ejecutan con un solo `pytest` desde la raíz. Detalle en el [protocolo 11](./11_protocolo_pruebas_automaticas_y_testing_e2e.md).

---

## 4. Sesión, permisos y proceso (BP-18 a BP-23)

**BP-18. Tokens.**
- El **access token** (JWT, de vida corta) DEBE vivir solo en memoria (estado del `AuthContext` o del cliente HTTP) y enviarse en `Authorization: Bearer <token>`.
- El **refresh token** DEBE viajar en una cookie `HttpOnly; Secure; SameSite=Lax` limitada a `/api/v1/auth/`. Se rota en cada uso y el anterior va a una lista negra.
- Ningún token DEBE guardarse en `localStorage` ni en `sessionStorage`, ni viajar en la URL (`?token=`).
- Al cargar la página, la app llama a `/api/v1/auth/refresh/` para recuperar la sesión.
- *Excepciones auditadas:* (1) el retorno de SSO OAuth2 puede traer un código o token en la URL; el frontend DEBE canjearlo de inmediato y limpiar la URL con `history.replaceState`. (2) Las descargas que el navegador abre directamente o los conectores externos (por ejemplo Power BI) PUEDEN usar un token de un solo uso, de vida muy corta y con alcance limitado a ese recurso.
*Por qué:* cualquier script inyectado (XSS) puede leer `localStorage`, pero no puede leer una cookie `HttpOnly`. Los tokens en la URL quedan en el historial, en los logs del servidor y en la cabecera `Referer`.

> **Origen de las excepciones:** conectores de reportes y SSO con Microsoft 365 usados en proyectos internos.

**BP-19. Roles y permisos.**
- Las decisiones de acceso NO DEBEN depender de nombres de rol escritos en el código (`if rol == "Admin"`); DEBEN depender de claves de permiso (`ventas.ver`, `usuarios.editar`).
- Los roles DEBERÍAN estar en una tabla propia (`Rol`, con sus permisos) relacionada con usuarios por muchos a muchos. El backend expone los permisos efectivos en `GET /api/v1/mis-permisos/` y el frontend protege rutas y botones por clave de permiso.
- Un cambio de permisos DEBERÍA reflejarse sin obligar a cerrar sesión: el `AuthContext` vuelve a consultar los permisos.
- Modelo: [`model/roles/`](../model/roles/spec_model_roles_permisos.md).
*Por qué:* agregar un rol o mover un permiso se vuelve un cambio de datos, no de código.

**BP-20. Vencimiento de sesión.** Ante un token vencido o una respuesta 401, la app NO DEBE quedar en blanco ni entrar en un bucle de redirecciones. Lo que sí debe hacer:
- Reactiva: el interceptor HTTP intenta **un** refresh (las peticiones simultáneas esperan ese mismo intento) y, si falla, emite el evento `session-expired`.
- Proactiva: el cliente lee el `exp` del access token en memoria y renueva antes de que venza.
- Muestra el `SessionExpirationModal` bloqueante, limpia el estado de sesión y redirige al login conservando la ruta de regreso.

Componentes: [`context/auth_context.md`](../components/context/auth_context.md), [`services/api_client.md`](../components/services/api_client.md), [`modal/session_expiration_modal.md`](../components/modal/session_expiration_modal.md).

**BP-21. Cambios de nivel 2.** Una funcionalidad incremental o un refactor (nivel 2) DEBERÍA tener su carpeta `specs/changes/AAAA-MM-DD-nombre/` con `proposal.md`, `design.md`, `tasks.md` y `evidence.md`. No se da por terminado sin la salida real de las pruebas en `evidence.md`. Ver [protocolo 14](./14_protocolo_cambios_atomicos_y_especificaciones_vivas.md).
*Por qué:* queda escrito qué se decidió, qué quedó fuera y con qué evidencia se cerró.

**BP-22. Memoria del proyecto.** Antes de un cambio relevante DEBERÍAN revisarse `memory/adrs/` (decisiones vigentes) y `memory/learnings/` (convenciones y errores ya resueltos). Un error difícil de diagnosticar se registra en `memory/learnings/bug_lessons.md`. Ver [protocolo 15](./15_protocolo_memoria_persistente_y_aprendizaje_agentes.md).

**BP-23. Archivos de tamaño manejable.** Ningún archivo DEBERÍA crecer hasta volverse inmanejable. Cuando se acerca al límite, se desacopla: en el frontend, en componentes, hooks y hojas de estilo por componente; en el backend, en funciones y módulos por responsabilidad.

| Tipo de archivo | Aviso (planear la división) | Límite (dividir antes de agregar más) |
| :--- | :--- | :--- |
| Componente o vista React (`.tsx`) | 300 líneas | 500 líneas |
| Hook, servicio o utilidad (`.ts`) | 300 líneas | 500 líneas |
| Hoja de estilos (`.css`) | 500 líneas | 800 líneas |
| Módulo Python (router, servicio, esquemas, modelos) | 400 líneas | 600 líneas |
| Función o método | 50 líneas | 80 líneas |

Cómo se aplica:
- **Antes de agregar código** a un archivo que ya pasó el límite, primero se extrae una parte (la que se va a tocar, como mínimo). No se suman líneas a un archivo que ya está por encima.
- **Frontend.** Una vista se divide en componentes hijos con su propio archivo (`Usuarios/TablaUsuarios.tsx`, `Usuarios/FiltrosUsuarios.tsx`); la lógica con estado sale a hooks (`useUsuarios.ts`); los estilos van junto al componente (`TablaUsuarios.css`) o en hojas por área importadas desde un índice, nunca en una sola hoja global gigante. Un servicio de API se divide por dominio (`services/api/usuarios.ts`, `services/api/clientes.ts`) con un índice que reexporta, para no romper importaciones.
- **Backend.** Un router grande pasa a ser un paquete por dominio (`routers/mensajes/__init__.py`, `conversaciones.py`, `adjuntos.py`); la lógica de negocio sale de los endpoints a funciones de servicio (`servicios/mensajes.py`) que se pueden probar solas; los esquemas y modelos se agrupan por dominio en módulos que el `__init__.py` reexporta.
- **Sin cambio de comportamiento.** Dividir es un refactor: las rutas, los nombres exportados, las clases CSS y los contratos quedan iguales, y las pruebas existentes DEBEN pasar antes y después.
- **Excepciones**: archivos generados (tipos de OpenAPI, migraciones, registros JSON), datos estáticos y archivos de terceros no cuentan.

*Por qué:* un archivo de miles de líneas no cabe en la cabeza de una persona ni en el contexto de un asistente de IA. Cada cambio obliga a leer de más, los conflictos de git se multiplican, los estilos y funciones se pisan sin que se note y los errores se esconden. Dividir cuando el archivo crece es barato; dividirlo cuando ya tiene miles de líneas es un proyecto en sí mismo.

---

## 5. Backend: prácticas complementarias

### 5.1. Errores sin fugas de información
Las respuestas de error NO DEBEN incluir trazas, SQL, nombres de tablas ni rutas internas. Se responde con un contrato estable y un identificador de correlación que permite buscar el detalle en los logs:

```json
{
  "status": "error",
  "error_code": "ERR_DATABASE_UNAVAILABLE",
  "message": "En este momento no es posible procesar la solicitud. Intente nuevamente en unos minutos.",
  "correlation_id": "c8b417ef-5769-42b8-935a-4933a30c5e7b"
}
```

### 5.2. Django y FastAPI
La división de responsabilidades (Django para seguridad y escrituras, FastAPI para lecturas de alto volumen), con sus costos, está en [`stack/asgi_hybrid_architecture.md`](../stack/asgi_hybrid_architecture.md) y en el [ADR 0001](../memory/adrs/0001_arquitectura_hibrida_fastapi_django.md). Conexiones persistentes a PostgreSQL: `CONN_MAX_AGE` con `CONN_HEALTH_CHECKS = True`.

---

## 6. Frontend: convenciones de interfaz

Estas reglas dan consistencia entre aplicaciones. Son **DEBERÍA**: se pueden desviar con una razón registrada o a pedido del usuario.

> **Origen:** patrones de las aplicaciones internas de gestión, centradas en tablas y uso diario en monitores de escritorio.

**6.1. Tokens de diseño.** Los colores, espaciados, radios y fuentes DEBERÍAN venir de [`variables.css`](../components/variables.css) (`var(--...)`). NO DEBERÍAN escribirse colores hexadecimales en los componentes.
*Por qué:* el modo noche/día y un cambio de marca se resuelven en un solo archivo.

**6.2. Reutilizar componentes.** Antes de crear estilos o componentes nuevos se DEBERÍA usar el [catálogo](../components/README.md): tablas (`data_table.md`), barras de acciones (`icon_action_group.md`), filtros (`expandable_filter_group.md`), drawer (`drawer.md`), modales (`confirm_modal.md`), selectores (`select_filter.md`) y campos de formulario (`floating_field.md`). Si hace falta un estilo nuevo, se escribe con tokens y, si sirve a más de un proyecto, se propone para el catálogo.
*Por qué:* cada CSS ad-hoc crea otra variante que se debe mantener, probar en ambos temas y revisar en accesibilidad.

**6.3. Pantallas a todo el ancho.** Las vistas de trabajo (tablas, tableros, módulos) DEBERÍAN ocupar el ancho disponible, sin contenedores angostos centrados (`max-width` de lectura más `margin: auto`). Se centran los modales y la tarjeta de login. Los textos largos de lectura PUEDEN limitar su ancho de línea dentro del layout completo.
*Por qué:* las tablas con muchas columnas son el uso principal; un contenedor angosto obliga a desplazarse en horizontal y deja espacio vacío.

**6.4. CRUD en drawer.** Crear y editar registros DEBERÍA hacerse en el panel lateral derecho ([`drawer.md`](../components/drawer/drawer.md), 560 px o 720 px para formularios largos). Los modales se reservan para confirmaciones, firmas, escáneres y sesión vencida. Un formulario de muchos pasos o de pantalla completa PUEDE ir en una página propia, registrando la razón.
*Por qué:* la tabla sigue visible como contexto y el usuario no pierde su lugar.

**6.5. Acciones de fila agrupadas.** Dos o más botones en una fila DEBERÍAN ir en un grupo con `role="group"` y `aria-label` (en el panel: `div.row-actions-group` con botones `action-btn` de 30 × 28, ver [`admin_table_screen.md`](../components/data_table/admin_table_screen.md) §4.7), con altura uniforme de 26 a 28 px. Los botones de solo ícono DEBEN tener `aria-label` y `title`. Con más de tres acciones secundarias, se agrupan en un menú desplegable.

**6.6. Paginador arriba y al pie.** El paginador DEBERÍA ir en la barra superior de la tabla (solo botones, junto a las acciones) y, completo, al pie de la tarjeta (selector de registros por página, resumen "Mostrando 1 a 10 de 150" y botones). Ver [`admin_table_screen.md`](../components/data_table/admin_table_screen.md) §3.
*Por qué:* el usuario ve cuántos registros hay y navega sin bajar hasta el final de la tabla.

**6.7. Rendimiento en React.** `useMemo` y `useCallback` se usan cuando una medición o una lista grande lo justifican, no por defecto. Los efectos con temporizadores, suscripciones o peticiones DEBEN limpiarse (`return () => ...` y `AbortController`). Los formularios DEBERÍAN validar con errores en línea (`aria-invalid` + mensaje bajo el campo); React Hook Form + Zod es la opción recomendada en proyectos nuevos. *(Referencia: `validarUsuario()` + `p.drawer-field-error` en el drawer de usuario de Pandora, ver [`drawer.md`](../components/drawer/drawer.md) §1.2.)*

**6.8. Almacenamiento del navegador.** `localStorage` solo guarda preferencias no sensibles (tema, anchos y visibilidad de columnas, documento recordado si el usuario lo marcó), con claves que llevan el slug de la app (`<app>:theme`, o `<app>_<modulo>_...` en las preferencias de tablas y drawers, ver [`admin_table_screen.md`](../components/data_table/admin_table_screen.md) §7) y acceso envuelto en `try/catch`.

**6.9. Campos de captura con etiqueta flotante; filtros y buscadores sin ella.** Todo formulario donde el usuario captura datos (login, recuperar o cambiar contraseña, crear o editar registros) DEBERÍA usar el campo con etiqueta flotante de [`floating_field.md`](../components/form/floating_field.md) en sus inputs, selects (nativos y propios) y textareas, en web y en apps React Native: la etiqueta hace de placeholder y, con foco o valor, sube animada (220 ms) al borde superior y lo corta. Los **buscadores, filtros de tablas, barras de herramientas, cuadros de chat y campos de solo consulta NO DEBERÍAN usarlo**: conservan su estilo. Las etiquetas van con mayúscula inicial solamente y siguen siendo una `<label>` real (o `accessibilityLabel` en React Native), nunca solo un placeholder.
*Por qué:* da presencia y orden a los formularios sin ocupar una fila extra por etiqueta; en filtros y buscadores, que se usan a cada rato, sería intrusivo. Un solo componente evita que cada pantalla invente su propio campo.

---

## 7. Contenedores e infraestructura

Plantillas: [`stack/`](../stack/README.md).

1. Las imágenes de producción DEBEN ejecutarse con un usuario sin privilegios, no `root`.
2. Las imágenes base DEBERÍAN ser ligeras y estar fijadas a una versión mayor (`python:3.12-slim`, `node:20-alpine`).
3. `.dockerignore` DEBE excluir `.git`, `.env`, `node_modules`, `.venv`, `__pycache__` y los logs.
4. `db`, `redis` y `backend` DEBERÍAN tener `healthcheck`. El backend expone `GET /health/live` y `GET /health/ready`.
5. Los datos DEBEN vivir en volúmenes con nombre (`postgres_data`, `redis_data`, `media_volume`).
6. En producción, PostgreSQL y Redis NO DEBEN publicar puertos hacia fuera de la red de contenedores.

---

## 8. Lista de verificación antes de entregar

- [ ] `.env` está en `.gitignore` y existe `.env.example` sin secretos (BP-01).
- [ ] `ALLOWED_HOSTS` y CORS son listas explícitas (BP-02, BP-03).
- [ ] El login y la recuperación tienen límite de tasa (BP-04).
- [ ] Todo endpoint nuevo es privado salvo declaración explícita y figura en el registro y en `endpoints.ts` (BP-05, BP-09).
- [ ] Las cabeceras de seguridad están activas y las cookies de sesión/refresh son `HttpOnly` (BP-06).
- [ ] No hay rutas absolutas ni URLs fijas (BP-07).
- [ ] No hay consultas dentro de ciclos; los listados tienen un máximo de consultas probado (BP-11).
- [ ] Las escrituras dependientes van en `transaction.atomic()` (BP-12).
- [ ] Ningún token está en `localStorage`, `sessionStorage` ni en la URL (BP-18).
- [ ] Los permisos se validan por clave, no por nombre de rol (BP-19).
- [ ] Un 401 termina en el modal de sesión vencida, sin bucles (BP-20).
- [ ] Las pruebas pasan: `pytest`, `npm test`, `npm run typecheck`, y `pruebas/validate_endpoints.py` con la app levantada.
- [ ] `pip-audit` y `npm audit --audit-level=high` sin hallazgos altos ni críticos.
- [ ] La interfaz usa tokens y componentes del catálogo, y es accesible por teclado (sección 6).
- [ ] Los formularios de captura usan la etiqueta flotante y los filtros y buscadores no (6.9).
- [ ] `README.md` y `docs/` describen el estado actual (BP-16).
- [ ] Ningún archivo tocado supera el límite de líneas de su tipo; si ya lo superaba, se extrajo al menos la parte modificada (BP-23).

---

## 9. Reglas para asistentes de IA

Las reglas operativas para agentes (Claude Code, Cursor, Copilot) están resumidas en [`stack/agent_harness/AGENTS.md`](../stack/agent_harness/AGENTS.md), que `init_project.py` copia a cada proyecto. Ese archivo cita estos códigos BP y no los redefine.
