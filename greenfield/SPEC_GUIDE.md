# Guía Maestra de Desarrollo Guiado por Especificaciones (SDD - Spec-Driven Development)
## Ecosistema Greenfield / Jolifoods — Metodología Universal y Portátil

Esta guía define el estándar operacional y metodológico que la **Inteligencia Artificial (IA)** y los desarrolladores deben seguir obligatoriamente para documentar, diseñar e implementar cualquier página o módulo dentro de las aplicaciones del ecosistema **Greenfield** (desarrollo limpio desde cero).

---

## 1. Principio Fundamental: Cero Suposición de Rutas y Portabilidad Total

> **REGLA DE ORO DE SDD**:
> Un archivo de especificación `.sdd` debe ser **100% agnóstico y portable**. 
> Cualquier persona, equipo de ingeniería, pipeline de CI/CD o agente de Inteligencia Artificial que reciba la carpeta `.sdd` debe ser capaz de estructurar, inicializar y construir un proyecto desde cero sin suponer la existencia de rutas locales absolutas, rutas de red privadas o dependencias del entorno de quien lo escribió.

### Directrices de Portabilidad para la IA:
1. **Rutas 100% Relativas y Estructuras Canónicas**: Siempre prescribir la arquitectura en términos de la raíz del proyecto (`./frontend/`, `./backend/`, `./src/`). Jamás utilizar rutas absolutas del sistema operativo (`C:\Users\...`, `/home/...`) ni dominios fijos quemados (`http://localhost:8000/media/...`).
2. **Directorio Canónico `backend/media/` para Cargas**: Exigir la existencia de `backend/media/` con su archivo `.gitkeep` y montada en Docker para toda subida de firmas, PDFs, fotos y evidencias corporativas.
3. **Identidad Corporativa Jolifoods**: El logo oficial (`.sdd/assets/Jolifoods.svg`, `Joli.svg`, `logoJoli.png`) debe copiarse e inyectarse en los assets del nuevo proyecto.
4. **Definición de Blueprint de Archivos**: Cada especificación debe incluir el árbol canónico de archivos que el proyecto debe generar.
5. **Parametrización por Variables de Entorno**: Endpoints, hosts, nombres de cookies, client IDs de OAuth y secretos deben ser documentados mediante plantillas `.env.example`.
6. **Contratos como Especificación Declarativa**: Los esquemas de datos (OpenAPI, JSON Schema, Zod, Pydantic/Serializers) son la fuente de verdad universal.


---

## 1.1. Protocolo de Preguntas Pertinentes Obligatorio para la IA

Antes de escribir código o generar estructuras, la Inteligencia Artificial **NO DEBE ASUMIR REQUERIMIENTOS A CIEGAS**. Debe iniciar siempre con la pregunta de perfil:

---

### Paso 0 Obligatorio: Filtro de Perfil de Usuario
La IA debe formular obligatoriamente la siguiente pregunta antes de cualquier otra acción:

> **"¡Hola! Para brindarte la mejor experiencia en el ecosistema SDD (Spec-Driven Development), cuéntame:**  
> **¿Eres desarrollador de software o tienes un perfil no técnico / de negocio?"**
>
> - **[1] No soy desarrollador (Perfil de Negocio, Operativo o Líder Funcional)**  
>   *(Se activará el **Modo Prototipado No-Code** en la carpeta `mock/`)*
> - **[2] Sí, soy desarrollador (Ingeniería, Fullstack o Integrador)**  
>   *(Se activará el **Modo Arquitectura y Código** para construir proyectos o complementos desde cero)*

---

### Si el Usuario responde: [1] NO SOY DESARROLLADOR
La IA activa el flujo de prototipado rápido en la carpeta **`mock/<nombre_modulo>/`**:

> **REGLA FUNDAMENTAL DE AGNOSTICISMO TEMÁTICO**:  
> La IA **NUNCA DEBE ASUMIR QUE EL MÓDULO O PANTALLA ES DE VENTAS O FINANZAS**. La persona puede pedir un módulo del **clima y sensores agrícolas**, inventario de fruta, mantenimiento de maquinaria, despacho de vehículos, recursos humanos o cualquier otra área.  
> Lo que es **estricto y no negociable** es la **reutilización de componentes y estilos del SDD** (tarjetas KPI `.cartera-kpi-card`, tabla interactiva `.joli-table`, badges de estado, buscador en vivo, `ConfirmModal` con justificación). Los campos y datos se moldean dinámicamente según la necesidad del usuario sin inventar CSS nuevo.

1. **Lenguaje 100% Humano y de Negocio**:
   - Cero jerga técnica (sin menciones a Docker, puertos, Pydantic, migraciones, ORM ni hooks).
2. **Cuestionario Guiado Anti-Olvidos de Negocio**:
   La IA formula de manera conversacional las siguientes preguntas clave para evitar omisiones:
   - **Objetivo y Métricas**: *"¿Qué proceso o pantalla quieres gestionar y cuáles son los 3 o 4 números más importantes (KPIs) que debes ver de un vistazo?"*
   - **Datos o Tabla desde Excel**: *"¿Tienes ya una tabla o archivo de Excel con datos de ejemplo? Puedes copiar y pegar las filas directamente aquí y yo las convierto a la tabla del mock."*
   - **Permisos y Roles**: *"¿Quiénes van a entrar a esta pantalla? ¿Todos pueden ver los mismos datos o hay información reservada (como costos o márgenes)? ¿Quién tiene permiso de anular o borrar?"*
   - **Acciones Delicadas**: *"Si hay botones para anular, cancelar o borrar, ¿el sistema debe exigir obligatoriamente que la persona escriba el motivo de la anulación?"*
   - **Dispositivo**: *"¿Esta vista se usará en computadores de oficina o también en tablets/celulares en bodega o campo?"*
   - **Pantalla sin Datos**: *"¿Qué mensaje constructivo o botón debe aparecer cuando un usuario entre por primera vez y la tabla aún no tenga registros?"*

