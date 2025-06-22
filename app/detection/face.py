import face_recognition
import os
import cv2
from app.config import EMPLOYEE_FACES_DIR

known_faces = []
known_names = []

# Rasmlarni yuklash
for filename in os.listdir(EMPLOYEE_FACES_DIR):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        path = EMPLOYEE_FACES_DIR / filename
        image = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_faces.append(encoding[0])
            known_names.append(filename.rsplit(".", 1)[0])  # ismi.png

def recognize_faces(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, locations)
    results = []

    for (top, right, bottom, left), face_encoding in zip(locations, encodings):
        matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.5)
        name = "Unknown"

        if True in matches:
            idx = matches.index(True)
            name = known_names[idx]

        results.append(((top, right, bottom, left), name))

    return results
