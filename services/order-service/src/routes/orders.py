"""
REST API routes for order operations.

This module defines the HTTP endpoints for creating and retrieving orders.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from src.models.order import OrderCreate, OrderResponse
from src.services.order_service import OrderService
from src.repository.orders_repository import OrdersRepository

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


# ---------- Dependencies ----------

def get_orders_repository() -> OrdersRepository:
    return OrdersRepository()


def get_order_service(
    repo: OrdersRepository = Depends(get_orders_repository),
) -> OrderService:
    return OrderService(repo)


# ---------- Routes ----------

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order_endpoint(
    order: OrderCreate,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Create a new order.
    
    Args:
        order: OrderCreate model with order data (user_id, product_id, quantity)
        
    Returns:
        OrderResponse: Created order with generated ID and timestamps
        
    Raises:
        HTTPException: If order creation fails
    """
    try:
        return service.create_order(order)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )


@router.get("/{id}", response_model=OrderResponse)
async def get_order_endpoint(
    id: int,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Retrieve an order by its ID.
    
    Args:
        id: The ID of the order to retrieve
        
    Returns:
        OrderResponse: Order data
        
    Raises:
        HTTPException: 404 if order not found, 500 if database error occurs
    """
    try:
        order = service.get_order_by_id(id)
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {id} not found"
            )
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve order: {str(e)}"
        )

