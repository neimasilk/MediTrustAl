# Baby-Step To-Do List: Penyelesaian MVP Lanjutan (Post Step 4.1)

Dokumen ini merinci langkah-langkah kecil (baby-steps) untuk mengimplementasikan fitur-fitur berikut:
1.  **Step 4.2**: Peningkatan Pencatatan Audit Akses Data untuk Kepatuhan PIPL.
2.  **Step 5.1**: Antarmuka Pengguna (UI) Frontend untuk Manajemen Persetujuan Pasien.
3.  **Step 5.2**: Integrasi Nyata dengan API NLP DeepSeek.

Setiap *major step* dipecah menjadi *baby-steps* yang lebih konkret.

---

## Major Step 1: Implementasi Step 4.2 - Peningkatan Pencatatan Audit Akses Data

**Tujuan:** Mencatat semua aktivitas penting terkait akses dan modifikasi persetujuan rekam medis untuk meningkatkan transparansi, akuntabilitas, dan mendukung kepatuhan PIPL.

### Baby-Step 4.2.1: Desain dan Pembuatan Tabel Database untuk Log Audit
* **Tugas:**
    1.  Rancang skema untuk tabel baru bernama `audit_data_access_logs`.
    2.  Kolom yang dibutuhkan (minimal):
        * `id`: `UUID`, Primary Key, default `gen_random_uuid()`.
        * `timestamp`: `TIMESTAMPTZ`, default `now()`, `NOT NULL`.
        * `actor_user_id`: `UUID`, Foreign Key ke `users.id`, `NOT NULL` (pengguna yang melakukan aksi).
        * `owner_user_id`: `UUID`, Foreign Key ke `users.id`, `NOT NULL` (pemilik rekam medis).
        * `record_id`: `UUID`, Foreign Key ke `medical_records.id`, `NULLABLE` (karena aksi grant/revoke bisa jadi belum terkait langsung dengan melihat satu record spesifik, namun sebaiknya tetap ada jika memungkinkan).
        * `action_type`: `VARCHAR(50)`, `NOT NULL` (contoh: `VIEW_RECORD_SUCCESS`, `VIEW_RECORD_FAILURE_FORBIDDEN`, `GRANT_ACCESS_SUCCESS`, `REVOKE_ACCESS_SUCCESS`, `GRANT_ACCESS_FAILURE`, `REVOKE_ACCESS_FAILURE`).
        * `ip_address`: `VARCHAR(45)`, `NULLABLE` (alamat IP pemohon).
        * `target_address`: `VARCHAR(42)`, `NULLABLE` (alamat blockchain dokter yang diberi/dicabut aksesnya, relevan untuk `GRANT_ACCESS` dan `REVOKE_ACCESS`).
        * `details`: `JSONB`, `NULLABLE` (untuk menyimpan konteks tambahan, misalnya, pesan error jika gagal).
    3.  Buat model SQLAlchemy di file baru `src/app/models/audit_log.py` untuk tabel `audit_data_access_logs`. Pastikan semua tipe data sesuai.
    4.  Buat file migrasi Alembic baru untuk membuat tabel ini.
        * Jalankan `alembic revision -m "create_audit_data_access_logs_table"`
        * Isi fungsi `upgrade()` dan `downgrade()` pada file migrasi yang dihasilkan.
        * Jalankan `alembic upgrade head` untuk menerapkan migrasi ke database development Anda.
* **Kriteria Keberhasilan:**
    * Tabel `audit_data_access_logs` berhasil dibuat di database dengan skema yang benar.
    * Model SQLAlchemy `AuditDataAccessLog` tersedia.
* **Dokumen Terkait untuk Dirujuk:** `memory-bank/database-schema.md` (untuk konsistensi).

