# Baby Step 4.1: Implementasi Logika Konsen Sederhana di Smart Contract dan Backend

**Tujuan:** Mengimplementasikan mekanisme dasar bagi pasien untuk memberikan izin akses rekam medis mereka kepada dokter melalui _smart contract_, dan mengintegrasikannya dengan _backend_.

**Referensi Dokumen:**
* `memory-bank/implementation-plan.md` (Phase 4, Step 4.1)
* `memory-bank/tech-stack.md`
* `blockchain/contracts/MedicalRecordRegistry.sol`
* `src/app/core/blockchain.py`
* `src/app/api/endpoints/medical_records.py`

---

## Bagian 1: Modifikasi Smart Contract (`MedicalRecordRegistry.sol`)

**Estimasi Waktu:** 3-4 jam

**Deskripsi:**
Modifikasi _smart contract_ `MedicalRecordRegistry.sol` untuk menambahkan fungsionalitas pemberian izin akses.

**Tugas:**

1.  **Definisi Struktur Data untuk Daftar Akses:**
    * Di dalam `MedicalRecordRegistry.sol`, tambahkan sebuah `mapping` untuk mencatat dokter mana saja yang diizinkan mengakses sebuah `recordHash`.
    * Pilihan: `mapping(bytes32 => mapping(address => bool)) internal recordAccessList;`
        * Kunci pertama adalah `recordHash` (hash dari rekam medis).
        * Kunci kedua adalah `address` dari dokter yang diberi akses.
        * Nilainya adalah `bool` (`true` jika diizinkan, `false` jika tidak/dicabut).

2.  **Implementasi Fungsi `grantAccess`:**
    * Buat fungsi `public` baru: `function grantAccess(bytes32 recordHash, address doctorAddress) external`.
    * **Validasi Pemilik:** Pastikan hanya pemilik rekam medis yang dapat memanggil fungsi ini.
        * Ambil `RecordMetadata` untuk `recordHash` menggunakan `recordMetadataMap[recordHash]`.
        * Verifikasi bahwa `msg.sender` (pemanggil fungsi) sama dengan `submitter` yang tersimpan di `RecordMetadata.submitter`. Jika tidak sama, `revert` dengan _custom error_ (misalnya, `NotRecordOwner(bytes32 recordHash, address caller)`).
    * **Logika Pemberian Akses:**
        * Set `recordAccessList[recordHash][doctorAddress] = true;`.
    * **Emit Event:**
        * Definisikan _event_ baru: `event AccessGranted(bytes32 indexed recordHash, address indexed ownerAddress, address indexed doctorAddress, uint256 timestamp);`
        * Emit _event_ ini: `emit AccessGranted(recordHash, msg.sender, doctorAddress, block.timestamp);`.

3.  **Implementasi Fungsi `revokeAccess` (Opsional namun Direkomendasikan):**
    * Buat fungsi `public` baru: `function revokeAccess(bytes32 recordHash, address doctorAddress) external`.
    * **Validasi Pemilik:** Sama seperti `grantAccess`.
    * **Logika Pencabutan Akses:**
        * Set `recordAccessList[recordHash][doctorAddress] = false;`.
    * **Emit Event:**
        * Definisikan _event_ baru: `event AccessRevoked(bytes32 indexed recordHash, address indexed ownerAddress, address indexed doctorAddress, uint256 timestamp);`
        * Emit _event_ ini.

4.  **Implementasi Fungsi Query Akses (untuk verifikasi):**
    * Buat fungsi `public view` baru: `function checkAccess(bytes32 recordHash, address accessorAddress) external view returns (bool)`.
    * Fungsi ini akan mengembalikan `recordAccessList[recordHash][accessorAddress]`.
    * Ini akan digunakan oleh _backend_ atau untuk pengujian guna memverifikasi status akses.

