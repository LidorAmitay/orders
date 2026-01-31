"""
End-to-end integration tests for Order Service.

These tests use real User Service and real database to verify
complete service-to-service communication.
"""
import pytest
import requests
from fastapi.testclient import TestClient
from src.main import app
from src.config.settings import settings


@pytest.fixture
def client():
    """TestClient with NO mocked dependencies (real E2E)."""
    return TestClient(app)


@pytest.fixture
def verify_user_service_available():
    """
    Verify User Service is running before E2E tests.

    Skip E2E tests if User Service is not available.
    """
    try:
        response = requests.get(f"{settings.user_service_url}/health", timeout=2)
        if response.status_code != 200:
            pytest.skip("User Service is not available")
    except requests.RequestException:
        pytest.skip("User Service is not available")


@pytest.mark.integration
def test_create_order_with_real_user_service(client, test_users, verify_user_service_available):
    """Test creating order with real User Service validation."""
    # test_users fixture seeds users 1, 2, 3 in database
    order_data = {"user_id": 1, "product_id": 100, "quantity": 2}

    response = client.post("/api/v1/orders", json=order_data)

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == 1
    assert data["product_id"] == 100
    assert data["quantity"] == 2
    assert data["status"] == "created"
    assert "order_id" in data
    assert "created_at" in data


@pytest.mark.integration
def test_create_order_user_not_found_real_service(client, verify_user_service_available):
    """Test creating order with non-existent user fails via real User Service."""
    order_data = {"user_id": 99999, "product_id": 100, "quantity": 2}

    response = client.post("/api/v1/orders", json=order_data)

    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


@pytest.mark.integration
def test_full_order_lifecycle_e2e(client, test_users, verify_user_service_available, db_connection):
    """Test complete order lifecycle from creation to retrieval."""
    # Create order
    order_data = {"user_id": 2, "product_id": 200, "quantity": 5}
    create_response = client.post("/api/v1/orders", json=order_data)
    assert create_response.status_code == 201

    order_id = create_response.json()["order_id"]

    # Retrieve order via API
    get_response = client.get(f"/api/v1/orders/{order_id}")
    assert get_response.status_code == 200

    retrieved = get_response.json()
    created = create_response.json()
    assert retrieved == created

    # Verify in database
    cursor = db_connection.cursor()
    cursor.execute("SELECT user_id, product_id, quantity FROM orders WHERE id = %s", (order_id,))
    row = cursor.fetchone()
    assert row[0] == 2
    assert row[1] == 200
    assert row[2] == 5


@pytest.mark.integration
def test_multiple_orders_same_user_e2e(client, test_users, verify_user_service_available):
    """Test creating multiple orders for same user."""
    order1 = {"user_id": 1, "product_id": 100, "quantity": 1}
    order2 = {"user_id": 1, "product_id": 200, "quantity": 2}

    response1 = client.post("/api/v1/orders", json=order1)
    response2 = client.post("/api/v1/orders", json=order2)

    assert response1.status_code == 201
    assert response2.status_code == 201

    # Both orders should have same user_id
    assert response1.json()["user_id"] == 1
    assert response2.json()["user_id"] == 1

    # But different order IDs
    assert response1.json()["order_id"] != response2.json()["order_id"]


@pytest.mark.integration
def test_user_service_timeout_configuration(client, test_users, verify_user_service_available):
    """Test that User Service timeout is configured correctly."""
    # This test verifies the timeout setting is applied
    # We can't easily test timeout behavior without mocking,
    # but we can verify requests succeed within timeout
    order_data = {"user_id": 1, "product_id": 100, "quantity": 1}

    import time
    start = time.time()
    response = client.post("/api/v1/orders", json=order_data)
    duration = time.time() - start

    # Should complete quickly (well under timeout)
    assert duration < settings.user_service_timeout
    assert response.status_code in [201, 404]  # Either succeeds or user not found


@pytest.mark.integration
def test_order_validation_before_database_insert_e2e(client, verify_user_service_available, db_connection):
    """Test that user validation happens before database insert (E2E)."""
    # Count orders before
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    count_before = cursor.fetchone()[0]

    # Try to create order with non-existent user
    order_data = {"user_id": 88888, "product_id": 100, "quantity": 1}
    response = client.post("/api/v1/orders", json=order_data)

    assert response.status_code == 404

    # Count orders after - should be unchanged
    cursor.execute("SELECT COUNT(*) FROM orders")
    count_after = cursor.fetchone()[0]

    assert count_after == count_before, "No order should be created when user doesn't exist"
