import cv2
from app.config import RTSP_URL

def test_rtsp_connection():
    cap = cv2.VideoCapture(RTSP_URL)

    if not cap.isOpened():
        print("❌ Kamera ochilmadi.")
        return

    print("✅ Kamera ulanish muvaffaqiyatli. Stream ko‘rsatilmoqda...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Frame o‘qib bo‘lmadi.")
            break

        cv2.imshow("RTSP Stream", frame)

        # Chiqish uchun "q" tugmasi
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_rtsp_connection()
