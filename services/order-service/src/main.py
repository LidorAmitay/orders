from fastapi import FastAPI
from src.config.settings import settings

app = FastAPI(title=settings.app_name)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

