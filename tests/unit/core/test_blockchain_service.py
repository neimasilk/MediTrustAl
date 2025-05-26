import pytest
from unittest.mock import MagicMock, patch
import os

from src.app.core.blockchain import BlockchainService, get_blockchain_service
from src.app.core.config import BLOCKCHAIN_CONFIG

# Ensure critical env vars for BlockchainService are set for testing context
# These might be already set in conftest.py, but explicit here for clarity if this test is run standalone.
os.environ["GANACHE_RPC_URL"] = os.getenv("GANACHE_RPC_URL", "http://127.0.0.1:8545") # Use a different port if main conftest uses 7545
os.environ["BLOCKCHAIN_SENDER_PRIVATE_KEY"] = os.getenv("BLOCKCHAIN_SENDER_PRIVATE_KEY", "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")


@pytest.fixture
def mock_web3_and_contracts():
    """
    Mocks Web3 instance and contract objects used by BlockchainService.
    This fixture provides fine-grained control over contract interactions for unit testing.
    """
    mock_w3 = MagicMock()
    mock_w3.is_connected.return_value = True
    
    # Mock UserRegistry contract
    mock_user_registry_contract = MagicMock()
    
    # Mock MedicalRecordRegistry contract
    mock_medical_record_registry_contract = MagicMock()
    
    # Mock transaction receipt
    mock_tx_receipt = MagicMock()
    mock_tx_receipt.status = 1 # Simulate successful transaction
    mock_tx_receipt.transactionHash.hex.return_value = "0xmockedtransactionhash"

    # Setup contract functions
    mock_medical_record_registry_contract.functions.addRecord.return_value.build_transaction.return_value = {}
    mock_w3.eth.account.sign_transaction.return_value = MagicMock(rawTransaction=b"raw_tx_bytes")
    mock_w3.eth.send_raw_transaction.return_value = b"tx_hash_bytes"
    mock_w3.eth.wait_for_transaction_receipt.return_value = mock_tx_receipt
    mock_w3.eth.get_transaction_count.return_value = 1 # Mock nonce
    mock_w3.eth.gas_price = 10**9 # Mock gas price (1 Gwei)
    
    # Patch BLOCKCHAIN_CONFIG to simulate loaded contract ABIs and addresses
    # This is crucial because BlockchainService __init__ tries to load them
    original_user_reg_addr = BLOCKCHAIN_CONFIG.get("user_registry_address")
    original_user_reg_abi = BLOCKCHAIN_CONFIG.get("user_registry_abi")
    original_med_rec_reg_addr = BLOCKCHAIN_CONFIG.get("medical_record_registry_address")
    original_med_rec_reg_abi = BLOCKCHAIN_CONFIG.get("medical_record_registry_abi")

    BLOCKCHAIN_CONFIG["user_registry_address"] = "0xMockUserRegistryAddress"
    BLOCKCHAIN_CONFIG["user_registry_abi"] = [{"type": "function", "name": "mockFunction"}] # Simplified ABI
    BLOCKCHAIN_CONFIG["medical_record_registry_address"] = "0xMockMedicalRecordRegistryAddress"
    BLOCKCHAIN_CONFIG["medical_record_registry_abi"] = [{"type": "function", "name": "addRecord"}] # Simplified ABI
    
    with patch('src.app.core.blockchain.Web3', return_value=mock_w3):
        # Re-initialize service with mocks in place for contract loading
        # Need to reset the global singleton to force re-initialization
        from src.app.core import blockchain as blockchain_module
        blockchain_module._blockchain_service_instance = None
        service = get_blockchain_service() # This will now use the mocked Web3 and config

        # Directly assign mocked contracts if initialization logic is complex or doesn't pick them up via config alone
        service.user_registry_contract = mock_user_registry_contract
        service.medical_record_registry_contract = mock_medical_record_registry_contract
        service.w3 = mock_w3 # Ensure the service's w3 instance is the mocked one

        yield service, mock_w3, mock_user_registry_contract, mock_medical_record_registry_contract, mock_tx_receipt

    # Restore original BLOCKCHAIN_CONFIG values after test
    BLOCKCHAIN_CONFIG["user_registry_address"] = original_user_reg_addr
    BLOCKCHAIN_CONFIG["user_registry_abi"] = original_user_reg_abi
    BLOCKCHAIN_CONFIG["medical_record_registry_address"] = original_med_rec_reg_addr
    BLOCKCHAIN_CONFIG["medical_record_registry_abi"] = original_med_rec_reg_abi
    
    # Reset the global singleton again after tests
    from src.app.core import blockchain as blockchain_module
    blockchain_module._blockchain_service_instance = None


