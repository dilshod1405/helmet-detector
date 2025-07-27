import cv2
import numpy as np
from ultralytics import YOLO
from deepface import DeepFace
from sqlalchemy.orm import Session
from app.db.models import Employee, Incident
from app.core.config import settings
import os
import uuid
from datetime import datetime, timedelta

# YOLO modelini yuklash
try:
    yolo_model = YOLO(settings.YOLO_MODEL_PATH)
    print(f"YOLO modeli '{settings.YOLO_MODEL_PATH}' muvaffaqiyatli yuklandi.")
except Exception as e:
    print(f"YOLO modelini yuklashda xato: {e}")
    yolo_model = None

# Saqlanadigan rasmlar uchun papka
INCIDENT_PHOTO_DIR = settings.IMAGE_SAVE_PATH
os.makedirs(INCIDENT_PHOTO_DIR, exist_ok=True)

class HelmetDetectionService:
    def __init__(self, db: Session):
        self.db = db
        self.known_face_encodings = []
        self.known_employee_ids = []
        self.known_employee_full_names = []
        self._load_employee_faces()
        self.last_incident_save_time = {}
        self.INCIDENT_COOLDOWN_SECONDS = 30
        self.face_model_name = "Facenet"
        self.face_detector_backend = "opencv"
        self.RECOGNITION_THRESHOLD = 0.5 # Kosiniy o'xshashlik uchun chegara (0.0 dan 1.0 gacha, yuqori qiymat o'xshashlikni bildiradi)

    def _load_employee_faces(self):
        """
        Ma'lumotlar bazasidan barcha xodimlarning yuz embeddinglarini yuklaydi.
        """
        print("Xodimlar yuz embeddinglarini yuklash boshlandi...")
        employees = self.db.query(Employee).filter(Employee.face_embedding.isnot(None)).all()
        
        self.known_face_encodings = []
        self.known_employee_ids = []
        self.known_employee_full_names = []

        for emp in employees:
            if emp.face_embedding:
                self.known_face_encodings.append(np.array(emp.face_embedding))
                self.known_employee_ids.append(emp.id)
                self.known_employee_full_names.append(emp.full_name)
        
        if len(self.known_face_encodings) == 0:
            print("DIQQAT: Ma'lumotlar bazasida yuz embeddinglari topilmadi. Xodimlar tanilmaydi.")
            print("Iltimos, '/employees/update-from-api' endpointini ishga tushirib, xodimlar ma'lumotlarini yuklang.")
        else:
            print(f"{len(self.known_face_encodings)} ta xodim yuzi yuklandi.")

    def update_known_faces(self):
        """
        Xodimlar ma'lumotlari yangilanganda bu funksiyani chaqirib,
        yuz embeddinglarini qayta yuklash mumkin.
        """
        self._load_employee_faces()

    def detect_and_recognize(self, frame: np.ndarray):
        """
        Berilgan video kadrda kaskasiz odamlarni aniqlaydi va ularni identifikatsiya qiladi.
        """
        if yolo_model is None:
            print("YOLO modeli yuklanmagan. Deteksiya bajarilmadi.")
            return []

        results = yolo_model(frame, verbose=False)

        detected_incidents = []
        current_time = datetime.now()

        for r in results:
            person_boxes = []
            helmet_boxes = []

            for *xyxy, conf, cls in r.boxes.data:
                class_name = yolo_model.names[int(cls)]
                if class_name == 'person' and conf > 0.5:
                    person_boxes.append(xyxy)
                elif class_name == 'helmet' and conf > 0.5:
                    helmet_boxes.append(xyxy)

            for p_box in person_boxes:
                has_helmet = False
                for h_box in helmet_boxes:
                    h_center_x = (h_box[0] + h_box[2]) / 2
                    h_center_y = (h_box[1] + h_box[3]) / 2
                    p_top_half_y_limit = p_box[1] + (p_box[3] - p_box[1]) / 2

                    if (h_box[0] < p_box[2] and h_box[2] > p_box[0] and
                        h_box[1] < p_box[3] and h_box[3] > p_box[1] and
                        h_center_y < p_top_half_y_limit):
                        has_helmet = True
                        break
                
                if not has_helmet:
                    x1, y1, x2, y2 = map(int, p_box)
                    
                    try:
                        face_embeddings_in_frame = DeepFace.represent(
                            img_path=frame,
                            model_name=self.face_model_name,
                            detector_backend=self.face_detector_backend,
                            enforce_detection=False
                        )
                    except Exception as e:
                        print(f"Kadrda yuz embeddingini yaratishda xato: {e}")
                        face_embeddings_in_frame = []

                    if face_embeddings_in_frame:
                        for face_info in face_embeddings_in_frame:
                            current_face_embedding = np.array(face_info["embedding"])
                            face_x, face_y, face_w, face_h = face_info["facial_area"]["x"], face_info["facial_area"]["y"], face_info["facial_area"]["w"], face_info["facial_area"]["h"]
                            face_box_on_frame = [face_x, face_y, face_x + face_w, face_y + face_h]

                            name = "Noma'lum xodim"
                            employee_id = None
                            incident_key = "unknown_face_" + str(uuid.uuid4()) # Noma'lum yuzlar uchun unikal kalit

                            # Yuz embeddingini mavjud embeddinglar bilan solishtirish
                            if len(self.known_face_encodings) > 0:
                                similarities = np.dot(self.known_face_encodings, current_face_embedding) / \
                                               (np.linalg.norm(self.known_face_encodings, axis=1) * np.linalg.norm(current_face_embedding))
                                
                                best_match_index = np.argmax(similarities)
                                best_similarity = similarities[best_match_index]

                                if best_similarity > self.RECOGNITION_THRESHOLD:
                                    name = self.known_employee_full_names[best_match_index]
                                    employee_id = self.known_employee_ids[best_match_index]
                                    incident_key = str(employee_id)
                                    print(f"Kaskasiz xodim aniqlandi: {name} (O'xshashlik: {best_similarity:.2f})")
                                else:
                                    print(f"Kaskasiz noma'lum xodim aniqlandi. Eng yaxshi o'xshashlik: {best_similarity:.2f} (chegaradan past)")
                                    # Agar tanilmasa, hodisani saqlamaymiz
                                    continue # Keyingi yuzga o'tish yoki loopni tugatish
                            else:
                                print("Bazadagi yuz embeddinglari yuklanmagan. Noma'lum xodim sifatida qayd etildi.")
                                # Agar embeddinglar yuklanmagan bo'lsa, tanish imkonsiz, saqlamaymiz
                                continue # Keyingi yuzga o'tish yoki loopni tugatish

                            # --- Hodisa saqlashni cheklash logikasi ---
                            if incident_key in self.last_incident_save_time:
                                time_since_last_save = (current_time - self.last_incident_save_time[incident_key]).total_seconds()
                                if time_since_last_save < self.INCIDENT_COOLDOWN_SECONDS:
                                    continue
                            
                            self.last_incident_save_time[incident_key] = current_time

                            # Agar bu nuqtaga kelsak, demak xodim tanildi va cooldown tugagan
                            incident_photo_filename = f"incident_{uuid.uuid4()}.jpg"
                            incident_photo_path = os.path.join(INCIDENT_PHOTO_DIR, incident_photo_filename)
                            cv2.imwrite(incident_photo_path, frame)
                            
                            detected_incidents.append({
                                "employee_id": employee_id,
                                "full_name": name,
                                "incident_photo_path": incident_photo_path,
                                "timestamp": datetime.now(),
                                "person_box": [x1, y1, x2, y2],
                                "face_box": face_box_on_frame
                            })
                    else:
                        print("Kaskasiz odam topildi, lekin yuz aniqlanmadi. Hodisa saqlanmadi.")
        return detected_incidents

# `main.py` da ishga tushirish uchun
def get_detection_service(db: Session = None):
    """
    Dependency Injection uchun deteksiya xizmatini qaytaradi.
    """
    if db:
        return HelmetDetectionService(db)
    else:
        class DummyDetectionService:
            def __init__(self):
                self.yolo_model = yolo_model
            def detect_and_recognize(self, frame):
                print("Ma'lumotlar bazasi sessiyasi mavjud emas, deteksiya bajarilmadi.")
                return []
            def update_known_faces(self):
                print("Ma'lumotlar bazasi sessiyasi mavjud emas, yuzlar yangilanmadi.")
        return DummyDetectionService()
