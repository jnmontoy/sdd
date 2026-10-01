# Plantilla HTML de Correo Corporativo: Restablecimiento de Contraseña
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

Esta especificación define la **plantilla de correo electrónico corporativo** enviada a los colaboradores cuando solicitan recuperar o restablecer su clave de acceso.

Diseñada con **HTML transaccional en línea (inline-styles)** para garantizar máxima compatibilidad y renderizado perfecto en Microsoft Outlook (escritorio y web), Gmail, Apple Mail y clientes móviles de iOS/Android.

---

## 1. Parámetros Dinámicos del Correo

La plantilla acepta las siguientes variables de contexto (Jinja2 / Django Templates / Python `f-strings`):

| Variable | Tipo | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- |
| `{{ nombre_usuario }}` | String | Nombre y apellido del colaborador | `Joan Montoya` |
| `{{ numero_documento }}` | String | Cédula o identificador del usuario | `1020405060` |
| `{{ enlace_recuperacion }}` | URL | Enlace único de un solo uso (OTT) con token criptográfico | `https://app.jolifoods.com/auth/reset?token=a8f9...` |
| `{{ tiempo_expiracion_minutos }}` | Entero | Ventana de validez del enlace | `15` |
| `{{ ip_solicitante }}` | String | Dirección IP que generó la solicitud | `190.14.85.120` |
| `{{ fecha_hora_solicitud }}` | String | Marca de tiempo legible en zona horaria local | `30/09/2026 12:10 PM` |
| `{{ nombre_proyecto }}` | String | Módulo o aplicación destino | `Portal Corporativo` |

---

## 2. Código HTML Canónico (Inline CSS & Tablas para Máxima Compatibilidad)