3. **Generación del Paquete No-Code Modular y Portable en `mock/<nombre_modulo>/`**:
   Todo módulo para perfiles no técnicos se genera obligatoriamente en **4 archivos separados e independientes más su subcarpeta de assets locales (Cero HTML monolítico)**:
   - **`[nombre_modulo].html`**: Estructura de marcado semántico limpia, que enlaza `<link rel="stylesheet" href="./[nombre_modulo].css">`, `<script src="./[nombre_modulo].js"></script>` y `<img src="./assets/Jolifoods.svg" class="topheader-logo">`, abriendo con doble clic en cualquier navegador.
   - **`[nombre_modulo].css`**: Hoja de estilos con variables oficiales de [variables.css](../components/variables.css), layout de pantalla con card principal (`.cartera-main-card`) que ocupa hasta la parte inferior del viewport visible (`flex: 1`), toolbar con paginador superior, tabla con scroll interno y controles de formulario.
   - **`[nombre_modulo].js`**: Lógica funcional interactiva (dataset `MOCK_DATA` con 20-30 registros, paginación dinámica superior, filtros tipo Excel `ChecklistPopover`, arrastre de columnas `ColumnResizer`, selector `Columns3`, apertura de Right Drawer y conmutador sincrónico de tema).
   - **`datos_[nombre_modulo].md`**: Documento de especificación de datos basado en [plantilla_datos_necesarios.md](../mock/plantilla_datos_necesarios.md), detallando campos JSON, tipos de datos, filtros y fixtures para el integrador backend.
   - **`assets/` (Directorio Local de Identidad de Marca)**: Subcarpeta con copias locales de los logos corporativos (`Jolifoods.svg`, `Joli.svg`, `logoJoli.png`) copiados desde `.sdd/assets/`, asegurando que el prototipo sea 100% portable y offline al abrirse o trasladarse entre computadores.

   **Directrices Clave de la Interfaz**:
   - **Identidad Corporativa y Assets Locales Portables**: La Top Navbar debe incluir el logo Jolifoods enlazado relativamente desde `./assets/Jolifoods.svg` (con fallback a `./assets/logoJoli.png`) y favicon corporativo. Prohibido enlaces absolutos a rutas locales de usuario o imágenes rotas. (Ver [logo.md](../components/login/logo.md)).
   - **Layout 100% Horizontal a lo Largo de la Pantalla (PROHIBIDO CENTRAR EL FRONTEND)**: Queda estrictamente prohibido generar interfaces encogidas o centradas en el medio de la pantalla (prohibido `max-w-xl mx-auto`). Todo desarrollo debe extenderse horizontalmente ocupando el 100% del ancho del viewport de borde a borde para maximizar la productividad y visibilidad de datos. (Ver [layout_rules.md](../components/layout/layout_rules.md) y [sidebar.md](../components/layout/sidebar.md)).
   - **Título Directo de la Página en Lado Izquierdo (Cero Breadcrumbs de Navegación)**: (Ver [navbar.md](../components/layout/navbar.md)).
   - **Paginador Superior Integrado en Toolbar (Estándar bi/cartera)**: El paginador se coloca **ARRIBA DE LA TABLA**, dentro de la toolbar superior (`.cartera-table-header-toolbar.pagination-container`), unificando selector de filas ("Mostrar [10 v] por página"), buscador, filtros activos, visibilidad de columnas, info de registros y botonera de páginas (`<<`, `<`, 1, 2, `>`, `>>`).
   - **Card Contenedora hasta Abajo del Viewport (`.cartera-main-card`)**: La card principal tiene `flex: 1; min-height: 420px; display: flex; flex-direction: column; overflow: hidden;` extendiéndose hasta el borde inferior de la pantalla sin dejar espacios vacíos desaprovechados. La tabla interna tiene `flex: 1; overflow: auto; min-height: 250px;`.
   - **Estilo Obligatorio en Controles de Formulario e Inputs (Modales y Drawers)**: Queda prohibido el uso de inputs nativos sin estilo. Todo formulario usa `.form-field` / `.drawer-form-field`, etiqueta `.form-label` (uppercase 0.72rem, `--text-secondary`) y control `.input-control` / `.drawer-input-control` con altura de 38px, fondo `var(--input-bg)`, borde `var(--input-border)` y halo de foco de acento.
   - **Acciones Agrupadas**: Toolbar compacta de 28px (`.cartera-compact-action-box`) y acciones por fila en contenedor de 26px (`.cartera-row-actions-group`) con divisores de 1px.
   - **Cero Textos Verdes o Azules Innecesarios**: Los códigos de registro y datos usan tipografía monospace neutra (`var(--text-primary)` o `var(--text-secondary)`). Colores reservados exclusivamente para badges de estado (`OPTIMO`, `PAGADA`).
   - **ConfirmModal Canónico con Justificación de Auditoría**: Diálogo con halo cromático, textarea a ancho 100% (`.joli-modal-textarea`), contador dinámico (`0 / 10 mín.`) y botón confirmar condicionado a mínimo 10 caracteres para acciones críticas ([confirm_modal.md](../components/modal/confirm_modal.md)).
   - **Right Drawer Lateral Obligatorio para Creación y Edición CRUD (`.cartera-sidebar-drawer`) (PROHIBIDO MODALES O PÁGINAS SEPARADAS)**: La creación (`+ Nuevo Registro`) y edición (`Editar`) de cualquier CRUD debe realizarse obligatoriamente desde el panel lateral derecho deslizante de 560px con pie contextual fijo ([drawer.md](../components/drawer/drawer.md)). Queda terminantemente prohibido abrir formularios de CRUD en modales flotantes centrados o navegar a páginas separadas a menos que el usuario lo solicite expresamente.
   - **Centro de Multi-Notificaciones Desplegable**: Popover interactivo con pestañas segmentadas y badges ([notification_popover.md](../components/notification/notification_popover.md)).
   - **Menú Desplegable de Perfil con Salida Segura**: Avatar y nombre con menú flotante respaldado por `ConfirmModal` ([user_profile_dropdown.md](../components/layout/user_profile_dropdown.md)).
   - **Conmutador de Tema**: Alternancia instantánea y sincrónica (`data-theme`, `data-bs-theme`, `style.colorScheme`).

