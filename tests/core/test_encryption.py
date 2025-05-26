import pytest
import os

from src.app.core.encryption import (
    generate_encryption_key,
    encrypt_data,
    decrypt_data,
    hash_data,
    AES_NONCE_SIZE,
    AES_TAG_SIZE
)

def test_generate_encryption_key():
    """
    Test that generate_encryption_key returns a key of the correct length (32 bytes).
    """
    key = generate_encryption_key()
    assert isinstance(key, bytes)
    assert len(key) == 32

def test_encrypt_decrypt_data_success():
    """
    Test that data can be encrypted and then decrypted back to its original form.
    """
    key = generate_encryption_key()
    original_data = "This is a secret message for testing."
    
    encrypted_blob = encrypt_data(original_data, key)
    assert isinstance(encrypted_blob, bytes)
    # Check if length is at least nonce + tag size. Ciphertext can be empty for empty original_data.
    assert len(encrypted_blob) >= AES_NONCE_SIZE + AES_TAG_SIZE 
    
    decrypted_data = decrypt_data(encrypted_blob, key)
    assert decrypted_data == original_data

def test_encrypt_decrypt_empty_data():
    """
    Test encryption and decryption of an empty string.
    """
    key = generate_encryption_key()
    original_data = ""
    
    encrypted_blob = encrypt_data(original_data, key)
    assert isinstance(encrypted_blob, bytes)
    assert len(encrypted_blob) == AES_NONCE_SIZE + 0 + AES_TAG_SIZE # Ciphertext is 0 bytes
    
    decrypted_data = decrypt_data(encrypted_blob, key)
    assert decrypted_data == original_data

def test_decrypt_data_wrong_key():
    """
    Test that decryption fails if the wrong key is used.
    """
    key1 = generate_encryption_key()
    key2 = generate_encryption_key()
    assert key1 != key2 # Ensure keys are different
    
    original_data = "Another secret message."
    encrypted_blob = encrypt_data(original_data, key1)
    
    with pytest.raises(ValueError) as excinfo:
        decrypt_data(encrypted_blob, key2)
    assert "Decryption failed" in str(excinfo.value)

def test_decrypt_data_tampered_nonce():
    """
    Test that decryption fails if the nonce part of the encrypted blob is tampered with.
    """
    key = generate_encryption_key()
    original_data = "Sensitive information here."
    encrypted_blob = encrypt_data(original_data, key)
    
    tampered_blob_list = list(encrypted_blob)
    # Tamper the first byte of the nonce
    tampered_blob_list[0] = tampered_blob_list[0] ^ 0x01 
    tampered_blob = bytes(tampered_blob_list)
    
    with pytest.raises(ValueError) as excinfo:
        decrypt_data(tampered_blob, key)
    assert "Decryption failed" in str(excinfo.value)

def test_decrypt_data_tampered_ciphertext():
    """
    Test that decryption fails if the ciphertext part of the encrypted blob is tampered with.
    """
    key = generate_encryption_key()
    original_data = "More secrets."
    encrypted_blob = encrypt_data(original_data, key)
    
    # Ensure there is ciphertext to tamper (original_data is not empty)
    if len(encrypted_blob) > AES_NONCE_SIZE + AES_TAG_SIZE:
        tampered_blob_list = list(encrypted_blob)
        # Tamper a byte in the ciphertext (after nonce, before tag)
        ciphertext_index = AES_NONCE_SIZE 
        tampered_blob_list[ciphertext_index] = tampered_blob_list[ciphertext_index] ^ 0x01
        tampered_blob = bytes(tampered_blob_list)
        
        with pytest.raises(ValueError) as excinfo:
            decrypt_data(tampered_blob, key)
        assert "Decryption failed" in str(excinfo.value)
    else:
        pytest.skip("Ciphertext is empty, cannot test tampering ciphertext.")

def test_decrypt_data_tampered_tag():
    """
    Test that decryption fails if the authentication tag part of the encrypted blob is tampered with.
    """
    key = generate_encryption_key()
    original_data = "Final piece of secret data."
    encrypted_blob = encrypt_data(original_data, key)
    
    tampered_blob_list = list(encrypted_blob)
    # Tamper the last byte of the tag
    tampered_blob_list[-1] = tampered_blob_list[-1] ^ 0x01
    tampered_blob = bytes(tampered_blob_list)
    
    with pytest.raises(ValueError) as excinfo:
        decrypt_data(tampered_blob, key)
    assert "Decryption failed" in str(excinfo.value)

def test_decrypt_data_invalid_length():
    """
    Test that decryption fails if the encrypted data is too short.
    """
    key = generate_encryption_key()
    short_blob = os.urandom(AES_NONCE_SIZE + AES_TAG_SIZE - 1) # Shorter than nonce + tag
    
    with pytest.raises(ValueError) as excinfo:
        decrypt_data(short_blob, key)
    assert "Encrypted data is too short" in str(excinfo.value)

def test_encrypt_invalid_key_type():
    """Test encryption with an invalid key type."""
    with pytest.raises(ValueError) as excinfo:
        encrypt_data("test", "not_bytes_key")
    assert "Encryption key must be 32 bytes" in str(excinfo.value)

def test_encrypt_invalid_key_length():
    """Test encryption with an invalid key length."""
    with pytest.raises(ValueError) as excinfo:
        encrypt_data("test", b"shortkey")
    assert "Encryption key must be 32 bytes" in str(excinfo.value)

def test_decrypt_invalid_key_type():
    """Test decryption with an invalid key type."""
    key = generate_encryption_key()
    encrypted_blob = encrypt_data("test", key)
    with pytest.raises(ValueError) as excinfo:
        decrypt_data(encrypted_blob, "not_bytes_key")
    assert "Decryption key must be 32 bytes" in str(excinfo.value)

def test_decrypt_invalid_key_length():
    """Test decryption with an invalid key length."""
    key = generate_encryption_key()
    encrypted_blob = encrypt_data("test", key)
    with pytest.raises(ValueError) as excinfo:
        decrypt_data(encrypted_blob, b"shortkey")
    assert "Decryption key must be 32 bytes" in str(excinfo.value)

def test_hash_data_consistency():
    """
    Test that hash_data produces consistent output for the same input.
    """
    data = "This data will be hashed."
    hash1 = hash_data(data)
    hash2 = hash_data(data)
    assert hash1 == hash2
    assert isinstance(hash1, str)
    assert len(hash1) == 64 # SHA-256 hex output length

def test_hash_data_difference():
    """
    Test that hash_data produces different output for different inputs.
    """
    data1 = "Data string 1"
    data2 = "Data string 2"
    hash1 = hash_data(data1)
    hash2 = hash_data(data2)
    assert hash1 != hash2

def test_hash_empty_data():
    """
    Test hashing an empty string.
    """
    data = ""
    hash_val = hash_data(data)
    assert isinstance(hash_val, str)
    assert len(hash_val) == 64
    # Known SHA-256 hash for an empty string
    assert hash_val == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
