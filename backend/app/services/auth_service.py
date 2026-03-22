from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.subscription import Subscription
from app.models.setting import UserSettings
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, payload: RegisterRequest) -> tuple[str, User]:
        existing_user = self.db.query(User).filter((User.email == payload.email) | (User.username == payload.username)).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already in use")

        user = User(
            name=payload.name,
            username=payload.username,
            email=payload.email,
            phone=payload.phone,
            password_hash=get_password_hash(payload.password),
            plan="free",
        )
        self.db.add(user)
        self.db.flush()

        defaults = UserSettings(user_id=user.id)
        self.db.add(defaults)
        self.db.add(
            Subscription(
                user_id=user.id,
                plan_id="free",
                status="active",
                monthly_price=0.0,
                yearly_price=0.0,
                billing_cycle="monthly",
            )
        )
        self.db.commit()
        self.db.refresh(user)
        token = create_access_token(str(user.id))
        return token, user

    def login(self, payload: LoginRequest) -> tuple[str, User]:
        user = self.db.query(User).filter(User.email == payload.email).first()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = create_access_token(str(user.id))
        return token, user
