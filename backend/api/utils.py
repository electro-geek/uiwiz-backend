from cryptography.fernet import Fernet
from django.conf import settings

def get_fernet():
    """Get Fernet instance with key from settings."""
    key = getattr(settings, 'ENCRYPTION_KEY', '')
    if not key:
        return None
    try:
        return Fernet(key.encode())
    except Exception:
        return None

def encrypt_data(data):
    """Encrypt string data."""
    if not data:
        return None
    f = get_fernet()
    if not f:
        return data  # Fallback: store as plain text if no key
    try:
        return f.encrypt(data.encode()).decode()
    except Exception:
        return data

def decrypt_data(data):
    """Decrypt string data. Handles legacy plain text."""
    if not data:
        return None
    f = get_fernet()
    if not f:
        return data
    try:
        return f.decrypt(data.encode()).decode()
    except Exception:
        # If decryption fails, assume it's plain text (legacy data)
        return data
