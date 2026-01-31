from fastapi import FastAPI
from src.config.settings import settings
from src.routes.health import router as health_router
from src.routes.users import router as users_router

app = FastAPI(title=settings.app_name)

app.include_router(health_router)
app.include_router(users_router)
