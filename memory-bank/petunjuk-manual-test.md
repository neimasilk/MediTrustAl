# Petunjuk Manual Test untuk Frontend Patient Portal

Dokumen ini berisi langkah-langkah untuk melakukan tes manual pada fungsionalitas dasar Patient Portal frontend dan beberapa aspek backend terkait.

**Catatan Penting:** Saat ini, terdapat 5 tes backend otomatis yang gagal:
*   3 kegagalan di `tests/integration/api/test_api_medical_records.py` (berkaitan dengan `DetachedInstanceError` dan `IntegrityError` - kemungkinan masalah sesi SQLAlchemy dalam tes).
*   2 kegagalan `AssertionError` di `tests/integration/api/test_api_nlp.py` (berkaitan dengan detail pesan error yang tidak cocok saat mock service NLP menghasilkan exception).
Mohon lakukan verifikasi manual yang lebih teliti pada fungsionalitas terkait (detail rekam medis, terutama terkait error handling dekripsi dan kasus dokter tanpa hash; dan error handling pada endpoint NLP).

## Prerequisites (Persiapan Awal):

1.  **Backend Server Berjalan:**
    *   Pastikan server backend FastAPI sudah berjalan. Biasanya dijalankan dengan perintah seperti `python -m src.app.main` (jika di root) atau `python -m app.main` dari dalam direktori `src/`.
    *   Verifikasi backend dapat diakses, misalnya di `http://localhost:8000/docs`.

2.  **Frontend Development Server Berjalan:**
    *   Pastikan server development frontend Vite sudah berjalan.
    *   Masuk ke direktori `frontend` (`cd frontend`).
    *   Jalankan dengan perintah `npm run dev`.
    *   Frontend akan tersedia di `http://localhost:5173` (atau port lain jika 5173 sudah digunakan).

3.  **Data Pengguna (User):**
    *   Siapkan setidaknya dua akun pasien (Pasien A, Pasien B) dan dua akun dokter (Dokter X, Dokter Y) yang sudah terdaftar di sistem. Pastikan Dokter X dan Dokter Y memiliki alamat blockchain yang valid dan terkonfigurasi di database.
    *   Anda bisa mendaftarkan pengguna baru melalui endpoint API backend (`POST /api/v1/auth/register`) menggunakan tools seperti Postman atau curl.
    *   Catat username dan password semua pengguna tersebut untuk login.

4.  **Data Rekam Medis (Opsional):**
    *   Untuk menguji tampilan daftar rekam medis di dashboard, pengguna yang login sebaiknya memiliki beberapa data rekam medis.
    *   Jika tidak ada, dashboard diharapkan menampilkan pesan "Anda belum memiliki rekam medis" atau sejenisnya. Anda bisa membuat rekam medis melalui endpoint API backend (`POST /api/v1/medical-records`) atas nama pengguna yang akan login. Pastikan rekam medis ini memiliki `data_hash`.

5.  **Akses Database:**
    *   Siapkan akses ke database backend untuk memverifikasi entri tabel `audit_data_access_logs`.

## Test Cases Frontend:

### 1. Tampilan Halaman Login (Login Page UI)

*   **Tindakan:**
    1.  Buka browser (misalnya Chrome, Firefox).
    2.  Navigasi ke alamat frontend, contoh: `http://localhost:5173`.
*   **Hasil yang Diharapkan:**
    *   Anda akan secara otomatis diarahkan ke halaman `/login`.
    *   Halaman login harus menampilkan:
        *   Judul (misalnya, "Login" atau "Masuk").
        *   Input field untuk "Username or Email".
        *   Input field untuk "Password".
        *   Tombol "Login" (atau "Masuk").

### 2. Login dengan Kredensial Tidak Valid

*   **Tindakan:**
    1.  Di halaman login, masukkan kombinasi username/email dan password yang salah atau tidak terdaftar.
    2.  Klik tombol "Login".
*   **Hasil yang Diharapkan:**
    *   Sebuah pesan error akan ditampilkan di halaman login (misalnya, "Login Gagal. Periksa kembali username/email dan password Anda," atau pesan error dari backend).
    *   Anda tetap berada di halaman `/login`.
    *   Periksa _browser console_ (Developer Tools > Console): tidak boleh ada error fatal yang menghentikan aplikasi. Error terkait respons API (misalnya 401 atau 400) boleh ada.