4. **Entrega, Validación y Exención Absoluta de Testing**:
   - El usuario de negocio prueba la pantalla en su navegador con doble clic, verifica flujos, colores y datos y, una vez conforme, entrega la subcarpeta `mock/<nombre_modulo>/` al desarrollador para su codificación definitiva en React + FastAPI.
   - **CERO TESTING EN MODO MOCK**: En esta fase de prototipado queda **terminantemente prohibido y es totalmente innecesario exigir o ejecutar pruebas automáticas, Pytest, Playwright, suites E2E o scripts de validación de endpoints (`validate_endpoints.py`)**, dado que es solo una maqueta visual interactiva sin base de datos ni backend real. Las pruebas automáticas aplican de forma obligatoria únicamente cuando el programador traslada el prototipo al código de producción en `frontend/` y `backend/`.

---

### Si el Usuario responde: [2] SÍ, SOY DESARROLLADOR
La IA procede con las gestiones técnicas de arquitectura y desarrollo:

#### ⚠️ REGLA CRÍTICA DE REUTILIZACIÓN FRONTEND: PROHIBIDO INVENTAR CSS DESDE CERO
> [!CAUTION]
> **OBLIGACIÓN DE CONSUMO DE COMPONENTES YA AUDITADOS**:  
> En el desarrollo de nuevos módulos, vistas o pantallas, queda **TERMINANTEMENTE PROHIBIDO CREAR ARCHIVOS `.css` AISLADOS O IMPROVISADOS** (ej. inventar `users.css`, `productos.css` con reglas CSS ad-hoc no auditadas).  
> **TODO DESARROLLO DEBE ENSAMBLARSE REUTILIZANDO LAS CLASES Y COMPONENTES PROBADOS DE `.sdd/components/`**:  
> - **Tablas**: `.sdd/components/data_table/data_table.md` (`.joli-table`, `.cartera-table-wrapper-full`, `ChecklistPopover`, `ColumnResizer`, `ColumnVisibility`).  
> - **Toolbars y Acciones**: `.sdd/components/button/icon_action_group.md` (`.cartera-compact-action-box` 28px y acciones por fila 26px).  
> - **Filtros**: `.sdd/components/dropdown/expandable_filter_group.md` (`.cartera-topbar`, `.cartera-btn-group`).  
> - **Detalle y Edición**: `.sdd/components/drawer/drawer.md` (`.cartera-sidebar-drawer`).  
> - **Modales**: `.sdd/components/modal/confirm_modal.md` y `modal_dialog.md`.  
> - **Selectores**: `.sdd/components/dropdown/select_filter.md`.  
> - **Tokens**: `variables.css` (Día/Noche).  
> *Inventar CSS nuevo evade la auditoría corporativa y fragmenta el ecosistema.*

#### 📖 PROTOCOLO DE DOCUMENTACIÓN VIVA HOLÍSTICA EN MODO DESARROLLO (`docs/` Y `README.md`)
> [!IMPORTANT]
> **DOCUMENTACIÓN DE CAPACIDADES GLOBALES (PROHIBIDO CHANGELOGS DE MICRO-CAMBIOS)**:  
> En el modo de desarrollo Greenfield, el sistema debe ir documentando progresivamente en la carpeta de documentación del proyecto (`docs/` o especificaciones de módulo) y en el `README.md` principal lo que se va construyendo.  
> 
> **Reglas Inflexibles de Documentación**:
> 1. **Cero Micro-Cambios o Fragmentos**: Queda estrictamente prohibido redactar bitácoras de tareas técnicas puntuales, diffs o ediciones menores (ej. *"se añadió el campo teléfono al formulario"*, *"se corrigió un padding en el botón"*, *"se creó la función validate()"*).
> 2. **Documentación Holística por Componente / Módulo**: Cuando se cree o evolucione una página o componente (ej. la página de `usuarios`), se debe documentar **TODO LO QUE REALIZA LA APLICACIÓN Y EL MÓDULO** de extremo a extremo:
>    - **Propósito y Valor de Negocio**: Qué necesidad operativa resuelve dentro de la organización.
>    - **Capacidades Funcionales Completas**: Listado exhaustivo de todas las operaciones disponibles (búsqueda reactiva, filtros multicriterio tipo Excel, paginación server-side, ciclo de vida de la entidad, activación/suspensión, justificaciones de auditoría).
>    - **Arquitectura de Ejecución**: Desacoplamiento entre la capa de entrega ultra rápida de JSON en FastAPI (`ORJSONResponse`, Pydantic v2) y la capa exclusiva de seguridad en Django (RBAC, permisos y modelos).
>    - **Experiencia de Usuario (UI)**: Uso del Right Drawer para CRUD, modales de confirmación con justificación y componentes auditados de `.sdd/components/`.
> 3. **Contexto del Destino de la Plataforma en el `README.md`**: Con cada nuevo módulo entregado, la IA debe actualizar el `README.md` raíz para mantener vivo el **contexto del destino y visión de la plataforma**:
>    - Visión general del producto y metas organizacionales que resuelve.
>    - Matriz de capacidades activas (catálogo de módulos operativos disponibles).
>    - Estado arquitectónico consolidado del stack técnico (FastAPI + Django + React + Docker).

