from sqlalchemy import Column, Integer, String
from app.db.base import Base

class User(Base):
    __tablename__ = "users" # Así se llamará la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String, unique=True, index=True) # Ej: OP-001
    full_name = Column(String)
    hashed_password = Column(String) # Aquí guardaremos la contraseña encriptada luego
    role = Column(String, default="Worker") # Puede ser Worker, Admin, HR