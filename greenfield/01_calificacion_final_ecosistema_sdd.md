# Evaluación de madurez del SDD

**Fecha de la evaluación**: 2026-11-04
**Alcance**: contenido del repositorio `.sdd/` (protocolos 00–15, catálogo de componentes, `stack/`, `mock/`, `memory/`, `changes_template/`).
**Método**: revisión documental del repositorio. No se midió el uso del SDD en proyectos reales ni se ejecutaron sus plantillas en un proyecto de prueba como parte de esta evaluación.

> Este documento reemplaza una versión anterior que se autocalificaba con 99,7/100 y "CMMI nivel 5". Esa calificación no tenía método ni evidencia: el SDD se calificaba a sí mismo, sin mediciones de uso, y CMMI es un modelo que evalúa procesos de una organización mediante una valoración formal (SCAMPI), no un repositorio de documentos. Aquí no se asignan puntajes; se describe qué está respaldado por una herramienta, qué es solo una norma escrita y qué falta.

---

## 1. Cómo leer esta evaluación

Cada capacidad se clasifica en uno de tres niveles:

| Nivel | Significado |
|---|---|
| **Implementado** | Existe un archivo ejecutable o una plantilla funcional en el SDD que lo genera o lo verifica. |
| **Documentado** | Existe una norma o especificación escrita, pero ninguna herramienta del SDD la aplica ni la comprueba; su cumplimiento depende de la disciplina de cada equipo o de la revisión de código. |
| **Ausente** | Se menciona como objetivo, pero no hay especificación suficiente ni herramienta. |

---

## 2. Estado por área

| Área | Qué hay | Nivel | Brecha principal |
|---|---|---|---|
| **Andamiaje de proyecto** | `stack/init_project.py` / `.ps1` crean la estructura, el `.venv`, `.vscode/settings.json`, `pytest.ini`, copian `memory/`, `changes_template/` y las instrucciones para agentes (`AGENTS.md`, `.cursorrules`). | Implementado | No hay prueba automática del propio script; un cambio puede romperlo sin que nadie lo note. |
| **Validación de endpoints** | `stack/validate_endpoints.py` (prueba de humo HTTP: estado, latencia, exportación de cURL sin secretos, código de salida para CI) y `endpoints_registry_template.json`. | Implementado | Solo verifica lo que esté en el registro; no detecta endpoints sin registrar. |
| **Infraestructura local** | `docker-compose.yml`, Dockerfiles, `entrypoint.sh`, `healthcheck.py`, `seed_data.py`, `settings_security_template.py`. | Implementado (plantillas) | Las rutas de salud del `healthcheck.py` deben coincidir con las canónicas (`/health/live`, `/health/ready`, `/fast/v1/health`); revisar en cada cambio de `stack/`. |
| **Componentes de interfaz** | 36 carpetas en `components/` con especificaciones Markdown y código de ejemplo React/CSS, más `variables.css` con tokens de tema claro/oscuro. | Documentado | No es una librería instalable: el código se copia desde Markdown a cada proyecto, por lo que las copias divergen con el tiempo. No hay pruebas ni revisión automática de accesibilidad. |
| **Normativa de buenas prácticas** | BP-01 a BP-22 en [`00_normativa_buenas_practicas_y_auditoria.md`](./00_normativa_buenas_practicas_y_auditoria.md). | Documentado (parcialmente implementado) | Algunas reglas están en las plantillas (p. ej. `SECRET_KEY` obligatoria con `DEBUG=False`, CORS restringido); la mayoría (N+1, `bulk_create`, transacciones) solo se verifica en revisión de código. |
| **Pruebas automáticas** | Protocolo 11, guía `stack/e2e_testing_guide.md`, `pytest.ini` y `requirements-dev.txt` generados por el andamiaje. | Documentado / plantilla | No hay un proyecto de referencia con pruebas que demuestre la configuración funcionando de punta a punta. |
| **CI/CD y control de calidad** | Protocolo 06 (pre-commit, ramas, Conventional Commits, puertas de calidad). | Documentado | No hay `.pre-commit-config.yaml` ni flujo de CI (GitHub Actions / GitLab CI) en `stack/`. Cada proyecto debe crearlos. |
| **Observabilidad** | Protocolo 07 (Correlation ID, salud, SLO, Sentry). | Documentado | No hay middleware de Correlation ID, configuración de métricas ni de Sentry en `stack/`. Los SLO son objetivos sin medición base. |
| **Migraciones y recuperación** | Protocolo 08 (*Expand & Contract*, índices concurrentes, RPO/RTO). | Documentado | No hay script de respaldo/restauración ni archivado de WAL configurado. RPO/RTO son metas, no capacidades comprobadas. |
| **Gobierno de APIs** | Protocolo 09 (versionado en URL, `oasdiff`, cabeceras `Deprecation`/`Sunset`). | Documentado | No hay paso de `oasdiff` en CI ni middleware de deprecación en `stack/`. |
| **Incidentes** | Protocolo 10 (severidades, roles, post-mortem sin culpa). | Documentado | No hay herramienta de guardia ni canal definidos para la organización; los tiempos de respuesta son referencias. |
| **Ciclo de vida y mejora continua** | Protocolo 12, especificación `components/dashboard/platform_usage_dashboard.md`. | Documentado | No hay instrumentación de uso implementada ni política de tratamiento de datos de telemetría. |
| **Prototipos sin código** | `mock/` (plantilla HTML autocontenida, plantilla de datos), metodología 05, ejemplo en `pages/dashboard/`. | Implementado (plantillas) | La plantilla depende de CDN (Bootstrap, Lucide, fuente Inter) para verse completa. |
| **Cambios atómicos** | `changes_template/` (propuesta, diseño, tareas, evidencia) y protocolo 14. | Implementado (plantilla) | Su uso no se verifica; depende de la revisión de pull requests. |
| **Memoria de proyecto** | `memory/` (ADR base, plantilla de ADR, lecciones y convenciones) y protocolo 15. | Implementado (plantilla) | Su valor depende de que se mantenga actualizada; no hay recordatorio ni verificación. |