### Baby-Step 4.2.2: Pembuatan Fungsi CRUD untuk Log Audit
* **Tugas:**
    1.  Buat file baru `src/app/crud/crud_audit_log.py`.
    2.  Implementasikan fungsi `create_audit_log(db: Session, actor_user_id: uuid.UUID, owner_user_id: uuid.UUID, action_type: str, record_id: uuid.UUID = None, ip_address: str = None, target_address: str = None, details: dict = None, status: str = "SUCCESS") -> models.AuditDataAccessLog`:
        * Fungsi ini akan membuat entri baru di tabel `audit_data_access_logs`.
        * Perhatikan bahwa `record_id`, `ip_address`, `target_address`, dan `details` bersifat opsional.
        * `action_type` harus mencerminkan status keberhasilan atau kegagalan, misal `VIEW_RECORD_SUCCESS` atau `VIEW_RECORD_FAILURE_FORBIDDEN`.
* **Kriteria Keberhasilan:**
    * Fungsi `create_audit_log` berhasil dibuat dan dapat menyimpan data ke tabel `audit_data_access_logs`.
    * Unit test dasar untuk fungsi `create_audit_log` dibuat dan lolos (bisa menggunakan database sesi tes SQLite).
* **File yang Dikerjakan:** `src/app/crud/crud_audit_log.py`, `tests/unit/crud/test_crud_audit_log.py` (baru).

### Baby-Step 4.2.3: Integrasi Logging pada Endpoint `get_medical_record_detail`
* **Tugas:**
    1.  Buka file `src/app/api/endpoints/medical_records.py`.
    2.  Modifikasi fungsi `get_medical_record_detail`.
    3.  Dapatkan alamat IP pemohon dari `request.client.host`. Tambahkan parameter `request: Request` pada definisi endpoint.
    4.  **Sebelum** `return response_data` (jika akses berhasil):
        * Panggil `crud_audit_log.create_audit_log` dengan:
            * `actor_user_id`: `current_user.id`.
            * `owner_user_id`: `db_record.patient_id`.
            * `record_id`: `db_record.id`.
            * `action_type`: `'VIEW_RECORD_SUCCESS'`.
            * `ip_address`: alamat IP pemohon.
    5.  **Dalam blok `HTTPException`** jika akses ditolak (`status_code=status.HTTP_403_FORBIDDEN` atau `status_code=status.HTTP_400_BAD_REQUEST` untuk dokter tanpa alamat blockchain, atau `status_code=status.HTTP_503_SERVICE_UNAVAILABLE` saat cek blockchain gagal):
        * Panggil `crud_audit_log.create_audit_log` dengan:
            * `actor_user_id`: `current_user.id`.
            * `owner_user_id`: `db_record.patient_id` (jika `db_record` sudah terdefinisi, jika belum mungkin hanya `actor_user_id`).
            * `record_id`: `db_record.id` (jika ada).
            * `action_type`: Sesuai alasan kegagalan, misal `'VIEW_RECORD_FAILURE_FORBIDDEN'`, `'VIEW_RECORD_FAILURE_NO_BC_ADDR'`, `'VIEW_RECORD_FAILURE_BC_CHECK_FAILED'`.
            * `ip_address`: alamat IP pemohon.
            * `details`: Bisa berisi pesan error dari exception.
* **Kriteria Keberhasilan:**
    * Setiap panggilan sukses atau gagal (karena otorisasi) ke `get_medical_record_detail` menghasilkan entri log audit yang benar di database.
* **File yang Dikerjakan:** `src/app/api/endpoints/medical_records.py`.
* **Pengujian Manual (Tambahan untuk `petunjuk-manual-test.md`):**
    1.  Pasien A login, lihat rekam medisnya -> Cek log: `VIEW_RECORD_SUCCESS` oleh Pasien A.
    2.  Dokter X (sudah di-grant akses) login, lihat rekam medis Pasien A -> Cek log: `VIEW_RECORD_SUCCESS` oleh Dokter X.
    3.  Dokter Y (belum di-grant akses) login, coba lihat rekam medis Pasien A -> Cek log: `VIEW_RECORD_FAILURE_FORBIDDEN` (atau sejenisnya) oleh Dokter Y.

