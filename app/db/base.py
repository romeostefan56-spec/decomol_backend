from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Usamos SQLite (un archivo local) para empezar rápido
SQLALCHEMY_DATABASE_URL = "sqlite:///./decomol.db" 

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Plantilla base para nuestras tablas
Base = declarative_base()

# Función para que las rutas hablen con la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()