# Protocolo 09: gobierno de APIs, versionado y cambios incompatibles

Reglas para que la evolución de las APIs REST/JSON no rompa a quienes las consumen: el frontend web, las aplicaciones instaladas (PWA) y las integraciones con otros sistemas.

Las palabras **DEBE / DEBERÍA / PUEDE** siguen la RFC 2119.

> **Estado de implementación en el SDD**: este protocolo es normativo. El SDD no incluye todavía el paso de `oasdiff` en CI ni un middleware que agregue las cabeceras de deprecación; cada proyecto los configura.

---

## 1. Versionado en la URL

1. Todo endpoint de producción DEBE incluir la versión mayor en la ruta:
   * Django: `/api/v1/usuarios/`
   * FastAPI: `/fast/v1/telemetria/`
   * Excepción: las sondas de salud `/health/live` y `/health/ready` no llevan versión.
2. La versión de la URL solo cambia (`v1` → `v2`) ante un cambio incompatible. Los cambios compatibles se publican en la misma versión.

**Por qué:** la versión en la URL es explícita, fácil de enrutar en el proxy y visible en los logs.

### ¿Qué es un cambio incompatible (*breaking change*)?
Un cambio DEBE tratarse como incompatible si:
* elimina o renombra un endpoint, un campo de la respuesta o un parámetro;
* cambia el tipo de un campo (p. ej. de `string` a `number`) o su formato (fecha sin zona a fecha con zona);
* vuelve obligatorio un parámetro o campo de entrada que era opcional, o agrega uno nuevo obligatorio;
* restringe los valores aceptados (p. ej. quita un valor de un `enum` de entrada);
* cambia los códigos de estado o la semántica (p. ej. de `200` a `202` con procesamiento diferido);
* cambia los requisitos de autenticación o permisos.

Son compatibles: agregar endpoints, agregar campos opcionales de entrada y agregar campos a la respuesta (los clientes DEBEN ignorar campos que no conocen).

---

## 2. Contratos OpenAPI y detección automática en CI

1. **Especificación generada**: FastAPI genera OpenAPI 3.1 automáticamente (`/fast/openapi.json` o la ruta que se configure). Para Django REST Framework se usa `drf-spectacular` (genera OpenAPI 3.0 por defecto). Cada especificación se versiona como archivo en el repositorio (p. ej. `docs/openapi/django.json`, `docs/openapi/fastapi.json`).
2. **Comparación en el *pull request*** con [oasdiff](https://github.com/oasdiff/oasdiff): se compara la especificación de la rama principal con la del cambio y el *pipeline* DEBE fallar si hay rupturas sin cambio de versión:

   ```bash
   oasdiff breaking docs/openapi/base.json docs/openapi/pr.json --fail-on ERR
   ```

   (`oasdiff breaking` clasifica cada hallazgo como `ERR` —ruptura— o `WARN` —posible ruptura—; `--fail-on ERR` hace que el comando termine con error ante rupturas.)

**Por qué:** las rupturas se detectan al revisar el código, no cuando un usuario reporta que algo dejó de funcionar.

---

## 3. Deprecación y retiro de endpoints

Cuando un endpoint o una versión vaya a retirarse:

1. **Periodo de aviso**: mínimo **90 días calendario** desde el anuncio para consumidores internos de la organización; para integraciones con terceros, el plazo pactado con ellos si es mayor.
2. **Cabeceras HTTP** en todas las respuestas del endpoint deprecado:

   ```http
   Deprecation: @1735689600
   Sunset: Thu, 01 Jul 2027 00:00:00 GMT
   Link: <https://app.ejemplo.local/docs/migracion-v2>; rel="deprecation"
   ```

   * `Deprecation` ([RFC 9745](https://www.rfc-editor.org/rfc/rfc9745)): fecha desde la que el recurso está deprecado, como fecha estructurada (`@` + segundos Unix). El ejemplo corresponde al 1 de enero de 2025 00:00 UTC.
   * `Sunset` ([RFC 8594](https://www.rfc-editor.org/rfc/rfc8594)): fecha a partir de la cual el recurso puede dejar de responder, en formato de fecha HTTP.
   * `Link` con `rel="deprecation"` (RFC 9745): documentación de migración.
3. **Seguimiento de consumidores**: registrar (en métricas o logs, sin datos personales) qué clientes siguen usando el endpoint deprecado y contactarlos antes del retiro.
4. **Retiro**: después de la fecha `Sunset`, el endpoint PUEDE responder `410 Gone` durante un tiempo antes de eliminarse.

---

## 4. Registro y documentación

* Todo endpoint DEBE registrarse en `backend/config/endpoints_registry.json` (lo usa `pruebas/validate_endpoints.py`) y en `frontend/src/services/endpoints.ts` (BP-09).
* Un cambio incompatible se documenta en el `design.md` del cambio (ver `changes_template/`) y se anuncia a los consumidores afectados, incluidos los de otras áreas o unidades de negocio.
