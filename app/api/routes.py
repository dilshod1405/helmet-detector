from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.databases import models, schemas, crud
from app.databases.db import get_db

router = APIRouter(
    prefix="/api",
    tags=["Violations"]
)

@router.get("/violations", response_model=list[schemas.ViolationOut])
def get_violations(db: Session = Depends(get_db)):
    return crud.get_all_violations(db)
