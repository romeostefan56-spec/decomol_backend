from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.security import hash_password, require_admin
from app.db.base import get_db
from app.models.user import User

router = APIRouter()


@router.get("")
def list_users(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return [
        {"id": user.id, "employee_code": user.employee_code, "full_name": user.full_name, "role": user.role}
        for user in db.query(User).order_by(User.employee_code).all()
    ]

@router.post("/create")
def create_user(
    employee_code: str,
    full_name: str,
    password: str,
    role: str = "Worker",
    _: str = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Da de alta a un nuevo empleado en la base de datos de NexusMold CLoud"""

    if db.query(User).filter(User.employee_code == employee_code).first():
        raise HTTPException(status_code=400, detail=f"El empleado con código '{employee_code}' ya existe")

    if role not in {"Worker", "Admin", "HR"}:
        raise HTTPException(status_code=400, detail="Rol no válido")

    nuevo_empleado = User(
        employee_code=employee_code,
        full_name=full_name,
        password=None,
        hashed_password=hash_password(password),
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
def reset_password(
    employee_code: str,
    new_password: str,
    _: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.employee_code == employee_code).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    db_user.password = None
    db_user.hashed_password = hash_password(new_password)
    db.commit()
    return {"message": f"Contraseña actualizada con éxito para el empleado {employee_code}"}


@router.put("/{employee_code}")
def update_user(
    employee_code: str,
    full_name: str,
    role: str = "Worker",
    _: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if role not in {"Worker", "Admin", "HR"}:
        raise HTTPException(status_code=400, detail="Rol no válido")
    db_user = db.query(User).filter(User.employee_code == employee_code).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    db_user.full_name = full_name.strip()
    db_user.role = role
    db.commit()
    return {"message": f"Empleado {employee_code} actualizado correctamente"}


@router.delete("/{employee_code}")
def delete_user(employee_code: str, _: str = Depends(require_admin), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.employee_code == employee_code).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    if db_user.role == "Admin":
        raise HTTPException(status_code=400, detail="No se puede eliminar un administrador")
    db.delete(db_user)
    db.commit()
    return {"message": f"Empleado {employee_code} eliminado correctamente"}