# Catálogo de Innovaciones y Mejores Prácticas de Proyectos del Ecosistema
## Referencia de Ingeniería Cruzada — Jolifoods / Greenyard (SDD)

Este documento documenta **lo mejor de cada uno de los proyectos desarrollados en la organización** (`bi`, `app_tic`, `tiendita`, `vibra`, `contenedores`, `porterias`, `color`, `instalador Joli`). Su propósito es que cualquier desarrollador técnico o líder senior cuente con las bases conceptuales, arquitectónicas y de código para reutilizar estas soluciones en proyectos futuros sin inventar la rueda.

---

## 🗺️ Mapa de Excelencia Técnica por Proyecto

```text
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│      BI      │   │   APP_TIC    │   │   TIENDITA   │   │ CONTENEDORES │
│ Tutoriales   │   │ MCP & Agentes│   │ Firma, PDF & │   │ Biometría    │
│ Divididos &  │   │ Hitos/Sprints│   │ Escáner QR   │   │ Facial       │
│ Data Quality │   │ Grid Integral│   │ Dotaciones   │   │ WebRTC       │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
       ▲                  ▲                  ▲                  ▲
       │                  │                  │                  │
 ──────┴──────────────────┴──────────────────┴──────────────────┴──────
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  PORTERÍAS   │   │    VIBRA     │   │    COLOR     │   │  INSTALADOR  │
│ Modo Kiosco  │   │ Calendario   │   │ ColorLab &   │   │ Empaquetado  │
│ PWA Tablets  │   │ Cuadrillas & │   │ Mezcla de    │   │ Offline      │
│ Check-in Ráp │   │ Novedades    │   │ Pigmentos    │   │ Desktop .exe │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
```

---

## 1. Proyecto `bi` (Business Intelligence & Datahub)

### 🌟 Innovaciones Destacadas:
1. **Tutorial Interactivo Dividido (`SplitTutorialModal`)**:
   - **Problema resuelto**: Los usuarios de negocio no sabían conectar Power BI o Excel a la base de datos PostgreSQL.
   - **Solución**: Un modal con vista dividida (Split Screen). A la izquierda, datos de conexión con botón "Copiar" en un clic; a la derecha, carrusel guiado con capturas de pantalla, zoom interactivo (`ImageLightbox`) y resaltado automático de botones entre comillas.
   - **Selector de Tutorial (`TutorialChooserModal`)**: Diálogo previo que permite al usuario escoger entre Power BI o Excel antes de iniciar el recorrido.
2. **Módulo de Calidad de Datos (`Data Quality - DQ`)**:
   - Reglas de validación en tiempo real para detectar registros huérfanos, inconsistencias de formato y anomalías en tablas maestras.
3. **Gestión de Tickets PQRS**:
   - Módulo integrado para registrar, clasificar y dar seguimiento a peticiones, quejas, reclamos y solicitudes de analítica.

---

## 2. Proyecto `app_tic` (Gestión Ágil de Proyectos TIC)

### 🌟 Innovaciones Destacadas:
1. **Gobernanza de Proyectos en Cuadrícula (`GridTIC`)**:
   - Seguimiento integral de proyectos mediante 6 entidades enlazadas: **Hitos, Sprints, Decisiones de Arquitectura (ADRs), Compromisos, Tareas y Línea de Tiempo**.
2. **Integración Nativa con Agentes de IA vía MCP (Model Context Protocol)**:
   - Exposición de endpoints de control y herramientas que permiten a agentes autónomos consultar tareas pendientes, crear decisiones y auditar el avance del sprint sin intervención humana manual.
3. **Módulo ACPM (Acciones Correctivas, Preventivas y de Mejora)**:
   - Registro con consecutivo formal, seguimiento de causas raíz y subida de evidencias hacia `backend/media/`.

---

## 3. Proyecto `tiendita` (Entrega de Dotaciones y Beneficios)

### 🌟 Innovaciones Destacadas:
1. **Firma Digital Táctil con Auto-Recorte (`SignatureModal`)**:
   - Captura sobre Canvas con algoritmo `cropToSignature` que elimina los espacios vacíos y genera un PNG transparente Base64 optimizado para almacenamiento.
2. **Visor de Documentos PDF en Canvas (`PdfPreviewFrame`)**:
   - Renderizado con `pdfjs-dist` en elementos `<canvas>` simulando hojas físicas apiladas con sombras, zoom escalonado (`ZoomControls`) y navegación sin depender del plugin nativo del navegador.
3. **Lector de Código de Barras y QR por Cámara (`ScannerModal`)**:
   - Integración con `html5-qrcode` para lectura instantánea de etiquetas de dotación o cédulas con cierre automático al detectar lectura válida.
4. **Selector de Modalidad de Entrega (`EntregaTypeModal`)**:
   - Flujo diferenciado si la entrega es presencial en planta o despacho a domicilio.

---

## 4. Proyecto `contenedores` (Inspección y Logística de Carga)

