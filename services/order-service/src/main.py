from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config.settings import settings
from src.messaging.event_publisher import EventPublisher
from src.routes import orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    publisher = EventPublisher()
    await publisher.connect(settings.rabbitmq_url)
    app.state.event_publisher = publisher
    yield
    await publisher.disconnect()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Register routers
app.include_router(orders.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

