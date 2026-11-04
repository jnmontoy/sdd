# ADR 0001: Arquitectura híbrida Django + FastAPI en un solo proceso ASGI

* **Estado**: Aceptado
* **Fecha**: 2026-10-13
* **Decisores (roles)**: Arquitectura de software TIC, Joli Foods
* **Reemplaza a**: Ninguno (ADR base del SDD)

---

## 1. Contexto y problema

Las aplicaciones internas de Joli Foods comparten dos tipos de carga:

* **Lectura intensiva**: tablas con miles de filas, filtros por columna y KPIs que se refrescan con frecuencia.
* **Gobierno y escritura**: autenticación (credenciales locales y Microsoft 365), roles y permisos, auditoría, migraciones de base de datos y un panel administrativo.

Restricciones conocidas:
* Equipo pequeño, con experiencia previa en Django.
* PostgreSQL como base de datos y Redis disponible.
* No hay mediciones formales publicadas que comparen el rendimiento de las alternativas con datos de Joli; la ventaja de rendimiento de la opción elegida es una **expectativa basada en benchmarks públicos**, no un hecho medido en nuestros sistemas.

---

## 2. Opciones consideradas

1. **Django + Django REST Framework (DRF) únicamente**
   * Ventajas: un solo framework, una sola capa de autenticación, ecosistema maduro, menor curva de aprendizaje.
   * Desventajas: los serializadores de DRF tienen sobrecosto con respuestas grandes. Se mitiga parcialmente con `.values()`, paginación en servidor y un renderizador JSON más rápido (p. ej. orjson), opción no evaluada formalmente.
2. **Django + Django Ninja** (API tipada con Pydantic sobre Django)
   * Ventajas: validación y serialización con Pydantic, OpenAPI automático, un solo framework y una sola capa de autenticación.
   * Desventajas: comunidad más pequeña que DRF y FastAPI; no se evaluó en un piloto.
3. **FastAPI únicamente con SQLAlchemy**
   * Ventajas: asincronía nativa, Pydantic v2, OpenAPI automático.
   * Desventajas: se pierden el panel administrativo, el sistema de migraciones y la autenticación de Django; habría que reconstruirlos.
4. **Híbrido ASGI: Django para modelos, seguridad y escritura; FastAPI montado en `/fast/` para lecturas rápidas** (elegida)
   * Ventajas: conserva el ecosistema de Django y suma la serialización de Pydantic v2 en endpoints de lectura masiva.
   * Desventajas: ver consecuencias negativas.

---

## 3. Decisión

Se adopta la **opción 4**.

* **Django** (`/api/v1/...`, `/admin/`): modelos, migraciones, autenticación, permisos, escrituras y auditoría.
* **FastAPI** (`/fast/v1/...`): endpoints de solo lectura o de alto volumen (tablas, KPIs, reportes), usando el ORM de Django. Cada endpoint declara su tipo de respuesta con modelos Pydantic (`response_model` o anotación de retorno); FastAPI serializa con Pydantic directamente. NO se usa `ORJSONResponse` como clase de respuesta por defecto.

> **Nota de actualización (2026-11-04)**: la versión original de este ADR fijaba `ORJSONResponse` (orjson) como respuesta por defecto de FastAPI. En versiones recientes de FastAPI esa clase está obsoleta y la vía recomendada es declarar el tipo de respuesta con modelos Pydantic, por lo que se actualizó la decisión.
* **Salud**: `/health/live` y `/health/ready` servidos por FastAPI; `/fast/v1/health` para la capa FastAPI.
* Ambas capas validan el **mismo** access token JWT (cabecera `Authorization: Bearer`) y aplican los mismos permisos.

**Por qué no la opción 2**, que es más simple: el equipo ya tenía plantillas y experiencia con FastAPI; se reconoce que Django Ninja podría cubrir la necesidad con menos complejidad y queda como primera alternativa si este ADR se revisa.

---

## 4. Consecuencias

### Positivas
* Se conservan el panel administrativo, las migraciones y la autenticación de Django.
* Los endpoints de lectura masiva pueden usar Pydantic v2 y respuestas JSON más rápidas.
* Un solo esquema de base de datos (modelos de Django) para ambas capas.

### Negativas y costos asumidos
* **Dos frameworks que aprender y mantener**, con dos formas de declarar rutas, dependencias y errores. Mitigación: plantillas en `.sdd/stack/` y reglas de uso claras (qué va a cada capa).
* **Doble capa de autenticación y permisos**: FastAPI no hereda los middlewares ni los permisos de Django; hay que reimplementar la validación del JWT y los chequeos de permiso como dependencias de FastAPI. Riesgo: que un endpoint `/fast/` quede menos protegido que su equivalente en Django. Mitigación: dependencia de autenticación obligatoria en el router de FastAPI y pruebas de acceso no autorizado por endpoint.
* **ORM síncrono dentro de un servidor asíncrono**: llamar al ORM de Django desde una función `async def` lanza `SynchronousOnlyOperation`. Hay que usar funciones `def` (FastAPI las ejecuta en un pool de hilos) o envolver con `sync_to_async`.
* **Gestión de conexiones a la base de datos**: las rutas de FastAPI no disparan las señales de petición de Django, así que las conexiones no se reciclan solas. Mitigación: dependencia que llame a `django.db.close_old_connections()` antes y después de cada petición (ver `learnings/bug_lessons.md`, BUG-001).
* **Dos documentaciones OpenAPI** (una por capa) que hay que mantener coherentes y versionar (protocolo 09).
* **Depuración más compleja**: un error puede venir de cualquiera de las dos capas o de su integración en `asgi.py`.

### Riesgos
* Si el volumen real de datos no justifica la capa rápida, se paga la complejidad sin beneficio. No hay medición que lo confirme todavía.

---

## 5. Cuándo revisar esta decisión
* Si una medición con datos reales muestra que DRF optimizado o Django Ninja cumplen los tiempos objetivo (protocolo 07).
* Si aparecen incidentes de seguridad o de conexiones atribuibles a la doble capa.
* Si cambia la composición o la experiencia del equipo.

---

## 6. Implicaciones para quien programa (incluidos agentes de IA)
Mientras este ADR esté vigente, NO se debe proponer:
* reescribir modelos o autenticación en SQLAlchemy;
* eliminar FastAPI de los endpoints de lectura masiva ya construidos;
* crear endpoints `/fast/` sin la dependencia de autenticación;

salvo que una persona pida explícitamente revisar este ADR.