#### Escenario A: Creación de un Nuevo Proyecto desde Cero
La IA pregunta interactivamente:
1. **Nombre del Proyecto**: Identificador y título visible (ej. `logistica`, `empaque`, `despachos`).
2. **Alcance de Páginas y Módulos**:
   - *(Recomendado)* **Completo Empresarial**: Login SSO, Dashboard KPIs BI Cartera, Usuarios CRUD, Roles RBAC, Bitácora, Perfil, Configuración y Errores 404/403.
   - **Esencial**: Login + Layout Shell + Dashboard mínimo.
   - **Personalizado**: Selección específica de páginas.
3. **Motor de Base de Datos**:
   - PostgreSQL (Estándar Docker Jolifoods puerto 5432).
   - MySQL / MariaDB (Puerto 3306).
   - SQLite (Desarrollo local sin contenedores).
4. **Métodos de Autenticación**:
   - Híbrido: Cédula/Contraseña + Microsoft 365 (Azure AD SSO corporativo).
   - Solo credenciales locales.

#### Escenario B: Creación de un Complemento / Módulo Adicional
*(Consultar la ficha técnica completa en [`02_catalogo_y_menu_de_complementos.md`](./02_catalogo_y_menu_de_complementos.md))*

Cuando el usuario pida agregar una funcionalidad, módulo o complemento a un proyecto existente, la IA **DEBE PRESENTARLE OBLIGATORIAMENTE EL SIGUIENTE MENÚ DE OPCIONES NUMERADO**:

> *"¿Cuál complemento o tipo de módulo deseas crear para el proyecto? Elige una opción del catálogo corporativo SDD:"*

```text
====================================================================================================
               MENÚ DE COMPLEMENTOS Y MÓDULOS CORPORATIVOS — JOLIFOODS (SDD)
====================================================================================================
 [1] Listado Tabular Avanzado (Data Table Tipo Excel)
     -> Incluye: Filtros por columna ChecklistPopover (A-Z/Z-A, buscador reactivo, botón 'Solo'),
        Paginación server-side Anti-N+1, Selector de columnas visibles (Columns3) y Exportador a Excel.
     -> Ref: .sdd/components/data_table/data_table.md | checklist_popover.md | pagination.md

 [2] Tablero de Control y Métricas KPI (Estándar BI Cartera)
     -> Incluye: Rejilla inteligente .cartera-kpi-row, Cards interactivas con halo cromático,
        indicador flotante 'FILTRO ACTIVO', Skeleton loaders y filtrado dinámico cruzado.
     -> Ref: .sdd/components/kpi/kpi_cards.md | .sdd/greenfield/pages/dashboard/

 [3] Panel Lateral Deslizable de Detalle o Edición (Drawer / Slide-Over)
     -> Incluye: Deslizamiento lateral (sm: 400px, md: 600px, lg: 840px), backdrop blur,
        scroll independiente y pie de acciones fijo sin perder el contexto de la tabla.
     -> Ref: .sdd/components/drawer/drawer.md

 [4] Selector Inteligente Tipo Búsqueda (Searchable SelectFilter)
     -> Incluye: Reemplazo total de <select> nativo, buscador reactivo en vivo, badges,
        navegación completa por teclado (flechas y Enter) y soporte para catálogos extensos.
     -> Ref: .sdd/components/dropdown/select_filter.md

 [5] Diálogo Modal de Confirmación y Seguridad (ConfirmModal)
     -> Incluye: Sustituto de confirm() nativo con portal, backdrop blur, icono con halo
        de color (danger, warning, primary), spinner asíncrono y opción emphasizeCancel.
     -> Ref: .sdd/components/modal/confirm_modal.md

 [6] Sistema de Alertas y Notificaciones Asíncronas (Toast Notification)
     -> Incluye: Notificaciones flotantes no bloqueantes (success, error, warning, info),
        auto-cierre inteligente, icono contextual y botón opcional de acción/deshacer.
     -> Ref: .sdd/components/toast/toast_notification.md

 [7] Guardián de Resiliencia ante Despliegues (Global Error Boundary)
     -> Incluye: Captura de excepciones globales y autorecarga inteligente ante 'ChunkLoadError'
        (evita pantallas blancas tras compilar nuevas versiones en producción).
     -> Ref: .sdd/components/error_boundary/error_boundary.md

 [8] Alerta Desacoplada de Sesión Expirada (Session Expiration Modal)
     -> Incluye: Interceptor de errores 401 por evento desacoplado (SESSION_EXPIRED_EVENT),
        bloqueo de interfaz y redirección segura preservando la URL de origen.
     -> Ref: .sdd/components/modal/session_expiration_modal.md

 [9] Pantalla de Estado Vacío Ilustrada (Empty State)
     -> Incluye: Variantes para búsqueda sin resultados, bandejas vacías o errores,
        con iconos grandes, mensajes constructivos y botones de llamada a la acción (CTA).
     -> Ref: .sdd/components/empty_state/empty_state.md

[10] Matriz de Control de Acceso por Roles (Módulo RBAC)
     -> Incluye: Pantalla administrativa para asignar permisos por módulo (ver, crear, editar,
        eliminar, exportar) con protección de roles de sistema y auditoría obligatoria.
     -> Ref: .sdd/greenfield/pages/roles/ | .sdd/model/roles/spec_model_roles_permisos.md

[11] Flujo Obligatorio de Activación y Cambio de Clave (Primer Ingreso)
     -> Incluye: Pantalla forzada para usuarios con debe_cambiar_password = true, medidor
        de entropía visual en tiempo real (Débil a Fuerte) y validación de reglas estrictas.
     -> Ref: .sdd/greenfield/pages/primer_ingreso/

[12] Capa Backend de Alta Velocidad FastAPI (Zero N+1)
     -> Incluye: Servidor ASGI híbrido (Django + FastAPI /fast), consultas con select_related
        y .values(), esquemas Pydantic y refresco automático de conexiones a la base de datos.
     -> Ref: .sdd/stack/asgi_hybrid_architecture.md | asgi_template.py
====================================================================================================
```

