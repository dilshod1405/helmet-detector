from pathlib import Path
from decouple import config


CAMERA_URLS = config("CAMERA_URLS", default="").split(",")


YOLO_MODEL_PATH = "yolov8n.pt"

VIOLATION_DIR = Path("violations")
VIOLATION_DIR.mkdir(exist_ok=True)

EMPLOYEE_FACES_DIR = Path("employee_faces")
