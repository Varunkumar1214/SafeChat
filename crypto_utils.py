# crypto_utils.py

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

def generate_keys() -> tuple[str, str]:
    """
    Generate a new RSA 2048-bit key pair.
    Returns: (private_key_str, public_key_str)
    """
    key = RSA.generate(2048)
    private_key = key.export_key().decode()
    public_key = key.publickey().export_key().decode()
    return private_key, public_key

def encrypt_message(public_key_str: str, message: str) -> str:
    """
    Encrypts a message using the recipient's public key.
    Returns: base64-encoded encrypted message
    """
    public_key = RSA.import_key(public_key_str)
    cipher = PKCS1_OAEP.new(public_key)
    encrypted = cipher.encrypt(message.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_message(private_key_str: str, encrypted_message: str) -> str:
    """
    Decrypts a base64-encoded encrypted message using the user's private key.
    Returns: decrypted plain text message
    """
    private_key = RSA.import_key(private_key_str)
    cipher = PKCS1_OAEP.new(private_key)
    decrypted = cipher.decrypt(base64.b64decode(encrypted_message))
    return decrypted.decode()
