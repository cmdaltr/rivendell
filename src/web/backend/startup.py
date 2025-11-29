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
        print(f"  Email: {settings.default_admin_email}")
        print(f"  Password: {settings.default_admin_password}")
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
