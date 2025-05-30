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


@pytest.mark.asyncio
async def test_get_record_hashes_for_patient_success(mock_web3_and_contracts):
    """
    Test successful retrieval of record hashes for a patient.
    """
    service, _, _, mock_medical_record_contract, _ = mock_web3_and_contracts
    patient_did = "did:example:patient1"
    mock_hashes_bytes = [
        b'\x12\x34\x56\x78\x90\xab\xcd\xef\x12\x34\x56\x78\x90\xab\xcd\xef\x12\x34\x56\x78\x90\xab\xcd\xef\x12\x34\x56\x78\x90\xab\xcd\xef',
        b'\xfe\xdc\xba\x09\x87\x65\x43\x21\xfe\xdc\xba\x09\x87\x65\x43\x21\xfe\xdc\xba\x09\x87\x65\x43\x21\xfe\xdc\xba\x09\x87\x65\x43\x21'
    ]
    expected_hex_hashes = [
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "0xfedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321"
    ]

    # Revised mock setup:
    # Mock the specific function 'getRecordHashesByPatient'
    mock_get_hashes_func = mock_medical_record_contract.functions.getRecordHashesByPatient
    # Set the return_value for the 'call()' method on the object returned by 'getRecordHashesByPatient(patient_did)'
    mock_get_hashes_func.return_value.call.return_value = mock_hashes_bytes

    result = await service.get_record_hashes_for_patient(patient_did)

    assert result['success'] is True
    assert result['data']['hashes'] == expected_hex_hashes
    # Assert that 'getRecordHashesByPatient' itself was called once with the correct patient_did
    mock_get_hashes_func.assert_called_once_with(patient_did)


@pytest.mark.asyncio
async def test_get_record_hashes_for_patient_empty_list(mock_web3_and_contracts):
    """
    Test retrieval of an empty list of record hashes.
    """
    service, _, _, mock_medical_record_contract, _ = mock_web3_and_contracts
    patient_did = "did:example:patient2"
    
    # Revised mock setup
    mock_get_hashes_func = mock_medical_record_contract.functions.getRecordHashesByPatient
    mock_get_hashes_func.return_value.call.return_value = []

    result = await service.get_record_hashes_for_patient(patient_did)

    assert result['success'] is True
    assert result['data']['hashes'] == []
    mock_get_hashes_func.assert_called_once_with(patient_did)


@pytest.mark.asyncio
async def test_get_record_hashes_for_patient_contract_not_initialized(mock_web3_and_contracts):
    """
    Test behavior when MedicalRecordRegistry contract is not initialized.
    """
    service, mock_w3, _, _, _ = mock_web3_and_contracts
    # Ensure w3 is connected to bypass that check
    service.w3.is_connected.return_value = True 
    
    original_contract = service.medical_record_registry_contract
    service.medical_record_registry_contract = None # Simulate uninitialized contract
    patient_did = "did:example:patient3"

    result = await service.get_record_hashes_for_patient(patient_did)

    assert result['success'] is False
    assert result['error'] == "MedicalRecordRegistry contract not initialized."
    
    service.medical_record_registry_contract = original_contract # Restore


@pytest.mark.asyncio
async def test_get_record_hashes_for_patient_web3_not_connected(mock_web3_and_contracts):
    """
    Test behavior when Web3 provider is not connected.
    """
    service, mock_w3, _, mock_medical_record_contract, _ = mock_web3_and_contracts
     # Ensure contract is "initialized" to pass that check
    assert service.medical_record_registry_contract is not None

    service.w3.is_connected.return_value = False # Simulate not connected
    patient_did = "did:example:patient4"

    result = await service.get_record_hashes_for_patient(patient_did)

    assert result['success'] is False
    assert result['error'] == "Could not connect to Ethereum node."
    
    service.w3.is_connected.return_value = True # Restore for other tests


@pytest.mark.asyncio
async def test_get_record_hashes_for_patient_contract_call_exception(mock_web3_and_contracts):
    """
    Test handling of an exception during the contract call.
    """
    service, _, _, mock_medical_record_contract, _ = mock_web3_and_contracts
    patient_did = "did:example:patient5"
    
    # Revised mock setup
    mock_get_hashes_func = mock_medical_record_contract.functions.getRecordHashesByPatient
    mock_get_hashes_func.return_value.call.side_effect = Exception("Blockchain RPC error")

    result = await service.get_record_hashes_for_patient(patient_did)

    assert result['success'] is False
    assert result['error'] == "Failed to retrieve record hashes: Blockchain RPC error"
    mock_get_hashes_func.assert_called_once_with(patient_did)