#### Preguntas de Seguimiento para el Complemento Seleccionado:
Una vez que el usuario elija la opción del menú, la IA formula las preguntas específicas:
1. **Destino o Ubicación**: ¿Deseas incorporarlo en el proyecto o carpeta actual, en un proyecto nuevo o como un módulo independiente?
2. **Entidad y Atributos**: ¿Cuál es el nombre de la entidad y qué campos o columnas principales manejará?
3. **Privilegios (RBAC)**: ¿Qué perfiles (`ADMIN`, `OPERADOR`, etc.) tendrán acceso a este complemento?

---

## 1.2. Protocolo Guiado y Recomendaciones de Arquitectura para Páginas

Cuando el usuario exprese la intención de **crear o rediseñar una página** (por ejemplo: *"vamos a crear un CRUD"*, *"quiero una vista de reportes"*, *"diseñemos una pantalla de pedidos"*), la Inteligencia Artificial **NO DEBE GENERAR CÓDIGO DIRECTAMENTE**. 

Debe actuar como un Arquitecto de Software Consultor y guiar interactivamente al usuario con las siguientes preguntas y recomendaciones:

### Paso 0: Identificación Inicial de Perfil (Mandatorio)

> **REGLA OBLIGATORIA**:
> La Inteligencia Artificial **NUNCA DEBE ASUMIR UN TEMA O DOMINIO POR DEFECTO** (ej. clima, ventas, pedidos) ni asumir el perfil técnico de la persona.
> Lo primero que debe consultar es el rol y el tema:

> *"¡Hola! Antes de iniciar, para adaptar las opciones y entregables a tu perfil:*
> *1. **¿Eres desarrollador de software o tienes un perfil no técnico / de negocio?***
>    - **Perfil No Técnico / Negocio**: Se activa la ruta No-Code y se generan prototipos visuales interactivos autónomos (HTML + Array JSON + .md de datos) listos para abrir con doble clic y entregar al integrador.
>    - **Perfil Desarrollador / Técnico**: Se procede con el diseño de arquitectura técnica, esquemas Pydantic/FastAPI, modelos Django ORM, Docker y componentes React 19.
> *2. **¿Qué módulo o temática de negocio deseas construir?** (Ej. Ventas, Inventario, Clima, Cartera, Producción, etc.)"*

---

### Paso 1: Identificar el Arquetipo de Página
Una vez confirmado el perfil y el tema, la IA presenta el tipo de pantalla:

> *"¿Qué arquetipo de pantalla deseas construir para este módulo?"*

- **[A] Gestión de Entidad / CRUD Operativo**: Listado con tabla, filtros, buscador y creación/edición/eliminación.
- **[B] Tablero de Control / Dashboard**: Métricas KPI en cabecera, gráficos, bitácora de actividad y alertas en vivo.
- **[C] Consulta Tabular / Reporte Analítico**: Tabla masiva con exportación a Excel, ordenamiento avanzado y filtros de auditoría.
- **[D] Formulario de Proceso / Asistente por Pasos (Wizard)**: Captura progresiva secuencial (Paso 1, 2, 3 con `StepperWizard`).
- **[E] Dashboard de Uso, Adopción y Mejora Continua (SDLC)**: Medición de uso real por los usuarios, ranking de funciones más usadas, micro-encuestas in-app y planificación de sprints evolutivos.
- **[F] Acta / Inspección con Firma Multi-Firmante**: Aprobaciones de despacho, control de calidad y sellado criptográfico ISO con geolocalización.


---

### Paso 2: Recomendar la Experiencia de Creación y Edición (Modal vs Drawer)
Si la página es un CRUD o requiere captura de datos, la IA pregunta y recomienda:

> *"Para crear o editar registros en este módulo, ¿cómo prefieres la experiencia de usuario?"*

```text
----------------------------------------------------------------------------------------------------
           OPCIONES DE EXPERIENCIA PARA FORMULARIOS DE CAPTURA / EDICIÓN
----------------------------------------------------------------------------------------------------
 (1) [Recomendado para 1 a 6 campos] Ventana Modal Centrada (ModalDialog)
     -> Ventajas: Enfoque rápido, diálogo centrado con backdrop blur, excelente para operaciones breves
        (ej. crear rol, asignar celular, suspender cuenta, cambiar estado).
     -> Ref: .sdd/components/modal/modal_dialog.md

 (2) [Recomendado para formularios extensos o cuando se consulta la tabla] Panel Lateral Deslizable (Drawer)
     -> Ventajas: Slide-over lateral desde la derecha (sm: 400px, md: 600px, lg: 840px) con scroll
        independiente y pie fijo. Permite inspeccionar o editar sin perder de vista la tabla de fondo.
     -> Ref: .sdd/components/drawer/drawer.md

 (3) Pantalla Completa Dedicada (Página /nueva y /editar/:id)
     -> Ventajas: Ideal para entidades con más de 15 campos, múltiples pestañas y anexos documentales.
----------------------------------------------------------------------------------------------------
```

---

### Paso 3: Configurar los Componentes de la Tabla (Menú Interactivo de Tabla)
Si la página incluye una tabla de datos, la IA le muestra la lista de capacidades disponibles para que el usuario elija o confirme la configuración recomendada:

> *"Para la tabla de datos, he preseleccionado el estándar empresarial Jolifoods. ¿Deseas incluir todos estos componentes o ajustar la lista?"*

