# Project Status, To-Do List, and Suggestions: MediTrustAl

## Current Project Status (per 2025-05-27):
* **Project Phase:** Fase 2 - Patient Data Management - MVP Core (Blockchain Interaction)
* **Description:**
    * Step 1.1 (Project Setup), Step 1.2 (Basic Blockchain Network Setup - UserRegistry), dan Step 1.3 (User Identity and Basic Authentication) telah selesai diimplementasikan.
    * Step 2.1 (Basic Patient Health Record Structure on Blockchain - MedicalRecordRegistry) dan Step 2.2 (Basic Off-Chain Data Storage Setup - PostgreSQL dengan enkripsi) juga telah selesai diimplementasikan melalui API `medical_records`. Ini mencakup pembuatan model `MedicalRecord`, CRUD, API untuk membuat dan mengambil rekam medis (dengan enkripsi/dekripsi), perhitungan `data_hash`, dan integrasi dengan _smart contract_ `MedicalRecordRegistry` untuk mencatat `data_hash`.
    * Semua tes untuk fungsionalitas yang ada telah lolos.
* **Last Completed Steps (merangkum `implementation-plan.md`):**
    * Step 1.1: Project Setup and Basic Backend Structure - ✅ SELESAI.
    * Step 1.2: Basic Blockchain Network Setup (Local Development - UserRegistry) - ✅ SELESAI.
    * Step 1.3: User Identity and Basic Authentication (Application Layer) - ✅ SELESAI.
    * Step 2.1: Basic Patient Health Record (PHR) Structure on Blockchain (MedicalRecordRegistry) - ✅ SELESAI.
    * Step 2.2: Basic Off-Chain Data Storage Setup (PostgreSQL with Encryption for Medical Records) - ✅ SELESAI.
* **Next Step (sesuai `implementation-plan.md`):** Step 2.3: Basic Patient Data Retrieval - ⏳ PENDING.

## Progress Update (Snapshot 2025-05-27):
1.  **Database Setup** ✅ SELESAI
    * [x] Instalasi dan konfigurasi PostgreSQL 15.x.
    * [x] Pembuatan model database (`User`, `MedicalRecord`).
    * [x] Pengaturan migrasi Alembic dan migrasi awal untuk tabel `users` dan `medical_records`.
    * [x] Konfigurasi koneksi database.

2.  **Authentication System** ✅ SELESAI
    * [x] Implementasi token JWT (pembuatan, dekode).
    * [x] Hashing password dengan bcrypt.
    * [x] Skema Pydantic untuk User (request, response, login).
    * [x] Implementasi Endpoint Registrasi Aplikasi Lengkap (termasuk validasi duplikasi).
    * [x] Implementasi Endpoint Login Aplikasi (username/email).
    * [x] Implementasi Middleware Proteksi Rute menggunakan JWT (`get_current_active_user`).
    * [x] Implementasi Generasi DID sesuai format `did:meditrustal:{base58(sha256(user_id))}`.

3.  **Blockchain Integration (User Registry & Medical Record Registry)** ✅ SELESAI
    * [x] Setup Ganache (sesuai `README.md` dan `hardhat.config.js`).
    * [x] _Smart contract_ dasar `UserRegistry` dan `MedicalRecordRegistry` sudah di-deploy (via skrip `deployUserRegistry.js` & `deployMedicalRecordRegistry.js`).
    * [x] Service (`BlockchainService` di `blockchain.py`) untuk interaksi dengan kontrak `UserRegistry` (register user, get role) dan `MedicalRecordRegistry` (add medical record hash).
    * [x] Penandatanganan Transaksi Blockchain menggunakan _private key_ dari _environment variable_.
    * [x] Integrasi pemanggilan `blockchain_service.register_user` ke dalam alur registrasi aplikasi.
    * [x] Integrasi pemanggilan `blockchain_service.add_medical_record_hash` ke dalam alur pembuatan rekam medis.

