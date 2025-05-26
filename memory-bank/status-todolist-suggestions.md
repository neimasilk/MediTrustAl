# Project Status, To-Do List, and Suggestions: MediTrustAl

## Current Project Status (per 2025-05-26):
* **Project Phase:** Phase 1 - Core Backend Setup & Blockchain Foundation (MVP Focus)
* **Description:** Step 1.3 (User Identity and Basic Authentication) telah selesai diimplementasikan. Sistem identitas pengguna lengkap dengan registrasi ke database PostgreSQL, pembuatan DID, pendaftaran ke smart contract UserRegistry, login dengan JWT, dan proteksi rute telah diimplementasikan. Keamanan penandatanganan transaksi blockchain telah diperbaiki dengan menggunakan private key dari environment variable. Semua tes untuk fungsionalitas yang ada telah lolos.
* **Last Completed Step:**
    * Step 1.1: Project Setup and Basic Backend Structure - Selesai.
    * Step 1.2: Basic Blockchain Network Setup (Local Development) - Selesai.
    * Step 1.3: User Identity and Basic Authentication (Application Layer) - Selesai.
* **Next Step:** Step 1.4: Medical Record Data Model and Storage (Application Layer) - PENDING.

## Progress Update (Snapshot 2025-05-26):
1. **Database Setup** ✅ COMPLETED
   - [x] PostgreSQL 15.x installation and configuration.
   - [x] Database model creation (`User` model).
   - [x] Alembic migration setup and initial migration for `users` table.
   - [x] Database connection configuration.

2. **Authentication System** ✅ COMPLETED
   - [x] JWT token implementation (create, decode).
   - [x] Password hashing with bcrypt.
   - [x] Skema Pydantic untuk User (request, response, login).
   - [x] Implementasi Endpoint Registrasi Aplikasi Lengkap (termasuk validasi duplikasi).
   - [x] Implementasi Endpoint Login Aplikasi (username/email).
   - [x] Implementasi Middleware Proteksi Rute menggunakan JWT (`get_current_active_user`).
   - [x] Implementasi Generasi DID sesuai format `did:meditrustal:{base58(sha256(user_id))}`.

3. **Blockchain Integration (User Registry)** ✅ COMPLETED
   - [x] Ganache setup (sesuai `README.md` dan `hardhat.config.js`).
   - [x] Basic smart contract `UserRegistry` deployment (via `deployUserRegistry.js`).
   - [x] Service (`BlockchainService` di `blockchain.py`) untuk interaksi dengan `UserRegistry` contract (register user, get role).
   - [x] Perbaikan Penandatanganan Transaksi Blockchain untuk menangani private key dengan aman dari environment variables.
   - [x] Integrasi pemanggilan `blockchain_service.register_user` ke dalam alur registrasi aplikasi.

4. **Testing** ✅ COMPLETED
   - [x] Unit tests untuk fungsi utilitas (DID generation di `test_utils.py`).
   - [x] Integration tests untuk endpoint auth (register, login di `test_auth.py`).
   - [x] Integration tests untuk endpoint yang diproteksi (`/users/me` di `test_auth.py`).
   - [x] Test fixtures dan setup (SQLite in-memory database, mock blockchain service di `conftest.py`).

## Immediate Next Steps (Implementasi Step 1.4 - Medical Record):

Fokus utama adalah membuat model data, smart contract, dan API untuk manajemen rekam medis dasar, sesuai dengan `database-schema.md` dan `implementation-plan.md` (Step 2.1 & 2.2).

