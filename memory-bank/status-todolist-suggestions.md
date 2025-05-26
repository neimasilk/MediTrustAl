# Project Status, To-Do List, and Suggestions: MediTrustAl

## Current Project Status (per 2025-05-27):
* **Project Phase:** Fase 2 - Patient Data Management - MVP Core (Blockchain Interaction)
* **Description:**
    * Step 1.1 (Project Setup), Step 1.2 (Basic Blockchain Network Setup - UserRegistry), dan Step 1.3 (User Identity and Basic Authentication) telah selesai diimplementasikan.
    * Step 2.1 (Basic Patient Health Record Structure on Blockchain - MedicalRecordRegistry) dan Step 2.2 (Basic Off-Chain Data Storage Setup - PostgreSQL dengan enkripsi) juga telah selesai diimplementasikan melalui API `medical_records`. Ini mencakup pembuatan model `MedicalRecord`, CRUD, API untuk membuat dan mengambil rekam medis (dengan enkripsi/dekripsi), perhitungan `data_hash`, dan integrasi dengan _smart contract_ `MedicalRecordRegistry` untuk mencatat `data_hash`.
    * **Step 2.3 (Basic Patient Data Retrieval - Backend)**: Backend untuk pengambilan data pasien dasar telah diimplementasikan. Ini melibatkan modifikasi API `GET /medical-records/patient/me` untuk mengambil daftar hash rekam medis dari `BlockchainService` (awalnya di-mock) dan kemudian mengambil detail dari database. Perubahan pada _smart contract_ `MedicalRecordRegistry.sol` telah disiapkan, namun **deployment _smart contract_ oleh pengguna masih PENDING**.
    * Semua tes untuk fungsionalitas yang ada, termasuk backend Step 2.3, telah lolos.
* **Last Completed Steps (merangkum `implementation-plan.md`):**
    * Step 1.1: Project Setup and Basic Backend Structure - ✅ SELESAI.
    * Step 1.2: Basic Blockchain Network Setup (Local Development - UserRegistry) - ✅ SELESAI.
    * Step 1.3: User Identity and Basic Authentication (Application Layer) - ✅ SELESAI.
    * Step 2.1: Basic Patient Health Record (PHR) Structure on Blockchain (MedicalRecordRegistry) - ✅ SELESAI.
    * Step 2.2: Basic Off-Chain Data Storage Setup (PostgreSQL with Encryption for Medical Records) - ✅ SELESAI.
    * Step 2.3: Basic Patient Data Retrieval (Backend Portion) - ✅ SELESAI (Deployment _smart contract_ oleh pengguna ⏳ PENDING).
* **Next Step (sesuai `implementation-plan.md`):** Menunggu aksi pengguna untuk deployment _smart contract_ `MedicalRecordRegistry.sol` yang telah dimodifikasi (Step 2.3).

## Progress Update (Snapshot 2025-05-27 -> Diperbarui untuk Step 2.3 Backend):
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
    * **[BARU - Step 2.3 Backend]** [x] Unit tes untuk metode `get_record_hashes_for_patient` di `BlockchainService`.
    * **[BARU - Step 2.3 Backend]** [x] Tes integrasi untuk _endpoint_ `GET /medical-records/patient/me` yang dimodifikasi, mencakup berbagai skenario (data cocok, data parsial, tidak ada data blockchain, error service blockchain, paginasi).
    * **[BARU - Step 2.3 Backend]** [x] Dokumentasi kode (komentar) dan `README.md` (catatan developer) telah diperbarui.

## Immediate Next Steps (Menunggu Aksi Pengguna untuk Step 2.3 Blockchain):

Sistem sekarang menunggu aksi dari pengguna (developer utama) untuk mendeploy perubahan pada _smart contract_ `MedicalRecordRegistry.sol` yang telah disiapkan. Perubahan ini mencakup penambahan fungsi `getRecordHashesByPatient` dan modifikasi terkait untuk mendukung Step 2.3.

1.  **Aksi Pengguna (Developer Utama):**
    *   Deploy _smart contract_ `MedicalRecordRegistry.sol` yang telah dimodifikasi ke jaringan Ganache lokal.
    *   Verifikasi deployment berhasil.
    *   Sediakan informasi ABI dan alamat kontrak yang baru jika ada perubahan dari yang sebelumnya di-mock atau digunakan.

