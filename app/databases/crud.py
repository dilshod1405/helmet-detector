from .models import Violation
from sqlalchemy.orm import Session

def create_violation(db: Session, employee_name: str, image_path: str):
    violation = Violation(
        employee_name=employee_name,
        image_path=image_path
    )
    db.add(violation)
    db.commit()
    db.refresh(violation)
    return violation


def get_all_violations(db):
    return db.query(Violation).all()