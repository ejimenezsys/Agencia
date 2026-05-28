import os
import uuid
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request, Response, Depends, status, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Prosper IA API Stack", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Mock Database
SESSIONS = {}


SESSIONS = {}

INITIAL_LEADS = [
    {
        "id": 1,
        "name": "Carlos Mendoza",
        "email": "carlos.mendoza@technologysolutions.com",
        "company": "Technology Solutions",
        "phone": "+34 612 345 678",
        "status": "new",
        "source": "website",
        "score": 85,
        "created_at": "2026-05-19T10:15:30Z",
        "notes": "Interesado en automatizar el seguimiento de leads fríos por WhatsApp."
    },
    {
        "id": 2,
        "name": "Laura Gómez",
        "email": "laura.gomez@retailgroup.es",
        "company": "Retail Group España",
        "phone": "+34 654 321 098",
        "status": "contacted",
        "source": "social",
        "score": 70,
        "created_at": "2026-05-18T14:22:15Z",
        "notes": "Llamada inicial realizada. Quiere integrar el chatbot con su catálogo Shopify."
    },
    {
        "id": 3,
        "name": "Javier Ortiz",
        "email": "j.ortiz@innovatech.mx",
        "company": "InnovaTech S.A.",
        "phone": "+52 55 1234 5678",
        "status": "qualified",
        "source": "referral",
        "score": 90,
        "created_at": "2026-05-17T09:05:00Z",
        "notes": "Lead muy caliente. Presupuesto aprobado para IA en atención a clientes de nivel 1."
    },
    {
        "id": 4,
        "name": "Sofía Castro",
        "email": "sofia.castro@marketingdigital.co",
        "company": "Marketing Digital Co",
        "phone": "+57 300 987 6543",
        "status": "converted",
        "source": "email",
        "score": 95,
        "created_at": "2026-05-15T16:45:00Z",
        "notes": "Cerrada suscripción Plan Elite. SVE-90 desplegado y funcionando correctamente."
    },
    {
        "id": 5,
        "name": "Alejandra Ruiz",
        "email": "a.ruiz@bienesraices.net",
        "company": "Ruiz Bienes Raíces",
        "phone": "+34 677 889 900",
        "status": "lost",
        "source": "website",
        "score": 40,
        "created_at": "2026-05-14T11:30:00Z",
        "notes": "El cliente considera que es muy costoso para su volumen actual de ventas."
    },
    {
        "id": 6,
        "name": "Roberto Peña",
        "email": "roberto@constructorapena.com",
        "company": "Pena Constructores",
        "phone": "+34 600 112 233",
        "status": "new",
        "source": "other",
        "score": 65,
        "created_at": "2026-05-20T08:12:00Z",
        "notes": "Dejó mensaje preguntando si es posible programar recordatorios de pago automáticos."
    },
    {
        "id": 7,
        "name": "Lucía Fernández",
        "email": "lfernandez@educaciononline.edu",
        "company": "EducaOnline S.L.",
        "phone": "+34 622 334 455",
        "status": "qualified",
        "source": "social",
        "score": 80,
        "created_at": "2026-05-16T15:10:00Z",
        "notes": "Desea automatizar el proceso de admisión de alumnos y asignación de tutores."
    },
    {
        "id": 8,
        "name": "Miguel Torres",
        "email": "miguel@consultoria360.com",
        "company": "Consultores 360",
        "phone": "+34 699 887 766",
        "status": "contacted",
        "source": "website",
        "score": 75,
        "created_at": "2026-05-19T18:40:00Z",
        "notes": "Envió formulario pidiendo demo del agente conversacional por voz."
    }
]

