# 👷 Helmet Detection System

## 🎯 About the Project

The **Helmet Detection System** is an advanced AI-powered platform designed to monitor and enforce workplace safety regulations by detecting whether individuals are wearing safety helmets in real-time video streams.

It identifies individuals not wearing helmets, recognizes their faces using stored employee data, and logs incidents for monitoring and action.

---

## ✨ Features

- **Real-time Detection** – Analyzes live video feeds from IP cameras.
- **Helmet & Person Detection** – Powered by YOLOv8 to identify people and helmets.
- **Hard Hat Absence Alerts** – Detects individuals without helmets and flags them.
- **Face Recognition** – Identifies individuals using DeepFace.
- **Incident Logging** – Records incident time, employee ID, image, name, and camera location.
- **Employee Sync** – Fetches employee photos and generates embeddings via external API.
- **Camera Management** – Add, start, stop, and list camera streams via API.
- **Scalable Deployment** – Docker & Docker Compose ready.
- **GPU Support** – Accelerated inference using NVIDIA GPUs (e.g., Tesla T4).

---

## 🛠️ Technologies

### Backend
- **Python 3.12**
- **FastAPI** – High-performance async API framework.
- **SQLAlchemy** – ORM for DB interaction.
- **PostgreSQL** – Relational database.
- **pgvector** – For storing face embeddings.
- **DeepFace** – Face detection & recognition.
- **YOLOv8 (Ultralytics)** – Object detection (people, helmets).
- **httpx** – Async HTTP client.
- **APScheduler** – Scheduled jobs.
- **Gunicorn** – WSGI server.

### Frontend Admin Panel
- **Next.js**
- **Tailwind CSS**
- **Lucide React**
- **Yarn**

### Infrastructure
- **Docker & Docker Compose**
- **Alembic** – Database migrations.
- **NVIDIA CUDA & cuDNN**
- **NVIDIA Container Toolkit**
- **NGINX (Recommended for production)**
- **GitLab CI/CD (Recommended)**

---

## 📂 Project Structure

```
helmet_detector/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── cameras.py
│   │   ├── employees.py
│   │   └── incidents.py
│   ├── core/config.py
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   └── services/
│       ├── camera_manager.py
│       ├── employee_data_updater.py
│       └── helmet_detection_service.py
├── alembic/
│   ├── env.py
│   └── versions/
├── data/
│   ├── detected_incidents/
│   └── employee_photos/
├── models/ (contains yolov8n.pt)
├── venv/
├── entrypoint.sh
├── wait-for-it.sh
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── prod_requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## 🚀 Setup and Running

### ✅ Requirements

- Python 3.12
- PostgreSQL
- ffmpeg (system-level)
- Docker & Docker Compose
- Git

---

## ⚙️ Local Setup (CPU-Only)

```bash
# Clone repo
git clone https://github.com/dilshod1405/helmet-detector.git helmet_detector
cd helmet_detector

# Virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

```

##  .env

```bash

DATABASE_URL=postgresql://user:password@localhost:5432/helmet_db
EXTERNAL_API_URL=http://api-vchd-7.uz/api/w-list
EXTERNAL_API_TOKEN=your_api_token
FORCE_CPU_FOR_TF=True

# Replace user, password, and helmet_db with your actual PostgreSQL credentials.

```


##  🧩 Database Setup

Ensure PostgreSQL is running and the database helmet_db is created.

```bash

# If not already initialized
alembic init alembic

# Configure alembic/env.py with render_item

# Create and apply migration
alembic revision --autogenerate -m "Initial setup"
alembic upgrade head

```


## 🤖 YOLO Model

Place the YOLOv8 model file in models/ directory:

```bash

models/yolov8n.pt

```

## ▶️ Run Application

```bash

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

```
Visit: http://localhost:8000


## 🔁 Sync Employee Data

```bash

POST /employees/update-from-api

```

This fetches employee data and face embeddings from the external API.


## 🧠 GPU-Enabled Server Deployment (Tesla T4)

### Server Requirements

- **Ubuntu LTS**
- **NVIDIA Drivers (e.g., nvidia-driver-535)**
- **CUDA 12.x**
- **cuDNN 9.3.0+**
- **Docker + Compose**
- **NVIDIA Container Toolkit**
- **PostgreSQL (hosted)**

Suggestion: DigitalOcean would be better choice for this project. It provides GPU droplets.

### Steps

1. Installation dependencies:

```bash

sudo apt update
sudo apt install docker.io docker-compose ffmpeg python3.12 python3.12-venv git curl netcat-traditional -y

```

2. Install NVIDIA drivers, CUDA, cuDNN

    Follow official guides at:
    - [https://developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)
    - [https://developer.nvidia.com/cudnn](https://developer.nvidia.com/cudnn)


3. Configure `.bashrc`:

```bash

export PATH=/usr/local/cuda-12.x/bin:${PATH}
export LD_LIBRARY_PATH=/usr/local/cuda-12.x/lib64:${LD_LIBRARY_PATH}
source ~/.bashrc

```

4. Install NVIDIA Container Toolkit:

```bash

distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list |
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' |
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

```


5. Clone and configure project:

```bash

git clone https://github.com/dilshod1405/helmet-detector.git
cd helmet_detector

```

Update  `.env` file:

```env

DATABASE_URL=postgresql://yourusername:password@host:port/database_name
EXTERNAL_API_URL=http://api-vchd-7.uz/api/w-list
EXTERNAL_API_TOKEN=your_api_token
FORCE_CPU_FOR_TF=False

```

6. Alembic Migration:

```bash

alembic revision --autogenerate -m "Initial setup"
alembic upgrade head

```

7. Run with Docker Compose:

```bash

docker compose up -d --build

```

Access: http://<your-server-ip>:8000


## 💡 Main API Endpoints

- `POST /employees/update-from-api` - Sync employee data and face embeddings
- `POST /cameras/add` - Add new camera
- `POST /cameras/start-single/{camera_id}` - Start single camera stream
- `POST /cameras/stop/{camera_id}` - Stop specific camera
- `POST /cameras/start-all-active` - Start all active cameras
- `GET /cameras/all` - Get list of all cameras
- `GET /cameras/status` - Get active camera statuses
- `GET /incidents/all` - Get all recorded incidents


## 📸 Incident Workflow

1. Camera captures frames → YOLOv8 detects person & helmet.

2. No helmet → Face cropped → DeepFace runs identification.

3. Incident logged in PostgreSQL and image saved to data/.
