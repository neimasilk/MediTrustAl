# Baby Steps: Penyelesaian Step 2.3 - Integrasi Penuh Pengambilan Data Rekam Medis Pasien

**Tujuan Utama:** Memastikan backend dapat berinteraksi dengan _smart contract_ `MedicalRecordRegistry` yang sudah di-deploy secara "live" (di Ganache) untuk mengambil daftar hash rekam medis pasien, dan kemudian mengambil data lengkap dari database.

**Prasyarat:**
* Developer utama telah berhasil men-deploy versi terbaru dari `MedicalRecordRegistry.sol` (yang menyertakan fungsi `getRecordHashesByPatient` dan `mapping patientRecordHashes`) ke jaringan Ganache lokal.
* Alamat kontrak dan ABI dari `MedicalRecordRegistry` yang baru telah disimpan dengan benar di `blockchain/build/deployments/MedicalRecordRegistry-address.json` dan `MedicalRecordRegistry-abi.json`.
* Layanan backend FastAPI dapat dijalankan.
* Database PostgreSQL berjalan dan termigrasi.

---

### **Baby Step 2.3.1: Verifikasi Konfigurasi Backend untuk Smart Contract Baru**

* **Tujuan:** Memastikan aplikasi FastAPI memuat alamat dan ABI yang benar untuk _smart contract_ `MedicalRecordRegistry` yang baru di-deploy.
* **Instruksi:**
    1.  Hentikan server FastAPI jika sedang berjalan.
    2.  Hapus file `.env` jika ada untuk memastikan variabel lingkungan tidak meng-override konfigurasi dari file JSON (atau pastikan `.env` tidak berisi `MEDICAL_RECORD_REGISTRY_ADDRESS` dan `MEDICAL_RECORD_REGISTRY_ABI` yang lama).
    3.  Jalankan kembali server FastAPI:
        ```bash
        cd src
        uvicorn app.main:app --reload --port 8000
        ```
    4.  Periksa log output server FastAPI saat startup. Cari pesan yang mengindikasikan bahwa "Medical Record Registry contract ABI and address loaded successfully." dari `src/app/core/config.py`.
        * Pastikan alamat kontrak yang dimuat sesuai dengan alamat yang Anda catat setelah deployment.
* **Kriteria Penerimaan:**
    * Server FastAPI berjalan tanpa error terkait pemuatan konfigurasi _smart contract_.
    * Log menunjukkan bahwa ABI dan alamat untuk `MedicalRecordRegistry` telah dimuat dengan benar dari file JSON yang diperbarui.
* **Rollback (jika gagal):**
    * Periksa kembali path ke file `MedicalRecordRegistry-address.json` dan `MedicalRecordRegistry-abi.json` di `src/app/core/config.py`.
    * Pastikan isi file JSON tersebut valid dan sesuai dengan hasil deployment terbaru.
    * Pastikan skrip deployment (`scripts/deployMedicalRecordRegistry.js`) sudah benar dalam menyimpan informasi ini.

---

### **Baby Step 2.3.2: Pengujian Integrasi API `/medical-records/patient/me` dengan Smart Contract "Live"**