DB_PATH = "prosper_ia.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            company TEXT,
            phone TEXT,
            plan TEXT,
            api_key TEXT
        )
    """)
    
    # 2. Create leads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT,
            phone TEXT,
            status TEXT DEFAULT 'new',
            source TEXT DEFAULT 'website',
            score INTEGER DEFAULT 50,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)
    
    # 3. Seed users if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (email, name, password, company, phone, plan, api_key)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "admin@prosperia.com",
            "Administrador Prosper",
            "admin1234",
            "Prosper IA Corp",
            "+34 600 000 000",
            "premium",
            "pk_live_51Hz8xProsperSecureToken99aB"
        ))
        
    # 4. Seed leads if empty
    cursor.execute("SELECT COUNT(*) FROM leads")
    if cursor.fetchone()[0] == 0:
        for lead in INITIAL_LEADS:
            cursor.execute("""
                INSERT INTO leads (id, name, email, company, phone, status, source, score, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead["id"],
                lead["name"],
                lead["email"],
                lead["company"],
                lead["phone"],
                lead["status"],
                lead["source"],
                lead["score"],
                lead["notes"],
                lead["created_at"]
            ))
            
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_db()


# Request schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdateRequest(BaseModel):
    name: str
    company: Optional[str] = None
    phone: Optional[str] = None

class PasswordUpdateRequest(BaseModel):
    password: str

class LeadCreateRequest(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = ""
    phone: Optional[str] = ""
    status: Optional[str] = "new"
    source: Optional[str] = "website"
    score: Optional[int] = 50
    notes: Optional[str] = ""

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = ""
    phone: Optional[str] = ""
    message: Optional[str] = ""
    source: Optional[str] = "website"

# Auth helper
def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token:
        token = request.cookies.get("auth_token")
        
    if not token or token not in SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido o ausente."
        )
    
    email = SESSIONS[token]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado."
        )
    return dict(row)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )

# ─── FRONTEND PAGES ─────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
@app.get("/login.html", response_class=HTMLResponse)
async def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/dashboard.html", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# ─── API ENDPOINTS ──────────────────────────────────────────────────────────

@app.post("/api/auth/login")
async def api_login(req: LoginRequest, response: Response):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (req.email,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Credenciales incorrectas."}
        )
        
    user = dict(row)
    if user["password"] != req.password:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Credenciales incorrectas."}
        )
    
    # Generate unique token
    token = f"token_{uuid.uuid4().hex}"
    SESSIONS[token] = req.email
    
    user_payload = {
        "name": user["name"],
        "email": user["email"],
        "company": user["company"],
        "phone": user["phone"],
        "plan": user["plan"],
        "api_key": user["api_key"]
    }
    
    response.set_cookie(key="auth_token", value=token, max_age=604800, path="/")
    
    return {
        "success": True,
        "data": {
            "token": token,
            "user": user_payload
        }
    }

@app.post("/api/auth/logout")
async def api_logout(request: Request, response: Response):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    if not token:
        token = request.cookies.get("auth_token")
        
    if token in SESSIONS:
        del SESSIONS[token]
        
    response.delete_cookie("auth_token")
    return {"success": True}