1.  **Database (PostgreSQL):**
    * Implementasikan model SQLAlchemy `MedicalRecord` berdasarkan `memory-bank/database-schema.md`.
        * Fields: `id` (UUID), `patient_id` (FK ke `users.id`), `blockchain_record_id` (VARCHAR, hash transaksi Ethereum), `record_type` (ENUM), `metadata` (JSONB), `encrypted_data` (BYTEA), `data_hash` (VARCHAR, SHA-256), `created_at`, `updated_at`.
    * Definisikan ENUM untuk `record_type` di Python.
    * Buat skema Pydantic untuk `MedicalRecord` (Create, Response).
    * Buat dan jalankan migrasi Alembic untuk tabel `medical_records`.
    * Implementasikan fungsi CRUD di `src/app/crud/crud_medical_record.py`.

2.  **Smart Contract (Solidity & Hardhat):**
    * Buat smart contract baru `MedicalRecordRegistry.sol`.
        * Fungsi untuk mencatat hash rekam medis: `addRecord(bytes32 recordHash, string patientDid, string recordType, uint256 timestamp)`. `recordHash` adalah `data_hash` dari data mentah yang tidak dienkripsi.
        * Mapping untuk menyimpan `recordHash` dan metadata terkait (misalnya `patientDid`, `recordType`, `timestamp`).
        * Event untuk pencatatan rekam medis baru.
        * (Untuk MVP, fungsionalitas grant access bisa ditunda sesuai `implementation-plan.md` Step 4.1, atau diimplementasikan secara sederhana jika waktu memungkinkan).
    * Update skrip deployment Hardhat (`scripts/deployMedicalRecordRegistry.js`) dan jalankan untuk deploy ke Ganache.
    * Simpan ABI dan alamat kontrak `MedicalRecordRegistry` di `blockchain/build/deployments/`.
    * Update `src/app/core/config.py` untuk memuat ABI dan alamat kontrak baru.
    * Perluas `BlockchainService` (`src/app/core/blockchain.py`) dengan metode untuk berinteraksi dengan `MedicalRecordRegistry` (misalnya `add_medical_record_hash`).

3.  **Backend API (FastAPI):**
    * Buat file endpoint baru `src/app/api/endpoints/medical_records.py`.
    * Implementasikan endpoint `POST /medical-records` untuk membuat rekam medis baru:
        * Endpoint harus menerima data rekam medis (misalnya, dalam format yang mendekati FHIR R4 atau subsetnya untuk metadata, dan data utama yang akan dienkripsi).
        * Data sensitif harus dienkripsi (AES-256-GCM disarankan) sebelum disimpan di field `encrypted_data` (BYTEA) di PostgreSQL. Kunci enkripsi perlu dikelola dengan aman (detail pengelolaan kunci perlu dipikirkan, untuk MVP mungkin bisa disederhanakan atau menggunakan kunci per pengguna yang diturunkan dari password atau disimpan terenkripsi).
        * Hitung `data_hash` (SHA-256) dari data *sebelum* enkripsi.
        * Simpan metadata, `encrypted_data`, dan `data_hash` di tabel `medical_records` PostgreSQL.
        * Panggil `BlockchainService` untuk mencatat `data_hash`, `patient_did`, `record_type`, dan `timestamp` ke smart contract `MedicalRecordRegistry`.
        * Simpan `transaction_hash` dari blockchain ke field `blockchain_record_id` di tabel `medical_records`.
        * Endpoint harus diproteksi dan hanya bisa diakses oleh pengguna yang terautentikasi (misalnya, pasien membuat rekam medis untuk dirinya sendiri, atau dokter untuk pasien dengan consent).
    * Implementasikan endpoint `GET /medical-records/patient/{patient_id}` untuk mengambil daftar metadata rekam medis milik pasien (tanpa `encrypted_data`).
    * Implementasikan endpoint `GET /medical-records/{record_id}` untuk mengambil detail satu rekam medis, termasuk `encrypted_data` (yang perlu didekripsi di sisi klien atau backend setelah otorisasi).
    * Pastikan ada mekanisme otorisasi yang tepat (misalnya, pasien hanya bisa akses datanya sendiri, dokter perlu consent).

