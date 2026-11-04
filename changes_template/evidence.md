# Evidencia de verificación: [Nombre breve del cambio]

> **Regla**: el cambio no se declara terminado con frases como "ya quedó y funciona". Se pega aquí la salida real de cada herramienta. Si algo no se ejecutó, se marca **NO EJECUTADO** con el motivo; nunca se marca como aprobado por suposición.

---

## 1. Pruebas de backend (Pytest)
* **Fecha**: `AAAA-MM-DD HH:MM`
* **Comando**: `.\.venv\Scripts\python.exe -m pytest -m "not e2e"` (configuración en `pytest.ini`, `testpaths = pruebas`)
* **Resultado**: `[N pasaron, N fallaron, N omitidas]`

```text
[PEGAR SALIDA REAL]
```

## 2. Pruebas de frontend (Vitest)
* **Comando**: `npm test` (en `frontend/`)
* **Resultado**: `[...]`

```text
[PEGAR SALIDA REAL]
```

## 3. Validador de endpoints (prueba de humo HTTP)
* **Comando**: `.\.venv\Scripts\python.exe pruebas\validate_endpoints.py --base-url http://localhost:8000 --login-user <usuario>`
  (la contraseña se toma de la variable de entorno `SDD_LOGIN_PASSWORD`; no se pasa por argumento ni se pega aquí)
* **Código de salida**: `[0 / distinto de 0]`

```text
[PEGAR SALIDA REAL — revisar que no contenga tokens ni contraseñas]
```

## 4. Pruebas de extremo a extremo (si aplica)
* **Comando**: `.\.venv\Scripts\python.exe -m pytest -m e2e pruebas\e2e`
* **Resultado**: `[... / NO EJECUTADO: motivo]`

## 5. Lint y dependencias
* `ruff check .` → `[resultado]`
* `npm run lint` → `[resultado]`
* `pip-audit -r backend/requirements.txt` → `[resultado]`
* `npm audit --audit-level=high` → `[resultado]`

## 6. Revisión de interfaz (manual)
Marcar solo lo verificado; dejar sin marcar y explicar lo que no aplica.

* [ ] Sin CSS nuevo fuera de componentes de `.sdd/components/` y tokens de `variables.css`.
* [ ] Vista de ancho completo (sin contenedor centrado estrecho).
* [ ] Crear/editar en drawer derecho (o desviación justificada en `design.md`).
* [ ] Acciones críticas con `ConfirmModal` y motivo mínimo de 10 caracteres.
* [ ] Revisado en tema claro y oscuro.

## 7. Cierre
* **Responsable (rol / sesión)**: `[...]`
* **Estado**: `[COMPLETADO | COMPLETADO CON PENDIENTES | BLOQUEADO]`
* **Pendientes**: `[...]`
