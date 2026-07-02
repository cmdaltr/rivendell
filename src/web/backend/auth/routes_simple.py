"""
Simple File-Based Authentication Routes

Lightweight authentication without database dependencies.
Uses JSON file storage for users.
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

try:
    from ..config import settings
    from .security import hash_password, verify_password, create_access_token
except ImportError:
    from config import settings
    from auth.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# File-based user storage
USERS_FILE = os.environ.get("USERS_FILE", "/app/data/users.json")


def ensure_data_dir():
    """Ensure data directory exists."""
    data_dir = os.path.dirname(USERS_FILE)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)


def load_users() -> dict:
    """Load users from JSON file."""
    ensure_data_dir()
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_users(users: dict):
    """Save users to JSON file."""
    ensure_data_dir()
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2, default=str)


def init_default_admin():
    """Create default admin user if no users exist."""
    users = load_users()
    if not users:
        admin_id = str(uuid.uuid4())
        users[admin_id] = {
            "id": admin_id,
            "email": settings.default_admin_email,
            "username": "admin",
            "hashed_password": hash_password(settings.default_admin_password),
            "full_name": "Administrator",
            "role": "admin",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
        }
        save_users(users)
    return users


# Request/Response Models
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    email: str  # Email validated manually
    username: str
    password: str
    full_name: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    role: str


# Routes
@router.post("/login", response_model=LoginResponse)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Login with username/email and password (OAuth2 form data)."""
    users = init_default_admin()

    # Find user by username or email
    user = None
    for u in users.values():
        if u["username"] == form_data.username or u["email"] == form_data.username:
            user = u
            break

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # Create access token
    access_token = create_access_token(data={"sub": user["id"], "role": user["role"]})

    # Update last login
    user["last_login"] = datetime.utcnow().isoformat()
    save_users(users)

    # Set session cookie
    response.set_cookie(
        key="session_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user.get("full_name"),
            "role": user["role"],
        }
    }


@router.post("/guest", response_model=LoginResponse)
async def login_as_guest(response: Response):
    """Login as guest user (limited access)."""
    access_token = create_access_token(
        data={"sub": "guest", "role": "guest"},
        expires_delta=timedelta(seconds=settings.guest_session_timeout)
    )

    response.set_cookie(
        key="session_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.guest_session_timeout,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": "guest",
            "email": "guest@rivendell.app",
            "username": "guest",
            "full_name": "Guest User",
            "role": "guest",
        }
    }


@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest):
    """Register a new user account."""
    users = init_default_admin()

    # Check if email already exists
    for u in users.values():
        if u["email"] == request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        if u["username"] == request.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    # Create user
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": request.email,
        "username": request.username,
        "hashed_password": hash_password(request.password),
        "full_name": request.full_name,
        "role": "user",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "last_login": None,
    }

    users[user_id] = user
    save_users(users)

    return {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "full_name": user.get("full_name"),
        "role": user["role"],
    }


@router.post("/logout")
async def logout(response: Response):
    """Logout current user."""
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
async def forgot_password(email: str):
    """Request password reset (stub)."""
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}


@router.get("/me")
async def get_current_user_stub():
    """Get current user info (stub - returns guest for now)."""
    return {
        "id": "guest",
        "email": "guest@rivendell.app",
        "username": "guest",
        "full_name": "Guest User",
        "role": "guest",
    }
