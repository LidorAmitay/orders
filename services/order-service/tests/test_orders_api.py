import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_create_order(client):
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


def test_get_order_by_id(client):
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


def test_get_order_not_found(client):
    response = client.get("/api/v1/orders/99999")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_create_order_invalid_data(client):
    invalid_data = {"user_id": 1}

    response = client.post("/api/v1/orders", json=invalid_data)

    assert response.status_code == 422


def test_create_order_negative_values(client):
    invalid_data = {"user_id": -1, "product_id": 100, "quantity": 2}

    response = client.post("/api/v1/orders", json=invalid_data)

    assert response.status_code == 422


def test_crud_flow(client):
    order_data = {"user_id": 3, "product_id": 300, "quantity": 5}

    create_response = client.post("/api/v1/orders", json=order_data)
    assert create_response.status_code == 201
    created = create_response.json()

    order_id = created["order_id"]

    get_response = client.get(f"/api/v1/orders/{order_id}")
    assert get_response.status_code == 200

    retrieved = get_response.json()
    assert retrieved == created
