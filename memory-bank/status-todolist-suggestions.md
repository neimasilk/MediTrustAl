# Project Status, To-Do List, and Suggestions: MediTrustAl

## Current Project Status (per 2025-05-27):
* **Project Phase:** Phase 1 - Core Backend Setup & Blockchain Foundation (MVP Focus)
* **Description:** Step 1.3 telah selesai diimplementasikan. Sistem identitas pengguna lengkap dengan registrasi ke database PostgreSQL, pembuatan DID, pendaftaran ke smart contract UserRegistry, login dengan JWT, dan proteksi rute telah diimplementasikan. Keamanan penandatanganan transaksi blockchain telah diperbaiki dengan menggunakan private key dari environment variable.
* **Last Completed Step:**
    * Step 1.1: Project Setup and Basic Backend Structure - Selesai.
    * Step 1.2: Basic Blockchain Network Setup (Local Development) - Selesai.
    * Step 1.3: User Identity and Basic Authentication (Application Layer) - Selesai.
* **Next Step:** Step 1.4: Medical Record Data Model and Storage (Application Layer) - PENDING.

## Progress Update (Snapshot 2025-05-27):
1. **Database Setup** ✅ COMPLETED
   - [x] PostgreSQL 15.x installation and configuration.
   - [x] Database model creation (`User` model).
   - [x] Alembic migration setup.
   - [x] Database connection configuration.

2. **Authentication System** ✅ COMPLETED
   - [x] JWT token implementation.
   - [x] Password hashing with bcrypt.
   - [x] Skema Pydantic untuk User.
   - [x] Implementasi Endpoint Registrasi Aplikasi Lengkap.
   - [x] Implementasi Endpoint Login Aplikasi.
   - [x] Implementasi Middleware Proteksi Rute menggunakan JWT.
   - [x] Implementasi Generasi DID sesuai format `did:meditrustal:{base58(sha256(user_id))}`.

3. **Blockchain Integration** ✅ COMPLETED
   - [x] Ganache setup.
   - [x] Basic smart contract deployment.
   - [x] Service untuk interaksi dengan `UserRegistry` contract.
   - [x] Perbaikan Penandatanganan Transaksi Blockchain untuk menangani private key dengan aman.
   - [x] Integrasi pemanggilan `blockchain_service.register_user` ke dalam alur registrasi aplikasi.

4. **Testing** ✅ COMPLETED
   - [x] Unit tests untuk fungsi utilitas (DID generation).
   - [x] Integration tests untuk endpoint auth (register, login).
   - [x] Integration tests untuk endpoint yang diproteksi.
   - [x] Test fixtures dan setup (SQLite in-memory database).

## Immediate Next Steps (Step 1.4):

1. **Desain Model Data Rekam Medis:**
   * Definisikan skema database untuk rekam medis.
   * Tentukan struktur data yang akan disimpan di blockchain vs database.
   * Implementasikan model SQLAlchemy dan skema Pydantic.

2. **Smart Contract untuk Rekam Medis:**
   * Desain dan implementasi smart contract `MedicalRecordRegistry`.
   * Definisikan fungsi untuk mengelola akses dan riwayat rekam medis.
   * Implementasikan mekanisme enkripsi dan dekripsi data sensitif.

3. **Endpoint API untuk Rekam Medis:**
   * Implementasi CRUD operations untuk rekam medis.
   * Integrasi dengan blockchain untuk tracking dan verifikasi.
   * Implementasi kontrol akses berbasis role (RBAC).

4. **Pengujian:**
   * Unit tests untuk model dan utilitas rekam medis.
   * Integration tests untuk endpoint rekam medis.
   * Tests untuk interaksi dengan smart contract rekam medis.

## Technical Debt & Issues:

1. **Authentication & User Management:**
   * **[COMPLETED]** ~~Endpoint registrasi dan login aplikasi belum ada.~~
   * **[COMPLETED]** ~~Middleware proteksi rute belum ada.~~
   * **[COMPLETED]** ~~Generasi DID belum ada.~~
   * **[PENDING]** Perlu mekanisme refresh token.
   * **[PENDING]** Alur reset password belum dirancang.
   * **[PENDING]** Manajemen sesi perlu diimplementasikan.
   * **[PENDING]** Pertimbangan 2FA untuk masa depan.

2. **Database:**
   * **[PENDING]** Perlu optimasi indeks.
   * **[PENDING]** Fine-tune database pooling.
   * **[PENDING]** Siapkan strategi backup.
   * **[PENDING]** Tambahkan query monitoring.

3. **Blockchain:**
   * **[COMPLETED]** ~~Penandatanganan transaksi di `blockchain.py` kurang aman.~~
   * **[PENDING]** Optimasi gas diperlukan.
   * **[PENDING]** Setup backup node.
   * **[PENDING]** Strategi upgrade kontrak.
   * **[PENDING]** Sistem monitoring event.

4. **Testing:**
   * **[COMPLETED]** ~~Unit tests untuk auth dan DID generation.~~
   * **[COMPLETED]** ~~Integration tests untuk auth endpoints.~~
   * **[PENDING]** Tes E2E.
   * **[PENDING]** Tes performa.
   * **[PENDING]** Kerangka kerja tes keamanan.
   * **[PENDING]** Load testing.

## Next Meeting Agenda:

1. Review implementasi Step 1.3 yang telah selesai.
2. Demo fitur registrasi, login, dan proteksi rute.
3. Review hasil pengujian.
4. Diskusi desain dan implementasi Step 1.4 (Medical Record).
5. Prioritisasi technical debt yang perlu diselesaikan.
6. Planning untuk sprint berikutnya.

*(Note: This file was last updated on 2025-05-27 based on completion of Step 1.3.)*