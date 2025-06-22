from pathlib import Path

# 4 ta RTSP URL lar
CAMERA_URLS = [
    "rtsp://admin:a12345678A@93.188.83.34/Streaming/Channels/101/",
]

YOLO_MODEL_PATH = "helmet-detection.pt"

VIOLATION_DIR = Path("violations")
VIOLATION_DIR.mkdir(exist_ok=True)

EMPLOYEE_FACES_DIR = Path("employee_faces")
