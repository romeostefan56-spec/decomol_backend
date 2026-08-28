from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.time_entry import TimeEntry, EntryType
from app.models.project import Client, Project
from app.models.user import User

router = APIRouter()

@router.post("/clock")
def clock_in_out(employee_code: str, entry_type: str, location: str, db: Session = Depends(get_db)):
    """Registra la entrada (CLOCK_IN) o salida (CLOCK_OUT) general del trabajador"""

    empleado = db.query(User).filter(User.employee_code == employee_code).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # Validamos que el tipo de fichaje sea correcto
    if entry_type not in ["CLOCK_IN", "CLOCK_OUT"]:
        raise HTTPException(status_code=400, detail="El tipo de fichaje debe ser CLOCK_IN o CLOCK_OUT")

    tipo_enum = EntryType.CLOCK_IN if entry_type == "CLOCK_IN" else EntryType.CLOCK_OUT

    nuevo_fichaje = TimeEntry(
        user_id=empleado.id,
        entry_type=tipo_enum,
        location=location
    )
    db.add(nuevo_fichaje)
    db.commit()

    accion = "Entrada" if entry_type == "CLOCK_IN" else "Salida"
    return {
        "estado": "Registrado",
        "mensaje": f"¡{accion} correcta! {empleado.full_name} ha fichado en {location}"
    }

@router.post("/task")
def register_task(employee_code: str, client_code: str, duration_minutes: int, db: Session = Depends(get_db)):
    empleado = db.query(User).filter(User.employee_code == employee_code).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    cliente = db.query(Client).filter(Client.client_code == client_code).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Código de cliente incorrecto")

    tarea = db.query(Project).filter(Project.client_id == cliente.id).first()
    
    nueva_tarea = TimeEntry(
        user_id=empleado.id,
        entry_type=EntryType.TASK,
        project_id=tarea.id if tarea else None,
        duration_minutes=duration_minutes
    )
    db.add(nueva_tarea)
    db.commit()
    
    nombre_tarea = tarea.name if tarea else ""
    resumen = f"{cliente.client_code} {cliente.name} {nombre_tarea}".strip()
    
    return {
        "estado": "Guardado",
        "pantalla_trabajador": resumen
    }

@router.get("/report/client/{client_code}")
def get_client_report(client_code: str, db: Session = Depends(get_db)):
    """ADMIN: Muestra el total de horas acumuladas en un cliente por su código"""

    cliente = db.query(Client).filter(Client.client_code == client_code).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    proyectos_ids = [p.id for p in cliente.projects]
    fichajes = db.query(TimeEntry).filter(TimeEntry.project_id.in_(proyectos_ids)).all()

    total_minutos = sum([f.duration_minutes for f in fichajes if f.duration_minutes])
    total_horas = total_minutos / 60

    return {
        "codigo_cliente": cliente.client_code,
        "cliente": cliente.name,
        "total_fichajes_registrados": len(fichajes),
        "total_horas_acumuladas": round(total_horas, 2)
    }

@router.get("/employee/{employee_code}/history")
def get_employee_history(employee_code: str, db: Session = Depends(get_db)):
    """Devuelve el historial de fichajes y horas de un operario específico"""

    empleado = db.query(User).filter(User.employee_code == employee_code).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    fichajes = db.query(TimeEntry).filter(TimeEntry.user_id == empleado.id).all()

    return {
        "empleado": empleado.full_name,
        "codigo": empleado.employee_code,
        "total_registros": len(fichajes),
        "fichajes": fichajes
    }

@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    fichajes = db.query(TimeEntry).all()
    return {"total_fichajes": len(fichajes), "datos": fichajes}