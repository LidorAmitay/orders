"""
Pydantic models for Order domain.

Model hierarchy:
- OrderBase: Common fields shared across models
- OrderCreate: Input model for creating orders
- OrderInDB: Full model representing database row
- OrderResponse: Output model for API responses
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OrderBase(BaseModel):
    """Base order model with common fields."""
    
    user_id: int = Field(..., gt=0, description="User ID who placed the order")
    product_id: int = Field(..., gt=0, description="Product ID being ordered")
    quantity: int = Field(..., gt=0, description="Quantity of the product")


class OrderCreate(OrderBase):
    """Model for creating a new order (input validation)."""
    pass


class OrderInDB(OrderBase):
    """Full order model representing a database row."""
    
    id: int = Field(..., description="Order ID (primary key)")
    status: str = Field(default="created", description="Order status")
    created_at: datetime = Field(..., description="Timestamp when order was created")
    
    class Config:
        from_attributes = True  # Pydantic v2 - allows ORM mode for DB row mapping


class OrderResponse(BaseModel):
    """Model for API responses (what gets returned to clients)."""
    
    order_id: int = Field(..., description="Order ID")
    user_id: int = Field(..., description="User ID who placed the order")
    product_id: int = Field(..., description="Product ID being ordered")
    quantity: int = Field(..., description="Quantity of the product")
    status: str = Field(..., description="Order status")
    created_at: datetime = Field(..., description="Timestamp when order was created")
    
    @classmethod
    def from_order_in_db(cls, order: OrderInDB) -> "OrderResponse":
        """Convert OrderInDB to OrderResponse."""
        return cls(
            order_id=order.id,
            user_id=order.user_id,
            product_id=order.product_id,
            quantity=order.quantity,
            status=order.status,
            created_at=order.created_at,
        )

