from fastapi import FastAPI
from src.config.settings import settings
from src.routes.health import router as health_router

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
