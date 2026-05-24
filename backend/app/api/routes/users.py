from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import UserRead
from app.schemas.user import UserMeResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserMeResponse)
def user_me(current_user: User = Depends(get_current_user)) -> UserMeResponse:
    return UserMeResponse(
        id=current_user.id,
        name=current_user.name,
        username=current_user.username,
        email=current_user.email,
        phone=current_user.phone,
        plan=current_user.plan,
    )


@router.patch("/me", response_model=UserRead)
def user_update_me(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    updated = UserService(db).update_me(current_user, payload)
    return UserRead.model_validate(updated)
