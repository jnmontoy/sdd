# Convenciones del proyecto

> **Propósito**: convenciones de negocio, datos y presentación que cualquier persona o agente de IA debe aplicar en cada sesión. Esta es la versión base del SDD para proyectos de Joli Foods; cada proyecto puede ajustarla registrando el motivo.

---

## 1. Fechas y zonas horarias
* **Zona horaria de negocio**: `America/Bogota` (UTC−5, sin horario de verano).
* **Almacenamiento**: en UTC (`USE_TZ = True` en Django); en JSON, ISO 8601 con zona (`2026-10-15T14:30:00Z`).
* **Visualización**: `DD/MM/AAAA HH:MM` en hora de Bogotá (12 h o 24 h según el módulo, de forma consistente en todo el módulo).
* **Meses y días**: en español y en minúscula dentro de una frase (enero, febrero…), como indica la RAE.

**Por qué:** guardar en UTC evita errores al comparar o sumar fechas; mostrar en hora local evita confusiones al usuario.

---

## 2. Moneda y números
* **Moneda base**: peso colombiano (`COP`); otras monedas se indican explícitamente (`USD`).
* **Formato visual**: `$ 1.250.000` (punto para miles, coma para decimales; locale `es-CO`).
* **Cálculos en backend**: `Decimal` de Python y `DecimalField` en modelos. NO DEBE usarse `float` para dinero.

**Por qué:** `float` introduce errores de redondeo binario (p. ej. `0.1 + 0.2 != 0.3`).

---

## 3. Identidad visual
* **Fuente única de colores y tipografía**: [`components/variables.css`](../../components/variables.css). NO DEBEN copiarse valores hexadecimales en el código de los módulos; se usan los tokens `var(--...)`.
* **Logos**: `Jolifoods.svg`, `Joli.svg`, `logoJoli.png` en `.sdd/assets/`; cada prototipo o proyecto copia los que use a su carpeta `assets/`.
* **Pendiente de decisión**: la paleta actual de `variables.css` (verde esmeralda) no coincide con la identidad corporativa de Joli Foods (morado, amarillo, azul y naranja; tipografías Gotham y Arvo). Hasta que se decida, se mantiene `variables.css` como está; el cambio, cuando se haga, se hará solo en ese archivo.

---

## 4. Base de datos
* **Nombres de tabla**: los que genera Django (`<app>_<modelo>`, p. ej. `logistica_despacho`), en minúscula.
* **Claves primarias**: `BigAutoField` por defecto; UUID cuando el identificador se expone fuera del sistema o se genera en el cliente.
* **Campos de auditoría**: todo modelo de negocio DEBERÍA incluir `creado_en` (`auto_now_add=True`) y `actualizado_en` (`auto_now=True`).
* **Borrado lógico**: se prefiere `activo = models.BooleanField(default=True)` al `DELETE` físico en entidades con historial, registrando quién y por qué en la bitácora de auditoría.

---

## 5. Datos personales
* Los datos personales se tratan conforme a la Ley 1581 de 2012 (protección de datos personales, Colombia). Los datos biométricos (rostro, huella, firma manuscrita digitalizada) son **datos sensibles** y requieren autorización expresa del titular.
* En ejemplos, pruebas y prototipos se usan valores ficticios: cédula `1000000001`, correo `usuario@ejemplo.com`, dominio `app.ejemplo.local`.
