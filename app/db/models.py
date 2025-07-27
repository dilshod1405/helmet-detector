# Tables of models

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from pgvector.sqlalchemy import Vector
from app.db.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    full_name = Column(String, index=True)
    photo_url = Column(String)
    external_id = Column(Integer, index=True)
    # Yuz embeddingi: 512 o'lchamli vektor (FaceNet/ArcFace odatda 512 o'lchamli embedding beradi)
    face_embedding = Column(Vector(512), nullable=True)

    incidents = relationship("Incident", back_populates="employee") # Bu xodim bilan bog'liq hodisalar

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True) # Hodisa ID'si
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id")) # Qoidabuzar xodim ID'si
    incident_photo_path = Column(String) # Hodisa rasmining fayl yo'li
    timestamp = Column(DateTime(timezone=True), server_default=func.now()) # Hodisa vaqti

    # Aloqalar
    employee = relationship("Employee", back_populates="incidents") # Bu hodisa bilan bog'liq xodim
