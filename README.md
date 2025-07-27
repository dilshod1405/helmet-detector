👷 Helmet Detection System
🎯 About the Project
The "Helmet Detection System" is an advanced artificial intelligence-based solution designed to monitor employee compliance with safety regulations, specifically the mandatory wearing of hard hats, through real-time video streams. The system automatically detects individuals moving without a hard hat, identifies them by face, and records relevant incidents. This helps to enhance safety and ensure adherence to workplace rules.

✨ Features
Real-time Detection: Analyzes real-time video streams from IP cameras.

Helmet and Person Detection: Utilizes the YOLOv8 model to detect people and their hard hats within video frames.

Hard Hat Absence Detection: Automatically flags instances where a person is detected but a hard hat is not.

Face Recognition: Identifies employees without hard hats using the DeepFace library.

Incident Logging: Stores information about detected and identified hard-hatless employees (employee ID, name, incident time, image, location) in a database.

Employee Data Synchronization: Automatically fetches employee lists and their photos from an external API and generates face embeddings.

Camera Management: API endpoints to add, remove, start, and stop camera streams.

Scalability: Easy deployment and scaling using Docker and Docker Compose.

GPU Acceleration: Leverages NVIDIA GPUs (e.g., Tesla T4) for high-performance AI model inference.

🛠️ Technologies
Backend
Python: Primary programming language.

FastAPI: High-performance and fast web framework for building APIs.

SQLAlchemy: ORM (Object-Relational Mapper) for database interaction.

PostgreSQL: Relational database for data storage.

pgvector: PostgreSQL extension for vector data types, enabling efficient storage and similarity search of face embeddings.

DeepFace: Advanced library for face detection, alignment, and recognition (utilizes TensorFlow/Keras models internally).

Ultralytics YOLOv8: State-of-the-art model for object detection (person and hard hat).

httpx: For asynchronous HTTP requests.

APScheduler: For scheduling background tasks (e.g., employee data synchronization).

Gunicorn: WSGI server for running the FastAPI application in a production environment.

Frontend (Future)
React.js (JSX): JavaScript library for building interactive user interfaces.

Yarn: Package manager.

Tailwind CSS: Utility-first CSS framework for rapid and responsive UI development.

Lucide React: Vector icon library.

Next.js (Planned for future): React framework for server-side rendering and other advanced features.

Infrastructure & Deployment
Docker: For containerizing the application.

Docker Compose: For managing multiple Docker containers (application, database) together.

Alembic: For managing database migrations.

NVIDIA CUDA & cuDNN: Libraries for GPU acceleration.

NVIDIA Container Toolkit: Enables Docker containers to utilize NVIDIA GPUs.

GitLab CI/CD (Recommended): For automated build, test, and deployment pipelines.

NGINX (Recommended): For reverse proxy and load balancing.

📂 Project Structure
helmet_detector/
├── app/
│   ├── __init__.py
│   ├── main.py                     # Main FastAPI application file
│   ├── api/                        # API endpoints
│   │   ├── __init__.py
│   │   ├── cameras.py
│   │   ├── employees.py
│   │   └── incidents.py
│   ├── core/                       # Configuration and utility functions
│   │   ├── __init__.py
│   │   └── config.py               # Project settings
│   ├── db/                         # Database-related code
│   │   ├── __init__.py
│   │   ├── database.py             # DB connection
│   │   └── models.py               # SQLAlchemy models
│   └── services/                   # Core business logic
│       ├── __init__.py
│       ├── camera_manager.py       # Manages camera streams (future)
│       ├── employee_data_updater.py # Updates employee data
│       └── helmet_detection_service.py # Helmet and face detection logic
├── alembic/                        # Alembic migration directory
│   ├── versions/                   # Migration script files
│   ├── env.py                      # Alembic environment configuration
│   └── script.py.mako
├── data/                           # Runtime generated data
│   ├── detected_incidents/         # Images of detected incidents
│   └── employee_photos/            # Employee photos
├── models/                         # ML models (e.g., yolov8n.pt)
├── venv/                           # Python virtual environment (ignored by Git)
├── entrypoint.sh                   # Script executed when Docker container starts
├── wait-for-it.sh                  # Script to wait for service availability
├── Dockerfile                      # Docker image build file
├── docker-compose.yml              # Docker Compose configuration file
├── requirements.txt                # Local (development) dependencies
├── prod_requirements.txt           # Server (production) dependencies
├── .env                            # Environment variables (ignored by Git)
├── .gitignore                      # Files ignored by Git
└── README.md                       # Project README file

🚀 Setup and Running
Requirements
Python 3.12

PostgreSQL database

Docker and Docker Compose

ffmpeg (should be installed at the system level)

Git

Local Setup (CPU-Only)
This method is for running the project on your local machine using only the CPU.

Clone the repository:

