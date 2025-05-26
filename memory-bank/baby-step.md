# Baby Step To-Do List: MediTrustAl

## Konteks Baby-Step Saat Ini:
* **Parent Module:** Module 0: Environment Setup & Basic Infrastructure.
* **Step Sesuai Implementation Plan:** Step 1.2: Basic Blockchain Network Setup (Local Development).
* **Pilihan Teknologi Blockchain (Untuk MVP Lokal Awal):** Ganache (Jaringan Ethereum lokal untuk simulasi dan pengembangan cepat smart contract dasar). Ini dipilih untuk kesederhanaan MVP awal dan akan dievaluasi untuk migrasi ke Hyperledger Fabric sesuai `tech-stack.md` di fase selanjutnya.
* **Bahasa Smart Contract:** Solidity (karena menggunakan Ganache).
* **Tujuan Baby-Step:** Menyiapkan jaringan blockchain lokal menggunakan Ganache, membuat dan mendeploy smart contract "UserRegistry" yang sangat dasar, dan memastikan backend FastAPI dapat berinteraksi dengannya untuk mendaftarkan pengguna.

## Detail Tugas untuk Baby-Step Saat Ini:

### Bagian 1: Setup Ganache dan Persiapan Lingkungan Smart Contract

1.  **Tugas: Instalasi Ganache**
    * **Deskripsi:** Menginstal Ganache CLI atau Ganache UI untuk membuat jaringan Ethereum lokal.
    * **Instruksi (Pilih salah satu: CLI atau UI):**
        * **Untuk Ganache CLI (Direkomendasikan untuk integrasi skrip):**
            1.  Pastikan Node.js dan npm (atau yarn) sudah terinstal di sistem Anda.
            2.  Buka terminal atau command prompt.
            3.  Jalankan perintah: `npm install -g ganache` (atau `yarn global add ganache` jika menggunakan yarn).
            4.  Setelah instalasi, jalankan `ganache --version` untuk memastikan instalasi berhasil dan catat versinya.
        * **Untuk Ganache UI (Alternatif jika lebih suka antarmuka grafis):**
            1.  Kunjungi situs resmi Truffle Suite ([https://trufflesuite.com/ganache/](https://trufflesuite.com/ganache/)) dan unduh installer Ganache UI yang sesuai dengan sistem operasi Anda.
            2.  Ikuti petunjuk instalasi.
            3.  Buka aplikasi Ganache UI.
    * **Validasi:**
        * Ganache CLI dapat dijalankan dari terminal dengan perintah `ganache` (atau `ganache-cli` tergantung versi, `ganache` adalah yang terbaru).
        * Atau, Ganache UI dapat dibuka dan menampilkan opsi untuk membuat "Quickstart" workspace atau "New Workspace".

2.  **Tugas: Menjalankan Jaringan Blockchain Lokal Ganache**
    * **Deskripsi:** Memulai instance jaringan blockchain lokal Ganache.
    * **Instruksi:**
        * **Untuk Ganache CLI:**
            1.  Buka terminal.
            2.  Jalankan perintah: `ganache`
            3.  Perhatikan output di terminal. Catat alamat RPC Server (biasanya `HTTP://127.0.0.1:8545` atau `HTTP://0.0.0.0:8545`) dan daftar akun Ethereum yang dibuat beserta private key-nya (ini penting untuk deployment dan interaksi).
        * **Untuk Ganache UI:**
            1.  Buka Ganache UI.
            2.  Klik "Quickstart" (atau buat "New Workspace" dengan konfigurasi default).
            3.  Di layar utama workspace, catat "RPC SERVER" (biasanya `HTTP://127.0.0.1:8545`) dan lihat tab "ACCOUNTS" untuk daftar akun dan private key mereka.
    * **Validasi:**
        * Jaringan Ganache berjalan dan menampilkan alamat RPC serta daftar akun Ethereum.
        * Alamat RPC Server dapat diakses (misalnya, `http://127.0.0.1:8545`).

3.  **Tugas: Persiapan Struktur Folder untuk Smart Contract**
    * **Deskripsi:** Membuat struktur folder dasar untuk menyimpan kode smart contract Solidity di dalam root repositori Anda.
    * **Instruksi:**
        1.  Pastikan Anda berada di root direktori repositori `MediTrustAl` Anda.
        2.  Buat folder baru bernama `blockchain`.
        3.  Di dalam folder `blockchain` (yaitu `MediTrustAl/blockchain/`), buat subfolder bernama `contracts`.
        4.  Di dalam folder `blockchain` (yaitu `MediTrustAl/blockchain/`), buat subfolder bernama `scripts` (untuk skrip deployment nanti).
        5.  Di dalam folder `blockchain` (yaitu `MediTrustAl/blockchain/`), buat subfolder bernama `build` (akan digunakan oleh tools kompilasi).
    * **Struktur yang diharapkan di dalam repositori Anda:**
        ```
        MediTrustAl/
        ├── blockchain/
        │   ├── contracts/      // Tempat file .sol
        │   ├── scripts/        // Tempat skrip deployment
        │   └── build/          // Tempat output kompilasi (misalnya ABI, bytecode)
        ├── src/
        ├── memory-bank/
        ├── .gitignore
        ├── README.md
        └── requirements.txt
        ```
    * **Validasi:** Folder `blockchain/contracts/`, `blockchain/scripts/`, dan `blockchain/build/` telah berhasil dibuat di dalam root repositori `MediTrustAl`.

### Bagian 2: Pengembangan dan Deployment Smart Contract "UserRegistry"

4.  **Tugas: Pembuatan Smart Contract `UserRegistry.sol`**
    * **Deskripsi:** Menulis smart contract Solidity dasar bernama `UserRegistry` yang memiliki fungsi untuk mendaftarkan pengguna dengan ID dan peran, serta fungsi untuk mengambil peran pengguna berdasarkan ID.
    * **Instruksi:**
        1.  Di dalam folder `MediTrustAl/blockchain/contracts/`, buat file baru bernama `UserRegistry.sol`.
        2.  Isi `UserRegistry.sol` dengan kode berikut:
            ```solidity
            // SPDX-License-Identifier: MIT
            pragma solidity ^0.8.0; // Pastikan versi Solidity ini didukung oleh Hardhat config Anda

            contract UserRegistry {
                struct User {
                    string userId;
                    string role;
                    bool isRegistered;
                }

                mapping(string => User) public users;
                address public owner;

                event UserRegistered(string userId, string role);

                constructor() {
                    owner = msg.sender; // Akun yang mendeploy kontrak akan menjadi owner
                }

                modifier onlyOwner() {
                    require(msg.sender == owner, "Only owner can perform this action");
                    _;
                }

                function registerUser(string memory _userId, string memory _role) public {
                    // Untuk MVP ini, kita akan membiarkan siapa saja mendaftar.
                    // Di masa depan, ini bisa dibatasi oleh onlyOwner atau mekanisme lain.
                    require(bytes(users[_userId].userId).length == 0, "User ID already registered"); // Cek jika userId belum ada
                    require(!users[_userId].isRegistered, "User flag indicates already registered"); // Cek flag isRegistered

                    users[_userId] = User({
                        userId: _userId,
                        role: _role,
                        isRegistered: true
                    });

                    emit UserRegistered(_userId, _role);
                }

                function getUserRole(string memory _userId) public view returns (string memory, bool) {
                    return (users[_userId].role, users[_userId].isRegistered);
                }
            }
            ```
    * **Validasi:** File `UserRegistry.sol` telah dibuat di `MediTrustAl/blockchain/contracts/` dengan isi kode di atas. Tidak ada error sintaks awal yang terlihat.

5.  **Tugas: Instalasi dan Konfigurasi Alat Bantu Kompilasi dan Deployment (Hardhat)**
    * **Deskripsi:** Menginstal Hardhat, sebuah environment pengembangan Ethereum yang akan membantu dalam kompilasi, deployment, dan testing smart contract, di root repositori Anda.
    * **Instruksi:**
        1.  Buka terminal di root direktori repositori `MediTrustAl`.
        2.  Jalankan perintah: `npm init -y` (jika belum ada `package.json` di root repositori. Jika sudah ada, lewati langkah ini).
        3.  Jalankan perintah untuk menginstal Hardhat dan plugin yang dibutuhkan: `npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox dotenv`
            *(Catatan: `@nomicfoundation/hardhat-toolbox` sudah mencakup banyak plugin umum seperti ethers, chai, dll. Jika ada plugin spesifik lain yang dibutuhkan nanti, bisa ditambahkan.)*
        4.  Setelah instalasi, jalankan `npx hardhat` di root repositori `MediTrustAl`.
        5.  Pilih opsi "Create a JavaScript project" (atau "Create a TypeScript project" jika tim lebih familiar, namun JavaScript lebih sederhana untuk memulai).
        6.  Jawab pertanyaan yang muncul.
            * "Hardhat project root": Terima default (root repositori Anda).
            * "Do you want to add a .gitignore?": Pilih `yes` jika Anda belum memiliki `.gitignore` yang komprehensif atau ingin Hardhat menambahkannya.
            * "Do you want to install this sample project's dependencies with npm (...)?" Pilih `yes` jika Anda memilih untuk membuat contoh proyek (ini akan menginstal dependensi contoh, yang sebagian besar sudah kita instal di langkah 3).
        7.  Ini akan membuat file `hardhat.config.js` dan beberapa folder contoh (misalnya, `contracts`, `scripts`, `test` versi Hardhat). Anda dapat menghapus file kontrak contoh (`Lock.sol`) dari folder `contracts` yang dibuat Hardhat, karena kita akan menggunakan `blockchain/contracts/UserRegistry.sol`.
        8.  **PENTING:** Modifikasi file `hardhat.config.js` di root repositori `MediTrustAl` agar sesuai dengan struktur proyek Anda dan terhubung ke Ganache. Contoh isi `hardhat.config.js`:
            ```javascript
            require("@nomicfoundation/hardhat-toolbox");
            require('dotenv').config(); // Untuk memuat variabel dari file .env

            /** @type import('hardhat/config').HardhatUserConfig */
            module.exports = {
              solidity: "0.8.20", // PASTIKAN versi ini SESUAI atau KOMPATIBEL dengan pragma di UserRegistry.sol
              paths: {
                sources: "./blockchain/contracts", // Path ke folder kontrak Anda
                tests: "./blockchain/test",       // Path untuk unit test smart contract (buat folder ini jika belum)
                cache: "./blockchain/cache",      // Path untuk cache Hardhat
                artifacts: "./blockchain/build/artifacts" // Path untuk output kompilasi (ABI, bytecode)
              },
              networks: {
                ganache: { // Nama jaringan ini bebas, misalnya 'localganache' atau 'development'
                  url: process.env.GANACHE_RPC_URL || "[http://127.0.0.1:8545](http://127.0.0.1:8545)", // URL RPC Ganache Anda
                  // accounts: process.env.GANACHE_PRIVATE_KEY ? [process.env.GANACHE_PRIVATE_KEY] : [] // Opsional: Jika ingin menggunakan akun spesifik untuk deployment
                                                                                                     // Biasanya Hardhat otomatis menggunakan akun dari node Ganache
                }
                // Anda bisa menambahkan konfigurasi jaringan lain di sini (misalnya, testnet, mainnet)
              }
            };
            ```
        9.  Buat file `.env` di root repositori `MediTrustAl` (jika belum ada) untuk menyimpan konfigurasi sensitif. **Pastikan `.env` sudah ada di dalam file `.gitignore` Anda!**
            Contoh isi `.env`:
            ```env
            GANACHE_RPC_URL="[http://127.0.0.1:8545](http://127.0.0.1:8545)"
            # Opsional: GANACHE_PRIVATE_KEY="PRIVATE_KEY_AKUN_GANACHE_UNTUK_DEPLOYMENT"
            ```
    * **Validasi:**
        * Hardhat dan dependensinya terinstal di `node_modules` dalam root repositori.
        * File `hardhat.config.js` ada di root repositori dan telah dikonfigurasi dengan benar untuk path kontrak (`./blockchain/contracts`) dan jaringan Ganache.
        * File `.env` ada di root repositori dan berisi `GANACHE_RPC_URL`.
        * Perintah `npx hardhat compile` (dijalankan dari root repositori) berjalan tanpa error dan menghasilkan artifacts (file JSON berisi ABI dan bytecode) di dalam folder `MediTrustAl/blockchain/build/artifacts/blockchain/contracts/UserRegistry.sol/UserRegistry.json`.

6.  **Tugas: Membuat Skrip Deployment untuk `UserRegistry.sol`**
    * **Deskripsi:** Menulis skrip JavaScript menggunakan Hardhat untuk mendeploy `UserRegistry.sol` ke jaringan Ganache lokal.
    * **Instruksi:**
        1.  Di dalam folder `MediTrustAl/blockchain/scripts/` (yang path-nya sesuai dengan `hardhat.config.js`), buat file baru bernama `deployUserRegistry.js`. Jika Hardhat membuat file `deploy.js` atau `run.js` contoh, Anda bisa memodifikasinya atau membuat file baru ini.
        2.  Isi `deployUserRegistry.js` dengan kode berikut:
            ```javascript
            const hre = require("hardhat");
            const fs = require('fs'); // Untuk menyimpan alamat kontrak dan ABI
            const path = require('path'); // Untuk path yang lebih robust

            async function main() {
              const [deployer] = await hre.ethers.getSigners(); // Mengambil akun deployer dari Hardhat (yang terhubung ke Ganache)

              console.log("Deploying UserRegistry contract with the account:", deployer.address);
              console.log("Account balance:", (await hre.ethers.provider.getBalance(deployer.address)).toString());

              const UserRegistryFactory = await hre.ethers.getContractFactory("UserRegistry");
              const userRegistryContract = await UserRegistryFactory.deploy();

              // Menunggu hingga kontrak selesai dideploy dan mendapatkan alamatnya
              await userRegistryContract.waitForDeployment();
              const contractAddress = await userRegistryContract.getAddress();

              console.log("UserRegistry contract deployed to:", contractAddress);

              // Menyimpan alamat kontrak dan ABI untuk digunakan oleh backend
              saveDeploymentInfo(userRegistryContract, "UserRegistry");
            }

            function saveDeploymentInfo(contract, contractName) {
              const contractAddress = contract.target; // Alamat kontrak yang baru
              const contractArtifact = hre.artifacts.readArtifactSync(contractName);

              const deploymentInfoDir = path.join(__dirname, "..", "build", "deployments"); // misal: MediTrustAl/blockchain/build/deployments/
              if (!fs.existsSync(deploymentInfoDir)) {
                fs.mkdirSync(deploymentInfoDir, { recursive: true });
              }

              // Simpan alamat kontrak
              fs.writeFileSync(
                path.join(deploymentInfoDir, `${contractName}-address.json`),
                JSON.stringify({ address: contractAddress }, undefined, 2)
              );

              // Simpan ABI
              fs.writeFileSync(
                path.join(deploymentInfoDir, `${contractName}-abi.json`),
                JSON.stringify(contractArtifact.abi, undefined, 2) // Hanya simpan ABI
              );

              console.log(`Deployment info for ${contractName} saved to ${deploymentInfoDir}`);
            }

            main()
              .then(() => process.exit(0))
              .catch((error) => {
                console.error("Error deploying contract:", error);
                process.exit(1);
              });
            ```
    * **Validasi:** File `deployUserRegistry.js` telah dibuat di `MediTrustAl/blockchain/scripts/`.

7.  **Tugas: Mendeploy Smart Contract ke Ganache Menggunakan Hardhat**
    * **Deskripsi:** Menjalankan skrip deployment untuk mendeploy `UserRegistry.sol`.
    * **Instruksi:**
        1.  Pastikan jaringan Ganache lokal Anda (CLI atau UI) sedang berjalan.
        2.  Buka terminal di root direktori repositori `MediTrustAl`.
        3.  Jalankan perintah: `npx hardhat run blockchain/scripts/deployUserRegistry.js --network ganache`
            *(Pastikan `--network ganache` cocok dengan nama jaringan yang Anda definisikan di `hardhat.config.js`)*
    * **Validasi:**
        * Skrip berjalan tanpa error.
        * Output di terminal menunjukkan alamat deployer, saldo akun, dan alamat kontrak `UserRegistry` yang baru dideploy di jaringan Ganache.
        * File `UserRegistry-address.json` dan `UserRegistry-abi.json` tercipta di dalam folder `MediTrustAl/blockchain/build/deployments/`. Catat alamat kontrak dari `UserRegistry-address.json`.
        * Periksa di Ganache UI (jika menggunakan), pada tab "Transactions" atau "Blocks", akan terlihat transaksi deployment kontrak.

### Bagian 3: Integrasi Dasar dengan Backend FastAPI

8.  **Tugas: Instalasi Library Klien Ethereum untuk Python (`web3.py`)**
    * **Deskripsi:** Menambahkan `web3.py` ke `requirements.txt` agar backend FastAPI dapat berkomunikasi dengan jaringan Ethereum (Ganache).
    * **Instruksi:**
        1.  Buka file `requirements.txt` di root repositori `MediTrustAl`.
        2.  Tambahkan baris berikut jika belum ada: `web3==6.15.1` (atau versi stabil terbaru, periksa di PyPI untuk versi terbaru yang kompatibel).
        3.  Buka terminal di root repositori `MediTrustAl`.
        4.  Jalankan perintah: `pip install -r requirements.txt`
    * **Validasi:** `web3.py` berhasil terinstal di environment Python proyek Anda. Tidak ada error saat instalasi.

9.  **Tugas: Konfigurasi Koneksi ke Ganache di Backend FastAPI**
    * **Deskripsi:** Menyiapkan konfigurasi di backend FastAPI untuk terhubung ke Ganache dan mengetahui alamat smart contract `UserRegistry`.
    * **Instruksi:**
        1.  Buka file `.env` di root repositori `MediTrustAl`. Tambahkan variabel untuk alamat kontrak `UserRegistry` (ambil dari file `UserRegistry-address.json` atau output konsol saat deployment):
            ```env
            GANACHE_RPC_URL="[http://127.0.0.1:8545](http://127.0.0.1:8545)"
            USER_REGISTRY_CONTRACT_ADDRESS="ALAMAT_KONTRAK_ANDA_DARI_LANGKAH_7"
            # Opsional: BACKEND_ETHEREUM_ACCOUNT_ADDRESS="ALAMAT_AKUN_GANACHE_UNTUK_BACKEND"
            # Opsional: BACKEND_ETHEREUM_PRIVATE_KEY="PRIVATE_KEY_AKUN_GANACHE_UNTUK_BACKEND"
            ```
            *(Pastikan `ALAMAT_KONTRAK_ANDA_DARI_LANGKAH_7` diganti dengan alamat yang benar)*
        2.  Pastikan file `src/app/core/config.py` sudah ada dan sesuai dengan yang dibuat pada baby-step sebelumnya (Step 1.2 Task 9 di respons sebelumnya). Jika belum, buat atau update:
            ```python
            # src/app/core/config.py
            from pydantic_settings import BaseSettings, SettingsConfigDict
            import os
            from dotenv import load_dotenv

            # Memastikan .env dimuat sebelum Settings dibaca
            # Path ke .env relatif dari root proyek dimana skrip utama dijalankan
            dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env') # ../../../.env
            load_dotenv(dotenv_path=dotenv_path)


            class Settings(BaseSettings):
                model_config = SettingsConfigDict(env_file=dotenv_path, env_file_encoding='utf-8', extra='ignore')

                GANACHE_RPC_URL: str = "[http://127.0.0.1:8545](http://127.0.0.1:8545)" # Default jika tidak ada di .env
                USER_REGISTRY_CONTRACT_ADDRESS: str = "YOUR_DEFAULT_CONTRACT_ADDRESS_IF_ANY" # Default jika tidak ada di .env
                # BACKEND_ETHEREUM_ACCOUNT_ADDRESS: str | None = None
                # BACKEND_ETHEREUM_PRIVATE_KEY: str | None = None

            settings = Settings()
            ```
        3.  Pastikan library `python-dotenv` dan `pydantic-settings` ada di `requirements.txt` dan sudah terinstal.
    * **Validasi:**
        * File `.env` di root repositori telah diperbarui dengan `USER_REGISTRY_CONTRACT_ADDRESS`.
        * File `src/app/core/config.py` dapat memuat konfigurasi ini dengan benar. Saat aplikasi FastAPI dijalankan, `settings.USER_REGISTRY_CONTRACT_ADDRESS` akan memiliki nilai yang benar.

10. **Tugas: Pembuatan Service di Backend untuk Interaksi dengan `UserRegistry`**
    * **Deskripsi:** Membuat service di FastAPI yang dapat memanggil fungsi `registerUser` dan `getUserRole` pada smart contract `UserRegistry`. Service ini akan membaca ABI dari file yang disimpan oleh skrip deployment Hardhat.
    * **Instruksi:**
        1.  Buat folder `src/app/blockchain_services/` jika belum ada.
        2.  Buat file `src/app/blockchain_services/user_registry_service.py`:
            ```python
            # src/app/blockchain_services/user_registry_service.py
            from web3 import Web3
            from web3.middleware import geth_poa_middleware # Untuk jaringan PoA seperti beberapa konfigurasi Ganache
            from app.core.config import settings
            import json
            import os
            import logging # Tambahkan logging

            # Setup logging dasar
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)

            # Path ke file ABI yang disimpan oleh skrip deployment Hardhat
            # Relatif dari root proyek ke blockchain/build/deployments/UserRegistry-abi.json
            ABI_FILE_PATH = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), # -> root proyek
                "blockchain", "build", "deployments", "UserRegistry-abi.json"
            )


            class UserRegistryService:
                def __init__(self):
                    self.w3 = Web3(Web3.HTTPProvider(settings.GANACHE_RPC_URL))
                    # Tambahkan middleware jika Ganache Anda menggunakan PoA (seringkali default untuk Ganache UI/CLI baru)
                    self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

                    if not self.w3.is_connected():
                        logger.error("Failed to connect to Ganache RPC at %s", settings.GANACHE_RPC_URL)
                        raise ConnectionError(f"Failed to connect to Ganache RPC: {settings.GANACHE_RPC_URL}")
                    logger.info("Successfully connected to Ganache RPC at %s", settings.GANACHE_RPC_URL)


                    self.contract_address = settings.USER_REGISTRY_CONTRACT_ADDRESS
                    if not self.contract_address or not Web3.is_address(self.contract_address):
                         logger.error("Invalid or missing USER_REGISTRY_CONTRACT_ADDRESS: %s", self.contract_address)
                         raise ValueError(f"Invalid or missing USER_REGISTRY_CONTRACT_ADDRESS: {self.contract_address}")
                    logger.info("UserRegistry Contract Address: %s", self.contract_address)

                    try:
                        with open(ABI_FILE_PATH, 'r') as f:
                            contract_abi = json.load(f) # ABI adalah isi dari file JSON, bukan objek dengan key 'abi'
                        logger.info("Successfully loaded ABI from %s", ABI_FILE_PATH)
                    except FileNotFoundError:
                        logger.error("ABI file not found at %s", ABI_FILE_PATH)
                        raise FileNotFoundError(f"ABI file not found at {ABI_FILE_PATH}")
                    except json.JSONDecodeError:
                        logger.error("Error decoding ABI JSON from %s", ABI_FILE_PATH)
                        raise ValueError(f"Error decoding ABI JSON from {ABI_FILE_PATH}")

                    self.contract = self.w3.eth.contract(
                        address=self.w3.to_checksum_address(self.contract_address), # Gunakan to_checksum_address
                        abi=contract_abi
                    )

                    # Default account untuk mengirim transaksi (akun pertama di Ganache jika tidak diset spesifik)
                    # Pastikan Ganache memiliki akun
                    if not self.w3.eth.accounts:
                        logger.error("No accounts found in Ganache node.")
                        raise ValueError("No accounts found in Ganache node. Ensure Ganache is running and has accounts.")
                    self.default_account = self.w3.eth.accounts[0]
                    logger.info("Using default account for transactions: %s", self.default_account)

                    # Jika Anda ingin menggunakan private key spesifik dari .env untuk menandatangani transaksi:
                    # if settings.BACKEND_ETHEREUM_PRIVATE_KEY and settings.BACKEND_ETHEREUM_ACCOUNT_ADDRESS:
                    #     self.signing_account_address = self.w3.to_checksum_address(settings.BACKEND_ETHEREUM_ACCOUNT_ADDRESS)
                    #     self.signing_private_key = settings.BACKEND_ETHEREUM_PRIVATE_KEY
                    #     logger.info("Using specific signing account: %s", self.signing_account_address)
                    # else:
                    #     self.signing_account_address = self.default_account
                    #     self.signing_private_key = None # Transaksi akan dikirim dari default_account node


                async def register_user(self, user_id: str, role: str):
                    try:
                        logger.info(f"Attempting to register user_id: {user_id} with role: {role}")
                        # Perkirakan gas
                        transaction_details = {
                            'from': self.default_account,
                            # 'nonce': self.w3.eth.get_transaction_count(self.default_account) # Nonce otomatis diurus web3.py jika tidak diset
                        }
                        # Cek jika user sudah terdaftar sebelum mengirim transaksi
                        _current_role, is_registered = self.contract.functions.getUserRole(user_id).call()
                        if is_registered:
                            logger.warning(f"User {user_id} already registered with role {_current_role}.")
                            return {"status": "already_exists", "user_id": user_id, "role": _current_role}

                        gas_estimate = self.contract.functions.registerUser(user_id, role).estimate_gas(transaction_details)
                        transaction_details['gas'] = gas_estimate
                        # transaction_details['gasPrice'] = self.w3.eth.gas_price # Opsional

                        tx_hash = self.contract.functions.registerUser(user_id, role).transact(transaction_details)
                        logger.info(f"Transaction sent for registering user {user_id}. Tx hash: {tx_hash.hex()}")

                        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                        logger.info(f"Transaction receipt received for user {user_id}: {receipt}")

                        if receipt.status == 0: # Transaksi gagal
                             logger.error(f"Blockchain transaction failed for user {user_id}. Receipt: {receipt}")
                             return {"status": "failed_on_chain", "error": "Transaction reverted by EVM", "receipt": dict(receipt)}

                        return {"status": "success", "tx_hash": tx_hash.hex(), "receipt_status": receipt.status}
                    except Exception as e:
                        logger.error(f"Error in register_user for {user_id}: {str(e)}", exc_info=True)
                        return {"status": "failed", "error": str(e)}

                async def get_user_role(self, user_id: str):
                    try:
                        logger.info(f"Attempting to get role for user_id: {user_id}")
                        role_data, is_registered_data = self.contract.functions.getUserRole(user_id).call()
                        if not is_registered_data:
                            logger.info(f"User {user_id} not found on blockchain.")
                            return {"status": "not_found", "user_id": user_id}
                        logger.info(f"User {user_id} found. Role: {role_data}, IsRegistered: {is_registered_data}")
                        return {"status": "success", "user_id": user_id, "role": role_data, "is_registered": is_registered_data}
                    except Exception as e:
                        logger.error(f"Error in get_user_role for {user_id}: {str(e)}", exc_info=True)
                        return {"status": "failed", "error": str(e)}

            # Inisialisasi instance service agar bisa diimpor dan digunakan
            # Handle potensi error saat inisialisasi
            try:
                user_registry_service_instance = UserRegistryService()
            except Exception as e:
                logger.critical(f"CRITICAL: Failed to initialize UserRegistryService: {str(e)}", exc_info=True)
                # Pada aplikasi production, ini mungkin saatnya untuk exit atau masuk ke mode degraded.
                # Untuk development, kita biarkan error ini muncul agar bisa di-debug.
                user_registry_service_instance = None # atau raise error
            ```
    * **Validasi:** File `user_registry_service.py` dibuat. Tidak ada error import atau sintaks saat menjalankan aplikasi FastAPI. Pesan log koneksi sukses ke Ganache muncul saat FastAPI dimulai jika `UserRegistryService` diinisialisasi global.

11. **Tugas: Membuat Endpoint API Sementara untuk Testing Interaksi Blockchain**
    * **Deskripsi:** Menambahkan endpoint sementara di FastAPI untuk memicu fungsi `register_user` dan `get_user_role` dari service yang baru dibuat, memungkinkan testing melalui HTTP request.
    * **Instruksi:**
        1.  Buat file baru `src/app/api/blockchain_test_routes.py` (jika belum ada dari baby-step sebelumnya, atau perbarui):
            ```python
            # src/app/api/blockchain_test_routes.py
            from fastapi import APIRouter, HTTPException, Depends
            from pydantic import BaseModel
            from app.blockchain_services.user_registry_service import user_registry_service_instance, UserRegistryService
            import logging

            router = APIRouter()
            logger = logging.getLogger(__name__)

            class UserRegistrationRequest(BaseModel):
                user_id: str
                role: str

            # Dependency untuk memastikan service tersedia
            async def get_user_registry_service():
                if user_registry_service_instance is None:
                    logger.error("UserRegistryService is not available.")
                    raise HTTPException(status_code=503, detail="Blockchain service is not available at the moment.")
                return user_registry_service_instance

            @router.post("/test-blockchain/register-user", summary="Test User Registration on Blockchain", tags=["Blockchain Test"])
            async def test_register_user_on_blockchain(
                request_body: UserRegistrationRequest,
                service: UserRegistryService = Depends(get_user_registry_service)
            ):
                logger.info(f"Received request to register user on blockchain: {request_body.user_id}")
                response = await service.register_user(request_body.user_id, request_body.role)
                if response["status"] in ["failed", "failed_on_chain"]:
                    logger.error(f"Blockchain transaction failed for {request_body.user_id}: {response.get('error')}")
                    raise HTTPException(status_code=500, detail=f"Blockchain operation failed: {response.get('error')}")
                if response["status"] == "already_exists":
                    logger.info(f"User {request_body.user_id} already exists on blockchain.")
                    # Anda bisa memilih status code 409 Conflict jika sudah ada
                    # return response # atau
                    raise HTTPException(status_code=409, detail=f"User {request_body.user_id} already exists with role {response.get('role')}")
                logger.info(f"Successfully processed registration for {request_body.user_id} on blockchain.")
                return response

            @router.get("/test-blockchain/get-user-role/{user_id}", summary="Test Get User Role from Blockchain", tags=["Blockchain Test"])
            async def test_get_user_role_from_blockchain(
                user_id: str,
                service: UserRegistryService = Depends(get_user_registry_service)
            ):
                logger.info(f"Received request to get role for user from blockchain: {user_id}")
                response = await service.get_user_role(user_id)
                if response["status"] == "failed":
                    logger.error(f"Blockchain query failed for {user_id}: {response.get('error')}")
                    raise HTTPException(status_code=500, detail=f"Blockchain query failed: {response.get('error')}")
                if response["status"] == "not_found":
                    logger.info(f"User {user_id} not found on blockchain for get_user_role.")
                    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found on blockchain.")
                logger.info(f"Successfully retrieved role for {user_id} from blockchain.")
                return response
            ```
        2.  Update `src/app/main.py` untuk menyertakan router baru ini:
            ```python
            # src/app/main.py
            from fastapi import FastAPI
            from app.api import status_routes
            from app.api import blockchain_test_routes # Tambahkan/pastikan ada ini
            import logging

            # Setup logging dasar untuk aplikasi
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)

            app = FastAPI(
                title="MediTrustAl API",
                version="0.1.0",
                description="API for MediTrustAl Platform"
            )

            # Include routers
            app.include_router(status_routes.router, prefix="/api/v1", tags=["Status"])
            app.include_router(blockchain_test_routes.router, prefix="/api/v1") # Tags sudah diatur di router-nya

            @app.on_event("startup")
            async def startup_event():
                logger.info("MediTrustAl API starting up...")
                # Anda bisa menambahkan pengecekan koneksi blockchain di sini jika diperlukan
                # from app.blockchain_services.user_registry_service import user_registry_service_instance
                # if user_registry_service_instance is None:
                #     logger.critical("Blockchain service could not be initialized. API may not function correctly.")
                # elif not user_registry_service_instance.w3.is_connected():
                #     logger.warning("Not connected to blockchain node on startup.")


            @app.on_event("shutdown")
            async def shutdown_event():
                logger.info("MediTrustAl API shutting down...")

            @app.get("/", tags=["Root"])
            async def root():
                return {"message": "Welcome to MediTrustAl API. Visit /docs for API documentation."}
            ```
    * **Validasi:**
        * Restart aplikasi FastAPI (misalnya, dari root repositori `MediTrustAl`, jalankan `uvicorn src.app.main:app --reload --port 8000` dari terminal yang memiliki environment Python aktif).
        * Buka browser atau alat API seperti Postman ke `http://localhost:8000/docs` untuk melihat dokumentasi API otomatis. Endpoint baru `/api/v1/test-blockchain/...` harus terlihat.
        * **Test Registrasi:**
            * Kirim request `POST` ke `http://localhost:8000/api/v1/test-blockchain/register-user` dengan body JSON:
              `{"user_id": "testPatient001", "role": "PATIENT"}`
            * Harapannya: Respons JSON sukses (misalnya, `{"status": "success", "tx_hash": "0x...", "receipt_status": 1}`).
            * Cek log terminal FastAPI untuk pesan dari `UserRegistryService` dan `blockchain_test_routes`.
            * Cek di Ganache: Harus ada transaksi baru yang tercatat.
        * **Test Pengambilan Role (setelah registrasi sukses):**
            * Kirim request `GET` ke `http://localhost:8000/api/v1/test-blockchain/get-user-role/testPatient001`
            * Harapannya: Respons JSON `{"status": "success", "user_id": "testPatient001", "role": "PATIENT", "is_registered": true}`.
        * **Test Pengambilan Role (untuk user yang tidak ada):**
            * Kirim request `GET` ke `http://localhost:8000/api/v1/test-blockchain/get-user-role/nonExistentUser`
            * Harapannya: Respons error HTTP 404.
        * **Test Registrasi Ulang (user yang sama):**
            * Kirim lagi request `POST` ke `http://localhost:8000/api/v1/test-blockchain/register-user` dengan body JSON yang sama:
              `{"user_id": "testPatient001", "role": "PATIENT"}`
            * Harapannya: Respons HTTP 409 (Conflict) atau respons JSON `{"status": "already_exists", ...}` sesuai implementasi di `blockchain_test_routes.py`. Smart contract juga akan me-revert jika mencoba mendaftar ulang dengan ID yang sama.

*(File ini akan dihapus atau diarsipkan setelah semua tugas di dalamnya selesai dan divalidasi, kemudian Planning AI akan membuat baby-step berikutnya).*