import cv2
from ultralytics import YOLO
from app.config import YOLO_MODEL_PATH

model = YOLO(YOLO_MODEL_PATH)
names = model.names  # better than results.names

def detect_person_and_helmet(frame):
    """
    Frame ichidagi odamlarni va kaskalarni aniqlaydi.
    Har bir odam uchun kaska borligini qaytaradi.
    
    Returns:
        results: YOLO inferensiya natijasi (for visualization)
        person_helmet_status: list of tuples [(box, helmet_bool), ...]
    """
    results = model.predict(frame, verbose=False)[0]

    person_boxes = []
    helmet_boxes = []

    for box in results.boxes:
        cls_id = int(box.cls.cpu().item())
        label = names[cls_id].lower()
        if label == 'person':
            person_boxes.append(box)
        elif label == 'helmet':
            helmet_boxes.append(box)

    person_helmet_status = []
    for pbox in person_boxes:
        px1, py1, px2, py2 = pbox.xyxy.cpu().numpy()[0]

        helmet_found = False
        for hbox in helmet_boxes:
            hx1, hy1, hx2, hy2 = hbox.xyxy.cpu().numpy()[0]

            # helmet markazining person bbox ichida ekanini tekshiramiz
            hx_center = (hx1 + hx2) / 2
            hy_center = (hy1 + hy2) / 2

            if (px1 <= hx_center <= px2) and (py1 <= hy_center <= py2):
                helmet_found = True
                break

        person_helmet_status.append((pbox, helmet_found))

    return results, person_helmet_status
