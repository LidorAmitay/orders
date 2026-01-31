from fastapi.testclient import TestClient
from unittest.mock import Mock
from datetime import datetime, UTC

from main import app
from models.user import UserInDB
from services.user_service import UserAlreadyExistsError
from routes.users import get_user_service


def override_user_service_success():
    mock = Mock()

    user = UserInDB(
        id=1,
        email="test@example.com",
        name="John Doe",
        created_at=datetime.now(UTC),
    )

    mock.create_user.return_value = user
    mock.get_user_by_id.return_value = user

    return mock


app.dependency_overrides[get_user_service] = override_user_service_success

client = TestClient(app)


def test_get_user_success():
    response = client.get("/api/v1/users/1")

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def override_user_service_conflict():
    mock = Mock()
    mock.create_user.side_effect = UserAlreadyExistsError("exists")
    return mock


def test_create_user_conflict():
    app.dependency_overrides[get_user_service] = override_user_service_conflict

    response = client.post(
        "/api/v1/users",
        json={"email": "test@example.com", "name": "John"},
    )

    assert response.status_code == 409


def test_get_user_success():
    response = client.get("/api/v1/users/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def override_user_service_not_found():
    mock = Mock()
    mock.get_user_by_id.return_value = None
    return mock


def test_get_user_not_found():
    app.dependency_overrides[get_user_service] = override_user_service_not_found

    response = client.get("/api/v1/users/999")

    assert response.status_code == 404
