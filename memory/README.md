# Memoria persistente del proyecto (`memory/`)

Plantilla para que el conocimiento de un proyecto (decisiones tomadas, errores ya resueltos, convenciones del equipo) quede **escrito en el repositorio** y no dependa de la memoria de una persona ni de la sesión de un asistente de IA.

Se basa en dos prácticas conocidas:
* **ADR** (*Architecture Decision Record*, registro de decisión de arquitectura; formato popularizado por Michael Nygard): un archivo corto por decisión con contexto, alternativas y consecuencias.
* **Lecciones aprendidas**: catálogo de errores resueltos con síntoma, causa raíz y regla preventiva.

Protocolo que la rige: [`greenfield/15_protocolo_memoria_persistente_y_aprendizaje_agentes.md`](../greenfield/15_protocolo_memoria_persistente_y_aprendizaje_agentes.md).

---

## Para qué sirve

Los asistentes de IA (y las personas nuevas en un equipo) no recuerdan lo que pasó en sesiones anteriores. Sin un registro escrito:
1. Se repiten errores que ya se habían corregido.
2. Se vuelven a proponer alternativas que el equipo ya descartó, sin conocer el motivo.
3. Las convenciones (formatos, nombres, zona horaria) se aplican de forma inconsistente.

---

## Estructura

En el SDD esta carpeta es una **plantilla**: se copia a la raíz de cada proyecto nuevo y allí se mantiene.

```text
<proyecto>/
└── memory/
    ├── README.md               # Este documento
    ├── adrs/
    │   ├── 0000_template_adr.md   # Plantilla de ADR
    │   └── 0001_....md            # Decisiones del proyecto (numeradas, no se reescriben)
    └── learnings/
        ├── bug_lessons.md      # Errores resueltos y regla para no repetirlos
        └── conventions.md      # Convenciones de negocio, datos y formato
```

`adrs/0001_arquitectura_hibrida_fastapi_django.md` es la decisión base del stack del SDD; el proyecto la hereda y puede reemplazarla con un ADR propio si cambia de stack.

---

## Uso

### Al iniciar una sesión de trabajo (persona o agente)
Leer, en este orden, lo que aplique a la tarea:
* `memory/adrs/`: para no contradecir decisiones vigentes.
* `memory/learnings/conventions.md`: formatos y reglas del equipo.
* `memory/learnings/bug_lessons.md`: si la tarea toca un área con errores conocidos.

### Al cerrar una tarea
* Si se resolvió un error que costó más de un intento o una investigación, agregar una entrada en `bug_lessons.md`.
* Si se tomó una decisión de arquitectura, crear un ADR nuevo con el siguiente número. Un ADR aceptado **no se edita**: si la decisión cambia, se crea uno nuevo que lo reemplaza y se actualiza el campo "Estado" del anterior.
* NO registrar aquí datos personales, credenciales ni información confidencial del negocio.

---

## Cómo lo leen las herramientas de IA

Los archivos son Markdown plano, así que cualquier herramienta puede leerlos. La forma práctica de que un agente los consulte es referenciarlos desde el archivo de instrucciones del proyecto:
* **Claude Code**: `CLAUDE.md` (admite importar archivos con `@ruta/al/archivo.md`).
* **Cursor**: reglas de proyecto (`.cursor/rules/` o el formato heredado `.cursorrules`).
* **Otros agentes** (OpenCode, Copilot, etc.): `AGENTS.md` en la raíz.

También existen servidores MCP (*Model Context Protocol*) de memoria, por ejemplo Engram (Gentleman Programming), que indexan notas con búsqueda de texto completo (SQLite FTS5). Son **opcionales**: el SDD no los instala ni depende de ellos.
