from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.user import User

router = APIRouter()

@router.post("/create")
def create_user(
    employee_code: str,
    full_name: str,
    password: str,
    role: str = "Worker",
    db: Session = Depends(get_db)
):
    """Da de alta a un nuevo empleado en la base de datos de Decomol"""

    if db.query(User).filter(User.employee_code == employee_code).first():
        raise HTTPException(status_code=400, detail=f"El empleado con código '{employee_code}' ya existe")

    nuevo_empleado = User(
        employee_code=employee_code,
        full_name=full_name,
        password=password,
        hashed_password="password_falsa_por_ahora",
        role=role
    )

    try:
        db.add(nuevo_empleado)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"El empleado con código '{employee_code}' ya existe")

    return {"mensaje": f"¡Éxito! El empleado {full_name} ({employee_code}) ha sido dado de alta como {role}."}