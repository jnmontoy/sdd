# Sistema de Memoria Persistente para Agentes de IA (SDD Memory Engine)

Inspirado en el concepto de **memoria persistente de largo plazo (Engram™)** y los registros de decisiones arquitectónicas (**ADRs**), este sistema resuelve el mayor problema de programar con Inteligencia Artificial: **la amnesia entre sesiones**.

---

## 🧠 ¿Por qué es necesaria la Memoria Persistente?

Los modelos de lenguaje (LLMs) operan en ventanas de contexto efímeras:
1. **Pérdida de contexto**: Cada nueva sesión en la terminal o IDE arranca desde cero.
2. **Reincidencia en errores**: Si un desarrollador tardó 2 horas corrigiendo un bug sutil de dependencias circulares o serialización, en la siguiente sesión la IA puede volver a cometer exactamente el mismo error.
3. **Decisiones descartadas que vuelven a proponerse**: La IA sugiere arquitecturas que el equipo ya rechazó semanas atrás por motivos de rendimiento o seguridad.

---

## 📂 Estructura Canónica de la Carpeta `memory/`

Todo proyecto nacido bajo el ecosistema SDD incorpora en su raíz la carpeta `memory/`:

```text
mi_proyecto/
└── memory/
    ├── README.md                      # Explicación de uso para desarrolladores y agentes
    ├── adrs/                          # Architectural Decision Records (Decisiones inmutables)
    │   ├── 0000_template_adr.md       # Plantilla de registro de decisión
    │   └── 0001_arquitectura_stack.md # ADRs adoptados en el proyecto
    │
    └── learnings/                     # Aprendizaje continuo acumulativo
        ├── bug_lessons.md             # Lecciones aprendidas de bugs corregidos (Anti-Reincidencia)
        └── conventions.md             # Reglas y preferencias del negocio no negociables
```

---

## 🔄 Protocolo de Memoria para el Agente (Recall & Log)

### 1. Fase de Inicio de Sesión: Recall (Recuperación)
Antes de proponer o ejecutar código, el agente de IA **DEBE LEER OBLIGATORIAMENTE**:
* `memory/adrs/`: Para no contradecir decisiones arquitectónicas ya tomadas.
* `memory/learnings/conventions.md`: Para adoptar los formatos y reglas del equipo.
* `memory/learnings/bug_lessons.md`: Para verificar si la tarea que va a realizar toca un área propensa a bugs conocidos.

### 2. Fase de Cierre de Sesión: Log Learnings (Registro de Aprendizajes)
Cuando se resuelve un problema complejo, un bug sutil o se toma una decisión técnica clave:
* El agente o el desarrollador añade una entrada en `memory/learnings/bug_lessons.md`.
* Si se tomó una decisión de arquitectura, se redacta un nuevo ADR numerado (`0002_...md`).

---

## 🔌 Compatibilidad con Servidores MCP (Model Context Protocol)

Este estándar en Markdown es **100% interoperable** con:
* **Engram™ (Gentleman Programming)**: Servidor MCP local en Go + SQLite/FTS5 que indexa automáticamente estas carpetas.
* **Knowledge Items (KI) de Antigravity / Gemini**: Inyección directa en el prompt del sistema.
* **Claude Code / Cursor / OpenCode**: Consumo directo mediante reglas de proyecto (`AGENTS.md` o `.cursorrules`).
