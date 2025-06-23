import cv2
import time
from collections import defaultdict, deque
from multiprocessing import Process
import os
import face_recognition

from app.config import CAMERA_URLS
from app.detection.helmet import detect_person_and_helmet
from app.camera.capture import save_violation_image

# -------------- YUZ TANISH FUNKSIYALARI -------------------

employee_encodings = []
employee_names = []

def load_employee_faces(folder_path="employee_faces"):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(folder_path, filename)
            image = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(image)
            if len(encodings) > 0:
                employee_encodings.append(encodings[0])
                employee_names.append(os.path.splitext(filename)[0])
            else:
                print(f"Yuz topilmadi: {filename}")

def recognize_employee(face_image):
    unknown_encodings = face_recognition.face_encodings(face_image)
    if len(unknown_encodings) == 0:
        return None
    unknown_encoding = unknown_encodings[0]
    distances = face_recognition.face_distance(employee_encodings, unknown_encoding)
    best_match_index = distances.argmin()
    if distances[best_match_index] < 0.5:  # threshold, kerak bo'lsa sozlash mumkin
        return employee_names[best_match_index]
    else:
        return None

# ------------------- KASKA ANIQLASH VA SAQLASH -------------------

def draw_boxes(frame, person_helmet_status):
    for pbox, helmet in person_helmet_status:
        coords = pbox.xyxy.cpu().numpy()
        if coords.shape[0] == 1:
            coords = coords[0]
        x1, y1, x2, y2 = coords.astype(int)

        color = (0, 255, 0) if helmet else (0, 0, 255)
        label = "Kaska bor" if helmet else "Kaska yo'q"
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

def handle_camera(url, index):
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print(f"❌ Kamera ochilmadi: Camera {index + 1}")
        return

    print(f"✅ Kamera ishga tushdi: Camera {index + 1}")
    violation_last_saved = {}
    unknown_faces_logged = set()  # <<=== Yangi
    helmet_buffer = defaultdict(lambda: deque(maxlen=10))
    violation_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"❌ Frame olishda xatolik: Camera {index + 1}")
            break

        results, person_helmet_status = detect_person_and_helmet(frame)
        current_time = time.time()

        for pbox, helmet in person_helmet_status:
            coords = pbox.xyxy.cpu().numpy()
            if coords.shape[0] == 1:
                coords = coords[0]
            x1, y1, x2, y2 = coords.astype(int)

            bbox_key = f"{x1}_{y1}_{x2}_{y2}"
            helmet_buffer[bbox_key].append(helmet)

            if helmet_buffer[bbox_key].count(False) >= 8 and violation_count < 10:
                if bbox_key not in violation_last_saved or (current_time - violation_last_saved[bbox_key]) > 10:
                    cropped = frame[y1:y2, x1:x2]
                    face_image = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)

                    employee_name = recognize_employee(face_image)
                    if employee_name is not None:
                        img_path = save_violation_image(cropped, f"Camera{index+1}_violation_{employee_name}")
                        violation_last_saved[bbox_key] = current_time
                        violation_count += 1
                        print(f"🚨 {employee_name} kaskasiz! Rasm saqlandi: {img_path}")
                    else:
                        # Faqat bir marta saqlansin (agar bu bbox_key ilgari log qilinmagan bo‘lsa)
                        if bbox_key not in unknown_faces_logged:
                            img_path = save_violation_image(cropped, f"Camera{index+1}_violation_unknown")
                            unknown_faces_logged.add(bbox_key)
                            violation_count += 1
                            print(f"⚠️ Noma'lum shaxs (kaskasiz) — bir martalik rasm saqlandi: {img_path}")
                        else:
                            print("❗ Noma'lum shaxs allaqachon saqlangan. Yana rasm olinmadi.")

        if len(person_helmet_status) == 0:
            cv2.putText(frame, "Hech kim yo'q", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            draw_boxes(frame, person_helmet_status)

        cv2.imshow(f"Camera {index + 1}", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def run_all_cameras():
    print("Xodim yuzlari yuklanmoqda...")
    load_employee_faces()  # Employee yuzlarini dastlab yuklaymiz
    print(f"Yuzlar yuklandi: {len(employee_names)} ta xodim")
    for i, url in enumerate(CAMERA_URLS):
        p = Process(target=handle_camera, args=(url, i))
        p.start()

if __name__ == "__main__":
    run_all_cameras()
