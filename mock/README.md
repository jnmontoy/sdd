# Carpeta de prototipos sin código (`mock/`)

Esta carpeta guarda los prototipos visuales (*mocks*: maquetas navegables sin backend) y las especificaciones de datos que preparan **personas no técnicas** (líderes de área, analistas, coordinadores) antes de que el equipo de desarrollo escriba código de producción.

Las palabras **DEBE**, **NO DEBE**, **DEBERÍA** y **PUEDE** se usan con el sentido de la RFC 2119: DEBE es obligatorio; DEBERÍA es la convención recomendada, de la que se puede apartar con una decisión registrada (ADR en `memory/adrs/`) o por pedido explícito del usuario.

---

## 1. Cómo funciona el modo sin código

1. **Sin terminal**: no requiere Node.js, Python, Docker ni base de datos.
2. **Se abre con doble clic** en un navegador moderno (Chrome, Edge, Firefox).
3. **Datos como arreglo JSON**: el mock carga los datos desde un arreglo JavaScript (`const MOCK_DATA = [...]`) y los recorre para pintar la tabla. Así la forma de los datos es la misma que entregará el backend real (el backend siempre responde JSON).
4. **Documento de datos acompañante (`datos_<modulo>.md`)**: enumera los campos que el backend debe entregar. Se construye con [`plantilla_datos_necesarios.md`](./plantilla_datos_necesarios.md).
5. **Sin pruebas automáticas en esta fase**: un mock no tiene backend ni base de datos, así que NO se le exigen Pytest, Playwright ni `validate_endpoints.py`. **Por qué:** probar una maqueta no aporta información sobre el sistema real y frena la iteración con el usuario. Las pruebas se exigen cuando el mock se traslada a `frontend/` y `backend/` (ver protocolo 11).

> **Datos sensibles**: NO pegues en el chat con la IA ni en el mock datos personales reales (nombres, cédulas, correos, teléfonos), costos, fórmulas, recetas ni cifras financieras no públicas. Usa datos ficticios o anonimizados con la misma forma (por ejemplo `Cliente A`, `1000000001`, `usuario@ejemplo.com`). La responsabilidad por la información que se ingresa recae en quien la ingresa.

### Dependencias de red de la plantilla
[`mock_template_with_json.html`](./mock_template_with_json.html) carga Bootstrap 5.3.3, la fuente Inter y los iconos Lucide (versión fijada 0.460.0) desde CDN. La primera apertura necesita internet. Sin red, la página sigue funcionando: la fuente cae a la del sistema, los iconos no se dibujan (los botones conservan su `aria-label`) y se pierden algunas utilidades de Bootstrap. Si el prototipo debe funcionar sin internet, copia esos archivos a `assets/` y cambia los enlaces a rutas relativas.

---

## 2. Qué hay en esta carpeta y qué se genera

Contenido real de `mock/`:

```text
mock/
├── README.md                         <- Este documento
├── mock_template_with_json.html      <- Plantilla base (un solo archivo, autocontenido)
└── plantilla_datos_necesarios.md     <- Plantilla de especificación de datos para el backend
```

La plantilla es **un único archivo** a propósito: es más fácil de copiar y abrir. Cuando se crea el prototipo de un módulo concreto, DEBERÍA separarse en **4 archivos más `assets/`**, con esta forma (ejemplo ilustrativo; esta carpeta no viene incluida en el repositorio):

```text
mock/<nombre_modulo>/
├── <nombre_modulo>.html      <- Marcado semántico; enlaza su .css, su .js y assets/
├── <nombre_modulo>.css       <- Estilos del módulo usando los tokens de variables.css
├── <nombre_modulo>.js        <- Lógica: MOCK_DATA, filtros, paginador, drawer, tema
├── datos_<nombre_modulo>.md  <- Contrato de datos JSON para el backend
└── assets/                   <- Copia local de los logos (Jolifoods.svg, Joli.svg, logoJoli.png)
```

**Por qué 4 archivos:** separar marcado, estilos y lógica permite que el integrador ubique rápido cada parte y que los cambios del usuario no mezclen estilos con datos.

**Ejemplo completo existente:** el dashboard de ventas de muestra está en [`greenfield/pages/dashboard/mockup_dashboard_ventas_ejemplo.html`](../greenfield/pages/dashboard/mockup_dashboard_ventas_ejemplo.html) (archivo único, igual que la plantilla).

---

## 3. Qué hace el integrador al recibir el mock

1. Abre el `.html` para ver la interfaz que el usuario aprobó.
2. Lee `datos_<modulo>.md` para diseñar los esquemas Pydantic / serializadores de Django con los nombres de campo exactos.
3. Copia `MOCK_DATA` como datos semilla o *fixtures* (datos fijos de prueba).
4. Reemplaza el HTML manual por los componentes React de `.sdd/components/` (`KpiCard`, `DataTable`, `ConfirmModal`, `RightDrawer`, etc.) sin escribir CSS nuevo.

---

