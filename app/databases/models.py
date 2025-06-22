from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String, nullable=False)
    image_path = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
