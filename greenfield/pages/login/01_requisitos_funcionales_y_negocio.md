# 01. Requisitos Funcionales y de Negocio
## Módulo de Login / Autenticación — SDD Greenyard (`GY-SPEC-AUTH-001`)

---

## 1. Objetivos del Módulo

1. **Garantizar la identidad y trazabilidad** de cada persona que interactúa con los sistemas del ecosistema Greenyard / Jolifoods.
2. **Minimizar la fricción operativa** para el personal de planta y operaciones de portería, sin comprometer la seguridad institucional.
3. **Imponer gobernanza y control corporativo** para accesos de nivel administrativo mediante Single Sign-On (SSO) con Microsoft 365 Entra ID.
4. **Cumplir con estándares de auditoría informática** registrando cada intento de acceso exitoso y fallido con IP, agente de usuario y marca de tiempo.

---

## 2. Taxonomía de Perfiles y Roles

| Perfil | Descripción | Mecanismo de Autenticación Permitido | Requiere MFA |
| :--- | :--- | :--- | :--- |
| **Operario de Planta / Campo** | Personal operativo en líneas de producción y empaque. | Cédula física directa o Reconocimiento Facial. | No |
| **Guarda de Seguridad (Portería)** | Vigilantes a cargo del registro de ingreso perimetral. | Cédula física directa con validación de estado activo. | No |
| **Colaborador Administrativo** | Empleados de oficinas, logística, compras y contabilidad. | Cédula + Contraseña o Microsoft 365 SSO. | Opcional |
| **Líder de Área / Administrador TIC** | Administradores de plataforma y superusuarios. | **Obligatoriamente Microsoft 365 SSO**. | **Sí (Gestionado por Azure AD)** |
| **Auditor / Invitado Externo** | Inspectores de calidad y auditores temporales. | Credenciales con expiración forzada por fecha. | Recomendado |

---

## 3. Matriz de Requisitos Funcionales (RF)

| Código | Nombre del Requisito | Descripción Detallada |
| :--- | :--- | :--- |
| **RF-01** | Ingreso por Cédula | El sistema debe permitir la entrada ingresando el número de documento de identidad (sin puntos, guiones ni espacios). |
| **RF-02** | Validación de Contraseña | Para perfiles no-operativos, se debe exigir contraseña segura con verificación mediante algoritmo criptográfico robusto. |
| **RF-03** | Integración Microsoft SSO | Botón institucional "Iniciar con Microsoft" que inicia el flujo de autorización OAuth2 / OIDC con el tenant corporativo de Greenyard. |
| **RF-04** | Pre-chequeo Condicional de Rol | Capacidad de evaluar la cédula del usuario previo al envío de credenciales para exigir SSO si ostenta rol de Administrador. |
| **RF-05** | Función "Recuérdame" | Casilla opcional que almacena de forma persistente y segura el número de documento en el cliente para agilizar futuros accesos. |
| **RF-06** | Alternar Visibilidad de Contraseña | Control de interfaz interactivo (ícono de ojo) que cambia dinámicamente el tipo de campo entre texto plano y caracteres enmascarados. |
| **RF-07** | Recuperación de Contraseña | Enlace accesible *"¿Olvidaste tu contraseña?"* que redirige al flujo de restablecimiento por correo institucional verificado. |
| **RF-08** | Control de Sesión Expirada | Al vencer la validez del token de acceso, la interfaz debe notificar al usuario y permitir la reautenticación sin pérdida de ruta previa. |
| **RF-09** | Bloqueo por Tasa de Intentos | Detección automática de 5 intentos fallidos consecutivos en un intervalo de 60 segundos con bloqueo temporal escalonado. |
| **RF-10** | Detección de Usuario Inactivo | Si el usuario está registrado pero marcado como inactivo (`is_active = False` o `estado != 1`), se debe negar el acceso con mensaje explicativo. |
| **RF-11** | Fallback Biométrico | En terminales con soporte facial, conmutar a ingreso manual si el reconocimiento no es exitoso tras 3 intentos. |
| **RF-12** | Cierre de Sesión Seguro (Logout) | Invalidación explícita del refresh token en backend y purga de cookies / storage en el cliente. |

---

