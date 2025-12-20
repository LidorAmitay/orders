from typing import Optional

from src.models.user import UserCreate, UserInDB
from src.config.database import get_connection


class UserRepository:
    """
    Repository responsible for all user persistence operations.
    """

    def create_user(self, user: UserCreate) -> UserInDB:
        query = """
        INSERT INTO users (email, name)
        VALUES (%s, %s)
        RETURNING id, email, name, created_at;
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user.email, user.name))
                row = cur.fetchone()

        return UserInDB.model_validate(row)

    def get_user_by_id(self, user_id: int) -> Optional[UserInDB]:
        query = """
        SELECT id, email, name, created_at
        FROM users
        WHERE id = %s;
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                row = cur.fetchone()

        if row is None:
            return None

        return UserInDB.model_validate(row)

    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        query = """
        SELECT id, email, name, created_at
        FROM users
        WHERE email = %s;
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (email,))
                row = cur.fetchone()

        if row is None:
            return None

        return UserInDB.model_validate(row)
