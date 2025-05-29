# Testing Strategy

## Overview

MediTrustAl adopts a comprehensive testing approach to ensure system quality and reliability. This strategy covers various levels of testing from unit tests to end-to-end tests.

## Test Levels

### 1. Unit Testing

#### Requirements
- Minimum coverage: 80% for new code
- Use pytest as the test framework
- Every new function must have a unit test
- Mock external dependencies (database, blockchain, etc.)

#### Structure
```
tests/
├── unit/
│   ├── api/
│   ├── core/
│   ├── models/
│   └── services/
```

#### Conventions
```python
# Example test file structure
def test_should_do_something():
    # Arrange
    input_data = ...
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

### 2. Integration Testing

#### Scope
- Database interactions
- API endpoints
- Blockchain interactions
- External service integrations

#### Requirements
- Use a separate test database
- Clean state before each test
- Minimum one happy path and one error case for each endpoint

#### Structure
```
tests/
├── integration/
│   ├── api/
│   ├── blockchain/
│   └── database/
```

### 3. Contract Testing

#### Smart Contract Testing
- Unit tests for each function in the contract
- Gas optimization tests
- Security vulnerability tests
- Integration tests with the backend

#### API Contract Testing
- OpenAPI/Swagger validation
- Response schema validation
- Error handling validation

### 4. End-to-End Testing

#### Scope
- Critical user journeys
- Cross-component interactions
- Real environment testing

#### Tools
- Selenium/Playwright for UI testing
- Postman/Newman for API testing
- GitHub Actions for CI/CD integration

## Test Environment

### Local Development
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test category
pytest tests/unit/
pytest tests/integration/

# Run with verbose output
pytest -v

# Generate coverage report
pytest --cov=src --cov-report=html
```

### CI Environment
- Automated tests on pull requests
- Coverage reports in PR comments
- Required status checks before merge

## Coverage Requirements

### Backend (Python)
- Lines: minimum 80%
- Branches: minimum 70%
- Functions: minimum 90%

### Smart Contracts (Solidity)
- Lines: minimum 95%
- Branches: minimum 90%
- Functions: minimum 100%

### Frontend (Future)
- Components: minimum 80%
- User interactions: minimum 70%

## Test Data Management

### Fixtures
- Use pytest fixtures for reusable test data
- Maintain separate test data sets
- Version control test data

### Mocking Strategy
- Use pytest-mock for Python mocking
- Mock external services by default
- Document mock behaviors

## Security Testing

### Requirements
- Regular vulnerability scanning
- Penetration testing before major releases
- Security audit of dependencies

### Tools
- Safety for Python dependency checking
- Slither for Solidity security analysis
- OWASP ZAP for security testing

## Performance Testing

### Scope
- API response times
- Database query performance
- Smart contract gas optimization

### Tools
- Locust for load testing
- pytest-benchmark for performance testing
- eth-gas-reporter for gas analysis

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=src
          pytest tests/integration/
```

## Reporting

### Coverage Reports
- HTML reports generated after test runs
- Coverage trends tracked over time
- Regular coverage review meetings

### Test Results
- JUnit XML format for CI integration
- Detailed failure analysis
- Historical test results tracking

## Best Practices

1. **Test Independence**
   - Each test should be able to run in isolation
   - No dependencies between tests
   - Clean up after each test

2. **Test Readability**
   - Clear test names describing behavior
   - Well-structured arrange-act-assert pattern
   - Documented test purpose and edge cases

3. **Maintenance**
   - Regular review of test suite
   - Remove obsolete tests
   - Update tests with code changes

4. **Documentation**
   - Document test setup requirements
   - Maintain testing guidelines
   - Update documentation with new patterns

## Test Naming and Organization

### File Naming Convention
```
test_[module]_[class/function]_[scenario].py
```

Examples:
- `test_auth_login_success.py`
- `test_medical_record_creation_valid.py`
- `test_blockchain_transaction_verification.py`

### Class/Function Naming
```python
def test_should_[expected_behavior]_when_[condition]():
    pass

class TestUserAuthentication:
    def test_should_create_user_when_valid_data(self):
        pass
    
    def test_should_fail_when_invalid_password(self):
        pass
```

### Directory Structure
```
tests/
├── unit/
│   ├── auth/
│   │   ├── test_login.py
│   │   └── test_registration.py
│   ├── blockchain/
│   │   ├── test_smart_contracts.py
│   │   └── test_transactions.py
│   └── medical_records/
│       ├── test_creation.py
│       └── test_validation.py
├── integration/
│   ├── api/
│   ├── blockchain/
│   └── database/
└── e2e/
    └── scenarios/
```

## Blockchain Testing Tools

### Local Blockchain Testing
- **Ganache CLI** for local blockchain simulation
- **Hardhat Network** for advanced testing features
- **eth-tester** for Python-based Ethereum testing

### Smart Contract Testing
```python
# Example using eth-tester
from eth_tester import EthereumTester
from web3 import Web3, EthereumTesterProvider

def test_medical_record_creation():
    # Setup
    eth_tester = EthereumTester()
    web3 = Web3(EthereumTesterProvider(eth_tester))
    
    # Deploy contract
    contract = deploy_contract(web3)
    
    # Test
    tx_hash = contract.functions.createMedicalRecord(
        patient_id=1,
        record_type="DIAGNOSIS",
        data_hash="0x123..."
    ).transact()
    
    # Assert
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    assert receipt.status == 1

```

### Mocking Blockchain Interactions
```python
from unittest.mock import patch
from web3.providers.eth_tester import EthereumTesterProvider

class MockWeb3:
    def __init__(self):
        self.eth = EthereumTesterProvider()
        
    def create_transaction(self):
        return "0x123..."

@patch('services.blockchain.Web3', MockWeb3)
def test_blockchain_service():
    service = BlockchainService()
    result = service.create_transaction()
    assert result == "0x123..."
```

### Contract Testing Tools
- **Brownie** for Python-based contract testing
- **Truffle** for JavaScript contract testing
- **Slither** for security analysis 