import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv()

# Define settings using Pydantic BaseSettings
class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = "your_default_deepseek_api_key_if_any"
    
    # If other existing configs were to be moved here, they'd be defined as:
    # DATABASE_URL: str
    # JWT_SECRET_KEY: str
    # ... etc.

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# API Version - can remain as a global constant or move into Settings
API_V1_STR = "/api/v1"

# Project base directory - remains a global constant
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Existing dictionary-based configurations can remain for now,
# or be gradually refactored into the Settings class.
# For this task, we ensure DEEPSEEK_API_KEY is loaded via pydantic-settings.
# The existing os.getenv calls will still work for .env loaded by load_dotenv().

# Blockchain configuration
BLOCKCHAIN_CONFIG = {
    "ganache_url": os.getenv("GANACHE_RPC_URL", "http://127.0.0.1:7545"),
    "user_registry_address": None,  # Will be loaded dynamically
    "user_registry_abi": None,      # Will be loaded dynamically
    "medical_record_registry_address": None, # Will be loaded dynamically
    "medical_record_registry_abi": None,     # Will be loaded dynamically
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
    import json
    import logging
    logger = logging.getLogger(__name__)

    contracts_to_load = {
        "user_registry": ("UserRegistry-address.json", "UserRegistry-abi.json", "user_registry_address", "user_registry_abi"),
        "medical_record_registry": ("MedicalRecordRegistry-address.json", "MedicalRecordRegistry-abi.json", "medical_record_registry_address", "medical_record_registry_abi"),
    }

    for name, files_and_keys in contracts_to_load.items():
        address_filename, abi_filename, address_key, abi_key = files_and_keys
        
        address_file_path = BASE_DIR / "blockchain" / "build" / "deployments" / address_filename
        abi_file_path = BASE_DIR / "blockchain" / "build" / "deployments" / abi_filename
        
        try:
            if address_file_path.exists():
                with open(address_file_path, 'r') as f:
                    address_data = json.load(f)
                    BLOCKCHAIN_CONFIG[address_key] = address_data["address"]
            else:
                logger.warning(f"{name.replace('_', ' ').title()} address file not found at {address_file_path}. Contract may not be deployed.")
                BLOCKCHAIN_CONFIG[address_key] = None # Ensure it's None if file not found

            if abi_file_path.exists():
                with open(abi_file_path, 'r') as f:
                    BLOCKCHAIN_CONFIG[abi_key] = json.load(f)
            else:
                logger.warning(f"{name.replace('_', ' ').title()} ABI file not found at {abi_file_path}. Contract may not be deployed.")
                BLOCKCHAIN_CONFIG[abi_key] = None # Ensure it's None if file not found
            
            if BLOCKCHAIN_CONFIG[address_key] and BLOCKCHAIN_CONFIG[abi_key]:
                 logger.info(f"{name.replace('_', ' ').title()} contract ABI and address loaded successfully.")
            elif not BLOCKCHAIN_CONFIG[address_key] and not BLOCKCHAIN_CONFIG[abi_key] and not address_file_path.exists() and not abi_file_path.exists():
                # This is the normal case if files don't exist, warning already issued.
                pass
            else:
                # This case means one file exists but not the other, or some other partial load.
                logger.warning(f"Partial load for {name.replace('_', ' ').title()} contract. Address: {BLOCKCHAIN_CONFIG[address_key]}, ABI loaded: {BLOCKCHAIN_CONFIG[abi_key] is not None}")

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {name} contract file ({address_file_path} or {abi_file_path}): {e}")
            BLOCKCHAIN_CONFIG[address_key] = None
            BLOCKCHAIN_CONFIG[abi_key] = None
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading {name} contract info: {e}")
            BLOCKCHAIN_CONFIG[address_key] = None
            BLOCKCHAIN_CONFIG[abi_key] = None

# Load contract info at module import
load_contract_info() 