@pytest.mark.asyncio
async def test_get_record_hashes_for_patient_test_mode(mock_web3_and_contracts):
    """
    Test behavior in test_mode (service.w3 is None).
    """
    # Need to re-initialize service in test_mode, fixture might not cover this specific state for service.w3
    # The fixture sets up a mocked w3, so we override it for this test.
    
    with patch('src.app.core.blockchain.Web3') as MockWeb3: # Mock Web3 to prevent actual instantiation
        # Reset the global service instance
        from src.app.core import blockchain as blockchain_module
        blockchain_module._blockchain_service_instance = None
        
        # Instantiate service in test_mode (which should make self.w3 = None)
        # To ensure test_mode=True, we can patch os.environ or directly init BlockchainService(test_mode=True)
        # For simplicity and isolation, directly initialize.
        service_test_mode = BlockchainService(test_mode=True) 
        assert service_test_mode.w3 is None # Confirm test_mode setup

        patient_did = "did:example:patient_test_mode"
        result = await service_test_mode.get_record_hashes_for_patient(patient_did)

        assert result['success'] is True
        assert 'hashes' in result['data']
        # Check for the specific mock values defined in BlockchainService test_mode
        assert result['data']['hashes'] == [
            "0x123abc0000000000000000000000000000000000000000000000000000000000",
            "0x456def0000000000000000000000000000000000000000000000000000000000"
        ]

        # Reset global instance again so other tests use the fixtured one
        blockchain_module._blockchain_service_instance = None


@pytest.mark.asyncio
async def test_grant_record_access_success(mock_web3_and_contracts):
    service, mock_w3, _, mock_medical_record_contract, mock_tx_receipt = mock_web3_and_contracts
    
    record_hash_hex = "0x" + "a" * 64
    doctor_address = "0x1234567890123456789012345678901234567890" # Valid address

    # Mock the specific contract function call
    mock_medical_record_contract.functions.grantAccess.return_value.build_transaction.return_value = {'gas': 200000}
    mock_w3.eth.wait_for_transaction_receipt.return_value = mock_tx_receipt
    mock_tx_receipt.status = 1 # Ensure success

    result = await service.grant_record_access(record_hash_hex, doctor_address)

    assert result['success'] is True
    assert result['transaction_hash'] == "0xmockedtransactionhash"
    assert result['record_hash'] == record_hash_hex
    assert result['doctor_address'] == doctor_address
    
    record_hash_bytes32 = bytes.fromhex(record_hash_hex[2:])
    mock_medical_record_contract.functions.grantAccess.assert_called_once_with(
        record_hash_bytes32, doctor_address
    )
    mock_medical_record_contract.functions.grantAccess().build_transaction.assert_called_once()


@pytest.mark.asyncio
async def test_grant_record_access_revert(mock_web3_and_contracts):
    service, mock_w3, _, mock_medical_record_contract, mock_tx_receipt = mock_web3_and_contracts
    
    record_hash_hex = "0x" + "b" * 64
    doctor_address = "0x0987654321098765432109876543210987654321"

    # Simulate a transaction revert (status 0)
    mock_tx_receipt.status = 0
    mock_medical_record_contract.functions.grantAccess.return_value.build_transaction.return_value = {'gas': 200000}
    mock_w3.eth.wait_for_transaction_receipt.return_value = mock_tx_receipt
    
    result = await service.grant_record_access(record_hash_hex, doctor_address)

    assert result['success'] is False
    assert result['error'] == "Transaction to grant access failed on blockchain."
    assert result['transaction_hash'] == "0xmockedtransactionhash"


@pytest.mark.asyncio
async def test_grant_record_access_invalid_doctor_address(mock_web3_and_contracts):
    service, mock_w3, _, _, _ = mock_web3_and_contracts
    record_hash_hex = "0x" + "c" * 64
    invalid_doctor_address = "0xInvalidAddress"

    mock_w3.is_address.return_value = False # Simulate invalid address

    result = await service.grant_record_access(record_hash_hex, invalid_doctor_address)
    
    assert result['success'] is False
    assert "Invalid Ethereum address format for doctor" in result['error']
    mock_w3.is_address.assert_called_with(invalid_doctor_address)


