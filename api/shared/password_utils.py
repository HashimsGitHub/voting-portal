"""
Password Utilities
Plaintext password storage - intentional for this single-use election so an
admin with MongoDB access can look up/restore a forgotten password directly.
"""


def hash_password(password: str) -> str:
    """No-op: passwords are stored as plaintext"""
    return password


def verify_password(password: str, stored: str) -> bool:
    """Compare a plaintext password against the stored plaintext password"""
    if not password or not stored:
        return False
    return password == stored