* **Tujuan:** Memvalidasi bahwa endpoint `GET /api/v1/medical-records/patient/me` dapat berhasil mengambil daftar hash rekam medis dari _smart contract_ `MedicalRecordRegistry` yang "live" di Ganache dan kemudian mengambil data yang sesuai dari database.
* **Instruksi:**
    1.  Pastikan server FastAPI dan Ganache (dengan kontrak yang sudah di-deploy) berjalan.
    2.  Identifikasi seorang pengguna (pasien) yang sudah terdaftar di sistem (atau daftarkan pengguna baru melalui API jika perlu). Pastikan pengguna ini memiliki `did` yang valid.
    3.  Buat beberapa (misalnya 2-3) rekam medis untuk pengguna ini melalui endpoint `POST /api/v1/medical-records/`.
        * Catat `data_hash` dari setiap rekam medis yang dibuat. Ini akan tercatat di _smart contract_.
    4.  Gunakan `pytest` untuk menjalankan tes integrasi spesifik yang menargetkan endpoint `GET /api/v1/medical-records/patient/me`. Fokus pada tes-tes di `tests/integration/api/test_api_medical_records.py` yang relevan, khususnya:
        * `test_get_my_medical_records_scenario1_blockchain_match`
        * `test_get_my_medical_records_scenario2_partial_or_no_db_match` (jika Anda ingin membuat skenario ini secara manual)
        * `test_get_my_medical_records_scenario3_no_blockchain_records` (untuk pengguna lain atau setelah menghapus hash dari kontrak)
        * `test_get_my_medical_records_scenario5_pagination`
    5.  **Penting:** Untuk tes ini, Anda mungkin perlu menyesuaikan `conftest.py` atau tes spesifik agar **TIDAK** me-mock `BlockchainService` sepenuhnya, melainkan memungkinkan interaksi nyata dengan Ganache untuk fungsi `get_record_hashes_for_patient`. Atau, pastikan mock di `conftest.py` untuk `get_record_hashes_for_patient` (yang sekarang `AsyncMock`) dapat dikonfigurasi per tes untuk mengembalikan data yang diharapkan seolah-olah berasal dari kontrak live.
        * **Alternatif 1 (Interaksi Nyata):** Buat fixture baru atau modifikasi `client` fixture untuk kasus di mana interaksi blockchain nyata diinginkan. Ini lebih merupakan tes E2E mini.
        * **Alternatif 2 (Refined Mocking):** Pastikan Anda dapat meng-override `return_value` dari `blockchain_service_mock.get_record_hashes_for_patient` di setiap fungsi tes di `test_api_medical_records.py` untuk menyimulasikan output kontrak yang benar. Ini sudah dilakukan di tes yang ada. Pastikan data yang di-return mock (daftar hash) konsisten dengan apa yang Anda harapkan dari kontrak yang di-deploy.
    6.  Analisis hasil tes. Jika ada kegagalan:
        * Periksa log FastAPI untuk detail error saat berinteraksi dengan `BlockchainService` atau kontrak.
        * Periksa log Ganache untuk melihat apakah ada _revert_ atau error pada level _smart contract_.
        * Gunakan `breakpoint()` atau `print()` di `src/app/core/blockchain.py` dalam metode `get_record_hashes_for_patient` untuk melihat data mentah yang dikembalikan oleh kontrak.
* **Kriteria Penerimaan:**
    * Semua tes integrasi yang relevan di `test_api_medical_records.py` untuk endpoint `GET /medical-records/patient/me` lolos ketika berinteraksi (baik secara nyata maupun melalui mock yang akurat) dengan _smart contract_ `MedicalRecordRegistry` yang telah di-deploy.
    * Respons dari API mencerminkan data yang benar sesuai dengan hash yang ada di blockchain dan data yang ada di database.
* **Rollback (jika gagal):**
    * Kembali ke penggunaan `BlockchainService` yang sepenuhnya di-mock untuk endpoint ini.
    * Analisis error: Apakah masalahnya di logika backend, cara pemanggilan kontrak, atau di logika _smart contract_ itu sendiri?
    * Jika masalah di _smart contract_, perbaiki, deploy ulang, dan ulangi Baby Step 2.3.1.

---

### **Baby Step 2.3.3: Verifikasi Manual Fungsionalitas (Opsional tapi Direkomendasikan)**

