import cv2
from ultralytics import YOLO
import os
import json # JSON fayllar bilan ishlash uchun

# JSON konfiguratsiya fayli nomi
CAMERAS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'cameras.json')
YOLO_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'yolov8n.pt')

# JSON faylidan kameralarni o'qish
def load_cameras_from_json():
    if not os.path.exists(CAMERAS_CONFIG_FILE):
        print(f"Xato: Kameralar konfiguratsiya fayli '{CAMERAS_CONFIG_FILE}' topilmadi.")
        return []
    try:
        with open(CAMERAS_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Xato: '{CAMERAS_CONFIG_FILE}' faylini o'qishda xato yuz berdi (JSON formatida emas): {e}")
        return []

if not os.path.exists(YOLO_MODEL_PATH):
    print(f"Xato: YOLO modeli '{YOLO_MODEL_PATH}' topilmadi. Iltimos, model faylini to'g'ri joylashtiring.")
    exit()

# YOLO modelini yuklash
try:
    model = YOLO(YOLO_MODEL_PATH)
    print(f"YOLO modeli '{YOLO_MODEL_PATH}' muvaffaqiyatli yuklandi.")
except Exception as e:
    print(f"YOLO modelini yuklashda xato: {e}")
    print("Iltimos, ultralytics kutubxonasi to'g'ri o'rnatilganligini va model fayli buzilmaganligini tekshiring.")
    exit()

# Kameralarni JSON faylidan yuklash
cameras = load_cameras_from_json()
active_cameras = [cam for cam in cameras if cam.get('is_active', False)]

if not active_cameras:
    print("JSON faylida faol (is_active: true) kameralar topilmadi. Hech qanday test bajarilmaydi.")
    exit()

print(f"JSON faylidan {len(active_cameras)} ta faol kamera yuklandi. Test boshlanmoqda.")

for cam_data in active_cameras:
    camera_id = cam_data.get("camera_id", "unknown_camera")
    rtsp_url = cam_data.get("rtsp_url")

    if not rtsp_url:
        print(f"Kamera '{camera_id}' uchun RTSP URL topilmadi. O'tkazib yuborilmoqda.")
        continue

    print(f"\n--- Kamera '{camera_id}' ({rtsp_url}) testi boshlanmoqda ---")
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print(f"Xato: Kamera '{camera_id}' ga ulanib bo'lmadi: {rtsp_url}")
        print("RTSP URL to'g'ri ekanligini va kameraga kirish mumkinligini tekshiring.")
        continue # Keyingi kameraga o'tish

    print(f"Kamera '{camera_id}' ga muvaffaqiyatli ulanildi.")
    print(f"Kadrlarni qayta ishlash boshlandi. '{camera_id}' oynasini yopish yoki 'q' tugmasini bosish orqali keyingi kameraga o'ting.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Kamera '{camera_id}' dan kadr o'qishda xato. Stream tugagan bo'lishi mumkin yoki ulanish uzilgan.")
            break

        # YOLOv8 orqali deteksiya
        results = model(frame, verbose=False)

        # Natijalarni kadrga chizish
        for r in results:
            for *xyxy, conf, cls in r.boxes.data:
                x1, y1, x2, y2 = map(int, xyxy)
                class_name = model.names[int(cls)]
                confidence = float(conf)

                # Odam va kaska sinflariga e'tibor berish
                if class_name == 'person':
                    color = (0, 255, 0) # Yashil rang
                    label = f"Odam: {confidence:.2f}"
                elif class_name == 'helmet':
                    color = (255, 0, 0) # Ko'k rang
                    label = f"Kaska: {confidence:.2f}"
                else:
                    continue # Boshqa sinflarni e'tiborsiz qoldirish

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Kadrlarni ko'rsatish
        cv2.imshow(f'Kamera Deteksiyasi (Test) - {camera_id}', frame)

        # 'q' tugmasini bosish orqali chiqish
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Resurslarni bo'shatish
    cap.release()
    cv2.destroyAllWindows()
    print(f"--- Kamera '{camera_id}' testi yakunlandi ---")

print("\nBarcha faol kameralar testi yakunlandi.")