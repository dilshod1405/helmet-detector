import cv2
from app.config import CAMERA_URLS
from app.detection.helmet import detect_person_and_helmet

def draw_boxes(frame, person_helmet_status):
    for pbox, helmet in person_helmet_status:
        x1, y1, x2, y2 = pbox.xyxy.cpu().numpy()[0].astype(int)
        color = (0, 255, 0) if helmet else (0, 0, 255)
        label = "Kaska bor" if helmet else "Kaska yo'q"
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)


def test_helmet_detection():
    caps = []
    for i, url in enumerate(CAMERA_URLS):
        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            print(f"❌ Kamera ochilmadi: {url}")
        else:
            print(f"✅ Kamera {i+1} stream boshlandi.")
            caps.append((f"Camera {i+1}", cap))

    if not caps:
        print("⚠️ Hech bir kamera ulanmagan.")
        return

    while True:
        for name, cap in caps:
            ret, frame = cap.read()
            if not ret:
                print(f"❌ Frame o‘qib bo‘lmadi: {name}")
                continue

            results, person_helmet_status = detect_person_and_helmet(frame)

            if not person_helmet_status:
                cv2.putText(frame, "Hech kim yo'q", (30, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            else:
                draw_boxes(frame, person_helmet_status)

            cv2.imshow(name, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    for _, cap in caps:
        cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    test_helmet_detection()