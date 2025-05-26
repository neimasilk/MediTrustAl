# Project Status, To-Do List, and Suggestions: MediTrustAl

## Current Project Status (per 2024-05-26):
* **Project Phase:** Phase 1 - Core Backend Setup & Blockchain Foundation (MVP Focus)
* **Description:** Implementasi Step 1.3 sedang berjalan. Konfigurasi database PostgreSQL, model User dasar, dan interaksi awal dengan blockchain (registrasi ID ke contract) telah ada. Fungsi hashing password dan pembuatan JWT ada, namun endpoint registrasi dan login aplikasi lengkap belum terimplementasi.
* **Last Completed Step (Sebagian):** Step 1.2: Basic Blockchain Network Setup (Local Development) - Ganache setup, smart contract `UserRegistry` dideploy, dan service dasar untuk interaksi ada.
* **Current Step:** Step 1.3: User Identity and Basic Authentication (Application Layer) - Sebagian terimplementasi, memerlukan penyelesaian.

## Progress Update (Snapshot 2024-05-26):
1. **Database Setup** ✅ COMPLETED (dengan catatan)
   - [x] PostgreSQL 15.x installation and configuration (via Docker in `docker-compose.yml` and manual setup instructions in `README.md`).
   - [x] Database model creation (`User` model in `src/app/models/user.py`).
*Catatan: Telah diputuskan untuk menggunakan UUID untuk User.id sesuai dengan `database-schema.md` dan `implementation-plan.md`, dan ini akan diimplementasikan dalam kode.*
   - [x] Alembic migration setup (`alembic.ini`, `alembic/env.py`).
   - [x] Database connection configuration (`src/app/core/database.py`, `src/app/core/config.py`).

2. **Authentication System (Dasar Aplikasi)** 🔄 IN PROGRESS (memerlukan banyak tambahan)
   - [x] Fungsi JWT token implementation (python-jose di `src/app/core/security.py`).
   - [x] Fungsi Password hashing with bcrypt (work factor: 12 di `src/app/core/security.py` & `src/app/core/config.py`).
   - [x] Skema Pydantic dasar untuk User (`UserCreate`, `UserResponse` di `src/app/models/user.py`).
   - [ ] **Endpoint Registrasi Aplikasi Lengkap (email, username, password, role) ke PostgreSQL.** (Saat ini `/api/users/register` hanya untuk blockchain ID)
   - [ ] **Endpoint Login Aplikasi (`/api/v1/auth/login`) yang menghasilkan JWT.**
   - [ ] **Protected route middleware menggunakan JWT.**

3. **Blockchain Integration (Dasar)** ✅ COMPLETED (dengan catatan)
   - [x] Ganache setup (diasumsikan berjalan sesuai `hardhat.config.js` dan `README.md`).
   - [x] Basic smart contract deployment (`UserRegistry` via `scripts/deployUserRegistry.js`).
   - [x] Service untuk interaksi dengan `UserRegistry` contract (`blockchain_service.register_user`, `blockchain_service.get_user_role` di `src/app/core/blockchain.py`).
   - [ ] **Implementasi generasi DID sesuai format `did:meditrustal:{base58(sha256(user_id))}`.**
   - *Catatan: Penandatanganan transaksi di `blockchain.py` perlu diperbaiki untuk manajemen private key yang lebih aman.*

4. **Dokumentasi (`memory-bank`)** ✅ COMPLETED (Sangat Komprehensif)
   - [x] `README.md`, `architecture.md`, `database-schema.md`, `development-environment-notes.md`, `implementation-plan.md`, `product-design-document.md`, `proposal-draft.md`, `tech-stack.md`, `testing-strategy.md`.

## Immediate Next Steps (Prioritas untuk menyelesaikan Step 1.3):

