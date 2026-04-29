"""Authentication service for JWT token management."""
import logging
from datetime import datetime, timedelta
from typing import Optional

import jwt

from app.config import settings

logger = logging.getLogger(__name__)

TOKEN_EXPIRATION_HOURS = 24


def create_token(user_id: str, expires_in_hours: int = TOKEN_EXPIRATION_HOURS) -> str:
    """
    Create a JWT token for a user.
    
    Args:
        user_id: The user's unique identifier
        expires_in_hours: Token expiration time in hours
    
    Returns:
        Encoded JWT token string
    """
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=expires_in_hours),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    logger.info(f"Token created for user: {user_id}")
    return token


def verify_token(token: str) -> dict:
    """
    Verify a JWT token and return its payload.
    
    Args:
        token: The JWT token string
    
    Returns:
        Token payload as a dictionary
    
    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        logger.info(f"Token verified for user: {payload.get('sub')}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token verification failed: expired")
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token verification failed: {e}")
        raise ValueError(f"Invalid token: {e}")


def refresh_token(token: str) -> str:
    """
    Refresh a token if it's still valid.
    
    Args:
        token: The current JWT token
    
    Returns:
        New JWT token
    
    Raises:
        ValueError: If token is invalid or expired
    """
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise ValueError("Token missing user ID")
    
    # Create a new token
    new_token = create_token(user_id)
    logger.info(f"Token refreshed for user: {user_id}")
    return new_token


def get_user_from_token(token: str) -> Optional[str]:
    """
    Extract the user ID from a token.
    
    Args:
        token: The JWT token string
    
    Returns:
        User ID or None if token is invalid
    """
    try:
        payload = verify_token(token)
        return payload.get("sub")
    except ValueError:
        return None
