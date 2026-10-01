# Metodología SDD — Spec-Driven Development
## Ecosistema Greenyard / Jolifoods

Repositorio oficial y estándar de ingeniería de software guiado por especificaciones (**Spec-Driven Development - SDD**). Diseñado para ser agnóstico, modular y 100% portable para desarrolladores y agentes de Inteligencia Artificial.

---

## 🎯 ¿Qué es SDD?

**Spec-Driven Development (SDD)** es un marco de trabajo donde los requerimientos, contratos de datos, prototipos interactivos y lineamientos de seguridad se definen formalmente de manera previa a la implementación. Permite a ingenieros e inteligencias artificiales generar código consistente, seguro y desacoplado, reduciendo drásticamente el retrabajo y la ambigüedad.

---

## 📂 Estructura del Repositorio

```text
.sdd/
├── assets/          # Identidad corporativa, logos SVG y recursos visuales oficiales
├── components/      # Catálogo y especificaciones de componentes de UI/UX reutilizables
├── greenfield/      # Especificaciones canónicas por módulo/página y guía maestra
│   ├── pages/       # Login, Dashboard, Auditoría, Roles, Usuarios, Perfil, etc.
│   └── SPEC_GUIDE.md# Guía maestra y protocolo de desarrollo con IA
├── mock/            # Entorno de prototipado interactivo sin dependencias (No-Code/Mockups)
├── model/           # Esquemas canónicos de base de datos (SQL y Django ORM)
└── stack/           # Plantilla de arquitectura backend/frontend (ASGI híbrido, Docker, seed)
```

---

## 🚀 Módulos y Contenido Principal

### 1. [Greenfield / Especificaciones](greenfield/SPEC_GUIDE.md)
Guías maestras para desarrolladores e IA:
- Protocolo de preguntas de negocio vs. desarrollo técnico.
- Especificaciones de arquitectura de páginas:
  - **Login**: Flujos de autenticación, MFA, restablecimiento de contraseñas y auditoría.
  - **Layout Maestro**: Sidebar colapsable, breadcrumbs, topbar y perfil.
  - **Dashboard**: Métricas KPI, widgets y control de visibilidad por roles.
  - **Auditoría & Logs**: Trazabilidad completa de eventos del sistema.
  - **Usuarios & Roles**: CRUD, matriz de permisos y control de acceso.

### 2. [Modelos Canónicos](model/README.md)
Diseño de datos estandarizado y portable:
- Esquemas SQL canónicos.
- Implementaciones de referencia para **Django ORM**.
- Modelos de usuario unificado, sesiones activas, auditoría de eventos y permisos granulares.

### 3. [Prototipado Interactivo (Mockups)](mock/README.md)
Prototipos funcionales en HTML/Vanilla JS y CSS puro:
- Sin necesidad de instalar herramientas adicionales ni node_modules para visualización inicial.
- Plantilla basada en datos JSON locales para validación inmediata con usuarios de negocio.

### 4. [Stack Tecnológico de Referencia](stack/README.md)
Arquitectura de producción lista para desplegar:
- **Backend Híbrido ASGI**: Django (ORM, Admin, Auth) + FastAPI (Endpoints asíncronos de alta concurrencia).
- **Contenedores**: `Dockerfile.backend`, `Dockerfile.frontend` y `docker-compose.yml` optimizados.
- **Seguridad**: Hardening de headers HTTP, protección CSRF, rate-limiting y manejo estricto de CORS.

---

## 🛠️ Cómo Utilizar este Repositorio

1. **Para un nuevo proyecto:**
   - Clona este repositorio o copia la carpeta `.sdd` en la raíz de tu proyecto.
   - Consulta `greenfield/SPEC_GUIDE.md` para seguir el protocolo de generación de código guiado por especificaciones.
2. **Para validar una pantalla con usuarios de negocio:**
   - Utiliza la plantilla de `mock/` para generar una vista interactiva navegable en cualquier navegador web.
3. **Para inicializar la infraestructura:**
   - Apóyate en los archivos de `stack/` para estructurar la base del backend y frontend de inmediato.

---

## 🔒 Estándares de Seguridad y Calidad
- Autenticación robusta con cookies `HttpOnly`, `SameSite=Lax/Strict` y `Secure`.
- Principio de menor privilegio en roles y control de acceso (RBAC).
- Registro de auditoría inmutable de eventos críticos.
- Agnosticismo de entorno: Toda configuración sensible debe consumirse desde variables de entorno (`.env`).
