import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Header, HTTPException
from jose import JWTError, jwt

JWT_SECRET = os.getenv("NEXUS_JWT_SECRET", "change-this-secret-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.getenv("NEXUS_JWT_EXPIRE_HOURS", "11"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, stored_password: str | None, hashed_password: str | None) -> bool:
    if hashed_password and hashed_password.startswith("$2"):
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    return bool(stored_password) and password == stored_password


def crear_pulsera_vip(employee_code: str, role: str = "Worker") -> str:
    expires = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": employee_code, "role": role, "exp": expires},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def validar_pulsera_vip(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token VIP no proporcionado")
    try:
        payload = jwt.decode(
            authorization.removeprefix("Bearer ").strip(),
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        employee_code = payload.get("sub")
        if not employee_code:
            raise JWTError
        return employee_code
    except JWTError as error:
        raise HTTPException(status_code=401, detail="Token VIP inválido o expirado") from error


def require_admin(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Autenticación de administrador requerida")
    try:
        payload = jwt.decode(
            authorization.removeprefix("Bearer ").strip(),
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        if payload.get("role") != "Admin":
            raise HTTPException(status_code=403, detail="Se requiere rol de administrador")
        return payload["sub"]
    except JWTError as error:
        raise HTTPException(status_code=401, detail="Token de administrador inválido o expirado") from error
