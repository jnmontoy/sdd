# Especificación SDD: Módulo de Login y Autenticación
## Ecosistema Greenyard / Jolifoods — Spec-Driven Development (SDD)

Este directorio reúne la suite normativa de especificación canónica del módulo **Login** bajo la metodología **Spec-Driven Development (SDD)** para el ecosistema **Greenyard**.

Define rigurosamente cómo debe diseñarse, implementarse y auditarse el inicio de sesión en cualquiera de las aplicaciones de la organización, de forma **100% portable y agnóstica de rutas locales**.

---

## 1. Mapa de Complementos SDD del Módulo

| Complemento | Archivo | Contenido Clave |
| :--- | :--- | :--- |
| **01. Requisitos** | [`01_requisitos_funcionales_y_negocio.md`](./01_requisitos_funcionales_y_negocio.md) | Casos de uso, roles, criterios de aceptación Gherkin y reglas de negocio. |
| **02. Arquitectura** | [`02_arquitectura_y_maquina_estados.md`](./02_arquitectura_y_maquina_estados.md) | Topología cliente-servidor, diagramas de secuencia y FSM de la interfaz. |
| **03. Contratos API** | [`03_contrato_api_y_modelos_datos.md`](./03_contrato_api_y_modelos_datos.md) | OpenAPI 3.1, JSON Schemas, tipos TypeScript, headers y códigos de error. |
| **04. Referencias** | [`04_analisis_patrones_referencia.md`](./04_analisis_patrones_referencia.md) | Síntesis comparativa de patrones de los 6 proyectos del ecosistema. |
| **05. Seguridad** | [`05_seguridad_auditoria_y_hardening.md`](./05_seguridad_auditoria_y_hardening.md) | OWASP Top 10, Cookies HttpOnly, Rate Limiting y trazabilidad de accesos. |
| **06. UI/UX & A11y** | [`06_ui_ux_diseno_y_accesibilidad.md`](./06_ui_ux_diseno_y_accesibilidad.md) | Design tokens corporativos, microinteracciones y accesibilidad WCAG 2.1 AA. |
| **07. Plan de QA** | [`07_plan_de_pruebas_y_matriz_qa.md`](./07_plan_de_pruebas_y_matriz_qa.md) | Batería de pruebas unitarias, integración, E2E y pruebas de penetración. |
| **08. Guía para IA** | [`08_guia_de_implementacion_para_ia.md`](./08_guia_de_implementacion_para_ia.md) | Blueprint del proyecto destino e instrucciones de generación paso a paso. |
| **09. Restablecimiento** | [`09_flujo_restablecimiento_contrasena.md`](./09_flujo_restablecimiento_contrasena.md) | Especificación de recuperación de clave, tokens OTT de 15 min y correo seguro. |
| **10. Monitoreo & Salud** | [`10_healthcheck_y_monitoreo_infraestructura.md`](./10_healthcheck_y_monitoreo_infraestructura.md) | Sondas de Liveness y Readiness en FastAPI/Docker con métricas de PostgreSQL y Redis. |

---

## 2. Integración con el Sistema de Componentes (`.sdd/components/`)

El Login de Greenyard se ensambla mediante los componentes atómicos especificados en **[`.sdd/components/`](../../../components/README.md)**:

1. **Logo Corporativo**: [`logo.md`](../../../components/login/logo.md) — Isotipo estilizado Greenyard con halo esmeralda y tipografía de marca.
2. **Cards y Contenedores**: [`card.md`](../../../components/login/card.md) — 3 variantes estructurales (Centered Glass Card, Split-Screen Hero y Kiosk Minimal) con su CSS canónico `backdrop-filter: blur()`.
3. **Botón Microsoft SSO**: [`button_microsoft.md`](../../../components/login/button_microsoft.md) — Cuadrícula oficial SVG de 4 colores (`#f25022`, `#00a4ef`, `#7fba00`, `#ffb900`) y estados reactivos.
4. **Campos de Entrada (Inputs)**: [`input_field.md`](../../../components/login/input_field.md) — Inputs con icono prefijo, toggle interactivo de contraseña (íconos ojo) y animación shake de error.
5. **Botón Primario y Loader**: [`button_primary.md`](../../../components/login/button_primary.md) — Botón submit esmeralda con spinner integrado y halo reactivo glow.
6. **Feedback y Alertas**: [`feedback_alerts.md`](../../../components/login/feedback_alerts.md) — Banners de error accesibles (`role="alert"`) y modales de sesión expirada.

---

## 3. Principio de Autonomía y Portabilidad

Esta especificación **no asume ninguna ruta local de disco preexistente**. Cualquier agente de IA o desarrollador que reciba la carpeta `.sdd` puede estructurar y levantar un proyecto funcional completo siguiendo el Blueprint descrito en el Complemento 08 y configurando las variables de [`.sdd/greenfield/config_referencia.env.example`](../../config_referencia.env.example).