### 3. Login dengan Kredensial Valid

*   **Tindakan:**
    1.  Di halaman login, masukkan username/email dan password yang benar untuk Pasien A.
    2.  Klik tombol "Login".
*   **Hasil yang Diharapkan:**
    *   Anda akan diarahkan ke halaman `/dashboard`.
    *   Buka Developer Tools > Application > Local Storage: sebuah item `access_token` (atau nama serupa yang didefinisikan di `tokenManager.js`) harus ada dan berisi token JWT.

### 4. Tampilan Halaman Dashboard (Setelah Login)

*   **Tindakan:**
    1.  Setelah berhasil login sebagai Pasien A, Anda berada di halaman `/dashboard`.
*   **Hasil yang Diharapkan:**
    *   Sebuah pesan selamat datang ditampilkan (misalnya, "Selamat Datang di Dashboard Anda, [username Pasien A]").
    *   Tombol "Logout" (atau "Keluar") terlihat.
    *   **Jika Pasien A memiliki rekam medis:**
        *   Sebuah tabel atau daftar rekam medis akan ditampilkan.
        *   Kolom yang ada minimal: ID Rekam Medis, Tipe Rekam Medis, Tanggal Dibuat (terformat), Hash Data, dan tombol/ikon "Kelola Akses".
        *   Data yang ditampilkan harus sesuai dengan rekam medis milik Pasien A.
    *   **Jika Pasien A tidak memiliki rekam medis:**
        *   Pesan seperti "Anda belum memiliki rekam medis" atau "Tidak ada data rekam medis" akan ditampilkan.

### 5. Akses Rute Terproteksi (Dashboard)

*   **Tindakan (Ketika Belum Login):**
    1.  Pastikan Anda sudah logout atau buka _incognito window_ baru.
    2.  Coba akses langsung ke `http://localhost:5173/dashboard`.
*   **Hasil yang Diharapkan (Ketika Belum Login):**
    *   Anda akan secara otomatis diarahkan kembali ke halaman `/login`.

*   **Tindakan (Ketika Sudah Login):**
    1.  Login ke aplikasi sebagai Pasien A sehingga Anda berada di halaman `/dashboard`.
    2.  Refresh halaman `/dashboard` (tekan F5 atau tombol refresh browser).
*   **Hasil yang Diharapkan (Ketika Sudah Login):**
    *   Anda tetap berada di halaman `/dashboard`.
    *   Data di dashboard (termasuk daftar rekam medis) akan dimuat ulang dengan benar.

### 6. Fungsionalitas Logout

*   **Tindakan:**
    1.  Pastikan Anda sedang login dan berada di halaman `/dashboard`.
    2.  Klik tombol "Logout".
*   **Hasil yang Diharapkan:**
    *   Anda akan diarahkan kembali ke halaman `/login`.
    *   Buka Developer Tools > Application > Local Storage: item `access_token` harus sudah terhapus.
    *   Mencoba mengakses `http://localhost:5173/dashboard` secara langsung setelah logout akan mengarahkan Anda kembali ke `/login`.

### 7. UI Consent Management - Grant Access (Test Case 5.1.3)

*   **Persiapan:**
    *   Pastikan Pasien A memiliki setidaknya satu rekam medis.
    *   Pastikan Dokter Y memiliki akun dan alamat blockchain yang valid.
*   **Tindakan:**
    1.  Login sebagai Pasien A di frontend.
    2.  Navigasi ke Dashboard.
    3.  Untuk salah satu rekam medis milik Pasien A, klik tombol "Kelola Akses" (atau ikon serupa) untuk membuka modal "Manage Access for Record: [Record ID]".
    4.  Dalam modal, masukkan alamat blockchain Dokter Y yang valid di field "Alamat Blockchain Dokter".
    5.  Klik tombol "Berikan Akses".
*   **Hasil yang Diharapkan:**
    *   UI menampilkan indikator loading pada tombol "Berikan Akses".
    *   Setelah beberapa saat, UI menampilkan pesan sukses (misalnya, "Akses berhasil diberikan kepada [Alamat Dokter Y]").
    *   Input field alamat dokter mungkin dikosongkan atau tetap berisi alamat Dokter Y.
    *   **Verifikasi Backend:** Cek tabel `audit_data_access_logs`. Harus ada entri baru dengan `actor_user_id` = ID Pasien A, `owner_user_id` = ID Pasien A, `action_type` = `'GRANT_ACCESS_SUCCESS'`, `target_address` = alamat Dokter Y, dan IP address.
