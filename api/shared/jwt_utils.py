"""
JWT Utilities
Token generation and verification for authentication
"""
import os
import logging
import datetime
import jwt

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable not set")


def generate_token(user_id: str, email: str, role: str = 'voter') -> str:
    """Generate a signed JWT for an authenticated user"""
    now = datetime.datetime.utcnow()
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'iat': now,
        'exp': now + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str):
    """Verify and decode a JWT. Returns the decoded payload or None if invalid/expired."""
    if not token:
        return None
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        logger.info("Token verification failed: expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.info(f"Token verification failed: {str(e)}")
        return None


def get_user_from_token(token: str):
    """Return the user claims embedded in a valid token, or None"""
    return verify_token(token)
