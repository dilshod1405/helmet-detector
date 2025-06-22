import datetime
import cv2
from app.config import RTSP_URL
from app.detection.helmet import detect_person_and_helmet

def is_work_time():
    now = datetime.datetime.now().time()
    start = datetime.time(8, 0, 0)   # 08:00:00
    end = datetime.time(18, 0, 0)    # 18:00:00
    return start <= now < end

def test_helmet_detection():
    cap = None

    while True:
        if is_work_time():
            if cap is None or not cap.isOpened():
                print("✅ Ish vaqti boshlandi, kamera stream ochilmoqda...")
                cap = cv2.VideoCapture(RTSP_URL)
                if not cap.isOpened():
                    print("❌ Kamera ochilmadi.")
                    cap = None
                    cv2.waitKey(10000)
                    continue

            ret, frame = cap.read()
            if not ret:
                print("❌ Frame o‘qib bo‘lmadi.")
                cap.release()
                cap = None
                cv2.waitKey(1000)
                continue

            helmet = detect_person_and_helmet(frame)
            label = "✅ Kaska bor" if helmet else "❌ Kaska yo'q"
            cv2.putText(frame, label, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0,255,0) if helmet else (0,0,255), 2)
            cv2.imshow("Helmet Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        else:
            if cap is not None:
                print("❌ Ish vaqti tugadi, kamera stream yopilmoqda...")
                cap.release()
                cap = None
                cv2.destroyAllWindows()

            # Ish vaqti bo‘lmagani uchun 60 sekund kutamiz va yana tekshiramiz
            cv2.waitKey(60000)

    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_helmet_detection()
