import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Blockchain configuration
BLOCKCHAIN_CONFIG = {
    "ganache_url": os.getenv("GANACHE_RPC_URL", "http://127.0.0.1:7545"),
    "user_registry_address": None,  # Will be loaded dynamically
    "user_registry_abi": None,      # Will be loaded dynamically
    "sender_private_key": os.getenv("BLOCKCHAIN_SENDER_PRIVATE_KEY"),  # Private key for signing transactions
}

# Database configuration
DATABASE_CONFIG = {
    "url": os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/meditrustal"
    )
}

# JWT configuration
JWT_CONFIG = {
    "secret_key": os.getenv("JWT_SECRET_KEY", "your-secret-key-for-jwt"),
    "algorithm": "HS256",
    "access_token_expire_minutes": 30
}

# Security configuration
SECURITY_CONFIG = {
    "password_hash_rounds": 12  # For bcrypt
}

# Load contract address and ABI
def load_contract_info():
    try:
        address_file = BASE_DIR / "blockchain" / "build" / "deployments" / "UserRegistry-address.json"
        abi_file = BASE_DIR / "blockchain" / "build" / "deployments" / "UserRegistry-abi.json"
        
        if address_file.exists() and abi_file.exists():
            import json
            with open(address_file) as f:
                BLOCKCHAIN_CONFIG["user_registry_address"] = json.load(f)["address"]
            with open(abi_file) as f:
                BLOCKCHAIN_CONFIG["user_registry_abi"] = json.load(f)
    except Exception as e:
        print(f"Error loading contract info: {e}")

# Load contract info at module import
load_contract_info() 