* **Tujuan:** Melakukan verifikasi manual dari keseluruhan alur untuk memastikan fungsionalitas sesuai harapan di luar lingkup tes otomatis.
* **Instruksi:**
    1.  Gunakan alat seperti Postman atau `curl`.
    2.  **Registrasi dan Login:**
        * Daftarkan pengguna baru (Pasien A) melalui `POST /api/v1/auth/register`. Catat `user_id` dan `did`.
        * Login sebagai Pasien A melalui `POST /api/v1/auth/login` untuk mendapatkan token akses.
    3.  **Buat Rekam Medis:**
        * Sebagai Pasien A (menggunakan tokennya), buat 2-3 rekam medis melalui `POST /api/v1/medical-records/`.
        * Contoh payload:
            ```json
            {
              "record_type": "DIAGNOSIS",
              "record_metadata": {"symptom": "headache"},
              "raw_data": "Patient reports persistent headache for 3 days."
            }
            ```
            ```json
            {
              "record_type": "LAB_RESULT",
              "record_metadata": {"test_name": "Blood Sugar"},
              "raw_data": "Fasting Blood Sugar: 95 mg/dL"
            }
            ```
        * Perhatikan `data_hash` dari respons atau dari log FastAPI. Buka Ganache dan periksa transaksi ke _smart contract_ `MedicalRecordRegistry`. Pastikan event `RecordAdded` terpancar dengan `recordHash`, `patientDid`, dan `recordType` yang benar.
    4.  **Ambil Daftar Rekam Medis:**
        * Sebagai Pasien A, panggil `GET /api/v1/medical-records/patient/me`.
        * Verifikasi bahwa responsnya adalah daftar rekam medis yang baru saja dibuat (metadata saja). Jumlahnya harus sesuai. Hash data di respons harus cocok dengan yang Anda catat/lihat di blockchain.
    5.  **Ambil Detail Rekam Medis:**
        * Ambil salah satu `id` rekam medis dari respons di atas.
        * Sebagai Pasien A, panggil `GET /api/v1/medical-records/{record_id_tersebut}`.
        * Verifikasi bahwa `raw_data` yang terdekripsi muncul dan sesuai dengan yang Anda input.
    6.  **(Opsional) Skenario Negatif:**
        * Coba ambil rekam medis pasien lain (jika Anda punya pengguna lain dan tokennya) untuk memastikan otorisasi bekerja.
        * Coba ambil rekam medis dengan ID yang tidak ada.
* **Kriteria Penerimaan:**
    * Semua langkah manual berhasil dan data yang ditampilkan konsisten antara input, database, blockchain (hash), dan output API.
    * Tidak ada error tak terduga di log FastAPI maupun Ganache.
* **Rollback (jika gagal):**
    * Identifikasi langkah mana yang gagal.
    * Periksa log dan gunakan debugger jika perlu untuk menelusuri alur data.

---

### **Baby Step 2.3.4: Pembaruan Dokumentasi**

* **Tujuan:** Memastikan `README.md` dan dokumentasi relevan lainnya (jika ada) diperbarui untuk mencerminkan status penyelesaian Step 2.3.
* **Instruksi:**
    1.  Perbarui `README.md` di bagian "Catatan untuk Developer" untuk mengonfirmasi bahwa `BlockchainService` sekarang diharapkan berinteraksi dengan _smart contract_ `MedicalRecordRegistry` yang "live" untuk fungsi `get_record_hashes_for_patient`.
    2.  Perbarui `memory-bank/progress.md` dengan ringkasan penyelesaian Step 2.3 secara keseluruhan.
    3.  Perbarui `memory-bank/status-todolist-suggestions.md` untuk menandai Step 2.3 sebagai SELESAI dan mengidentifikasi langkah berikutnya (misalnya, memulai Step 3 atau menangani _technical debt_).
* **Kriteria Penerimaan:**
    * Dokumentasi yang disebutkan telah diperbarui dan akurat.
* **Rollback (jika gagal):**
    * Revisi pembaruan dokumentasi hingga akurat.

---

Setelah semua baby steps ini berhasil diselesaikan, Step 2.3 dari `implementation-plan.md` dapat dianggap sepenuhnya selesai.