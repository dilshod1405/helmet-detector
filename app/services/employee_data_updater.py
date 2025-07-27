import httpx
from deepface import DeepFace
import numpy as np
from sqlalchemy.orm import Session
from app.db.models import Employee
from app.core.config import settings
import os
import uuid
from PIL import Image
import io
import urllib.parse
import tensorflow as tf

# TensorFlow'ni CPU'da ishlashga majburlash (agar sozlamalarda belgilangan bo'lsa)
if settings.FORCE_CPU_FOR_TF:
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    print("TensorFlow GPU'da ishlashga majburlanmadi. Faqat CPU ishlatiladi.")
else:
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"TensorFlow quyidagi GPU'larda ishlaydi: {gpus}")
        except RuntimeError as e:
            print(f"GPU konfiguratsiyasida xato: {e}")
    else:
        print("GPU topilmadi. TensorFlow CPU'da ishlaydi.")


# Xodimlarning rasmlarini saqlash uchun papka
EMPLOYEE_PHOTO_DIR = os.path.join(settings.IMAGE_SAVE_PATH, "employee_photos")
os.makedirs(EMPLOYEE_PHOTO_DIR, exist_ok=True)
print(f"Rasm saqlash papkasi tekshirildi/yaratildi: {EMPLOYEE_PHOTO_DIR}")