### 🌟 Innovaciones Destacadas:
1. **Escáner Biométrico Facial WebRTC (`FacialScanner`)**:
   - Captura de video en tiempo real con cortinilla SVG oscura y guía ovalada central que asegura que el rostro del conductor u operario esté debidamente encuadrado e iluminado antes de disparar la foto.
2. **Inspección Física y Control de Cubicaje**:
   - Registro de estado estructural de contenedores (cerraduras, sellos, pisos, paredes) con captura fotográfica móvil directa hacia `backend/media/` y cálculo de capacidad volumétrica.

---

## 5. Proyecto `porterias` (Control de Acceso y Vigilancia)

### 🌟 Innovaciones Destacadas:
1. **Modo Kiosco y Aplicación PWA Offline (`PwaInstallBanner`)**:
   - Diseñado para operar en tablets Android/iOS en casetas de seguridad con pantalla táctil, arranque a pantalla completa (*standalone*) y soporte ante micro-cortes de red.
2. **Check-in y Check-out Ultrarrápido de Vehículos**:
   - Interfaz con botones gigantes y teclado numérico adaptado para operarios con guantes o terminales móviles rugerizadas.

---

## 6. Proyecto `vibra` (Talento Humano y Clima Organizacional)

### 🌟 Innovaciones Destacadas:
1. **Calendario Corporativo de Turnos (`CorporateCalendar`)**:
   - Rejilla mensual inteligente que visualiza turnos rotativos, novedades operativas, permisos, incapacidades y vacaciones mediante códigos de color semánticos.
2. **Perfil del Colaborador y Reconocimientos**:
   - Visualización de historial de novedades y cuadro de distinciones de colaboradores.

---

## 7. Proyecto `color` (Laboratorio de Color y Pigmentos - ColorLab)

### 🌟 Innovaciones Destacadas:
1. **Extractor de Paletas y Píxeles desde Imágenes**:
   - Permite al usuario cargar fotos de productos, frutas o materias primas y extraer los códigos RGB/Hex exactos mediante Canvas interactivo.
2. **Algoritmo de Mezcla de Pigmentos Reales (`pigmentos.py`)**:
   - A diferencia de la mezcla aditiva digital (donde rojo + verde da amarillo), modela la **mezcla sustractiva de colorantes físicos/alimentarios**, calculando la fórmula exacta de gotas o gramos de pigmento base para reproducir el tono deseado.

---

## 8. Proyecto `instalador Joli` (Empaquetador y Despliegue Desktop)

### 🌟 Innovaciones Destacadas:
1. **Empaquetado Offline en un Solo Archivo (`.spec` / PyInstaller)**:
   - Permite compilar aplicaciones web/Python en un archivo ejecutable `.exe` autosuficiente con entorno de ejecución embebido para equipos de planta que no tienen acceso a internet ni permisos para instalar Python/Node.
2. **Automatización de Instalación (`autorun.inf` & `build.py`)**:
   - Creación de memorias USB o carpetas compartidas con instalación automatizada en un clic.

---

## 💡 Matriz de Reutilización para Desarrolladores Técnicos y Seniors

| Si necesitas en tu nuevo proyecto... | Reutiliza la arquitectura de: | Componente canónico en SDD: |
| :--- | :--- | :--- |
| Enseñar a conectar Power BI/Excel o guiar paso a paso con fotos | **`bi`** | [`components/tutorial/split_tutorial_walkthrough.md`](../components/tutorial/split_tutorial_walkthrough.md) |
| Automatizar tareas con agentes de IA y registrar ADRs/sprints | **`app_tic`** | [`greenfield/12_protocolo_ciclo_de_vida_sdlc_y_mejora_continua.md`](12_protocolo_ciclo_de_vida_sdlc_y_mejora_continua.md) |
| Capturar firmas táctiles limpias y previsualizar PDFs | **`tiendita`** | [`components/signature/signature_modal.md`](../components/signature/signature_modal.md) y [`pdf_preview_frame.md`](../components/pdf/pdf_preview_frame.md) |
| Validar identidad facial por cámara o escanear QR/Barcode | **`contenedores`** y **`tiendita`** | [`components/biometrics/facial_scanner.md`](../components/biometrics/facial_scanner.md) y [`scanner_modal.md`](../components/scanner/scanner_modal.md) |
| Instalar la app como app nativa en tablets de planta | **`porterias`** | [`components/pwa/pwa_install_banner.md`](../components/pwa/pwa_install_banner.md) |
| Gestionar cuadrillas, turnos rotativos y vacaciones | **`vibra`** | [`components/calendar/corporate_calendar.md`](../components/calendar/corporate_calendar.md) |
| Formular colores reales o mezclar tintes desde fotos | **`color`** | Algoritmos de mezcla sustractiva en `pigmentos.py` |
| Desplegar en computadores sin internet ni Python instalado | **`instalador Joli`** | Plantilla de empaquetado `Instalador_JoliFoods.spec` |
