from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

CAMERA_URLS = [
    os.getenv("CAMERA_1_URL"),
]

YOLO_MODEL_PATH = "yolov8n.pt"

VIOLATION_DIR = Path("violations")
VIOLATION_DIR.mkdir(exist_ok=True)

EMPLOYEE_FACES_DIR = Path("employee_faces")
