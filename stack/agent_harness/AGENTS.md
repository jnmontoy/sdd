# Guía Operativa de Inteligencia Artificial (AGENTS.md)
## Estándar Oficial de Ingeniería Greenfield / Jolifoods — SDD

Este archivo es leído automáticamente por agentes de IA (Claude Code, Cursor, Antigravity, OpenCode, GitHub Copilot).
Toda IA que opere en este repositorio debe cumplir de forma inflexible las siguientes directrices operativas.

---

## 🛑 1. Guardrails de Seguridad y Deny-List (Innegociable)

1. **PROHIBIDO MODIFICAR O LEER ARCHIVOS DE SECRETOS**:
   * Queda estrictamente prohibido alterar o exponer credenciales de `.env`, `.env.local`, llaves privadas (`*.pem`, `*.key`), tokens de API o certificados.
2. **PROHIBIDO USAR RUTAS ABSOLUTAS (BP-07)**:
   * Toda ruta debe ser relativa a `BASE_DIR` (`Path(__file__).resolve().parent.parent`). Nunca cablear `C:\...` ni `/home/...`.
3. **AISLAMIENTO DE ENTORNO VIRTUAL (BP-15)**:
   * Toda ejecución de Python o pip debe realizarse dentro del `.venv` del proyecto (`.\.venv\Scripts\python.exe`).

---

## 🧠 2. Protocolo de Memoria Persistente (Recall & Log)

Antes de responder o escribir una sola línea de código:
1. **Consulta Obligatoria**:
   * Revisa `memory/adrs/`: Respeta las decisiones de arquitectura ya tomadas.
   * Revisa `memory/learnings/conventions.md`: Aplica las convenciones de datos y negocio.
   * Revisa `memory/learnings/bug_lessons.md`: Verifica que tu propuesta no reincida en bugs conocidos (N+1, leaks de conexiones, etc.).
2. **Registro de Aprendizajes**:
   * Si solucionas un bug complejo o tomas una decisión técnica de impacto, registra el aprendizaje en `memory/learnings/bug_lessons.md`.

---

## ⚖️ 3. Proporcionalidad del Trabajo (Principio ODD)

* **Nivel 1 (Micro-Fix / Hotfix)**: Si es un cambio cosmético o corrección de texto simple, ejecútalo de inmediato verificando no romper tests ni contratos.
* **Nivel 2 (Feature Incremental / Cambio Atómico)**:
  * Queda **PROHIBIDO programar a ciegas**.
  * Crea primero la carpeta `specs/changes/[fecha]-[nombre-cambio]/`.
  * Rellena `proposal.md`, `design.md` y `tasks.md`.
  * Ejecuta una tarea a la vez marcando `[x]`.
  * Adjunta la salida real en `evidence.md` antes de concluir.
* **Nivel 3 (Nuevo Módulo Completo)**: Aplica la entrevista guiada del SDD.

---

## 🎨 4. Reglas Inflexibles de Frontend y UI

1. **PROHIBIDO INVENTAR CSS AD-HOC**:
   * Reutiliza exclusivamente los componentes auditados y variables de diseño del SDD. No crees archivos `.css` aislados improvisados.
2. **LAYOUT 100% HORIZONTAL**:
   * Prohibido encoger la vista con `max-w-xl mx-auto`. La interfaz debe extenderse a lo largo de toda la pantalla de borde a borde.
3. **RIGHT DRAWER PARA EDICIÓN Y CREACIÓN**:
   * Todo formulario CRUD se despliega en panel lateral derecho de 560px (`drawer.md`), nunca en modales flotantes centrados.
4. **JUSTIFICACIÓN EN ACCIONES CRÍTICAS**:
   * Toda anulación o borrado debe exigir motivo con mínimo 10 caracteres (`confirm_modal.md`).

---

## 🔌 5. Reglas Inflexibles de Backend y Base de Datos

1. **CENTRALIZACIÓN DE ENDPOINTS (BP-09)**:
   * Todo endpoint debe registrarse en `backend/config/endpoints_registry.json` y consumirse desde `src/services/endpoints.ts`.
2. **TRANSACCIONALIDAD ATÓMICA (BP-12)**:
   * Envuelve operaciones dependientes en `with transaction.atomic():`.
3. **PERSISTENCIA EN BLOQUE (BP-13)**:
   * Prohibido `.save()` individual en bucles; usa `bulk_create` / `bulk_update`.
4. **VALIDACIÓN AUTOMÁTICA DE ENDPOINTS**:
   * Ejecuta siempre `python stack/validate_endpoints.py` para certificar que ningún contrato esté roto.
