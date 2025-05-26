# **MediTrustAl \- MVP Implementation Plan (implementation-plan.md)**

## **0\. Introduction & Guiding Principles**

This document outlines the step-by-step plan for developing the Minimum Viable Product (MVP) of the MediTrustAl platform. This plan is intended for an AI developer (e.g., Claude Sonnet 3.7 Thinking in Cursor) and should be executed sequentially.

**Key Principles for AI Developer:**

* **Adherence to Documents:** Strictly follow the guidelines, requirements, and technology choices outlined in:  
  * memory-bank/prd\_meditrustal\_v1\_en.md (Product Requirements Document)  
  * memory-bank/meditrustal\_tech\_stack\_v1.md (Tech Stack Recommendation)  
  * memory-bank/meditrustal\_cursor\_rules\_v1.md (Cursor Rules) \- especially the "Always" rules and modularity principles.  
* **Modularity:** Implement features in a modular way, creating separate files and components as per the Cursor Rules.  
* **Incremental Development:** Each step should result in a testable increment of functionality.  
* **No Code in This Plan:** This document contains instructions and tests, not code.  
* **Focus:** This plan focuses on the MVP features. Advanced features will be planned separately.  
* **Testing:** After each step, the AI should wait for the human developer to validate the described tests before proceeding.  
* **Documentation:** After successful validation of a step, the AI will be instructed to update progress.md and architecture.md.

## **1\. Phase 1: Core Backend Setup & Blockchain Foundation (MVP Focus)**

### **Step 1.1: Project Setup and Basic Backend Structure**

* **Instruction:**
  1. Initialize a new project directory structure as follows:
     ```
     / (Root Repositori Anda)
     ├── src/
     │   └── app/
     │       ├── api/      # For API endpoint definitions (e.g., status_routes.py)
     │       ├── core/     # For configuration, settings (e.g., config.py)
     │       ├── models/   # For Pydantic models (e.g., status_models.py)
     │       └── main.py   # Main FastAPI application instance
     ├── tests/            # For automated tests
     ├── memory-bank/      # Existing planning documents
     ├── .gitignore
     ├── README.md
     └── requirements.txt  # For Python dependencies
     ```
  2. Set up the backend framework using **Python with FastAPI**.
     * Create `requirements.txt` in the repository root with the following initial dependencies:
       ```
       fastapi==0.110.0
       uvicorn[standard]==0.27.1  # Includes python-dotenv and performance extras
       black==24.2.0
       flake8==7.0.0
       pydantic==2.6.3
       python-jose[cryptography]==3.3.0  # For JWT
       passlib[bcrypt]==1.7.4  # For password hashing
       psycopg2-binary==2.9.9  # For PostgreSQL
       alembic==1.13.1  # For database migrations
       ```
     * Install dependencies from the repository root (e.g., `pip install -r requirements.txt`).
     * Create a basic `main.py` in `src/app/` to initialize the FastAPI app.
  3. Create a basic API endpoint `/api/v1/status` that returns a success message, current ISO 8601 timestamp, and service version.
     * The JSON response should be structured as follows:
       ```json
       {
         "status": "success",
         "message": "API is running and healthy.",
         "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffffZ", // ISO 8601 format
         "service_version": "0.1.0"
       }
       ```
  4. Set up basic linting and formatting using **Black** (for formatting) and **Flake8** (for linting).
     * Create `pyproject.toml` for Black configuration with the following content:
       ```toml
       [tool.black]
       line-length = 88
       ```
     * Create `.flake8` for Flake8 configuration with the following content:
       ```ini
       [flake8]
       max-line-length = 88
       extend-ignore = 
           W503, # line break before binary operator (Black compatibility)
           E203  # whitespace before ':' (Black compatibility)
       ```
     * Add entries for common Python and IDE files/folders to `.gitignore` (e.g., `__pycache__/`, `*.pyc`, `.env`, `venv/`, `.venv/`, `env/`, `.vscode/`, `.idea/`, `*.egg-info/`, `build/`, `dist/`).
  5. Initialize a Git repository.
