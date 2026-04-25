import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config.settings import settings
from src.messaging.event_consumer import EventConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(name)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer = EventConsumer()
    await consumer.connect(settings.rabbitmq_url)
    app.state.event_consumer = consumer
    yield
    await consumer.disconnect()


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
