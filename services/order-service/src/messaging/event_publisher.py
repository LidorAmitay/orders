import json
import logging
import uuid
from datetime import datetime, timezone

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "orders.events"
ROUTING_KEY_ORDER_CREATED = "order.created"


class EventPublisher:
    def __init__(self):
        self._connection: aio_pika.abc.AbstractConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def connect(self, url: str) -> None:
        try:
            self._connection = await aio_pika.connect_robust(url)
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                EXCHANGE_NAME,
                ExchangeType.TOPIC,
                durable=True,
            )
            logger.info("EventPublisher connected to RabbitMQ, exchange '%s' declared", EXCHANGE_NAME)
        except Exception as e:
            logger.warning("EventPublisher failed to connect to RabbitMQ: %s", e)
            self._connection = None
            self._channel = None
            self._exchange = None

    async def disconnect(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("EventPublisher disconnected from RabbitMQ")

    async def publish_order_created(
        self,
        order_id: int,
        user_id: int,
        product_id: int,
        quantity: int,
        status: str,
    ) -> None:
        if self._exchange is None:
            logger.warning("EventPublisher not connected — skipping order.created event for order_id=%s", order_id)
            return

        payload = {
            "event_type": "order.created",
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "order_id": order_id,
                "user_id": user_id,
                "product_id": product_id,
                "quantity": quantity,
                "status": status,
            },
        }

        try:
            message = Message(
                body=json.dumps(payload).encode(),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
            )
            await self._exchange.publish(message, routing_key=ROUTING_KEY_ORDER_CREATED)
            logger.info("Published order.created event for order_id=%s (event_id=%s)", order_id, payload["event_id"])
        except Exception as e:
            logger.error("Failed to publish order.created event for order_id=%s: %s", order_id, e)
