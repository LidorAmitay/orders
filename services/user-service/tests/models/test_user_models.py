import pytest
from datetime import datetime

from pydantic import ValidationError

from models.user import UserBase, UserCreate, UserInDB


# ---------- UserCreate / UserBase ----------

def test_user_create_valid():
    user = UserCreate(
        email="test@example.com",
        name="John Doe"
    )

    assert user.email == "test@example.com"
    assert user.name == "John Doe"


def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            email="not-an-email",
            name="John Doe"
        )


def test_user_create_missing_required_field():
    with pytest.raises(ValidationError):
        UserCreate(
            email="test@example.com"
        )


# ---------- Type validation ----------

def test_user_in_db_invalid_id_type():
    with pytest.raises(ValidationError):
        UserInDB(
            id="abc",
            email="test@example.com",
            name="John Doe",
            created_at=datetime.utcnow()
        )


# ---------- from_attributes mapping ----------

class FakeDBRow:
    def __init__(self):
        self.id = 1
        self.email = "test@example.com"
        self.name = "John Doe"
        self.created_at = datetime.utcnow()


def test_user_in_db_from_attributes():
    row = FakeDBRow()

    user = UserInDB.model_validate(row)

    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.name == "John Doe"


# ---------- Serialization ----------

def test_user_in_db_serialization():
    user = UserInDB(
        id=1,
        email="test@example.com",
        name="John Doe",
        created_at=datetime(2024, 1, 1)
    )

    data = user.model_dump()

    assert data["id"] == 1
    assert data["email"] == "test@example.com"
    assert data["name"] == "John Doe"
    assert "created_at" in data
