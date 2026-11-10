# SDD — Desarrollo guiado por especificaciones

Estándar de ingeniería de software de Joli Foods. Reúne normas, plantillas, componentes de interfaz y herramientas de validación para que cualquier persona, sea de desarrollo, de negocio o un asistente de IA, pueda especificar, prototipar, construir y verificar una aplicación de la misma manera.

**Desarrollo guiado por especificaciones** (*Spec-Driven Development*) significa que antes de escribir código se define por escrito qué debe hacer el sistema: requisitos, contrato de datos, pantallas y criterios de aceptación. El código se construye contra esa especificación, y las pruebas automáticas verifican que la cumpla.

---

## 1. Principios

1. **Primero la especificación, después el código.** Los cambios de nivel 2 o mayor tienen propuesta, diseño, tareas y evidencia ([protocolo 14](greenfield/14_protocolo_cambios_atomicos_y_especificaciones_vivas.md)).
2. **Reglas justificadas, no dogmas.** Cada regla dice por qué existe y cuándo admite excepción. Se distingue **DEBE** (obligatorio) de **DEBERÍA** (recomendado, desviable con un ADR). Ver la [normativa](greenfield/00_normativa_buenas_practicas_y_auditoria.md).
3. **Genérico con procedencia.** Los patrones salieron de proyectos reales y cada documento indica su origen, pero la regla se escribe para cualquier proyecto. Procedencia completa: [catálogo de fuentes](greenfield/13_catalogo_innovaciones_y_mejores_practicas_proyectos.md).
4. **Lo que se exige, se verifica.** Toda puerta de calidad tiene un comando que la comprueba ([protocolo 11](greenfield/11_protocolo_pruebas_automaticas_y_testing_e2e.md)).

---

## 2. Estructura

```text
.sdd/
├── greenfield/          Normativa (00), protocolos de ingeniería (01–15), guía de especificación
│   └── pages/           Especificaciones de páginas base: login, layout, usuarios, roles, perfil, auditoría…
├── components/          Catálogo de componentes de interfaz y tokens de diseño (variables.css)
├── model/               Modelos de datos de referencia (SQL de PostgreSQL y Django ORM)
├── stack/               Plantillas de backend, frontend y Docker, generador de proyectos y validador de endpoints
├── mock/                Prototipos HTML sin servidor para validar pantallas con el negocio
├── changes_template/    Plantilla de cambio: proposal, design, tasks, evidence
├── memory/              Plantillas de ADR (decisiones) y aprendizajes
├── assets/              Logos oficiales
└── pruebas/             Pruebas automáticas del propio SDD
```

---

## 3. Cómo empezar

**Si no programa (perfil de negocio):** describa el proceso, los indicadores y las columnas siguiendo la [metodología de prototipos](greenfield/05_metodologia_mocks_no_programadores.md). El resultado es un prototipo HTML que se abre con doble clic, más un contrato de datos para el equipo técnico. Los prototipos no llevan pruebas automatizadas (BP-10).

**Si programa:**

```powershell
python .sdd\stack\init_project.py "Nombre del proyecto"     # crea el proyecto, .venv y el andamiaje de pruebas
cd nombre_del_proyecto
docker compose up --build
.\.venv\Scripts\python.exe -m pytest                        # pruebas del backend
.\.venv\Scripts\python.exe pruebas\validate_endpoints.py    # humo HTTP con la app levantada
```

Luego:

