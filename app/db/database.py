# Connection with database

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Get database url
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Make engine for database
# pool_pre_ping=True - check connection with database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
)

# Session for database to make queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Main class for database
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()