```text
====================================================================================================
               COMPONENTES DISPONIBLES PARA LA TABLA DE DATOS (DATA TABLE)
====================================================================================================
 [x] (1) Filtros de Columna Tipo Excel (ChecklistPopover en cada <th>)
         -> Orden A-Z / Z-A, buscador reactivo, casillas con conteo (N) y botón táctico 'Solo'.
 [x] (2) Paginador Server-Side (Pagination)
         -> Resumen 'Mostrando X a Y de Z', elipsis de páginas y selector de filas (10, 25, 50, 100).
 [x] (3) Exportador Limpio a Excel (ExportExcelButton)
         -> Descarga .xlsx con auto-ajuste de anchos de columna y respeto estricto a los filtros activos.
 [x] (4) Selector de Columnas Visibles (Columns3 Toggle)
         -> Desplegable para ocultar/mostrar columnas con persistencia en el navegador.
 [x] (5) Buscador Reactivo General
         -> Búsqueda en tiempo real con debounce y botón 'X' para limpiar.
 [x] (6) Botón 'Restablecer Filtros' (FilterX)
         -> Aparece solo cuando hay filtros activos con contador dinámico (N) para limpiar en un clic.
 [x] (7) Cabeceras Fijas (Sticky Headers)
         -> Encabezados pegajosos que no se pierden al hacer scroll vertical en listados largos.
 [x] (8) Tarjetas de Resumen KPI Superiores (Estándar BI Cartera)
         -> 3 a 5 tarjetas superiores que actúan como filtros cruzados rápidos al hacer clic en ellas.
====================================================================================================
```

---

### Paso 4: Normativa Obligatoria de Controles Internos
La IA debe asegurar e informar al usuario que se aplicarán automáticamente las siguientes reglas de calidad:
- **Selects**: Se implementará `SelectFilter` (Searchable Select con buscador interactivo y teclado). Prohibido el `<select>` nativo.
- **Confirmaciones**: Acciones destructivas o cambios de estado usarán `ConfirmModal` corporativo. Prohibido `window.confirm()`.
- **Notificaciones**: Éxitos y errores usarán `ToastNotification` corporativo. Prohibido `window.alert()`.
- **Cero Registros**: Si la tabla o los filtros no arrojan resultados, se renderizará el componente `EmptyState`.

---

## 2. Estructura Canónica de `.sdd/`

El repositorio de especificaciones se organiza de forma modular y jerárquica:

