from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    client_code = Column(String(4), unique=True, index=True) # <-- Esta línea es clave
    name = Column(String, index=True)
    
    projects = relationship("Project", back_populates="client")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    
    client = relationship("Client", back_populates="projects")