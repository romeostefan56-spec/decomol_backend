import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Render puede entregar el formato antiguo postgres://.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL:
    print("Modo nube: usando PostgreSQL configurado en DATABASE_URL")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    print("Modo local: usando SQLite en ./decomol.db")
    engine = create_engine(
        "sqlite:///./decomol.db",
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()