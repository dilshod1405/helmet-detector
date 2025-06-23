import cv2
import numpy as np
from ultralytics import YOLO
from app.config import YOLO_MODEL_PATH

model = YOLO(YOLO_MODEL_PATH)
names = model.names

def is_red_helmet(region):
    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_ratio = (mask1.sum() + mask2.sum()) / (region.size * 255)
    return red_ratio > 0.05

def detect_person_and_helmet(frame):
    results = model.predict(frame, verbose=False)[0]

    person_boxes = []
    helmet_boxes = []

    for box in results.boxes:
        cls_id = int(box.cls.cpu().item())
        label = names[cls_id].lower()
        if label in ['person', 'worker', 'construction_worker']:
            person_boxes.append(box)
        elif label in ['helmet', 'hardhat', 'safety_helmet', 'red_helmet']:
            helmet_boxes.append(box)

    if not person_boxes:
        return results, []

    person_helmet_status = []
    for pbox in person_boxes:
        coords = pbox.xyxy.cpu().numpy()
        if coords.shape[0] == 1:
            coords = coords[0]
        px1, py1, px2, py2 = coords.astype(int)

        helmet_found = False
        for hbox in helmet_boxes:
            hcoords = hbox.xyxy.cpu().numpy()
            if hcoords.shape[0] == 1:
                hcoords = hcoords[0]
            hx1, hy1, hx2, hy2 = hcoords.astype(int)

            hx_center = (hx1 + hx2) / 2
            hy_center = (hy1 + hy2) / 2
            if (px1 <= hx_center <= px2) and (py1 <= hy_center <= py2):
                helmet_found = True
                break

        if not helmet_found:
            h = py2 - py1
            head_y1 = max(py1, 0)
            head_y2 = min(py1 + h // 3, frame.shape[0])
            head_x1 = max(px1, 0)
            head_x2 = min(px2, frame.shape[1])
            head_region = frame[head_y1:head_y2, head_x1:head_x2]

            if head_region.size > 0 and is_red_helmet(head_region):
                helmet_found = True

        person_helmet_status.append((pbox, helmet_found))

    return results, person_helmet_status