*   **Tindakan (Input Tidak Valid):**
    1.  Di modal yang sama, kosongkan field "Alamat Blockchain Dokter".
    2.  Klik tombol "Berikan Akses".
*   **Hasil yang Diharapkan (Input Tidak Valid):**
    *   UI menampilkan pesan error validasi (misalnya, "Alamat dokter tidak boleh kosong.").
*   **Tindakan (Input Alamat Tidak Valid Format):**
    1.  Di modal yang sama, masukkan alamat blockchain yang tidak valid formatnya (misal, "0x123").
    2.  Klik tombol "Berikan Akses".
*   **Hasil yang Diharapkan (Input Alamat Tidak Valid Format):**
    *   Jika validasi frontend ada, tampilkan error. Jika tidak, backend akan mengembalikan error 422 atau 400. Pesan error API (misal, "Invalid Ethereum address format") harus ditampilkan di UI.

### 8. UI Consent Management - Revoke Access (Test Case 5.1.4)

*   **Persiapan:**
    *   Pastikan Dokter Y sudah memiliki akses ke salah satu rekam medis Pasien A (misalnya dari hasil Test Case 5.1.3).
*   **Tindakan:**
    1.  Login sebagai Pasien A di frontend.
    2.  Navigasi ke Dashboard.
    3.  Buka modal "Kelola Akses" untuk rekam medis yang aksesnya telah diberikan kepada Dokter Y.
    4.  Masukkan alamat blockchain Dokter Y di field "Alamat Blockchain Dokter".
    5.  Klik tombol "Cabut Akses".
*   **Hasil yang Diharapkan:**
    *   UI menampilkan indikator loading pada tombol "Cabut Akses".
    *   Setelah beberapa saat, UI menampilkan pesan sukses (misalnya, "Akses berhasil dicabut dari [Alamat Dokter Y]").
    *   **Verifikasi Backend:** Cek tabel `audit_data_access_logs`. Harus ada entri baru dengan `actor_user_id` = ID Pasien A, `owner_user_id` = ID Pasien A, `action_type` = `'REVOKE_ACCESS_SUCCESS'`, `target_address` = alamat Dokter Y, dan IP address.
*   **Tindakan (Input Tidak Valid):**
    1.  Di modal yang sama, kosongkan field "Alamat Blockchain Dokter".
    2.  Klik tombol "Cabut Akses".
*   **Hasil yang Diharapkan (Input Tidak Valid):**
    *   UI menampilkan pesan error validasi (misalnya, "Alamat dokter untuk dicabut tidak boleh kosong.").

## Test Cases Backend & API (Menggunakan Tools seperti Postman/curl):

### 1. Verifikasi Log Audit untuk `get_medical_record_detail` (Test Case 4.2.3)

*   **Persiapan:**
    *   Pasien A memiliki rekam medis (RM_A1).
    *   Dokter X memiliki akses ke RM_A1 (diberikan sebelumnya atau sebagai bagian dari persiapan tes).
    *   Dokter Y tidak memiliki akses ke RM_A1.
*   **Tindakan 1: Pasien A akses rekam medisnya sendiri**
    1.  Login sebagai Pasien A (dapatkan token).
    2.  Panggil API `GET /api/v1/medical-records/{RM_A1_ID}` dengan token Pasien A.
*   **Hasil yang Diharapkan 1:**
    *   Respons sukses (200 OK) dengan detail RM_A1.
    *   Cek tabel `audit_data_access_logs` di database: Entri baru dengan `actor_user_id` = ID Pasien A, `owner_user_id` = ID Pasien A, `record_id` = RM_A1_ID, `action_type` = `'VIEW_RECORD_SUCCESS'`, dan IP address pemanggil.
*   **Tindakan 2: Dokter X (berhak) akses rekam medis Pasien A**
    1.  Login sebagai Dokter X (dapatkan token).
    2.  Panggil API `GET /api/v1/medical-records/{RM_A1_ID}` dengan token Dokter X.