def send_email_notification(name: str, email: str, company: str, phone: str, message: str):
    notification_to = os.environ.get("NOTIFICATION_EMAIL", "ejimenezsys@gmail.com")
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    smtp_sender = os.environ.get("SMTP_SENDER", "noreply@prosper-ia.com")
    
    # Pre-process strings to avoid f-string backslash limitations in older Python versions
    message_html = message.replace('\n', '<br>')
    phone_clean = phone.replace('+', '').replace(' ', '')
    
    # Compose email subject and content (Premium SVE90 style HTML)
    subject = f"🔔 Nueva Aplicación SVE90: {name} ({company})"
    
    html_content = f"""
    <html>
      <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #020710; color: #ffffff; margin: 0; padding: 20px;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #050d1a; border: 1px solid rgba(0,229,255,0.2); border-radius: 12px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.5);">
          <!-- Header -->
          <tr style="background: linear-gradient(135deg, #081224 0%, #020710 100%); border-bottom: 1px solid rgba(0,229,255,0.15); text-align: center;">
            <td style="padding: 30px 20px;">
              <h1 style="color: #00e5ff; margin: 0; font-size: 26px; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase;">PROSPER IA</h1>
              <p style="color: #94a3b8; margin: 5px 0 0 0; font-size: 13px; font-weight: 600; letter-spacing: 0.5px;">NUEVA APLICACIÓN EJECUTIVA SVE90</p>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding: 35px 30px;">
              <h2 style="color: #ffffff; margin-top: 0; font-size: 18px; font-weight: 800; border-bottom: 1px solid rgba(0,229,255,0.25); padding-bottom: 8px;">Detalles de Prospección Directiva</h2>
              
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 15px;">
                <tr>
                  <td width="35%" style="padding: 10px 0; font-weight: bold; font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">Nombre completo:</td>
                  <td style="padding: 10px 0; font-size: 14px; color: #ffffff; font-weight: 600;">{name}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 0; font-weight: bold; font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">Email Corporativo:</td>
                  <td style="padding: 10px 0; font-size: 14px; color: #00e5ff; font-weight: 600;"><a href="mailto:{email}" style="color: #00e5ff; text-decoration: none; border-bottom: 1px dashed rgba(0,229,255,0.4);">{email}</a></td>
                </tr>
                <tr>
                  <td style="padding: 10px 0; font-weight: bold; font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">Nombre de Agencia:</td>
                  <td style="padding: 10px 0; font-size: 14px; color: #ffffff; font-weight: 600;">{company}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 0; font-weight: bold; font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">WhatsApp:</td>
                  <td style="padding: 10px 0; font-size: 14px; color: #00e5ff; font-weight: 600;"><a href="https://wa.me/{phone_clean}" style="color: #00e5ff; text-decoration: none;">{phone}</a></td>
                </tr>
              </table>
              
              <h2 style="color: #ffffff; margin-top: 30px; font-size: 18px; font-weight: 800; border-bottom: 1px solid rgba(0,229,255,0.25); padding-bottom: 8px;">Cuello de Botella Operativo / Notas</h2>
              <div style="background-color: rgba(0,229,255,0.03); border: 1px solid rgba(0,229,255,0.15); border-left: 4px solid #00e5ff; padding: 15px; margin-top: 15px; font-size: 14px; color: #cbd5e1; line-height: 1.6; border-radius: 4px;">
                {message_html}
              </div>
              
              <div style="margin-top: 40px; text-align: center;">
                <a href="http://127.0.0.1:8000/dashboard" style="background: linear-gradient(135deg, #00e5ff, #00b4cc); color: #020710; text-decoration: none; padding: 12px 28px; font-weight: bold; font-size: 13px; border-radius: 8px; display: inline-block; box-shadow: 0 4px 15px rgba(0,229,255,0.2); text-transform: uppercase; letter-spacing: 0.5px;">Acceder al CRM de Leads</a>
              </div>
            </td>
          </tr>
          <!-- Footer -->
          <tr style="background-color: #020710; text-align: center; border-top: 1px solid rgba(0,229,255,0.15);">
            <td style="padding: 20px; font-size: 11px; color: #64748b; line-height: 1.5;">
              Este es un correo automático de control generado por el Sistema Operativo SVE90.<br>
              © 2026 Prosper IA & PassportAI. Todos los derechos reservados.
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
    
    # Check if SMTP details are defined
    if not (smtp_host and smtp_user and smtp_pass):
        print(f"\n⚠️ [EMAIL NOTIFICATION MOCK]", flush=True)
        print(f"To: {notification_to}", flush=True)
        print(f"Subject: {subject}", flush=True)
        print(f"SMTP credentials not configured. Please define SMTP_HOST, SMTP_USER, SMTP_PASSWORD in environment variables to send real emails.", flush=True)
        print(f"Lead Name: {name} | Email: {email} | Company: {company} | Phone: {phone}", flush=True)
        print(f"Notes: {message}\n", flush=True)
        return
        
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_sender
        msg["To"] = notification_to
        
        text_content = f"Nueva Aplicación SVE90:\n\nNombre: {name}\nEmail: {email}\nAgencia: {company}\nTeléfono: {phone}\nMensaje: {message}"
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_sender, notification_to, msg.as_string())
        server.quit()
        print(f"📧 [EMAIL NOTIFICATION] Email sent successfully to {notification_to}!", flush=True)
    except Exception as e:
        print(f"❌ [EMAIL NOTIFICATION ERROR] Failed to send email to {notification_to}: {e}", flush=True)

@app.post("/api/auth/contact")
async def api_contact(req: ContactRequest, background_tasks: BackgroundTasks):
    conn = get_db()
    cursor = conn.cursor()
    created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    score = 75
    
    cursor.execute("""
        INSERT INTO leads (name, email, company, phone, status, source, score, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        req.name,
        req.email,
        req.company or "",
        req.phone or "",
        "new",
        req.source or "website",
        score,
        req.message or "",
        created_at
    ))
    conn.commit()
    conn.close()
    
    # Enviar email de notificación en segundo plano
    background_tasks.add_task(
        send_email_notification,
        name=req.name,
        email=req.email,
        company=req.company or "",
        phone=req.phone or "",
        message=req.message or ""
    )
    
    return {"success": True}

