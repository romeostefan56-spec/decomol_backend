from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import time_tracking, users, projects
from app.db.base import engine, Base
from app.models import time_entry, user, project

# Esto crea la base de datos y TODAS las tablas automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Decomol SaaS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conectamos las rutas
app.include_router(time_tracking.router, prefix="/api/v1/time", tags=["Control Horario"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Empleados (RRHH)"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Proyectos y Clientes"])

@app.get("/")
def read_root():
    return {"mensaje": "¡El motor de Decomol está encendido y funcionando!"}