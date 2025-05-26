# Baby Steps: Implementasi Step 2.3 - Basic Patient Data Retrieval

**Tujuan Utama:** Memungkinkan pasien yang terautentikasi untuk mengambil daftar metadata rekam medis mereka, dengan informasi yang divalidasi atau berasal dari blockchain, dan kemudian menggunakan ID rekam medis untuk mengambil detail data terenkripsi dari database.

**Referensi Utama:**
* `implementation-plan.md` (Step 2.3)
* `memory-bank/database-schema.md` (untuk tabel `medical_records`)
* `blockchain/contracts/MedicalRecordRegistry.sol` (perlu dimodifikasi)
* `src/app/core/blockchain.py`
* `src/app/api/endpoints/medical_records.py`
* `src/app/models/medical_record.py`

---

## Tahap 1: Modifikasi Smart Contract `MedicalRecordRegistry.sol`

### Baby Step 1.1: Tambah Struktur Data untuk Query per Pasien
* **Tugas:** Di `MedicalRecordRegistry.sol`, tambahkan struktur data untuk menyimpan daftar `recordHash` yang dimiliki oleh setiap `patientDid`.
* **Detail:**
    * Deklarasikan sebuah _mapping_ baru: `mapping(string => bytes32[]) private patientRecordHashes;`
        * `string` adalah `patientDid`.
        * `bytes32[]` adalah _array_ dari `recordHash`.
* **File:** `blockchain/contracts/MedicalRecordRegistry.sol`
* **Verifikasi:** Kode berhasil dikompilasi (`npx hardhat compile`).

### Baby Step 1.2: Update Fungsi `addRecord` untuk Mengisi Struktur Data Baru
* **Tugas:** Modifikasi fungsi `addRecord` di `MedicalRecordRegistry.sol` agar ketika sebuah _record_ baru ditambahkan, `recordHash`-nya juga ditambahkan ke _array_ `patientRecordHashes[patientDid]`.
* **Detail:**
    * Di dalam fungsi `addRecord(bytes32 recordHash, string calldata patientDid, string calldata recordType)`, setelah validasi dan sebelum emit event, tambahkan baris: `patientRecordHashes[patientDid].push(recordHash);`
* **File:** `blockchain/contracts/MedicalRecordRegistry.sol`
* **Verifikasi:** Kode berhasil dikompilasi. Logika penambahan ke _array_ terlihat benar.

### Baby Step 1.3: Implementasi Fungsi `getRecordHashesByPatient`
* **Tugas:** Buat fungsi _view_ baru `getRecordHashesByPatient` di `MedicalRecordRegistry.sol`.
* **Detail:**
    * Definisi fungsi: `function getRecordHashesByPatient(string calldata patientDid) external view returns (bytes32[] memory)`
    * Isi fungsi: `return patientRecordHashes[patientDid];`
* **File:** `blockchain/contracts/MedicalRecordRegistry.sol`
* **Verifikasi:** Kode berhasil dikompilasi.

### Baby Step 1.4: Tes Smart Contract Baru
* **Tugas:** Update `blockchain/test/MedicalRecordRegistry.test.js` untuk menguji fungsionalitas baru.
* **Detail:**
    * Tambahkan _test case_ baru:
        * Setelah beberapa `addRecord` untuk `patientDid` yang sama, panggil `getRecordHashesByPatient` dan verifikasi bahwa _array_ `recordHash` yang dikembalikan sesuai dengan yang diharapkan.
        * Panggil `getRecordHashesByPatient` untuk `patientDid` yang belum memiliki _record_, verifikasi _array_ kosong dikembalikan.
        * Panggil `getRecordHashesByPatient` untuk beberapa pasien berbeda dan verifikasi hasilnya benar untuk masing-masing.
* **File:** `blockchain/test/MedicalRecordRegistry.test.js`
* **Verifikasi:** Semua tes _smart contract_ lolos (`npx hardhat test`).

### Baby Step 1.5: Deploy Ulang Smart Contract (Lokal)
* **Tugas:** Jalankan skrip deployment untuk `MedicalRecordRegistry` ke Ganache.
* **Detail:**
    * Jalankan: `npx hardhat run scripts/deployMedicalRecordRegistry.js --network ganache`
    * Pastikan Ganache berjalan.
    * Verifikasi bahwa file ABI dan alamat kontrak di `blockchain/build/deployments/` telah diperbarui.
* **Verifikasi:** Skrip deployment berjalan sukses, alamat kontrak baru tercatat. Aplikasi backend (jika sudah berjalan) akan mengambil ABI/alamat baru saat di-restart.

---

## Tahap 2: Modifikasi Backend FastAPI