### Baby-Step 4.2.4: Integrasi Logging pada Endpoint `grant_medical_record_access`
* **Tugas:**
    1.  Buka file `src/app/api/endpoints/medical_records.py`.
    2.  Modifikasi fungsi `grant_medical_record_access`.
    3.  Dapatkan alamat IP pemohon.
    4.  **Setelah** panggilan `blockchain_service.grant_record_access` berhasil dan **sebelum** `return`:
        * Panggil `crud_audit_log.create_audit_log` dengan:
            * `actor_user_id`: `current_user.id` (pasien yang memberi akses).
            * `owner_user_id`: `current_user.id`.
            * `record_id`: `record_id` (dari path parameter).
            * `action_type`: `'GRANT_ACCESS_SUCCESS'`.
            * `ip_address`: alamat IP pemohon.
            * `target_address`: `access_request.doctor_address`.
            * `details`: Bisa berisi `transaction_hash` dari blockchain.
    5.  **Dalam blok `HTTPException`** jika `blockchain_service.grant_record_access` gagal:
        * Panggil `crud_audit_log.create_audit_log` dengan:
            * `actor_user_id`: `current_user.id`.
            * `owner_user_id`: `current_user.id`.
            * `record_id`: `record_id`.
            * `action_type`: `'GRANT_ACCESS_FAILURE'`.
            * `ip_address`: alamat IP pemohon.
            * `target_address`: `access_request.doctor_address`.
            * `details`: Pesan error dari `blockchain_result`.
* **Kriteria Keberhasilan:**
    * Setiap panggilan sukses atau gagal ke `grant_medical_record_access` menghasilkan entri log audit yang benar.
* **File yang Dikerjakan:** `src/app/api/endpoints/medical_records.py`.
* **Pengujian Manual (Tambahan untuk `petunjuk-manual-test.md`):**
    1.  Pasien A login, grant akses rekam medisnya ke Dokter X -> Cek log: `GRANT_ACCESS_SUCCESS`.

### Baby-Step 4.2.5: Integrasi Logging pada Endpoint `revoke_medical_record_access`
* **Tugas:**
    1.  Buka file `src/app/api/endpoints/medical_records.py`.
    2.  Modifikasi fungsi `revoke_medical_record_access`.
    3.  Dapatkan alamat IP pemohon.
    4.  **Setelah** panggilan `blockchain_service.revoke_record_access` berhasil dan **sebelum** `return`:
        * Panggil `crud_audit_log.create_audit_log` dengan:
            * `actor_user_id`: `current_user.id`.
            * `owner_user_id`: `current_user.id`.
            * `record_id`: `record_id`.
            * `action_type`: `'REVOKE_ACCESS_SUCCESS'`.
            * `ip_address`: alamat IP pemohon.
            * `target_address`: `access_request.doctor_address`.
            * `details`: `transaction_hash`.
    5.  **Dalam blok `HTTPException`** jika `blockchain_service.revoke_record_access` gagal:
        * Panggil `crud_audit_log.create_audit_log` dengan data serupa, `action_type`: `'REVOKE_ACCESS_FAILURE'`, dan detail error.
* **Kriteria Keberhasilan:**
    * Setiap panggilan sukses atau gagal ke `revoke_medical_record_access` menghasilkan entri log audit yang benar.
* **File yang Dikerjakan:** `src/app/api/endpoints/medical_records.py`.
* **Pengujian Manual (Tambahan untuk `petunjuk-manual-test.md`):**
    1.  Pasien A login, revoke akses Dokter X dari rekam medisnya -> Cek log: `REVOKE_ACCESS_SUCCESS`.

