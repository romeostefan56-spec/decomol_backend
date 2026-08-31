from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.time_entry import TimeEntry, EntryType
from app.models.project import Client, Project
from app.models.user import User

router = APIRouter()

@router.post("/clock")
def clock_in_out(
    employee_code: str,
    action: str,
    password: str,
    location: str = "Nave Principal",
    db: Session = Depends(get_db)
):
    """Registra la entrada (CLOCK_IN) o salida (CLOCK_OUT) general del trabajador"""

    empleado = db.query(User).filter(User.employee_code == employee_code).first()
    if not empleado or empleado.password != password:
        raise HTTPException(status_code=401, detail="Error: Contraseña incorrecta o empleado no encontrado")

    # Validamos que el tipo de fichaje sea correcto
    if action not in ["CLOCK_IN", "CLOCK_OUT"]:
        raise HTTPException(status_code=400, detail="El tipo de fichaje debe ser CLOCK_IN o CLOCK_OUT")

    tipo_enum = EntryType.CLOCK_IN if action == "CLOCK_IN" else EntryType.CLOCK_OUT

    nuevo_fichaje = TimeEntry(
        user_id=empleado.id,
        entry_type=tipo_enum,
        location=location
    )
    db.add(nuevo_fichaje)
    db.commit()

    accion = "Entrada" if action == "CLOCK_IN" else "Salida"
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

@router.get("/entries")
def get_all_entries(db: Session = Depends(get_db)):
    return db.query(TimeEntry).order_by(TimeEntry.timestamp.desc()).limit(50).all()

@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    fichajes = db.query(TimeEntry).all()
    return {"total_fichajes": len(fichajes), "datos": fichajes}
@router.get("/report/employee/{employee_code}")
def get_employee_total_hours(employee_code: str, db: Session = Depends(get_db)):
    """Calcula el total de horas trabajadas por un empleado"""
    
    # PASO 1: El robot busca al empleado por su código secreto
    empleado = db.query(User).filter(User.employee_code == employee_code).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # PASO 2: El robot saca de la caja fuerte todos los tickets de trabajo (TASK) de ese empleado
    fichajes = db.query(TimeEntry).filter(
        TimeEntry.user_id == empleado.id,
        TimeEntry.entry_type == EntryType.TASK
    ).all()

    # PASO 3: El robot suma todos los minutos usando una calculadora mágica
    total_minutos = sum([f.duration_minutes for f in fichajes if f.duration_minutes])
    
    # PASO 4: Como sabemos que una hora tiene 60 minutos, dividimos para sacar las horas
    total_horas = total_minutos / 60

    # PASO 5: El robot nos entrega un reporte bonito y fácil de leer
    return {
        "empleado": empleado.full_name,
        "codigo": empleado.employee_code,
        "total_tareas_realizadas": len(fichajes),
        "total_minutos": total_minutos,
        "total_horas": round(total_horas, 2) # Redondeamos a 2 decimales (ej: 2.5 horas)
    }