from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import Base, engine, get_db
from app.services.employee_data_updater import update_employee_data
from app.services.helmet_detection_service import HelmetDetectionService
from app.services.video_stream_proccessor import VideoStreamProcessor
from pydantic import BaseModel
import os
import asyncio
import json

# FastAPI ilovasini yaratish
app = FastAPI(
    title="Kaska Detektori Tizimi",
    description="Temir yo'l korxonalari uchun kaskasiz xodimlarni aniqlash va identifikatsiya qilish tizimi.",
    version="0.1.0",
)

# Global o'zgaruvchilar
detection_service: HelmetDetectionService = None
active_stream_processors: dict[str, VideoStreamProcessor] = {} # Kamera ID'si bo'yicha aktiv streamlar
CAMERAS_CONFIG_FILE = "cameras.json" # JSON konfiguratsiya fayli nomi

# Kamera qo'shish uchun ma'lumot modeli
class CameraAddRequest(BaseModel):
    camera_id: str
    rtsp_url: str
    is_active: bool = True # Kameraning faol holati

# JSON faylidan kameralarni o'qish
def load_cameras_from_json():
    if not os.path.exists(CAMERAS_CONFIG_FILE):
        return []
    with open(CAMERAS_CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# JSON fayliga kameralarni yozish
def save_cameras_to_json(cameras_data: list):
    with open(CAMERAS_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cameras_data, f, indent=2, ensure_ascii=False)

# Root endpoint - tizimning ishlashini tekshirish uchun
@app.get("/")
async def read_root():
    return {"message": "Kaska Detektori Tizimi ishlamoqda!"}

# Tizim sozlamalarini tekshirish uchun endpoint (ixtiyoriy)
@app.get("/settings")
async def get_settings():
    return {
        "database_url": settings.DATABASE_URL,
        "external_api_url": settings.EXTERNAL_API_URL,
        "yolo_model_path": settings.YOLO_MODEL_PATH,
        "image_save_path": settings.IMAGE_SAVE_PATH
    }

# Xodimlar ma'lumotlarini API'dan yangilash uchun endpoint
@app.post("/employees/update-from-api", summary="Xodimlar ma'lumotlarini tashqi API'dan yangilash")
async def update_employees(db: Session = Depends(get_db)):
    """
    Tashqi API'dan xodimlar ro'yxatini oladi, rasmlarni yuklaydi,
    yuz embeddinglarini yaratadi va ma'lumotlar bazasini yangilaydi.
    """
    success = await update_employee_data(db)
    if success:
        if detection_service:
            detection_service.update_known_faces()
        return {"message": "Xodimlar ma'lumotlari muvaffaqiyatli yangilandi."}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Xodimlar ma'lumotlarini yangilashda xato yuz berdi."
    )

@app.post("/cameras/add", summary="Yangi kamerani qo'shish/yangilash")
async def add_camera_config(request: CameraAddRequest):
    """
    Yangi kamerani JSON fayliga qo'shadi yoki mavjudini yangilaydi.
    Bu endpoint streamni avtomatik boshlamaydi, faqat konfiguratsiyani saqlaydi.
    """
    cameras_data = load_cameras_from_json()
    camera_exists = False
    message = ""

    for i, cam in enumerate(cameras_data):
        if cam["camera_id"] == request.camera_id:
            cameras_data[i]["rtsp_url"] = request.rtsp_url
            cameras_data[i]["is_active"] = request.is_active
            camera_exists = True
            message = f"Kamera ID '{request.camera_id}' ma'lumotlari yangilandi."
            break
    
    if not camera_exists:
        cameras_data.append(request.dict())
        message = f"Yangi kamera '{request.camera_id}' JSON fayliga qo'shildi."

    save_cameras_to_json(cameras_data)

    return {"message": f"{message} Streamni boshlash uchun '/cameras/start-all-active' yoki '/cameras/start-single/{{camera_id}}' endpointlarini ishlating."}


@app.post("/cameras/start-all-active", summary="JSON faylidagi barcha faol kameralarni ishga tushirish")
async def start_all_active_cameras():
    """
    JSON faylida 'is_active: true' deb belgilangan barcha kameralarni ishga tushiradi.
    """
    if not detection_service:
        raise HTTPException(status_code=500, detail="Deteksiya xizmati ishga tushirilmagan.")

    cameras_from_json = load_cameras_from_json()
    active_cameras_to_start = [cam for cam in cameras_from_json if cam.get("is_active", False)]
    
    started_count = 0
    skipped_count = 0
    
    if active_cameras_to_start:
        print(f"JSON faylidan {len(active_cameras_to_start)} ta faol kamera yuklanmoqda va ishga tushirilmoqda...")
        for cam in active_cameras_to_start:
            if cam["camera_id"] not in active_stream_processors:
                processor = VideoStreamProcessor(
                    rtsp_url=cam["rtsp_url"],
                    camera_id=cam["camera_id"],
                    detection_service=detection_service
                )
                active_stream_processors[cam["camera_id"]] = processor
                processor.start()
                print(f"Kamera '{cam['camera_id']}' ishga tushirildi.")
                started_count += 1
            else:
                print(f"Kamera '{cam['camera_id']}' allaqachon ishlamoqda. O'tkazib yuborildi.")
                skipped_count += 1
    else:
        print("JSON faylida faol kameralar topilmadi.")

    return {"message": f"{started_count} ta kamera ishga tushirildi, {skipped_count} ta kamera o'tkazib yuborildi."}