5.  **Kompilasi dan Uji Lokal Smart Contract:**
    * Gunakan Hardhat: `npx hardhat compile`.
    * Tulis atau perbarui tes unit di `blockchain/test/MedicalRecordRegistry.test.js` untuk mencakup:
        * Pemberian akses berhasil oleh pemilik.
        * Pemberian akses gagal jika bukan pemilik.
        * Pencabutan akses berhasil oleh pemilik (jika `revokeAccess` diimplementasikan).
        * Pengecekan status akses melalui `checkAccess`.
        * Verifikasi emisi _event_ `AccessGranted` dan `AccessRevoked`.
    * Jalankan tes: `npx hardhat test`.

6.  **Deployment Ulang Smart Contract ke Ganache (Lokal):**
    * Update skrip deployment di `scripts/deployMedicalRecordRegistry.js` jika diperlukan.
    * Jalankan: `npx hardhat run scripts/deployMedicalRecordRegistry.js --network ganache`.
    * Pastikan file ABI dan alamat kontrak yang baru di `blockchain/build/deployments/` telah diperbarui dan akan dibaca oleh `src/app/core/config.py`.

**Kriteria Keberhasilan Bagian 1:**
* _Smart contract_ berhasil dikompilasi tanpa _error_.
* Semua tes unit _smart contract_ untuk fungsionalitas konsen baru berhasil (lolos).
* _Smart contract_ berhasil di-deploy ulang ke Ganache, dan file ABI/alamat ter-update.

---

## Bagian 2: Update Backend Service (`BlockchainService`)

**Estimasi Waktu:** 2-3 jam

**Deskripsi:**
Perbarui `src/app/core/blockchain.py` untuk berinteraksi dengan fungsi-fungsi konsen baru di _smart contract_.

**Tugas:**

1.  **Tambahkan Metode `grant_record_access`:**
    * Buat metode `async def grant_record_access(self, record_hash_hex: str, doctor_address: str) -> dict:`.
    * Metode ini harus:
        * Mengonversi `record_hash_hex` menjadi `bytes32`.
        * Memvalidasi `doctor_address` (format alamat Ethereum).
        * Membangun transaksi untuk memanggil fungsi `grantAccess` pada `medical_record_registry_contract`.
        * Menggunakan `self.account` sebagai `from` dan `self.private_key` untuk menandatangani.
        * Mengirim transaksi dan menunggu _receipt_.
        * Mengembalikan dictionary yang berisi status sukses/gagal, `transaction_hash`, dan pesan _error_ jika ada.

2.  **Tambahkan Metode `revoke_record_access` (Jika Diimplementasikan di Smart Contract):**
    * Mirip dengan `grant_record_access`, tetapi untuk fungsi `revokeAccess`.

3.  **Tambahkan Metode `check_record_access`:**
    * Buat metode `async def check_record_access(self, record_hash_hex: str, accessor_address: str) -> dict:`.
    * Metode ini akan memanggil fungsi `checkAccess` (fungsi `view`) pada _smart contract_.
    * Mengembalikan dictionary yang berisi status sukses/gagal, dan `bool` status akses.

4.  **Update Unit Tests untuk `BlockchainService`:**
    * Di `tests/unit/core/test_blockchain_service.py`.
    * Tambahkan tes baru untuk metode `grant_record_access`, `revoke_record_access` (jika ada), dan `check_record_access`.
    * Gunakan `MagicMock` atau `AsyncMock` untuk mem-mock interaksi `web3.eth.contract.functions` dan `web3.eth.send_raw_transaction`, dll.
    * Pastikan kasus sukses dan gagal (misalnya, _revert_ dari _smart contract_) ditangani.

**Kriteria Keberhasilan Bagian 2:**
* Metode-metode baru di `BlockchainService` diimplementasikan.
* Semua tes unit baru untuk `BlockchainService` berhasil.

---

## Bagian 3: Implementasi Endpoint API Backend Baru

**Estimasi Waktu:** 2-3 jam