* **Test:**
  * The project directory is created with the specified structure at the repository root.
  * The backend server (Uvicorn with FastAPI app) can be started without errors (e.g., from the `src/` directory, run `uvicorn app.main:app --reload --port 8000`).
  * Accessing the `http://localhost:8000/api/v1/status` endpoint via a tool like `curl` or a browser returns a JSON response matching the specified structure with a valid current timestamp.
  * Linting (Flake8) and formatting (Black) tools run without errors on the initial files.
  * Git repository is initialized.

### **Step 1.2: Basic Blockchain Network Setup (Local Development)**

* **Instruction:**  
  1. Set up a local development instance of the chosen permissioned blockchain platform (e.g., Hyperledger Fabric using a minimal test network configuration, or a local Ganache instance if an Ethereum-based permissioned chain like Quorum is chosen initially for simplicity in local dev, to be migrated later).  
  2. Define a very basic chaincode/smart contract for registering a "User" entity with a unique ID and a role (e.g., "PATIENT", "DOCTOR"). This is a placeholder and will be expanded.  
  3. Write a script or use blockchain tools to deploy this basic chaincode/smart contract to the local network.  
  4. Write a simple backend service (within the application backend) to connect to the local blockchain network. This service should have a function to invoke the "registerUser" transaction on the chaincode.  
* **Test:**  
  * The local blockchain network can be started and is accessible.  
  * The basic "User" chaincode/smart contract is successfully deployed.  
  * The backend service can connect to the blockchain network.  
  * Calling the backend service function to register a new user (e.g., via an internal test or a temporary test API endpoint) results in a successful transaction on the blockchain, and the user can be queried (if query function is also basic implemented).

### **Step 1.3: User Identity and Basic Authentication (Application Layer)**

* **Instruction:**  
  1. Implement a basic user registration endpoint in the application backend (e.g., /api/v1/auth/register). This endpoint should accept user details:
     ```json
     {
       "username": "string",  // min length: 3, max length: 50
       "email": "string",     // valid email format
       "password": "string",  // min length: 8, must contain number & special char
       "role": "string"       // enum: "PATIENT", "DOCTOR", "ADMIN"
     }
     ```
  2. Upon successful registration:
     * Hash password using bcrypt (work factor: 12)
     * Generate DID using format: `did:meditrustal:{base58(sha256(user_id))}`
     * Store in PostgreSQL with UUID primary key
  3. Simultaneously, invoke the blockchain service (from Step 1.2) to register the user's DID (Decentralized Identifier \- for now, a unique ID derived from their application user ID) and role on the blockchain.  
  4. Implement a basic user login endpoint (e.g., /api/v1/auth/login) that validates credentials and returns a simple token (e.g., JWT \- JSON Web Token).  
  5. Implement basic middleware to protect certain future API endpoints, requiring a valid token.  
* **Test:**  
  * A new user can register via the /api/v1/auth/register endpoint.  
  * User credentials (hashed password) are stored in the application database.  
  * The corresponding user ID and role are recorded on the local blockchain via the chaincode.  
  * A registered user can log in via /api/v1/auth/login and receive a token.  
  * A test protected endpoint returns an unauthorized error without a token and a success response with a valid token.

## **2\. Phase 2: Patient Data Management \- MVP Core (Blockchain Interaction)**

### **Step 2.1: Basic Patient Health Record (PHR) Structure on Blockchain**

* **Instruction:**  
  1. Extend the chaincode/smart contract to include a function to create a basic, placeholder "Health Record" linked to a patient's DID. For MVP, this record might initially just be a reference or a hash of an off-chain document.  
  2. The "Health Record" should have a unique ID, a timestamp, and a field for a data hash (e.g., dataHash).  
  3. Implement a backend API endpoint (e.g., POST /api/v1/phr) for an authenticated patient to create a new placeholder health record. This endpoint will generate a dummy hash for now.  
  4. The endpoint should invoke the chaincode to store this basic health record structure linked to the patient's DID.  
* **Test:**  
  * An authenticated patient can call the POST /api/v1/phr endpoint.  
  * A new health record entry (with ID, timestamp, dummy dataHash) linked to the patient's DID is created on the blockchain.  
  * The transaction is successful and can be verified by querying the blockchain (if a basic query function is added to the chaincode).

