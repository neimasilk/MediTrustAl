import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# AES-GCM uses a 12-byte (96-bit) nonce by default, which is recommended.
# AES-GCM authentication tag is 16 bytes (128 bits) by default.
AES_NONCE_SIZE = 12  # bytes
AES_TAG_SIZE = 16  # bytes


def generate_encryption_key() -> bytes:
    """
    Generates a 32-byte random key for AES-256.
    """
    return os.urandom(32)


def encrypt_data(data: str, key: bytes) -> bytes:
    """
    Encrypts data using AES-256-GCM.

    Args:
        data: The string data to encrypt.
        key: The 32-byte encryption key.

    Returns:
        Bytes in the format: nonce + ciphertext + tag.
    """
    if not isinstance(key, bytes) or len(key) != 32:
        raise ValueError("Encryption key must be 32 bytes.")

    aesgcm = AESGCM(key)
    nonce = os.urandom(AES_NONCE_SIZE)  # AESGCM standard nonce size is 12 bytes
    data_bytes = data.encode('utf-8')
    ciphertext_with_tag = aesgcm.encrypt(nonce, data_bytes, None)  # No associated data

    # ciphertext_with_tag already includes the authentication tag at the end
    # The typical order is nonce || ciphertext || tag
    # AESGCM encrypt method returns ciphertext || tag
    
    # The encrypt() method returns ciphertext + tag.
    # We need to prepend the nonce to it.
    return nonce + ciphertext_with_tag


def decrypt_data(encrypted_data_with_nonce_tag: bytes, key: bytes) -> str:
    """
    Decrypts data encrypted with AES-256-GCM.

    Args:
        encrypted_data_with_nonce_tag: The encrypted data including nonce and tag.
                                       Expected format: nonce + ciphertext + tag.
        key: The 32-byte encryption key.

    Returns:
        The decrypted data as a string.
    """
    if not isinstance(key, bytes) or len(key) != 32:
        raise ValueError("Decryption key must be 32 bytes.")

    if len(encrypted_data_with_nonce_tag) < AES_NONCE_SIZE + AES_TAG_SIZE:
        raise ValueError("Encrypted data is too short to contain nonce, ciphertext, and tag.")

    nonce = encrypted_data_with_nonce_tag[:AES_NONCE_SIZE]
    # The rest is ciphertext + tag
    ciphertext_and_tag = encrypted_data_with_nonce_tag[AES_NONCE_SIZE:]
    
    aesgcm = AESGCM(key)
    
    try:
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext_and_tag, None)  # No associated data
        return decrypted_bytes.decode('utf-8')
    except Exception as e: # Catching general exception from decrypt, e.g. InvalidTag
        raise ValueError(f"Decryption failed. Data may be corrupted or key is incorrect. Error: {e}")


def hash_data(data: str) -> str:
    """
    Hashes data using SHA-256.

    Args:
        data: The string data to hash.

    Returns:
        The hex representation of the hash.
    """
    data_bytes = data.encode('utf-8')
    sha256_hash = hashlib.sha256(data_bytes).hexdigest()
    return sha256_hash

# Example Usage (not part of the module, for testing)
if __name__ == '__main__':
    # Key Generation
    encryption_key = generate_encryption_key()
    print(f"Generated Encryption Key (hex): {encryption_key.hex()}")

    # Data to be encrypted and hashed
    original_data = "This is a secret message for testing purposes! It's quite sensitive."
    print(f"Original Data: '{original_data}'")

    # Hashing
    data_hash_hex = hash_data(original_data)
    print(f"SHA-256 Hash (hex): {data_hash_hex}")

    # Encryption
    try:
        encrypted_blob = encrypt_data(original_data, encryption_key)
        print(f"Encrypted Blob (hex): {encrypted_blob.hex()}")
        print(f"Encrypted Blob Length: {len(encrypted_blob)} bytes")

        # Decryption
        decrypted_data_str = decrypt_data(encrypted_blob, encryption_key)
        print(f"Decrypted Data: '{decrypted_data_str}'")

        assert original_data == decrypted_data_str
        print("Encryption and Decryption successful!")

    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Test decryption with wrong key
    print("\nTesting decryption with wrong key...")
    wrong_key = generate_encryption_key()
    try:
        decrypt_data(encrypted_blob, wrong_key)
    except ValueError as ve:
        print(f"Successfully caught error for wrong key: {ve}")
    
    # Test decryption with tampered data
    print("\nTesting decryption with tampered data...")
    if len(encrypted_blob) > 20: # Ensure blob is long enough
        tampered_blob_list = list(encrypted_blob)
        # Flip a bit in the ciphertext part (after nonce)
        original_byte_index = AES_NONCE_SIZE + 5 # Tamper a byte in ciphertext
        if original_byte_index < len(tampered_blob_list) - AES_TAG_SIZE:
             tampered_blob_list[original_byte_index] = tampered_blob_list[original_byte_index] ^ 0x01 
        tampered_blob = bytes(tampered_blob_list)
        
        try:
            decrypt_data(tampered_blob, encryption_key)
        except ValueError as ve:
            print(f"Successfully caught error for tampered data: {ve}")
        except Exception as e:
            print(f"Unexpected error for tampered data: {e}")
    else:
        print("Encrypted blob too short to perform tampering test as designed.")
