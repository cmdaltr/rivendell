# Rivendell Web Interface - Implementation Guide

## Overview
This guide provides detailed implementation steps for the following features:
1. Export/Import functionality for settings, jobs, and accounts
2. Authentication system with login, registration, and password recovery
3. Default admin credentials and guest mode
4. Job management operations (start/stop/restart)
5. Archived jobs page
6. Save job configurations as pending/queued

## Table of Contents
- [1. Database Migration](#1-database-migration)
- [2. Authentication System](#2-authentication-system)
- [3. Export/Import Functionality](#3-exportimport-functionality)
- [4. Job Management Operations](#4-job-management-operations)
- [5. Archived Jobs](#5-archived-jobs)
- [6. Save Job Configurations](#6-save-job-configurations)
- [7. Testing Strategy](#7-testing-strategy)

---

## 1. Database Migration

### 1.1 Replace File-Based Storage with PostgreSQL

**Current State:**
- Jobs are stored as JSON files in `/tmp/elrond/output/jobs/`
- No user authentication or session management
- No relational data structure

**Implementation Steps:**

#### Step 1.1: Install Database Dependencies

**File:** `requirements/base.txt`
```python
# Add to existing dependencies
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
```

#### Step 1.2: Create Database Models

**File:** `src/web/backend/models/database.py` (NEW)
```python
"""
Database Models

SQLAlchemy models for PostgreSQL database.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean,
    JSON, Text, ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class JobStatus(str, enum.Enum):
    """Job status enumeration."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime)

    # Relationships
    jobs = relationship("Job", back_populates="owner")
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    accounts = relationship("Account", back_populates="user")

    # Indexes
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
        Index('idx_user_role', 'role'),
    )


class UserSettings(Base):
    """User settings model."""
    __tablename__ = "user_settings"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    theme = Column(String(50), default="dark")
    notifications_enabled = Column(Boolean, default=True)
    auto_refresh_interval = Column(Integer, default=5000)  # milliseconds
    default_analysis_options = Column(JSON)
    custom_settings = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="settings")


class Account(Base):
    """External account/integration model (e.g., Splunk, Elastic)."""
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    account_type = Column(String(50), nullable=False)  # splunk, elastic, etc.
    name = Column(String(255), nullable=False)
    credentials = Column(JSON, nullable=False)  # Encrypted credentials
    endpoint_url = Column(String(512))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="accounts")

    # Indexes
    __table_args__ = (
        Index('idx_account_user', 'user_id'),
        Index('idx_account_type', 'account_type'),
    )


class Job(Base):
    """Analysis job model."""
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    case_number = Column(String(255), nullable=False, index=True)
    source_paths = Column(JSON, nullable=False)
    destination_path = Column(String(1024))
    options = Column(JSON, nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    progress = Column(Integer, default=0)
    log = Column(JSON, default=list)
    result = Column(JSON)
    error = Column(Text)
    celery_task_id = Column(String(255), index=True)  # For job control
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    archived_at = Column(DateTime)

    # Relationships
    owner = relationship("User", back_populates="jobs")

    # Indexes
    __table_args__ = (
        Index('idx_job_user', 'user_id'),
        Index('idx_job_status', 'status'),
        Index('idx_job_case', 'case_number'),
        Index('idx_job_created', 'created_at'),
    )


class Session(Base):
    """User session model."""
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token = Column(String(512), unique=True, nullable=False, index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(512))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_session_token', 'token'),
        Index('idx_session_user', 'user_id'),
        Index('idx_session_expires', 'expires_at'),
    )


class AuditLog(Base):
    """Audit log for tracking user actions."""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(36))
    details = Column(JSON)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Indexes
    __table_args__ = (
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_action', 'action'),
    )
```

#### Step 1.3: Create Database Connection

**File:** `src/web/backend/database.py` (NEW)
```python
"""
Database Connection

SQLAlchemy database session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from .config import settings
from .models.database import Base

# Create engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.debug,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Get database session context manager.

    Usage:
        with get_db() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_dependency():
    """
    FastAPI dependency for database session.

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db_dependency)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### Step 1.4: Update Configuration

**File:** `src/web/backend/config.py`
```python
# Add to existing Settings class:

    # Database
    database_url: str = "postgresql://rivendell:rivendell@postgres:5432/rivendell"

    # JWT Authentication
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_days: int = 30

    # Default Admin
    default_admin_email: str = "admin@rivendell.app"
    default_admin_password: str = "IWasThere3000YearsAgo!"

    # Guest Mode
    guest_session_timeout: int = 3600  # 1 hour
```

#### Step 1.5: Create Alembic Migration

**File:** `alembic.ini` (NEW - in project root)
```ini
[alembic]
script_location = src/web/backend/alembic
prepend_sys_path = .
sqlalchemy.url = postgresql://rivendell:rivendell@postgres:5432/rivendell

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

**Create migration directory:**
```bash
cd src/web/backend
alembic init alembic
```

**File:** `src/web/backend/alembic/env.py` (MODIFY)
```python
# Replace the target_metadata line with:
from src.web.backend.models.database import Base
target_metadata = Base.metadata
```

**Create initial migration:**
```bash
cd src/web/backend
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

---

## 2. Authentication System

### 2.1 Password Hashing and JWT

**File:** `src/web/backend/auth/security.py` (NEW)
```python
"""
Security Utilities

Password hashing, JWT token generation, and verification.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

from ..config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


def generate_password_reset_token() -> str:
    """Generate a secure password reset token."""
    return str(uuid.uuid4())
```

### 2.2 Authentication Dependencies

**File:** `src/web/backend/auth/dependencies.py` (NEW)
```python
"""
Authentication Dependencies

FastAPI dependencies for authentication and authorization.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_db_dependency
from ..models.database import User, Session as UserSession, UserRole
from .security import verify_token
from datetime import datetime

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Cookie(None, alias="session_token"),
    db: Session = Depends(get_db_dependency),
) -> Optional[User]:
    """
    Get current authenticated user from JWT token or session cookie.

    Returns None for guest access.
    """
    token = None

    # Try Bearer token first
    if credentials:
        token = credentials.credentials
    # Then try session cookie
    elif session_token:
        token = session_token

    if not token:
        return None

    # Verify token
    payload = verify_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    # Get user from database
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()

    # Update session last activity
    if user and session_token:
        session = db.query(UserSession).filter(
            UserSession.token == session_token,
            UserSession.is_active == True
        ).first()
        if session:
            session.last_activity = datetime.utcnow()
            db.commit()

    return user


async def require_auth(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Require authentication. Raises 401 if not authenticated.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def require_admin(
    current_user: User = Depends(require_auth)
) -> User:
    """
    Require admin role. Raises 403 if not admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


async def get_user_or_guest(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Get current user or create guest user.
    Guest users can browse but cannot save.
    """
    if current_user:
        return current_user

    # Return a guest user (not saved to database)
    return User(
        id="guest",
        email="guest@rivendell.app",
        username="guest",
        hashed_password="",
        role=UserRole.GUEST,
        is_active=True,
    )
```

### 2.3 Authentication Routes

**File:** `src/web/backend/auth/routes.py` (NEW)
```python
"""
Authentication Routes

Login, registration, password reset, and session management.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session

from ..database import get_db_dependency
from ..models.database import User, UserSettings, Session as UserSession, UserRole
from ..config import settings
from .security import hash_password, verify_password, create_access_token
from .dependencies import get_current_user, require_auth

router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

    @validator('username')
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username must be alphanumeric')
        return v

    @validator('password')
    def password_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


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
    created_at: datetime
    last_login: Optional[datetime]


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @validator('new_password')
    def password_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


# Routes
@router.post("/register", response_model=UserResponse)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db_dependency),
):
    """
    Register a new user account.
    """
    # Check if email already exists
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        username=request.username,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        role=UserRole.USER,
        is_active=True,
        created_at=datetime.utcnow(),
    )

    db.add(user)
    db.flush()

    # Create default user settings
    user_settings = UserSettings(
        id=str(uuid.uuid4()),
        user_id=user.id,
    )
    db.add(user_settings)
    db.commit()

    return user


@router.post("/login", response_model=LoginResponse)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_dependency),
):
    """
    Login with username/email and password.
    """
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.id, "role": user.role})

    # Create session
    session = UserSession(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token=access_token,
        is_active=True,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes),
        last_activity=datetime.utcnow(),
    )
    db.add(session)

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Set session cookie
    response.set_cookie(
        key="session_token",
        value=access_token,
        httponly=True,
        secure=True,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
        }
    }


@router.post("/guest")
async def login_as_guest(response: Response):
    """
    Login as guest user (limited access, no persistence).
    """
    # Create a temporary guest token
    guest_token = create_access_token(
        data={"sub": "guest", "role": UserRole.GUEST},
        expires_delta=timedelta(seconds=settings.guest_session_timeout)
    )

    response.set_cookie(
        key="session_token",
        value=guest_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.guest_session_timeout,
    )

    return {
        "access_token": guest_token,
        "token_type": "bearer",
        "user": {
            "id": "guest",
            "email": "guest@rivendell.app",
            "username": "guest",
            "role": UserRole.GUEST,
        }
    }


@router.post("/logout")
async def logout(
    response: Response,
    session_token: Optional[str] = Cookie(None, alias="session_token"),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db_dependency),
):
    """
    Logout current user.
    """
    if session_token and current_user:
        # Invalidate session
        session = db.query(UserSession).filter(
            UserSession.token == session_token,
            UserSession.user_id == current_user.id
        ).first()

        if session:
            session.is_active = False
            db.commit()

    # Clear cookie
    response.delete_cookie(key="session_token")

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(require_auth),
):
    """
    Get current authenticated user information.
    """
    return current_user


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db_dependency),
):
    """
    Request password reset. Sends email with reset token.
    """
    user = db.query(User).filter(User.email == request.email).first()

    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If the email exists, a password reset link has been sent"}

    # Generate reset token
    reset_token = str(uuid.uuid4())
    user.password_reset_token = reset_token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()

    # TODO: Send email with reset link
    # For now, just log it (in production, use email service)
    print(f"Password reset token for {user.email}: {reset_token}")

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db_dependency),
):
    """
    Reset password using reset token.
    """
    user = db.query(User).filter(
        User.password_reset_token == request.token,
        User.password_reset_expires > datetime.utcnow()
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Update password
    user.hashed_password = hash_password(request.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None

    # Invalidate all sessions
    db.query(UserSession).filter(UserSession.user_id == user.id).update(
        {"is_active": False}
    )

    db.commit()

    return {"message": "Password reset successfully"}
```

### 2.4 Create Default Admin on Startup

**File:** `src/web/backend/startup.py` (NEW)
```python
"""
Application Startup

Initialize database and create default admin user.
"""

import uuid
from sqlalchemy.orm import Session

from .database import engine, init_db
from .models.database import User, UserSettings, UserRole
from .auth.security import hash_password
from .config import settings


def create_default_admin(db: Session):
    """Create default admin user if it doesn't exist."""
    admin = db.query(User).filter(User.email == settings.default_admin_email).first()

    if not admin:
        print(f"Creating default admin user: {settings.default_admin_email}")

        admin = User(
            id=str(uuid.uuid4()),
            email=settings.default_admin_email,
            username="admin",
            hashed_password=hash_password(settings.default_admin_password),
            full_name="Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )

        db.add(admin)
        db.flush()

        # Create default settings
        admin_settings = UserSettings(
            id=str(uuid.uuid4()),
            user_id=admin.id,
        )
        db.add(admin_settings)
        db.commit()

        print("Default admin user created successfully")
    else:
        print("Default admin user already exists")


def startup():
    """Run startup tasks."""
    print("Running startup tasks...")

    # Initialize database
    print("Initializing database...")
    init_db()

    # Create default admin
    from .database import SessionLocal
    db = SessionLocal()
    try:
        create_default_admin(db)
    finally:
        db.close()

    print("Startup complete!")
```

### 2.5 Update Main Application

**File:** `src/web/backend/main.py`
```python
# Add at the top:
from .startup import startup
from .auth.routes import router as auth_router

# Add after app initialization:
@app.on_event("startup")
async def on_startup():
    """Run startup tasks."""
    startup()

# Add authentication routes:
app.include_router(auth_router)

# Update existing routes to require authentication
# Example:
@app.post("/api/jobs", response_model=Job)
async def create_job(
    job_request: JobCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """Create a new analysis job (requires authentication)."""
    # Check if guest user
    if current_user.role == UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest users cannot create jobs. Please login or register.",
        )

    # ... rest of the existing code, but add user_id:
    job = Job(
        id=job_id,
        user_id=current_user.id,  # Add this
        case_number=job_request.case_number,
        # ... rest of fields
    )
```

---

## 3. Export/Import Functionality

### 3.1 Export Data Models

**File:** `src/web/backend/models/export.py` (NEW)
```python
"""
Export/Import Models

Models for exporting and importing application data.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ExportSettings(BaseModel):
    """User settings export model."""
    theme: str
    notifications_enabled: bool
    auto_refresh_interval: int
    default_analysis_options: Optional[Dict[str, Any]]
    custom_settings: Optional[Dict[str, Any]]


class ExportAccount(BaseModel):
    """External account export model."""
    account_type: str
    name: str
    credentials: Dict[str, Any]
    endpoint_url: Optional[str]
    is_active: bool


class ExportJob(BaseModel):
    """Job export model."""
    id: str
    case_number: str
    source_paths: List[str]
    destination_path: Optional[str]
    options: Dict[str, Any]
    status: str
    progress: int
    log: List[str]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    archived_at: Optional[datetime]


class ExportData(BaseModel):
    """Complete export data model."""
    version: str = "1.0"
    exported_at: datetime
    exported_by: str
    settings: Optional[ExportSettings]
    accounts: List[ExportAccount]
    jobs: List[ExportJob]


class ImportOptions(BaseModel):
    """Import options."""
    import_settings: bool = True
    import_accounts: bool = True
    import_jobs: bool = True
    overwrite_existing: bool = False
    merge_mode: bool = True  # Merge with existing or replace
```

### 3.2 Export/Import Routes

**File:** `src/web/backend/export/routes.py` (NEW)
```python
"""
Export/Import Routes

Export and import settings, jobs, and accounts.
"""

import json
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from ..database import get_db_dependency
from ..models.database import User, UserSettings, Account, Job
from ..models.export import (
    ExportData, ExportSettings, ExportAccount, ExportJob,
    ImportOptions
)
from ..auth.dependencies import require_auth

router = APIRouter(prefix="/api/export", tags=["export"])


@router.post("/export")
async def export_data(
    job_ids: Optional[List[str]] = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """
    Export user settings, accounts, and jobs to JSON file.

    Args:
        job_ids: Optional list of specific job IDs to export. If None, exports all.
    """
    # Get user settings
    user_settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()

    export_settings = None
    if user_settings:
        export_settings = ExportSettings(
            theme=user_settings.theme,
            notifications_enabled=user_settings.notifications_enabled,
            auto_refresh_interval=user_settings.auto_refresh_interval,
            default_analysis_options=user_settings.default_analysis_options,
            custom_settings=user_settings.custom_settings,
        )

    # Get accounts
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    export_accounts = [
        ExportAccount(
            account_type=acc.account_type,
            name=acc.name,
            credentials=acc.credentials,
            endpoint_url=acc.endpoint_url,
            is_active=acc.is_active,
        )
        for acc in accounts
    ]

    # Get jobs
    if job_ids:
        jobs = db.query(Job).filter(
            Job.user_id == current_user.id,
            Job.id.in_(job_ids)
        ).all()
    else:
        jobs = db.query(Job).filter(Job.user_id == current_user.id).all()

    export_jobs = [
        ExportJob(
            id=job.id,
            case_number=job.case_number,
            source_paths=job.source_paths,
            destination_path=job.destination_path,
            options=job.options,
            status=job.status,
            progress=job.progress,
            log=job.log,
            result=job.result,
            error=job.error,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            archived_at=job.archived_at,
        )
        for job in jobs
    ]

    # Create export data
    export_data = ExportData(
        exported_at=datetime.utcnow(),
        exported_by=current_user.email,
        settings=export_settings,
        accounts=export_accounts,
        jobs=export_jobs,
    )

    # Convert to JSON
    json_data = export_data.json(indent=2)

    # Create file response
    buffer = BytesIO(json_data.encode('utf-8'))
    buffer.seek(0)

    filename = f"rivendell_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

    return StreamingResponse(
        buffer,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    options: ImportOptions = ImportOptions(),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """
    Import settings, accounts, and jobs from JSON file.
    """
    try:
        # Read and parse JSON
        contents = await file.read()
        data = json.loads(contents)
        export_data = ExportData(**data)

        imported_count = {
            "settings": 0,
            "accounts": 0,
            "jobs": 0,
        }

        # Import settings
        if options.import_settings and export_data.settings:
            user_settings = db.query(UserSettings).filter(
                UserSettings.user_id == current_user.id
            ).first()

            if user_settings:
                # Update existing
                user_settings.theme = export_data.settings.theme
                user_settings.notifications_enabled = export_data.settings.notifications_enabled
                user_settings.auto_refresh_interval = export_data.settings.auto_refresh_interval
                user_settings.default_analysis_options = export_data.settings.default_analysis_options
                user_settings.custom_settings = export_data.settings.custom_settings
                user_settings.updated_at = datetime.utcnow()
            else:
                # Create new
                user_settings = UserSettings(
                    id=str(uuid.uuid4()),
                    user_id=current_user.id,
                    **export_data.settings.dict()
                )
                db.add(user_settings)

            imported_count["settings"] = 1

        # Import accounts
        if options.import_accounts:
            for acc_data in export_data.accounts:
                # Check if account already exists
                existing = db.query(Account).filter(
                    Account.user_id == current_user.id,
                    Account.name == acc_data.name,
                    Account.account_type == acc_data.account_type
                ).first()

                if existing:
                    if options.overwrite_existing:
                        existing.credentials = acc_data.credentials
                        existing.endpoint_url = acc_data.endpoint_url
                        existing.is_active = acc_data.is_active
                        existing.updated_at = datetime.utcnow()
                        imported_count["accounts"] += 1
                elif options.merge_mode or not existing:
                    account = Account(
                        id=str(uuid.uuid4()),
                        user_id=current_user.id,
                        **acc_data.dict()
                    )
                    db.add(account)
                    imported_count["accounts"] += 1

        # Import jobs
        if options.import_jobs:
            for job_data in export_data.jobs:
                # Check if job already exists
                existing = db.query(Job).filter(
                    Job.id == job_data.id
                ).first()

                if existing:
                    if options.overwrite_existing:
                        # Update existing job
                        for key, value in job_data.dict().items():
                            if key != "id":
                                setattr(existing, key, value)
                        existing.user_id = current_user.id  # Assign to current user
                        imported_count["jobs"] += 1
                elif options.merge_mode or not existing:
                    # Create new job
                    job = Job(
                        **job_data.dict(),
                        user_id=current_user.id,
                    )
                    db.add(job)
                    imported_count["jobs"] += 1

        db.commit()

        return {
            "message": "Import completed successfully",
            "imported": imported_count,
        }

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON file"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Import failed: {str(e)}"
        )
```

---

## 4. Job Management Operations

### 4.1 Update Job Model with Celery Task ID

The Job model already has `celery_task_id` field in the database model (see section 1.2).

### 4.2 Job Control Routes

**File:** `src/web/backend/jobs/routes.py` (UPDATE existing or CREATE)
```python
"""
Job Management Routes

Create, monitor, and control analysis jobs.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from celery.result import AsyncResult

from ..database import get_db_dependency
from ..models.database import User, Job, JobStatus, UserRole
from ..models.job import JobCreate, JobUpdate, JobListResponse
from ..auth.dependencies import require_auth, get_user_or_guest
from ..tasks import start_analysis, celery_app

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/start/{job_id}")
async def start_job(
    job_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """
    Start or restart a pending/failed job.
    """
    if current_user.role == UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest users cannot start jobs",
        )

    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == JobStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail="Job is already running"
        )

    # Update job status
    job.status = JobStatus.PENDING
    job.progress = 0
    job.error = None
    job.log.append(f"[{datetime.utcnow().isoformat()}] Job (re)started by user")

    # Start Celery task
    task = start_analysis.delay(job_id)
    job.celery_task_id = task.id

    db.commit()

    return {"message": "Job started", "task_id": task.id}


@router.post("/stop/{job_id}")
async def stop_job(
    job_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """
    Stop a running job.
    """
    if current_user.role == UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest users cannot stop jobs",
        )

    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
        raise HTTPException(
            status_code=400,
            detail="Can only stop pending or running jobs"
        )

    # Revoke Celery task
    if job.celery_task_id:
        celery_app.control.revoke(job.celery_task_id, terminate=True)

    # Update job status
    job.status = JobStatus.CANCELLED
    job.completed_at = datetime.utcnow()
    job.log.append(f"[{datetime.utcnow().isoformat()}] Job stopped by user")

    db.commit()

    return {"message": "Job stopped"}


@router.post("/restart/{job_id}")
async def restart_job(
    job_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """
    Restart a completed, failed, or cancelled job.
    """
    if current_user.role == UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest users cannot restart jobs",
        )

    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Reset job state
    job.status = JobStatus.PENDING
    job.progress = 0
    job.error = None
    job.result = None
    job.started_at = None
    job.completed_at = None
    job.log.append(f"[{datetime.utcnow().isoformat()}] Job restarted by user")

    # Start new Celery task
    task = start_analysis.delay(job_id)
    job.celery_task_id = task.id

    db.commit()

    return {"message": "Job restarted", "task_id": task.id}


@router.post("/archive/{job_id}")
async def archive_job(
    job_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """
    Archive a completed or failed job.
    """
    if current_user.role == UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest users cannot archive jobs",
        )

    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
        raise HTTPException(
            status_code=400,
            detail="Cannot archive running or pending jobs"
        )

    job.status = JobStatus.ARCHIVED
    job.archived_at = datetime.utcnow()
    job.log.append(f"[{datetime.utcnow().isoformat()}] Job archived by user")

    db.commit()

    return {"message": "Job archived"}


@router.post("/unarchive/{job_id}")
async def unarchive_job(
    job_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """
    Restore an archived job.
    """
    if current_user.role == UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest users cannot unarchive jobs",
        )

    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.ARCHIVED:
        raise HTTPException(
            status_code=400,
            detail="Job is not archived"
        )

    # Restore to completed or failed based on result
    if job.error:
        job.status = JobStatus.FAILED
    else:
        job.status = JobStatus.COMPLETED

    job.archived_at = None
    job.log.append(f"[{datetime.utcnow().isoformat()}] Job restored from archive by user")

    db.commit()

    return {"message": "Job restored"}


@router.post("/bulk/archive")
async def bulk_archive_jobs(
    job_ids: List[str],
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """
    Archive multiple jobs at once.
    """
    if current_user.role == UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest users cannot archive jobs",
        )

    jobs = db.query(Job).filter(
        Job.id.in_(job_ids),
        Job.user_id == current_user.id
    ).all()

    archived_count = 0
    for job in jobs:
        if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
            job.status = JobStatus.ARCHIVED
            job.archived_at = datetime.utcnow()
            job.log.append(f"[{datetime.utcnow().isoformat()}] Job archived by user (bulk)")
            archived_count += 1

    db.commit()

    return {"message": f"Archived {archived_count} jobs"}


@router.post("/bulk/delete")
async def bulk_delete_jobs(
    job_ids: List[str],
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """
    Delete multiple jobs at once.
    """
    if current_user.role == UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest users cannot delete jobs",
        )

    # Only allow deleting non-running jobs
    deleted_count = db.query(Job).filter(
        Job.id.in_(job_ids),
        Job.user_id == current_user.id,
        Job.status.in_([JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.ARCHIVED])
    ).delete(synchronize_session=False)

    db.commit()

    return {"message": f"Deleted {deleted_count} jobs"}
```

---

## 5. Archived Jobs

### 5.1 Update Job List Routes

**File:** `src/web/backend/main.py` (UPDATE)
```python
@app.get("/api/jobs", response_model=JobListResponse)
async def list_jobs(
    status: Optional[JobStatus] = None,
    include_archived: bool = False,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Optional[User] = Depends(get_user_or_guest),
    db: Session = Depends(get_db_dependency),
):
    """
    List all analysis jobs.

    Args:
        status: Filter by job status
        include_archived: Include archived jobs in results
        limit: Maximum number of jobs to return
        offset: Offset for pagination
    """
    query = db.query(Job)

    # Filter by user (except for admins who can see all)
    if current_user.role != UserRole.ADMIN:
        if current_user.role == UserRole.GUEST:
            # Guests see no jobs
            return JobListResponse(jobs=[], total=0)
        query = query.filter(Job.user_id == current_user.id)

    # Filter by status
    if status:
        query = query.filter(Job.status == status)
    elif not include_archived:
        # By default, exclude archived jobs
        query = query.filter(Job.status != JobStatus.ARCHIVED)

    # Get total count
    total = query.count()

    # Get paginated results
    jobs = query.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()

    return JobListResponse(jobs=jobs, total=total)


@app.get("/api/jobs/archived", response_model=JobListResponse)
async def list_archived_jobs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """
    List archived jobs only.
    """
    if current_user.role == UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest users cannot view archived jobs",
        )

    query = db.query(Job).filter(Job.status == JobStatus.ARCHIVED)

    # Filter by user (except for admins)
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Job.user_id == current_user.id)

    total = query.count()
    jobs = query.order_by(Job.archived_at.desc()).offset(offset).limit(limit).all()

    return JobListResponse(jobs=jobs, total=total)
```

### 5.2 Update Archive Frontend Component

**File:** `src/web/frontend/src/components/Archive.js` (UPDATE)
```javascript
// Update loadArchivedJobs to use new endpoint:
const loadArchivedJobs = async () => {
  try {
    const data = await listArchivedJobs();  // New API call
    setJobs(data.jobs);
    setError(null);
  } catch (err) {
    setError(err.response?.data?.detail || 'Failed to load archived jobs');
  } finally {
    setLoading(false);
  }
};

// Update handleBulkRestore:
const handleBulkRestore = async () => {
  try {
    for (const jobId of selectedJobs) {
      await unarchiveJob(jobId);
    }
    setSelectedJobs([]);
    loadArchivedJobs();
  } catch (err) {
    alert(`Failed to restore jobs: ${err.message}`);
  }
};

// Update handleBulkDelete:
const handleBulkDelete = async () => {
  if (!window.confirm(`Are you sure you want to permanently delete ${selectedJobs.length} archived job(s)?`)) {
    return;
  }

  try {
    await bulkDeleteJobs(selectedJobs);
    setSelectedJobs([]);
    loadArchivedJobs();
  } catch (err) {
    alert(`Failed to delete jobs: ${err.message}`);
  }
};
```

**File:** `src/web/frontend/src/api.js` (ADD)
```javascript
export const listArchivedJobs = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/jobs/archived`);
  return response.data;
};

export const archiveJob = async (jobId) => {
  const response = await axios.post(`${API_BASE_URL}/api/jobs/archive/${jobId}`);
  return response.data;
};

export const unarchiveJob = async (jobId) => {
  const response = await axios.post(`${API_BASE_URL}/api/jobs/unarchive/${jobId}`);
  return response.data;
};

export const bulkDeleteJobs = async (jobIds) => {
  const response = await axios.post(`${API_BASE_URL}/api/jobs/bulk/delete`, jobIds);
  return response.data;
};

export const bulkArchiveJobs = async (jobIds) => {
  const response = await axios.post(`${API_BASE_URL}/api/jobs/bulk/archive`, jobIds);
  return response.data;
};

export const startJob = async (jobId) => {
  const response = await axios.post(`${API_BASE_URL}/api/jobs/start/${jobId}`);
  return response.data;
};

export const stopJob = async (jobId) => {
  const response = await axios.post(`${API_BASE_URL}/api/jobs/stop/${jobId}`);
  return response.data;
};

export const restartJob = async (jobId) => {
  const response = await axios.post(`${API_BASE_URL}/api/jobs/restart/${jobId}`);
  return response.data;
};
```

---

## 6. Save Job Configurations as Pending/Queued

### 6.1 Add "Save for Later" Option

**File:** `src/web/backend/main.py` (UPDATE create_job)
```python
@app.post("/api/jobs", response_model=Job)
async def create_job(
    job_request: JobCreate,
    start_immediately: bool = True,  # Add this parameter
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """
    Create a new analysis job.

    Args:
        job_request: Job creation request
        start_immediately: If True, start job immediately. If False, save as QUEUED.
    """
    if current_user.role == UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest users cannot create jobs. Please login or register.",
        )

    # ... existing validation code ...

    # Create job
    initial_status = JobStatus.PENDING if start_immediately else JobStatus.QUEUED

    job = Job(
        id=job_id,
        user_id=current_user.id,
        case_number=job_request.case_number,
        source_paths=job_request.source_paths,
        destination_path=destination_path,
        options=job_request.options,
        status=initial_status,
        created_at=datetime.utcnow(),
    )

    # Save job
    db.add(job)
    db.commit()

    # Start analysis task only if start_immediately is True
    if start_immediately:
        task = start_analysis.delay(job_id)
        job.celery_task_id = task.id
        db.commit()

    return job
```

### 6.2 Update Frontend to Support Queued Jobs

**File:** `src/web/frontend/src/components/NewAnalysis.js` (UPDATE)
```javascript
// Add save mode state
const [saveMode, setSaveMode] = useState('start'); // 'start' or 'queue'

// Update form submission:
const handleSubmit = async (e) => {
  e.preventDefault();

  try {
    setSubmitting(true);
    setError(null);

    const startImmediately = saveMode === 'start';

    const job = await createJob({
      case_number: caseNumber,
      source_paths: selectedFiles,
      destination_path: destinationPath,
      options: analysisOptions
    }, startImmediately);

    if (startImmediately) {
      navigate(`/jobs/${job.id}`);
    } else {
      alert('Job configuration saved! You can start it from the Jobs page.');
      navigate('/jobs');
    }
  } catch (err) {
    setError(err.response?.data?.detail || 'Failed to create job');
  } finally {
    setSubmitting(false);
  }
};

// Add save mode selector in the form:
<div className="form-group">
  <label>Save Mode</label>
  <div style={{ display: 'flex', gap: '1rem' }}>
    <label>
      <input
        type="radio"
        name="saveMode"
        value="start"
        checked={saveMode === 'start'}
        onChange={(e) => setSaveMode(e.target.value)}
      />
      Start Immediately
    </label>
    <label>
      <input
        type="radio"
        name="saveMode"
        value="queue"
        checked={saveMode === 'queue'}
        onChange={(e) => setSaveMode(e.target.value)}
      />
      Save for Later
    </label>
  </div>
</div>

// Update submit button:
<button type="submit" disabled={submitting || !isFormValid()}>
  {submitting
    ? 'Processing...'
    : saveMode === 'start'
      ? 'Create and Start Analysis'
      : 'Save Configuration'}
</button>
```

**File:** `src/web/frontend/src/api.js` (UPDATE)
```javascript
export const createJob = async (jobData, startImmediately = true) => {
  const response = await axios.post(
    `${API_BASE_URL}/api/jobs?start_immediately=${startImmediately}`,
    jobData
  );
  return response.data;
};
```

---

## 7. Testing Strategy

### 7.1 Backend Tests

**File:** `tests/backend/test_auth.py` (NEW)
```python
"""
Authentication Tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.web.backend.main import app
from src.web.backend.database import Base, get_db_dependency
from src.web.backend.models.database import User, UserRole
from src.web.backend.auth.security import hash_password

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_dependency] = override_get_db

client = TestClient(app)


def test_register():
    """Test user registration."""
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


def test_login():
    """Test user login."""
    response = client.post("/api/auth/login", data={
        "username": "admin@rivendell.app",
        "password": "IWasThere3000YearsAgo!"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_guest_access():
    """Test guest user access."""
    response = client.post("/api/auth/guest")

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "guest"
```

### 7.2 Frontend Tests

**File:** `src/web/frontend/src/__tests__/Login.test.js` (NEW)
```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from '../components/Login';
import * as api from '../api';

jest.mock('../api');

test('renders login form', () => {
  render(
    <BrowserRouter>
      <Login />
    </BrowserRouter>
  );

  expect(screen.getByLabelText(/username or email/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
});

test('handles login submission', async () => {
  api.login.mockResolvedValue({
    access_token: 'test-token',
    user: { email: 'test@example.com' }
  });

  render(
    <BrowserRouter>
      <Login />
    </BrowserRouter>
  );

  fireEvent.change(screen.getByLabelText(/username or email/i), {
    target: { value: 'test@example.com' }
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: 'password123' }
  });
  fireEvent.click(screen.getByRole('button', { name: /login/i }));

  await waitFor(() => {
    expect(api.login).toHaveBeenCalledWith('test@example.com', 'password123');
  });
});
```

### 7.3 Integration Test Plan

1. **Authentication Flow:**
   - Register new user
   - Login with credentials
   - Access protected routes
   - Guest mode access and limitations
   - Logout

2. **Job Management:**
   - Create job (start immediately)
   - Create job (save for later)
   - Start queued job
   - Stop running job
   - Restart failed job
   - Archive completed job
   - View archived jobs
   - Restore archived job
   - Bulk operations

3. **Export/Import:**
   - Export all data
   - Export selected jobs
   - Import data with merge
   - Import data with overwrite
   - Host migration scenario

---

## Implementation Checklist

### Phase 1: Database Migration
- [ ] Install database dependencies
- [ ] Create database models
- [ ] Set up database connection
- [ ] Create Alembic migrations
- [ ] Run initial migration
- [ ] Test database connectivity

### Phase 2: Authentication
- [ ] Implement password hashing
- [ ] Implement JWT token generation
- [ ] Create authentication dependencies
- [ ] Build authentication routes
- [ ] Create default admin on startup
- [ ] Test authentication flow

### Phase 3: Frontend Auth UI
- [ ] Update Login page
- [ ] Create Registration page
- [ ] Create Forgot Password page
- [ ] Add auth context/state management
- [ ] Protect routes with auth guards
- [ ] Add logout functionality

### Phase 4: Job Management
- [ ] Update Job model with Celery task ID
- [ ] Implement start/stop/restart endpoints
- [ ] Add bulk operations
- [ ] Update frontend job controls
- [ ] Test job lifecycle

### Phase 5: Archive System
- [ ] Add ARCHIVED status to JobStatus enum
- [ ] Implement archive/unarchive endpoints
- [ ] Update Archive page frontend
- [ ] Test archive operations

### Phase 6: Export/Import
- [ ] Create export models
- [ ] Implement export endpoint
- [ ] Implement import endpoint
- [ ] Add frontend export/import UI
- [ ] Test host migration scenario

### Phase 7: Save for Later
- [ ] Add QUEUED status support
- [ ] Update create_job endpoint
- [ ] Add save mode selector in frontend
- [ ] Test queued job workflow

### Phase 8: Testing
- [ ] Write backend unit tests
- [ ] Write frontend component tests
- [ ] Perform integration testing
- [ ] Security audit
- [ ] Performance testing

---

## Security Considerations

1. **Password Storage:**
   - Use bcrypt for password hashing
   - Never store plaintext passwords
   - Enforce strong password requirements

2. **JWT Tokens:**
   - Use secure secret key (change in production)
   - Set appropriate expiration times
   - Implement token refresh mechanism

3. **Session Management:**
   - Use httpOnly cookies
   - Enable secure flag in production (HTTPS)
   - Implement session timeout
   - Track session activity

4. **Guest Mode:**
   - Read-only access
   - No data persistence
   - Auto-expire sessions
   - Clear identification

5. **Export/Import:**
   - Validate file format
   - Sanitize imported data
   - Prevent injection attacks
   - Audit import operations

6. **Database:**
   - Use parameterized queries (SQLAlchemy handles this)
   - Implement row-level security
   - Regular backups
   - Encrypt sensitive data (credentials)

---

## Next Steps

After implementing these features, consider:

1. **Email Integration:**
   - Password reset emails
   - Job completion notifications
   - Account verification

2. **Advanced Permissions:**
   - Custom roles
   - Fine-grained permissions
   - Team collaboration

3. **Audit Logging:**
   - Track all user actions
   - Export audit logs
   - Security monitoring

4. **API Rate Limiting:**
   - Prevent abuse
   - Throttle requests
   - IP-based limiting

5. **Two-Factor Authentication:**
   - TOTP support
   - Backup codes
   - SMS/Email 2FA

This implementation guide provides a complete roadmap for all requested features. Each section includes detailed code examples, database schemas, API endpoints, and frontend components needed for a production-ready implementation.
