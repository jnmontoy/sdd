# Fuentes y procedencia de los patrones del SDD

Este documento registra **de qué proyecto interno de Joli Foods salió cada patrón** que hoy el SDD describe de forma genérica. Sirve para trazabilidad (saber dónde ver una implementación real y a quién preguntar), no como norma: la norma es el componente o protocolo genérico enlazado en cada fila.

Reglas de uso:
* Para construir, se usa el **componente o protocolo genérico**, no el código del proyecto de origen.
* Que un patrón haya funcionado en un proyecto no lo convierte en obligatorio para otro: se evalúa si el problema es el mismo.
* Las advertencias de cada fila son parte del patrón; ignorarlas reproduce errores ya conocidos.

---

## 1. Tabla de procedencia

| Patrón genérico | Problema que resuelve | Componente / protocolo en el SDD | Origen | Advertencias |
|---|---|---|---|---|
| Tutorial de vista dividida con selector previo | Guiar paso a paso (p. ej. conectar Power BI o Excel a una base de datos) con capturas ampliables y datos copiables. | [`components/tutorial/split_tutorial_walkthrough.md`](../components/tutorial/split_tutorial_walkthrough.md) | `bi` (tutoriales de conexión) | NO mostrar credenciales permanentes en el panel; usar credenciales de solo lectura, temporales o un enlace al gestor de secretos. |
| Calidad de datos (reglas de validación sobre tablas maestras) | Detectar registros huérfanos, formatos inconsistentes y anomalías. | Sin componente genérico todavía. | `bi` (módulo DQ) | Candidato a especificar en `model/`. |
| Token en URL como respaldo para conectores externos | Herramientas que no pueden enviar cabeceras (conectores de Power BI/Excel, descargas directas). | Excepción documentada en BP-18 (normativa 00). | `bi` (`TokenAuthentication` con respaldo `?token=`) | Es una **excepción de seguridad**, no un patrón general: los tokens en URL quedan en logs, historial y cabecera `Referer`. Si se usa: token de solo lectura, alcance mínimo, vida corta y revocable, y registro de su uso. Para sesiones de usuario aplica el modelo canónico (access token en memoria + refresh en cookie `HttpOnly`). |
| Seguimiento de proyectos con hitos, sprints, decisiones (ADR), compromisos, tareas y línea de tiempo | Gobierno de proyectos de TI. | Inspira [`memory/`](../memory/README.md) y el protocolo 15 (ADR). | `app_tic` | — |
| Herramientas para agentes de IA vía MCP (*Model Context Protocol*) | Que un agente consulte o registre tareas y decisiones sin intervención manual. | Sin componente genérico; ver protocolo 15 §4. | `app_tic` | Toda herramienta MCP con escritura DEBE autenticarse y quedar auditada como cualquier API. |
| Acciones correctivas y preventivas (ACPM) con consecutivo y evidencias | Registro formal de no conformidades. | [`components/upload/file_uploader_pro.md`](../components/upload/file_uploader_pro.md), [`model/archivos/`](../model/archivos/spec_model_archivos_media.md) | `app_tic` | — |
| Roles en tabla propia con permisos en `JSONField` y unión de permisos del usuario | Cambiar roles y accesos sin migraciones ni cierre de sesión. | [`components/roles/roles_admin_sidebar.md`](../components/roles/roles_admin_sidebar.md), [`pages/roles/`](./pages/roles/01_roles_permisos_especificacion.md), BP-19 | `tiendita` | El refresco de permisos cada 5 s del proyecto original genera carga constante; el SDD recomienda refrescar al enfocar la ventana, al recibir 403 o con polling largo (ver [`js_polling_architecture.md`](../components/realtime/js_polling_architecture.md)). El backend DEBE validar permisos en cada petición; el refresco en el cliente solo afecta la interfaz. |
| Firma manuscrita en canvas con recorte automático | Capturar firmas limpias para actas y entregas. | [`components/signature/signature_modal.md`](../components/signature/signature_modal.md), [`multi_party_signature.md`](../components/signature/multi_party_signature.md) | `tiendita` (entrega de dotaciones) | Una firma manuscrita digitalizada **no es** una firma digital certificada (Ley 527 de 1999); su valor probatorio depende del proceso y de la evidencia asociada. Es dato personal. |
| Visor de PDF en canvas | Ver documentos sin depender del visor del navegador. | [`components/pdf/pdf_preview_frame.md`](../components/pdf/pdf_preview_frame.md) | `tiendita` | — |
| Lector de códigos de barras y QR por cámara | Captura rápida de códigos en bodega o portería. | [`components/scanner/scanner_modal.md`](../components/scanner/scanner_modal.md) | `tiendita` | La cámara requiere HTTPS (o `localhost`) y permiso del usuario. |
| Captura facial con guía de encuadre | Fotografía de identificación de conductores u operarios. | [`components/biometrics/facial_scanner.md`](../components/biometrics/facial_scanner.md) | `contenedores` | El rostro es un **dato biométrico sensible** (Ley 1581 de 2012): requiere autorización expresa, finalidad declarada y almacenamiento protegido. El componente captura imagen; no hace reconocimiento facial. |
| Inspección física con evidencia fotográfica | Registro del estado de contenedores (sellos, pisos, paredes). | [`components/upload/file_uploader_pro.md`](../components/upload/file_uploader_pro.md), BP-08 | `contenedores` | — |
| Aplicación instalable (PWA) en modo kiosco | Tablets en porterías con pantalla completa y tolerancia a cortes breves de red. | [`components/pwa/pwa_install_banner.md`](../components/pwa/pwa_install_banner.md) | `porterias` | El banner solo invita a instalar; el funcionamiento sin conexión requiere un *service worker* y una estrategia de sincronización que el SDD no especifica todavía. |
| Interfaz de registro rápido con botones grandes | Operación con guantes o en terminales resistentes. | Sin componente genérico todavía. | `porterias` | Al especificarlo, usar objetivos táctiles de al menos 44×44 px (WCAG 2.2, criterio 2.5.5) y textos legibles a distancia. |
| Calendario mensual de turnos y novedades | Ver turnos, permisos, incapacidades y vacaciones. | [`components/calendar/corporate_calendar.md`](../components/calendar/corporate_calendar.md) | `vibra` | Las incapacidades son datos de salud (sensibles): mostrar solo el tipo de novedad a quien no tenga permiso. |
| Menú de perfil de usuario y centro de notificaciones con pestañas | Acceso a perfil, cierre de sesión confirmado y avisos por categoría. | [`user_profile_dropdown.md`](../components/layout/user_profile_dropdown.md), [`notification_popover.md`](../components/notification/notification_popover.md) | `vibra`, `tiendita` | — |
| Filtros tipo Excel por columna, KPIs que filtran y paginador sobre la tabla | Exploración de tablas grandes con el modelo mental de una hoja de cálculo. | [`data_table.md`](../components/data_table/data_table.md), [`checklist_popover.md`](../components/data_table/checklist_popover.md), [`kpi_cards.md`](../components/kpi/kpi_cards.md), [`pagination.md`](../components/pagination/pagination.md) | `bi` (módulo de cartera) | — |
| Extracción de colores desde imágenes y modelo de mezcla sustractiva de pigmentos | Formular tonos a partir de fotos. | Sin componente genérico (lógica de dominio). | `color` | Es lógica específica del negocio; no se generaliza. Las fórmulas resultantes son información confidencial. |
| Empaquetado de aplicaciones Python como ejecutable de escritorio (PyInstaller) | Equipos de planta sin internet ni permisos para instalar Python. | Sin plantilla en el SDD. | instalador interno de Joli | Los ejecutables generados por PyInstaller suelen ser marcados por antivirus; requieren firma de código. El uso de `autorun.inf` está deshabilitado por defecto en Windows moderno y no es un mecanismo de instalación fiable. |

---

## 2. Cómo agregar una nueva procedencia

1. Describir el patrón de forma genérica en `components/`, `model/` o en un protocolo.
2. Agregar una fila a la tabla con el problema, el enlace genérico, el proyecto de origen y las advertencias conocidas.
3. En el documento genérico, si se quiere citar el origen, usar una sola nota: `> **Origen:** patrón tomado de <proyecto> (<módulo>). Aquí se describe de forma genérica.`
