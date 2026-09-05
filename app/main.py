import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, time_tracking, users, projects
from app.core.security import hash_password
from app.db.base import engine, Base
from app.models import time_entry, user, project
from app.db.base import SessionLocal

# Esto crea la base de datos y TODAS las tablas automáticamente
Base.metadata.create_all(bind=engine)

bootstrap_admin_code = os.getenv("NEXUS_ADMIN_CODE")
bootstrap_admin_password = os.getenv("NEXUS_ADMIN_PASSWORD")
if bootstrap_admin_code and bootstrap_admin_password:
    bootstrap_db = SessionLocal()
    try:
        bootstrap_admin = bootstrap_db.query(user.User).filter(
            user.User.employee_code == bootstrap_admin_code
        ).first()
        if not bootstrap_admin:
            bootstrap_db.add(user.User(
                employee_code=bootstrap_admin_code,
                full_name="NexusMold Administrator",
                password=None,
                hashed_password=hash_password(bootstrap_admin_password),
                role="Admin",
            ))
            bootstrap_db.commit()
    finally:
        bootstrap_db.close()

app = FastAPI(title="NexusMold CLoud SaaS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("NEXUS_CORS_ORIGINS", "*").split(",")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conectamos las rutas
app.include_router(time_tracking.router, prefix="/api/v1/time", tags=["Control Horario"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Empleados (RRHH)"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Proyectos y Clientes"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])

@app.get("/")
def read_root():
    return {"mensaje": "¡El motor de NexusMold CLoud está encendido y funcionando!"}