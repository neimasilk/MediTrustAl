# Project Status, To-Do List, and Suggestions: MediTrustAl

## Current Project Status (per 2025-05-27):
* **Project Phase:** Fase 3 - AI/ML Integration & Frontend Shell - SEDANG BERLANGSUNG.
* **Description:**
    * Step 1.1 (Project Setup), Step 1.2 (Basic Blockchain Network Setup - UserRegistry), dan Step 1.3 (User Identity and Basic Authentication) telah selesai diimplementasikan.
    * Step 2.1 (Basic Patient Health Record Structure on Blockchain - MedicalRecordRegistry) dan Step 2.2 (Basic Off-Chain Data Storage Setup - PostgreSQL dengan enkripsi) juga telah selesai diimplementasikan melalui API `medical_records`. Ini mencakup pembuatan model `MedicalRecord`, CRUD, API untuk membuat dan mengambil rekam medis (dengan enkripsi/dekripsi), perhitungan `data_hash`, dan integrasi dengan _smart contract_ `MedicalRecordRegistry` untuk mencatat `data_hash`.
    * Step 2.3 (Basic Patient Data Retrieval - Backend & Blockchain Integration) telah selesai. Backend (`GET /medical-records/patient/me`) berhasil mengambil daftar hash rekam medis dari _smart contract_ `MedicalRecordRegistry` yang sudah di-deploy di Ganache dan kemudian mengambil data yang sesuai dari database.
    * Step 3.1 (Placeholder NLP Service) telah selesai diimplementasikan.
    * Step 3.2 (Placeholder AI Predictive Service) telah selesai diimplementasikan.
* **Last Completed Steps (merangkum `implementation-plan.md`):**
    * Step 1.1: Project Setup and Basic Backend Structure - ✅ SELESAI.
    * Step 1.2: Basic Blockchain Network Setup (Local Development - UserRegistry) - ✅ SELESAI.
    * Step 1.3: User Identity and Basic Authentication (Application Layer) - ✅ SELESAI.
    * Step 2.1: Basic Patient Health Record (PHR) Structure on Blockchain (MedicalRecordRegistry - initial deployment) - ✅ SELESAI.
    * Step 2.2: Basic Off-Chain Data Storage Setup (PostgreSQL with Encryption for Medical Records) - ✅ SELESAI.
    * Step 2.3: Basic Patient Data Retrieval (Full Backend Logic & Integration with "Live" Ganache Smart Contract) - ✅ SELESAI.
    * Step 3.1: Placeholder NLP Service - ✅ SELESAI.
    * Step 3.2: Placeholder AI Predictive Service - ✅ SELESAI.
    * Step 3.3: Basic Frontend Shell (Patient Portal) - ✅ SELESAI.
* **Next Step (sesuai `implementation-plan.md`):** Rancang Baby Step Berikutnya.

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

3.  **Blockchain Integration (User Registry & Medical Record Registry)** ✅ SELESAI
    * [x] Setup Ganache (sesuai `README.md` dan `hardhat.config.js`).
    * [x] _Smart contract_ dasar `UserRegistry` dan `MedicalRecordRegistry` telah di-deploy.
    * [x] Service (`BlockchainService` di `blockchain.py`) untuk interaksi dengan kontrak `UserRegistry` (register user, get role) dan `MedicalRecordRegistry` (add medical record hash, get record hashes for patient).
    * [x] Penandatanganan Transaksi Blockchain menggunakan _private key_ dari _environment variable_.
    * [x] Integrasi pemanggilan `blockchain_service.register_user` ke dalam alur registrasi aplikasi.
    * [x] Integrasi pemanggilan `blockchain_service.add_medical_record_hash` ke dalam alur pembuatan rekam medis.
    * [x] Modifikasi _Smart Contract_ `MedicalRecordRegistry.sol` untuk menyertakan `getRecordHashesByPatient` telah diimplementasikan, dites, dan di-deploy.
    * [x] Implementasi metode `get_record_hashes_for_patient` di `BlockchainService` dan integrasinya dengan endpoint API terkait.

4.  **Medical Record Management (MVP Core)** ✅ SELESAI
    * [x] Model SQLAlchemy `MedicalRecord` dan skema Pydantic terkait.
    * [x] Fungsi CRUD untuk `MedicalRecord`.
    * [x] API Endpoint `POST /medical-records` untuk membuat rekam medis baru.
    * [x] API Endpoint `GET /medical-records/patient/me` untuk mengambil daftar rekam medis milik pasien saat ini.
    * [x] API Endpoint `GET /medical-records/{record_id}` untuk mengambil detail satu rekam medis.
    * [x] Implementasi enkripsi AES-GCM untuk `raw_data` dan SHA-256 untuk `data_hash`.

5.  **Testing** ✅ SELESAI (untuk fitur hingga Step 3.2)
    * [x] Unit tes untuk utilitas (enkripsi, generasi DID).
    * [x] Unit tes untuk CRUD (`medical_record`).
    * [x] Unit tes untuk `BlockchainService`.
    * [x] Tes integrasi untuk _endpoint auth_ (register, login).
    * [x] Tes integrasi untuk _endpoint_ yang diproteksi (`/users/me`).
    * [x] Tes integrasi untuk _endpoint_ API rekam medis.
    * [x] Pengaturan _test fixtures_ dan _mocking_.
    * [x] Tes _smart contract_ `MedicalRecordRegistry.test.js`.
    * [x] Dokumentasi kode (komentar) dan `README.md` (catatan developer) telah diperbarui.