@pytest.mark.asyncio
async def test_grant_record_access_contract_call_exception(mock_web3_and_contracts):
    service, mock_w3, _, mock_medical_record_contract, _ = mock_web3_and_contracts
    record_hash_hex = "0x" + "d" * 64
    doctor_address = "0xValidAddress00000000000000000000000000000"
    mock_w3.is_address.return_value = True # Assume address is valid

    # Simulate an exception during the contract call (e.g., build_transaction)
    mock_medical_record_contract.functions.grantAccess.return_value.build_transaction.side_effect = Exception("Build TX Error")
    
    result = await service.grant_record_access(record_hash_hex, doctor_address)

    assert result['success'] is False
    assert "An unexpected error occurred during grantAccess: Build TX Error" in result['error']


@pytest.mark.asyncio
async def test_revoke_record_access_success(mock_web3_and_contracts):
    service, mock_w3, _, mock_medical_record_contract, mock_tx_receipt = mock_web3_and_contracts
    record_hash_hex = "0x" + "e" * 64
    doctor_address = "0xDoctorAddressForRevokeSuccess0000000000"
    mock_w3.is_address.return_value = True

    mock_medical_record_contract.functions.revokeAccess.return_value.build_transaction.return_value = {'gas': 200000}
    mock_w3.eth.wait_for_transaction_receipt.return_value = mock_tx_receipt
    mock_tx_receipt.status = 1

    result = await service.revoke_record_access(record_hash_hex, doctor_address)

    assert result['success'] is True
    assert result['transaction_hash'] == "0xmockedtransactionhash"
    record_hash_bytes32 = bytes.fromhex(record_hash_hex[2:])
    mock_medical_record_contract.functions.revokeAccess.assert_called_once_with(
        record_hash_bytes32, doctor_address
    )
    mock_medical_record_contract.functions.revokeAccess().build_transaction.assert_called_once()


@pytest.mark.asyncio
async def test_revoke_record_access_revert(mock_web3_and_contracts):
    service, mock_w3, _, mock_medical_record_contract, mock_tx_receipt = mock_web3_and_contracts
    record_hash_hex = "0x" + "f" * 64
    doctor_address = "0xDoctorAddressForRevokeRevert0000000000"
    mock_w3.is_address.return_value = True
    
    mock_tx_receipt.status = 0 # Simulate revert
    mock_medical_record_contract.functions.revokeAccess.return_value.build_transaction.return_value = {'gas': 200000}
    mock_w3.eth.wait_for_transaction_receipt.return_value = mock_tx_receipt

    result = await service.revoke_record_access(record_hash_hex, doctor_address)

    assert result['success'] is False
    assert result['error'] == "Transaction to revoke access failed on blockchain."


@pytest.mark.asyncio
async def test_revoke_record_access_invalid_doctor_address(mock_web3_and_contracts):
    service, mock_w3, _, _, _ = mock_web3_and_contracts
    record_hash_hex = "0x" + "g" * 64
    invalid_doctor_address = "0xInvalidRevokeAddress"
    mock_w3.is_address.return_value = False

    result = await service.revoke_record_access(record_hash_hex, invalid_doctor_address)

    assert result['success'] is False
    assert "Invalid Ethereum address format for doctor" in result['error']
    mock_w3.is_address.assert_called_with(invalid_doctor_address)


@pytest.mark.asyncio
async def test_revoke_record_access_contract_call_exception(mock_web3_and_contracts):
    service, mock_w3, _, mock_medical_record_contract, _ = mock_web3_and_contracts
    record_hash_hex = "0x" + "a" * 64 # Changed 'h' to 'a'
    doctor_address = "0xValidRevokeAddress0000000000000000000000"
    mock_w3.is_address.return_value = True

    mock_medical_record_contract.functions.revokeAccess.return_value.build_transaction.side_effect = Exception("Revoke Build TX Error")
    
    result = await service.revoke_record_access(record_hash_hex, doctor_address)

    assert result['success'] is False
    assert "An unexpected error occurred during revokeAccess: Revoke Build TX Error" in result['error']


