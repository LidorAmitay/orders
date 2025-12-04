from fastapi import FastAPI
from src.config.settings import settings
from src.routes import orders

app = FastAPI(title=settings.app_name)

# Register routers
app.include_router(orders.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

