from pathlib import Path
import cv2
import datetime

VIOLATION_DIR = Path("violations")
VIOLATION_DIR.mkdir(exist_ok=True)

def save_violation_image(image, employee_name):
    if image is None or image.size == 0:
        print("❌ Rasm bo‘sh, saqlanmadi.")
        return None

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{employee_name}_{timestamp}.jpg"
    filepath = VIOLATION_DIR / filename

    success = cv2.imwrite(str(filepath), image)
    if not success:
        print(f"❌ Rasmni saqlashda xato: {filepath}")
        return None
    else:
        print(f"✅ Rasm saqlandi: {filepath}")
        return filepath
