import os
import sqlite3
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

def init_db():
    """Inicializa la base de datos y crea las tablas correspondientes."""
    Base.metadata.create_all(bind=engine)
    
    # Realizar precarga (seed) de datos por defecto si están vacías las tablas
    db = SessionLocal()
    try:
        # Seed Admin User
        if db.query(User).count() == 0:
            admin = User(
                email="admin@prosperia.com",
                name="Administrador Prosper",
                password="admin1234",
                company="Prosper IA Corp",
                phone="+34 600 000 000",
                plan="premium",
                api_key="pk_live_51Hz8xProsperSecureToken99aB"
            )
            db.add(admin)
            
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
        if db.query(BlogPost).count() == 0:
            from main import INITIAL_BLOG_POSTS
            for post_data in INITIAL_BLOG_POSTS:
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
