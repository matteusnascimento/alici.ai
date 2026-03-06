"""
Authentication service for multi-tenant platform
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_token_type
)
from app.core.config import settings
from app.models import User, Organization, APIKey
from app.core.database import SessionLocal, get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class AuthService:
    """Authentication service with multi-tenant support"""

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: str,
        full_name: str,
        organization_name: str = None
    ) -> User:
        """Create a new user and organization"""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create organization if not provided
        if not organization_name:
            organization_name = f"{full_name}'s Organization"

        organization = Organization(
            id=str(uuid.uuid4()),
            name=organization_name,
            slug=organization_name.lower().replace(" ", "-").replace("'", "")
        )
        db.add(organization)

        # Create user
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            organization_id=organization.id
        )
        db.add(user)

        # Create default agent for organization
        from app.models import Agent
        default_agent = Agent(
            id=str(uuid.uuid4()),
            name="ALICI Assistant",
            description="AI assistant for general tasks",
            system_prompt="You are ALICI, an intelligent AI assistant. Help users with their tasks.",
            organization_id=organization.id
        )
        db.add(default_agent)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def create_access_token_for_user(user: User) -> str:
        """Create access token for user"""
        return create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "organization_id": user.organization_id
            }
        )

    @staticmethod
    def create_refresh_token_for_user(user: User) -> str:
        """Create refresh token for user"""
        return create_refresh_token(
            data={
                "sub": user.id,
                "email": user.email,
                "organization_id": user.organization_id
            }
        )

    @staticmethod
    def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify access token and return payload"""
        payload = verify_token(token)
        if not payload or get_token_type(token) != "access":
            return None
        return payload

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify refresh token and return payload"""
        payload = verify_token(token)
        if not payload or get_token_type(token) != "refresh":
            return None
        return payload

    @staticmethod
    def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ) -> User:
        """Get current user from bearer token (FastAPI dependency)."""
        payload = AuthService.verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[str]:
        """Create new access token from refresh token"""
        payload = AuthService.verify_refresh_token(refresh_token)
        if not payload:
            return None

        # Create new access token
        return create_access_token(
            data={
                "sub": payload["sub"],
                "email": payload["email"],
                "organization_id": payload["organization_id"]
            }
        )

    @staticmethod
    def create_api_key(
        db: Session,
        organization_id: str,
        name: str,
        permissions: Dict[str, bool] = None
    ) -> APIKey:
        """Create API key for organization"""
        if permissions is None:
            permissions = {"can_chat": True, "can_generate": True}

        api_key = APIKey(
            id=str(uuid.uuid4()),
            key=f"alici_{uuid.uuid4().hex}",
            name=name,
            organization_id=organization_id,
            can_chat=permissions.get("can_chat", True),
            can_generate=permissions.get("can_generate", True)
        )
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        return api_key

    @staticmethod
    def verify_api_key(db: Session, api_key: str) -> Optional[Organization]:
        """Verify API key and return organization"""
        key_record = db.query(APIKey).filter(
            APIKey.key == api_key,
            APIKey.is_active == True
        ).first()

        if not key_record:
            return None

        # Update last used
        key_record.last_used_at = datetime.utcnow()
        key_record.total_requests += 1
        db.commit()

        return key_record.organization