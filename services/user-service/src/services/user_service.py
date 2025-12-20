from src.models.user import UserCreate, UserInDB
from src.repository.user_repository import UserRepository


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email."""


class UserService:
    """
    Business logic layer for user operations.
    """

    def __init__(self, repository: UserRepository):
        self._repository = repository

    def create_user(self, user: UserCreate) -> UserInDB:
        """
        Create a new user after applying business rules.
        """

        email = str(user.email)
        existing_user = self._repository.get_user_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError(
                f"User with email '{user.email}' already exists"
            )

        return self._repository.create_user(user)

    def get_user_by_id(self, user_id: int) -> UserInDB | None:
        """
        Retrieve user by ID.
        """
        return self._repository.get_user_by_id(user_id)
