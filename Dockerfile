# Dockerfile

# NVIDIA CUDA base imijini ishlatish.
# Bu imij CUDA 12.2 va CuDNN 8 ni o'z ichiga oladi, bu TensorFlow 2.19.0 va PyTorch 2.5.1 bilan mos keladi.
# Ubuntu 22.04 asosida.
FROM nvidia/cuda:12.2.0-cudnn8-runtime-ubuntu22.04

# Ishchi katalog yaratish va unga o'tish
WORKDIR /app

# Muhit o'zgaruvchilarini o'rnatish
# PYTHONUNBUFFERED: Python stdout/stderr ni buferlamasdan chiqarishni ta'minlaydi.
# DEBIAN_FRONTEND: apt-get interaktiv savollar bermasligini ta'minlaydi.
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

# Tizim bog'liqliklarini o'rnatish
# python3.12, python3.12-venv: Loyiha uchun kerakli Python versiyasi va virtual muhit yaratish vositasi.
# python3-pip: Python paket menejeri.
# ffmpeg: Video streamlarni qayta ishlash uchun.
# libgl1-mesa-glx: OpenCV uchun ba'zi grafik kutubxonalar.
# netcat-traditional: wait-for-it.sh skripti uchun 'nc' buyrug'ini ta'minlaydi.
# git: Agar loyiha ichida git buyruqlari ishlatilishi kerak bo'lsa.
# curl: Agar wait-for-it.sh ni yuklab olish kerak bo'lsa (hozir nusxalaymiz).
RUN apt-get update && apt-get install -y \
    python3.12 python3.12-venv python3-pip \
    ffmpeg libgl1-mesa-glx \
    netcat-traditional \
    git \
    curl \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Virtual muhit yaratish va faollashtirish
RUN python3.12 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# prod_requirements.txt faylini nusxalash
COPY prod_requirements.txt .

# Python bog'liqliklarini o'rnatish
# pip ni yangilash
RUN pip install --upgrade pip
# prod_requirements.txt dagi barcha bog'liqliklarni o'rnatish (GPU ga oid bo'lmaganlar)
RUN pip install --no-cache-dir -r prod_requirements.txt

# PyTorch ni alohida, CUDA qo'llab-quvvatlashi bilan o'rnatish
# Bu PyTorch'ning rasmiy manbasidan CUDA 12.1 uchun kompilyatsiya qilingan versiyasini yuklab oladi.
# CUDA 12.9 bilan ham orqaga qarab mos kelishi kerak.
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Loyiha fayllarini konteynerga nusxalash
# Bu barcha ilova kodini, shu jumladan models/ papkasini ham nusxalaydi.
COPY . .

# entrypoint.sh va wait-for-it.sh skriptlarini nusxalash va ijro etish ruxsatini berish
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# YOLO modelining mavjudligini tekshirish (ogohlantirish)
# Agar models/yolov8n.pt fayli loyiha katalogida mavjud bo'lmasa, ogohlantirish beradi.
# Konteyner qurishdan oldin modelni loyihangizning 'models/' papkasiga joylashtirganingizga ishonch hosil qiling.
RUN if [ ! -f "models/yolov8n.pt" ]; then echo "WARNING: models/yolov8n.pt topilmadi. Iltimos, YOLO modelingiz 'models/' katalogida ekanligiga ishonch hosil qiling."; fi

# Konteyner ishga tushganda bajariladigan asosiy buyruq
# Bu entrypoint.sh skriptini ishga tushiradi.
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]