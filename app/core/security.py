from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.time_entry import TimeEntry, EntryType
from app.models.user import User
import uuid

router = APIRouter()

# Almacén en memoria para pulseras válidas (en producción usar Redis)
pulseras_validas = {}


def crear_pulsera_vip(employee_code: str) -> str:
    pulsera = f"VIP-{employee_code}-{uuid.uuid4().hex[:12].upper()}"
    pulseras_validas[pulsera] = employee_code
    return pulsera


def validar_pulsera_vip(authorization: str = Header(None)) -> str:
    """Valida la pulsera VIP desde el header Authorization: Bearer <pulsera>"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Pulsera VIP no proporcionada")
    
    pulsera = authorization.replace("Bearer ", "").strip()
    
    if pulsera not in pulseras_validas:
        raise HTTPException(status_code=401, detail="Pulsera VIP inválida o expirada")
    
    return pulseras_validas[pulsera]


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