4.  **Utilitas Enkripsi/Dekripsi:**
    * Buat modul utilitas (misalnya di `src/app/core/encryption.py`) untuk fungsi enkripsi (AES-256-GCM) dan dekripsi data.
    * Buat fungsi untuk menghitung hash SHA-256.

5.  **Pengujian:**
    * Unit tests untuk model `MedicalRecord` dan skema Pydantic.
    * Unit tests untuk fungsi CRUD `medical_record`.
    * Unit tests untuk fungsi enkripsi/dekripsi dan hashing.
    * Unit tests untuk interaksi dengan smart contract `MedicalRecordRegistry` (mocking Web3).
    * Integration tests untuk endpoint API rekam medis (create, get).
        * Pastikan data dienkripsi dengan benar.
        * Pastikan hash dicatat di blockchain (via mock service).
        * Pastikan otorisasi berfungsi.

## Technical Debt & Issues:

1.  **Authentication & User Management:**
    * **[PENDING]** Perlu mekanisme refresh token.
    * **[PENDING]** Alur reset password belum dirancang.
    * **[PENDING]** Manajemen sesi yang lebih robas (jika refresh token diimplementasikan, ini terkait).
    * **[PENDING]** Pertimbangan 2FA untuk masa depan.
    * **[POTENTIAL]** `UserLogin` Pydantic model didefinisikan di `src/app/models/user.py` tapi digunakan di `src/app/api/endpoints/auth.py` tanpa diimpor secara eksplisit di sana, kemungkinan terimpor via `from ...models.user import *`. Sebaiknya impor eksplisit.

2.  **Database:**
    * **[PENDING]** Perlu optimasi indeks setelah query patterns lebih jelas.
    * **[PENDING]** Fine-tune database pooling untuk production.
    * **[PENDING]** Siapkan strategi backup & restore yang matang.
    * **[PENDING]** Tambahkan query monitoring untuk performa.

3.  **Blockchain:**
    * **[PENDING]** Optimasi gas untuk fungsi smart contract.
    * **[PENDING]** Setup backup node Ganache atau strategi untuk persistensi data dev blockchain yang lebih baik jika `.ganache-db` tidak cukup.
    * **[PENDING]** Strategi upgrade smart contract (untuk `UserRegistry` dan kontrak mendatang).
    * **[PENDING]** Sistem monitoring event dari smart contract.

4.  **Testing:**
    * **[PENDING]** Tes E2E (End-to-End) setelah frontend dasar ada.
    * **[PENDING]** Tes performa (load testing) untuk API.
    * **[PENDING]** Kerangka kerja tes keamanan (misalnya, scanning dependensi, static analysis).

5.  **Lain-lain:**
    * **[PENDING]** Pengelolaan Kunci Enkripsi: Perlu strategi yang jelas dan aman untuk mengelola kunci enkripsi data rekam medis.
    * **[PENDING]** Logging yang lebih terstruktur dan komprehensif di seluruh aplikasi.
    * **[PENDING]** Error handling yang lebih detail dan standar di API.

## Next Meeting Agenda:

1.  Review implementasi Step 1.3 yang telah selesai (singkat, karena sudah direview).
2.  Diskusi mendalam mengenai desain dan implementasi Step 1.4 (Medical Record Data Model and Storage):
    * Finalisasi struktur tabel `medical_records` dan skema Pydantic.
    * Desain fungsi dan event untuk smart contract `MedicalRecordRegistry.sol`.
    * Detail alur API untuk pembuatan dan pengambilan rekam medis (termasuk enkripsi/dekripsi dan interaksi blockchain).
    * Strategi awal pengelolaan kunci enkripsi untuk MVP.
3.  Prioritisasi technical debt yang mungkin perlu ditangani dalam waktu dekat.
4.  Planning untuk sprint berikutnya (fokus pada implementasi Step 1.4).

*(Note: This file was last updated on 2025-05-26 based on completion of Step 1.3.)*