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
    """Da de alta a un nuevo empleado en la base de datos de NexusMold CLoud"""

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


@router.put("/{employee_code}/reset-password")
def reset_password(employee_code: str, new_password: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.employee_code == employee_code).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    db_user.password = new_password
    db_user.hashed_password = new_password
    db.commit()
    return {"message": f"Contraseña actualizada con éxito para el empleado {employee_code}"}