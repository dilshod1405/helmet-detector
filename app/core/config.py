# Main configurations here

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # API keys
    EXTERNAL_API_URL: str = os.getenv("EXTERNAL_API_URL") # API URL for external employee data
    
    # API Bearer Token (long time)
    EXTERNAL_API_TOKEN: str = os.getenv("EXTERNAL_API_TOKEN")

    # Path for Yolo model
    YOLO_MODEL_PATH: str = "models/yolov8n.pt"

    # Path for employee photos
    IMAGE_SAVE_PATH: str = "data"
    
    # TensorFlow ni CPU'da ishlashga majburlash (True/False)
    # Agar GPU bilan muammolar davom etsa, True qiling.
    FORCE_CPU_FOR_TF: bool = os.getenv("FORCE_CPU_FOR_TF", "False").lower() in ('true', '1', 't')

settings = Settings()
