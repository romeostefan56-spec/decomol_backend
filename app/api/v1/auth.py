from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import crear_pulsera_vip, verify_password
from app.db.base import get_db
from app.models.user import User

router = APIRouter()


@router.post("/login")
def admin_login(employee_code: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.employee_code == employee_code).first()
    if not user or user.role != "Admin" or not verify_password(password, user.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales de administrador incorrectas")
    return {"token": crear_pulsera_vip(user.employee_code, user.role), "employee_code": user.employee_code}