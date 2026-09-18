"""Módulo de despacho de alertas por email para publicaciones de PROSPERIA Intelligence."""

import os
from pathlib import Path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional


def send_publication_email(
    title: str,
    slug: str,
    linkedin_url: Optional[str] = None,
    blog_url: Optional[str] = None,
    summary: Optional[str] = None,
    threads_text: Optional[str] = None,
    pdf_attached: bool = True,
    first_comment: Optional[str] = None
) -> bool:
    """Envía un correo ejecutivo a edward@agenciaprosperia.com confirmando la publicación en la web y LinkedIn."""
    smtp_host = os.environ.get("SMTP_HOST", "smtp.hostinger.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    smtp_user = os.environ.get("SMTP_USER", "edward@agenciaprosperia.com")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    recipient = os.environ.get("NOTIFICATION_EMAIL", "edward@agenciaprosperia.com")
    sender = os.environ.get("SMTP_SENDER", smtp_user)

    if not smtp_pass:
        print("[Alert Email] Falta SMTP_PASSWORD. No se pudo despachar el correo.")
        return False

    final_blog_url = blog_url or f"https://agenciaprosperia.com/blog/{slug}"
    final_linkedin_url = linkedin_url or "https://www.linkedin.com/in/edwardjimenezia/recent-activity/all/"

    subject = f"✅ [PROSPERIA] Publicado en Web y LinkedIn: {title[:60]}..."

    # Texto plano para clientes de correo sin HTML
    plain_parts = [
        f"¡Hola Edward!\n",
        f"Tu publicación matutina de PROSPERIA Intelligence ha quedado activa con éxito:\n",
        f"🌐 1. ARTÍCULO EN LA WEB:\n{final_blog_url}\n",
        f"💼 2. POST EN LINKEDIN:\n{final_linkedin_url}\n",
        f"• Carrusel PDF: {'Adjunto (8 láminas 4:5)' if pdf_attached else 'No adjunto'}",
        f"• Primer Comentario con enlace canónico: Publicado con éxito\n"
    ]
    if summary:
        plain_parts.append(f"📝 RESUMEN EJECUTIVO:\n{summary}\n")
    if threads_text:
        plain_parts.append(f"📱 COPYS PARA X Y THREADS (Opcional móvil):\n{threads_text}\n")
    plain_parts.append("\n---\nSistema Autónomo Cortexia 5×4×1 — Agencia ProsperIA")
    plain_content = "\n".join(plain_parts)

    # HTML profesional y adaptado a móviles
    threads_html = ""
    if threads_text:
        safe_threads = threads_text.replace("\n", "<br>")
        threads_html = f"""
        <div style="margin-top: 25px; padding: 20px; background: #030a16; border-radius: 12px; border: 1px solid rgba(0, 229, 255, 0.2);">
          <h3 style="color: #00e5ff; font-size: 15px; margin-top: 0; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px;">📱 Hilo para X y Threads (Listo para copiar):</h3>
          <div style="color: #cbd5e1; font-size: 13px; line-height: 1.6; font-family: monospace; max-height: 300px; overflow-y: auto; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px;">
            {safe_threads}
          </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #020710; color: #f8fafc; margin: 0; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: #051329; border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    
    <!-- Header -->
    <div style="background: linear-gradient(135deg, #05142b 0%, #030a14 100%); padding: 30px 25px; border-bottom: 1px solid rgba(0, 229, 255, 0.2); text-align: center;">
      <div style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #00e5ff; box-shadow: 0 0 10px #00e5ff; margin-right: 8px;"></div>
      <span style="color: #00e5ff; font-size: 12px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase;">PROSPERIA INTELLIGENCE</span>
      <h1 style="color: #ffffff; font-size: 20px; font-weight: 700; margin: 15px 0 0 0; line-height: 1.4;">{title}</h1>
    </div>

    <!-- Body -->
    <div style="padding: 30px 25px;">
      <p style="color: #94a3b8; font-size: 15px; margin-top: 0; line-height: 1.6;">
        Hola <strong>Edward</strong>, tu orquestador matutino ha publicado la rutina del día con éxito. Aquí tienes los enlaces directos para verificar desde tu teléfono:
      </p>

      <!-- Botón Web -->
      <div style="margin: 25px 0 15px 0;">
        <a href="{final_blog_url}" target="_blank" style="display: block; text-align: center; background: linear-gradient(135deg, #00e5ff 0%, #0ea5e9 100%); color: #020710; font-weight: 700; font-size: 15px; padding: 14px 20px; border-radius: 12px; text-decoration: none; box-shadow: 0 4px 15px rgba(0, 229, 255, 0.3);">
          🌐 Abrir Artículo en la Web
        </a>
      </div>

      <!-- Botón LinkedIn -->
      <div style="margin: 15px 0 25px 0;">
        <a href="{final_linkedin_url}" target="_blank" style="display: block; text-align: center; background: #0a66c2; color: #ffffff; font-weight: 700; font-size: 15px; padding: 14px 20px; border-radius: 12px; text-decoration: none; box-shadow: 0 4px 15px rgba(10, 102, 194, 0.3);">
          💼 Abrir Post en LinkedIn (con Carrusel PDF)
        </a>
      </div>

      <!-- Detalles de publicación -->
      <div style="background: rgba(2, 7, 16, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px; margin-bottom: 20px;">
        <p style="margin: 0 0 8px 0; font-size: 14px; color: #94a3b8;">
          📄 <strong>Carrusel Documento:</strong> <span style="color: #38bdf8;">8 Láminas en Formato PDF (4:5)</span>
        </p>
        <p style="margin: 0 0 8px 0; font-size: 14px; color: #94a3b8;">
          💬 <strong>Primer Comentario:</strong> <span style="color: #10b981;">Insertado con enlace canónico oficial</span>
        </p>
        <p style="margin: 0; font-size: 14px; color: #94a3b8;">
          📊 <strong>Slug en Producción:</strong> <code style="color: #00e5ff; font-size: 12px;">{slug}</code>
        </p>
      </div>

      {threads_html}

      <p style="color: #64748b; font-size: 12px; text-align: center; margin-top: 30px; margin-bottom: 0;">
        Enviado de forma autónoma desde el servidor de Agencia ProsperIA.<br>
        Disfruta tus vacaciones en Orlando. 🌴
      </p>
    </div>

  </div>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"PROSPERIA Intelligence <{sender}>"
    msg["To"] = recipient

    msg.attach(MIMEText(plain_content, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        # Intento primario con SSL 465
        server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15)
        server.login(smtp_user, smtp_pass)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
        print(f"✓ [Alerta Email] Correo de confirmación enviado exitosamente a {recipient} (SSL 465).")
        return True
    except Exception as e:
        print(f"Aviso SSL 465: {e}. Reintentando por TLS 587...")
        try:
            server = smtplib.SMTP(smtp_host, 587, timeout=15)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(sender, recipient, msg.as_string())
            server.quit()
            print(f"✓ [Alerta Email] Correo de confirmación enviado exitosamente a {recipient} (TLS 587).")
            return True
        except Exception as err:
            print(f"❌ [Alerta Email Error] No se pudo enviar el correo de confirmación: {err}")
            return False
