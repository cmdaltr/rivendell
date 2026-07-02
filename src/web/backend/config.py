"""
Web Backend Configuration

Configuration settings for the elrond web interface backend.
"""

import platform
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "elrond Web Interface"
    app_version: str = "2.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5687",
        "http://127.0.0.1:5687",
        "http://localhost:5688",
        "http://127.0.0.1:5688",
    ]

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    # Database
    database_url: str = "postgresql://rivendell:rivendell@postgres:5432/rivendell"

    # Storage
    upload_dir: Path = Path("/tmp/elrond/uploads")
    output_dir: Path = Path("/tmp/elrond/output")
    max_upload_size: int = 100 * 1024 * 1024 * 1024  # 100GB

    # JWT Authentication
    # CRITICAL: Change this in production! Use a cryptographically secure random string
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_days: int = 30

    # Security settings
    # Enable these in production
    enable_https_only: bool = False  # Set to True in production
    enable_rate_limiting: bool = False  # TODO: Implement rate limiting
    max_login_attempts: int = 5  # Account lockout threshold
    lockout_duration_minutes: int = 15  # How long accounts are locked after max attempts

    # Session
    session_timeout: int = 3600  # 1 hour

    # Default Admin
    default_admin_email: str = "admin@rivendell.app"
    default_admin_password: str = "IWasThere3000YearsAgo!"

    # Guest Mode
    guest_session_timeout: int = 3600  # 1 hour

    # Analysis
    max_concurrent_analyses: int = 3
    analysis_timeout: int = 86400  # 24 hours

    @property
    def allowed_paths(self) -> list:
        """Get OS-specific allowed directories for file browsing."""
        system = platform.system()

        if system == "Windows":
            # Windows paths only
            return [
                "C:\\Temp\\rivendell",
                "D:\\Temp\\rivendell",
                "E:\\Temp\\rivendell",
                "F:\\Temp\\rivendell",
            ]
        elif system == "Darwin":
            # macOS paths
            return [
                "/Volumes",
                "/tmp/rivendell",
            ]
        else:
            # Linux/Unix paths (includes Docker containers)
            return [
                "/Volumes",  # Docker on macOS - external drives
                "/mnt",
                "/media",
                "/tmp/rivendell",
                "/host/tmp/rivendell",  # Docker on macOS - host /tmp access
            ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Create necessary directories
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.output_dir.mkdir(parents=True, exist_ok=True)