### Baby Step 2.1: Update `BlockchainService`
* **Tugas:** Tambahkan metode baru di `BlockchainService` untuk memanggil `getRecordHashesByPatient`.
* **Detail:**
    * Buat metode `async def get_record_hashes_for_patient(self, patient_did: str) -> dict:` di `src/app/core/blockchain.py`.
    * Metode ini harus:
        * Memeriksa apakah `medical_record_registry_contract` sudah diinisialisasi.
        * Memanggil `self.medical_record_registry_contract.functions.getRecordHashesByPatient(patient_did).call()`.
        * Mengembalikan dictionary seperti: `{"success": True, "data": {"hashes": [...]}}` atau `{"success": False, "error": "..."}`.
        * Pastikan konversi `bytes32` dari Solidity ke _string hex_ di Python jika perlu.
* **File:** `src/app/core/blockchain.py`
* **Verifikasi:** Metode baru ada dan logikanya tampak benar.

### Baby Step 2.2: Unit Tes untuk Metode Baru `BlockchainService`
* **Tugas:** Tambahkan unit tes untuk `get_record_hashes_for_patient`.
* **Detail:**
    * Di `tests/unit/core/test_blockchain_service.py`.
    * Mock `medical_record_registry_contract.functions.getRecordHashesByPatient().call()` untuk mengembalikan:
        * Contoh _array_ `bytes32` (yang perlu dikonversi ke _hex string_ jika layanan melakukannya).
        * _Array_ kosong.
        * Membangkitkan _exception_.
    * Verifikasi bahwa output dari `get_record_hashes_for_patient` sesuai.
* **File:** `tests/unit/core/test_blockchain_service.py`
* **Verifikasi:** Unit tes baru lolos.

### Baby Step 2.3: Modifikasi Endpoint `GET /medical-records/patient/me`
* **Tugas:** Ubah logika _endpoint_ `get_my_medical_records` di `src/app/api/endpoints/medical_records.py`.
* **Detail:**
    1.  Dapatkan `current_user.did`.
    2.  Panggil `blockchain_service.get_record_hashes_for_patient(current_user.did)`.
    3.  Jika gagal atau tidak ada _hash_, kembalikan _list_ kosong atau _error_ yang sesuai.
    4.  Jika berhasil, untuk setiap `recordHashHex` yang diterima dari _blockchain_:
        * Cari di tabel `medical_records` PostgreSQL menggunakan `db.query(MedicalRecord).filter(MedicalRecord.data_hash == recordHashHex, MedicalRecord.patient_id == current_user.id).first()`. Filter juga dengan `patient_id` untuk keamanan tambahan.
        * Jika _record_ DB ditemukan, tambahkan ke daftar hasil (format sebagai `MedicalRecordResponse`).
        * Jika _record_ DB tidak ditemukan untuk `recordHashHex` tertentu (konsistensi data?), log peringatan dan lewati.
    5.  Terapkan _pagination_ (`skip`, `limit`) pada daftar hasil akhir *setelah* semua data dikumpulkan dan difilter.
    6.  Kembalikan daftar `MedicalRecordResponse`.
* **Pertimbangan:**
    * Respons `MedicalRecordResponse` saat ini sudah cukup (`id`, `patient_id`, `record_type`, `record_metadata`, `blockchain_record_id`, `data_hash`, `created_at`, `updated_at`). Pastikan field-field ini diisi dengan benar. `timestamp` dari _blockchain_ bisa dibandingkan/digunakan untuk `updated_at` jika relevan, atau `created_at` dari DB tetap digunakan. Untuk MVP, `created_at` dari DB cukup.
* **File:** `src/app/api/endpoints/medical_records.py`
* **Verifikasi:** Logika _endpoint_ diperbarui.

### Baby Step 2.4: Update Skema Pydantic (Jika Perlu)
* **Tugas:** Tinjau `MedicalRecordResponse` di `src/app/models/medical_record.py`.
* **Detail:**
    * Untuk saat ini, asumsikan `MedicalRecordResponse` sudah memadai. Tidak ada perubahan yang diperlukan kecuali jika diputuskan bahwa _timestamp_ dari _blockchain_ harus secara eksplisit dimasukkan dan berbeda dari `created_at`/`updated_at` DB.
* **File:** `src/app/models/medical_record.py`
* **Verifikasi:** Tidak ada perubahan, atau perubahan minimal jika ada.

---

## Tahap 3: Pengujian Integrasi Backend

### Baby Step 3.1: Update Test Fixture untuk `MedicalRecordRegistry`
* **Tugas:** Di `tests/conftest.py`, `authenticated_patient_token` fixture mungkin perlu diperbarui atau fixture baru dibuat jika `MedicalRecordRegistry` sekarang aktif digunakan oleh _endpoint_ yang diuji.
* **Detail:**
    * Mock untuk `blockchain_service.get_record_hashes_for_patient` perlu ditambahkan ke `client` fixture di `conftest.py`, serupa dengan `mock_register_user` dan `mock_add_medical_record_hash`.
    * Pastikan `mock_blockchain_service_instance` di `test_api_medical_records.py` juga menyediakan mock untuk `get_record_hashes_for_patient`.
