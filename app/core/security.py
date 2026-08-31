from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.time_entry import TimeEntry, EntryType
from app.models.user import User
import uuid

router = APIRouter()


def crear_pulsera_vip(employee_code: str) -> str:
    return f"VIP-{employee_code}-{uuid.uuid4().hex[:12].upper()}"


@router.post("/clock")
def clock_in_out(
    employee_code: str,
    entry_type: str,
    location: str,
    password: str,
    db: Session = Depends(get_db),
):
    """El guardia del Taller. Pide contraseña y reparte pulseras VIP al entrar."""

    empleado = db.query(User).filter(User.employee_code == employee_code).first()

    if not empleado or empleado.password != password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    if entry_type not in ["CLOCK_IN", "CLOCK_OUT"]:
        raise HTTPException(status_code=400, detail="El tipo de fichaje debe ser CLOCK_IN o CLOCK_OUT")

    tipo_enum = EntryType.CLOCK_IN if entry_type == "CLOCK_IN" else EntryType.CLOCK_OUT
    nuevo_fichaje = TimeEntry(
        user_id=empleado.id,
        entry_type=tipo_enum,
        location=location,
    )
    db.add(nuevo_fichaje)
    db.commit()

    pulsera = None
    if entry_type == "CLOCK_IN":
        pulsera = crear_pulsera_vip(empleado.employee_code)

    return {
        "mensaje": f"¡Fichaje de {entry_type} correcto!",
        "token": pulsera,
    }
