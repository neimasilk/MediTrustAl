from web3 import Web3
from .config import BLOCKCHAIN_CONFIG

class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_CONFIG["ganache_url"]))
        if not self.w3.is_connected():
            raise ConnectionError("Could not connect to Ethereum node")
        
        self.contract = self.w3.eth.contract(
            address=BLOCKCHAIN_CONFIG["user_registry_address"],
            abi=BLOCKCHAIN_CONFIG["user_registry_abi"]
        )
        
        # Get the default account to use for transactions
        self.account = self.w3.eth.accounts[0]
        
    async def register_user(self, user_id: str, role: str) -> dict:
        """
        Register a new user in the blockchain
        """
        try:
            # Build the transaction
            tx = self.contract.functions.registerUser(user_id, role).build_transaction({
                'from': self.account,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account),
            })
            
            # Sign and send the transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=None)  # Note: In production, handle private key securely
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

# Create a singleton instance
blockchain_service = BlockchainService() 