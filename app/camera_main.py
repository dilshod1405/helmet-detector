from app.config import CAMERA_URLS
from app.detection.helmet import detect_person_and_helmet
from app.detection.face import recognize_faces
from app.databases import crud, db
from app.camera.capture import save_violation_image
import cv2
import threading

def handle_camera(rtsp_url):
    db_session = next(db.get_db())
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print(f"❌ Kamera ochilmadi: {rtsp_url}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if not detect_person_and_helmet(frame):
            faces = recognize_faces(frame)
            for (top, right, bottom, left), name in faces:
                if name != "Unknown":
                    cropped = frame[top:bottom, left:right]
                    img_path = save_violation_image(cropped, name)
                    crud.create_violation(db_session, employee_name=name, image_path=img_path)
                    print(f"🚨 Violation: {name} - {img_path}")

    cap.release()

def run_all():
    threads = []
    for url in CAMERA_URLS:
        t = threading.Thread(target=handle_camera, args=(url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    run_all()
