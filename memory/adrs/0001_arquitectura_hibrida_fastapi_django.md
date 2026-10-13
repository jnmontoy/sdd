# ADR 0001: Arquitectura Híbrida Desacoplada FastAPI + Django

* **Estado**: Aceptado
* **Fecha**: 2026-10-13
* **Decisores**: Arquitectura de Software Ecosistema Greenfield / Jolifoods
* **Reemplaza a**: Ninguno (ADR Fundacional)

---

## 1. Contexto y Problema
En las aplicaciones empresariales de Jolifoods, el frontend requiere consumir listados con decenas de miles de registros (Data Tables tipo Excel), filtros reactivos complejos y métricas KPI sin latencia. 

Al mismo tiempo, la organización requiere un sistema blindado de seguridad, autenticación corporativa (Microsoft 365 / SSO), matriz de roles RBAC, migraciones de base de datos seguras y un panel de administración robusto.

---

## 2. Opciones Consideradas
1. **Opción A: Django Monolítico Puro (Django REST Framework - DRF)**
   * *Ventajas*: Un solo framework, fácil de mantener.
   * *Desventajas*: Serializadores lentos con datasets grandes, mayor latencia en responses masivos de JSON, overhead en queries complejas de solo lectura.
2. **Opción B: FastAPI Puro con SQLAlchemy / Tortoise ORM**
   * *Ventajas*: Rendimiento ultra rápido de JSON con Pydantic v2 y async nativo.
   * *Desventajas*: Pérdida del robusto ecosistema de autenticación, migraciones maduras de Django y panel administrativo probado.
3. **Opción C: Arquitectura Híbrida ASGI (FastAPI para Lectura/Entrega Rápida + Django para Seguridad y Modelos)**
   * *Ventajas*: Lo mejor de ambos mundos. FastAPI montado bajo `/fast/` entrega JSONs ultra optimizados usando `ORJSONResponse` y Pydantic v2, mientras que Django gobierna la seguridad, la gestión de sesiones y las migraciones del ORM.
   * *Desventajas*: Requiere disciplina en el manejo de conexiones a la base de datos (evitar leaks en ASGI).

---

## 3. Decisión Tomada
Se adopta formalmente la **Opción C: Arquitectura Híbrida ASGI**.
* **FastAPI (`/fast/...`)**: Es la capa de entrega ultra rápida de JSON para Data Tables, KPIs y reportes reactivos.
* **Django (`/api/...` y `/admin/...`)**: Es la capa de gobierno de modelos, autenticación RBAC y migraciones de base de datos.
* **Cierre de Conexiones**: Toda ruta FastAPI que toque el ORM de Django debe cerrar conexiones explícitamente (`django.db.close_old_connections()`).

---

## 4. Consecuencias

### Positivas:
* Latencias de respuesta en Data Tables reducidas a menos de 50ms para miles de filas.
* Se preserva intacto el sistema de seguridad y permisos de Django.
* Cero duplicidad de esquemas de base de datos.

### Mitigaciones Obligatorias:
* Uso estricto de `.values()` y `select_related()` en Django ORM para evitar el problema $N+1$.
* Toda ruta debe estar registrada en `endpoints_registry.json`.

---

## 5. Regla Inflexible para Agentes de IA
> **INSTRUCCIÓN DIRECTA PARA LA IA**:
> Queda terminantemente prohibido sugerir reescribir la autenticación o los modelos en SQLAlchemy, o sugerir eliminar FastAPI para volver a DRF estándar en pantallas con alta carga de datos.