**Deskripsi:**
Buat endpoint API di `src/app/api/endpoints/medical_records.py` untuk memungkinkan pasien memberikan akses.

**Tugas:**

1.  **Definikan Model Pydantic (jika perlu):**
    * Untuk _request body_ endpoint `grant-access`, mungkin diperlukan model Pydantic sederhana jika inputnya lebih dari sekadar alamat dokter, misalnya:
        ```python
        # Di src/app/models/medical_record.py atau file skema baru
        class GrantAccessRequest(BaseModel):
            doctor_address: str # Sebaiknya divalidasi sebagai alamat Ethereum
        ```

2.  **Implementasi Endpoint `POST /api/v1/medical-records/{record_id}/grant-access`:**
    * Router: `medical_records.router`.
    * Parameter Path: `record_id: uuid.UUID`.
    * Request Body: `access_request: GrantAccessRequest` (gunakan model Pydantic di atas).
    * Dependencies: `db: Session = Depends(get_db)`, `current_user: User = Depends(get_current_active_user)`, `blockchain_service: BlockchainService = Depends(get_blockchain_service)`.
    * **Logika:**
        1.  Ambil `MedicalRecord` dari database menggunakan `record_id`. Jika tidak ditemukan, kembalikan HTTP 404.
        2.  **Validasi Kepemilikan:** Pastikan `current_user.id` sama dengan `db_record.patient_id`. Jika tidak, kembalikan HTTP 403 (Forbidden).
        3.  Ambil `data_hash` dari `db_record.data_hash`.
        4.  **Validasi `doctor_address`:** Pastikan alamat dokter valid (misalnya, menggunakan `Web3.is_address`).
        5.  Panggil `await blockchain_service.grant_record_access(record_hash_hex=data_hash, doctor_address=access_request.doctor_address)`.
        6.  Jika pemanggilan ke `blockchain_service` gagal, kembalikan HTTP 500 atau 400 sesuai _error_ dari _service_.
        7.  Jika berhasil, kembalikan respons sukses (misalnya, HTTP 200 dengan pesan).

3.  **Implementasi Endpoint `POST /api/v1/medical-records/{record_id}/revoke-access` (Jika Diimplementasikan):**
    * Mirip dengan `grant-access`.

4.  **Update Tes Integrasi API:**
    * Di `tests/integration/api/test_api_medical_records.py`.
    * Tambahkan tes baru untuk endpoint `/grant-access` (dan `/revoke-access` jika ada).
        * Kasus sukses: pasien memberikan akses ke dokter.
        * Kasus gagal: pengguna yang bukan pemilik rekam medis mencoba memberikan akses.
        * Kasus gagal: `record_id` tidak valid.
        * Kasus gagal: `doctor_address` tidak valid.
        * Kasus gagal: _error_ dari `BlockchainService` (misalnya, _smart contract revert_ karena dokter sudah diberi akses, atau _gas_ habis).
    * Mock `BlockchainService.grant_record_access` (dan `revoke_record_access`) untuk mengontrol responsnya selama tes integrasi API.

**Kriteria Keberhasilan Bagian 3:**
* Endpoint API baru berhasil diimplementasikan dan tervalidasi melalui Swagger/OpenAPI.
* Semua tes integrasi untuk endpoint baru berhasil.
* Pasien yang terautentikasi dapat memberikan izin akses rekam medisnya kepada alamat dokter tertentu.

---

## Bagian 4: Modifikasi Endpoint Pengambilan Data Rekam Medis (Jika Perlu Sesuai Desain Akses)

**Estimasi Waktu:** 1-2 jam (tergantung kompleksitas)

**Deskripsi:**
Sesuai `implementation-plan.md`, fungsi *query* rekam medis di *chaincode* harus memeriksa akses. Jika ini diimplementasikan sepenuhnya *on-chain* dan `getRecordMetadata` diubah, atau fungsi baru seperti `getRecordMetadataForDoctor` dibuat di *smart contract*, maka `BlockchainService` dan endpoint API yang relevan perlu disesuaikan.

