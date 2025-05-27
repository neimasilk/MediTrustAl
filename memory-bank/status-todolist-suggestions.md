# Project Status, To-Do List, and Suggestions: MediTrustAl

## Current Project Status (per 2025-05-27):
* **Project Phase:** Menuju Penyelesaian MVP - Implementasi Fitur Lanjutan.
* **Description:**
    * Step 1.1 hingga Step 4.1 (Simplified Consent Logic in Smart Contract and Backend) telah selesai diimplementasikan dan semua tes yang ada telah lolos.
    * Fondasi backend, interaksi blockchain dasar, layanan placeholder AI/NLP, dan shell frontend dasar untuk portal pasien telah terbangun.
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
    * Step 4.1: Simplified Consent Logic in Smart Contract and Backend - ✅ SELESAI.
* **Next Major Steps (sesuai `implementation-plan.md` yang akan diperbarui):**
    * Step 4.2: Implementasi Fitur Peningkatan Pencatatan Audit Akses Data untuk Kepatuhan PIPL.
    * Step 5.1: Implementasi Antarmuka Pengguna (UI) Frontend untuk Manajemen Persetujuan Pasien.
    * Step 5.2: Integrasi Nyata dengan API NLP DeepSeek (Menggantikan Placeholder).

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
    * [x] Setup Ganache.
    * [x] _Smart contract_ `UserRegistry` dan `MedicalRecordRegistry` (termasuk fungsi `grantAccess`, `revokeAccess`, `checkAccess`) telah di-deploy.
    * [x] Service (`BlockchainService` di `blockchain.py`) untuk interaksi dengan kontrak `UserRegistry` dan `MedicalRecordRegistry`.
    * [x] Penandatanganan Transaksi Blockchain menggunakan _private key_ dari _environment variable_.
    * [x] Integrasi pemanggilan `blockchain_service.register_user` ke dalam alur registrasi aplikasi.
    * [x] Integrasi pemanggilan `blockchain_service.add_medical_record_hash` ke dalam alur pembuatan rekam medis.
    * [x] Implementasi metode `get_record_hashes_for_patient`, `grant_record_access`, `revoke_record_access`, `check_record_access` di `BlockchainService` dan integrasinya dengan endpoint API terkait.
4.  **Medical Record Management (MVP Core)** ✅ SELESAI
    * [x] Model SQLAlchemy `MedicalRecord` dan skema Pydantic terkait.
    * [x] Fungsi CRUD untuk `MedicalRecord`.
    * [x] API Endpoint `POST /medical-records` untuk membuat rekam medis baru.
    * [x] API Endpoint `GET /medical-records/patient/me` untuk mengambil daftar rekam medis.
    * [x] API Endpoint `GET /medical-records/{record_id}` untuk mengambil detail rekam medis (termasuk pemeriksaan akses dokter).
    * [x] Endpoint untuk `grant-access`, `revoke-access`, `check-access`.
    * [x] Implementasi enkripsi AES-GCM untuk `raw_data` dan SHA-256 untuk `data_hash`.
5.  **Testing** ✅ SELESAI (untuk fitur hingga Step 4.1)
    * [x] Unit tes untuk utilitas (enkripsi, generasi DID).
    * [x] Unit tes untuk CRUD (`medical_record`, `user`).
    * [x] Unit tes untuk `BlockchainService`.
    * [x] Tes integrasi untuk _endpoint auth_ (register, login).
    * [x] Tes integrasi untuk _endpoint_ yang diproteksi (`/users/me`).
    * [x] Tes integrasi untuk _endpoint_ API rekam medis (termasuk grant/revoke).
    * [x] Tes integrasi untuk _endpoint_ API NLP & AI placeholder.
    * [x] Pengaturan _test fixtures_ dan _mocking_.
    * [x] Tes _smart contract_ `MedicalRecordRegistry.test.js`.
    * [x] Dokumentasi kode (komentar) dan `README.md` (catatan developer) telah diperbarui.
    * [x] Tes manual frontend dasar (`petunjuk-manual-test.md`) untuk login dan dashboard telah dilakukan dan berhasil.
6.  **NLP Service (Placeholder - Step 3.1)** ✅ SELESAI
    * [x] Implementasi Placeholder NLP Service (`nlp_service.py`).
    * [x] Implementasi API Endpoint `POST /api/v1/nlp/extract-entities` (`nlp.py`).
    * [x] Penambahan Pydantic model untuk request/response NLP.
    * [x] Registrasi router NLP di `main.py`.
    * [x] Tes unit untuk `nlp_service.py`.
    * [x] Tes integrasi untuk API endpoint NLP.
7.  **AI Predictive Service (Placeholder - Step 3.2)** ✅ SELESAI
    * [x] Implementasi Placeholder AI Service (`ai_service.py`).
    * [x] Implementasi API Endpoint `POST /api/v1/ai/predict-risk` (`ai.py`).
    * [x] Penambahan Pydantic model untuk request/response AI Prediction.
    * [x] Registrasi router AI di `main.py`.
    * [x] Tes unit untuk `ai_service.py`.
    * [x] Tes integrasi untuk API endpoint AI.
