import csv
import io

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.security import crear_pulsera_vip, require_admin, validar_pulsera_vip, verify_password
from app.db.base import get_db
from app.models.project import Client, Project
from app.models.time_entry import EntryType, LocationType, TimeEntry
from app.models.user import User

router = APIRouter()


@router.post("/clock")
def clock_in_out(
    employee_code: str,
    action: str | None = None,
    entry_type: str | None = None,
    password: str | None = None,
    location: str = "Taller",
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
):
    empleado = db.query(User).filter(User.employee_code == employee_code).first()
    if not empleado:
        raise HTTPException(status_code=401, detail="Empleado no encontrado o credenciales incorrectas")

    tipo_accion = action or entry_type
    if tipo_accion not in ["CLOCK_IN", "CLOCK_OUT"]:
        raise HTTPException(status_code=400, detail="El tipo de fichaje debe ser CLOCK_IN o CLOCK_OUT")

    token_employee = validar_pulsera_vip(authorization) if authorization else None
    if password is not None:
        if not verify_password(password, empleado.password, empleado.hashed_password):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    elif token_employee != employee_code:
        raise HTTPException(status_code=401, detail="Contraseña o token VIP requerido")

    locations = {
        "Taller": LocationType.NAVE,
        "Nave Principal": LocationType.NAVE,
        "Obra": LocationType.OBRA,
        "Oficina": LocationType.OFICINA,
    }
    nuevo_fichaje = TimeEntry(
        user_id=empleado.id,
        entry_type=EntryType(tipo_accion),
        location=locations.get(location, LocationType.NAVE),
    )
    db.add(nuevo_fichaje)
    db.commit()

    accion = "Entrada" if tipo_accion == "CLOCK_IN" else "Salida"
    return {
        "estado": "Registrado",
        "mensaje": f"¡{accion} correcta! {empleado.full_name} ha fichado en {location}",
        "token": crear_pulsera_vip(empleado.employee_code, empleado.role) if tipo_accion == "CLOCK_IN" else None,
    }


@router.post("/task")
def register_task(
    employee_code: str,
    client_code: str,
    duration_minutes: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    employee_from_token = validar_pulsera_vip(authorization)
    if employee_from_token != employee_code:
        raise HTTPException(status_code=403, detail="Token no corresponde a este empleado")
    if duration_minutes < 1:
        raise HTTPException(status_code=400, detail="La duración debe ser mayor que cero")

    empleado = db.query(User).filter(User.employee_code == employee_code).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    cliente = db.query(Client).filter(Client.client_code == client_code).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Código de cliente incorrecto")
    tarea = db.query(Project).filter(Project.client_id == cliente.id).first()
    if not tarea:
        raise HTTPException(status_code=400, detail="La obra no tiene un proyecto asociado")

    nueva_tarea = TimeEntry(
        user_id=empleado.id,
        entry_type=EntryType.TASK,
        project_id=tarea.id,
        location=LocationType.OBRA,
        duration_minutes=duration_minutes,
    )
    db.add(nueva_tarea)
    db.commit()
    return {
        "estado": "Guardado",
        "pantalla_trabajador": f"{cliente.client_code} {cliente.name} {tarea.name}".strip(),
    }


@router.get("/report/client/{client_code}")
def get_client_report(client_code: str, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    cliente = db.query(Client).filter(Client.client_code == client_code).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    proyectos_ids = [project.id for project in cliente.projects]
    fichajes = db.query(TimeEntry).filter(TimeEntry.project_id.in_(proyectos_ids)).all()
    total_minutos = sum(entry.duration_minutes or 0 for entry in fichajes)
    return {
        "codigo_cliente": cliente.client_code,
        "cliente": cliente.name,
        "total_fichajes_registrados": len(fichajes),
        "total_horas_acumuladas": round(total_minutos / 60, 2),
    }


@router.get("/employee/{employee_code}/history")
def get_employee_history(employee_code: str, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    empleado = db.query(User).filter(User.employee_code == employee_code).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    fichajes = db.query(TimeEntry).filter(TimeEntry.user_id == empleado.id).all()
    return {
        "empleado": empleado.full_name,
        "codigo": empleado.employee_code,
        "total_registros": len(fichajes),
        "fichajes": fichajes,
    }


@router.get("/entries")
def get_all_entries(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    entries = db.query(TimeEntry).order_by(TimeEntry.timestamp.desc()).limit(50).all()
    return [
        {
            "id": entry.id,
            "timestamp": entry.timestamp,
            "entry_type": entry.entry_type.value,
            "location": entry.location.value if entry.location else None,
            "duration_minutes": entry.duration_minutes,
            "employee_code": db.query(User.employee_code).filter(User.id == entry.user_id).scalar(),
            "project_id": entry.project_id,
        }
        for entry in entries
    ]


@router.get("/history")
def get_history(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    fichajes = db.query(TimeEntry).all()
    return {"total_fichajes": len(fichajes), "datos": fichajes}


@router.get("/report/employee/{employee_code}")
def get_employee_total_hours(employee_code: str, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    empleado = db.query(User).filter(User.employee_code == employee_code).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    fichajes = db.query(TimeEntry).filter(
        TimeEntry.user_id == empleado.id,
        TimeEntry.entry_type == EntryType.TASK,
    ).all()
    total_minutos = sum(entry.duration_minutes or 0 for entry in fichajes)
    return {
        "empleado": empleado.full_name,
        "codigo": empleado.employee_code,
        "total_tareas_realizadas": len(fichajes),
        "total_minutos": total_minutos,
        "total_horas": round(total_minutos / 60, 2),
    }


@router.get("/export/excel")
def exportar_horas_excel(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(["Codigo Empleado", "Nombre", "Horas Totales Trabajadas"])
    for emp in db.query(User).all():
        fichajes = db.query(TimeEntry).filter(
            TimeEntry.user_id == emp.id,
            TimeEntry.entry_type == EntryType.TASK,
        ).all()
        total_minutos = sum(entry.duration_minutes or 0 for entry in fichajes)
        escritor.writerow([emp.employee_code, emp.full_name, round(total_minutos / 60, 2)])
    return Response(
        content=salida.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=informe_horas_nexusmold_cloud.csv"},
    )
