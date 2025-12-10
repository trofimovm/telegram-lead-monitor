from cryptography.fernet import Fernet, InvalidToken
from typing import Union

from app.config import settings


class EncryptionService:
    """
    Service for encrypting and decrypting sensitive data using Fernet (AES-128).
    Used primarily for Telegram session data.
    """

    def __init__(self):
        """
        Initialize encryption service with key from settings.

        Raises:
            ValueError: If encryption key is invalid
        """
        try:
            self.fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        except Exception as e:
            raise ValueError(f"Invalid encryption key: {e}")

    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        Encrypt data using Fernet.

        Args:
            data: String or bytes to encrypt

        Returns:
            Encrypted data as bytes

        Raises:
            Exception: If encryption fails
        """
        if isinstance(data, str):
            data = data.encode()

        try:
            return self.fernet.encrypt(data)
        except Exception as e:
            raise Exception(f"Encryption failed: {e}")

    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Decrypt data using Fernet.

        Args:
            encrypted_data: Encrypted bytes to decrypt

        Returns:
            Decrypted data as string

        Raises:
            InvalidToken: If decryption fails or data is corrupted
            Exception: For other decryption errors
        """
        try:
            decrypted = self.fernet.decrypt(encrypted_data)
            return decrypted.decode()
        except InvalidToken:
            raise InvalidToken("Failed to decrypt data: invalid token or corrupted data")
        except Exception as e:
            raise Exception(f"Decryption failed: {e}")


# Global instance
encryption_service = EncryptionService()


def encrypt_session(session_string: str) -> bytes:
    """
    Encrypt a Telegram session string.

    Args:
        session_string: Telegram session string to encrypt

    Returns:
        Encrypted session data as bytes
    """
    return encryption_service.encrypt(session_string)


def decrypt_session(encrypted_session: bytes) -> str:
    """
    Decrypt a Telegram session string.

    Args:
        encrypted_session: Encrypted session bytes

    Returns:
        Decrypted session string

    Raises:
        InvalidToken: If decryption fails
    """
    return encryption_service.decrypt(encrypted_session)


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.

    Returns:
        Base64-encoded encryption key as string

    Note:
        This is a utility function for generating new keys.
        The generated key should be stored securely in environment variables.
    """
    return Fernet.generate_key().decode()
