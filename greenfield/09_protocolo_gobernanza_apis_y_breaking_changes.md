# Protocolo de Gobernanza de APIs, Versionado y Detección de Breaking Changes
## Ecosistema Corporativo Jolifoods / Greenyard — Metodología SDD

Este protocolo norma la evolución de las interfaces de programación (REST / JSON API), impidiendo que cambios en el backend rompan clientes web, aplicaciones PWA o integraciones de terceros.

---

## 1. Reglas de Versionado de Endpoints

1. **Prefijo en URI Mandatorio**:
   - Todo endpoint de producción debe contener el número mayor de versión:
     - `/api/v1/usuarios/`
     - `/api/v2/pedidos/`
     - `/fast/v1/telemetria/`
2. **Definición de Cambio Disruptivo (*Breaking Change*)**:
   Un cambio se considera disruptivo y **exige un incremento de versión (`v1` -> `v2`)** si:
   - Elimina un campo o endpoint existente.
   - Cambia el tipo de dato de un campo (ej. de `string` a `number` o `array`).
   - Hace obligatorio un parámetro de entrada que antes era opcional.
   - Modifica la semántica o los códigos de estado HTTP de retorno (ej. de `200 OK` a `202 Accepted`).

---

## 2. Contratos OpenAPI y Validación en Pipeline CI

1. **Especificación Automática**:
   - Todo endpoint en FastAPI / Django REST Framework debe exportar su esquema formal **OpenAPI 3.1** vía Pydantic / Serializers tipados.
2. **Detección Automática de Rupturas (`oasdiff`)**:
   - En el pipeline de CI se ejecuta una comparación entre la especificación OpenAPI de la rama `main` y la rama del Pull Request.
   - Si se detecta una eliminación de campo sin cambio de versión `/v2/`, el pipeline se bloquea de forma inmediata:
     ```bash
     oasdiff -base main_openapi.json -revision pr_openapi.json -breaking
     ```

---

## 3. Protocolo Estándar de Deprecación (RFC Sunset)

Cuando un endpoint o versión anterior vaya a ser dada de baja:

1. **Periodo de Gracia**: Mínimo **90 días naturales** desde el anuncio formal.
2. **Cabeceras HTTP Obligatorias**:
   El backend debe inyectar las siguientes cabeceras en todas las respuestas del endpoint deprecado:
   ```http
   Deprecation: @1735689600
   Sunset: Wed, 01 Jul 2027 00:00:00 GMT
   Link: <https://docs.jolifoods.com/migration-v2>; rel="deprecation"
   ```
3. **Monitoreo de Consumidores Restantes**:
   - Monitorear en los logs de auditoría qué clientes o direcciones IP continúan invocando la versión deprecada antes del corte definitivo.
