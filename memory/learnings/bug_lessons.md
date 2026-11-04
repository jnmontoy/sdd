# Lecciones aprendidas de errores (catálogo para no repetirlos)

> **Propósito**: registrar cada error que costó más de un intento corregir, con su causa raíz y la regla que evita que vuelva a ocurrir.
> Las entradas BUG-001 a BUG-006 son **lecciones genéricas del stack del SDD** (Django + FastAPI + React) que sirven de ejemplo y punto de partida. Cada proyecto agrega las suyas a continuación.

**Formato de cada entrada**: síntoma (lo que se ve), causa raíz (por qué pasa), solución, regla preventiva (DEBE / DEBERÍA) y, si aplica, la buena práctica relacionada de la normativa 00.

---

## Índice
* [BUG-001: Conexiones a PostgreSQL agotadas en rutas FastAPI](#bug-001)
* [BUG-002: Consultas N+1 en serializadores o bucles](#bug-002)
* [BUG-003: Pantallas centradas y angostas por contenedores con ancho máximo](#bug-003)
* [BUG-004: `.save()` dentro de bucles masivos](#bug-004)
* [BUG-005: Rutas absolutas del sistema operativo en el código](#bug-005)
* [BUG-006: ORM de Django llamado desde `async def`](#bug-006)

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

## Lecciones del proyecto
> Agregar aquí las entradas propias (BUG-007 en adelante), sin datos personales ni secretos.