### Baby-Step 4.2.6 (Opsional untuk MVP Awal): Endpoint API untuk Pasien Melihat Riwayat Akses
* **Tugas:**
    1.  Buat endpoint baru di `src/app/api/endpoints/audit_log_routes.py` (atau nama file yang sesuai): `GET /api/v1/audit/my-record-access-history`
    2.  Endpoint ini harus diproteksi (`Depends(get_current_active_user)`).
    3.  Implementasikan fungsi CRUD di `crud_audit_log.py` untuk mengambil log berdasarkan `owner_user_id` atau kombinasi `owner_user_id` dan `record_id` (jika ingin lebih spesifik per rekam medis).
    4.  Endpoint mengembalikan daftar log audit yang relevan untuk `current_user` sebagai pemilik data.
* **Kriteria Keberhasilan:**
    * Pasien yang terautentikasi dapat mengambil riwayat akses yang relevan dengan data mereka.
* **File yang Dikerjakan:** `src/app/api/endpoints/audit_log_routes.py` (baru), `src/app/crud/crud_audit_log.py` (modifikasi).

---

## Major Step 2: Implementasi Step 5.1 - UI Frontend untuk Manajemen Persetujuan Pasien

**Tujuan:** Memberikan pasien kemampuan untuk mengelola (memberi dan mencabut) izin akses dokter ke rekam medis mereka melalui antarmuka pengguna yang intuitif di Portal Pasien.

### Baby-Step 5.1.1: Persiapan Layanan Frontend untuk Consent
* **Tugas:**
    1.  Buka file `frontend/src/services/medicalRecordService.js`.
    2.  Tambahkan fungsi asynchronous baru:
        * `grantAccessToRecord(recordId, doctorAddress)`:
            * Mengambil `recordId` dan `doctorAddress` sebagai argumen.
            * Mengambil token dari `tokenManager.getToken()`.
            * Membuat panggilan `POST` ke `http://localhost:8000/api/v1/medical-records/{recordId}/grant-access` dengan payload `{ doctor_address: doctorAddress }` dan header Otorisasi.
            * Menangani respons sukses dan error.
        * `revokeAccessFromRecord(recordId, doctorAddress)`:
            * Serupa dengan `grantAccessToRecord`, tetapi memanggil endpoint `revoke-access`.
        * `checkRecordAccessForDoctor(recordId, doctorAddress)` (jika dibutuhkan untuk menampilkan status akses dokter tertentu):
            * Membuat panggilan `GET` ke `http://localhost:8000/api/v1/medical-records/{recordId}/check-access/{doctorAddress}`.
* **Kriteria Keberhasilan:**
    * Fungsi-fungsi layanan berhasil dibuat dan siap digunakan oleh komponen UI.
* **File yang Dikerjakan:** `frontend/src/services/medicalRecordService.js`.

### Baby-Step 5.1.2: Desain dan Implementasi Komponen UI untuk Menampilkan Daftar Dokter yang Memiliki Akses (per Rekam Medis)
* **Tugas:**
    1.  Tentukan di mana daftar dokter yang memiliki akses akan ditampilkan. Opsi:
        * Sebagai bagian dari detail setiap rekam medis di `DashboardPage.jsx`.
        * Dalam sebuah modal yang muncul saat pasien mengklik tombol "Kelola Akses" pada item rekam medis. (Pendekatan ini mungkin lebih bersih).
    2.  Jika menggunakan modal, buat komponen baru `frontend/src/components/RecordAccessManagementModal.jsx`.
    3.  Modal ini akan menerima `record` sebagai prop.
    4.  Di dalam modal:
        * Tampilkan ID Rekam Medis.
        * **Placeholder**: Buat area untuk menampilkan daftar dokter yang saat ini memiliki akses. Untuk saat ini, ini bisa statis atau kosong karena kita belum memiliki cara mudah untuk mendapatkan daftar ini dari *smart contract* hanya dengan `record_hash`. *Smart contract* saat ini hanya bisa `checkAccess` untuk satu dokter spesifik.
            * **Ambiguitas/Penyederhanaan MVP**: Karena `MedicalRecordRegistry.sol` tidak memiliki fungsi untuk mengambil *semua* dokter yang memiliki akses ke suatu `recordHash`, kita akan menyederhanakan UI ini. Daripada menampilkan daftar, kita akan fokus pada fungsi grant dan revoke untuk dokter yang *diketahui* oleh pasien.
            * **Alternatif untuk UI yang Lebih Baik (Pasca-MVP)**: Perlu modifikasi *smart contract* untuk menyimpan dan mengambil daftar alamat yang diizinkan per `recordHash`.
