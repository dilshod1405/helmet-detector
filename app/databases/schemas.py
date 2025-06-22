from pydantic import BaseModel
from datetime import datetime

class ViolationOut(BaseModel):
    id: int
    employee_name: str
    image_path: str
    timestamp: datetime

    class Config:
        orm_mode = True
