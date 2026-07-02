"""
Authentication Module

Handles user authentication, authorization, and security.
"""

from .security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    generate_password_reset_token,
)

# Disabled - requires database
# from .dependencies import (
#     get_current_user,
#     require_auth,
#     require_admin,
#     get_user_or_guest,
# )

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "verify_token",
    "generate_password_reset_token",
]
