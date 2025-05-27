# Project Status, To-Do List, and Suggestions: MediTrustAl

## Current Project Status (per 2025-05-27):
* **Project Phase:** Fase 2 - Patient Data Management - MVP Core (Blockchain Interaction)
* **Description:**
    * Step 1.1 (Project Setup), Step 1.2 (Basic Blockchain Network Setup - UserRegistry), dan Step 1.3 (User Identity and Basic Authentication) telah selesai diimplementasikan.
    * Step 2.1 (Basic Patient Health Record Structure on Blockchain - MedicalRecordRegistry) dan Step 2.2 (Basic Off-Chain Data Storage Setup - PostgreSQL dengan enkripsi) juga telah selesai diimplementasikan melalui API `medical_records`. Ini mencakup pembuatan model `MedicalRecord`, CRUD, API untuk membuat dan mengambil rekam medis (dengan enkripsi/dekripsi), perhitungan `data_hash`, dan integrasi dengan _smart contract_ `MedicalRecordRegistry` untuk mencatat `data_hash`.
    * **Step 2.3 (Basic Patient Data Retrieval - Backend)**: Backend untuk pengambilan data pasien dasar telah diimplementasikan. Ini melibatkan modifikasi API `GET /medical-records/patient/me` untuk mengambil daftar hash rekam medis dari `BlockchainService` (di-mock untuk tes unit dan integrasi awal) dan kemudian mengambil detail dari database. Perubahan pada _smart contract_ `MedicalRecordRegistry.sol` telah disiapkan dan dites (`MedicalRecordRegistry.test.js`).
* **Last Completed Steps (merangkum `implementation-plan.md`):**
    * Step 1.1: Project Setup and Basic Backend Structure - ✅ SELESAI.
    * Step 1.2: Basic Blockchain Network Setup (Local Development - UserRegistry) - ✅ SELESAI.
    * Step 1.3: User Identity and Basic Authentication (Application Layer) - ✅ SELESAI.
    * Step 2.1: Basic Patient Health Record (PHR) Structure on Blockchain (MedicalRecordRegistry - initial deployment) - ✅ SELESAI.
    * Step 2.2: Basic Off-Chain Data Storage Setup (PostgreSQL with Encryption for Medical Records) - ✅ SELESAI.
    * Step 2.3: Basic Patient Data Retrieval (Backend Logic with Mocked Blockchain & Smart Contract Modification) - ✅ SELESAI.
* **Next Step (sesuai `implementation-plan.md` dan review saat ini):** Menunggu aksi pengguna (developer utama) untuk **mendeploy _smart contract_ `MedicalRecordRegistry.sol` yang telah dimodifikasi (termasuk fungsi `getRecordHashesByPatient`) ke jaringan Ganache lokal.** Setelah itu, integrasi penuh backend dengan smart contract yang "live".

## Progress Update (Snapshot 2025-05-27 - Mencerminkan status saat ini):
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

3.  **Blockchain Integration (User Registry & Medical Record Registry)** ✅ SELESAI (untuk fungsionalitas hingga pencatatan hash rekam medis)
    * [x] Setup Ganache (sesuai `README.md` dan `hardhat.config.js`).
    * [x] _Smart contract_ dasar `UserRegistry` dan `MedicalRecordRegistry` (versi awal) sudah di-deploy (via skrip `deployUserRegistry.js` & `deployMedicalRecordRegistry.js`).
    * [x] Service (`BlockchainService` di `blockchain.py`) untuk interaksi dengan kontrak `UserRegistry` (register user, get role) dan `MedicalRecordRegistry` (add medical record hash).
    * [x] Penandatanganan Transaksi Blockchain menggunakan _private key_ dari _environment variable_.
    * [x] Integrasi pemanggilan `blockchain_service.register_user` ke dalam alur registrasi aplikasi.
    * [x] Integrasi pemanggilan `blockchain_service.add_medical_record_hash` ke dalam alur pembuatan rekam medis.
    * [x] Modifikasi _Smart Contract_ `MedicalRecordRegistry.sol` untuk menyertakan `getRecordHashesByPatient`.
    * [x] Implementasi metode `get_record_hashes_for_patient` di `BlockchainService`.

4.  **Medical Record Management (MVP Core)** ✅ SELESAI (Backend logic)
    * [x] Model SQLAlchemy `MedicalRecord` dan skema Pydantic terkait.
    * [x] Fungsi CRUD untuk `MedicalRecord`.
    * [x] API Endpoint `POST /medical-records` untuk membuat rekam medis baru (termasuk enkripsi data, _hashing_, penyimpanan ke DB, dan pencatatan _hash_ ke _blockchain_).
    * [x] API Endpoint `GET /medical-records/patient/me` untuk mengambil daftar rekam medis milik pasien saat ini (menggunakan hash dari `BlockchainService` dan data dari DB).
    * [x] API Endpoint `GET /medical-records/{record_id}` untuk mengambil detail satu rekam medis, termasuk data mentah yang sudah didekripsi (dari DB).
    * [x] Implementasi enkripsi AES-GCM untuk `raw_data` dan SHA-256 untuk `data_hash`.