async def fetch_employees_from_external_api():
    """
    Tashqi API'dan xodimlar ma'lumotlarini POST so'rov orqali pagination bilan oladi.
    Sahifa raqamini URL query parametri sifatida yuboradi.
    """
    headers = {
        "Authorization": f"Bearer {settings.EXTERNAL_API_TOKEN}",
        "Content-Type": "application/json"
    }
    all_employees_data = []
    current_page = 1
    total_pages_from_api = 1

    print("Xodimlar ma'lumotlarini sahifalar bo'yicha olish boshlandi...")
    print(f"Boshlang'ich total_pages_from_api: {total_pages_from_api}")

    while current_page <= total_pages_from_api:
        request_url = f"{settings.EXTERNAL_API_URL}?page={current_page}"
        payload = {} 

        print(f"So'rov yuborilmoqda: URL={request_url}, Sahifa={current_page}, Hozirgi total_pages_from_api={total_pages_from_api}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(request_url, headers=headers, json=payload, timeout=60.0)
                response.raise_for_status()
                data = response.json()

                print(f"API javobi (sahifa {current_page}): {data.keys()}")

                if "results" in data and isinstance(data["results"], list):
                    all_employees_data.extend(data["results"])
                    
                    if "total_pages" in data:
                        total_pages_from_api = data["total_pages"]
                        print(f"total_pages_from_api {total_pages_from_api} ga yangilandi.")
                    else:
                        print("API javobida 'total_pages' kaliti topilmadi. Pagination to'xtatilishi mumkin.")
                        break

                    print(f"Sahifa {current_page}/{total_pages_from_api} yuklandi. Jami xodimlar: {len(all_employees_data)}")
                    current_page += 1
                else:
                    print(f"API javobida 'results' kaliti topilmadi yoki format noto'g'ri: {data}")
                    break
        except httpx.RequestError as exc:
            print(f"Tashqi API'ga so'rov yuborishda xato yuz berdi (sahifa {current_page}): {exc}")
            break
        except httpx.HTTPStatusError as exc:
            print(f"Tashqi API'dan xato javob keldi (sahifa {current_page}): {exc.response.status_code} - {exc.response.text}")
            break
        except Exception as exc:
            print(f"Xodimlarni olishda kutilmagan xato (sahifa {current_page}): {exc}")
            break
    
    print(f"Jami {len(all_employees_data)} ta xodim ma'lumotlari olindi. Pagination tugadi.")
    return all_employees_data

async def download_and_save_photo(photo_url: str, employee_external_id: int):
    """
    Xodim rasmini URL orqali yuklab oladi va mahalliy saqlaydi.
    Rasmni xodimning unikal external_id si bilan nomlaydi.
    """
    try:
        parsed_url = urllib.parse.urlparse(photo_url)
        path_segments = parsed_url.path.split('.')
        file_extension = path_segments[-1] if len(path_segments) > 1 else "png"

        new_filename = f"{employee_external_id}.{file_extension}"
        photo_path = os.path.join(EMPLOYEE_PHOTO_DIR, new_filename)
        
        if os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
            print(f"Rasm '{new_filename}' allaqachon mavjud va to'liq. Yuklab o'tkazib yuborildi.")
            return photo_path

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(photo_url, timeout=10.0)
            response.raise_for_status()

            if response.history:
                print(f"Rasm URL'i {photo_url} dan {response.url} ga yo'naltirildi. Yakuniy status: {response.status_code}")
            else:
                print(f"Rasm {photo_url} dan yuklab olindi. Status: {response.status_code}")

            print(f"Rasmni saqlashga urinish: {photo_path}")
            with open(photo_path, "wb") as f:
                f.write(response.content)
            print(f"Rasm muvaffaqiyatli saqlandi: {photo_path}")
            return photo_path
    except httpx.RequestError as exc:
        print(f"Rasm yuklashda so'rov xatosi yuz berdi {photo_url}: {exc}")
        return None
    except httpx.HTTPStatusError as exc:
        print(f"Rasm yuklashda HTTP status xatosi {photo_url} (yakuniy URL: {exc.response.url}): {exc.response.status_code} - {exc.response.text}")
        return None
    except Exception as exc:
        print(f"Rasm yuklashda kutilmagan xato {photo_url}: {exc}")
        return None

def generate_face_embedding(image_path: str):
    """
    Berilgan rasm yo'lidan yuz embeddingini yaratadi.
    DeepFace kutubxonasidan foydalanadi.
    Agar rasmda yuz topilmasa yoki embedding yaratilmasa, None qaytaradi.
    """
    try:
        print(f"Yuz embeddingi uchun rasmni yuklash va DeepFace orqali qayta ishlash: {image_path}")
        embeddings = DeepFace.represent(
            img_path=image_path,
            model_name="Facenet",
            detector_backend="opencv",
            enforce_detection=False
        )
        
        if embeddings and len(embeddings) > 0:
            print(f"DeepFace tomonidan yaratilgan embedding (birinchi 5 element): {embeddings[0]['embedding'][:5]}...")
            print("Yuz embeddingi muvaffaqiyatli yaratildi.")
            return embeddings[0]["embedding"]
        else:
            print(f"Rasmdan yuz topilmadi yoki embedding yaratilmadi: {image_path}")
            return None
    except tf.errors.OpError as exc:
        print(f"Xato: TensorFlow operatsiyasida muammo yuz berdi {image_path}: {exc}")
        print("Bu ko'pincha GPU drayverlari, CUDA/cuDNN yoki TensorFlow o'rnatilishi bilan bog'liq.")
        return None
    except Exception as exc:
        print(f"Xato: Yuz embeddingini yaratishda kutilmagan xato {image_path}: {exc}")
        return None

async def update_employee_data(db: Session):
    """
    Tashqi API'dan xodimlar ma'lumotlarini yangilaydi,
    rasmlarni yuklaydi va yuz embeddinglarini bazaga saqlaydi.
    Faqat yangi yoki o'zgargan xodimlar uchun embedding yaratadi.
    """
    print("Xodimlar ma'lumotlarini yangilash boshlandi...")
    employees_data = await fetch_employees_from_external_api()

    if not employees_data:
        print("Xodimlar ma'lumotlari API'dan olinmadi. Yangilash bekor qilindi.")
        return False

    updated_count = 0
    for emp_data in employees_data:
        external_id = emp_data.get("id")
        full_name = emp_data.get("fullName")
        photo_url = emp_data.get("photo")

        if not all([external_id, full_name, photo_url]):
            print(f"Xodim ma'lumotlarida yetishmayotgan kalitlar mavjud: {emp_data}. O'tkazib yuborildi.")
            continue

        db_employee = db.query(Employee).filter(Employee.external_id == external_id).first()

        # Rasmni yuklab olish
        local_photo_path = await download_and_save_photo(photo_url, external_id)

        if not local_photo_path:
            print(f"Xodim {full_name} ({external_id}) uchun rasm yuklab bo'lmadi. O'tkazib yuborildi.")
            continue

        # Embeddingni yaratish faqat quyidagi hollarda:
        # 1. Xodim yangi bo'lsa (bazada yo'q bo'lsa)
        # 2. Xodim mavjud bo'lsa-yu, lekin uning rasm URL'i o'zgargan bo'lsa
        # 3. Xodim mavjud bo'lsa-yu, lekin uning face_embedding'i yo'q bo'lsa (avvalgi xato tufayli bo'lishi mumkin)
        face_embedding = None
        if not db_employee or \
            (db_employee and db_employee.photo_url != photo_url) or \
            (db_employee and db_employee.face_embedding is None):
            
            print(f"Xodim {full_name} ({external_id}) uchun yangi/yangilangan rasm embeddingi yaratilmoqda...")
            face_embedding = generate_face_embedding(local_photo_path)
        else:
            # Agar rasm URL'i o'zgarmagan bo'lsa va embedding mavjud bo'lsa, mavjud embeddingni ishlatamiz
            face_embedding = db_employee.face_embedding
            print(f"Xodim {full_name} ({external_id}) uchun embedding o'tkazib yuborildi (o'zgarish yo'q).")


        if face_embedding is None:
            print(f"Xodim {full_name} ({external_id}) uchun yuz embeddingi yaratilmadi. O'tkazib yuborildi.")
            continue

        if db_employee:
            db_employee.full_name = full_name
            db_employee.photo_url = photo_url
            db_employee.face_embedding = face_embedding
            print(f"Xodim {full_name} ({external_id}) yangilandi.")
        else:
            new_employee = Employee(
                external_id=external_id,
                full_name=full_name,
                photo_url=photo_url,
                face_embedding=face_embedding
            )
            db.add(new_employee)
            print(f"Yangi xodim {full_name} ({external_id}) qo'shildi.")
        updated_count += 1
    
    db.commit()
    print(f"Xodimlar ma'lumotlarini yangilash yakunlandi. {updated_count} ta xodim yangilandi/qo'shildi.")
    return True