git clone [https://github.com/dilshod1405/helmet-detector.git](https://github.com/dilshod1405/helmet-detector.git) helmet_detector
cd helmet_detector

Create and activate a virtual environment:

python3.12 -m venv venv
source venv/bin/activate

Install Python dependencies:

pip install --upgrade pip
pip install -r requirements.txt

Configure the .env file:
Create a .env file in the project root directory and fill in the following:

# .env
DATABASE_URL=postgresql://user:password@localhost:5432/helmet_db
EXTERNAL_API_URL=http://api-vchd-7.uz/api/w-list
EXTERNAL_API_TOKEN=your_api_token
YOLO_MODEL_PATH=models/yolov8n.pt
IMAGE_SAVE_PATH=data/detected_incidents
FORCE_CPU_FOR_TF=True # Set to TRUE for CPU-only operation

Adjust user, password, helmet_db to match your PostgreSQL setup.

Start PostgreSQL database:
Ensure your PostgreSQL server is running and create a database named helmet_db.

Apply Alembic migrations:

alembic init alembic (If not already done)

Configure alembic/env.py with the render_item function (refer to the "Alembic Configuration" section in the conversation history).

alembic revision --autogenerate -m "Initial database setup"

alembic upgrade head

Download YOLO model:
Place the yolov8n.pt file into the models/ directory.

Run the application:

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

The application will be accessible at http://localhost:8000.

Synchronize employee data:
To load employees and generate their face embeddings via API:
Send a POST request to http://localhost:8000/employees/update-from-api (e.g., using Postman).

Server Deployment (GPU-Enabled - NVIDIA Tesla T4)
This method is for deploying the project on a server using Docker containers and leveraging an NVIDIA Tesla T4 GPU.

Server Requirements
Ubuntu Server LTS (recommended)

NVIDIA Drivers: Latest stable drivers for Tesla T4.

CUDA Toolkit 12.x: (Compatible with your CUDA 12.9).

cuDNN 9.3.0 (or newer): Must be compatible with TensorFlow 2.19.0.

Docker and Docker Compose

NVIDIA Container Toolkit

PostgreSQL server (on a separate VM or as a service)

Deployment Steps (on Server)
Connect to your server via SSH.

Install system-level dependencies:

sudo apt update
sudo apt install docker.io docker-compose ffmpeg python3.12 python3.12-venv git curl netcat-traditional -y

python3.12-venv and python3.12 should match your Python version.

Add user to Docker group:

sudo usermod -aG docker ${USER}
newgrp docker # Or log out and log back in

Install NVIDIA Drivers, CUDA Toolkit, and cuDNN:

Drivers: sudo apt install nvidia-driver-<version> (e.g., nvidia-driver-535 or the latest recommended). Remember to sudo reboot.

CUDA Toolkit: Find and follow the installation guide for your Ubuntu version and CUDA 12.x on the NVIDIA Developer website (developer.nvidia.com/cuda-downloads).

cuDNN: Download CuDNN 9.3.0 (or newer) for CUDA 12.x from the NVIDIA Developer website (developer.nvidia.com/cudnn) and install it on your system via .deb packages.

Configure environment variables: Add export PATH=/usr/local/cuda-12.x/bin:${PATH} and export LD_LIBRARY_PATH=/usr/local/cuda-12.x/lib64:${LD_LIBRARY_PATH} to your .bashrc file (replace 12.x with your exact CUDA version) and source ~/.bashrc.

Install NVIDIA Container Toolkit:

distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
&& curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
&& curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

Clone the repository:

git clone [https://github.com/dilshod1405/helmet-detector.git](https://github.com/dilshod1405/helmet-detector.git) helmet_detector
cd helmet_detector

Update prod_requirements.txt:
Replace the content of prod_requirements.txt with the code from the "Python Libraries (GPU-enabled version)" section provided in previous conversations.

Configure the .env file:
Create a .env file in the project root directory and fill in the following:

# .env (on Server)
DB_HOST=<DB_VM_IP_ADDRESS> # IP address of your PostgreSQL VM
DB_PORT=5432
DB_USER=user
DB_PASSWORD=password
DB_NAME=helmet_db

EXTERNAL_API_URL=http://api-vchd-7.uz/api/w-list
EXTERNAL_API_TOKEN=your_api_token

FORCE_CPU_FOR_TF=False # Set to FALSE to utilize GPU

YOLO_MODEL_PATH=models/yolov8n.pt
IMAGE_SAVE_PATH=data/detected_incidents

Replace <DB_VM_IP_ADDRESS> with the actual IP address of your PostgreSQL VM.

Place YOLO model:
Ensure the yolov8n.pt file is in the models/ directory. This file should be part of your Git repository.

Configure Alembic and apply migrations:

alembic init alembic (If not already done)

Configure alembic/env.py with the render_item function (refer to the "Alembic Configuration" section in the conversation history).

alembic revision --autogenerate -m "Initial database setup"

alembic upgrade head

Run the application using Docker Compose:

docker compose up -d --build

The application will be accessible on the server's port 8000.

💡 Usage
Once the system is running, you can use the following main API endpoints:

POST /employees/update-from-api: Synchronizes employee data (including photos and face embeddings) from the external API. It's crucial to run this process once after deployment.

POST /cameras/add: Adds a new camera to the system and saves its configuration to cameras.json.

POST /cameras/start-single/{camera_id}: Starts processing the video stream from a specific camera.

POST /cameras/stop/{camera_id}: Stops processing the video stream from a specific camera and marks it as inactive in cameras.json.

POST /cameras/start-all-active: Starts processing video streams from all cameras marked as active in cameras.json.

GET /cameras/all: Retrieves a list of all cameras configured in cameras.json.

GET /cameras/status: Retrieves a list of currently active camera streams.

GET /incidents/all: Retrieves a list of all recorded incidents.

When a video stream is received from a camera, the system detects individuals without hard hats, identifies them, and saves incidents to the database. Detected incident images are stored in the data/detected_incidents folder.