### **Step 2.2: Basic Off-Chain Data Storage Setup**

* **Instruction:**  
  1. Set up the chosen off-chain storage solution locally:
     * Use PostgreSQL with pgcrypto extension for encrypted storage
     * Use AES-256-GCM for data encryption
  2. Modify the POST /api/v1/phr endpoint:  
     * Accept structured medical data in FHIR R4 format
     * Calculate SHA-256 hash of the normalized JSON data
     * Store encrypted data in PostgreSQL
     * Store hash on blockchain with format: `sha256(timestamp + did + normalized_json)`
* **Test:**  
  * When a patient calls POST /api/v1/phr with structured medical data:  
    * The data is stored in the configured off-chain storage.  
    * A SHA-256 hash of the normalized JSON data is calculated.  
    * The health record on the blockchain contains the correct dataHash and a reference to the off-chain data.

### **Step 2.3: Basic Patient Data Retrieval**

* **Instruction:**  
  1. Implement a chaincode/smart contract function to query health records for a given patient DID.  
  2. Implement a backend API endpoint (e.g., GET /api/v1/phr) for an authenticated patient to retrieve a list of their health record metadata (ID, timestamp, dataHash, off-chain reference) from the blockchain.  
  3. Implement another backend API endpoint (e.g., GET /api/v1/phr/{recordId}/data) for an authenticated patient to retrieve the actual data from off-chain storage, using the off-chain reference obtained from the blockchain record.  
* **Test:**  
  * An authenticated patient can call GET /api/v1/phr and receive a list of their health record metadata stored on the blockchain.  
  * An authenticated patient can call GET /api/v1/phr/{recordId}/data and retrieve the correct structured medical data from off-chain storage that corresponds to the blockchain record.  
  * Attempting to access another patient's data should fail (basic authorization check).

## **3\. Phase 3: Basic NLP & AI Placeholder and Frontend Shell**

### **Step 3.1: Placeholder NLP Service**

* **Instruction:**  
  1. Create a very simple NLP service (e.g., a separate Python Flask/FastAPI microservice, or a module within the main backend if simpler for MVP).  
  2. This service should have one endpoint (e.g., POST /nlp/extract-entities) that accepts text.  
  3. For MVP, this service will not perform real NLP. It should simply return a predefined, dummy JSON response indicating mock entities (e.g., {"entities": \[{"text": "Blood Pressure", "type": "VitalSign"}, {"text": "120/80 mmHg", "type": "Measurement"}\]}).  
* **Test:**  
  * The placeholder NLP service can be started.  
  * Sending text to POST /nlp/extract-entities returns the predefined dummy JSON entity structure.

### **Step 3.2: Placeholder AI Predictive Service**

* **Instruction:**  
  1. Create a very simple AI service (similar setup to NLP service).  
  2. This service should have one endpoint (e.g., POST /ai/predict-risk) that accepts some structured dummy data (e.g., {"age": 50, "systolic\_bp": 120}).  
  3. For MVP, this service will not perform real AI prediction. It should return a predefined dummy JSON risk score (e.g., {"risk\_level": "low", "score": 0.1}).  
* **Test:**  
  * The placeholder AI service can be started.  
  * Sending dummy structured data to POST /ai/predict-risk returns the predefined dummy JSON risk score.

### **Step 3.3: Basic Frontend Shell (Patient Portal)**

* **Instruction:**  
  1. Set up a basic frontend project using the chosen framework (e.g., React/Vue, as per tech-stack.md).  
  2. Implement a simple login page that calls the backend's /api/v1/auth/login endpoint. Upon successful login, store the token (e.g., in localStorage or a state management solution).  
  3. Create a basic dashboard page accessible after login.  
  4. On the dashboard, implement a section to display a list of the patient's health records by calling the backend's GET /api/v1/phr endpoint. Display the metadata (ID, timestamp).  
  5. (Optional for MVP, can be deferred) Add a button next to each record to view details, which would call GET /api/v1/phr/{recordId}/data and display the raw text.  