```html
<!DOCTYPE html>
<html lang="es" xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Restablecimiento de Contraseña | Jolifoods</title>
  <!--[if mso]>
  <style type="text/css">
    body, table, td {font-family: Arial, Helvetica, sans-serif !important;}
  </style>
  <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%;">

  <!-- CONTENEDOR PRINCIPAL EXTERNO -->
  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #0f172a; min-height: 100vh;">
    <tr>
      <td align="center" style="padding: 40px 15px;">

        <!-- TARJETA CENTRAL DEL CORREO -->
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 580px; background-color: #1e293b; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4); overflow: hidden;">
          
          <!-- CABECERA CON BRANDING JOLIFOODS -->
          <tr>
            <td align="center" style="padding: 36px 30px 24px 30px; border-bottom: 1px solid rgba(255, 255, 255, 0.06); background: linear-gradient(180deg, rgba(16, 185, 129, 0.08) 0%, rgba(30, 41, 59, 0) 100%);">
              <!-- LOGO VECTORIAL O IMAGEN HOSTED -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center">
                    <span style="font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
                      Joli<span style="color: #10b981;">foods</span>
                    </span>
                  </td>
                </tr>
                <tr>
                  <td align="center" style="padding-top: 6px;">
                    <span style="font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px;">
                      {{ nombre_proyecto }} &bull; Seguridad de Identidad
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- CUERPO PRINCIPAL DEL MENSAJE -->
          <tr>
            <td style="padding: 32px 36px 20px 36px;">
              <h1 style="margin: 0 0 16px 0; font-size: 22px; font-weight: 700; color: #f8fafc; text-align: left; letter-spacing: -0.3px;">
                Restablecer contraseña de acceso
              </h1>
              
              <p style="margin: 0 0 20px 0; font-size: 15px; line-height: 1.6; color: #cbd5e1;">
                Hola <strong style="color: #ffffff;">{{ nombre_usuario }}</strong> (Doc. <span style="font-family: monospace; color: #10b981;">{{ numero_documento }}</span>),
              </p>

              <p style="margin: 0 0 28px 0; font-size: 14px; line-height: 1.6; color: #94a3b8;">
                Hemos recibido una solicitud para cambiar la contraseña de tu cuenta institucional. Haz clic en el botón siguiente para definir tu nueva clave de acceso seguro:
              </p>

              <!-- BOTÓN PRINCIPAL DE ACCIÓN (ESMERALDA INSTITUCIONAL) -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                  <td align="center" style="padding: 10px 0 28px 0;">
                    <!--[if mso]>
                    <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="{{ enlace_recuperacion }}" style="height:48px;v-text-anchor:middle;width:280px;" arcsize="18%" stroke="f" fillcolor="#10b981">
                    <w:anchorlock/>
                    <center style="color:#ffffff;font-family:Arial,sans-serif;font-size:15px;font-weight:bold;">Restablecer mi Contraseña</center>
                    </v:roundrect>
                    <![endif]-->
                    <!--[if !mso]><!-->
                    <a href="{{ enlace_recuperacion }}" target="_blank" style="display: inline-block; background-color: #10b981; color: #ffffff; font-size: 15px; font-weight: 700; text-decoration: none; padding: 14px 36px; border-radius: 10px; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35); text-align: center;">
                      Restablecer mi Contraseña
                    </a>
                    <!--<![endif]-->
                  </td>
                </tr>
              </table>

              <!-- ADVERTENCIA DE SEGURIDAD Y EXPIRACIÓN -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: rgba(15, 23, 42, 0.6); border-radius: 8px; border-left: 3px solid #10b981; margin-bottom: 24px;">
                <tr>
                  <td style="padding: 14px 16px;">
                    <p style="margin: 0; font-size: 13px; line-height: 1.5; color: #e2e8f0;">
                      <strong style="color: #10b981;">Importante:</strong> Este enlace caduca automáticamente en <strong>{{ tiempo_expiracion_minutos }} minutos</strong> y solo puede ser utilizado una única vez.
                    </p>
                  </td>
                </tr>
              </table>

              <!-- ENLACE DE TEXTO PLANO POR SI FALLA EL BOTÓN -->
              <p style="margin: 0 0 8px 0; font-size: 12px; color: #64748b; line-height: 1.5;">
                Si el botón no funciona, copia y pega la siguiente URL en tu navegador web:
              </p>
              <p style="margin: 0 0 24px 0; font-size: 12px; word-break: break-all; color: #10b981; font-family: monospace; background-color: #0b1120; padding: 10px 12px; border-radius: 6px;">
                {{ enlace_recuperacion }}
              </p>

              <!-- METADATOS DE SEGURIDAD / AUDITORÍA -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-top: 1px solid rgba(255, 255, 255, 0.06); padding-top: 18px;">
                <tr>
                  <td style="font-size: 11px; color: #64748b; line-height: 1.6;">
                    <strong>Detalles de la solicitud:</strong><br>
                    &bull; Dirección IP: <span style="font-family: monospace; color: #94a3b8;">{{ ip_solicitante }}</span><br>
                    &bull; Fecha y hora: <span style="color: #94a3b8;">{{ fecha_hora_solicitud }}</span>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- PIE DE PÁGINA INSTITUCIONAL -->
          <tr>
            <td style="padding: 20px 36px 30px 36px; background-color: #141f32; border-top: 1px solid rgba(255, 255, 255, 0.04); text-align: center;">
              <p style="margin: 0 0 6px 0; font-size: 12px; color: #94a3b8;">
                Si tú no realizaste esta solicitud, puedes ignorar este mensaje; tu contraseña actual continuará siendo segura.
              </p>
              <p style="margin: 0; font-size: 11px; color: #475569;">
                &copy; 2026 Jolifoods S.A.S. &bull; Todos los derechos reservados.<br>
                Este es un mensaje generado automáticamente por el sistema de seguridad. Por favor no responder a este correo.
              </p>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>
```

---

## 3. Implementación en Backend (Python / Django)

```python
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def enviar_correo_recuperacion(usuario, token_plano, request):
    enlace = f"{settings.FRONTEND_URL}/auth/reset?token={token_plano}"
    
    contexto = {
        "nombre_usuario": f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username,
        "numero_documento": usuario.numero_documento,
        "enlace_recuperacion": enlace,
        "tiempo_expiracion_minutos": 15,
        "ip_solicitante": request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR")),
        "fecha_hora_solicitud": "30/09/2026 12:10 PM",
        "nombre_proyecto": settings.APP_NAME or "Portal Jolifoods",
    }
    
    html_content = render_to_string("emails/recovery_password.html", contexto)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject="[Jolifoods] Restablecimiento de contraseña de acceso",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[usuario.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)
```
