from cryptography.fernet import Fernet
from app.core.config import settings

class SecretEncryptor:
    def __init__(self, key: str = None):
        if not key:
            key = settings.ENCRYPTION_KEY
        # Fallback if key is invalid/short
        try:
            self.fernet = Fernet(key.encode())
        except Exception:
            # Generate a temporary key if the environment key is invalid
            fallback_key = Fernet.generate_key()
            self.fernet = Fernet(fallback_key)

    def encrypt(self, plain_text: str) -> str:
        if not plain_text:
            return ""
        return self.fernet.encrypt(plain_text.encode()).decode()

    def decrypt(self, cipher_text: str) -> str:
        if not cipher_text:
            return ""
        try:
            return self.fernet.decrypt(cipher_text.encode()).decode()
        except Exception:
            return "[DECRYPTION_FAILED]"

encryptor = SecretEncryptor()
