"""
Repository for order database operations.

Handles all database interactions for orders with proper transaction management,
error handling, and logging.
"""
import logging
from typing import Optional

import psycopg2
from psycopg2 import errors

from src.config.database import get_connection
from src.models.order import OrderCreate, OrderInDB, OrderResponse

logger = logging.getLogger(__name__)


def create_order(order: OrderCreate) -> OrderResponse:
    """
    Create a new order in the database.
    
    Args:
        order: OrderCreate model with order data
        
    Returns:
        OrderResponse: Created order with generated ID and timestamps
        
    Raises:
        psycopg2.Error: If database operation fails
        ValueError: If order data is invalid
    """
    logger.debug(
        f"Creating new order",
        extra={
            "service_name": "order-service",
            "user_id": order.user_id,
            "product_id": order.product_id,
            "quantity": order.quantity,
        }
    )
    
    with get_connection() as conn:
        try:
            with conn.cursor() as cur:
                # Use RETURNING clause to get the inserted row
                insert_query = """
                    INSERT INTO orders (user_id, product_id, quantity, status)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, user_id, product_id, quantity, status, created_at
                """
                
                cur.execute(
                    insert_query,
                    (order.user_id, order.product_id, order.quantity, "created")
                )
                
                # Fetch the returned row
                row = cur.fetchone()
                
                if not row:
                    raise ValueError("Failed to create order - no row returned")
                
                # Map database row to OrderInDB
                order_in_db = OrderInDB(
                    id=row[0],
                    user_id=row[1],
                    product_id=row[2],
                    quantity=row[3],
                    status=row[4],
                    created_at=row[5],
                )
                
                # Commit transaction
                conn.commit()
                
                logger.info(
                    f"Created new order",
                    extra={
                        "service_name": "order-service",
                        "order_id": order_in_db.id,
                        "user_id": order_in_db.user_id,
                        "product_id": order_in_db.product_id,
                        "quantity": order_in_db.quantity,
                    }
                )
                
                # Convert to response model
                return OrderResponse.from_order_in_db(order_in_db)
                
        except errors.UniqueViolation as e:
            conn.rollback()
            logger.error(
                f"Unique constraint violation while creating order: {e}",
                extra={
                    "service_name": "order-service",
                    "user_id": order.user_id,
                    "product_id": order.product_id,
                },
                exc_info=True
            )
            raise ValueError(f"Order violates unique constraint: {e}") from e
            
        except errors.ForeignKeyViolation as e:
            conn.rollback()
            logger.error(
                f"Foreign key violation while creating order: {e}",
                extra={
                    "service_name": "order-service",
                    "user_id": order.user_id,
                    "product_id": order.product_id,
                },
                exc_info=True
            )
            raise ValueError(f"Invalid foreign key reference: {e}") from e
            
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(
                f"Database error while creating order: {e}",
                extra={
                    "service_name": "order-service",
                    "user_id": order.user_id,
                    "product_id": order.product_id,
                },
                exc_info=True
            )
            raise
            
        except Exception as e:
            conn.rollback()
            logger.error(
                f"Unexpected error while creating order: {e}",
                extra={
                    "service_name": "order-service",
                    "user_id": order.user_id,
                    "product_id": order.product_id,
                },
                exc_info=True
            )
            raise


def get_order_by_id(order_id: int) -> Optional[OrderResponse]:
    """
    Retrieve an order by its ID.
    
    Args:
        order_id: The ID of the order to retrieve
        
    Returns:
        OrderResponse if order exists, None otherwise
        
    Raises:
        psycopg2.Error: If database operation fails
    """
    logger.debug(
        f"Retrieving order by ID",
        extra={
            "service_name": "order-service",
            "order_id": order_id,
        }
    )
    
    with get_connection() as conn:
        try:
            with conn.cursor() as cur:
                select_query = """
                    SELECT id, user_id, product_id, quantity, status, created_at
                    FROM orders
                    WHERE id = %s
                """
                
                cur.execute(select_query, (order_id,))
                row = cur.fetchone()
                
                if not row:
                    logger.debug(
                        f"Order not found",
                        extra={
                            "service_name": "order-service",
                            "order_id": order_id,
                        }
                    )
                    return None
                
                # Map database row to OrderInDB
                order_in_db = OrderInDB(
                    id=row[0],
                    user_id=row[1],
                    product_id=row[2],
                    quantity=row[3],
                    status=row[4],
                    created_at=row[5],
                )
                
                logger.debug(
                    f"Retrieved order successfully",
                    extra={
                        "service_name": "order-service",
                        "order_id": order_id,
                    }
                )
                
                # Convert to response model
                return OrderResponse.from_order_in_db(order_in_db)
                
        except psycopg2.Error as e:
            logger.error(
                f"Database error while retrieving order: {e}",
                extra={
                    "service_name": "order-service",
                    "order_id": order_id,
                },
                exc_info=True
            )
            raise
            
        except Exception as e:
            logger.error(
                f"Unexpected error while retrieving order: {e}",
                extra={
                    "service_name": "order-service",
                    "order_id": order_id,
                },
                exc_info=True
            )
            raise

