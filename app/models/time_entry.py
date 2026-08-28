from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
import enum
from app.db.base import Base

class EntryType(enum.Enum):
    CLOCK_IN = "CLOCK_IN"
    CLOCK_OUT = "CLOCK_OUT"
    TASK = "TASK"

class LocationType(enum.Enum):
    NAVE = "NAVE"
    OBRA = "OBRA"
    OFICINA = "OFICINA"

class TimeEntry(Base):
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False) # Simplificado por ahora
    entry_type = Column(Enum(EntryType), nullable=False)
    location = Column(Enum(LocationType), nullable=True)
    
    project_id = Column(Integer, nullable=True)
    task_type_id = Column(Integer, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)