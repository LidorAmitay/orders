"""
Shared fixtures for Order Service tests.

This module provides reusable fixtures for test isolation and test data setup.
"""
import pytest
import psycopg2
from psycopg2.extensions import connection
from typing import Generator
from src.config.settings import settings


@pytest.fixture(scope="session")
def db_config():
    """
    Database configuration for tests.

    Returns configuration dict with database connection parameters.
    """
    return {
        "host": settings.db_host,
        "port": settings.db_port,
        "database": settings.db_name,
        "user": settings.db_user,
        "password": settings.db_password,
    }


@pytest.fixture
def db_connection(db_config) -> Generator[connection, None, None]:
    """
    Provide a database connection with transaction rollback for test isolation.

    Each test gets a fresh transaction that is rolled back after the test,
    ensuring no test data persists to the database.

    Yields:
        psycopg2 connection object in transaction mode
    """
    conn = psycopg2.connect(**db_config)
    conn.autocommit = False  # Ensure we're in a transaction

    try:
        yield conn
    finally:
        # Rollback any changes made during the test
        conn.rollback()
        conn.close()


@pytest.fixture
def test_users(db_config):
    """
    Seed test users for integration tests.

    Creates users with known IDs (1, 2, 3) for predictable testing.
    Users are explicitly cleaned up after the test.

    Args:
        db_config: Database configuration fixture

    Yields:
        list of tuples: (user_id, email, name)
    """
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    users = [
        (1, "user1@example.com", "User One"),
        (2, "user2@example.com", "User Two"),
        (3, "user3@example.com", "User Three"),
    ]

    # Clean up any existing test users first
    for user_id, _, _ in users:
        cursor.execute("DELETE FROM orders WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

    # Insert test users
    for user_id, email, name in users:
        cursor.execute(
            "INSERT INTO users (id, email, name) VALUES (%s, %s, %s)",
            (user_id, email, name)
        )

    conn.commit()

    yield users

    # Cleanup after test
    for user_id, _, _ in users:
        cursor.execute("DELETE FROM orders WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

    conn.commit()
    cursor.close()
    conn.close()