@app.get("/api/users/me")
async def api_get_profile(current_user: dict = Depends(get_current_user)):
    user_payload = {
        "name": current_user["name"],
        "email": current_user["email"],
        "company": current_user["company"],
        "phone": current_user["phone"],
        "plan": current_user["plan"],
        "api_key": current_user["api_key"]
    }
    return {"success": True, "data": user_payload}

@app.put("/api/users/me")
async def api_update_profile(req: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET name = ?, company = ?, phone = ?
        WHERE email = ?
    """, (req.name, req.company, req.phone, current_user["email"]))
    conn.commit()
    conn.close()
    return {"success": True}

@app.put("/api/users/me/password")
async def api_update_password(req: PasswordUpdateRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET password = ?
        WHERE email = ?
    """, (req.password, current_user["email"]))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/api/leads")
async def api_get_leads(
    status: Optional[str] = None,
    source: Optional[str] = None,
    limit: Optional[int] = 100,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if source:
        query += " AND source = ?"
        params.append(source)
        
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    leads = [dict(row) for row in rows]
    return {"success": True, "data": {"leads": leads}}

@app.post("/api/leads")
async def api_create_lead(req: LeadCreateRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    cursor.execute("""
        INSERT INTO leads (name, email, company, phone, status, source, score, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        req.name,
        req.email,
        req.company or "",
        req.phone or "",
        req.status or "new",
        req.source or "website",
        req.score if req.score is not None else 50,
        req.notes or "",
        created_at
    ))
    
    lead_id = cursor.lastrowid
    conn.commit()
    
    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    row = cursor.fetchone()
    conn.close()
    
    return {"success": True, "data": dict(row)}

@app.delete("/api/leads/{lead_id}")
async def api_delete_lead(lead_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM leads WHERE id = ?", (lead_id,))
    if not cursor.fetchone():
        conn.close()
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Lead no encontrado."}
        )
        
    cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.put("/api/leads/{lead_id}")
async def api_update_lead(lead_id: int, req: LeadCreateRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM leads WHERE id = ?", (lead_id,))
    if not cursor.fetchone():
        conn.close()
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Lead no encontrado."}
        )
        
    cursor.execute("""
        UPDATE leads
        SET name = ?, email = ?, company = ?, phone = ?, status = ?, source = ?, score = ?, notes = ?
        WHERE id = ?
    """, (
        req.name,
        req.email,
        req.company or "",
        req.phone or "",
        req.status or "new",
        req.source or "website",
        req.score if req.score is not None else 50,
        req.notes or "",
        lead_id
    ))
    
    conn.commit()
    
    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    row = cursor.fetchone()
    conn.close()
    
    return {"success": True, "data": dict(row)}

@app.get("/api/dashboard/stats")
async def api_get_stats(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new_count,
            SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END) as converted_count
        FROM leads
    """)
    row = cursor.fetchone()
    conn.close()
    
    total = row["total"] if row else 0
    new_leads = row["new_count"] if row and row["new_count"] is not None else 0
    converted = row["converted_count"] if row and row["converted_count"] is not None else 0
    
    revenue = converted * 2500
    rate = (converted / total * 100) if total > 0 else 0.0
    
    return {
        "success": True,
        "data": {
            "total_leads": total,
            "new_leads": new_leads,
            "converted_leads": converted,
            "total_revenue": revenue,
            "conversion_rate": rate
        }
    }
