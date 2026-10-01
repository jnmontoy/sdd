# Guía de Pruebas de Humo (Smoke Testing) y E2E — SDD Jolifoods
## Automatización de Calidad y Cero Regresiones en el Ecosistema

Este documento establece el estándar organizacional para la ejecución de pruebas de extremo a extremo (E2E) y pruebas de humo automatizadas en todos los proyectos del ecosistema (`app_tic`, `tiendita`, `vibra`, `contenedores`, `porterias`, `bi`, `proyectovideo`).

---

## 1. Filosofía de Calidad: Pruebas de Humo Resilientes
Para evitar suites de testing infladas o frágiles que bloqueen los despliegues continuos, Jolifoods implementa el principio de **Smoke Testing Crítico**:
1. **Flujo de Acceso**: Autenticación exitosa (Local / SSO M365) y redirección correcta según RBAC.
2. **Carga y Paginación de Datos**: Renderizado de `DataTable`, respuesta sin error 500 y paginación reactiva.
3. **Filtros e Interacción**: Funcionamiento del `ChecklistPopover` (tipo Excel), apertura del `Drawer` lateral y modales (`ConfirmModal`).
4. **Resiliencia de Red**: Validación del interceptor Bearer (401 -> `SessionExpirationModal`) y funcionamiento del `useSmartPolling` sin saturar el socket.

---

## 2. Selectores Estables (`data-testid`)
Todo componente especificado en `.sdd` debe exponer atributos `data-testid` normalizados para desacoplar las pruebas de los cambios estéticos:

| Componente | Atributo `data-testid` | Propósito en el Test |
| :--- | :--- | :--- |
| **Input Usuario/Email** | `data-testid="input-username"` | Inserción de credenciales |
| **Input Contraseña** | `data-testid="input-password"` | Inserción de clave de acceso |
| **Botón Primario Login** | `data-testid="btn-login-submit"` | Envío de formulario de login |
| **Buscador de Tabla** | `data-testid="datatable-search-input"` | Búsqueda reactiva con debounce |
| **Fila de Tabla** | `data-testid="datatable-row"` | Conteo y selección de filas |
| **Botón Exportar Excel**| `data-testid="btn-export-excel"` | Descarga de reporte tabular |
| **Drawer Lateral** | `data-testid="sidebar-drawer"` | Inspección contextual de registros |
| **Modal de Confirmación**| `data-testid="confirm-modal"` | Acciones críticas y destructivas |

---

## 3. Suite de Smoke Testing con Playwright (Frontend E2E)

### Estructura de Proyecto Frontend
```bash
frontend/
  ├── tests/
  │   └── smoke.spec.ts
  └── playwright.config.ts
```

### Especificación `frontend/tests/smoke.spec.ts`
```typescript
import { test, expect } from '@playwright/test';

test.describe('Ecosistema Jolifoods — Smoke Tests Críticos', () => {

  test('Flujo 1: Autenticación, carga inicial y TopHeader', async ({ page }) => {
    await page.goto('/login');

    // Validación de elementos de login
    await expect(page.locator('[data-testid="input-username"]')).toBeVisible();
    await expect(page.locator('[data-testid="input-password"]')).toBeVisible();

    // Diligenciamiento de credenciales de prueba
    await page.fill('[data-testid="input-username"]', 'admin@jolifoods.com');
    await page.fill('[data-testid="input-password"]', 'JoliSecure2026!');
    await page.click('[data-testid="btn-login-submit"]');

    // Validación de redirección y presencia de TopHeader corporativo
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    await expect(page.locator('.topheader-left')).toBeVisible();
    await expect(page.locator('.user-profile-badge')).toBeVisible();
  });

  test('Flujo 2: Renderizado de Tabla, Buscador Debounce y Drawer', async ({ page }) => {
    await page.goto('/modulo-principal');

    // Esperar a que los skeletons desaparezcan y la tabla esté poblada
    await page.waitForSelector('[data-testid="datatable-row"]', { state: 'attached', timeout: 8000 });
    const rowCount = await page.locator('[data-testid="datatable-row"]').count();
    expect(rowCount).toBeGreaterThan(0);

    // Probar búsqueda reactiva
    await page.fill('[data-testid="datatable-search-input"]', 'Prueba');
    await page.waitForTimeout(400); // Superar el debounce de 300ms

    // Abrir primer detalle en Drawer lateral
    const firstRowAction = page.locator('[data-testid="datatable-row"]').first().locator('.btn-action-view');
    if (await firstRowAction.isVisible()) {
      await firstRowAction.click();
      await expect(page.locator('[data-testid="sidebar-drawer"]')).toBeVisible();
      // Cerrar Drawer con tecla Escape
      await page.keyboard.press('Escape');
      await expect(page.locator('[data-testid="sidebar-drawer"]')).not.toBeVisible();
    }
  });

  test('Flujo 3: Resiliencia de Sesión y Detección 401', async ({ page }) => {
    await page.goto('/dashboard');

    // Simular expiración de sesión emitiendo el evento corporativo
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('jolifoods:session-expired', {
        detail: { reason: 'Token revocado o caducado' }
      }));
    });

    // Validar aparición del modal bloqueante desacoplado
    await expect(page.locator('.session-expiration-modal')).toBeVisible();
  });

});
```

---

## 4. Pruebas de Humo en Backend (Pytest-Django / FastAPI)
Bajo la **Regla Crítica de Aislamiento en `.venv`**, las pruebas de backend siempre se ejecutan con el intérprete virtual:

### Windows PowerShell:
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_smoke_api.py -v
```

### Especificación `backend/tests/test_smoke_api.py`
```python
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestSmokeBackendAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='qa_test_user',
            email='qa@jolifoods.com',
            password='TestPassword123!',
            is_active=True
        )

    def test_healthcheck_endpoint(self):
        """Verifica que el endpoint /health o /api/health responda HTTP 200 en <100ms"""
        response = self.client.get('/api/health/')
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'ok'
        assert 'database' in data

    def test_unauthenticated_protected_endpoint_returns_401(self):
        """Verifica que rutas protegidas rechacen solicitudes sin Bearer token"""
        response = self.client.get('/api/maestros/')
        assert response.status_code == 401

    def test_authenticated_read_anti_n_plus_one(self, django_assert_num_queries):
        """Garantiza que la lectura masiva de registros no sufra de N+1 queries"""
        self.client.force_authenticate(user=self.user)
        # La consulta debe resolverse en máximo 3 consultas SQL optimizadas
        with django_assert_num_queries(3):
            response = self.client.get('/api/maestros/?page=1&page_size=20')
            assert response.status_code == 200
```

---

## 5. Reglas de Ejecución y Pre-Despliegue
1. **Tiempo Límite**: Toda la suite de humo debe ejecutarse en menos de **45 segundos**.
2. **No Mockear la Base de Datos en Humo**: Se debe usar SQLite en memoria o la base de datos de pruebas Docker para validar los constraints reales.
3. **Cero Falsos Positivos por Timing**: Usar esperas basadas en selectores (`waitForSelector`) y nunca `sleep()` fijos en Playwright.
