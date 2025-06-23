# app/face_recognition_utils.py
import face_recognition
import os

employee_encodings = []
employee_names = []

def load_employee_faces(folder_path="employee_faces"):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(folder_path, filename)
            image = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(image)
            if len(encodings) > 0:
                employee_encodings.append(encodings[0])
                employee_names.append(os.path.splitext(filename)[0])
            else:
                print(f"Yuz topilmadi: {filename}")

def recognize_employee(face_image):
    unknown_encodings = face_recognition.face_encodings(face_image)
    if len(unknown_encodings) == 0:
        return None

    unknown_encoding = unknown_encodings[0]
    distances = face_recognition.face_distance(employee_encodings, unknown_encoding)
    best_match_index = distances.argmin()

    if distances[best_match_index] < 0.5:  # Threshold sozlanishi mumkin
        return employee_names[best_match_index]
    else:
        return None
