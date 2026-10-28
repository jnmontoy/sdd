# Registro de Lecciones Aprendidas de Bugs (Anti-Reincidencia para Agentes de IA)

> **PROPÓSITO DE ESTE DOCUMENTO**:
> Los agentes de IA suelen cometer una y otra vez los mismos errores técnicos comunes a lo largo del tiempo.
> Este catálogo registra cada bug crítico solucionado, su causa raíz y la regla estricta que la IA debe obedecer para no reincidir jamás.

---

## 🗂️ Índice de Lecciones Aprendidas

* [BUG-001: Pérdida de Conexiones DB en Endpoints Híbridos FastAPI](#bug-001)
* [BUG-002: Error N+1 en Consultas con Serializadores o Loops](#bug-002)
* [BUG-003: Rotura de Layout por Contenedores Centrados o max-w](#bug-003)
* [BUG-004: Invocación de `.save()` en Bucles Masivos](#bug-004)
* [BUG-005: Rutas Absolutas de Sistema Operativo Quemadas en Código](#bug-005)
* [BUG-006: Uso Indebido de Modales Centrados en lugar de Sidebar Derecho (Right Drawer) para Formularios CRUD](#bug-006)

---

### <a id="bug-001"></a> BUG-001: Pérdida de Conexiones DB en Endpoints Híbridos FastAPI
* **Síntoma**: Endpoints de `/fast/` fallan tras horas de uso con error `OperationalError: remaining connection slots are reserved` o conexiones "colgadas" a PostgreSQL.
* **Causa Raíz**: A diferencia del ciclo de vida WSGI tradicional de Django, FastAPI opera en un bucle ASGI asíncrono y los workers no cierran automáticamente las conexiones inactivas del hilo de Django ORM.
* **Solución Aplicada**: Añadir middleware o dependencia FastAPI que ejecute `django.db.close_old_connections()` antes y después de cada petición.
* **Regla Inflexible para la IA**: En todo router de FastAPI que invoque modelos de Django, asegurar siempre el cierre explícito de conexiones inactivas.

---

### <a id="bug-002"></a> BUG-002: Error N+1 en Consultas con Serializadores o Loops
* **Síntoma**: La carga de una tabla con 500 registros ejecuta 501 consultas SQL, disparando la CPU y tardando 3.5 segundos.
* **Causa Raíz**: Acceder a relaciones ForeignKey (ej. `registro.usuario.nombre`) dentro de un ciclo `for` o en la serialización sin haber pre-cargado la relación.
* **Solución Aplicada**: Utilizar `select_related()` para relaciones uno a uno / foreign key, y `prefetch_related()` para muchos a muchos, o consultar directamente `.values('id', 'nombre', 'usuario__nombre')`.
* **Regla Inflexible para la IA (BP-11)**: Queda estrictamente prohibido anidar ciclos `for` para cruzar colecciones y ejecutar consultas SQL dentro de loops. Toda relación debe pre-cargarse en un solo viaje de red.

---

### <a id="bug-003"></a> BUG-003: Rotura de Layout por Contenedores Centrados o max-w
* **Síntoma**: El frontend se renderiza como una columna angosta en el centro de la pantalla con espacios vacíos gigantes a los lados.
* **Causa Raíz**: Uso de clases CSS como `max-w-xl mx-auto` o contenedores fijos de ancho pequeño.
* **Solución Aplicada**: Remover límites de ancho y aplicar el estándar SDD 100% horizontal de borde a borde (`flex: 1; width: 100%;`).
* **Regla Inflexible para la IA**: Prohibido centrar o encoger interfaces. Todo módulo debe extenderse a lo largo del viewport.

---

### <a id="bug-004"></a> BUG-004: Invocación de `.save()` en Bucles Masivos
* **Síntoma**: Importación de 2,000 registros toma más de 40 segundos.
* **Causa Raíz**: Ejecutar `obj.save()` dentro de un loop de 2,000 iteraciones (2,000 transacciones SQL individuales).
* **Solución Aplicada**: Acumular instancias en una lista y ejecutar `bulk_create(batch_size=500)` dentro de `with transaction.atomic():`.
* **Regla Inflexible para la IA (BP-13)**: Prohibido invocar `.save()` o `.create()` en iteraciones; usar siempre operaciones en bloque.

---

### <a id="bug-005"></a> BUG-005: Rutas Absolutas de Sistema Operativo Quemadas en Código
* **Síntoma**: El código funciona en la máquina del desarrollador (`C:\Users\juan\...`) pero explota en el contenedor Docker (`/app/...`) o en CI/CD con `FileNotFoundError`.
* **Causa Raíz**: Concatenación de strings con rutas absolutas locales fijas.
* **Solución Aplicada**: Resolver siempre con `Path(__file__).resolve().parent.parent` (`BASE_DIR`).
* **Regla Inflexible para la IA (BP-07)**: Prohibido quemar rutas absolutas; toda ruta debe ser 100% relativa a la raíz.

---

### <a id="bug-006"></a> BUG-006: Uso Indebido de Modales Centrados en lugar de Sidebar Derecho (Right Drawer) para Formularios CRUD
* **Síntoma**: En módulos administrativos (como Administración de Usuarios), las acciones de "Agregar" o "Editar" abren una ventana modal flotante en el centro de la pantalla (`.modal-card-dialog`), tapando la tabla/cards y rompiendo el estándar UX de Jolifoods.
* **Causa Raíz**: Creación de un modal genérico centrado en lugar de consultar la especificación canónica [`sdd/components/drawer/drawer.md`](../../components/drawer/drawer.md).
* **Solución Aplicada**: Reemplazar todo modal de creación/edición CRUD por el componente canónico **`RightDrawer` (`.joli-drawer-container`)**, que se desliza desde el borde derecho (`translateX(100%) -> translateX(0)`), conserva el contexto visual de la vista principal, muestra Mini-KPIs contextuales (`.drawer-kpi-grid`) al editar y utiliza controles estilizados con iconos (`.drawer-input-control.has-icon`).
* **Regla Inflexible para la IA**: **NUNCA** volver a crear modales centrados para formularios de agregar o editar registros. Todo formulario CRUD debe abrirse siempre en un Sidebar lateral derecho (`RightDrawer`).