@app.post("/cameras/start-single/{camera_id}", summary="Bitta kamerani ishga tushirish")
async def start_single_camera(camera_id: str):
    """
    Berilgan kamera ID'si bo'yicha kamerani ishga tushiradi.
    """
    if not detection_service:
        raise HTTPException(status_code=500, detail="Deteksiya xizmati ishga tushirilmagan.")

    cameras_data = load_cameras_from_json()
    camera_config = next((cam for cam in cameras_data if cam["camera_id"] == camera_id), None)

    if not camera_config:
        raise HTTPException(status_code=404, detail=f"Kamera ID '{camera_id}' JSON faylida topilmadi.")
    
    if not camera_config.get("is_active", False):
        raise HTTPException(status_code=400, detail=f"Kamera '{camera_id}' faol emas deb belgilangan. Uni faollashtiring.")

    if camera_id in active_stream_processors:
        raise HTTPException(status_code=400, detail=f"Kamera ID '{camera_id}' allaqachon ishlamoqda.")

    processor = VideoStreamProcessor(
        rtsp_url=camera_config["rtsp_url"],
        camera_id=camera_id,
        detection_service=detection_service
    )
    active_stream_processors[camera_id] = processor
    processor.start()

    return {"message": f"Kamera '{camera_id}' stream muvaffaqiyatli boshlandi."}


@app.post("/cameras/stop/{camera_id}", summary="Kamerani to'xtatish")
async def stop_camera(camera_id: str):
    """
    Berilgan kamera ID'si bo'yicha streamni to'xtatadi va uni JSON faylida nofaol holatga o'tkazadi.
    """
    if camera_id not in active_stream_processors:
        raise HTTPException(status_code=404, detail=f"Kamera ID '{camera_id}' topilmadi yoki ishlamoqda emas.")

    # Streamni to'xtatish
    processor = active_stream_processors.pop(camera_id)
    processor.stop()

    # JSON faylida kamerani nofaol holatga o'tkazish
    cameras_data = load_cameras_from_json()
    found = False
    for cam in cameras_data:
        if cam["camera_id"] == camera_id:
            cam["is_active"] = False # Nofaol holatga o'tkazish
            found = True
            break
    save_cameras_to_json(cameras_data)

    if found:
        return {"message": f"Kamera '{camera_id}' stream to'xtatildi va JSON faylida nofaol holatga o'tkazildi."}
    
    return {"message": f"Kamera '{camera_id}' stream to'xtatildi. JSON faylida topilmadi."}

@app.get("/cameras/status", summary="Aktiv kameralar holatini olish")
async def get_camera_status():
    """
    Hozirda faol bo'lgan kameralar ro'yxatini qaytaradi.
    """
    return {"active_cameras": list(active_stream_processors.keys())}

@app.get("/cameras/all", summary="Barcha kameralar ro'yxatini JSON faylidan olish")
async def get_all_cameras():
    """
    JSON faylida saqlangan barcha kameralar ro'yxatini qaytaradi.
    """
    return {"cameras": load_cameras_from_json()}


# Dastur ishga tushganda (server start bo'lganda) bajariladigan funksiya
@app.on_event("startup")
async def startup_event():
    global detection_service # Global o'zgaruvchini belgilash

    # Papkalarni yaratish
    os.makedirs(settings.IMAGE_SAVE_PATH, exist_ok=True)
    print(f"'{settings.IMAGE_SAVE_PATH}' papkasi yaratildi yoki mavjud.")
    employee_photo_dir = os.path.join(settings.IMAGE_SAVE_PATH, "employee_photos")
    os.makedirs(employee_photo_dir, exist_ok=True)
    print(f"'{employee_photo_dir}' papkasi yaratildi yoki mavjud.")

    # Deteksiya xizmatini ishga tushirish va yuz embeddinglarini yuklash
    db_session = next(get_db())
    try:
        detection_service = HelmetDetectionService(db_session)
    finally:
        db_session.close()

    # Dastur ishga tushganda kameralar avtomatik ishga tushirilmaydi.
    # Ular "/cameras/start-all-active" yoki "/cameras/start-single/{camera_id}" orqali boshlanadi.
    print("FastAPI ilovasi ishga tushdi. Kameralar avtomatik ishga tushirilmaydi.")

# Dastur to'xtatilganda (server stop bo'lganda) bajariladigan funksiya
@app.on_event("shutdown")
async def shutdown_event():
    print("FastAPI ilovasi to'xtatildi.")
    # Barcha aktiv streamlarni to'xtatish
    for camera_id, processor in list(active_stream_processors.items()):
        print(f"O'chirish vaqtida kamera '{camera_id}' streamini to'xtatish...")
        processor.stop()
    active_stream_processors.clear()