* **Kriteria Keberhasilan (untuk MVP yang disederhanakan):**
    * Modal/bagian UI dasar dibuat dan dapat menampilkan ID rekam medis.
* **File yang Dikerjakan:** `frontend/src/components/RecordAccessManagementModal.jsx` (baru), `frontend/src/pages/DashboardPage.jsx` (modifikasi untuk memicu modal).

### Baby-Step 5.1.3: Implementasi UI untuk Memberikan Akses (Grant Access)
* **Tugas:**
    1.  Di dalam `RecordAccessManagementModal.jsx` (atau di mana pun fitur ini ditempatkan):
        * Tambahkan *form input* untuk "Alamat Blockchain Dokter" (`TextField` dari MUI).
        * Tambahkan tombol "Berikan Akses" (`Button` dari MUI).
        * State lokal untuk menyimpan input alamat dokter, status loading, dan pesan error/sukses.
    2.  Saat tombol "Berikan Akses" diklik:
        * Panggil fungsi `grantAccessToRecord` dari `medicalRecordService.js` dengan `record.id` dan alamat dokter yang diinput.
        * Tampilkan indikator loading selama proses.
        * Tampilkan pesan sukses atau error berdasarkan respons API.
        * (Opsional) Setelah sukses, bersihkan input field.
* **Kriteria Keberhasilan:**
    * Pasien dapat memasukkan alamat dokter dan berhasil memicu panggilan API untuk memberikan akses.
    * UI merespons dengan status loading, sukses, atau error.
* **File yang Dikerjakan:** `frontend/src/components/RecordAccessManagementModal.jsx`.
* **Pengujian Manual (Tambahkan ke `petunjuk-manual-test.md`):**
    1.  Login sebagai Pasien A.
    2.  Buka pengelolaan akses untuk salah satu rekam medisnya.
    3.  Masukkan alamat blockchain Dokter Y (yang valid).
    4.  Klik "Berikan Akses".
    5.  Verifikasi pesan sukses di UI.
    6.  Cek log audit di backend (dari Step 4.2) untuk `GRANT_ACCESS_SUCCESS`.
    7.  (Opsional) Coba login sebagai Dokter Y dan verifikasi bisa mengakses rekam medis tersebut.
    8.  Tes dengan alamat tidak valid -> UI menampilkan error.

### Baby-Step 5.1.4: Implementasi UI untuk Mencabut Akses (Revoke Access)
* **Tugas:**
    1.  Di dalam `RecordAccessManagementModal.jsx`:
        * Tambahkan *form input* untuk "Alamat Blockchain Dokter yang Aksesnya Akan Dicabut".
        * Tambahkan tombol "Cabut Akses".
    2.  Saat tombol "Cabut Akses" diklik:
        * Panggil fungsi `revokeAccessFromRecord` dari `medicalRecordService.js`.
        * Tampilkan indikator loading.
        * Tampilkan pesan sukses/error.
* **Kriteria Keberhasilan:**
    * Pasien dapat memasukkan alamat dokter dan berhasil memicu panggilan API untuk mencabut akses.
    * UI merespons dengan status loading, sukses, atau error.
