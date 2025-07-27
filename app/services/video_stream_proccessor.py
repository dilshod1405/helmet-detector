# Update information of employee by API
import cv2
import threading
import time
from queue import Queue
from app.services.helmet_detection_service import HelmetDetectionService
from app.db.database import SessionLocal # DB sessiyasini olish uchun
from app.db.models import Incident, Employee # Incident modelini saqlash uchun

class VideoStreamProcessor:
    def __init__(self, rtsp_url: str, camera_id: str, detection_service: HelmetDetectionService):
        self.rtsp_url = rtsp_url
        self.camera_id = camera_id
        self.detection_service = detection_service
        self.cap = None # VideoCapture obyekti
        self.running = False # Streamni boshqarish uchun flag
        self.thread = None # Streamni alohida threadda ishlatish uchun
        self.frame_queue = Queue(maxsize=10) # Kadrlarni buferlash uchun navbat
        print(f"VideoStreamProcessor yaratildi: Kamera ID - {self.camera_id}, URL - {self.rtsp_url}")

    def _read_frames(self):
        """
        RTSP streamdan kadrlarni o'qish va navbatga qo'yish.
        """
        print(f"Kamera {self.camera_id} uchun stream o'qish boshlandi.")
        while self.running:
            if not self.cap or not self.cap.isOpened():
                print(f"Kamera {self.camera_id} ga ulanishga urinish...")
                self.cap = cv2.VideoCapture(self.rtsp_url)
                if not self.cap.isOpened():
                    print(f"Xato: Kamera {self.camera_id} ga ulanib bo'lmadi. 5 soniyadan keyin qayta urinish.")
                    time.sleep(5)
                    continue
                else:
                    print(f"Kamera {self.camera_id} ga muvaffaqiyatli ulanildi.")

            ret, frame = self.cap.read()
            if not ret:
                print(f"Kamera {self.camera_id} dan kadr o'qishda xato. Ulanishni qayta tiklashga urinish.")
                self.cap.release() # Ulanishni yopish
                time.sleep(1) # Biroz kutish
                continue

            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            else:
                # Navbat to'la bo'lsa, eng eski kadrni tashlab yuborish
                self.frame_queue.get_nowait()
                self.frame_queue.put(frame)
            time.sleep(0.03) # Taxminan 30 FPS uchun (1/30 = 0.033)

        if self.cap:
            self.cap.release()
        print(f"Kamera {self.camera_id} uchun stream o'qish to'xtatildi.")

    def _process_frames(self):
        """
        Navbatdan kadrlarni olib, deteksiya xizmatiga yuborish.
        """
        print(f"Kamera {self.camera_id} uchun kadr qayta ishlash boshlandi.")
        while self.running:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                
                # Deteksiya xizmatini chaqirish
                incidents = self.detection_service.detect_and_recognize(frame)
                
                # Agar hodisalar aniqlansa, bazaga saqlash
                if incidents:
                    db = SessionLocal() # Har bir hodisa uchun yangi sessiya ochish
                    try:
                        for incident_data in incidents:
                            # Agar xodim topilmasa (Noma'lum xodim), employee_id None bo'ladi
                            employee_obj = None
                            if incident_data["employee_id"]:
                                employee_obj = db.query(Employee).filter(Employee.id == incident_data["employee_id"]).first()

                            new_incident = Incident(
                                employee_id=incident_data["employee_id"],
                                incident_photo_path=incident_data["incident_photo_path"],
                                timestamp=incident_data["timestamp"]
                            )
                            db.add(new_incident)
                            print(f"Kamera {self.camera_id}: Hodisa bazaga saqlandi. Xodim: {incident_data['full_name']}")
                        db.commit()
                    except Exception as e:
                        db.rollback()
                        print(f"Kamera {self.camera_id}: Hodisani bazaga saqlashda xato: {e}")
                    finally:
                        db.close()
            else:
                time.sleep(0.01) # Navbat bo'sh bo'lsa biroz kutish
        print(f"Kamera {self.camera_id} uchun kadr qayta ishlash to'xtatildi.")


    def start(self):
        """
        Streamni boshlash.
        """
        if not self.running:
            self.running = True
            # Kadrlarni o'qish va qayta ishlash uchun ikkita alohida thread
            self.read_thread = threading.Thread(target=self._read_frames)
            self.process_thread = threading.Thread(target=self._process_frames)
            
            self.read_thread.start()
            self.process_thread.start()
            print(f"Kamera {self.camera_id} uchun stream ishga tushirildi.")

    def stop(self):
        """
        Streamni to'xtatish.
        """
        if self.running:
            self.running = False
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join() # Thread tugashini kutish
            if self.process_thread and self.process_thread.is_alive():
                self.process_thread.join() # Thread tugashini kutish
            print(f"Kamera {self.camera_id} uchun stream to'xtatildi.")