*   **Hasil yang Diharapkan 2:**
    *   Respons sukses (200 OK) dengan detail RM_A1.
    *   Cek tabel `audit_data_access_logs`: Entri baru dengan `actor_user_id` = ID Dokter X, `owner_user_id` = ID Pasien A, `record_id` = RM_A1_ID, `action_type` = `'VIEW_RECORD_SUCCESS'`, dan IP address pemanggil.
*   **Tindakan 3: Dokter Y (tidak berhak) coba akses rekam medis Pasien A**
    1.  Login sebagai Dokter Y (dapatkan token).
    2.  Panggil API `GET /api/v1/medical-records/{RM_A1_ID}` dengan token Dokter Y.
*   **Hasil yang Diharapkan 3:**
    *   Respons gagal (403 Forbidden atau error lain yang sesuai jika akses blockchain gagal).
    *   Cek tabel `audit_data_access_logs`: Entri baru dengan `actor_user_id` = ID Dokter Y, `owner_user_id` = ID Pasien A, `record_id` = RM_A1_ID, `action_type` sesuai skenario kegagalan (misalnya, `'VIEW_RECORD_FAILURE_FORBIDDEN'`, `'VIEW_RECORD_FAILURE_BC_CHECK_FAILED'`), dan IP address pemanggil.

### 2. Verifikasi Log Audit untuk `grant_medical_record_access` (Test Case 4.2.4)

*   **Persiapan:**
    *   Pasien A memiliki rekam medis (RM_A2) yang belum diakseskan ke Dokter X.
    *   Pasien B memiliki rekam medis (RM_B1).
*   **Tindakan 1: Pasien A memberikan akses RM_A2 ke Dokter X**
    1.  Login sebagai Pasien A (dapatkan token).
    2.  Panggil API `POST /api/v1/medical-records/{RM_A2_ID}/grant-access` dengan token Pasien A dan payload `{"doctor_address": "ALAMAT_BLOCKCHAIN_DOKTER_X"}`.
*   **Hasil yang Diharapkan 1:**
    *   Respons sukses (200 OK).
    *   Cek tabel `audit_data_access_logs`: Entri baru dengan `actor_user_id` = ID Pasien A, `owner_user_id` = ID Pasien A, `record_id` = RM_A2_ID, `action_type` = `'GRANT_ACCESS_SUCCESS'`, `target_address` = ALAMAT_BLOCKCHAIN_DOKTER_X, dan IP address pemanggil.
*   **Tindakan 2: Pasien A coba memberikan akses RM_B1 (milik Pasien B) ke Dokter Y**
    1.  Login sebagai Pasien A (dapatkan token).
    2.  Panggil API `POST /api/v1/medical-records/{RM_B1_ID}/grant-access` dengan token Pasien A dan payload `{"doctor_address": "ALAMAT_BLOCKCHAIN_DOKTER_Y"}`.
*   **Hasil yang Diharapkan 2:**
    *   Respons gagal (403 Forbidden).
    *   Cek tabel `audit_data_access_logs`: Entri baru dengan `actor_user_id` = ID Pasien A, `owner_user_id` = ID Pasien A (karena Pasien A adalah aktornya, owner_user_id di sini juga ID Pasien A, bukan Pasien B, karena audit log mencatat aksi dari `current_user`), `record_id` = RM_B1_ID, `action_type` = `'GRANT_ACCESS_FAILURE_FORBIDDEN'`.

### 3. Verifikasi Log Audit untuk `revoke_medical_record_access` (Test Case 4.2.5)

*   **Persiapan:**
    *   Pasien A memiliki rekam medis (RM_A2) yang aksesnya sudah diberikan ke Dokter X.
*   **Tindakan: Pasien A mencabut akses RM_A2 dari Dokter X**
    1.  Login sebagai Pasien A (dapatkan token).
    2.  Panggil API `POST /api/v1/medical-records/{RM_A2_ID}/revoke-access` dengan token Pasien A dan payload `{"doctor_address": "ALAMAT_BLOCKCHAIN_DOKTER_X"}`.
*   **Hasil yang Diharapkan:**
    *   Respons sukses (200 OK).
    *   Cek tabel `audit_data_access_logs`: Entri baru dengan `actor_user_id` = ID Pasien A, `owner_user_id` = ID Pasien A, `record_id` = RM_A2_ID, `action_type` = `'REVOKE_ACCESS_SUCCESS'`, `target_address` = ALAMAT_BLOCKCHAIN_DOKTER_X, dan IP address pemanggil.

