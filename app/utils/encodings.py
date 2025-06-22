import face_recognition
import pickle
import os
from pathlib import Path
from app.config import EMPLOYEE_FACES_DIR

ENCODINGS_PATH = "encodings.pkl"

def generate_encodings():
    encodings = []
    names = []

    if not EMPLOYEE_FACES_DIR.exists() or not EMPLOYEE_FACES_DIR.is_dir():
        print(f"❗ Papka topilmadi yoki noto‘g‘ri: {EMPLOYEE_FACES_DIR}")
        return

    for image_path in EMPLOYEE_FACES_DIR.glob("*.jpg"):
        try:
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                for encoding in face_encodings:
                    encodings.append(encoding)
                    names.append(image_path.stem)
            else:
                print(f"❗ Yuz topilmadi: {image_path.name}")
        except Exception as e:
            print(f"❗ Xatolik yuz berdi {image_path.name} faylini o‘qishda: {e}")

    if encodings:
        try:
            with open(ENCODINGS_PATH, "wb") as f:
                pickle.dump({"encodings": encodings, "names": names}, f)
            print(f"✅ Yuz encodinglari saqlandi: {ENCODINGS_PATH}")
        except Exception as e:
            print(f"❗ Encodinglarni saqlashda xatolik: {e}")
    else:
        print("❗ Hech qanday yuz encodinglari yaratilmadi.")

def load_encodings():
    if not os.path.exists(ENCODINGS_PATH):
        print(f"❗ Encoding fayli topilmadi: {ENCODINGS_PATH}")
        return [], []
    try:
        with open(ENCODINGS_PATH, "rb") as f:
            data = pickle.load(f)
        return data.get("encodings", []), data.get("names", [])
    except Exception as e:
        print(f"❗ Encoding faylini o‘qishda xatolik: {e}")
        return [], []