5.  **Testing** ✅ SELESAI (untuk fitur yang ada, dengan mock blockchain untuk Step 2.3)
    * [x] Unit tes untuk utilitas (enkripsi, generasi DID).
    * [x] Unit tes untuk CRUD (`medical_record`).
    * [x] Unit tes untuk `BlockchainService` (interaksi dengan `UserRegistry` dan `MedicalRecordRegistry`, termasuk `get_record_hashes_for_patient`).
    * [x] Tes integrasi untuk _endpoint auth_ (register, login).
    * [x] Tes integrasi untuk _endpoint_ yang diproteksi (`/users/me`).
    * [x] Tes integrasi untuk _endpoint_ API rekam medis (create, get list, get detail), termasuk tes untuk `GET /medical-records/patient/me` yang dimodifikasi dengan berbagai skenario (data cocok, parsial, tidak ada data blockchain, error service blockchain, paginasi).
    * [x] Pengaturan _test fixtures_ dan _mocking_ (SQLite _in-memory database_, _mock blockchain service_).
    * [x] Tes _smart contract_ `MedicalRecordRegistry.test.js` (termasuk `getRecordHashesByPatient`).
    * [x] Dokumentasi kode (komentar) dan `README.md` (catatan developer) telah diperbarui untuk Step 2.3.

## Immediate Next Steps (Menunggu Aksi Pengguna untuk Step 2.3 Blockchain):

Sistem sekarang menunggu aksi dari Anda (developer utama) untuk mendeploy perubahan pada _smart contract_ `MedicalRecordRegistry.sol` yang telah disiapkan dan dites.

1.  **Aksi Pengguna (Developer Utama):**
    * Pastikan Ganache berjalan (sesuai `README.md` Port: 7545, RPC Server: `http://127.0.0.1:7545`).
    * Compile ulang _smart contract_ jika ada perubahan terakhir:
        ```bash
        cd blockchain
        npx hardhat compile
        ```
    * Deploy _smart contract_ `MedicalRecordRegistry.sol` **yang telah dimodifikasi** ke jaringan Ganache lokal menggunakan skrip yang telah disesuaikan (jika `scripts/deployMedicalRecordRegistry.js` sudah benar, gunakan itu):
        ```bash
        cd blockchain # jika belum di direktori blockchain
        npx hardhat run scripts/deployMedicalRecordRegistry.js --network ganache
        ```
    * Verifikasi deployment berhasil dan catat alamat kontrak `MedicalRecordRegistry` yang baru. ABI seharusnya sudah ada di `blockchain/artifacts/blockchain/contracts/MedicalRecordRegistry.sol/MedicalRecordRegistry.json`.
    * Pastikan file `blockchain/build/deployments/MedicalRecordRegistry-address.json` dan `MedicalRecordRegistry-abi.json` terupdate dengan benar oleh skrip deployment.

2.  **Setelah Konfirmasi Deployment oleh Pengguna, Langkah Berikutnya oleh Sistem/AI (sesuai `baby-step.md` berikutnya):**
    * **Update Konfigurasi Backend**: Sistem akan secara otomatis mencoba memuat ABI dan alamat kontrak yang baru melalui `load_contract_info()` di `src/app/core/config.py` saat aplikasi FastAPI dimulai ulang. Pastikan file JSON alamat dan ABI di `blockchain/build/deployments/` sudah benar.
    * **Verifikasi `BlockchainService`**: Tinjau kembali metode `get_record_hashes_for_patient` di `src/app/core/blockchain.py`. Pastikan implementasinya sudah sesuai untuk berinteraksi dengan kontrak yang "live", bukan mock. (Ini seharusnya sudah benar karena unit test untuk service ini sudah ada).
    * **Pengujian Integrasi Penuh**: Jalankan kembali semua tes integrasi, khususnya yang ada di `tests/integration/api/test_api_medical_records.py`, untuk memastikan fungsionalitas `GET /medical-records/patient/me` bekerja dengan benar terhadap _smart contract_ yang "live" di Ganache. Mocking untuk `get_blockchain_service` di `conftest.py` mungkin perlu disesuaikan untuk tes tertentu agar menggunakan instance `BlockchainService` yang sesungguhnya yang terhubung ke Ganache, atau memastikan mock merefleksikan perilaku kontrak live secara akurat jika tes isolasi masih diinginkan.
    * **Verifikasi Fungsional**: (Opsional, jika ada UI atau alat seperti Postman) Lakukan verifikasi fungsional manual untuk memastikan alur pengambilan data rekam medis pasien berjalan sesuai harapan.

