import requests
from requests import Response


class UserNotFoundError(Exception):
    pass


class UserServiceUnavailableError(Exception):
    pass


class UserClient:
    """
    HTTP client for communicating with User Service.
    """

    def __init__(self, base_url: str, timeout: float = 2.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_user(self, user_id: int) -> None:
        """
        Validate that a user exists.

        Raises:
            UserNotFoundError
            UserServiceUnavailableError
        """
        url = f"{self.base_url}/api/v1/users/{user_id}"

        try:
            response: Response = requests.get(url, timeout=self.timeout)
        except requests.RequestException as e:
            raise UserServiceUnavailableError(
                "User service is unavailable"
            ) from e

        if response.status_code == 404:
            raise UserNotFoundError(f"User {user_id} not found")

        if response.status_code != 200:
            raise UserServiceUnavailableError(
                f"Unexpected response from user service: {response.status_code}"
            )

        # We don't care about the body here — existence is enough
        return None