## 4. Convenciones visuales para todo mock

Estas convenciones son **DEBERÍA** (estilo y diseño). Se pueden ajustar con pedido explícito del usuario o un ADR.

| # | Convención | Por qué | Referencia |
|---|---|---|---|
| 1 | Layout de ancho completo; barra lateral solo si el usuario la pide. | Las pantallas operativas son tablas anchas; el ancho útil importa más que el menú permanente. | [layout_rules.md](../components/layout/layout_rules.md), [sidebar.md](../components/layout/sidebar.md) |
| 2 | Título de la página en el lado izquierdo de la barra superior (como `<h1>`), sin migas de pan salvo pedido. Títulos sin color verde. | Ahorra espacio vertical y mantiene un único encabezado principal accesible. | [navbar.md](../components/layout/navbar.md) |
| 3 | Acciones agrupadas: caja compacta de 28 px en la barra de la tabla y grupo `btn-group btn-group-sm` de 26 px por fila, botones solo-icono con `aria-label`. | Reduce ruido visual y errores de clic; el lector de pantalla anuncia cada acción. | [icon_action_group.md](../components/button/icon_action_group.md) |
| 4 | Códigos e identificadores en fuente monoespaciada neutra; el verde se reserva para estados positivos. | El color debe comunicar estado, no decorar. | [badge_status.md](../components/badge/badge_status.md) |
| 5 | Confirmaciones críticas con `ConfirmModal`: motivo obligatorio (mínimo 10 caracteres), contador visible y botón Confirmar deshabilitado hasta cumplirlo. NO usar `alert()` ni `confirm()` nativos. | Deja trazabilidad del motivo y evita confirmaciones accidentales. | [confirm_modal.md](../components/modal/confirm_modal.md) |
| 6 | Crear y editar en panel lateral derecho (*drawer*), no en modales centrados. | Mantiene visible la tabla de contexto mientras se edita. | [drawer.md](../components/drawer/drawer.md) |
| 7 | Filtros superiores en grupo expandible con botón para limpiar. | Muchos filtros en poco espacio. | [expandable_filter_group.md](../components/dropdown/expandable_filter_group.md) |
| 8 | Campana de notificaciones con contador y popover con pestañas por categoría. | Separa avisos operativos de alertas críticas. | [notification_popover.md](../components/notification/notification_popover.md) |
| 9 | Menú de perfil con "Mi perfil" y "Cerrar sesión"; cerrar sesión pide confirmación. | Evita cierres involuntarios. | [user_profile_dropdown.md](../components/layout/user_profile_dropdown.md) |
| 10 | Paginador **arriba** de la tabla, junto a la barra de herramientas; tarjeta contenedora que llega al fondo de la pantalla; 20–30 registros de ejemplo. | El usuario ve el total y navega sin bajar al final de la tabla. | [pagination.md](../components/pagination/pagination.md), [data_table.md](../components/data_table/data_table.md) |
| 11 | Filtros tipo Excel por columna (orden A-Z/Z-A, búsqueda, casillas con conteo). | Es el modelo mental que ya tienen los usuarios de hojas de cálculo. | [checklist_popover.md](../components/data_table/checklist_popover.md) |
| 12 | Columnas redimensionables y selector de columnas visibles (al menos una visible). | Tablas anchas en monitores distintos. | [column_resizer.md](../components/data_table/column_resizer.md), [column_visibility.md](../components/data_table/column_visibility.md) |
| 13 | Colores siempre con tokens de `variables.css` (`var(--...)`); el cambio de tema actualiza `data-theme`, `data-bs-theme` y `color-scheme`. Ningún texto blanco sobre fondo claro. | Un color quemado no cambia con el tema y rompe el contraste. | [variables.md](../components/variables.md) |
| 14 | Controles de formulario con etiqueta asociada (`<label for>`), estilo corporativo y foco visible; el botón principal dice qué guarda ("Guardar registro"). | Accesibilidad y claridad de la acción. | [drawer.md](../components/drawer/drawer.md) |
| 15 | Paquete del módulo en 4 archivos + `assets/` (sección 2). | Ver sección 2. | — |
| 16 | Logo enlazado de forma relativa desde `./assets/Jolifoods.svg`, con respaldo `logoJoli.png`. | El prototipo se puede mover de carpeta sin imágenes rotas. | [logo.md](../components/login/logo.md) |

> **Nota sobre la plantilla**: `mock_template_with_json.html` replica los tokens de `variables.css` en un único bloque `:root` para poder abrirse sola. Es la única excepción aceptada a "no copiar tokens": si `variables.css` cambia, este bloque DEBE actualizarse.

> **Origen:** las convenciones 8 y 9 (notificaciones y menú de perfil) se tomaron de proyectos internos de Joli Foods; aquí se describen de forma genérica. Ver [`greenfield/13_catalogo_innovaciones_y_mejores_practicas_proyectos.md`](../greenfield/13_catalogo_innovaciones_y_mejores_practicas_proyectos.md).
