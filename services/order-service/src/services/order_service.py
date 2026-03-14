"""
Service layer for order business logic.

This layer acts as an intermediary between the API routes and the repository layer,
providing a place for business logic and orchestration.
"""
import asyncio
import logging
from typing import Optional
from src.models.order import OrderCreate, OrderResponse
from src.repository.orders_repository import OrdersRepository
from src.clients.user_client import UserClient, UserNotFoundError, UserServiceUnavailableError
from src.messaging.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class OrderService:
    """
    Business logic layer for order operations.
    """

    def __init__(self, repository: OrdersRepository, user_client: UserClient, event_publisher: Optional[EventPublisher] = None):
        self._repository = repository
        self._user_client = user_client
        self._event_publisher = event_publisher

    async def create_order(self, order: OrderCreate) -> OrderResponse:
        """
        Create a new order after validating user exists.

        Args:
            order: OrderCreate model with order data

        Returns:
            OrderResponse: Created order with generated ID and timestamps

        Raises:
            UserNotFoundError: If user does not exist
            UserServiceUnavailableError: If user service is unavailable
            psycopg2.Error: If database operation fails
            ValueError: If order data is invalid
        """
        logger.debug(
            "Validating user existence before creating order",
            extra={
                "service_name": "order-service",
                "user_id": order.user_id,
            }
        )

        # Validate user exists via User Service
        self._user_client.get_user(order.user_id)

        logger.debug(
            "User validation successful, proceeding with order creation",
            extra={
                "service_name": "order-service",
                "user_id": order.user_id,
            }
        )

        # Create order in database
        response = self._repository.create_order(order)

        # Publish domain event (fire-and-forget — does not block HTTP response)
        if self._event_publisher:
            asyncio.create_task(self._event_publisher.publish_order_created(
                order_id=response.order_id,
                user_id=response.user_id,
                product_id=response.product_id,
                quantity=response.quantity,
                status=response.status,
            ))
            logger.info(
                "Scheduled order.created event",
                extra={"service_name": "order-service", "order_id": response.order_id}
            )

        return response

    def get_order_by_id(self, order_id: int) -> Optional[OrderResponse]:
        """
        Retrieve an order by its ID.
        
        Args:
            order_id: The ID of the order to retrieve
            
        Returns:
            OrderResponse if order exists, None otherwise
            
        Raises:
            psycopg2.Error: If database operation fails
        """
        return self._repository.get_order_by_id(order_id)

