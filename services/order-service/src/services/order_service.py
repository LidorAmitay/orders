"""
Service layer for order business logic.

This layer acts as an intermediary between the API routes and the repository layer,
providing a place for business logic and orchestration.
"""
from typing import Optional

from src.models.order import OrderCreate, OrderResponse
from src.repository.orders_repository import create_order, get_order_by_id


def create_order_service(order: OrderCreate) -> OrderResponse:
    """
    Create a new order.
    
    Args:
        order: OrderCreate model with order data
        
    Returns:
        OrderResponse: Created order with generated ID and timestamps
        
    Raises:
        psycopg2.Error: If database operation fails
        ValueError: If order data is invalid
    """
    return create_order(order)


def get_order_service(order_id: int) -> Optional[OrderResponse]:
    """
    Retrieve an order by its ID.
    
    Args:
        order_id: The ID of the order to retrieve
        
    Returns:
        OrderResponse if order exists, None otherwise
        
    Raises:
        psycopg2.Error: If database operation fails
    """
    return get_order_by_id(order_id)