@pytest.mark.asyncio
async def test_check_record_access_success_has_access(mock_web3_and_contracts):
    service, mock_w3, _, mock_medical_record_contract, _ = mock_web3_and_contracts
    record_hash_hex = "0x" + "b" * 64 # Changed 'i' to 'b'
    accessor_address = "0xAccessorHasAccess0000000000000000000000"
    mock_w3.is_address.return_value = True

    # Simulate contract call returning True (has access)
    mock_medical_record_contract.functions.checkAccess.return_value.call.return_value = True

    result = await service.check_record_access(record_hash_hex, accessor_address)

    assert result['success'] is True
    assert result['has_access'] is True
    assert result['record_hash'] == record_hash_hex
    assert result['accessor_address'] == accessor_address
    
    record_hash_bytes32 = bytes.fromhex(record_hash_hex[2:])
    mock_medical_record_contract.functions.checkAccess.assert_called_once_with(
        record_hash_bytes32, accessor_address
    )
    mock_medical_record_contract.functions.checkAccess().call.assert_called_once()


@pytest.mark.asyncio
async def test_check_record_access_success_no_access(mock_web3_and_contracts):
    service, mock_w3, _, mock_medical_record_contract, _ = mock_web3_and_contracts
    record_hash_hex = "0x" + "c" * 64 # Changed 'j' to 'c'
    accessor_address = "0xAccessorNoAccess00000000000000000000000"
    mock_w3.is_address.return_value = True

    # Simulate contract call returning False (no access)
    mock_medical_record_contract.functions.checkAccess.return_value.call.return_value = False

    result = await service.check_record_access(record_hash_hex, accessor_address)

    assert result['success'] is True
    assert result['has_access'] is False
    mock_medical_record_contract.functions.checkAccess.assert_called_once()


@pytest.mark.asyncio
async def test_check_record_access_invalid_accessor_address(mock_web3_and_contracts):
    service, mock_w3, _, _, _ = mock_web3_and_contracts
    record_hash_hex = "0x" + "k" * 64
    invalid_accessor_address = "0xInvalidCheckAddress"
    mock_w3.is_address.return_value = False # Simulate invalid address

    result = await service.check_record_access(record_hash_hex, invalid_accessor_address)

    assert result['success'] is False
    assert "Invalid Ethereum address format for accessor" in result['error']
    mock_w3.is_address.assert_called_with(invalid_accessor_address)


@pytest.mark.asyncio
async def test_check_record_access_contract_call_exception(mock_web3_and_contracts):
    service, mock_w3, _, mock_medical_record_contract, _ = mock_web3_and_contracts
    record_hash_hex = "0x" + "d" * 64 # Changed 'l' to 'd'
    accessor_address = "0xValidCheckAddress00000000000000000000000"
    mock_w3.is_address.return_value = True

    # Simulate an exception during the contract's .call() method
    mock_medical_record_contract.functions.checkAccess.return_value.call.side_effect = Exception("CheckAccess Call Error")
    
    result = await service.check_record_access(record_hash_hex, accessor_address)

    assert result['success'] is False
    assert "An unexpected error occurred during checkAccess: CheckAccess Call Error" in result['error']


@pytest.mark.asyncio
async def test_check_record_access_test_mode(mock_web3_and_contracts):
    # This test needs to ensure BlockchainService is in test_mode (service.w3 is None)
    from src.app.core import blockchain as blockchain_module
    blockchain_module._blockchain_service_instance = None # Reset global instance
    service_test_mode = BlockchainService(test_mode=True)
    assert service_test_mode.w3 is None

    record_hash_hex = "0x" + "m" * 64
    
    # Test with the specific address mocked to have access in test_mode
    accessor_has_access = "0xDoctorHasAccess"
    result_has_access = await service_test_mode.check_record_access(record_hash_hex, accessor_has_access)
    assert result_has_access['success'] is True
    assert result_has_access['has_access'] is True

    # Test with another address mocked to not have access
    accessor_no_access = "0xAnotherDoctor"
    result_no_access = await service_test_mode.check_record_access(record_hash_hex, accessor_no_access)
    assert result_no_access['success'] is True
    assert result_no_access['has_access'] is False
    
    blockchain_module._blockchain_service_instance = None # Clean up global instance
