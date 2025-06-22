import uuid
from datetime import datetime
from app.config import VIOLATION_DIR
import cv2

def save_violation_image(image, employee_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{employee_name}_{timestamp}_{uuid.uuid4().hex[:6]}.jpg"
    path = VIOLATION_DIR / filename
    cv2.imwrite(str(path), image)
    return str(path)
