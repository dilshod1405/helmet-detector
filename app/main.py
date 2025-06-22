from fastapi import FastAPI
from app.api.routes import router as violations_router

app = FastAPI(
    title="Helmet Detection API",
    description="Zavodda kaskani tekshiruvchi va qoidabuzarliklarni qayd etuvchi API",
    version="1.0.0",
)

# Routerni ilovaga qo'shamiz
app.include_router(violations_router)

# Root endpoint — test uchun oddiy javob qaytaradi
@app.get("/")
async def root():
    return {"message": "Helmet detection API ishga tushdi!"}
