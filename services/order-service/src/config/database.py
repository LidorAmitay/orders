"""
Database connection pool management.

Provides a connection pool and context manager for database operations.
Connections are reused from the pool, not created on-demand.
"""
import logging
from contextlib import contextmanager
from typing import Generator

from psycopg2 import pool
from psycopg2.extensions import connection

from src.config.settings import settings

logger = logging.getLogger(__name__)

# Global connection pool instance
_db_pool: pool.SimpleConnectionPool | None = None


def get_db_pool() -> pool.SimpleConnectionPool:
    """
    Get or create the database connection pool.
    
    Returns:
        SimpleConnectionPool: The database connection pool instance.
    """
    global _db_pool
    
    if _db_pool is None:
        connection_string = (
            f"postgresql://{settings.db_user}:{settings.db_password}"
            f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
        )
        
        logger.info(
            f"Initializing database connection pool",
            extra={
                "service_name": "order-service",
                "db_host": settings.db_host,
                "db_port": settings.db_port,
                "db_name": settings.db_name,
            }
        )
        
        try:
            _db_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=connection_string
            )
            
            if _db_pool:
                logger.info(
                    "Database connection pool created successfully",
                    extra={"service_name": "order-service"}
                )
            else:
                raise Exception("Failed to create connection pool")
                
        except Exception as e:
            logger.error(
                f"Failed to create database connection pool: {e}",
                extra={"service_name": "order-service"},
                exc_info=True
            )
            raise
    
    return _db_pool


@contextmanager
def get_connection() -> Generator[connection, None, None]:
    """
    Context manager for getting a database connection from the pool.
    
    Usage:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT ...")
                conn.commit()
    
    Yields:
        connection: A database connection from the pool.
    
    Raises:
        Exception: If connection cannot be obtained from pool.
    """
    pool_instance = get_db_pool()
    conn = None
    
    try:
        conn = pool_instance.getconn()
        if conn is None:
            raise Exception("Failed to get connection from pool")
        
        logger.debug(
            "Acquired database connection from pool",
            extra={"service_name": "order-service"}
        )
        
        yield conn
        
    except Exception as e:
        logger.error(
            f"Error with database connection: {e}",
            extra={"service_name": "order-service"},
            exc_info=True
        )
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            pool_instance.putconn(conn)
            logger.debug(
                "Returned database connection to pool",
                extra={"service_name": "order-service"}
            )


def close_db_pool():
    """
    Close all connections in the pool.
    Should be called during application shutdown.
    """
    global _db_pool
    
    if _db_pool:
        _db_pool.closeall()
        _db_pool = None
        logger.info(
            "Database connection pool closed",
            extra={"service_name": "order-service"}
        )