1.  **Selesaikan Sistem Identitas & Autentikasi Aplikasi (High Priority):**
    * **Modifikasi User Model:**
        * Ubah `id` di `src/app/models/user.py` dari `Integer` menjadi `UUID` sesuai `database-schema.md` dan `implementation-plan.md`. Buat migrasi Alembic baru.
    * **Implementasi Endpoint Registrasi Aplikasi:**
        * Buat endpoint API baru (misal, `POST /api/v1/auth/register`) yang menerima data pengguna (`username`, `email`, `password`, `role`) sesuai `UserCreate` schema.
        * Simpan pengguna baru ke database PostgreSQL dengan password yang sudah di-hash.
        * (Opsional di tahap ini, bisa diintegrasikan nanti) Generate DID dan daftarkan ke blockchain jika diperlukan saat registrasi aplikasi.
    * **Implementasi Endpoint Login Aplikasi:**
        * Buat endpoint API (`POST /api/v1/auth/login`) yang menerima kredensial (`username`/`email` dan `password`).
        * Validasi kredensial terhadap data di PostgreSQL.
        * Jika valid, generate dan kembalikan JWT access token.
    * **Implementasi Middleware Proteksi Rute:**
        * Buat middleware FastAPI untuk memverifikasi JWT pada endpoint yang memerlukan autentikasi.
    * **Implementasi Generasi DID:**
        * Buat fungsi untuk menghasilkan DID sesuai format: `did:meditrustal:{base58(sha256(user_id))}`. Tentukan `user_id` yang akan digunakan (misalnya UUID dari database).
    * **Refactor Blockchain User Registration:**
        * Endpoint `/api/users/register` saat ini bisa dipertahankan atau diintegrasikan ke dalam alur registrasi aplikasi yang lebih besar, setelah pengguna aplikasi dibuat di DB. Pastikan `user_id` yang dikirim ke blockchain adalah DID yang sudah digenerate.
    * **Perbaiki Penandatanganan Transaksi Blockchain:**
        * Modifikasi `src/app/core/blockchain.py` untuk menangani private key dengan lebih aman, misalnya dengan mengambilnya dari konfigurasi (untuk development) atau menggunakan wallet/signer service.

2.  **Implementasi Pengujian Dasar (Medium Priority - setelah fungsionalitas inti Step 1.3 ada):**
    * Tulis unit test untuk layanan autentikasi (registrasi, login, pembuatan token).
    * Tulis unit test untuk layanan blockchain (registrasi user ke contract).
    * Mulai implementasi integration test untuk alur registrasi dan login.

3.  **Konsistensi Konfigurasi dan Path (Low Priority - bisa dilakukan sambil jalan):**
    * Pastikan konsistensi nama database (misal, `meditrustal` atau `meditrustal_dev`) di semua file konfigurasi.
    * Terapkan `API_V1_PREFIX` jika memang diinginkan untuk semua endpoint.

## Technical Debt & Issues (dari status sebelumnya & review baru):

1.  **Authentication & User Management:**
    * **[BARU]** Endpoint registrasi dan login aplikasi belum ada.
    * **[BARU]** Middleware proteksi rute belum ada.
    * **[BARU]** Generasi DID belum ada.
    * **[DARI SEBELUMNYA]** Perlu mekanisme refresh token.
    * **[DARI SEBELUMNYA]** Alur reset password belum dirancang.
    * **[DARI SEBELUMNYA]** Manajemen sesi perlu diimplementasikan.
    * **[DARI SEBELUMNYA]** Pertimbangan 2FA untuk masa depan.
2.  **Database:**
    * **[DARI SEBELUMNYA]** Perlu optimasi indeks (setelah ada query pattern).
    * **[DARI SEBELUMNYA]** Tambahkan database pooling (FastAPI biasanya menangani ini dengan baik, tapi bisa di-fine-tune).
    * **[DARI SEBELUMNYA]** Siapkan strategi backup.
    * **[DARI SEBELUMNYA]** Tambahkan query monitoring.
3.  **Blockchain:**
    * **[BARU]** Penandatanganan transaksi di `blockchain.py` kurang aman.
    * **[DARI SEBELUMNYA]** Optimasi gas diperlukan (setelah kontrak lebih kompleks).
    * **[DARI SEBELUMNYA]** Setup backup node (untuk production).
    * **[DARI SEBELUMNYA]** Strategi upgrade kontrak diperlukan.
    * **[DARI SEBELUMNYA]** Sistem monitoring event diperlukan.
    * **[BARU]** Kontrak `UserRegistry.sol` tidak ada dalam file yang diunggah, sehingga fungsionalitasnya tidak dapat diverifikasi sepenuhnya.
4.  **Testing:**
    * **[DARI SEBELUMNYA]** Tes E2E belum ada.
    * **[DARI SEBELUMNYA]** Tes performa diperlukan.
    * **[DARI SEBELUMNYA]** Kerangka kerja tes keamanan diperlukan.
    * **[DARI SEBELUMNYA]** Rencana load testing diperlukan.

## Next Meeting Agenda (Saran):

1.  Review progres penyelesaian Step 1.3, khususnya endpoint registrasi & login aplikasi.
2.  Diskusikan solusi untuk manajemen private key pada `blockchain.py`.
3.  Konfirmasi implementasi `User.id` sebagai UUID telah dilakukan (keputusan final: UUID).
4.  Rencanakan implementasi pengujian unit dan integrasi untuk fitur autentikasi.
5.  Tentukan prioritas untuk item-item dalam "Technical Debt & Issues".

*(Note: This file was last updated on 2024-05-26 based on codebase review.)*