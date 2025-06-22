import cv2
import threading
from app.detection.helmet import detect_person_and_helmet as has_helmet

CAMERA_URLS = [
    "rtsp://admin:a12345678A@93.188.83.34/Streaming/Channels/101/"
]

def stream_camera(url, window_name):
    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        print(f"❌ Kamera ochilmadi: {window_name}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"❌ Frame o‘qib bo‘lmadi: {window_name}")
            break

        helmet = has_helmet(frame)
        label = "Kaska bor" if helmet else "Kaska yo'q"
        color = (0, 255, 0) if helmet else (0, 0, 255)

        cv2.putText(frame, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyWindow(window_name)

def run_all_cameras():
    threads = []
    for i, url in enumerate(CAMERA_URLS):
        window_name = f"Camera {i+1}"
        t = threading.Thread(target=stream_camera, args=(url, window_name))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    run_all_cameras()
