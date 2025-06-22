import cv2
from multiprocessing import Process
from app.config import CAMERA_URLS
from app.detection.helmet import detect_person_and_helmet
from app.camera.capture import save_violation_image
import time

def draw_boxes(frame, person_helmet_status):
    for pbox, helmet in person_helmet_status:
        x1, y1, x2, y2 = pbox.xyxy.cpu().numpy()[0].astype(int)
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

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"❌ Frame olishda xatolik: Camera {index + 1}")
            break

        results, person_helmet_status = detect_person_and_helmet(frame)

        current_time = time.time()

        for pbox, helmet in person_helmet_status:
            if not helmet:
                x1, y1, x2, y2 = pbox.xyxy.cpu().numpy()[0].astype(int)
                bbox_key = f"{x1}_{y1}_{x2}_{y2}"

                # Agar oxirgi saqlangan vaqtdan 10 sekund o‘tgan bo‘lsa yoki birinchi marta bo‘lsa
                if bbox_key not in violation_last_saved or (current_time - violation_last_saved[bbox_key]) > 10:
                    cropped = frame[y1:y2, x1:x2]
                    img_path = save_violation_image(cropped, f"Camera{index+1}_violation")
                    violation_last_saved[bbox_key] = current_time
                    print(f"🚨 Violation saved: {img_path}")

        if len(person_helmet_status) == 0:
            label = "Hech kim yo'q"
            cv2.putText(frame, label, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            draw_boxes(frame, person_helmet_status)

        cv2.imshow(f"Camera {index + 1}", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def run_all_cameras():
    for i, url in enumerate(CAMERA_URLS):
        p = Process(target=handle_camera, args=(url, i))
        p.start()


if __name__ == "__main__":
    run_all_cameras()