* **Test:**  
  * The frontend application can be built and started.  
  * A user can enter credentials on the login page, and upon successful authentication, is redirected to the dashboard.  
  * The dashboard page successfully fetches and displays a list of the logged-in patient's health record metadata.  
  * (If implemented) Clicking a "view details" button shows the raw text data for that record.

## **4\. Phase 4: Basic Consent Mechanism (Simplified for MVP)**

### **Step 4.1: Simplified Consent Logic in Chaincode**

* **Instruction:**  
  1. Modify the "Health Record" structure in the chaincode to include a very simple access list, e.g., an array of DIDs (doctor DIDs) that are allowed to read this specific record. Initially, this list is empty or only contains the patient's DID.  
  2. Implement a chaincode function grantAccess(recordId, doctorDid) that allows a patient (owner of the record) to add a doctor's DID to the access list of a specific health record.  
  3. Modify the chaincode function for querying health records (from Step 2.3) so that it checks if the requester's DID (e.g., a doctor's DID) is in the access list for that record before returning data. (For MVP, the actual data retrieval from off-chain will still be via a separate API call, but the blockchain will gatekeep metadata access).  
* **Test:**  
  * A patient can successfully call a new backend endpoint (e.g., POST /api/v1/phr/{recordId}/grant-access) which invokes the grantAccess chaincode function, adding a (pre-registered dummy) doctor's DID to a health record's access list on the blockchain.  
  * A (dummy) doctor attempting to query metadata for that specific record (via a new test endpoint simulating doctor access) succeeds if access was granted, and fails if not.  
  * The patient can still access their own record metadata.

This MVP implementation plan focuses on establishing the foundational layers and core interactions. Real NLP/AI, comprehensive PIPL compliance, advanced consent models, and other portal functionalities will be part of subsequent development phases.

## **API Standards & Error Handling**

### Error Response Format
All API errors will follow this structure:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {
      "field1": ["error detail 1", "error detail 2"],
      "field2": ["error detail"]
    },
    "timestamp": "2024-03-15T12:34:56.789Z",
    "request_id": "req_123abc"
  }
}
```

### Standard Error Codes
1. **Authentication Errors (40x)**
   - `UNAUTHORIZED`: Missing or invalid authentication
   - `INVALID_CREDENTIALS`: Wrong username/password
   - `TOKEN_EXPIRED`: JWT token has expired
   - `INSUFFICIENT_PERMISSIONS`: Not authorized for this action

2. **Validation Errors (422)**
   - `VALIDATION_ERROR`: Request body validation failed
   - `INVALID_FORMAT`: Data format is incorrect
   - `MISSING_REQUIRED`: Required field is missing

3. **Business Logic Errors (409)**
   - `DUPLICATE_ENTRY`: Resource already exists
   - `RESOURCE_CONFLICT`: Cannot perform action due to state
   - `BLOCKCHAIN_ERROR`: Blockchain transaction failed

4. **Server Errors (500)**
   - `INTERNAL_ERROR`: Unexpected server error
   - `DATABASE_ERROR`: Database operation failed
   - `EXTERNAL_SERVICE_ERROR`: Third-party service failed

### Rate Limiting
```python
RATE_LIMIT_CONFIG = {
    "default": {
        "calls": 100,
        "period": 60  # seconds
    },
    "auth": {
        "calls": 5,
        "period": 60
    },
    "blockchain": {
        "calls": 20,
        "period": 60
    }
}

# Rate limit error response
{
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Too many requests. Please try again in X seconds.",
        "details": {
            "retry_after": 30,
            "limit": 100,
            "remaining": 0,
            "reset": "2024-03-15T12:35:00Z"
        }
    }
}
```

### Logging Format
```python
LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "loggers": {
        "app": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "app.auth": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "app.blockchain": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        }
    }
}
```

### Log Entry Format
```json
{
    "timestamp": "2024-03-15T12:34:56.789Z",
    "level": "INFO",
    "logger": "app.auth",
    "request_id": "req_123abc",
    "user_id": "usr_456def",
    "message": "User login successful",
    "details": {
        "ip": "192.168.1.1",
        "user_agent": "Mozilla/5.0...",
        "method": "POST",
        "path": "/api/v1/auth/login",
        "status_code": 200,
        "duration_ms": 45
    }
}
```
