# Lista de Tareas Atómicas: [Nombre Breve del Cambio]

> **INSTRUCCIÓN OBLIGATORIA PARA EL AGENTE DE IA**:
> 1. Ejecuta una sola tarea a la vez en estricto orden secuencial.
> 2. Marca con `[x]` únicamente cuando hayas verificado que el código funciona y compila sin errores.
> 3. Si una tarea arroja un fallo, **NO procedas con la siguiente**; corrígela o detén la ejecución reportando la discrepancia.

---

## 📋 Lista de Tareas

### Fase 1: Modelos y Base de Datos (Backend)
- [ ] **Tarea 1.1**: Crear/actualizar modelo Django o migración en `backend/apps/...` siguiendo BP-07 (rutas relativas) y BP-12 (atomicidad).
- [ ] **Tarea 1.2**: Ejecutar migraciones en `.venv` de forma segura.

### Fase 2: Esquemas y Endpoints (FastAPI / Django)
- [ ] **Tarea 2.1**: Registrar el endpoint en `endpoints_registry.json` con su método, ruta y roles RBAC.
- [ ] **Tarea 2.2**: Implementar esquema Pydantic v2 en `backend/schemas/`.
- [ ] **Tarea 2.3**: Implementar la vista o ruta FastAPI en `/fast/...` con rate-limiting y manejo de excepciones.

### Fase 3: Integración de Frontend (React / UI)
- [ ] **Tarea 3.1**: Actualizar `src/services/endpoints.ts` consumiendo la ruta registrada (prohibido cablear URLs fijas).
- [ ] **Tarea 3.2**: Ensamblar la interfaz reutilizando los componentes auditados de `.sdd/components/` (prohibido inventar CSS nuevo).
- [ ] **Tarea 3.3**: Conectar la apertura del Right Drawer y modales con justificación de mínimo 10 caracteres.

### Fase 4: Calidad y Pruebas
- [ ] **Tarea 4.1**: Ejecutar `python stack/validate_endpoints.py` y verificar que el endpoint esté en verde (100%).
- [ ] **Tarea 4.2**: Ejecutar pruebas automáticas en `pruebas/` (`pytest` / `playwright`).
- [ ] **Tarea 4.3**: Registrar la evidencia en `evidence.md`.
