# 04. Arquetipos de Autenticación y Decisiones Canónicas
## Módulo de Login / Autenticación — SDD Joli Foods (`SPEC-AUTH-001`)

> **Origen:** patrón tomado de app_tic, tiendita, vibra, porterias y contenedores (módulos de login). Aquí se describe de forma genérica.

---

## 1. Arquetipos

| Arquetipo | Autenticación | Sesión | Cuándo usarlo | Riesgo principal y mitigación |
| :--- | :--- | :--- | :--- | :--- |
| **A. Quiosco operativo** | Documento + contraseña (o facial) en equipo compartido | Decisión canónica de sesión con refresh de vida corta | Turnos de planta con alta rotación | Equipo compartido: sin "Recordar documento", cierre de sesión por inactividad. |
| **B. Corporativo** | Documento + contraseña o SSO | Decisión canónica | Personal administrativo | Reutilización de claves: política de contraseñas y bloqueo por intentos. |
| **C. SSO obligatorio por rol** | Microsoft SSO para roles con `exige_sso` | Decisión canónica | Cuentas privilegiadas | Contraseñas locales débiles en cuentas admin: el backend rechaza contraseña con `SSO_REQUIRED`. |
| **D. Biometría con alternativa** | Reconocimiento facial + ingreso manual tras 3 fallos | Decisión canónica | Planta, manos ocupadas | Falsos negativos por luz/cámara: alternativa manual. |

---

## 2. Decisiones Canónicas

### Decisión 1: Access token en memoria + refresh en cookie HttpOnly
- **Regla:** el access token (JWT) DEBE vivir solo en memoria; el refresh token DEBE viajar en cookie `HttpOnly; Secure; SameSite=Lax`, rotarse en cada uso y protegerse con CSRF en `/auth/refresh/` y `/auth/logout/`.
- **Por qué:** lo que está en `localStorage`/`sessionStorage` lo lee cualquier script inyectado (XSS). La cookie HttpOnly no es legible por JavaScript y el access token en memoria desaparece al cerrar la pestaña.
- **Excepciones:** ninguna para aplicaciones web. Integraciones máquina a máquina usan credenciales de servicio propias, no este flujo.

### Decisión 2: Validación temprana con Zod
- **Regla:** el formulario DEBERÍA validar con un esquema `zod` compartido con los tipos TypeScript.
- **Por qué:** evita peticiones inútiles y da retroalimentación inmediata. No reemplaza la validación del servidor, que DEBE existir siempre.

### Decisión 3: Gobierno de cuentas privilegiadas
- **Regla:** los roles con `exige_sso = true` DEBEN autenticarse con Microsoft SSO; el backend DEBE rechazar su contraseña local con 403 `SSO_REQUIRED`.
- **Por qué:** delega MFA y bloqueo de cuentas en Entra ID, que ya administra TI.

### Decisión 4: Estilos solo con tokens
- **Regla:** la presentación DEBERÍA consumir exclusivamente los tokens de [`variables.css`](../../../components/variables.css) (modo noche y día).
- **Por qué:** un solo origen de colores mantiene el contraste verificado en ambos temas.
