import json
import logging

import aio_pika
from aio_pika import ExchangeType

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "orders.events"
QUEUE_NAME = "notifications.order_created"
ROUTING_KEY = "order.created"
DLX_NAME = "dlx.orders"
DLQ_NAME = "dlq.orders"


class EventConsumer:
    def __init__(self):
        self._connection: aio_pika.abc.AbstractConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None

    async def connect(self, url: str) -> None:
        try:
            self._connection = await aio_pika.connect_robust(url)
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=10)

            exchange = await self._channel.declare_exchange(
                EXCHANGE_NAME,
                ExchangeType.TOPIC,
                durable=True,
            )

            queue = await self._channel.declare_queue(
                QUEUE_NAME,
                durable=True,
                arguments={
                    "x-dead-letter-exchange": DLX_NAME,
                    "x-message-ttl": 86400000,
                },
            )

            await queue.bind(exchange, routing_key=ROUTING_KEY)

            dlx_exchange = await self._channel.declare_exchange(
                DLX_NAME,
                ExchangeType.FANOUT,
                durable=True,
            )
            dlq = await self._channel.declare_queue(DLQ_NAME, durable=True)
            await dlq.bind(dlx_exchange)

            await queue.consume(self._on_message)

            logger.info(
                "EventConsumer connected to RabbitMQ, consuming from queue '%s'",
                QUEUE_NAME,
            )
        except Exception as e:
            logger.warning("EventConsumer failed to connect to RabbitMQ: %s", e)
            self._connection = None
            self._channel = None

    async def disconnect(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("EventConsumer disconnected from RabbitMQ")

    async def _on_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process(requeue=False):
            try:
                payload = json.loads(message.body)
                data = payload["data"]
                logger.info(
                    "Notification | order_id=%s user_id=%s product_id=%s quantity=%s status=%s event_id=%s",
                    data["order_id"],
                    data["user_id"],
                    data["product_id"],
                    data["quantity"],
                    data["status"],
                    payload["event_id"],
                )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.error(
                    "Invalid message rejected (routing to DLQ): %s | body=%s",
                    e,
                    message.body,
                )
