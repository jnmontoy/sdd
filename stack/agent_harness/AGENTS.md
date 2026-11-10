# Guía para agentes de IA (AGENTS.md)

Este archivo lo leen automáticamente los asistentes de código (Claude Code, Cursor, Copilot y otros). Resume las reglas del proyecto; la fuente completa es la normativa de buenas prácticas del SDD (`.sdd/greenfield/00_normativa_buenas_practicas_y_auditoria.md`).

Palabras clave: **DEBE / NO DEBE** = obligatorio; **DEBERÍA / NO DEBERÍA** = recomendado, se puede desviar dejando la razón en un ADR (`memory/adrs/`) o si el usuario lo pide expresamente.

Idioma: respuestas, comentarios y documentación en español.

---

## 1. Seguridad

1. NO DEBE leer, mostrar ni modificar secretos (`.env`, `*.pem`, `*.key`, tokens). Para configurar, use `.env.example`.
2. NO DEBE instalar paquetes fuera del entorno virtual del proyecto (BP-15): `.\.venv\Scripts\python.exe -m pip ...` (Windows) o `./.venv/bin/python -m pip ...` (Linux/macOS). **Por qué:** instalar en el Python global mezcla versiones entre proyectos y no se puede reproducir.
3. NO DEBE escribir rutas absolutas de disco ni URLs de servidor en el código (BP-07); use `BASE_DIR` en el backend y `ENDPOINTS` en el frontend (BP-09).
4. Los tokens de sesión NO DEBEN guardarse en `localStorage`/`sessionStorage`: el access token vive en memoria y el refresh en cookie HttpOnly (BP-18).
5. Las respuestas NO DEBEN revelar qué cuentas o registros existen (BP-24): login con usuario inexistente o contraseña incorrecta, mismo mensaje, código y tiempo (hash ficticio); recuperación siempre con el mismo mensaje; recurso ajeno = `404`; usuarios desactivados no se muestran. **Por qué:** una lista de cuentas válidas facilita la fuerza bruta y la suplantación. Aunque se pida mostrar el error exacto, advierta el riesgo antes de hacerlo.
6. Ningún dato externo DEBE terminar ejecutado (BP-25): SQL siempre con parámetros (`%s` y los valores aparte), nunca con f-strings, `.format()` ni concatenación; nombres de columna desde una lista cerrada; nada de `dangerouslySetInnerHTML`/`innerHTML` sin DOMPurify, ni `eval` o `shell=True`. **Por qué:** un solo campo mal armado basta para leer o borrar tablas completas.
7. Antes de instalar o actualizar una dependencia, revise que sea la librería correcta (nombre exacto, mantenida) y corra `pip-audit` o `npm audit` después. **Por qué:** un paquete con nombre parecido o abandonado es una puerta de entrada directa al proyecto.

## 2. Antes de programar

1. Revise `memory/adrs/` (decisiones vigentes) y `memory/learnings/` (convenciones y errores ya conocidos).
2. Ajuste el esfuerzo al tamaño del cambio:
   - **Nivel 1, corrección pequeña:** se hace directamente y se verifica que las pruebas sigan pasando.
   - **Nivel 2, funcionalidad o refactor:** cree `specs/changes/AAAA-MM-DD-nombre/` con `proposal.md`, `design.md`, `tasks.md` y `evidence.md` (plantilla en `specs/changes/_plantilla/`). **Por qué:** deja escrito qué se decidió y con qué evidencia se dio por terminado.
   - **Nivel 3, módulo nuevo:** siga la entrevista guiada del SDD (`greenfield/03`).
3. Si resuelve un error difícil, regístrelo en `memory/learnings/bug_lessons.md`.

## 3. Backend

1. Operaciones con 2 o más escrituras dependientes DEBEN ir en `transaction.atomic()` (BP-12).
2. Consultas con relaciones DEBEN usar `select_related`/`prefetch_related` (sin N+1). NO DEBERÍA haber consultas a la base de datos dentro de ciclos (BP-11).
3. Las inserciones masivas DEBERÍAN usar `bulk_create`/`bulk_update` (BP-13). Tenga en cuenta que no ejecutan `save()` ni señales.
4. Todo endpoint nuevo DEBE registrarse en `backend/config/endpoints_registry.json` y en `frontend/src/services/endpoints.ts`.
5. Las vistas son privadas por defecto (BP-05); una vista pública lo declara explícitamente.

## 4. Frontend

1. DEBERÍA construir con los componentes y tokens del SDD (`variables.css`) antes de crear estilos nuevos. Si un estilo nuevo es necesario, use tokens `var(--...)`, nunca colores fijos.
2. Las pantallas de trabajo DEBERÍAN ocupar todo el ancho disponible. Se centran solo los modales y la tarjeta de login.
3. La creación y edición en CRUD DEBERÍA hacerse en el panel lateral derecho (drawer); los modales quedan para confirmaciones, firmas, escáneres y sesión vencida.
4. Las acciones de fila (2 o más botones) DEBERÍAN agruparse con `btn-group btn-group-sm` y llevar `aria-label`.
5. Las acciones destructivas DEBEN pedir confirmación; si el negocio exige trazabilidad, también un motivo.

## 5. Verificación antes de dar algo por terminado

Ejecute y pegue la salida real en `evidence.md` (cambios de nivel 2):

```powershell
.\.venv\Scripts\python.exe -m pytest                                   # pruebas del backend (pruebas/)
npm --prefix frontend run typecheck; npm --prefix frontend test        # tipos y pruebas de React
.\.venv\Scripts\python.exe pruebas\validate_endpoints.py --base-url http://localhost:8000
```

NO DEBE declarar una tarea como terminada sin esa evidencia, ni entregar archivos con código truncado o marcadores del tipo `// ... resto del código ...` (BP-14).

En formularios de captura (login, contraseñas, crear o editar registros) DEBERÍA usar el campo con etiqueta flotante de `sdd/components/form/floating_field.md` en inputs, selects y textareas; NO DEBERÍA aplicarlo a buscadores, filtros ni cuadros de chat (normativa 6.9).

NO DEBERÍA agregar código a un archivo que supera su límite de líneas (componente o `.ts` 500, `.css` 800, módulo Python 600, función 80): primero lo desacopla en componentes, hooks o funciones sin cambiar el comportamiento (BP-23). El hook `stack/agent_harness/hooks/limite-lineas.js` (en `.claude/settings.json`, evento `PostToolUse` sobre `Write|Edit`) avisa automáticamente al pasar el aviso o el límite.

Antes de entregar una pantalla, repase los principios de usabilidad de la normativa 6.10: respuesta en menos de 400 ms o esqueleto, una acción principal, blancos táctiles de 44 px en móvil, errores que dicen cómo corregir.
