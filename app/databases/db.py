from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.databases.models import Base
from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DB ulanish dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dastlabki db yaratish uchun:
def init_db():
    Base.metadata.create_all(bind=engine)
