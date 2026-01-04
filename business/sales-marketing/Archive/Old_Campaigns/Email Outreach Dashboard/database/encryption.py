"""
Password Encryption Module
Campaign Control Center Dashboard

Provides secure password encryption using Fernet symmetric encryption.
Passwords for SMTP accounts are encrypted before storage and decrypted only when needed.
"""

import os
from typing import Optional
from cryptography.fernet import Fernet


def get_key_file_path() -> str:
    """
    Get the path to the encryption key file.

    Returns:
        str: Full path to the encryption key file
    """
    # Store in the same directory as this module
    module_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_dir = os.path.dirname(module_dir)
    return os.path.join(dashboard_dir, '.encryption_key')


def generate_key() -> bytes:
    """
    Generate a new Fernet encryption key.

    Returns:
        bytes: A new encryption key
    """
    return Fernet.generate_key()


def save_key(key: bytes) -> None:
    """
    Save the encryption key to a file.

    Args:
        key: The encryption key to save

    Raises:
        IOError: If the key file cannot be written
    """
    try:
        key_path = get_key_file_path()
        with open(key_path, 'wb') as key_file:
            key_file.write(key)

        # Set file permissions to be readable only by owner (on Unix-like systems)
        try:
            os.chmod(key_path, 0o600)
        except (OSError, AttributeError):
            # Windows doesn't support chmod in the same way, skip
            pass

    except Exception as e:
        raise IOError(f"Failed to save encryption key: {str(e)}")


def load_key() -> bytes:
    """
    Load the encryption key from file. Creates a new key if one doesn't exist.

    Returns:
        bytes: The encryption key

    Raises:
        IOError: If the key file cannot be read or created
    """
    try:
        key_path = get_key_file_path()

        # If key file doesn't exist, generate and save a new one
        if not os.path.exists(key_path):
            key = generate_key()
            save_key(key)
            return key

        # Load existing key
        with open(key_path, 'rb') as key_file:
            return key_file.read()

    except Exception as e:
        raise IOError(f"Failed to load encryption key: {str(e)}")


def encrypt_password(password: str) -> bytes:
    """
    Encrypt a plaintext password using Fernet symmetric encryption.

    Args:
        password: The plaintext password to encrypt

    Returns:
        bytes: The encrypted password

    Raises:
        ValueError: If password is empty or None
        RuntimeError: If encryption fails
    """
    if not password:
        raise ValueError("Password cannot be empty")

    try:
        key = load_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(password.encode('utf-8'))
        return encrypted

    except Exception as e:
        raise RuntimeError(f"Failed to encrypt password: {str(e)}")


def decrypt_password(encrypted_password: bytes) -> str:
    """
    Decrypt an encrypted password.

    Args:
        encrypted_password: The encrypted password bytes

    Returns:
        str: The decrypted plaintext password

    Raises:
        ValueError: If encrypted_password is empty or None
        RuntimeError: If decryption fails
    """
    if not encrypted_password:
        raise ValueError("Encrypted password cannot be empty")

    try:
        key = load_key()
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_password)
        return decrypted.decode('utf-8')

    except Exception as e:
        raise RuntimeError(f"Failed to decrypt password: {str(e)}")


def test_encryption() -> bool:
    """
    Test that encryption/decryption is working correctly.

    Returns:
        bool: True if encryption/decryption works, False otherwise
    """
    try:
        test_password = "test_password_123!@#"
        encrypted = encrypt_password(test_password)
        decrypted = decrypt_password(encrypted)
        return decrypted == test_password
    except Exception:
        return False


if __name__ == "__main__":
    # Test encryption when run directly
    print("Testing encryption module...")

    if test_encryption():
        print("✓ Encryption test passed!")
        print(f"✓ Key file location: {get_key_file_path()}")
    else:
        print("✗ Encryption test failed!")