2.  **Setelah Konfirmasi Deployment oleh Pengguna, Langkah Berikutnya oleh Sistem/AI:**
    *   **Update Konfigurasi Backend**: Perbarui file konfigurasi `.env` dan/atau `src/app/core/config.py` dengan ABI dan alamat kontrak `MedicalRecordRegistry` yang baru (jika berubah).
    *   **Review `BlockchainService`**: Tinjau kembali metode `get_record_hashes_for_patient` di `BlockchainService`. Sesuaikan implementasi jika interaksi aktual dengan _smart contract_ yang di-deploy berbeda dari asumsi saat mocking (misalnya, terkait format data yang dikembalikan atau parameter fungsi).
    *   **Pengujian Integrasi Penuh**: Jalankan kembali semua tes integrasi, khususnya yang terkait dengan `GET /medical-records/patient/me`, untuk memastikan fungsionalitas bekerja dengan benar terhadap _smart contract_ yang "live" di Ganache.
    *   **Verifikasi Fungsional**: Lakukan verifikasi fungsional manual (jika memungkinkan dalam lingkungan pengembangan) untuk memastikan alur pengambilan data rekam medis pasien berjalan sesuai harapan.

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
    * **[BARU - Terkait Step 2.3]** Struktur data di `MedicalRecordRegistry.sol` untuk menyimpan dan mengambil _record_ per pasien secara efisien telah diimplementasikan (penyimpanan `patientRecordHashes`). Efisiensi perlu diverifikasi lebih lanjut pada skala besar.
4.  **Testing:**
    * **[PENDING]** Tes E2E (End-to-End) setelah _frontend_ dasar ada.
    * **[PENDING]** Tes performa (load testing) untuk API.
    * **[BARU - Step 2.3]** Pengujian integrasi penuh untuk `get_record_hashes_for_patient` dan endpoint `GET /medical-records/patient/me` dengan _smart contract_ yang "live" di Ganache (setelah deployment oleh pengguna).
5.  **Lain-lain:**
    * **[MITIGATED FOR MVP]** Pengelolaan Kunci Enkripsi: Penggunaan JWT _secret_ untuk kunci enkripsi sudah dicatat sebagai solusi MVP.
    * **[IMPROVED]** _Logging_ telah ditambahkan di beberapa area kritis (misalnya, `get_my_medical_records` untuk diskrepansi data), namun _logging_ yang lebih terstruktur dan komprehensif masih PENDING.
    * **[PENDING]** _Error handling_ yang lebih detail dan standar di API.
    * **[POTENTIAL]** Peran `/api/v1/users/register` perlu diklarifikasi atau di-deprecate.

## Next Meeting Agenda:

1.  **Review Deployment Smart Contract oleh Pengguna (Step 2.3)**:
    *   Konfirmasi status deployment _smart contract_ `MedicalRecordRegistry.sol` yang telah dimodifikasi.
    *   Diskusikan kendala atau isu yang muncul saat deployment oleh pengguna.
    *   Kumpulkan informasi ABI dan alamat kontrak baru (jika ada).
2.  **Perencanaan Integrasi Penuh Step 2.3**:
    *   Rencanakan langkah-langkah untuk mengintegrasikan backend dengan _smart contract_ yang baru di-deploy (update config, review `BlockchainService`).
    *   Alokasikan waktu untuk pengujian integrasi penuh terhadap Ganache.
3.  **Prioritisasi Technical Debt**: Tinjau kembali daftar _technical debt_ dan prioritaskan item yang paling mendesak atau berdampak.
4.  **Perencanaan Sprint Berikutnya**: Setelah Step 2.3 selesai sepenuhnya (termasuk integrasi dengan kontrak live), diskusikan target untuk _sprint_ berikutnya (misalnya, memulai Step 2.4 atau menangani _technical debt_ prioritas).

*(Note: This file was last updated on 2025-05-27 based on completion of medical records API and related functionalities, and subsequently updated for Step 2.3 backend completion.)*