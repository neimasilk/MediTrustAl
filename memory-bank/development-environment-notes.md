# Development Environment Setup

## System Requirements

### Operating System
- **Windows:** Windows 10 (20H2) or newer
- **macOS:** Catalina (10.15) or newer
- **Linux:** Ubuntu 20.04 LTS or newer

### Hardware Requirements
1. **Minimum Specifications**
   - CPU: 4 cores
   - RAM: 8GB
   - Storage: 20GB free space
   - Network: Stable internet connection

2. **Recommended Specifications**
   - CPU: 8 cores
   - RAM: 16GB
   - Storage: 50GB SSD
   - Network: 10Mbps+ stable connection

### Disk Space Allocation
```
Project Directory (~20GB):
├── Source Code: 500MB
├── Dependencies: 2GB
├── Database: 5GB
├── Blockchain Data: 10GB
├── Logs: 1GB
└── Backups: 1.5GB
```

## Required Software

1. **Python Environment**
   - Python 3.11 or higher
   - pip (latest version)
   - virtualenv or venv

2. **Database**
   - PostgreSQL 15.x
   - pgAdmin 4 (optional but recommended)

3. **Blockchain Development**
   - Ganache 7.x (for local blockchain)
   - Node.js 20.x LTS (for web3 tools)
   - Truffle Suite (for smart contract development)

4. **Frontend Development**
   - Node.js 20.x LTS
   - npm 10.x or yarn 1.22.x
   - VS Code with extensions:
     * ESLint
     * Prettier
     * React Developer Tools

5. **Development Tools**
   - Git 2.x
   - Visual Studio Code
   - Postman (for API testing)

## Initial Setup Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-org/MediTrustAl.git
   cd MediTrustAl
   ```

2. **Python Environment Setup**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix/MacOS
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   # Create database
   createdb meditrustal_dev
   
   # Run migrations
   cd src
   alembic upgrade head
   ```

4. **Local Blockchain Setup**
   ```bash
   # Install Truffle globally
   npm install -g truffle@5.11.5
   
   # Install Ganache
   npm install -g ganache@7.9.2
   
   # Start local blockchain
   ganache --deterministic
   ```

5. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Environment Variables

Create a `.env` file in the project root:

```env
# System
NODE_ENV=development
DEBUG=True
LOG_LEVEL=debug

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/meditrustal_dev
DB_MAX_CONNECTIONS=20
DB_IDLE_TIMEOUT=300

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Blockchain
BLOCKCHAIN_PROVIDER_URL=http://127.0.0.1:8545
CHAIN_ID=1337
GAS_PRICE=20000000000
GAS_LIMIT=6721975

# API
API_V1_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT_ENABLED=true

# Security
BCRYPT_ROUNDS=12
ALLOWED_HOSTS=localhost,127.0.0.1
SSL_ENABLED=false
```

## Development Workflow

1. **Start Development Servers**
   ```bash
   # Terminal 1: Backend
   cd src
   uvicorn app.main:app --reload --port 8000
   
   # Terminal 2: Blockchain
   ganache --deterministic
   
   # Terminal 3: Frontend
   cd frontend
   npm run dev
   ```

2. **Running Tests**
   ```bash
   # Run backend tests
   pytest
   
   # Run frontend tests
   cd frontend
   npm test
   ```

3. **Code Quality**
   ```bash
   # Backend
   black src/
   flake8 src/
   
   # Frontend
   cd frontend
   npm run lint
   npm run format
   ```

## Troubleshooting

1. **Database Connection Issues**
   - Verify PostgreSQL is running: `pg_isready`
   - Check connection string in `.env`
   - Ensure database exists: `psql -l`

2. **Blockchain Connection Issues**
   - Verify Ganache is running: `curl http://127.0.0.1:8545`
   - Check Ganache logs for errors
   - Reset Ganache if needed: `ganache --deterministic --force`

3. **Python Environment Issues**
   - Recreate virtualenv if needed
   - Update pip: `python -m pip install --upgrade pip`
   - Clear pip cache: `pip cache purge`

## VS Code Configuration

Add these settings to `.vscode/settings.json`:

```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## Git Hooks (Optional)

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
-   repo: https://github.com/psf/black
    rev: 24.2.0
    hooks:
    -   id: black
-   repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
    -   id: flake8
```