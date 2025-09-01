import base64
import hashlib
import os
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)

def generate_iv():
    """Generate a random 12-byte IV for AES-GCM."""
    return os.urandom(12)

def derive_key_from_metadata(metadata: dict) -> bytes:
    """Derive encryption key from metadata."""
    # For now, we'll use a fixed key that matches what the Flutter app generates
    # In production, this would retrieve the actual key from secure storage using key_id
    key_id = metadata.get('key_id', 'placeholder')
    
    # Use a consistent key that both Flutter and server can use
    # This is a 32-byte key that matches the Flutter app's key generation
    if key_id == 'flutter_app_key':
        # Use a fixed key that the Flutter app will also use
        # This is a base64-encoded 32-byte key
        import base64
        # This is a 32-byte key encoded as base64
        key_b64 = "cGxhY2Vob2xkZXJfa2V5XzMyX2J5dGVzX2xvbmdfZm8="
        return base64.b64decode(key_b64)
    else:
        # Fallback to placeholder key for other key_ids
        logger.warning(f"Using placeholder key for key_id: {key_id}")
        return b'placeholder_key_32_bytes_long_fo'

def encrypt_message(plaintext: str, request_metadata: dict) -> tuple[bytes, dict]:
    """
    Encrypt a message using AES-GCM.
    
    Args:
        plaintext: The message to encrypt
        request_metadata: Metadata from the encrypted request
        
    Returns:
        tuple: (encrypted_bytes, new_metadata)
    """
    try:
        # Generate a new IV for this response
        iv = generate_iv()
        
        # Derive the encryption key
        key = derive_key_from_metadata(request_metadata)
        
        # Create AESGCM cipher
        cipher = AESGCM(key)
        
        # Encrypt the plaintext
        plaintext_bytes = plaintext.encode('utf-8')
        encrypted_data = cipher.encrypt(iv, plaintext_bytes, None)
        
        # Create new metadata for the response
        response_metadata = {
            'algorithm': 'AES-256-GCM',
            'key_id': request_metadata.get('key_id', 'placeholder'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            'created_at': request_metadata.get('created_at', 'unknown')
        }
        
        logger.info(f"Message encrypted successfully using {response_metadata['algorithm']}")
        return encrypted_data, response_metadata
        
    except Exception as e:
        logger.error(f"Failed to encrypt message: {str(e)}")
        raise

def decrypt_message(encrypted_data: bytes, metadata: dict) -> str:
    """
    Decrypt a message using AES-GCM.
    
    Args:
        encrypted_data: The encrypted message bytes
        metadata: Encryption metadata containing IV and algorithm info
        
    Returns:
        str: The decrypted plaintext
    """
    try:
        # Extract IV from metadata
        iv_b64 = metadata.get('iv')
        if not iv_b64:
            raise ValueError("No IV found in metadata")
        
        iv = base64.b64decode(iv_b64)
        
        # Derive the decryption key
        key = derive_key_from_metadata(metadata)
        
        # Create AESGCM cipher
        cipher = AESGCM(key)
        
        # Decrypt the data
        plaintext_bytes = cipher.decrypt(iv, encrypted_data, None)
        
        logger.info("Message decrypted successfully")
        return plaintext_bytes.decode('utf-8')
        
    except Exception as e:
        logger.error(f"Failed to decrypt message: {str(e)}")
        raise

def verify_message_hash(message: str, expected_hash: str) -> bool:
    """Verify the SHA-256 hash of a message."""
    calculated_hash = hashlib.sha256(message.encode('utf-8')).hexdigest()
    return calculated_hash == expected_hash