@pytest.mark.asyncio
async def test_add_medical_record_hash_success(mock_web3_and_contracts):
    """
    Test successful addition of a medical record hash.
    """
    service, mock_w3, _, mock_medical_record_contract, _ = mock_web3_and_contracts
    
    record_hash_hex = "0x" + "a" * 64 # 32 bytes hex string
    patient_did = "did:example:123"
    record_type = "DIAGNOSIS"

    result = await service.add_medical_record_hash(record_hash_hex, patient_did, record_type)

    assert result['success'] is True
    assert result['transaction_hash'] == "0xmockedtransactionhash"
    
    # Verify contract call
    record_hash_bytes32 = bytes.fromhex(record_hash_hex[2:])
    mock_medical_record_contract.functions.addRecord.assert_called_once_with(
        record_hash_bytes32, patient_did, record_type
    )
    # Verify transaction building, signing, and sending
    mock_medical_record_contract.functions.addRecord().build_transaction.assert_called_once()
    mock_w3.eth.account.sign_transaction.assert_called_once()
    mock_w3.eth.send_raw_transaction.assert_called_once()
    mock_w3.eth.wait_for_transaction_receipt.assert_called_once()


@pytest.mark.asyncio
async def test_add_medical_record_hash_transaction_failure(mock_web3_and_contracts):
    """
    Test handling of a failed blockchain transaction (status 0 in receipt).
    """
    service, mock_w3, _, mock_medical_record_contract, mock_tx_receipt = mock_web3_and_contracts
    
    # Simulate transaction failure
    mock_tx_receipt.status = 0 
    mock_w3.eth.wait_for_transaction_receipt.return_value = mock_tx_receipt

    record_hash_hex = "0x" + "b" * 64
    patient_did = "did:example:456"
    record_type = "LAB_RESULT"

    result = await service.add_medical_record_hash(record_hash_hex, patient_did, record_type)

    assert result['success'] is False
    assert result['error'] == "Transaction failed on blockchain."
    assert result['transaction_hash'] == "0xmockedtransactionhash"

@pytest.mark.asyncio
async def test_add_medical_record_hash_invalid_hash_length(mock_web3_and_contracts):
    """
    Test that add_medical_record_hash raises ValueError for incorrect hash length.
    """
    service, _, _, _, _ = mock_web3_and_contracts
    
    invalid_hash_hex = "0x12345" # Too short
    patient_did = "did:example:789"
    record_type = "PRESCRIPTION"

    result = await service.add_medical_record_hash(invalid_hash_hex, patient_did, record_type)
    assert result['success'] is False
    assert "Record hash hex string must be 64 characters" in result['error']

@pytest.mark.asyncio
async def test_add_medical_record_hash_no_sender_key(mock_web3_and_contracts):
    """
    Test behavior when sender private key is not configured.
    """
    service, _, _, _, _ = mock_web3_and_contracts
    original_private_key = service.private_key
    service.private_key = None # Simulate missing key

    record_hash_hex = "0x" + "c" * 64
    patient_did = "did:example:101"
    record_type = "TREATMENT_PLAN"

    result = await service.add_medical_record_hash(record_hash_hex, patient_did, record_type)
    assert result['success'] is False
    assert "Blockchain sender private key not configured" in result['error']
    
    service.private_key = original_private_key # Restore key

@pytest.mark.asyncio
async def test_add_medical_record_hash_contract_not_initialized(mock_web3_and_contracts):
    """
    Test behavior when MedicalRecordRegistry contract is not initialized.
    """
    service, _, _, _, _ = mock_web3_and_contracts
    original_contract = service.medical_record_registry_contract
    service.medical_record_registry_contract = None # Simulate uninitialized contract

    record_hash_hex = "0x" + "d" * 64
    patient_did = "did:example:112"
    record_type = "VACCINATION"

    result = await service.add_medical_record_hash(record_hash_hex, patient_did, record_type)
    assert result['success'] is False
    assert "MedicalRecordRegistry contract is not initialized" in result['error']
    
    service.medical_record_registry_contract = original_contract # Restore contract

@pytest.mark.asyncio
async def test_add_medical_record_hash_web3_not_connected(mock_web3_and_contracts):
    """
    Test behavior when Web3 is not connected.
    """
    service, mock_w3, _, _, _ = mock_web3_and_contracts
    
    # Simulate Web3 not connected *after* service initialization for this specific test case
    # The main mock_web3_and_contracts fixture sets it to connected.
    # We need to mock the w3 instance *within* the service that was already created.
    service.w3.is_connected.return_value = False


    record_hash_hex = "0x" + "e" * 64
    patient_did = "did:example:113"
    record_type = "IMAGING"

    result = await service.add_medical_record_hash(record_hash_hex, patient_did, record_type)
    assert result['success'] is False
    assert "Could not connect to Ethereum node" in result['error']
    
    service.w3.is_connected.return_value = True # Restore for other tests if service instance is reused by other tests (though fixture should prevent this)

# To consider: Test for specific exceptions during build_transaction, sign_transaction, send_raw_transaction
# These would involve making the mock objects raise exceptions when their methods are called.
# Example:
# async def test_add_medical_record_hash_signing_error(mock_web3_and_contracts):
#     service, mock_w3, _, _, _ = mock_web3_and_contracts
#     mock_w3.eth.account.sign_transaction.side_effect = Exception("Signing failed")
#     ...
#     result = await service.add_medical_record_hash(...)
#     assert result['success'] is False
#     assert "Signing failed" in result['error']