**Alternatif MVP:** Jika query *on-chain* dengan pemeriksaan akses terlalu rumit untuk MVP *smart contract* saat ini, maka *backend* API `GET /api/v1/medical-records/{record_id}` yang sudah ada (yang mengambil data dari DB) perlu dimodifikasi untuk:
1.  Jika pemanggil adalah dokter (cek `current_user.role`), maka sebelum mengambil data dari DB:
2.  Panggil `blockchain_service.check_record_access(data_hash, current_user.blockchain_address)` (asumsi `blockchain_address` dokter disimpan di model `User`).
3.  Jika tidak diizinkan, kembalikan HTTP 403.

**Tugas (Pilih salah satu pendekatan berdasarkan keputusan desain akses):**

* **Pendekatan A (Akses dicek di Smart Contract saat Query Metadata):**
    1.  Update `BlockchainService` untuk memanggil fungsi _smart contract_ baru/yang dimodifikasi (misalnya, `get_record_metadata_for_doctor`).
    2.  Update endpoint API `GET /api/v1/medical-records/{record_id}` atau buat endpoint baru khusus dokter yang menggunakan metode _service_ baru ini untuk mendapatkan metadata dari _blockchain_ (jika metadata juga disajikan melalui _blockchain_).
    3.  Logika pengambilan data terenkripsi dari DB dan dekripsi tetap sama, namun didahului oleh pemeriksaan izin dari _blockchain_.

* **Pendekatan B (Akses dicek di Backend menggunakan `checkAccess` dari Smart Contract):**
    1.  Modifikasi endpoint `GET /api/v1/medical-records/{record_id}` di `src/app/api/endpoints/medical_records.py`.
    2.  Dalam endpoint tersebut, jika `current_user.role == UserRole.DOCTOR`:
        * Ambil `db_record` seperti biasa.
        * Panggil `await blockchain_service.check_record_access(record_hash_hex=db_record.data_hash, accessor_address=current_user.blockchain_address)`. (Pastikan `current_user` memiliki atribut `blockchain_address` yang valid atau cara lain untuk mendapatkan alamat Ethereum dokter).
        * Jika `check_record_access` mengembalikan `False` atau gagal, kembalikan HTTP 403.
    3.  Jika `current_user.id == db_record.patient_id` (pemilik), lanjutkan seperti biasa.
    4.  Update tes integrasi untuk endpoint `GET /api/v1/medical-records/{record_id}` untuk skenario dokter dengan dan tanpa akses.

**Kriteria Keberhasilan Bagian 4:**
* Endpoint pengambilan data rekam medis (detail) berhasil menerapkan logika pemeriksaan izin akses.
* Dokter hanya dapat mengambil detail rekam medis jika telah diberi izin oleh pasien melalui _smart contract_.
* Pasien selalu dapat mengambil detail rekam medisnya sendiri.
* Tes integrasi yang relevan berhasil.

---

**Definisi Selesai (Definition of Done) untuk Baby Step 4.1:**
* Semua tugas di atas telah diselesaikan.
* Semua tes unit dan integrasi baru (backend dan _smart contract_) berhasil (lolos).
* Dokumentasi kode (komentar, docstring) telah diperbarui untuk kode baru/yang dimodifikasi.
* Dokumentasi OpenAPI (Swagger) telah diperbarui dan akurat untuk endpoint API baru/yang dimodifikasi.
* File `memory-bank/progress.md` telah diperbarui untuk mencerminkan penyelesaian Step 4.1.
* File `README.md` telah diperbarui jika ada perubahan signifikan pada cara menjalankan atau menguji fitur baru.
* Pengujian manual singkat untuk memverifikasi alur pemberian akses dari sisi API telah dilakukan (misalnya, menggunakan Postman/curl).