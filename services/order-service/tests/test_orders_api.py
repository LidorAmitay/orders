"""
Tests for the orders API endpoints (CRUD operations).
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_create_order():
    """Test creating a new order via POST /api/v1/orders."""
    order_data = {
        "user_id": 1,
        "product_id": 100,
        "quantity": 2
    }
    
    response = client.post("/api/v1/orders", json=order_data)
    
    assert response.status_code == 201
    assert response.headers["content-type"] == "application/json"
    
    data = response.json()
    assert "order_id" in data
    assert data["user_id"] == order_data["user_id"]
    assert data["product_id"] == order_data["product_id"]
    assert data["quantity"] == order_data["quantity"]
    assert data["status"] == "created"
    assert "created_at" in data
    
    # Store order_id for subsequent tests
    return data["order_id"]


def test_get_order_by_id():
    """Test retrieving an order by ID via GET /api/v1/orders/{id}."""
    # First create an order
    order_data = {
        "user_id": 2,
        "product_id": 200,
        "quantity": 3
    }
    
    create_response = client.post("/api/v1/orders", json=order_data)
    assert create_response.status_code == 201
    order_id = create_response.json()["order_id"]
    
    # Then retrieve it
    response = client.get(f"/api/v1/orders/{order_id}")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    data = response.json()
    assert data["order_id"] == order_id
    assert data["user_id"] == order_data["user_id"]
    assert data["product_id"] == order_data["product_id"]
    assert data["quantity"] == order_data["quantity"]
    assert data["status"] == "created"
    assert "created_at" in data


def test_get_order_not_found():
    """Test retrieving a non-existent order returns 404."""
    non_existent_id = 99999
    response = client.get(f"/api/v1/orders/{non_existent_id}")
    
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"
    
    data = response.json()
    assert "detail" in data
    assert str(non_existent_id) in data["detail"]


def test_create_order_invalid_data():
    """Test creating an order with invalid data returns 422."""
    # Missing required fields
    invalid_data = {
        "user_id": 1
        # Missing product_id and quantity
    }
    
    response = client.post("/api/v1/orders", json=invalid_data)
    
    assert response.status_code == 422  # Validation error


def test_create_order_negative_values():
    """Test creating an order with negative values returns 422."""
    invalid_data = {
        "user_id": -1,
        "product_id": 100,
        "quantity": 2
    }
    
    response = client.post("/api/v1/orders", json=invalid_data)
    
    assert response.status_code == 422  # Validation error


def test_crud_flow():
    """Test complete CRUD flow: create and retrieve order."""
    # Create order
    order_data = {
        "user_id": 3,
        "product_id": 300,
        "quantity": 5
    }
    
    create_response = client.post("/api/v1/orders", json=order_data)
    assert create_response.status_code == 201
    created_order = create_response.json()
    order_id = created_order["order_id"]
    
    # Verify created order fields
    assert created_order["user_id"] == order_data["user_id"]
    assert created_order["product_id"] == order_data["product_id"]
    assert created_order["quantity"] == order_data["quantity"]
    assert created_order["status"] == "created"
    assert "created_at" in created_order
    
    # Retrieve order
    get_response = client.get(f"/api/v1/orders/{order_id}")
    assert get_response.status_code == 200
    retrieved_order = get_response.json()
    
    # Verify retrieved order matches created order
    assert retrieved_order["order_id"] == created_order["order_id"]
    assert retrieved_order["user_id"] == created_order["user_id"]
    assert retrieved_order["product_id"] == created_order["product_id"]
    assert retrieved_order["quantity"] == created_order["quantity"]
    assert retrieved_order["status"] == created_order["status"]
    assert retrieved_order["created_at"] == created_order["created_at"]

