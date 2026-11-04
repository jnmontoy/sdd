# Especificación SDD: Módulo de Login y Autenticación
## Joli Foods — Spec-Driven Development (SDD)

Suite de especificación del módulo **Login** para cualquier aplicación de Joli Foods. Define cómo diseñar, implementar y probar el inicio de sesión sin depender de rutas locales.

**Decisión canónica de sesión:** access token (JWT) solo en memoria; refresh token en cookie `HttpOnly; Secure; SameSite=Lax`, rotado en `/api/v1/auth/refresh/` con CSRF; logout que invalida el refresh. Ver [`02`](./02_arquitectura_y_maquina_estados.md) §4 y [`05`](./05_seguridad_auditoria_y_hardening.md) §2.

---

## 1. Mapa de Documentos

| # | Archivo | Contenido |
| :--- | :--- | :--- |
| 01 | [`01_requisitos_funcionales_y_negocio.md`](./01_requisitos_funcionales_y_negocio.md) | Perfiles, requisitos, criterios Gherkin y reglas de negocio. |
| 02 | [`02_arquitectura_y_maquina_estados.md`](./02_arquitectura_y_maquina_estados.md) | Topología, secuencias (credenciales y SSO), máquina de estados y ciclo de vida de la sesión. |
| 03 | [`03_contrato_api_y_modelos_datos.md`](./03_contrato_api_y_modelos_datos.md) | Endpoints `/api/v1/auth/*`, cookies, cabeceras, códigos de error y tipos TypeScript. |
| 04 | [`04_analisis_patrones_referencia.md`](./04_analisis_patrones_referencia.md) | Arquetipos de autenticación y decisiones canónicas. |
| 05 | [`05_seguridad_auditoria_y_hardening.md`](./05_seguridad_auditoria_y_hardening.md) | OWASP, cookies, CSRF, límite de intentos, bitácora y sesión vencida. |
| 06 | [`06_ui_ux_diseno_y_accesibilidad.md`](./06_ui_ux_diseno_y_accesibilidad.md) | Tokens de diseño, estados de interacción y WCAG 2.1 AA. |
| 07 | [`07_plan_de_pruebas_y_matriz_qa.md`](./07_plan_de_pruebas_y_matriz_qa.md) | Casos verificables en `pruebas/` (unitarias, integración, E2E, seguridad). |
| 08 | [`08_guia_de_implementacion_para_ia.md`](./08_guia_de_implementacion_para_ia.md) | Estructura del proyecto destino e instrucciones paso a paso. |
| 09 | [`09_flujo_restablecimiento_contrasena.md`](./09_flujo_restablecimiento_contrasena.md) | Recuperación de contraseña: token de un solo uso con hash, 15 min, sin enumeración. |
| 10 | [`10_healthcheck_y_monitoreo_infraestructura.md`](./10_healthcheck_y_monitoreo_infraestructura.md) | Sondas `/health/live` y `/health/ready`. |
| 11 | [`11_componentes_de_la_pagina.md`](./11_componentes_de_la_pagina.md) | Árbol de componentes, CSS con tokens y código de `LoginPage.tsx`. |

Modelos de datos: [`../../../model/login/README.md`](../../../model/login/README.md).

---

## 2. Componentes Atómicos (`.sdd/components/login/`)

1. [`logo.md`](../../../components/login/logo.md) — logo de la aplicación.
2. [`card.md`](../../../components/login/card.md) — variantes de tarjeta (centrada, pantalla dividida, quiosco).
3. [`button_microsoft.md`](../../../components/login/button_microsoft.md) — botón de Microsoft SSO.
4. [`input_field.md`](../../../components/login/input_field.md) — campos con ícono y ver/ocultar contraseña.
5. [`button_primary.md`](../../../components/login/button_primary.md) — botón de envío con spinner.
6. [`feedback_alerts.md`](../../../components/login/feedback_alerts.md) — alertas accesibles (`role="alert"`).
7. [`recovery_form.md`](../../../components/login/recovery_form.md) y [`email_recovery_template.md`](../../../components/login/email_recovery_template.md) — restablecimiento de contraseña.

---

## 3. Portabilidad

La especificación no asume rutas locales. Cualquier persona o agente con la carpeta `.sdd` puede levantar el módulo siguiendo [`08`](./08_guia_de_implementacion_para_ia.md) y las variables de [`config_referencia.env.example`](../../config_referencia.env.example).