6.  **NLP Service (Placeholder - Step 3.1)** ✅ SELESAI
    * [x] Implementasi Placeholder NLP Service (`nlp_service.py`).
    * [x] Implementasi API Endpoint `POST /api/v1/nlp/extract-entities` (`nlp.py`).
    * [x] Penambahan Pydantic model untuk request/response NLP.
    * [x] Registrasi router NLP di `main.py`.
    * [x] Tes unit untuk `nlp_service.py`.
    * [x] Tes integrasi untuk API endpoint NLP.
    * [x] Verifikasi dan pembaruan dokumentasi OpenAPI (Swagger).

7.  **AI Predictive Service (Placeholder - Step 3.2)** ✅ SELESAI
    * [x] Implementasi Placeholder AI Service (`ai_service.py`).
    * [x] Implementasi API Endpoint `POST /api/v1/ai/predict-risk` (`ai.py`).
    * [x] Penambahan Pydantic model untuk request/response AI Prediction.
    * [x] Registrasi router AI di `main.py`.
    * [x] Tes unit untuk `ai_service.py`.
    * [x] Tes integrasi untuk API endpoint AI.
    * [x] Verifikasi dan pembaruan dokumentasi OpenAPI (Swagger).

8.  **Basic Frontend Shell (Patient Portal - Step 3.3)** ✅ SELESAI
    * [x] Setup proyek frontend dasar (React.js dengan Vite).
    * [x] Implementasi halaman login (UI, service, panggil API, simpan token).
    * [x] Pengaturan state management (Redux Toolkit untuk auth).
    * [x] Implementasi protected routes.
    * [x] Implementasi halaman dashboard dasar (logout, panggil API untuk rekam medis, tampilkan data).
    * [x] Konfigurasi CORS di backend.
    * [x] Pembuatan panduan tes manual (`petunjuk-manual-test.md`).

## Immediate Next Steps (Baby-Step To-Do List):

1.  **Rancang Baby Step Berikutnya:** Tentukan detail untuk langkah implementasi selanjutnya (misalnya, Step 3.4 atau fitur frontend berikutnya).

## Technical Debt & Future Considerations:

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
    * **[INFO]** Struktur data di `MedicalRecordRegistry.sol` untuk `patientRecordHashes` (`mapping(string => bytes32[])`) sudah diimplementasikan. Efisiensi pada skala besar perlu menjadi perhatian di masa depan.
4.  **Testing:**
    * **[PENDING]** Tes E2E (End-to-End) setelah _frontend_ dasar ada.
    * **[PENDING]** Tes performa (load testing) untuk API.
5.  **Dokumentasi & Lain-lain:**
    * **[MITIGATED FOR MVP]** Pengelolaan Kunci Enkripsi: Penggunaan JWT _secret_ untuk kunci enkripsi (MVP).
    * **[IMPROVED]** _Logging_ telah ditambahkan di `medical_records.py`. Perluasan _logging_ terstruktur dan komprehensif masih PENDING.
    * **[PENDING]** _Error handling_ yang lebih detail dan standar di seluruh API (lihat `implementation-plan.md` bagian "API Standards & Error Handling").
    * **[POTENTIAL REFACTOR/CLARIFICATION]** Endpoint `/api/v1/users/register` (yang hanya berinteraksi dengan blockchain) dan `/api/v1/auth/register` (yang mendaftar ke DB dan blockchain) memiliki potensi tumpang tindih fungsionalitas. Perlu diklarifikasi mana yang menjadi standar atau apakah salah satunya akan di-deprecate. Fokus utama saat ini pada `/api/v1/auth/register` untuk pendaftaran pengguna aplikasi.
    * **[INFO]** `Create Date` pada file migrasi Alembic `a1b2e4306629_create_users_table.py` masih berupa placeholder `<Tanggal Pembuatan Awal Anda>`.
    * **[SUGGESTION]** Update file `memory-bank/progress.md` untuk mencerminkan penyelesaian Step 3.2.
    * **[SUGGESTION]** Sinkronkan bagian "Status Implementasi" di `README.md` agar konsisten dengan `status-todolist-suggestions.md` dan `implementation-plan.md`.

## Next Meeting Agenda (Saran):

    * **Review Implementasi Step 3.3 (Basic Frontend Shell) - SELESAI**: Konfirmasi penyelesaian.
    * **Pembahasan Detail dan Implementasi Langkah Berikutnya**:
        * Finalisasi detail untuk langkah implementasi berikutnya (misalnya, Step 3.4 atau fitur frontend berikutnya).
        * Rencanakan komponen UI dan logika yang dibutuhkan.
        * Identifikasi API backend yang mungkin diperlukan atau dimodifikasi.
3.  **Prioritisasi Technical Debt**: Tinjau kembali daftar _technical debt_. Apakah ada yang perlu segera ditangani sebelum Fase 4?
4.  **Perencanaan Awal Step 4.1 (Simplified Consent Logic in Chaincode)**: Meskipun masih jauh, diskusi awal mengenai bagaimana mekanisme konsen sederhana akan diimplementasikan di smart contract dapat dimulai.

*(Note: This file was last updated on 2025-05-28 based on completion of Step 3.3.)*