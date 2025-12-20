from fastapi import APIRouter, Depends, HTTPException, status

from src.models.user import UserCreate, UserInDB
from src.services.user_service import UserService, UserAlreadyExistsError
from src.repository.user_repository import UserRepository

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
)


# ---------- Dependencies ----------

def get_user_repository() -> UserRepository:
    return UserRepository()


def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)


# ---------- Routes ----------

@router.post(
    "",
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserInDB:
    """
    Create a new user.
    """
    try:
        return service.create_user(user)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get(
    "/{user_id}",
    response_model=UserInDB,
)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserInDB:
    """
    Get user by ID.
    """
    user = service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