4.  **Medical Record Management (MVP Core)** ✅ SELESAI
    * [x] Model SQLAlchemy `MedicalRecord` dan skema Pydantic terkait.
    * [x] Fungsi CRUD untuk `MedicalRecord`.
    * [x] API Endpoint `POST /medical-records` untuk membuat rekam medis baru (termasuk enkripsi data, _hashing_, penyimpanan ke DB, dan pencatatan _hash_ ke _blockchain_).
    * [x] API Endpoint `GET /medical-records/patient/me` untuk mengambil daftar rekam medis milik pasien saat ini (dari DB, _metadata only_).
    * [x] API Endpoint `GET /medical-records/{record_id}` untuk mengambil detail satu rekam medis, termasuk data mentah yang sudah didekripsi (dari DB).
    * [x] Implementasi enkripsi AES-GCM untuk `raw_data` dan SHA-256 untuk `data_hash`.

5.  **Testing** ✅ SELESAI (untuk fitur yang ada)
    * [x] Unit tes untuk utilitas (enkripsi, generasi DID).
    * [x] Unit tes untuk CRUD (`medical_record`).
    * [x] Unit tes untuk `BlockchainService` (interaksi dengan `MedicalRecordRegistry`).
    * [x] Tes integrasi untuk _endpoint auth_ (register, login).
    * [x] Tes integrasi untuk _endpoint_ yang diproteksi (`/users/me`).
    * [x] Tes integrasi untuk _endpoint_ API rekam medis (create, get list, get detail).
    * [x] Pengaturan _test fixtures_ dan _mocking_ (SQLite _in-memory database_, _mock blockchain service_).
    * [x] Tes _smart contract_ `MedicalRecordRegistry.test.js`.

## Immediate Next Steps (Implementasi Step 2.3 - Basic Patient Data Retrieval):

Fokus utama adalah memungkinkan pasien mengambil _metadata_ rekam medis mereka yang berasal dari _blockchain_, dan kemudian menggunakan informasi tersebut (jika diperlukan) untuk mengambil data lengkap dari _off-chain storage_.

1.  **Smart Contract (`MedicalRecordRegistry.sol`):**
    * Implementasikan fungsi baru `getRecordHashesByPatient(string memory patientDid) external view returns (bytes32[] memory, string[] memory, uint256[] memory)` yang mengembalikan _array_ dari `recordHash`, `recordType`, dan `timestamp` untuk `patientDid` tertentu.
        * Ini memerlukan penyimpanan daftar `recordHash` per `patientDid` di dalam kontrak, atau iterasi melalui semua _record_ (kurang efisien untuk banyak _record_). Pertimbangkan struktur data yang efisien di kontrak (misalnya, `mapping(string => bytes32[]) private patientRecords;`).
    * Pastikan event `RecordAdded` sudah mencakup semua informasi yang relevan (`recordHash`, `patientDid`, `recordType`, `timestamp`, `submitter`). (Event sudah ada dan cukup baik).
    * Update skrip deployment Hardhat jika ada perubahan signifikan pada penyimpanan atau konstruktor.
    * Update `blockchain/test/MedicalRecordRegistry.test.js` untuk menguji fungsi baru `getRecordHashesByPatient`.

2.  **Backend (`BlockchainService` dan API):**
    * Perluas `BlockchainService` (`src/app/core/blockchain.py`) dengan metode baru, misal `async def get_medical_record_metadata_from_blockchain(self, patient_did: str) -> dict:`. Metode ini akan memanggil fungsi `getRecordHashesByPatient` dari _smart contract_.
    * Modifikasi _endpoint_ `GET /api/v1/medical-records/patient/me` (`src/app/api/endpoints/medical_records.py`):
        * Panggil metode baru di `BlockchainService` untuk mendapatkan daftar _metadata_ (`recordHash`, `recordType`, `timestamp`) dari _blockchain_ untuk `current_user.did`.
        * Untuk setiap `recordHash` yang diterima, cari _record_ yang sesuai di tabel `medical_records` PostgreSQL berdasarkan kolom `data_hash`.
        * Gabungkan informasi dari _blockchain_ dan PostgreSQL (misalnya, `id` dari DB, `blockchain_record_id`, `created_at` dari DB, dan `recordType`, `timestamp` dari _blockchain_ sebagai sumber kebenaran) untuk membentuk respons.
        * Respons harus tetap berupa `List[MedicalRecordResponse]`, pastikan data yang dikembalikan konsisten dan tidak membingungkan antara sumber DB dan _blockchain_. Pertimbangkan untuk memperbarui `MedicalRecordResponse` jika perlu field tambahan dari _blockchain_.
    * Endpoint `GET /api/v1/medical-records/{record_id}` (`src/app/api/endpoints/medical_records.py`):
        * Tetap berfungsi seperti sekarang (mengambil dari DB berdasarkan `record_id` UUID dan mendekripsi). Alur "menggunakan _off-chain reference_ yang diperoleh dari _blockchain record_" diimplementasikan dengan _frontend_ pertama kali mendapatkan daftar (yang mungkin berisi UUID DB dari langkah di atas) dan kemudian menggunakan UUID tersebut untuk _endpoint_ ini.

