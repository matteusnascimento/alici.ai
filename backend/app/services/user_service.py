from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserUpdateRequest


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def update_me(self, user: User, payload: UserUpdateRequest) -> User:
        update_data = payload.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] != user.email:
            conflict = self.db.query(User).filter(User.email == update_data["email"], User.id != user.id).first()
            if conflict:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

        if "username" in update_data and update_data["username"] != user.username:
            conflict = self.db.query(User).filter(User.username == update_data["username"], User.id != user.id).first()
            if conflict:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already in use")

        for key, value in update_data.items():
            setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user