```
.sdd/
├── assets/                                    # Identidad vectorial oficial (Jolifoods.svg, Joli.svg)
├── components/
│   ├── variables.css                          # Tokens maestros y selector Modo Noche / Día
│   ├── variables.md
│   ├── README.md                              # Catálogo maestro de componentes
│   ├── login/                                 # Componentes atómicos de autenticación y restablecimiento
│   │   ├── logo.md
│   │   ├── card.md
│   │   ├── input_field.md
│   │   ├── button_primary.md
│   │   ├── button_microsoft.md
│   │   ├── feedback_alerts.md
│   │   ├── recovery_form.md
│   │   ├── login_form.md
│   │   └── email_recovery_template.md
│   ├── layout/                                # Componentes de navegación y estructura general
│   │   ├── navbar.md
│   │   └── sidebar.md
│   ├── kpi/                                   # Tarjetas de Indicadores KPI (Estándar BI Cartera)
│   │   └── kpi_cards.md                       # Rejilla inteligente, clickeables como filtros y skeletons
│   ├── data_table/                            # Componentes de gestión de datos y listados
│   │   ├── data_table.md                      # Paginación server-side Anti-N+1, buscador debounce y export
│   │   └── checklist_popover.md               # Filtro por columna desplegable tipo Excel
│   ├── modal/                                 # Diálogos y confirmaciones accesibles
│   │   ├── modal_dialog.md                    # Variantes sm, md, lg, xl con focus trap y blur
│   │   └── confirm_modal.md                   # Reemplazo de confirm() nativo con portal y spinner
│   ├── badge/                                 # Indicadores de estado y roles
│   │   └── badge_status.md                    # Badges activos, inactivos, admin, operador, etc.
│   ├── dropdown/                              # Selectores y filtros avanzados
│   │   └── select_filter.md                   # Select tipo búsqueda interactivo con teclado
│   ├── toast/                                 # Notificaciones flotantes
│   │   └── toast_notification.md              # Toast con auto-cierre y acción de deshacer
│   ├── pagination/                            # Paginación corporativa
│   │   └── pagination.md                      # Selector por página, elipsis y resumen numérico
│   ├── export/                                # Utilidades de exportación de datos
│   │   └── excel_export.md                    # Exportación a Excel respetando filtros
│   ├── empty_state/                           # Vistas y tablas vacías
│   │   └── empty_state.md                     # Mensajes amigables y llamadas a la acción
│   ├── services/                              # Comunicación HTTP
│   │   └── api_client.md                      # Doble cliente Axios (Django + FastAPI) con interceptores
│   ├── context/                               # Estado global
│   │   └── auth_context.md                    # AuthContext con tipado de usuario, RBAC y tema
│   ├── routing/                               # Enrutamiento y control de acceso
│   │   └── protected_route.md                 # ProtectedRoute con validación RBAC y pantalla de carga
│   ├── drawer/                                # Panel lateral deslizable
│   │   └── drawer.md                          # Slide-over para inspección y edición de registros
│   └── error_boundary/                        # Captura y rescate de errores
│       └── error_boundary.md                  # Auto-recarga por ChunkLoadError y pantalla de rescate
├── model/                                     # Especificaciones formales de datos y persistencia
│   ├── README.md                              # Catálogo maestro de modelos
│   ├── login/                                 # Entidades de identidad y credenciales
│   │   ├── README.md (ERD)
│   │   ├── spec_model_usuario.md
│   │   ├── spec_model_sesion_auditoria.md
│   │   ├── spec_model_restablecimiento.md
│   │   ├── esquema_sql_canonico.md
│   │   └── implementacion_django_orm.md
│   ├── auditoria/                             # Trazabilidad inmutable de eventos
│   │   └── spec_model_bitacora.md
│   └── roles/                                 # Control de Acceso Basado en Roles (RBAC)
│       └── spec_model_roles_permisos.md
├── stack/                                     # Infraestructura, dependencias y automatización
│   ├── README.md
│   ├── asgi_hybrid_architecture.md            # Arquitectura híbrida Django + FastAPI (Zero N+1)
│   ├── asgi_template.py                       # Plantilla de enrutador ASGI universal
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── entrypoint.sh                          # Orquestación y migraciones automáticas en Docker
│   ├── seed_data.py                           # Carga de datos semilla idempotente (Admin y Roles)
│   ├── requirements.txt                       # Librerías consolidadas backend
│   ├── package.json                           # Librerías consolidadas frontend
│   ├── healthcheck.py                         # Sonda de salud y monitoreo FastAPI
│   ├── settings_security_template.py          # Plantilla Django de seguridad pre-auditada
│   ├── init_project.py                        # Scaffolding automatizado con creación de .venv
│   └── init_project.ps1                       # Scaffolding PowerShell para Windows
└── greenfield/
    ├── README.md                              # Manifiesto y visión del ecosistema
    ├── SPEC_GUIDE.md                          # Esta guía maestra de desarrollo
    ├── 00_normativa_buenas_practicas_y_auditoria.md # Normativa de Conformidad y Hardening (100/100)
    ├── 02_catalogo_y_menu_de_complementos.md  # Catálogo interactivo y fichas técnicas de complementos
    ├── 03_asistente_interactivo_diseno_paginas.md # Asistente de decisión arquitectónica (Modal vs Drawer, Tablas)
    ├── 04_menus_de_seleccion_por_componente.md # Menús de variantes por componente (KPI, Tablas, Modales, etc.)
    ├── config_referencia.env.example          # Variables de entorno universales
    └── pages/
        ├── README.md                          # Catálogo de páginas del sistema
        ├── login/                             # Módulo de Login (Suite completa SDD 01 a 10)
        │   ├── README.md
        │   ├── 01_requisitos_funcionales_y_negocio.md
        │   ├── 02_arquitectura_y_maquina_estados.md
        │   ├── 03_contrato_api_y_modelos_datos.md
        │   ├── 04_analisis_patrones_referencia.md
        │   ├── 05_seguridad_auditoria_y_hardening.md
        │   ├── 06_ui_ux_diseno_y_accesibilidad.md
        │   ├── 07_plan_de_pruebas_y_matriz_qa.md
        │   ├── 08_guia_de_implementacion_para_ia.md
        │   ├── 09_flujo_restablecimiento_contrasena.md
        │   └── 10_healthcheck_y_monitoreo_infraestructura.md
        ├── layout/                            # Layout Maestro (App Shell post-login)
        │   ├── README.md
        │   └── 01_layout_maestro_especificacion.md
        ├── dashboard/                         # Tablero Principal (KPIs, Telemetría, Actividad)
        │   ├── README.md
        │   └── 01_dashboard_especificacion.md
        ├── usuarios/                          # Gestión de Usuarios y Roles (CRUD Paginado)
        │   ├── README.md
        │   └── 01_usuarios_crud_especificacion.md
        ├── auditoria/                         # Bitácora de Auditoría (Trazabilidad inmutable)
        │   ├── README.md
        │   └── 01_auditoria_logs_especificacion.md
        ├── profile/                           # Perfil y Seguridad (Cambio clave, Sesiones activas)
        │   ├── README.md
        │   └── 01_perfil_usuario_especificacion.md
        ├── not_found/                         # Páginas de Error Corporativas (404, 403, 500)
        │   ├── README.md
        │   └── 01_errores_404_403_especificacion.md
        ├── roles/                             # Roles y Permisos (RBAC Matricial)
        │   ├── README.md
        │   └── 01_roles_permisos_especificacion.md
        ├── primer_ingreso/                    # Activación forzada de cuenta y cambio de clave
        │   ├── README.md
        │   └── 01_primer_ingreso_especificacion.md
        └── configuracion/                     # Configuración y Parámetros del Sistema
            ├── README.md
            └── 01_configuracion_sistema_especificacion.md
```

---

## 3. Estructura Objetivo de un Proyecto Creado a partir del SDD

Cualquier proyecto nuevo que implemente el módulo de login a partir de este `.sdd` estructurará sus directorios siguiendo este Blueprint canónico:

```
<project-root>/
├── .env                              # Variables de entorno locales configuradas
├── .env.example
├── .gitignore                        # Reglas de exclusión de git (.venv, node_modules, .env, etc.)
├── .venv/                            # Entorno virtual Python aislado para el IDE y herramientas locales
├── .vscode/                          # Configuración de intérprete Python para el editor
│   └── settings.json
├── README.md
├── docker-compose.yml
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── src/
│       ├── schemas/          # Esquemas de validación Zod (según 03_contrato_api)
│       ├── types/            # Interfaces TypeScript tipadas
│       ├── services/         # Clientes de red y llamadas a API
│       ├── context/          # Estado global de autenticación (AuthContext)
│       ├── hooks/            # Hooks de lógica de formulario (useLoginForm)
│       ├── components/
│       │   └── auth/         # Componentes UI (LoginForm, SocialLogin, Feedback)
│       └── pages/
│           └── LoginPage.tsx # Ensamblaje de la página
│
└── backend/
    ├── requirements.txt
    ├── manage.py
    └── apps/
        └── auth_core/
            ├── models.py     # Modelo Usuario y sesiones
            ├── serializers.py# Serializadores y validadores DRF
            ├── views.py      # Controladores de login, SSO y refresh
            ├── urls.py       # Enrutamiento de endpoints
            ├── security.py   # Rate limiting, hashing y auditoría
            └── middleware.py # Inyección de sesión y cookies seguras
│
└── pruebas/                  # <-- UBICACIÓN OBLIGATORIA DE PRUEBAS EN LA RAÍZ (MODO GREENFIELD)
    ├── conftest.py           # Configuración y fixtures globales de Pytest
    ├── unitarias/            # Pruebas unitarias de servicios, schemas y helpers
    ├── integracion/          # Pruebas de endpoints FastAPI (TestClient) y Django (APIClient)
    └── e2e/                  # Pruebas de humo y Playwright
```