## 4. Requisitos No Funcionales (RNF)

| Código | Categoría | Métrica / Criterio |
| :--- | :--- | :--- |
| **RNF-01** | **Rendimiento** | Tiempo de respuesta de autenticación exitosa p95 inferior a 1.2 segundos en redes corporativas. |
| **RNF-02** | **Disponibilidad** | Tasa de operatividad del servicio de autenticación del 99.9% (24/7/365). |
| **RNF-03** | **Seguridad de Tráfico** | Obligatoriedad absoluta de HTTPS / TLS 1.3 en todas las conexiones del frontend con la API. |
| **RNF-04** | **Protección de Credenciales** | Ninguna contraseña debe ser registrada en texto plano en logs de servidor, bases de datos o mensajes de depuración. |
| **RNF-05** | **Accesibilidad (A11y)** | Cumplimiento del estándar WCAG 2.1 Nivel AA en todos los elementos interactivos del formulario. |
| **RNF-06** | **Compatibilidad Cross-Browser** | Funcionamiento certificado en Google Chrome, Microsoft Edge, Safari, Firefox y navegadores móviles Chromium. |
| **RNF-07** | **Adaptabilidad Responsive** | Maquetación visualmente impecable desde resoluciones mínimas de 360px (móvil vertical) hasta 4K (3840px). |
| **RNF-08** | **Internacionalización** | Todos los textos y mensajes de error deben ser presentados en idioma español con soporte para localización futura. |

---

## 5. Criterios de Aceptación en Formato Gherkin

### Escenario 1: Autenticación exitosa de colaborador con documento y contraseña
```gherkin
Característica: Inicio de sesión con credenciales válidas
  Dado que el usuario navega a la página de inicio de sesión de Greenyard
  Cuando ingresa su número de documento "1037645123"
  Y escribe su contraseña correcta
  Y presiona el botón "Iniciar Sesión"
  Entonces el sistema muestra un indicador de carga en el botón
  Y el backend responde con código de estado HTTP 200 OK
  Y se inyecta la cookie de sesión segura HttpOnly en el navegador
  Y el sistema despliega un mensaje de bienvenida "Bienvenido de nuevo"
  Y redirige al usuario a la vista correspondiente a su perfil.
```

### Escenario 2: Intento de acceso de usuario con cuenta inactiva
```gherkin
Característica: Bloqueo de usuario inactivo
  Dado que el usuario con documento "1020304050" fue desactivado por el área de Gestión Humana
  Cuando intenta iniciar sesión en el sistema
  Entonces el backend responde con código de estado HTTP 403 Forbidden
  Y la interfaz no redirige al usuario
  Y muestra un mensaje de advertencia: "Tu cuenta se encuentra desactivada. Contacta al administrador del sistema."
  Y el intento queda registrado en la bitácora de auditoría de seguridad.
```

### Escenario 3: Forzar Single Sign-On para perfiles de Administrador
```gherkin
Característica: Restricción de acceso para Administradores
  Dado que el usuario con documento "71234567" posee el rol de Administrador en Greenyard
  Cuando ingresa su documento en el formulario regular
  Entonces el sistema detecta su perfil en el pre-chequeo
  Y no solicita contraseña estándar
  Y muestra un mensaje informativo: "Los administradores deben iniciar sesión con Microsoft."
  Y destaca visualmente el botón "Iniciar sesión con Microsoft 365".
```

---

## 6. Reglas de Negocio Institucionales (BR)

- **BR-01**: Ninguna contraseña en el sistema puede tener una longitud menor a 8 caracteres, ni carecer de al menos un número y una letra mayúscula.
- **BR-02**: Todo colaborador con correo `@jolifoods.com` o `@greenyard.com` debe tener habilitado el acceso mediante SSO con Microsoft.
- **BR-03**: En las terminales de portería física, el ingreso de guardas está exento de contraseña temporalmente por acuerdo de agilidad operativa, siempre y cuando la IP de origen pertenezca a la subred perimetral autorizada.
- **BR-04**: El tiempo de vida máximo del token de acceso (Access Token) no debe superar las 24 horas continuas; transcurrido este tiempo se debe renovar mediante refresh token o solicitar reingreso.
