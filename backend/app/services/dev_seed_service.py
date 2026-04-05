from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.setting import UserSettings
from app.models.subscription import Subscription
from app.models.user import User


class DevSeedService:
    def __init__(self, db: Session):
        self.db = db

    def ensure_local_dev_user(self) -> User | None:
        if not self._should_seed_dev_user():
            return None

        user = (
            self.db.query(User)
            .filter((User.email == settings.dev_seed_email) | (User.username == settings.dev_seed_username))
            .first()
        )
        if not user:
            user = User(
                name=settings.dev_seed_name,
                username=settings.dev_seed_username,
                email=settings.dev_seed_email,
                phone=settings.dev_seed_phone,
                password_hash=get_password_hash(settings.dev_seed_password),
                plan="free",
            )
            self.db.add(user)
            self.db.flush()
            self.db.add(UserSettings(user_id=user.id))
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
        else:
            user.name = settings.dev_seed_name
            user.username = settings.dev_seed_username
            user.email = settings.dev_seed_email
            user.phone = settings.dev_seed_phone
            user.password_hash = get_password_hash(settings.dev_seed_password)
            user.plan = "free"

        self.db.commit()
        self.db.refresh(user)
        return user

    def _should_seed_dev_user(self) -> bool:
        return settings.should_seed_dev_user
