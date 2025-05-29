# MediTrustAI

A blockchain-based medical record management system with AI integration for health data analysis.

## System Requirements

- Python 3.11 or higher
- PostgreSQL 15.x
- Node.js 20.x LTS or higher (for smart contract development)
- Ganache (for local blockchain development)

## Development Environment Setup

### 1. Database Setup (PostgreSQL)

1. Download PostgreSQL 15.x from the [official website](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
2. Run the installer with the following configuration:
   - Port: 5432 (default)
   - Password for 'postgres' user: postgres
   - Locale: Default
   - Components to install: minimal PostgreSQL Server and pgAdmin 4

3. After installation, create a new database:
   - Open pgAdmin 4
   - Create a new database named: `meditrustal`

### 2. Python Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MediTrustAl.git
   cd MediTrustAl
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   # OR
   .\venv\Scripts\activate  # For Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Blockchain Development Setup

1. Install Ganache:
   - Download from [Truffle Suite](https://trufflesuite.com/ganache/)
   - Install and run
   - Create a new workspace with RPC SERVER port: 7545

2. Setup smart contract:
   ```bash
   cd blockchain
   npm install
   npx hardhat compile
   npx hardhat run scripts/deploy.js --network ganache
   ```

### 4. Environment Configuration

1. Create a `.env` file in the project root:
   ```env
   GANACHE_RPC_URL=http://127.0.0.1:7545 # Ensure Ganache is running on port 7545
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/meditrustal
   JWT_SECRET_KEY=your-secret-key-for-jwt
   ```

2. Run database migrations:
   ```bash
   python -m alembic -c ./alembic.ini upgrade head
   ```
   *Note: Ensure you run this command from the project root directory.*

### 5. Running the Application

1. Run the backend:
   ```bash
   uvicorn src.app.main:app --reload
   ```

2. Access API documentation:
   - http://localhost:8000/docs (Swagger UI)
   - http://localhost:8000/redoc (ReDoc)

## Implementation Status

- [x] Medical record management implementation (MVP Core)
- [x] Blockchain integration (UserRegistry & MedicalRecordRegistry)
- [x] User authentication and registration system
- [x] AI/NLP integration (Placeholder implemented)
- [x] Unit & integration testing for main features
- [ ] AI Predictive Service (Placeholder, next step)

## Testing

### Unit Testing
```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src

# Run specific tests
pytest tests/test_specific_file.py
```

### Smart Contract Testing
```bash
# In the blockchain/ directory
npx hardhat test
```

### Developer Notes
- **Endpoint `/api/v1/medical-records/patient/me`**: Retrieving medical records through this endpoint depends on the `BlockchainService` which returns the medical record hashes (data_hash) associated with the patient's DID via the `get_record_hashes_for_patient` method. Note that:
  - The `get_record_hashes_for_patient` function returns an array of medical record hashes (data_hash) from the blockchain, not transaction hashes.
  - The `blockchain_record_id` column in the database stores the transaction hash (tx_hash) generated when recording the data_hash to the blockchain, not the data_hash itself.
  - Matching between hashes from the blockchain and medical records in the database is done using the `data_hash` column, not `blockchain_record_id`.
  - In local development and integration testing, ensure the `get_record_hashes_for_patient` method of the `BlockchainService` (mocked in `tests/conftest.py`) is configured to return hashes that correspond to the `data_hash` column in the database for medical records to appear.

- **Database Column Names vs ORM Model Attributes**: Note that there are naming differences between columns in the database and attributes in the ORM model:
  - The `record_metadata` column in the database (previously named `metadata` in migration files) is mapped to the `record_metadata` attribute in the ORM and Pydantic models.
  - If you are using direct SQL or other database tools, make sure to refer to the correct column name (`record_metadata`).


## Troubleshooting

### Database Issues
1. **Error: Connection refused**
   - Ensure PostgreSQL service is running
   - Verify port 5432 is not used by another application
   - Check credentials in `.env` match PostgreSQL setup

2. **Error: Database meditrustal does not exist**
   - Create the database via pgAdmin 4
   - Or use the command: `createdb meditrustal`

### Blockchain Issues
1. **Error: Cannot connect to Ganache**
   - Ensure Ganache is running
   - Verify RPC URL in `.env` matches Ganache settings
   - Default port: 7545

2. **Error: Contract deployment failed**
   - Ensure there is ETH in the Ganache account
   - Check network configuration in `hardhat.config.js`

### Python Environment Issues
1. **Error: Module not found**
   - Ensure virtual environment is active
   - Run `pip install -r requirements.txt`
   - Check `PYTHONPATH` includes project root

2. **Error: Import error src.app**
   - Run the application from the root directory
   - Add project root to PYTHONPATH

## Project Structure

```
MediTrustAl/
├── src/
│   └── app/
│       ├── core/          # Core configuration
│       ├── models/        # Database models
│       ├── schemas/       # Pydantic schemas
│       └── api/           # API endpoints
├── blockchain/            # Smart contracts
├── alembic/              # Database migrations
└── tests/                # Unit tests
```

## Implementation Status 

- [x] Basic project setup
- [x] UserRegistry smart contract implementation
- [x] Blockchain integration with FastAPI
- [x] PostgreSQL database setup
- [x] Basic authentication implementation
- [ ] Medical record management implementation
- [ ] AI integration for analysis
- [ ] Frontend development

## Contribution

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

## License

[MIT License](LICENSE)