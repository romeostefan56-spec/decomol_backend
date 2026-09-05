from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.security import require_admin
from app.db.base import get_db
from app.models.project import Client, Project

router = APIRouter()

@router.post("/client")
def create_client(
    name: str,
    client_code: str | None = None,
    _: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Da de alta a un nuevo cliente (Ej: Promotora XYZ)"""
    codigo = (client_code or name or "").strip()
    if not codigo:
        raise HTTPException(status_code=400, detail="Falta el código del cliente")
    if len(codigo) < 4:
        raise HTTPException(status_code=400, detail="El código del cliente debe tener al menos 4 caracteres")

    if db.query(Client).filter(Client.client_code == codigo).first():
        raise HTTPException(status_code=400, detail=f"El cliente con código '{codigo}' ya existe")

    nuevo_cliente = Client(client_code=codigo, name=name)
    try:
        db.add(nuevo_cliente)
        db.flush()
        db.add(Project(name=name, client_id=nuevo_cliente.id))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"El cliente con código '{codigo}' ya existe")
    return {"mensaje": f"¡Cliente '{name}' con código '{codigo}' añadido a la base de datos!"}

@router.post("/project")
def create_project(
    name: str,
    client_id: int | None = None,
    client_code: str | None = None,
    _: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Crea un nuevo proyecto/obra y lo asocia a un cliente"""
    if client_id is None:
        if not client_code:
            raise HTTPException(status_code=400, detail="Debes indicar client_id o client_code")
        cliente = db.query(Client).filter(Client.client_code == client_code).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        client_id = cliente.id

    cliente = db.query(Client).filter(Client.id == client_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    nuevo_proyecto = Project(name=name, client_id=cliente.id)
    db.add(nuevo_proyecto)
    db.commit()
    return {"mensaje": f"¡Proyecto '{name}' creado correctamente para el cliente '{cliente.name}'!"}