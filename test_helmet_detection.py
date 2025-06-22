import cv2
from app.config import RTSP_URL
from app.detection.helmet import detect_person_and_helmet

def draw_boxes(frame, person_helmet_status):
    for pbox, helmet in person_helmet_status:
        x1, y1, x2, y2 = pbox.xyxy.cpu().numpy()[0].astype(int)
        color = (0, 255, 0) if helmet else (0, 0, 255)
        label = "Kaska bor" if helmet else "Kaska yo'q"
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

def test_helmet_detection():
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print("❌ Kamera ochilmadi.")
        return

    print("✅ Kamera stream boshlandi. Kaskani aniqlash test ishlamoqda...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Frame o‘qib bo‘lmadi.")
            break

        results, person_helmet_status = detect_person_and_helmet(frame)

        if len(person_helmet_status) == 0:
            label = "Hech kim yo'q"
            cv2.putText(frame, label, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            draw_boxes(frame, person_helmet_status)

        cv2.imshow("Helmet Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



if __name__ == "__main__":
    test_helmet_detection()