### 4. Verifikasi API Riwayat Akses Pasien (Test Case 4.2.6)

*   **Persiapan:**
    *   Pasien A sudah melakukan beberapa aksi yang menghasilkan log audit (misalnya, dari tes 1, 2, dan 3 di atas).
*   **Tindakan:**
    1.  Login sebagai Pasien A (dapatkan token).
    2.  Panggil API `GET /api/v1/audit/my-record-access-history` dengan token Pasien A.
*   **Hasil yang Diharapkan:**
    *   Respons sukses (200 OK).
    *   Body respons berisi daftar (array) log audit.
    *   Setiap entri dalam daftar memiliki `owner_user_id` yang sama dengan ID Pasien A.
    *   Verifikasi bahwa log-log yang relevan dari aksi-aksi sebelumnya (misalnya, `VIEW_RECORD_SUCCESS` oleh Pasien A sendiri, `VIEW_RECORD_SUCCESS` oleh Dokter X, `GRANT_ACCESS_SUCCESS` oleh Pasien A, `REVOKE_ACCESS_SUCCESS` oleh Pasien A) muncul dalam daftar dengan urutan timestamp terbaru di awal.
    *   Cek parameter `skip` dan `limit` untuk fungsionalitas paginasi.

---
Jika ada masalah atau hasil yang tidak sesuai harapan, catat langkah-langkahnya, hasil yang didapat, dan hasil yang diharapkan untuk dilaporkan.

## Deployment Smart Contract (MedicalRecordRegistry.sol) ke Ganache (Lokal)

Setelah melakukan modifikasi pada `MedicalRecordRegistry.sol` dan tes unitnya berhasil, langkah berikutnya adalah men-deploy ulang _smart contract_ tersebut ke jaringan Ganache lokal Anda.

1.  **Pastikan Ganache Berjalan:**
    *   Pastikan instance Ganache Anda sudah berjalan dan dikonfigurasi sesuai dengan `hardhat.config.js` (biasanya di `http://127.0.0.1:8545` atau `http://127.0.0.1:7545` dengan `chainId: 1337`).
    *   Anda bisa menjalankan Ganache dengan perintah (sesuaikan `dbPath` jika perlu):
        ```bash
        ganache --deterministic --chain.chainId 1337 --database.dbPath ./.ganache-db
        ```

2.  **Navigasi ke Direktori Blockchain:**
    *   Buka terminal Anda dan navigasi ke direktori `blockchain` di dalam proyek Anda:
        ```bash
        cd path/to/your/project/blockchain
        ```

3.  **Jalankan Skrip Deployment:**
    *   Gunakan Hardhat untuk menjalankan skrip deployment. Skrip ini biasanya berada di direktori `scripts/` (misalnya, `deployMedicalRecordRegistry.js`).
        ```bash
        npx hardhat run scripts/deployMedicalRecordRegistry.js --network ganache
        ```
    *   **Catatan:** Jika Anda menjalankan perintah dari direktori root proyek, path ke skrip mungkin perlu disesuaikan (misalnya `blockchain/scripts/...`). Namun, instruksi di atas mengasumsikan Anda berada di dalam direktori `blockchain`.

4.  **Verifikasi Deployment:**
    *   Setelah deployment berhasil, Hardhat akan mencetak alamat kontrak yang baru di-deploy ke konsol.
    *   Pastikan file ABI (Application Binary Interface) dan alamat kontrak yang baru telah diperbarui di direktori `blockchain/build/deployments/`. File-file ini (biasanya `MedicalRecordRegistry.json` yang berisi ABI dan alamat di jaringan tertentu) sangat penting karena backend (`src/app/core/config.py`) akan membaca informasi ini untuk berinteraksi dengan kontrak.
    *   Jika `config.py` membaca dari path seperti `blockchain/build/deployments/ganache/MedicalRecordRegistry.json`, pastikan file tersebut ter-update dengan timestamp dan alamat terbaru.

5.  **Restart Backend Server (Jika Perlu):**
    *   Jika backend server Anda sudah berjalan, restart server tersebut agar ia memuat konfigurasi _smart contract_ yang baru (ABI dan alamat).