## Technical Debt & Issues:

1.  **Authentication & User Management:**
    * **[PENDING]** Mekanisme _refresh token_.
    * **[PENDING]** Alur reset password.
    * **[PENDING]** Manajemen sesi yang lebih robas.
2.  **Database:**
    * **[PENDING]** Optimasi indeks lebih lanjut setelah _query patterns_ lebih jelas.
    * **[PENDING]** Fine-tune _database pooling_ untuk produksi.
    * **[PENDING]** Strategi _backup & restore_ yang matang (lihat `database-schema.md`).
3.  **Blockchain:**
    * **[PENDING]** Optimasi gas untuk fungsi _smart contract_, terutama jika ada iterasi.
    * **[PENDING]** Strategi _upgrade smart contract_ yang lebih matang.
    * **[PENDING]** Sistem _monitoring event_ dari _smart contract_ (berguna untuk sinkronisasi data atau notifikasi).
    * **[VERIFIED - Step 2.3]** Struktur data di `MedicalRecordRegistry.sol` untuk `patientRecordHashes` (`mapping(string => bytes32[])`) sudah diimplementasikan dan dites. Efisiensi pada skala besar perlu menjadi perhatian di masa depan.
4.  **Testing:**
    * **[PENDING]** Tes E2E (End-to-End) setelah _frontend_ dasar ada.
    * **[PENDING]** Tes performa (load testing) untuk API.
    * **[NEXT]** Pengujian integrasi penuh untuk `get_record_hashes_for_patient` dan endpoint `GET /medical-records/patient/me` dengan _smart contract_ yang "live" di Ganache (setelah deployment oleh pengguna).
5.  **Lain-lain:**
    * **[MITIGATED FOR MVP]** Pengelolaan Kunci Enkripsi: Penggunaan JWT _secret_ untuk kunci enkripsi (MVP).
    * **[IMPROVED]** _Logging_ telah ditambahkan di `medical_records.py`. Perluasan _logging_ terstruktur dan komprehensif masih PENDING.
    * **[PENDING]** _Error handling_ yang lebih detail dan standar di seluruh API (lihat `implementation-plan.md` bagian "API Standards & Error Handling").
    * **[POTENTIAL]** Endpoint `/api/v1/users/register` tampaknya duplikasi fungsionalitas dengan `/api/v1/auth/register` dan mungkin perlu diklarifikasi atau di-deprecate. Fokus pada `/api/v1/auth/register` untuk pendaftaran pengguna aplikasi yang juga mendaftarkan ke blockchain.

## Next Meeting Agenda:

1.  **Konfirmasi Deployment Smart Contract `MedicalRecordRegistry.sol` (Step 2.3 oleh Pengguna)**:
    * Verifikasi status deployment _smart contract_ `MedicalRecordRegistry.sol` yang telah dimodifikasi oleh Anda.
    * Pastikan alamat kontrak dan ABI sudah terupdate di `blockchain/build/deployments/` dan dapat dimuat oleh `src/app/core/config.py`.
2.  **Review Hasil Pengujian Integrasi Penuh Step 2.3**:
    * Jalankan dan diskusikan hasil dari `pytest tests/integration/api/test_api_medical_records.py` setelah backend terhubung dengan _smart contract_ yang "live".
    * Identifikasi dan selesaikan masalah yang mungkin muncul.
3.  **Perencanaan Implementasi Step 2.3 - Bagian Frontend (jika Backend sudah stabil)**:
    * Diskusikan bagaimana frontend akan mengkonsumsi endpoint `GET /api/v1/phr` (alias `GET /medical-records/patient/me`) dan `GET /api/v1/phr/{recordId}/data` (alias `GET /medical-records/{record_id}`).
    * Ini adalah langkah berikutnya sesuai `implementation-plan.md` setelah backend Step 2.3 selesai.
4.  **Prioritisasi Technical Debt**: Tinjau kembali daftar _technical debt_ dan pilih item yang paling mendesak.
5.  **Pembahasan Awal Step 3 (Placeholder NLP & AI, Frontend Shell)**: Jika Step 2.3 sudah sepenuhnya stabil, mulai diskusikan perencanaan untuk Step 3.1, 3.2, dan 3.3 dari `implementation-plan.md`.

*(Note: This file was last updated on 2025-05-27 based on completion of backend logic for Step 2.3 and review of existing codebase.)*