1. Diseñe la pantalla con el [asistente de diseño](greenfield/03_asistente_interactivo_diseno_paginas.md) y el [catálogo de complementos](greenfield/02_catalogo_y_menu_de_complementos.md).
2. Construya con los [componentes](components/README.md) y los [modelos](model/README.md) de referencia.
3. Antes de integrar, pase las [puertas de calidad](greenfield/11_protocolo_pruebas_automaticas_y_testing_e2e.md#5-puertas-de-calidad-ci).

**Si es un asistente de IA:** siga [`stack/agent_harness/AGENTS.md`](stack/agent_harness/AGENTS.md), que se copia a cada proyecto.

---

## 4. Documentos principales

| # | Documento | Para qué |
| :---: | :--- | :--- |
| 00 | [Normativa de buenas prácticas](greenfield/00_normativa_buenas_practicas_y_auditoria.md) | BP-01 a BP-24, fuente única de las reglas |
| 01 | [Evaluación de madurez del SDD](greenfield/01_calificacion_final_ecosistema_sdd.md) | Qué está cubierto, qué se verifica con herramienta y qué falta |
| 02 | [Catálogo de complementos](greenfield/02_catalogo_y_menu_de_complementos.md) | Módulos de negocio listos para usar |
| 03 | [Asistente de diseño de páginas](greenfield/03_asistente_interactivo_diseno_paginas.md) | Entrevista guiada para especificar una pantalla |
| 04 | [Menús por componente](greenfield/04_menus_de_seleccion_por_componente.md) | Opciones de cada componente |
| 05 | [Prototipos para no programadores](greenfield/05_metodologia_mocks_no_programadores.md) | Flujo de prototipo y contrato de datos |
| 06 | [DevOps, CI/CD y calidad](greenfield/06_protocolo_devops_cicd_y_calidad.md) | Ramas, versiones, hooks y pipeline |
| 07 | [Observabilidad](greenfield/07_protocolo_observabilidad_telemetria_apm.md) | Logs, trazas, métricas y SLO |
| 08 | [Migraciones sin interrupción](greenfield/08_protocolo_migraciones_zero_downtime.md) | Expandir y contraer, respaldos |
| 09 | [Gobierno de APIs](greenfield/09_protocolo_gobernanza_apis_y_breaking_changes.md) | Versionado y cambios incompatibles |
| 10 | [Incidentes y post-mortem](greenfield/10_protocolo_incidentes_sre_y_postmortem.md) | Severidades y análisis sin culpables |
| 11 | [Pruebas automáticas](greenfield/11_protocolo_pruebas_automaticas_y_testing_e2e.md) | Qué probar, dónde y con qué puertas |
| 12 | [Ciclo de vida y mejora continua](greenfield/12_protocolo_ciclo_de_vida_sdlc_y_mejora_continua.md) | Fases, roles y priorización |
| 13 | [Fuentes y procedencia de patrones](greenfield/13_catalogo_innovaciones_y_mejores_practicas_proyectos.md) | De qué proyecto salió cada patrón |
| 14 | [Cambios atómicos](greenfield/14_protocolo_cambios_atomicos_y_especificaciones_vivas.md) | proposal, design, tasks, evidence |
| 15 | [Memoria del proyecto](greenfield/15_protocolo_memoria_persistente_y_aprendizaje_agentes.md) | ADR y aprendizajes |
| — | [Guía de especificación](greenfield/SPEC_GUIDE.md) | Cómo escribir una especificación |
| — | [Stack y herramientas](stack/README.md) | Plantillas, generador y validador |

---

## 5. Validación del propio SDD

El SDD tiene pruebas que verifican que sus herramientas funcionan y que la documentación es coherente: enlaces válidos, sin tokens en `localStorage`, rutas canónicas y plantillas que compilan.

```powershell
cd .sdd
python -m venv .venv                                         # una sola vez; no instala paquetes
.\.venv\Scripts\python.exe -m unittest discover -s pruebas -v
```

Solo usan la librería estándar de Python. Ejecútelas antes de publicar cambios al SDD.

---

## 6. Cómo proponer cambios al SDD

1. Un patrón nuevo se documenta de forma genérica, con su nota de **Origen** (proyecto y módulo donde se probó).
2. Si cambia una regla, se actualiza la normativa 00 (fuente única) y no se copia la regla en otros documentos.
3. Las pruebas de la sección 5 deben pasar.
4. Una decisión de arquitectura con alternativas reales se registra como ADR en `memory/adrs/`.
