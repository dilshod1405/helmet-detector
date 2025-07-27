#!/bin/bash
# entrypoint.sh

# Skript xatolik yuz berganda to'xtashini ta'minlash
set -e

echo "----------------------------------------------------"
echo "Entrypoint.sh skripti ishga tushmoqda..."
echo "----------------------------------------------------"

# 1. PostgreSQL ma'lumotlar bazasining tayyor bo'lishini kutish
# Bu Docker Compose yoki Kubernetes kabi muhitlarda muhim,
# chunki DB konteyneri ilova konteyneridan oldin to'liq ishga tushmasligi mumkin.
echo "PostgreSQL ma'lumotlar bazasining tayyor bo'lishini kutmoqda..."
/usr/bin/wait-for-it.sh "$DATABASE_HOST:$DATABASE_PORT" --timeout=60 --strict -- echo "PostgreSQL tayyor!"

# 2. Alembic migratsiyalarini qo'llash
# Bu ma'lumotlar bazasi sxemasini eng so'nggi holatga yangilaydi.
echo "Alembic migratsiyalarini qo'llamoqda..."
alembic upgrade head

# 3. Xodimlar ma'lumotlarini tashqi API'dan yangilash (birinchi marta yoki yangilash uchun)
# Bu API orqali xodimlarni yuklash va ularning rasmlari/embeddinglarini saqlashni ta'minlaydi.
# Bu faqat bir marta bajarilishi kerak bo'lishi mumkin, yoki har deployda yangilanishi mumkin.
# Agar bu jarayon uzoq davom etsa va ilova tezroq ishga tushishi kerak bo'lsa,
# bu qadamni alohida CronJob yoki boshqa mexanizm orqali bajarish tavsiya etiladi.
echo "Xodimlar ma'lumotlarini tashqi API'dan yangilamoqda..."
# Uvicorn serverini fon rejimida ishga tushirish
# Bu endpoint.sh ni bloklamasdan API chaqiruvini bajarishga imkon beradi
# Uvicornni to'g'ri ishga tushirish uchun kerakli PYTHONPATH ni sozlash
export PYTHONPATH=/app:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8000 & # FastAPI ni fon rejimida ishga tushirish

# FastAPI ishga tushishi uchun biroz kutish
echo "FastAPI ishga tushishi uchun 10 soniya kutmoqda..."
sleep 10

# Xodimlarni yangilash endpointini chaqirish
echo "Xodimlarni yangilash endpointini chaqirmoqda..."
curl -X POST "http://localhost:8000/employees/update-from-api" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $EXTERNAL_API_TOKEN" \
     --fail --silent --show-error || { echo "Xodimlarni yangilashda xato yuz berdi. Davom etilmoqda..."; }

# Fon rejimida ishlayotgan FastAPI jarayonini o'ldirish
echo "Fon rejimida ishlayotgan FastAPI jarayonini to'xtatmoqda..."
kill %1 || true # %1 - oxirgi fon jarayoni (uvicorn)

# 4. Asosiy ilovani ishga tushirish (Gunicorn bilan production uchun)
# Gunicorn FastAPI ilovasini barqaror va samarali boshqaradi.
echo "Asosiy FastAPI ilovasini Gunicorn orqali ishga tushirmoqda..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000

# Agar gunicorn ishga tushmasa, uvicorn bilan ishga tushirish (zaxira)
# exec uvicorn app.main:app --host 0.0.0.0 --port 8000