import hashlib
import base58
import uuid

def generate_did(user_uuid: uuid.UUID) -> str:
    """
    Generates a Decentralized Identifier (DID) for a user.
    Format: did:meditrustal:{base58(sha256(user_uuid_str))}
    
    Args:
        user_uuid (uuid.UUID): The user's UUID from the database
        
    Returns:
        str: The generated DID in the format did:meditrustal:{base58(sha256(user_uuid_str))}
        
    Raises:
        TypeError: If user_uuid is not a UUID object
    """
    if not isinstance(user_uuid, uuid.UUID):
        raise TypeError("user_uuid must be a UUID object")

    user_uuid_str = str(user_uuid)
    
    # SHA256 hash of the UUID string
    sha256_hash = hashlib.sha256(user_uuid_str.encode('utf-8')).digest()
    
    # Base58 encode the hash
    encoded_hash = base58.b58encode(sha256_hash).decode('utf-8')
    
    # Create the DID string
    did = f"did:meditrustal:{encoded_hash}"
    return did 