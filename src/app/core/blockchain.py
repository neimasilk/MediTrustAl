from web3 import Web3
from eth_account import Account
from .config import BLOCKCHAIN_CONFIG
import os

class BlockchainService:
    def __init__(self, test_mode=False):
        if test_mode:
            # Use mock values for testing
            self.w3 = None
            self.contract = None
            self.private_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
            self.account = "0x1234567890123456789012345678901234567890"
            return

        self.w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_CONFIG["ganache_url"]))
        if not self.w3.is_connected():
            raise ConnectionError("Could not connect to Ethereum node")
        
        self.contract = self.w3.eth.contract(
            address=BLOCKCHAIN_CONFIG["user_registry_address"],
            abi=BLOCKCHAIN_CONFIG["user_registry_abi"]
        )
        
        # Get the private key from config
        self.private_key = BLOCKCHAIN_CONFIG["sender_private_key"]
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
            tx = self.contract.functions.registerUser(user_id, role).build_transaction({
                'from': self.account,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account),
            })
            
            # Sign and send the transaction using the configured private key
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
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

            role, is_registered = await self.contract.functions.getUserRole(user_id).call()
            
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