# Plantilla de Cambios Atómicos y Especificaciones Vivas (SDD Changes)

Inspirado en el estándar **OpenSpec** y la metodología **Spec-Driven Development (SDD)** promovida en ecosistemas modernos de desarrollo con agentes de Inteligencia Artificial (Gentle-AI / Gentleman Programming).

---

## 🎯 ¿Para qué sirve esta estructura?

Cuando un proyecto ya está inicializado o en producción y se requiere implementar una **nueva funcionalidad, refactorización o cambio incremental significativo (Nivel 2 de ODD)**, queda prohibido pedirle a la Inteligencia Artificial cambios sueltos mediante "prompts ciegos" o "vibe coding".

Toda modificación debe gestionarse creando una subcarpeta dentro del directorio `specs/changes/` del proyecto:

```text
mi_proyecto/
└── specs/
    └── changes/
        └── [YYYY-MM-DD]-[nombre-del-cambio]/
            ├── proposal.md     # 1. Motivación, alcance y qué NO incluye el cambio
            ├── design.md       # 2. Contratos de datos, componentes UI y casos de borde
            ├── tasks.md        # 3. Lista de tareas atómicas secuenciales con casillas [ ]
            └── evidence.md     # 4. Evidencia verificable de ejecución (pruebas y contratos)
```

---

## 🔄 El Ciclo de 4 Fases de un Cambio Atómico

```mermaid
flowchart LR
    P[1. proposal.md<br/>Propuesta y Alcance] --> D[2. design.md<br/>Diseño y Contratos]
    D --> T[3. tasks.md<br/>Plan Atómico [ ]]
    T --> E[4. evidence.md<br/>Validación con Pruebas]
```

1. **Fase de Propuesta (`proposal.md`)**: El desarrollador o la IA define el problema de negocio y el valor a entregar. Se fija el límite de alcance (Out-of-Scope) para evitar que el agente agregue código innecesario.
2. **Fase de Diseño Técnico (`design.md`)**: Se definen los contratos TypeScript/Pydantic, los endpoints que se modificarán o crearán en `endpoints_registry.json`, los componentes reutilizables de `.sdd/components/` y la gestión de casos de borde.
3. **Fase de Tareas Ejecutables (`tasks.md`)**: Desglose paso a paso. La IA debe marcar `[x]` a medida que completa cada tarea. Si una tarea falla, se detiene y reporta.
4. **Fase de Cierre y Evidencia (`evidence.md`)**: La IA **no puede dar por completada la solicitud** sin adjuntar la salida del validador de endpoints (`python validate_endpoints.py`), la ejecución de tests Pytest/Playwright o las trazas de prueba.

---

## 🛠️ Cómo Inicializar un Nuevo Cambio

Simplemente copia esta carpeta `changes_template/` dentro de `specs/changes/` de tu proyecto y renómbrala con la fecha y el nombre de la característica:

```bash
cp -r .sdd/changes_template specs/changes/2026-10-15-filtro-avanzado-pedidos/
```
