import os
import sqlite3
import hashlib
import hmac
import secrets
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_PATH = os.environ.get("DATABASE_PATH", "prosper_ia.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    """Genera un hash PBKDF2 con sal aleatoria; nunca persiste texto plano."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PASSWORD_ITERATIONS)
    return f"{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iterations, salt_hex, digest_hex = stored.split("$", 3)
        if scheme != PASSWORD_SCHEME:
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except (AttributeError, TypeError, ValueError):
        return False

class User(Base):
    """Modelo ORM para la tabla de usuarios administradores."""
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    company = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    plan = Column(String, nullable=True)
    api_key = Column(String, nullable=True)

class Lead(Base):
    """Modelo ORM para almacenar prospectos (leads) calificados."""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    company = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(String, default="new", nullable=False)
    source = Column(String, default="website", nullable=False)
    score = Column(Integer, default=50, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(String, nullable=False)

class SessionModel(Base):
    """Modelo ORM para almacenar tokens de sesión activos."""
    __tablename__ = "sessions"

    token = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=False)
    created_at = Column(String, nullable=False)

class BlogPost(Base):
    """Modelo ORM para almacenar artículos de blog del sistema."""
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    published_at = Column(String, nullable=False)
    author = Column(String, nullable=False)

class IntegrationSetting(Base):
    """Modelo ORM para almacenar configuraciones de integración (GHL, n8n, etc.)."""
    __tablename__ = "integration_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=True)

def init_db():
    """Inicializa la base de datos y crea las tablas correspondientes."""
    Base.metadata.create_all(bind=engine)
    
    # Realizar precarga (seed) de datos por defecto si están vacías las tablas
    db = SessionLocal()
    try:
        # Seed Admin User
        admin_email = os.environ.get("ADMIN_EMAIL")
        admin_password = os.environ.get("ADMIN_PASSWORD")
        if db.query(User).count() == 0 and admin_email and admin_password:
            admin = User(
                email=admin_email,
                name=os.environ.get("ADMIN_NAME", "Administrador ProsperIA"),
                password=hash_password(admin_password),
                company=os.environ.get("ADMIN_COMPANY", "Prosper IA Corp"),
                phone=os.environ.get("ADMIN_PHONE"),
                plan=os.environ.get("ADMIN_PLAN", "premium"),
                api_key=os.environ.get("ADMIN_API_KEY")
            )
            db.add(admin)
            
        # Seed Integration Settings
        default_settings = {
            "ghl_webhook_url": os.environ.get("GHL_WEBHOOK_URL", ""),
            "n8n_webhook_url": "",
            "whatsapp_status": "pending",
            "whatsapp_token": "",
            "whatsapp_phone_id": ""
        }
        for key, val in default_settings.items():
            exists = db.query(IntegrationSetting).filter(IntegrationSetting.key == key).first()
            if not exists:
                setting = IntegrationSetting(key=key, value=val)
                db.add(setting)
            
        # Seed Leads
        if db.query(Lead).count() == 0:
            from main import INITIAL_LEADS
            for lead_data in INITIAL_LEADS:
                lead = Lead(
                    id=lead_data["id"],
                    name=lead_data["name"],
                    email=lead_data["email"],
                    company=lead_data.get("company"),
                    phone=lead_data.get("phone"),
                    status=lead_data.get("status", "new"),
                    source=lead_data.get("source", "website"),
                    score=lead_data.get("score", 50),
                    notes=lead_data.get("notes"),
                    created_at=lead_data["created_at"]
                )
                db.add(lead)
                
        # Seed Blog Posts
        from main import INITIAL_BLOG_POSTS
        seeded_slugs = set()
        for post_data in INITIAL_BLOG_POSTS:
            if post_data["slug"] in seeded_slugs:
                continue
            seeded_slugs.add(post_data["slug"])
            exists = db.query(BlogPost).filter(BlogPost.slug == post_data["slug"]).first()
            if not exists:
                post = BlogPost(
                    slug=post_data["slug"],
                    title=post_data["title"],
                    category=post_data["category"],
                    summary=post_data["summary"],
                    content=post_data["content"],
                    image_url=post_data["image_url"],
                    published_at=post_data["published_at"],
                    author=post_data["author"]
                )
                db.add(post)

        # Los artículos nuevos aprobados son archivos versionados; SQLite es su índice de lectura.
        published_dir = Path(__file__).parent / "content" / "editorial_published"
        for article_path in published_dir.glob("*.json"):
            article = json.loads(article_path.read_text(encoding="utf-8"))
            if article.get("status") != "published":
                continue
            values = {
                "title": article["title"],
                "category": article["lane"],
                "summary": article["summary"],
                "content": article["content"],
                "image_url": article.get("image_url", "/static/logo_prosper_ia_cropped.jpg"),
                "published_at": article["published_at"],
                "author": article["author"],
            }
            existing_article = db.query(BlogPost).filter(BlogPost.slug == article["slug"]).first()
            if existing_article is None:
                db.add(BlogPost(slug=article["slug"], **values))
            else:
                for key, value in values.items():
                    setattr(existing_article, key, value)
                
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

def get_db_session():
    """Generador de sesiones de base de datos para dependencias FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sync_blog_posts(db):
    """Sincroniza los posts de INITIAL_BLOG_POSTS con la base de datos.

    Inserta posts nuevos y actualiza el image_url de los existentes
    si difiere del valor en código. Esto permite que los artículos
    generados por GitHub Actions aparezcan en producción sin rebuild,
    y que las rutas de imagen se corrijan automáticamente.

    Args:
        db: Sesión activa de SQLAlchemy.
    """
    from main import INITIAL_BLOG_POSTS
    synced_slugs = set()
    for post_data in INITIAL_BLOG_POSTS:
        if post_data["slug"] in synced_slugs:
            continue
        synced_slugs.add(post_data["slug"])
        exists = db.query(BlogPost).filter(BlogPost.slug == post_data["slug"]).first()
        if not exists:
            post = BlogPost(
                slug=post_data["slug"],
                title=post_data["title"],
                category=post_data["category"],
                summary=post_data["summary"],
                content=post_data["content"],
                image_url=post_data["image_url"],
                published_at=post_data["published_at"],
                author=post_data["author"]
            )
            db.add(post)
        elif exists.image_url != post_data["image_url"]:
            # Actualizar la ruta de imagen si cambió en el código fuente
            exists.image_url = post_data["image_url"]
    db.commit()
