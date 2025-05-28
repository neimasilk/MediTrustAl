import os
import hashlib
from cryptography.fernet import Fernet
from .config import JWT_CONFIG

def get_encryption_key() -> bytes:
    """
    Derives a 32-byte encryption key from the JWT secret key.
    
    WARNING: This is a placeholder/MVP approach for development only.
    In production, use a dedicated key management service like:
    - HashiCorp Vault
    - AWS KMS
    - Azure Key Vault
    - Google Cloud KMS
    
    TODO: Replace with proper key management system before production deployment.
    See memory-bank/status-todolist-suggestions.md for migration plan.
    """
    # Get JWT secret from config
    jwt_secret = JWT_CONFIG.get("secret_key", "default-fallback-secret-key-for-encryption")
    
    # Use PBKDF2 to derive a proper encryption key from the JWT secret
    # This is more secure than simple truncation/padding
    salt = b'meditrustal_salt_2024'  # In production, use a random salt stored securely
    key = hashlib.pbkdf2_hmac('sha256', jwt_secret.encode('utf-8'), salt, 100000)
    
    return key[:32]  # AES-256 requires 32 bytes

def get_fernet_key() -> bytes:
    """
    Generate a Fernet-compatible key for symmetric encryption.
    Fernet uses 32 bytes base64url-encoded.
    
    WARNING: This is also a development-only approach.
    """
    encryption_key = get_encryption_key()
    # Fernet expects a base64url-encoded 32-byte key
    import base64
    return base64.urlsafe_b64encode(encryption_key)

def create_fernet_cipher():
    """
    Create a Fernet cipher instance for encryption/decryption.
    """
    return Fernet(get_fernet_key())

# Security configuration constants
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "login_attempts": {
        "max_attempts": 5,
        "window_minutes": 15,
        "lockout_minutes": 30
    },
    "api_calls": {
        "max_calls_per_minute": 100,
        "max_calls_per_hour": 1000
    }
}