3.  **Skema Pydantic (`src/app/models/medical_record.py`):**
    * Tinjau `MedicalRecordResponse`. Apakah perlu dimodifikasi untuk mengakomodasi data _timestamp_ yang mungkin berasal dari _blockchain_ (jika berbeda dari `created_at` di DB)? Untuk MVP, mungkin bisa disamakan atau `created_at` DB dianggap cukup. `implementation-plan.md` menyebut `timestamp` sebagai bagian dari _metadata_ dari _blockchain_.

4.  **Pengujian:**
    * Unit tes untuk metode baru di `BlockchainService` (mocking Web3).
    * _Integration test_ untuk _endpoint_ `GET /medical-records/patient/me` yang dimodifikasi. Pastikan data yang dikembalikan adalah gabungan yang benar dan otorisasi berfungsi.

## Technical Debt & Issues (Beberapa Diambil dari Status Sebelumnya):

1.  **Authentication & User Management:**
    * **[PENDING]** Mekanisme _refresh token_.
    * **[PENDING]** Alur reset password.
    * **[PENDING]** Manajemen sesi yang lebih robas.
2.  **Database:**
    * **[PENDING]** Optimasi indeks lebih lanjut setelah _query patterns_ lebih jelas.
    * **[PENDING]** Fine-tune _database pooling_ untuk produksi.
    * **[PENDING]** Strategi _backup & restore_ yang matang.
3.  **Blockchain:**
    * **[PENDING]** Optimasi gas untuk fungsi _smart contract_, terutama jika ada iterasi.
    * **[PENDING]** Strategi _upgrade smart contract_.
    * **[PENDING]** Sistem _monitoring event_ dari _smart contract_ (berguna untuk sinkronisasi data atau notifikasi).
    * **[BARU]** Struktur data di `MedicalRecordRegistry.sol` untuk menyimpan dan mengambil _record_ per pasien secara efisien.
4.  **Testing:**
    * **[PENDING]** Tes E2E (End-to-End) setelah _frontend_ dasar ada.
    * **[PENDING]** Tes performa (load testing) untuk API.
5.  **Lain-lain:**
    * **[MITIGATED FOR MVP]** Pengelolaan Kunci Enkripsi: Penggunaan JWT _secret_ untuk kunci enkripsi sudah dicatat sebagai solusi MVP.
    * **[PENDING]** _Logging_ yang lebih terstruktur dan komprehensif di seluruh aplikasi.
    * **[PENDING]** _Error handling_ yang lebih detail dan standar di API.
    * **[POTENTIAL]** Peran `/api/v1/users/register` perlu diklarifikasi atau di-deprecate.

## Next Meeting Agenda:

1.  Review singkat penyelesaian implementasi API `medical_records` (Step 2.1 & 2.2).
2.  Diskusi mendalam mengenai desain dan implementasi **Step 2.3 (Basic Patient Data Retrieval)**:
    * Finalisasi desain fungsi _query_ di `MedicalRecordRegistry.sol` (misalnya `getRecordHashesByPatient`).
    * Struktur data di _smart contract_ untuk mendukung _query_ tersebut.
    * Detail alur API `GET /medical-records/patient/me` (bagaimana data _blockchain_ dan DB digabungkan).
    * Skema respons Pydantic yang final untuk _metadata_ rekam medis.
3.  Prioritisasi _technical debt_ yang mungkin perlu ditangani dalam waktu dekat.
4.  Perencanaan untuk _sprint_ berikutnya (fokus pada implementasi Step 2.3).

*(Note: This file was last updated on 2025-05-27 based on completion of medical records API and related functionalities.)*