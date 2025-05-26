# MediTrustAl Project

## Project Description

MediTrustAl is a comprehensive platform designed to address various challenges in global and local healthcare services, including in Hangzhou and China. These challenges include data fragmentation, difficulty in leveraging large volumes of clinical narrative data, a lack of sophisticated predictive analytics to support proactive decision-making, and crucial issues related to patient data privacy and security. MediTrustAl synergistically integrates Natural Language Processing (NLP), Artificial Intelligence (AI), and Blockchain technology.

MediTrustAl's core innovation lies in the unique combination of these three technologies:
* **NLP** to extract meaning and valuable insights from unstructured medical data such as doctor's notes and pathology reports.
* **AI** to provide predictive analytics, personalized care, and clinical decision support.
* **Blockchain** to guarantee security, privacy, data interoperability, and transparent and decentralized governance.

This project aims to improve the quality of healthcare services, operational efficiency for service providers, patient empowerment through greater control over their health data, and accelerate medical research progress.

## Project Goal (Platform Vision)

MediTrustAl aims to create a connected, intelligent, secure, and patient-centric healthcare ecosystem. This vision goes beyond mere data management, towards empowering all stakeholders in the health system through the synergistic utilization of advanced technologies.

## Project Scope (Based on Initial MVP)

The initial focus (Minimum Viable Product - MVP) will cover the development of core platform components and validation of the technical concept, including:
* Development of a basic NLP module for key information extraction from Mandarin-language medical records.
* Development of initial predictive AI models for 1-2 priority use cases relevant to Hangzhou.
* Implementation of a basic blockchain architecture (e.g., private permissioned testnet) for decentralized identity management (DID) and simple access permission mechanisms.
* Development of an initial user interface (UI) for patients and doctors to demonstrate core functionalities.

## Technologies Used (Core for MVP)

* **Backend:** Python 3.9+ (with FastAPI)
* **Blockchain (Local MVP):** Ganache (for local Ethereum simulation)
* **Smart Contract Language:** Solidity (for Ganache)
* **Blockchain Development Toolkit:** Node.js (LTS version), npm, Hardhat
* **Python Dependencies:** Listed in `requirements.txt` (e.g., `fastapi`, `uvicorn`, `web3.py`, `python-dotenv`, `pydantic-settings`)
* **Linting/Formatting:** Black, Flake8 (Python)
* **Version Control:** Git

*(Refer to `memory-bank/tech-stack.md` for more comprehensive technology details for the entire project).*

## Prerequisites (System Requirements)

Before you begin, ensure your system has the following software installed:

1.  **Git:** For version control.
    * Installation guide: [https://git-scm.com/book/en/v2/Getting-Started-Installing-Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
2.  **Python:** Version 3.9 or newer.
    * Installation guide: [https://www.python.org/downloads/](https://www.python.org/downloads/)
    * Ensure `pip` (Python package installer) is also installed and updated.
3.  **Node.js and npm:** LTS (Long Term Support) version recommended.
    * npm (Node Package Manager) is usually installed with Node.js.
    * Installation guide: [https://nodejs.org/](https://nodejs.org/)
    * Verify with `node -v` and `npm -v`.
4.  **Ganache (CLI or UI):** For the local Ethereum blockchain network.
    * **Ganache CLI:** `npm install -g ganache`
    * **Ganache UI:** Download from [https://trufflesuite.com/ganache/](https://trufflesuite.com/ganache/)
    * Verify Ganache CLI with `ganache --version`.

## How to Get Started (Development Setup)

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/neimasilk/MediTrustAl.git](https://github.com/neimasilk/MediTrustAl.git)
    cd MediTrustAl
    ```

2.  **Set Up Python Environment (Virtual environment recommended):**
    ```bash
    python -m venv venv
    # Activate the virtual environment:
    # Windows:
    # venv\Scripts\activate
    # macOS/Linux:
    # source venv/bin/activate
    ```

3.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Node.js Dependencies (for Hardhat and Smart Contracts):**
    ```bash
    npm install
    ```
    *(This will install Hardhat and other dependencies defined in `package.json`)*

5.  **Set Up `.env` File:**
    * Create a `.env` file in the project root directory. You can copy it from `env.example` if one is provided in the future, or create it manually.
    * Fill the `.env` file with the necessary configurations, such as:
        ```env
        GANACHE_RPC_URL="[http://127.0.0.1:8545](http://127.0.0.1:8545)"
        USER_REGISTRY_CONTRACT_ADDRESS="" # This will be filled after smart contract deployment
        # Add other variables as needed
        ```
    * **IMPORTANT:** Ensure the `.env` file is added to `.gitignore` and is not committed to the repository.

6.  **Run Local Ganache Network:**
    * If using Ganache CLI: `ganache`
    * If using Ganache UI: Open the application and create/open a workspace.
    * Ensure the RPC URL (usually `http://127.0.0.1:8545`) matches the one in your `.env` file.

7.  **Compile and Deploy Smart Contracts (UserRegistry for initial MVP):**
    * Compile smart contracts:
        ```bash
        npx hardhat compile
        ```
    * Deploy smart contracts to the local Ganache network (adjust network name if different in `hardhat.config.js`):
        ```bash
        npx hardhat run blockchain/scripts/deployUserRegistry.js --network ganache
        ```
    * After successful deployment, update the `USER_REGISTRY_CONTRACT_ADDRESS` value in your `.env` file with the displayed contract address.

8.  **Run FastAPI Backend Server:**
    ```bash
    uvicorn src.app.main:app --reload --port 8000
    ```
    * The API will be available at `http://localhost:8000`.
    * API documentation (Swagger UI) will be available at `http://localhost:8000/docs`.

9.  **Familiarize Yourself with Project Documentation:**
    * Read all documents within the `memory-bank/` folder to understand the project's vision, architecture, implementation plan, and coding rules.

## Project Structure & Methodology

This project will follow the "Vibe Coding Indonesia V1.0" methodology. All planning and progress documents will be stored in the `memory-bank/` folder.

## Contribution

Contribution guidelines will be added in the future. For now, follow the "Vibe Coding" workflow.

## License

The license will be determined later.