* **File yang Dikerjakan:** `frontend/src/components/RecordAccessManagementModal.jsx`.
* **Pengujian Manual (Tambahkan ke `petunjuk-manual-test.md`):**
    1.  Login sebagai Pasien A.
    2.  Pastikan Dokter Y sudah memiliki akses ke salah satu rekam medis Pasien A.
    3.  Buka pengelolaan akses untuk rekam medis tersebut.
    4.  Masukkan alamat blockchain Dokter Y.
    5.  Klik "Cabut Akses".
    6.  Verifikasi pesan sukses di UI.
    7.  Cek log audit di backend untuk `REVOKE_ACCESS_SUCCESS`.
    8.  (Opsional) Coba login sebagai Dokter Y dan verifikasi TIDAK BISA lagi mengakses rekam medis tersebut.

---

## Major Step 3: Implementasi Step 5.2 - Integrasi Nyata dengan API NLP DeepSeek

**Tujuan:** Mengganti layanan NLP placeholder dengan integrasi fungsional ke DeepSeek API untuk melakukan ekstraksi entitas medis dari teks.

### Baby-Step 5.2.1: Riset dan Persiapan API DeepSeek
* **Tugas:**
    1.  Kunjungi situs web DeepSeek API ([https://platform.deepseek.com/](https://platform.deepseek.com/) atau yang relevan).
    2.  Buat akun dan dapatkan API Key.
    3.  Pelajari dokumentasi API mereka:
        * Identifikasi endpoint yang tepat untuk *text entity extraction* atau *Named Entity Recognition (NER)*.
        * Pahami format *request body* yang diharapkan (misalnya, model yang digunakan, parameter input teks).
        * Pahami format *response body*, terutama bagaimana entitas yang diekstrak dikembalikan (teks entitas, tipe entitas, posisi, skor kepercayaan, dll.).
        * Perhatikan batasan penggunaan (*rate limits*, ukuran teks maksimum).
    4.  Simpan API Key DeepSeek Anda dengan aman di file `.env` di root proyek backend dengan nama variabel `DEEPSEEK_API_KEY="kunci_api_anda"`. JANGAN masukkan kunci API langsung ke kode.
    5.  Tambahkan `DEEPSEEK_API_KEY` ke `src/app/core/config.py` untuk dimuat dari variabel lingkungan.
    6.  Pastikan `httpx` (atau `requests`) sudah ada di `requirements.txt`. Jika belum, tambahkan dan install (`pip install httpx`).
* **Kriteria Keberhasilan:**
    * API Key DeepSeek berhasil didapatkan.
    * Dokumentasi API DeepSeek telah dipahami.
    * API Key tersimpan aman di `.env` dan dapat diakses melalui `config.py`.
* **File yang Dikerjakan:** `.env`, `src/app/core/config.py`.

### Baby-Step 5.2.2: Implementasi Panggilan ke DeepSeek API di Layanan NLP Backend
* **Tugas:**
    1.  Buka file `src/app/services/nlp_service.py`.
    2.  Hapus fungsi `extract_entities_placeholder` yang lama atau modifikasi fungsi `extract_entities_placeholder` menjadi fungsi utama yang baru. Mari kita sebut fungsi utama baru ini `extract_entities_from_text(text_input: str) -> dict`.
    3.  Di dalam `extract_entities_from_text`:
        * Impor `httpx` dan `DEEPSEEK_API_KEY` dari `config`.
        * Definisikan URL endpoint DeepSeek API.
        * Siapkan *headers* untuk panggilan API, termasuk `Authorization: Bearer {DEEPSEEK_API_KEY}` dan `Content-Type: application/json`.
        * Siapkan *payload* (request body) sesuai format DeepSeek. Biasanya akan ada field untuk `model` (pilih model yang sesuai, misal `deepseek-coder` atau model chat jika NER adalah bagian dari kemampuan chatnya) dan `messages` atau `prompt` yang berisi `text_input`.
            ```python
            # Contoh payload (sesuaikan dengan dokumentasi DeepSeek):
            # payload = {
            #     "model": "deepseek-chat", # atau model lain yang sesuai
            #     "messages": [
            #         {"role": "system", "content": "You are an expert medical entity extractor."},
            #         {"role": "user", "content": f"Extract medical entities from the following text: {text_input}"}
            #     ],
            #     # tambahkan parameter lain jika perlu, seperti temperature, max_tokens, dll.
            # }
            ```
        * Gunakan `httpx.AsyncClient()` untuk membuat panggilan `POST` asinkron ke DeepSeek API.
            ```python
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30.0)
            #     response.raise_for_status() # Akan raise exception untuk status 4xx/5xx
            #     deepseek_response_data = response.json()
            ```
        * Implementasikan *error handling* yang baik untuk panggilan API (koneksi error, timeout, status error dari API).
* **Kriteria Keberhasilan:**
    * Fungsi `extract_entities_from_text` dapat membuat panggilan ke DeepSeek API dan menerima respons.
    * Error pada panggilan API ditangani dengan baik (misalnya, melempar exception yang spesifik).
* **File yang Dikerjakan:** `src/app/services/nlp_service.py`.

### Baby-Step 5.2.3: Pemrosesan Respons DeepSeek API dan Transformasi Data
* **Tugas:**
    1.  Masih di `src/app/services/nlp_service.py`, dalam fungsi `extract_entities_from_text`.
    2.  Setelah mendapatkan `deepseek_response_data` (JSON dari DeepSeek):
        * Telusuri struktur respons DeepSeek untuk menemukan bagian yang berisi entitas yang diekstrak. Ini akan sangat bergantung pada model dan endpoint yang Anda gunakan.
        * Untuk setiap entitas yang ditemukan di respons DeepSeek, transformasikan ke format `NLPEntity` yang didefinisikan di `src/app/api/endpoints/nlp.py` (`{"text": "...", "type": "..."}`).
            * Anda mungkin perlu melakukan pemetaan. Misalnya, jika DeepSeek mengembalikan tipe entitas "DISEASE_OR_SYMPTOM", Anda mungkin ingin memetakannya ke "Diagnosis" atau "Symptom" di sistem Anda, atau menggunakannya apa adanya.
            * Jika DeepSeek tidak secara langsung memberikan tipe entitas yang Anda inginkan, Anda mungkin perlu logika tambahan atau menggunakan *prompt engineering* yang lebih baik saat memanggil API. Untuk MVP, pemetaan sederhana atau penggunaan tipe dari DeepSeek secara langsung mungkin cukup.
        * Kumpulkan semua entitas yang telah ditransformasi ke dalam sebuah list.
    3.  Fungsi `extract_entities_from_text` harus mengembalikan dictionary dengan format: `{"entities": list_of_transformed_nlp_entities}`.
* **Kriteria Keberhasilan:**
    * Respons JSON dari DeepSeek berhasil diproses.
    * Data entitas dari DeepSeek berhasil ditransformasi ke format `NLPEntity` yang digunakan oleh aplikasi Anda.
    * Fungsi mengembalikan data dalam format yang diharapkan oleh `NLPExtractionResponse`.
* **File yang Dikerjakan:** `src/app/services/nlp_service.py`.

### Baby-Step 5.2.4: Pengujian Unit dan Integrasi untuk Layanan NLP Baru
* **Tugas:**
    1.  Update/buat unit test baru untuk `extract_entities_from_text` di `tests/unit/services/test_nlp_service.py`.
        * **PENTING**: *Mock* panggilan `httpx.AsyncClient().post` untuk mengembalikan respons DeepSeek API yang sudah Anda siapkan (berbagai skenario: sukses dengan entitas, sukses tanpa entitas, error API).
        * Verifikasi bahwa fungsi memproses *mock response* dengan benar dan menghasilkan output yang diharapkan.
        * Verifikasi bahwa *error handling* berfungsi (misalnya, jika *mock response* adalah error 500 dari DeepSeek).
    2.  Jalankan kembali tes integrasi di `tests/integration/api/test_api_nlp.py`.
        * Tes ini sekarang akan memanggil layanan NLP yang sesungguhnya (yang akan memanggil DeepSeek API jika tidak di-*mock* di level `conftest.py` atau tes integrasi).
        * Jika Anda ingin tes integrasi tidak benar-benar memanggil DeepSeek API (untuk menghindari biaya atau dependensi eksternal selama tes otomatis), Anda perlu mem-*mock* fungsi `extract_entities_from_text` itu sendiri di level tes integrasi, atau mem-*mock* panggilan `httpx` di `conftest.py` jika itu mempengaruhi semua tes.
        * **Saran untuk tes integrasi**: Mungkin lebih baik membiarkannya memanggil DeepSeek jika Anda memiliki *allowance* API call yang cukup dan koneksi internet yang stabil, untuk pengujian yang lebih nyata. Atau, siapkan *mock server* untuk DeepSeek API.
* **Kriteria Keberhasilan:**
    * Semua unit test untuk layanan NLP lolos.
    * Tes integrasi untuk endpoint `/api/v1/nlp/extract-entities` lolos, mengembalikan entitas yang diharapkan (baik dari *mock* DeepSeek atau panggilan nyata).
* **File yang Dikerjakan:** `tests/unit/services/test_nlp_service.py`, `tests/integration/api/test_api_nlp.py`.

### Baby-Step 5.2.5: (Opsional untuk Demo MVP) Menampilkan Entitas Hasil Ekstraksi di Frontend
* **Tugas (jika diputuskan untuk diimplementasikan sebagai bagian dari MVP):**
    1.  Tentukan di mana entitas akan ditampilkan. Contoh: di halaman detail rekam medis, setelah mengambil `raw_data`, ada tombol "Ekstrak Entitas" yang memanggil API NLP.
    2.  Buat komponen React baru untuk menampilkan daftar entitas (misalnya, `EntityDisplayList.jsx`).
    3.  Modifikasi layanan frontend (`nlpService.js` atau yang serupa) untuk memanggil endpoint `/api/v1/nlp/extract-entities` dengan teks dari rekam medis.
    4.  Tampilkan entitas yang diterima di komponen `EntityDisplayList.jsx`.
* **Kriteria Keberhasilan:**
    * Pengguna dapat memicu ekstraksi entitas dari teks rekam medis di frontend.
    * Entitas yang diekstrak oleh DeepSeek (melalui backend) ditampilkan dengan benar di UI.
* **File yang Dikerjakan (Frontend):** Komponen baru, modifikasi halaman yang ada, layanan API baru.
* **Pengujian Manual (Tambahan untuk `petunjuk-manual-test.md`):**
    1.  Login sebagai Pasien A.
    2.  Buka rekam medis yang memiliki `raw_data` (teks).
    3.  Klik tombol "Ekstrak Entitas".
    4.  Verifikasi bahwa daftar entitas (misalnya "Blood Pressure" - "VitalSign", "120/80 mmHg" - "Measurement", atau entitas nyata dari DeepSeek) ditampilkan.
    5.  Coba dengan beberapa teks medis yang berbeda untuk melihat variasi hasil ekstraksi.

---

Pastikan setiap *baby-step* di atas diuji secara menyeluruh sebelum melanjutkan ke *baby-step* berikutnya. Setelah semua *baby-steps* dalam satu *major step* selesai, lakukan pengujian manual yang lebih komprehensif untuk fitur tersebut secara keseluruhan. Jangan lupa untuk terus memperbarui `progress.md` dan dokumen relevan lainnya setelah setiap *major step* berhasil diselesaikan dan divalidasi.