* **File:** `tests/conftest.py` (jika perlu modifikasi global), `tests/integration/api/test_api_medical_records.py` (untuk mock spesifik tes).

### Baby Step 3.2: Tes Integrasi untuk `GET /medical-records/patient/me`
* **Tugas:** Tambahkan/modifikasi tes integrasi di `tests/integration/api/test_api_medical_records.py` untuk _endpoint_ `GET /medical-records/patient/me`.
* **Detail:**
    * **Skenario 1: Pasien memiliki beberapa _record_ di _blockchain_ dan DB:**
        * Setup: Buat beberapa _record_ di DB untuk pasien uji. Mock `blockchain_service.get_record_hashes_for_patient` untuk mengembalikan `data_hash` yang sesuai.
        * Aksi: Panggil _endpoint_.
        * Assert: Respons 200 OK. Daftar _record_ yang dikembalikan cocok dengan data gabungan yang diharapkan.
    * **Skenario 2: Pasien memiliki _record_ di _blockchain_, tapi tidak ada yang cocok di DB:**
        * Setup: Mock `blockchain_service.get_record_hashes_for_patient` untuk mengembalikan beberapa `data_hash`. Pastikan tidak ada _record_ di DB yang cocok.
        * Aksi: Panggil _endpoint_.
        * Assert: Respons 200 OK. Daftar _record_ kosong. (Atau log peringatan di backend).
    * **Skenario 3: Pasien tidak memiliki _record_ di _blockchain_:**
        * Setup: Mock `blockchain_service.get_record_hashes_for_patient` untuk mengembalikan _list_ kosong.
        * Aksi: Panggil _endpoint_.
        * Assert: Respons 200 OK. Daftar _record_ kosong.
    * **Skenario 4: Error saat memanggil _blockchain_:**
        * Setup: Mock `blockchain_service.get_record_hashes_for_patient` untuk mengembalikan `{"success": False, "error": "Blockchain down"}`.
        * Aksi: Panggil _endpoint_.
        * Assert: Respons status error yang sesuai (misalnya, 503 Service Unavailable atau 500 Internal Server Error).
    * **Skenario 5: Otorisasi:** Pastikan pasien lain tidak bisa mengakses _endpoint_ ini untuk data pasien yang sedang login. (Ini seharusnya sudah dicakup oleh `get_current_active_user` dan filter `patient_id` di query).
* **File:** `tests/integration/api/test_api_medical_records.py`
* **Verifikasi:** Semua tes integrasi baru/modifikasi lolos.

---

## Tahap 4: Verifikasi Endpoint `GET /medical-records/{record_id}`

### Baby Step 4.1: Tinjau Ulang dan Pastikan Alur
* **Tugas:** Pastikan _endpoint_ `GET /medical-records/{record_id}` yang sudah ada tetap berfungsi dengan benar dan alurnya sesuai dengan rencana ("menggunakan _off-chain reference_ yang diperoleh dari _blockchain record_").
* **Detail:**
    * Alur yang diharapkan:
        1.  _Frontend_ (atau _client_ API lain) memanggil `GET /medical-records/patient/me` (yang diimplementasikan di Tahap 2 & 3 di atas).
        2.  Respons dari _endpoint_ tersebut akan berisi daftar _metadata_ rekam medis, termasuk `id` (UUID dari PostgreSQL) untuk setiap _record_.
        3.  _Frontend_ menggunakan `id` (UUID) ini untuk memanggil `GET /medical-records/{record_id}` untuk mendapatkan detail lengkap, termasuk `raw_data` yang didekripsi.
    * Tidak ada perubahan kode yang diperlukan untuk _endpoint_ ini jika alur di atas sudah benar.
* **File:** `src/app/api/endpoints/medical_records.py`
* **Verifikasi:** Alur logis dan kode _endpoint_ sudah mendukung ini. Tes integrasi yang ada untuk _endpoint_ ini (`test_get_medical_record_detail_success`, dll.) harus tetap lolos.

---

## Tahap 5: Dokumentasi (Singkat)

### Baby Step 5.1: Update Komentar Kode
* **Tugas:** Tambahkan atau perbarui komentar di kode yang dimodifikasi (`MedicalRecordRegistry.sol`, `blockchain.py`, `medical_records.py`) untuk menjelaskan logika baru atau perubahan.
* **Verifikasi:** Komentar jelas dan membantu pemahaman.

### Baby Step 5.2: Update README (Jika Perlu)
* **Tugas:** Jika ada perubahan signifikan pada cara kerja API atau interaksi _smart contract_ yang perlu diketahui pengguna/developer lain, update `README.md` atau dokumentasi API lainnya.
* **Detail:** Untuk perubahan ini, mungkin belum perlu update besar di `README.md` kecuali ada perubahan pada proses _setup_ atau _deployment_ kontrak.
* **Verifikasi:** Dokumentasi relevan sudah diperbarui.

---

Dengan menyelesaikan semua _baby step_ ini, Step 2.3 dari `implementation-plan.md` akan selesai.