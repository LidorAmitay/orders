import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from src.main import app
from src.routes.orders import get_user_client
from src.clients.user_client import UserNotFoundError, UserServiceUnavailableError


@pytest.fixture
def mock_user_client():
    """Create a mock UserClient."""
    client = Mock()
    # By default, assume users exist (get_user returns None for success)
    client.get_user.return_value = None
    return client


@pytest.fixture
def client(mock_user_client):
    """Create TestClient with mocked UserClient dependency."""
    app.dependency_overrides[get_user_client] = lambda: mock_user_client
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.mark.unit
def test_create_order(client, mock_user_client):
    """Test creating an order with a valid user."""
    order_data = {"user_id": 1, "product_id": 100, "quantity": 2}

    response = client.post("/api/v1/orders", json=order_data)

    assert response.status_code == 201
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()
    assert data["order_id"] > 0
    assert data["user_id"] == order_data["user_id"]
    assert data["product_id"] == order_data["product_id"]
    assert data["quantity"] == order_data["quantity"]
    assert data["status"] == "created"
    assert "created_at" in data

    # Verify user validation was called
    mock_user_client.get_user.assert_called_once_with(1)


@pytest.mark.unit
def test_create_order_user_not_found(client, mock_user_client):
    """Test creating an order with a non-existent user returns 404."""
    mock_user_client.get_user.side_effect = UserNotFoundError("User 999 not found")

    order_data = {"user_id": 999, "product_id": 100, "quantity": 2}
    response = client.post("/api/v1/orders", json=order_data)

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "User not found" in data["detail"]

    # Verify user validation was called
    mock_user_client.get_user.assert_called_once_with(999)


@pytest.mark.unit
def test_create_order_user_service_unavailable(client, mock_user_client):
    """Test creating an order when user service is down returns 503."""
    mock_user_client.get_user.side_effect = UserServiceUnavailableError(
        "User service is unavailable"
    )

    order_data = {"user_id": 1, "product_id": 100, "quantity": 2}
    response = client.post("/api/v1/orders", json=order_data)

    assert response.status_code == 503
    data = response.json()
    assert "detail" in data
    assert "User service unavailable" in data["detail"]


@pytest.mark.unit
def test_get_order_by_id(client, mock_user_client):
    """Test retrieving an order by ID."""
    order_data = {"user_id": 2, "product_id": 200, "quantity": 3}

    create_response = client.post("/api/v1/orders", json=order_data)
    assert create_response.status_code == 201
    order_id = create_response.json()["order_id"]

    response = client.get(f"/api/v1/orders/{order_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert data["user_id"] == order_data["user_id"]
    assert data["product_id"] == order_data["product_id"]


@pytest.mark.unit
def test_get_order_not_found():
    """Test retrieving a non-existent order returns 404."""
    # This test doesn't need user validation, so we don't need the mock
    test_client = TestClient(app)
    response = test_client.get("/api/v1/orders/99999")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.unit
def test_create_order_invalid_data(client, mock_user_client):
    """Test creating an order with missing required fields returns 422."""
    invalid_data = {"user_id": 1}

    response = client.post("/api/v1/orders", json=invalid_data)

    assert response.status_code == 422
    # User validation should not be called for invalid input
    mock_user_client.get_user.assert_not_called()


@pytest.mark.unit
def test_create_order_negative_values(client, mock_user_client):
    """Test creating an order with negative values returns 422."""
    invalid_data = {"user_id": -1, "product_id": 100, "quantity": 2}

    response = client.post("/api/v1/orders", json=invalid_data)

    assert response.status_code == 422
    # User validation should not be called for invalid input
    mock_user_client.get_user.assert_not_called()


@pytest.mark.unit
def test_crud_flow(client, mock_user_client):
    """Test complete create-read flow for orders."""
    order_data = {"user_id": 3, "product_id": 300, "quantity": 5}

    create_response = client.post("/api/v1/orders", json=order_data)
    assert create_response.status_code == 201
    created = create_response.json()

    order_id = created["order_id"]

    get_response = client.get(f"/api/v1/orders/{order_id}")
    assert get_response.status_code == 200

    retrieved = get_response.json()
    assert retrieved == created


@pytest.mark.unit
def test_user_validation_called_before_db_insert(client, mock_user_client):
    """Test that user validation happens before database insertion."""
    # Make user validation fail
    mock_user_client.get_user.side_effect = UserNotFoundError("User 123 not found")

    order_data = {"user_id": 123, "product_id": 100, "quantity": 2}
    response = client.post("/api/v1/orders", json=order_data)

    # Should fail with 404
    assert response.status_code == 404

    # Verify the user validation was called
    mock_user_client.get_user.assert_called_once_with(123)
