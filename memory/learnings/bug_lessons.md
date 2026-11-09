# Lecciones aprendidas de errores (catálogo para no repetirlos)

> **Propósito**: registrar cada error que costó más de un intento corregir, con su causa raíz y la regla que evita que vuelva a ocurrir.
> Las entradas BUG-001 a BUG-013 son **lecciones genéricas del stack del SDD** (Django + FastAPI + React) que sirven de ejemplo y punto de partida. Cada proyecto agrega las suyas a continuación.

**Formato de cada entrada**: síntoma (lo que se ve), causa raíz (por qué pasa), solución, regla preventiva (DEBE / DEBERÍA) y, si aplica, la buena práctica relacionada de la normativa 00.

---

## Índice
* [BUG-001: Conexiones a PostgreSQL agotadas en rutas FastAPI](#bug-001)
* [BUG-002: Consultas N+1 en serializadores o bucles](#bug-002)
* [BUG-003: Pantallas centradas y angostas por contenedores con ancho máximo](#bug-003)
* [BUG-004: `.save()` dentro de bucles masivos](#bug-004)
* [BUG-005: Rutas absolutas del sistema operativo en el código](#bug-005)
* [BUG-006: ORM de Django llamado desde `async def`](#bug-006)
* [BUG-007: Formularios CRUD en modal centrado en lugar del drawer](#bug-007)
* [BUG-008: Barra final en la ruta: la redirección 307 pierde la sesión detrás de un proxy](#bug-008)
* [BUG-009: Recarga automática de uvicorn colgada por WebSockets abiertos](#bug-009)
* [BUG-010: `text-overflow: ellipsis` no aparece en elementos `flex`](#bug-010)
* [BUG-011: Salud de un servicio remoto medida con el costo de conectar](#bug-011)
* [BUG-012: Avisos (sonner) de distinto tamaño al apilarse](#bug-012)
* [BUG-013: La URL conserva la última sección después de cerrar sesión](#bug-013)
* [BUG-014: Guardar sin conexión que igual espera la red (app móvil)](#bug-014)
* [BUG-015: Con señal débil la app «carga» aunque tenga los datos guardados](#bug-015)
* [BUG-016: Guardado doble por llamar a la API dentro de setState(prev => …)](#bug-016)
* [BUG-019: En FastAPI reciente, app.routes no lista las rutas de los routers incluidos](#bug-019)
* [BUG-020: Menú que muestra todo cuando la consulta de permisos falla](#bug-020)

---

### <a id="bug-001"></a> BUG-001: Conexiones a PostgreSQL agotadas en rutas FastAPI
* **Síntoma**: tras horas de uso, las rutas `/fast/` fallan con `OperationalError: remaining connection slots are reserved` o con conexiones cerradas por el servidor.
* **Causa raíz**: Django recicla conexiones al recibir las señales `request_started` / `request_finished`. Las rutas de FastAPI montadas en el mismo proceso ASGI no disparan esas señales, y FastAPI ejecuta las funciones `def` en un pool de hilos; cada hilo conserva su propia conexión.
* **Solución**: dependencia (o middleware) de FastAPI que llame a `django.db.close_old_connections()` antes y después de cada petición, y `CONN_MAX_AGE` acotado.
* **Regla**: todo router de FastAPI que use el ORM de Django DEBE incluir esa dependencia.

---

### <a id="bug-002"></a> BUG-002: Consultas N+1 en serializadores o bucles
* **Síntoma**: una tabla de 500 filas ejecuta 501 consultas SQL y tarda segundos.
* **Causa raíz**: acceder a una relación (`registro.usuario.nombre`) dentro de un bucle o serializador sin haberla precargado: 1 consulta para la lista + 1 por fila.
* **Solución**: `select_related()` para ForeignKey/OneToOne, `prefetch_related()` para relaciones múltiples, o `.values('id', 'nombre', 'usuario__nombre')`.
* **Regla (BP-11)**: NO DEBEN ejecutarse consultas dentro de bucles; las relaciones se precargan. Verificar con `django-debug-toolbar` en desarrollo o con `assertNumQueries` en pruebas.

---

### <a id="bug-003"></a> BUG-003: Pantallas centradas y angostas por contenedores con ancho máximo
* **Síntoma**: la vista se dibuja como una columna estrecha en el centro, con grandes márgenes vacíos en monitores anchos.
* **Causa raíz**: contenedores con `max-width` pequeño y `margin: auto` (p. ej. `max-w-xl mx-auto`) en vistas de datos.
* **Solución**: contenedor principal de ancho completo (`width: 100%`), dejando el límite de ancho solo para modales y la tarjeta de inicio de sesión.
* **Regla**: convención de diseño (DEBERÍA). Ver [`components/layout/layout_rules.md`](../../components/layout/layout_rules.md).

---

### <a id="bug-004"></a> BUG-004: `.save()` dentro de bucles masivos
* **Síntoma**: importar 2.000 registros tarda decenas de segundos.
* **Causa raíz**: `obj.save()` en cada iteración: 2.000 viajes a la base de datos (y 2.000 transacciones si no hay una envolvente).
* **Solución**: acumular instancias y usar `bulk_create(objs, batch_size=500)` dentro de `transaction.atomic()`. Tener en cuenta que `bulk_create` no llama a `save()` ni emite señales `pre_save`/`post_save`.
* **Regla (BP-13)**: las colecciones DEBERÍAN escribirse en bloque.

---

### <a id="bug-005"></a> BUG-005: Rutas absolutas del sistema operativo en el código
* **Síntoma**: funciona en el equipo de quien lo escribió (`C:\Users\...`) y falla en Docker (`/app/...`) o en CI con `FileNotFoundError`.
* **Causa raíz**: rutas absolutas escritas a mano.
* **Solución**: resolver desde `BASE_DIR = Path(__file__).resolve().parent.parent` o desde variables de entorno.
* **Regla (BP-07)**: NO DEBEN escribirse rutas absolutas en el código.

---

### <a id="bug-006"></a> BUG-006: ORM de Django llamado desde `async def`
* **Síntoma**: `django.core.exceptions.SynchronousOnlyOperation: You cannot call this from an async context`.
* **Causa raíz**: el ORM de Django es síncrono; se invocó desde una ruta FastAPI declarada con `async def`.
* **Solución**: declarar la ruta con `def` (FastAPI la ejecuta en un hilo) o envolver la consulta con `asgiref.sync.sync_to_async`. Desde Django 4.1 existen métodos asíncronos del ORM para casos simples (`aget()`, `acreate()`, `acount()` e iteración de querysets con `async for`); las transacciones siguen sin soporte asíncrono.
* **Regla**: NO DEBE llamarse el ORM síncrono dentro de `async def` sin `sync_to_async`.

---

### <a id="bug-007"></a> BUG-007: Formularios CRUD en modal centrado en lugar del drawer
* **Síntoma**: en un módulo administrativo, "Agregar" o "Editar" abre un modal flotante en el centro que tapa la tabla; el usuario pierde de vista el registro y la lista de la que partió.
* **Causa raíz**: se creó un modal genérico sin consultar el componente de drawer del catálogo.
* **Solución**: usar el panel lateral derecho ([`components/drawer/drawer.md`](../../components/drawer/drawer.md), `.joli-drawer-container`), que mantiene la vista principal visible y tiene cabecera, cuerpo con scroll y pie de acciones fijos.
* **Regla**: convención de diseño (DEBERÍA, normativa 00 §6.4). Los modales quedan para confirmaciones, firmas, escáneres y sesión vencida.

---

### <a id="bug-008"></a> BUG-008: Barra final en la ruta: la redirección 307 pierde la sesión detrás de un proxy
* **Síntoma**: el usuario inicia sesión y el panel lo saca de inmediato. En el log aparece `GET /api/v1/auth/me/ - 307`, luego `OPTIONS` y `GET /api/v1/auth/me - 401` como «Invitado».
* **Causa raíz**: la ruta existe sin barra final; FastAPI responde 307 con una URL **absoluta** hacia el backend (`http://127.0.0.1:8001/...`). Detrás del proxy de Vite eso es otro origen: el navegador sigue la redirección como petición CORS y, por seguridad, **quita la cabecera `Authorization`**.
* **Solución**: en el middleware HTTP, normalizar las rutas `/api/...` que terminan en `/` (quitar la barra en `request.scope["path"]` y `raw_path`) antes de que el router las busque; así no hay redirección.
* **Regla**: las rutas de la API NO DEBEN depender de redirecciones por barra final. El cliente DEBE llamar las rutas exactas y el backend DEBERÍA normalizarlas en lugar de redirigir.

---

### <a id="bug-009"></a> BUG-009: Recarga automática de uvicorn colgada por WebSockets abiertos
* **Síntoma**: tras editar el backend, los endpoints nuevos responden 404 («Recurso no encontrado») y el log sigue con el formato viejo: el servidor sirve el código anterior.
* **Causa raíz**: con `reload=True`, uvicorn espera a que se cierren las conexiones abiertas antes de cambiar de proceso. Los WebSocket (chat, notificaciones) no se cierran solos, y la recarga queda esperando indefinidamente.
* **Solución**: `uvicorn.run(..., reload=True, timeout_graceful_shutdown=5)`: tras 5 s corta las conexiones; los clientes se reconectan solos. Aplica después de reiniciar el proceso una vez.
* **Regla**: todo backend con WebSockets DEBE fijar `timeout_graceful_shutdown`. Si un endpoint nuevo da 404, verificar primero que el proceso en ejecución cargó el código (`/openapi.json`).

---

### <a id="bug-010"></a> BUG-010: `text-overflow: ellipsis` no aparece en elementos `flex`
* **Síntoma**: un texto largo en una insignia o etiqueta (`.trigger-badge`) se corta en seco, sin «...».
* **Causa raíz**: con `display: flex` o `inline-flex`, el texto queda en una caja anónima de flex y `text-overflow` del contenedor no se aplica.
* **Solución**: `display: inline-block` (o `block`) con `overflow: hidden; white-space: nowrap; text-overflow: ellipsis; min-width: 0`, y el texto completo en `title`.
* **Regla**: todo contenedor que deba cortar texto con «...» DEBE ser `block` o `inline-block`, no `flex`.

---

### <a id="bug-011"></a> BUG-011: Salud de un servicio remoto medida con el costo de conectar
* **Síntoma**: el tablero de estado marca un servicio externo (p. ej. una base PostgreSQL remota) como «lento» (~1,5 s), aunque sus consultas responden en ~150 ms.
* **Causa raíz**: la revisión abría una conexión nueva en cada chequeo: red remota (~140 ms por ida y vuelta) + SSL + autenticación ≈ 7 idas y vueltas ≈ 1 s. Se medía conectar, no consultar.
* **Solución**: reutilizar una conexión de solo lectura (`autocommit=True`, `SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY`), medir `SELECT 1` sobre ella, reconectar si se cae y mostrar aparte el costo de la última conexión nueva. Ejecutar la revisión en un hilo (`asyncio.to_thread`) para no bloquear FastAPI.
* **Regla**: un indicador de salud DEBE medir la operación que importa (la consulta), con umbrales propios del servicio, y separar el costo de conexión.

---

### <a id="bug-012"></a> BUG-012: Avisos (sonner) de distinto tamaño al apilarse
* **Síntoma**: al aparecer dos avisos seguidos, el de atrás se ve más alto o más ancho que el de adelante.
* **Causa raíz**: con `toastOptions={{ unstyled: true }}`, sonner da al aviso de atrás la altura del de adelante pero **no oculta su contenido** (eso solo lo hace con sus estilos propios), y el ancho del contenedor (`--width`, 356 px por defecto) no coincide con el de la tarjeta.
* **Solución**: `style={{ '--width': '<ancho de la tarjeta>' }}` en el `Toaster`, tarjeta con `width: 100%`, y para los avisos apilados detrás: `overflow: hidden` en el contenedor, `height: 100%` en la tarjeta y `opacity: 0` en su contenido (ver [`components/toast/toast_notification.md`](../../components/toast/toast_notification.md)).
* **Regla**: con avisos sin estilo propio DEBEN declararse el ancho y el apilado; si no, los tamaños no coinciden.
* **Recaída (Pandora, 2026-11-08)**: aun con `--width` y la tarjeta en `width: 100%`, los avisos con poco texto salían más angostos. Sonner solo pone `width: var(--width)` al `li` de sus avisos con estilo propio (`[data-styled='true']`); el `li` sin estilo va en `position: absolute` sin ancho y se encoge al contenido, así que el `100%` de la tarjeta no sirve. Hay que fijar `width: var(--width)` en la clase del `li` (`toastOptions.className`, p. ej. `.joli-toaster-container`). En pantallas de 600 px o menos manda la regla de sonner.
* **Recaída 2 (Pandora, 2026-11-08)**: con varios avisos, el más viejo quedaba encima del nuevo y el de atrás se salía por debajo. Dos causas: (1) `z-index: 99999 !important` en la clase del `li` pisaba el `--z-index` que sonner da a cada aviso; (2) sonner envuelve el contenido personalizado en `[data-content] > [data-title]`, así que `li > .joli-toast` nunca coincidía. **Regla**: no poner `z-index` en la clase del aviso (el `ol` de sonner ya trae 999999999) y apuntar a la tarjeta con selector descendiente, dando `height: 100%` también a las dos capas de sonner.

---

### <a id="bug-013"></a> BUG-013: La URL conserva la última sección después de cerrar sesión
* **Síntoma**: tras salir, la barra del navegador sigue en la sección anterior (`/rutero/programacion`); el siguiente usuario entra a la ruta del anterior, y «Atrás» vuelve a secciones privadas sobre el login.
* **Causa raíz**: la app sincroniza módulo ↔ URL con `pushState`, pero al perder la sesión solo cambia la vista, no la dirección.
* **Solución**: sin sesión (salir, sesión vencida o sin permisos), `history.replaceState(null, '', '/')` y un `popstate` que repite la limpieza mientras no haya sesión.
* **Regla**: al terminar una sesión, la app DEBE devolver la URL al inicio, sin parámetros.

---

## Lecciones del proyecto
> Agregar aquí las entradas propias (BUG-014 en adelante), sin datos personales ni secretos.

### <a id="bug-014"></a> BUG-014: Guardar sin conexión que igual espera la red (app móvil)
* **Síntoma**: con señal débil (hay red pero responde muy lento), al guardar la pantalla se queda «guardando» 30-60 s o más, aunque la app «trabaja sin conexión». Sin red funciona bien.
* **Causa raíz**: el dato se guardaba en el celular, pero la pantalla hacía `await` de la subida de toda la cola, y las peticiones de escritura no tenían tiempo máximo: el sistema operativo tardaba en cortarlas. La red «conectada» hacía que sí se intentara.
* **Solución**: guardar local y liberar la pantalla (espera máxima corta, p. ej. 3 s, para confirmar con buena red; la subida sigue en segundo plano sin cancelarse). Tiempo máximo por petición (15 s datos; archivos: cancelar si no avanzan en 45 s). Reintentos espaciados con jitter y «modo red débil» que deja de insistir. Carriles separados para datos y archivos.
* **Regla preventiva**: una app local-first NO DEBE hacer `await` de la red en la acción del usuario; toda escritura en cola DEBE tener tiempo máximo y una llave de idempotencia (id de operación único que el servidor reconoce) para reintentar sin duplicar.

### <a id="bug-015"></a> BUG-015: Con señal débil la app «carga» aunque tenga los datos guardados
* **Síntoma**: con red lenta, abrir una pantalla muestra el esqueleto de carga varios segundos aunque el celular tenga la copia; las fotos tardan minutos en subir y las descargas de fondo frenan lo que guarda el usuario.
* **Causa raíz**: lectura *network-first* (se espera al servidor y solo si falla se usa la copia), respuestas JSON sin comprimir, descargas completas aunque nada cambió y fotos de cámara a tamaño completo.
* **Solución**: *stale-while-revalidate* (pintar la copia y actualizar en silencio); gzip en el servidor; ETag con `If-None-Match` → 304; aplazar descargas de fondo con red débil; reducir fotos a ~1600 px y JPEG ~70 % antes de subir.
* **Regla preventiva**: en apps móviles, toda pantalla con copia local DEBE pintarla primero; las respuestas grandes DEBEN ir comprimidas y, si cambian poco, con ETag; las imágenes DEBEN reducirse en el dispositivo antes de subirlas.

### <a id="bug-016"></a> BUG-016: Guardado doble por llamar a la API dentro de setState(prev => …)
* **Síntoma**: cada clic en una casilla envía dos guardados iguales al servidor (se ve en el log en desarrollo); a veces un sondeo periódico «devuelve» un cambio recién hecho.
* **Causa raíz**: la petición se lanzaba dentro de la función de actualización de `setState(prev => { …; guardar(next); return next })`. React puede ejecutar esa función más de una vez (en `StrictMode` siempre la ejecuta dos veces): debe ser pura. Además, un sondeo cada pocos segundos reemplazaba el estado local mientras el guardado seguía en curso.
* **Solución**: calcular el nuevo estado, ponerlo con `setState(next)` y llamar a la API fuera; en pantallas de configuración, editar en local y guardar con un botón (con aviso de «cambios sin guardar»), sin sondeo que pise lo editado.
* **Regla preventiva**: las funciones de actualización de `setState` NO DEBEN tener efectos (peticiones, eventos, toasts). Un sondeo NO DEBE sobrescribir un estado con cambios locales sin guardar.

### <a id="bug-017"></a> BUG-017: Botón de recargar como ícono suelto y que gira al revés
* **Síntoma**: el botón de recargar de una tabla se ve como un ícono flotando (no parece botón) y, al cargar, la flecha gira en sentido contrario al que apunta.
* **Causa raíz**: se usó `btn-icon-compact` sin su contenedor `compact-action-box` (que le da fondo, borde y sombra), y el ícono `RotateCcw` (flecha antihoraria) usaba la clase `spin`, que gira en sentido horario.
* **Solución**: poner los botones de ícono de la barra dentro de `<div className="compact-action-box" role="toolbar">`; con `RotateCcw` usar `spin-antihorario` (la misma animación en `reverse`); con `RefreshCw` (flecha horaria), `spin`.
* **Regla preventiva**: un botón solo-ícono de barra DEBE ir dentro de su grupo visual (ver [`icon_action_group.md`](../../components/button/icon_action_group.md)); la animación de giro DEBE seguir el sentido de la flecha del ícono.

### <a id="bug-018"></a> BUG-018: Variable CSS que se referencia a sí misma al centralizar colores
* **Síntoma**: tras pasar los colores a una paleta de variables, el color de «leído» del chat desaparece (el ícono toma el color heredado) sin ningún error en consola.
* **Causa raíz**: la paleta base creó `--chat-leido: #3b9ae1` en `:root`, y el componente ya tenía `.chat-layout { --chat-leido: … }`; el reemplazo automático dejó `--chat-leido: var(--chat-leido)`. Una variable que se usa a sí misma es un ciclo: el navegador la marca como inválida en silencio.
* **Solución**: nombrar la paleta por el color (`--azul-leido`) y dejar los nombres por uso (`--chat-leido`) solo como tokens semánticos en `variables.css`; mover los tokens del componente a `variables.css`.
* **Regla preventiva**: los nombres de la paleta base describen el color (`--slate-800`, `--azul-leido`), nunca el uso; antes de un reemplazo masivo, buscar `--x: var(--x)` y nombres repetidos entre la paleta y las variables de los componentes.

---

### <a id="bug-019"></a> BUG-019: En FastAPI reciente, app.routes no lista las rutas de los routers incluidos
* **Síntoma**: una prueba o un script que recorre `app.routes` para revisar todos los endpoints (deny-by-default, registro de endpoints) solo encuentra la ruta raíz y pasa sin revisar nada.
* **Causa raíz**: desde FastAPI 0.14x, `include_router` agrega un objeto `_IncludedRouter` en vez de copiar cada ruta; las rutas reales quedan en `ruta.original_router.routes`.
* **Solución**: recorrer de forma recursiva: si la ruta tiene `original_router`, bajar a sus `routes`; si no, usar la ruta (`APIRoute` o `APIWebSocketRoute`).
* **Regla preventiva**: una prueba que recorre rutas DEBE comprobar también que encontró las que esperaba (p. ej. que la lista de públicas sea exactamente la declarada), para que una lista vacía no la haga pasar en falso.

---

### <a id="bug-020"></a> BUG-020: Menú que muestra todo cuando la consulta de permisos falla
* **Síntoma**: los usuarios de un rol restringido ven todas las secciones del panel.
* **Causa raíz**: la barra lateral pedía los permisos del rol a un endpoint reservado al superadministrador. Para los demás respondía 403, el estado de permisos quedaba en `null` y el menú interpretaba `null` como «sin filtro». Además, el backend solo verificaba que fuera administrador, no la sección.
* **Solución**: endpoint propio `GET /api/v1/mis-permisos` (BP-19) para el menú, y validación de la sección en el backend con una dependencia por endpoint (`requiere_seccion(...)`).
* **Regla preventiva**: los permisos DEBEN fallar cerrados (si no se pudieron leer, no se muestra nada restringido) y el backend DEBE exigir el mismo permiso que el menú; ocultar una opción no protege el endpoint. Una prueba que recorra las rutas del panel debe exigir que cada una declare su permiso.

## Archivos monolíticos que se vuelven inmanejables (2026-11-08)
- Síntoma: en un proyecto real, una hoja `index.css` llegó a ~7.100 líneas, una vista React a ~2.200 y routers de FastAPI a más de 1.000. Cada ajuste de diseño rompía otra pantalla y los asistentes de IA tenían que leer miles de líneas para un cambio pequeño.
- Causa: se agregaba código al archivo existente en cada pedido, sin un límite que obligara a dividir.
- Regla: BP-23 (límites por tipo de archivo y dividir antes de agregar a un archivo que ya los superó).
- Cómo dividir sin romper (comprobado en un proyecto real con BP-23):
  - **CSS (Vite):** partir en hojas por área y dejar `index.css` como índice de `@import` en el orden original produce un bundle idéntico byte a byte. Se comprueba guardando el CSS de `dist/` antes y comparando con `cmp` después.
  - **Servicio TS con estado compartido:** cada variable `let` vive en un solo módulo; el `index.ts` de la carpeta reexporta solo lo que antes era público, así ningún import cambia. Verificar comparando la lista de exportaciones antes/después con el compilador.
  - **Router FastAPI en paquete:** un solo `router` compartido por los submódulos; el orden de import en `__init__.py` es el orden de registro de rutas (importa con rutas fijas vs. con parámetros). Los `patch("paquete.X")` de las pruebas deben apuntar al submódulo donde se usa `X`. Si un registro de endpoints usa el nombre del módulo, tomarlo del paquete.
  - **Modelos Django en paquete:** `models/__init__.py` importa todos los modelos; `makemigrations --check` debe decir «No changes detected».
  - **Esquemas Pydantic en paquete:** el `__init__` reexporta todos los modelos; el contrato OpenAPI generado debe quedar idéntico.

  - **Componentes React / React Native (2026-11-09, 17 archivos de un proyecto real):** el archivo original queda como componente de entrada con el mismo nombre exportado y las mismas props (ningún import cambia; si otros módulos importaban tipos o constantes de él, reexportarlos). Las piezas van en una subcarpeta junto a él: `estilos.ts` (el `StyleSheet.create` copiado tal cual), `use*.ts` (estado y efectos), `*Config.ts` / `utilidades.ts` (constantes y funciones puras) y subcomponentes. Las funciones que devolvían JSX (`celda()`, `filtro()`) pasan a ser componentes; el DOM queda igual. Verificar con `tsc`, lint y pruebas; los cambios visuales solo se confirman abriendo la pantalla.
  - **Constantes con iconos en un `.ts` de configuración:** si llevan JSX, el archivo tiene que ser `.tsx` y el lint marca `only-export-components`; usar `createElement(Icono, { size })` permite dejarlo en `.ts`.

## Vite responde 404 a un módulo que se convirtió en carpeta (2026-11-09)
- Síntoma: tras reemplazar `src/services/api.ts` por la carpeta `src/services/api/` (con `index.ts`), el navegador pedía `/src/services/api.ts?t=...` y recibía 404; el panel no cargaba.
- Causa: el servidor de desarrollo de Vite, iniciado antes del cambio, conservaba en su grafo de módulos la ruta del archivo viejo.
- Regla: al convertir un archivo en carpeta (o mover módulos importados por muchos), reiniciar `vite` antes de diagnosticar. No es un error del código si `tsc` pasa.

## `Animated.Value` en `useRef` rompe el lint de React (2026-11-09)
- Síntoma: `npx expo lint` falla con `react-hooks/refs` («Cannot access refs during render») en `style={{ opacity: progreso }}` cuando `progreso = useRef(new Animated.Value(0)).current`.
- Regla: crear el valor animado con `const [progreso] = useState(() => new Animated.Value(0))`: es estable entre renders y el lint lo acepta.

## Coordenadas opcionales en rutas y mapas (2026-11-09)
- Riesgo: al volver opcionales `lat`/`lon` de una parada, `haversine(null…)` da `NaN` y contamina toda la suma de km; un `Marker` con coordenadas nulas cierra la app en Android.
- Regla: un solo guardián de tipo (`tieneCoordenadas(p): p is T & Punto`) y filtrar con él antes de medir, ordenar, trazar, encuadrar o pintar marcadores. Las paradas sin coordenadas van al final en su orden, sin distancia, y los enlaces de Google Maps usan la dirección escrita (dirección, barrio, ciudad, país) en su lugar.
- Contrato: un campo que pasa de obligatorio a `Optional` rompe a los clientes viejos que lo dan por hecho; revisar qué hace la versión instalada antes de publicar.
