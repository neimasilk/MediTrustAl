from web3 import Web3
from eth_account import Account
from .config import BLOCKCHAIN_CONFIG
import os

class BlockchainService:
    def __init__(self, test_mode=False):
        if test_mode:
            # Use mock values for testing
            self.w3 = None
            self.user_registry_contract = None # Renamed from self.contract
            self.medical_record_registry_contract = None
            self.private_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
            self.account = "0x1234567890123456789012345678901234567890"
            return

        self.w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_CONFIG["ganache_url"]))
        if not self.w3.is_connected():
            # Allow initialization to proceed for cases where blockchain is optional or checked later
            print("Warning: Could not connect to Ethereum node during BlockchainService init.")
            self.user_registry_contract = None
            self.medical_record_registry_contract = None
        else:
            try:
                if BLOCKCHAIN_CONFIG.get("user_registry_address") and BLOCKCHAIN_CONFIG.get("user_registry_abi"):
                    self.user_registry_contract = self.w3.eth.contract(
                        address=BLOCKCHAIN_CONFIG["user_registry_address"],
                        abi=BLOCKCHAIN_CONFIG["user_registry_abi"]
                    )
                    print("UserRegistry contract initialized.")
                else:
                    self.user_registry_contract = None
                    print("Warning: UserRegistry contract address or ABI not loaded. User-related blockchain interactions might fail.")

                if BLOCKCHAIN_CONFIG.get("medical_record_registry_address") and BLOCKCHAIN_CONFIG.get("medical_record_registry_abi"):
                    self.medical_record_registry_contract = self.w3.eth.contract(
                        address=BLOCKCHAIN_CONFIG["medical_record_registry_address"],
                        abi=BLOCKCHAIN_CONFIG["medical_record_registry_abi"]
                    )
                    print("MedicalRecordRegistry contract initialized.")
                else:
                    self.medical_record_registry_contract = None
                    print("Warning: MedicalRecordRegistry contract address or ABI not loaded. Medical record-related blockchain interactions might fail.")
            except Exception as e:
                print(f"Error initializing contracts during BlockchainService init: {e}")
                self.user_registry_contract = None
                self.medical_record_registry_contract = None
        
        # Get the private key from config
        self.private_key = BLOCKCHAIN_CONFIG.get("sender_private_key")
        if not self.private_key:
            raise ValueError("BLOCKCHAIN_SENDER_PRIVATE_KEY must be set in .env")
        
        # Derive the account address from private key
        self.account = Account.from_key(self.private_key).address
        
    async def register_user(self, user_id: str, role: str) -> dict:
        """
        Register a new user in the blockchain
        """
        try:
            if not self.w3:  # Test mode
                return {
                    'success': True,
                    'transaction_hash': '0x1234567890abcdef',
                    'user_id': user_id,
                    'role': role
                }

            # Build the transaction
            if not self.user_registry_contract:
                raise ConnectionError("UserRegistry contract is not initialized.")
            tx = self.user_registry_contract.functions.registerUser(user_id, role).build_transaction({
                'from': self.account,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account),
            })
            
            # Sign and send the transaction using the configured private key
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': True,
                'transaction_hash': receipt['transactionHash'].hex(),
                'user_id': user_id,
                'role': role
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_user_role(self, user_id: str) -> dict:
        """
        Get user role from the blockchain
        """
        try:
            if not self.w3:  # Test mode
                return {
                    'success': True,
                    'user_id': user_id,
                    'role': 'PATIENT',
                    'is_registered': True
                }
            
            if not self.user_registry_contract:
                raise ConnectionError("UserRegistry contract is not initialized.")
            # Note: Smart contract `getUserRole` is not async, but web3.py call might be if provider is async.
            # Assuming it's a standard call for now.
            role_data = self.user_registry_contract.functions.getUserRole(user_id).call()
            role = role_data[0]
            is_registered = role_data[1]
            
            return {
                'success': True,
                'user_id': user_id,
                'role': role,
                'is_registered': is_registered
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def add_medical_record_hash(self, record_hash_hex: str, patient_did: str, record_type: str) -> dict:
        """
        Adds a medical record hash to the MedicalRecordRegistry smart contract.
        """
        try:
            if not self.w3: # Test mode
                return {
                    'success': True, 
                    'transaction_hash': '0xabcdef1234567890', 
                    'record_hash': record_hash_hex
                }

            if not self.w3.is_connected():
                raise ConnectionError("Could not connect to Ethereum node. Cannot add medical record hash.")

            if not self.medical_record_registry_contract:
                raise ConnectionError("MedicalRecordRegistry contract is not initialized. Cannot add medical record hash.")

            if not self.private_key:
                raise ValueError("Blockchain sender private key not configured. Cannot add medical record hash.")

            # Convert hex string to bytes32
            if record_hash_hex.startswith("0x"):
                record_hash_hex = record_hash_hex[2:]
            
            if len(record_hash_hex) != 64: # 32 bytes = 64 hex characters
                raise ValueError(f"Record hash hex string must be 64 characters (32 bytes) long, got {len(record_hash_hex)}")
            
            record_hash_bytes32 = bytes.fromhex(record_hash_hex)

            # Build transaction
            tx = self.medical_record_registry_contract.functions.addRecord(
                record_hash_bytes32,
                patient_did,
                record_type
            ).build_transaction({
                'from': self.account,
                'gas': 300000,  # Adjust gas limit as needed
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account),
            })

            # Sign and send the transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                return {
                    'success': True,
                    'transaction_hash': receipt.transactionHash.hex(),
                    'record_hash': record_hash_hex
                }
            else:
                return {
                    'success': False,
                    'error': 'Transaction failed on blockchain.',
                    'transaction_hash': receipt.transactionHash.hex()
                }

        except ValueError as ve:
             return {'success': False, 'error': str(ve)}
        except ConnectionError as ce:
             return {'success': False, 'error': str(ce)}
        except Exception as e:
            return {
                'success': False,
                'error': f"An unexpected error occurred: {str(e)}"
            }

    async def get_record_hashes_for_patient(self, patient_did: str) -> dict:
        """
        Retrieves a list of record hashes for a given patient DID from the MedicalRecordRegistry smart contract.

        Args:
            patient_did (str): The patient's Decentralized Identifier.

        Returns:
            dict: A dictionary with:
                  - "success" (bool): True if successful, False otherwise.
                  - "data" (dict, optional): If successful, a dictionary containing "hashes" (list of hex strings).
                  - "error" (str, optional): An error message if unsuccessful.
        """
        try:
            # Handle test_mode where self.w3 is None
            if not self.w3:
                # In test mode, return a mock successful response with predefined example hashes
                return {
                    'success': True,
                    'data': {
                        'hashes': [
                            "0x123abc0000000000000000000000000000000000000000000000000000000000",
                            "0x456def0000000000000000000000000000000000000000000000000000000000"
                        ]
                    }
                }

            # Check for Ethereum node connection
            if not self.w3.is_connected():
                return {'success': False, 'error': "Could not connect to Ethereum node."}

            # Check if the MedicalRecordRegistry contract instance is initialized
            if not self.medical_record_registry_contract:
                return {'success': False, 'error': "MedicalRecordRegistry contract not initialized."}

            # Call the 'getRecordHashesByPatient' function of the smart contract.
            # This is a read-only operation (.call()), so it doesn't create a transaction.
            # Note: With a standard Web3.HTTPProvider, this .call() is synchronous (blocking),
            # even within an async method. For true async behavior here, an AsyncHTTPProvider
            # and `await contract.functions.method(...).call()` would be needed.
            raw_hashes = self.medical_record_registry_contract.functions.getRecordHashesByPatient(patient_did).call()

            # The smart contract returns a list of bytes32 values.
            # Convert each bytes32 hash (represented as `bytes` in Python) to a hex string.
            hex_hashes = [f"0x{h.hex()}" for h in raw_hashes]

            return {
                'success': True,
                'data': {'hashes': hex_hashes} # Successfully retrieved hashes
            }

        except Exception as e:
            # Catch any other exceptions during the process.
            # In a production system, more specific exceptions (e.g., web3.exceptions.ContractLogicError
            # for reverts, or network-related errors) would ideally be caught and handled.
            # For now, a general exception is caught for robustness.
            # Consider logging the error `e` here for debugging purposes.
            error_message = str(e)
            # Example of how one might check for common revert messages if the exception string contains them.
            # This is basic and might need refinement based on actual error patterns.
            # if 'revert' in error_message.lower() or 'execution reverted' in error_message.lower():
            #     error_message = "Smart contract execution reverted. (Details: " + str(e) + ")"
            
            return {
                'success': False,
                'error': f"Failed to retrieve record hashes: {error_message}"
            }

_blockchain_service_instance = None

def get_blockchain_service():
    """
    Returns a singleton instance of the BlockchainService.
    Initializes the service if it hasn't been already.
    """
    global _blockchain_service_instance
    if _blockchain_service_instance is None:
        _blockchain_service_instance = BlockchainService(test_mode="PYTEST_CURRENT_TEST" in os.environ)
    return _blockchain_service_instance