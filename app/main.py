from threading import Thread
from fastapi import FastAPI
from app.api.routes import router as violations_router
from app.camera.stream import run_all_cameras

app = FastAPI(
    title="Helmet Detection API",
    description="Zavodda kaskani tekshiruvchi va qoidabuzarliklarni qayd etuvchi API",
    version="1.0.0",
)

app.include_router(violations_router)

@app.on_event("startup")
def start_streams():
    t = Thread(target=run_all_cameras)
    t.start()

@app.get("/")
async def root():
    return {"message": "Helmet detection API ishga tushdi!"}
