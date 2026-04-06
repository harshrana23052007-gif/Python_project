"""
Authentication utilities for user login/signup
Handles password hashing and validation
"""

import hashlib
import secrets


def hash_password(password):
    """
    Hash a password using SHA256 with a random salt
    Returns: salt$hash format
    """
    salt = secrets.token_hex(32)  # 64-character random salt
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 100,000 iterations
    )
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password, stored_hash):
    """
    Verify a password against a stored hash
    Returns: True if password matches, False otherwise
    """
    try:
        salt, pwd_hash = stored_hash.split('$')
        pwd_check = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return pwd_check.hex() == pwd_hash
    except:
        return False


def validate_username(username):
    """Validate username format"""
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 20:
        return False, "Username must be 20 characters or less"
    if not username.isalnum():
        return False, "Username must be alphanumeric only"
    return True, ""


def validate_password(password):
    """Validate password strength"""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters"
    if len(password) > 50:
        return False, "Password must be 50 characters or less"
    return True, ""
