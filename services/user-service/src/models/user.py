from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """
    Core User domain model.

    Contains fields shared across all user representations.
    Free of database and HTTP concerns.
    """

    email: EmailStr
    name: str


class UserCreate(UserBase):
    """
    Input model for creating a new user.
    """

    pass


class UserInDB(UserBase):
    """
    User model representing a persisted user entity.
    """

    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
