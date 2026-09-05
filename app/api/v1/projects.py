from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.security import require_admin
from app.db.base import get_db
from app.models.project import Client, Project
from app.models.time_entry import TimeEntry

router = APIRouter()


@router.get("/clients")
def list_clients(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return [
        {"id": client.id, "client_code": client.client_code, "name": client.name,
         "projects": [{"id": project.id, "name": project.name} for project in client.projects]}
        for client in db.query(Client).order_by(Client.client_code).all()
    ]

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


@router.put("/client/{client_code}")
def update_client(
    client_code: str,
    name: str,
    _: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    client = db.query(Client).filter(Client.client_code == client_code).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    client.name = name.strip()
    db.commit()
    return {"mensaje": "Cliente actualizado correctamente"}


@router.delete("/client/{client_code}")
def delete_client(client_code: str, _: str = Depends(require_admin), db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.client_code == client_code).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for project in list(client.projects):
        db.query(TimeEntry).filter(TimeEntry.project_id == project.id).delete(synchronize_session=False)
        db.delete(project)
    db.delete(client)
    db.commit()
    return {"mensaje": "Cliente y sus obras eliminados correctamente"}


@router.put("/project/{project_id}")
def update_project(
    project_id: int,
    name: str,
    client_code: str | None = None,
    _: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if client_code:
        client = db.query(Client).filter(Client.client_code == client_code).first()
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        project.client_id = client.id
    project.name = name.strip()
    db.commit()
    return {"mensaje": "Obra actualizada correctamente"}


@router.delete("/project/{project_id}")
def delete_project(project_id: int, _: str = Depends(require_admin), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    db.query(TimeEntry).filter(TimeEntry.project_id == project.id).delete(synchronize_session=False)
    db.delete(project)
    db.commit()
    return {"mensaje": "Obra eliminada correctamente"}