---

## 3. Fortalezas verificables

* Estructura de proyecto reproducible mediante un script, con entorno Python aislado.
* Un validador de endpoints que puede ejecutarse en CI y devuelve código de salida.
* Rutas canónicas definidas (`/api/v1/`, `/fast/v1/`, `/health/live`, `/health/ready`) y un registro único de endpoints.
* Plantillas que separan decisión (ADR), alcance (propuesta) y evidencia (salida real de herramientas).
* Prototipado sin código que permite validar pantallas con usuarios de negocio antes de programar.

## 4. Debilidades y riesgos

1. **Mucha norma y poca verificación automática.** La mayoría de las reglas dependen de la disciplina del equipo. Sin CI que las compruebe, se degradan.
2. **Componentes como texto, no como paquete.** Cada proyecto copia el código; las correcciones no se propagan.
3. **Sin evidencia de adopción.** No hay registro de qué proyectos usan el SDD ni de resultados (defectos, tiempos de entrega) antes y después.
4. **Identidad visual no alineada.** `variables.css` usa una paleta verde esmeralda y tipografía Inter; la identidad corporativa de Joli Foods es morado, amarillo, azul y naranja con Gotham y Arvo. Es una decisión de negocio pendiente.
5. **Riesgo de rigidez.** Varias convenciones de diseño (ancho completo, drawer para CRUD, paginador arriba) son preferencias razonables, no requisitos de seguridad; tratarlas como absolutas puede producir malas soluciones en casos que no encajan. Por eso se expresan como DEBERÍA, con desviación registrada en un ADR.

## 5. Prioridades sugeridas

| Prioridad | Acción | Efecto |
|---|---|---|
| 1 | Agregar a `stack/` un `.pre-commit-config.yaml` y un flujo de CI de referencia (lint, pruebas, `pip-audit`, `npm audit`, validador de endpoints). | Convierte varias normas "documentadas" en "implementadas". |
| 2 | Crear un proyecto de ejemplo mínimo generado con el andamiaje y con pruebas pasando. | Prueba de que las plantillas funcionan juntas; detecta roturas. |
| 3 | Decidir la paleta y tipografía corporativas y aplicarlas en `variables.css`. | Coherencia de marca en todas las aplicaciones. |
| 4 | Evaluar publicar los componentes como paquete interno versionado. | Las correcciones llegan a todos los proyectos. |
| 5 | Registrar qué proyectos adoptan el SDD y medir algunos indicadores (defectos en producción, tiempo de entrega). | Permite evaluar el SDD con datos y no con autocalificación. |

---

## 6. Cómo repetir esta evaluación

Repetir la tabla de la sección 2 tras cada cambio relevante del SDD. Una capacidad solo pasa a "Implementado" cuando existe el archivo ejecutable o la plantilla en el repositorio y se ha probado al menos una vez en un proyecto generado. Las mejoras se registran con su evidencia (comando ejecutado y resultado), no con un puntaje.
