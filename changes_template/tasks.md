# Lista de tareas: [Nombre breve del cambio]

> **Reglas de ejecución (para personas y agentes de IA)**
> 1. Una tarea a la vez, en orden.
> 2. Marcar `[x]` solo cuando la verificación indicada en la tarea pasó.
> 3. Si una tarea falla, NO continuar con la siguiente: corregir o detenerse y reportar.
> 4. Si aparece trabajo fuera del alcance de `proposal.md`, anotarlo al final como pendiente; no ejecutarlo.

---

## Fase 1: Modelos y base de datos
- [ ] **1.1** Crear o actualizar el modelo y la migración en `backend/apps/<app>/`. Verificación: `.\.venv\Scripts\python.exe backend\manage.py makemigrations --check --dry-run` no muestra cambios pendientes tras generar la migración.
- [ ] **1.2** Aplicar migraciones en el entorno local (`.\.venv\Scripts\python.exe backend\manage.py migrate`). Si la tabla es grande, seguir el protocolo 08.

## Fase 2: Esquemas y endpoints
- [ ] **2.1** Registrar el endpoint en `backend/config/endpoints_registry.json`.
- [ ] **2.2** Implementar el esquema Pydantic v2 o el serializador DRF.
- [ ] **2.3** Implementar la vista (Django `/api/v1/...`) o la ruta (FastAPI `/fast/v1/...`) con autenticación, permisos y manejo de errores sin filtrar detalles internos.
- [ ] **2.4** Escribir pruebas en `pruebas/integracion/` para el caso feliz y los casos de borde de `design.md`.

## Fase 3: Interfaz
- [ ] **3.1** Agregar la ruta en `frontend/src/services/endpoints.ts` (sin URLs quemadas en componentes).
- [ ] **3.2** Ensamblar la vista con componentes de `.sdd/components/`.
- [ ] **3.3** Conectar drawer y `ConfirmModal` (motivo mínimo 10 caracteres) donde aplique.
- [ ] **3.4** Escribir pruebas Vitest junto al componente (`*.test.tsx`).

## Fase 4: Verificación y evidencia
- [ ] **4.1** `.\.venv\Scripts\python.exe -m pytest -m "not e2e"` (usa `pytest.ini` de la raíz) sin fallos.
- [ ] **4.2** `npm test` en `frontend/` sin fallos.
- [ ] **4.3** `ruff check .` y `npm run lint` sin errores.
- [ ] **4.4** `.\.venv\Scripts\python.exe pruebas\validate_endpoints.py --base-url http://localhost:8000` con código de salida 0.
- [ ] **4.5** Si el cambio toca flujos críticos: `.\.venv\Scripts\python.exe -m pytest -m e2e pruebas\e2e`.
- [ ] **4.6** Pegar las salidas en `evidence.md`.

## Pendientes detectados (fuera de alcance)
- [...]