---

## 4. Instrucciones de Ejecución para la IA

Cuando se le pida a la IA: *"Crea el login a partir del SDD"*:
1. Leer los complementos `01` a `08` de `.sdd/greenfield/pages/login/`.
2. Tomar el **Blueprint canónico** anterior para crear los directorios en el espacio de trabajo objetivo.
3. **AISLAMIENTO OBLIGATORIO DE PYTHON (`.venv`)**: Crear inmediatamente el entorno virtual en la raíz del proyecto (`python -m venv .venv`), configurar `.vscode/settings.json` vinculando el intérprete (`${workspaceFolder}/.venv/Scripts/python.exe`), e instalar las librerías exclusivamente usando el ejecutable de dicho entorno (`.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt`). **PROHIBIDO TERMINANTEMENTE ejecutar `pip install` o comandos de Python en el entorno global del equipo anfitrión.**
4. Implementar los contratos de `03_contrato_api_y_modelos_datos.md` sin alterar los nombres de campos ni códigos de error.
5. Aplicar las normas de seguridad de `05_seguridad_auditoria_y_hardening.md` (Cookies HttpOnly, Rate Limiting, sanitización).
6. Seguir el diseño y tokens de `06_ui_ux_diseno_y_accesibilidad.md`.
7. Generar las pruebas prescritas en `07_plan_de_pruebas_y_matriz_qa.md` para garantizar cobertura total.
8. **UBICACIÓN OBLIGATORIA DE PRUEBAS EN LA RAÍZ (`pruebas/`)**: Si la IA necesita crear, redactar o ejecutar pruebas automatizadas, pruebas de integración o scripts de validación, **QUEDA TERMINANTEMENTE PROHIBIDO crear archivos o carpetas de pruebas dentro de `backend/`**. Debe crear obligatoriamente una carpeta en la raíz del proyecto llamada `pruebas/` (`<project-root>/pruebas/`), manteniendo el código productivo de `backend/` completamente limpio de archivos de test.


---

## 5. Mocks Autónomos en HTML para Usuarios No Técnicos y el Integrador

Para permitir que cualquier persona sin conocimientos de programación proponga una nueva pantalla o dashboard y se la entregue al integrador:

1. **Metodología y Matriz de Equivalencias**:
   - Consultar la guía completa en [`05_metodologia_mocks_no_programadores.md`](./05_metodologia_mocks_no_programadores.md).
2. **Plantilla Base Autónoma**:
   - [mockup_template.html](../components/mockup_template.html): Archivo HTML con Bootstrap 5, Lucide Icons, tokens Jolifoods, modo noche y sin dependencias locales (abre con doble clic).
3. **Ejemplo en Vivo (Dashboard de Ventas)**:
   - [mockup_dashboard_ventas_ejemplo.html](pages/dashboard/mockup_dashboard_ventas_ejemplo.html): Dashboard con 4 KPIs interactivos, tabla con filtros Excel simulados y conmutador de tema.
4. **Regla de Integración**: El programador **NO debe crear CSS nuevo**. Mapea cada bloque del HTML directamente a los componentes React documentados en `.sdd/components/`.
5. **Las 15 Reglas de Oro Visuales para Mocks y Nuevas Pantallas**:
   - Consultar la guía completa de directrices visuales en [mock/README.md](../mock/README.md):
     1. Layout Full-Width por defecto (Cero Sidebar a menos que se solicite expresamente).
     2. Título directo de la página a la izquierda del TopHeader (Cero breadcrumbs de navegación `>` y cero textos verdes en títulos).
     3. Acciones agrupadas tanto en toolbar (`.cartera-compact-action-box`) como por fila (`.cartera-row-actions-group`).
     4. Cero textos verdes o azules innecesarios en tablas (códigos e IDs en tipografía monospace neutra).
     5. Diálogo modal canónico con justificación auditada, textarea al 100% y contador dinámico ([confirm_modal.md](../components/modal/confirm_modal.md)).
     6. Panel lateral deslizable para formularios ([drawer.md](../components/drawer/drawer.md)).
     7. Filtros expandibles segmentados ([expandable_filter_group.md](../components/dropdown/expandable_filter_group.md)).
     8. Centro de Multi-Notificaciones en TopHeader ([notification_popover.md](../components/notification/notification_popover.md)).
     9. Menú desplegable de perfil con salida segura ([user_profile_dropdown.md](../components/layout/user_profile_dropdown.md)).
     10. Paginación superior integrada en toolbar y card contenedora hasta abajo del viewport ([pagination.md](../components/pagination/pagination.md) y [data_table.md](../components/data_table/data_table.md)).
     11. Filtros de columna tipo Excel interactivos ([checklist_popover.md](../components/data_table/checklist_popover.md)).
     12. Columnas ajustables/redimensionables ([column_resizer.md](../components/data_table/column_resizer.md)) y selector de visibilidad de columnas ([column_visibility.md](../components/data_table/column_visibility.md)).
     13. Conformidad absoluta de variables CSS y tematización dual Día/Noche sin textos invisibles ([variables.md](../components/variables.md)).
     14. Estilo corporativo obligatorio en controles de formulario e inputs dentro de Modales y Drawers ([drawer.md](../components/drawer/drawer.md)).
     15. Arquitectura modular obligatoria de 4 archivos separados por módulo (`.html`, `.css`, `.js`, `datos_*.md`) con cero HTML monolítico ([mock/README.md](../mock/README.md)).