8.  **Basic Frontend Shell (Patient Portal - Step 3.3)** ✅ SELESAI
    * [x] Setup proyek frontend dasar (React.js dengan Vite).
    * [x] Implementasi halaman login (UI, service, panggil API, simpan token).
    * [x] Pengaturan state management (Redux Toolkit untuk auth).
    * [x] Implementasi protected routes.
    * [x] Implementasi halaman dashboard dasar (logout, panggil API untuk rekam medis, tampilkan data).
    * [x] Konfigurasi CORS di backend.
    * [x] Pembuatan panduan tes manual (`petunjuk-manual-test.md`) awal.

## Immediate Next Steps (Baby-Step To-Do List - menuju penyelesaian 3 poin utama):

1.  **Definisi dan Implementasi Step 4.2: Peningkatan Pencatatan Audit Akses Data untuk Kepatuhan PIPL**
    * Detailkan dan implementasikan backend logging untuk setiap akses rekam medis dan modifikasi consent.
    * (Opsional untuk MVP awal) Buat UI sederhana di frontend bagi pasien untuk melihat riwayat akses.
2.  **Implementasi Step 5.1: Antarmuka Pengguna (UI) Frontend untuk Manajemen Persetujuan Pasien**
    * Rancang dan implementasikan UI di Portal Pasien yang memungkinkan pasien untuk memberikan (`grant`) dan mencabut (`revoke`) akses dokter ke rekam medis mereka.
3.  **Implementasi Step 5.2: Integrasi Nyata dengan API NLP DeepSeek**
    * Gantikan layanan NLP placeholder dengan panggilan aktual ke DeepSeek API.
    * Tangani API key, format request/response, dan error handling.

## Technical Debt & Future Considerations:

1.  **Authentication & User Management:**
    * **[PENDING]** Mekanisme _refresh token_.
    * **[PENDING]** Alur reset password.
    * **[PENDING]** Manajemen sesi yang lebih robas.
2.  **Database:**
    * **[PENDING]** Optimasi indeks lebih lanjut setelah _query patterns_ lebih jelas.
    * **[PENDING]** Fine-tune _database pooling_ untuk produksi.
    * **[PENDING]** Strategi _backup & restore_ yang matang.
3.  **Blockchain:**
    * **[PENDING]** Optimasi gas untuk fungsi _smart contract_.
    * **[PENDING]** Strategi _upgrade smart contract_ yang lebih matang.
    * **[PENDING]** Sistem _monitoring event_ dari _smart contract_.
4.  **Testing:**
    * **[PENDING]** Pengujian manual komprehensif untuk fitur-fitur baru (Audit Log, UI Consent, Integrasi DeepSeek).
    * **[PENDING]** Tes E2E (End-to-End) setelah _frontend_ lebih matang.
    * **[PENDING]** Tes performa (load testing) untuk API.
5.  **Dokumentasi & Lain-lain:**
    * **[MITIGATED FOR MVP]** Pengelolaan Kunci Enkripsi: Penggunaan JWT _secret_ untuk kunci enkripsi (MVP). Perlu solusi lebih baik pasca-MVP.
    * **[IMPROVED, BUT EXPANSION PENDING]** _Logging_ telah ditambahkan di `medical_records.py`. Perluasan _logging_ terstruktur dan komprehensif masih PENDING.
    * **[PENDING]** _Error handling_ yang lebih detail dan standar di seluruh API (sesuai definisi di `implementation-plan.md` bagian "API Standards & Error Handling").
    * **[POTENTIAL REFACTOR/CLARIFICATION]** Endpoint `/api/v1/users/register` vs `/api/v1/auth/register`. Fokus utama saat ini pada `/api/v1/auth/register`.
    * **[INFO/MINOR]** `Create Date` pada file migrasi Alembic `a1b2e4306629_create_users_table.py` masih berupa placeholder.
    * **[PENDING]** Sinkronkan bagian "Status Implementasi" di `README.md`.

## Next Meeting Agenda (Saran):

* **Review Rencana Implementasi Step 4.2, 5.1, dan 5.2**: Pastikan semua tim memahami detail dan dependensi.
* **Pembagian Tugas**: Alokasikan tugas untuk masing-masing baby-step.
* **Diskusi Ambiguitas**: Jika ada ambiguitas dalam `baby-step.md` yang akan dibuat, diskusikan dan klarifikasi.
* **Prioritisasi Technical Debt**: Identifikasi apakah ada item *technical debt* yang *harus* ditangani sebelum atau selama implementasi langkah-langkah berikutnya.

*(Note: This file was last updated on 2025-05-27 based on completion of Step 4.1 and plans for next features.)*