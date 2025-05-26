import pytest
import uuid
from src.app.core.utils import generate_did

def test_generate_did_valid_uuid():
    test_uuid = uuid.uuid4()
    did = generate_did(test_uuid)
    
    # Check format
    assert did.startswith("did:meditrustal:")
    assert len(did) > len("did:meditrustal:")  # Should have base58 hash after prefix
    
    # Check deterministic
    did2 = generate_did(test_uuid)
    assert did == did2  # Same UUID should produce same DID

def test_generate_did_different_uuids():
    uuid1 = uuid.uuid4()
    uuid2 = uuid.uuid4()
    
    did1 = generate_did(uuid1)
    did2 = generate_did(uuid2)
    
    assert did1 != did2  # Different UUIDs should produce different DIDs

def test_generate_did_invalid_input():
    with pytest.raises(TypeError, match="user_uuid must be a UUID object"):
        generate_did("not-a-uuid")  # Should raise TypeError

def test_generate_did_base58_format():
    test_uuid = uuid.uuid4()
    did = generate_did(test_uuid)
    
    # Extract base58 part
    base58_part = did.split(":")[-1]
    
    # Base58 should only contain alphanumeric characters (excluding 0, O, I, l)
    valid_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    assert all(c in valid_chars for c in base58_part) 