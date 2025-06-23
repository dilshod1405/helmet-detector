# Helmet Detector

![Project Logo](https://i.postimg.cc/j53sHDSc/cam1.png) <!-- Optional -->

---

## Overview

**Helmet Detector** is a real-time AI-powered monitoring system designed to detect whether workers are wearing helmets by analyzing video streams from RTSP cameras. It uses the YOLOv8 model for helmet detection and `face_recognition` for employee identification. Violations (absence of helmets) are saved with images and timestamps, accessible via a REST API.

---

## Features

- Real-time processing of RTSP camera streams
- Helmet detection using YOLOv8
- Employee face recognition for identity verification
- Violation logging with images and timestamps
- Stream monitoring only during working hours (e.g., 8:00 to 18:00)
- REST API built with FastAPI for accessing violation data
- PostgreSQL database with Alembic migrations for schema management
- Easy deployment using Docker and Docker Compose

---

## Technologies

- Python 3.12+
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [face_recognition](https://github.com/ageitgey/face_recognition)
- FastAPI
- SQLAlchemy & Alembic
- PostgreSQL
- Docker & Docker Compose
- OpenCV

---

## Requirements

- Python 3.12 or higher
- Docker (for deployment)
- RTSP-compatible IP camera

---

## Installation & Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/username/helmet_detector.git
   cd helmet_detector
   ```


2. **Create and activate a virtual environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables**

    ```bash
    POSTGRES_USER=your_db_user
    POSTGRES_PASSWORD=your_db_password
    POSTGRES_DB=your_db_name
    DATABASE_URL=postgresql+psycopg2://your_db_user:your_db_password@localhost:5432/your_db_name
    RTSP_URL=rtsp://username:password@camera_ip:port/path
    YOLO_MODEL_PATH=helmet-detection.pt
    ```

5. **Apply database migrations**
    ```bash
    alembic upgrade head
    ```

6. **Prepare directors**
    ```bash
    mkdir violations employee_faces
    ```

## Running the application
### Locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
```

### Using Docker Compose

```bash
docker-compose up --build
```

The API will be available at: http://localhost:8010/api/violations



## API Endpoints

- GET /api/violations — Returns a list of recorded violations with employee names, timestamps, and image paths.


## Project Structure

```bash
helmet_detector/
├── app/
│   ├── detection/          # Helmet and face detection modules
│   ├── databases/          # DB models, schemas, CRUD
│   ├── camera/             # Camera capture and violation image saving
│   ├── main.py             # FastAPI app and camera streaming threads
│   └── config.py           # Configuration variables
├── violations/             # Saved violation images
├── employee_faces/         # Employee face images for encoding
├── Dockerfile
├── docker-compose.yml
├── alembic/                # Alembic migration scripts
├── requirements.txt
└── README.md
```


## Notes

- Make sure your camera supports RTSP streaming.
- Adjust working hours in the configuration if necessary.
- The system assumes no people are present outside working hours.
- Use environment variables for all sensitive information.

## Contact
For questions or support, contact [dilshod.normurodov1392@gmail.com]