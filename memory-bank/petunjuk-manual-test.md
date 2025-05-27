# Petunjuk Manual Test untuk Frontend Patient Portal

Dokumen ini berisi langkah-langkah untuk melakukan tes manual pada fungsionalitas dasar Patient Portal frontend.

## Prerequisites (Persiapan Awal):

1.  **Backend Server Berjalan:**
    *   Pastikan server backend FastAPI sudah berjalan. Biasanya dijalankan dengan perintah seperti `python -m app.main` dari dalam direktori `src/`.
    *   Verifikasi backend dapat diakses, misalnya di `http://localhost:8000/docs`.

2.  **Frontend Development Server Berjalan:**
    *   Pastikan server development frontend Vite sudah berjalan.
    *   Masuk ke direktori `frontend` (`cd frontend`).
    *   Jalankan dengan perintah `npm run dev`.
    *   Frontend akan tersedia di `http://localhost:5173` (atau port lain jika 5173 sudah digunakan).

3.  **Data Pengguna (User):**
    *   Siapkan setidaknya satu akun pengguna yang sudah terdaftar di sistem. Anda bisa mendaftarkan pengguna baru melalui endpoint API backend (`POST /api/v1/auth/register`) menggunakan tools seperti Postman atau curl jika belum ada mekanisme registrasi di UI.
    *   Catat username dan password pengguna tersebut untuk login.

4.  **Data Rekam Medis (Opsional):**
    *   Untuk menguji tampilan daftar rekam medis di dashboard, pengguna yang login sebaiknya memiliki beberapa data rekam medis.
    *   Jika tidak ada, dashboard diharapkan menampilkan pesan "Anda belum memiliki rekam medis" atau sejenisnya. Anda bisa membuat rekam medis melalui endpoint API backend (`POST /api/v1/medical-records`) atas nama pengguna yang akan login.

## Test Cases:

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
    *   (Opsional) Jika menggunakan Redux DevTools: _action_ `auth/loginStart` diikuti `auth/loginFailure` akan ter-dispatch. State `auth.isAuthenticated` harus `false`.

### 3. Login dengan Kredensial Valid

*   **Tindakan:**
    1.  Di halaman login, masukkan username/email dan password yang benar untuk pengguna yang sudah terdaftar.
    2.  Klik tombol "Login".
*   **Hasil yang Diharapkan:**
    *   Anda akan diarahkan ke halaman `/dashboard`.
    *   Buka Developer Tools > Application > Local Storage: sebuah item `access_token` (atau nama serupa yang didefinisikan di `tokenManager.js`) harus ada dan berisi token JWT.
    *   (Opsional) Jika menggunakan Redux DevTools: _action_ `auth/loginStart` diikuti `auth/loginSuccess` akan ter-dispatch. State `auth.isAuthenticated` harus `true`, dan token tersimpan di state Redux.

### 4. Tampilan Halaman Dashboard (Setelah Login)

*   **Tindakan:**
    1.  Setelah berhasil login, Anda berada di halaman `/dashboard`.
*   **Hasil yang Diharapkan:**
    *   Sebuah pesan selamat datang ditampilkan (misalnya, "Selamat Datang di Dashboard Anda").
    *   Tombol "Logout" (atau "Keluar") terlihat.
    *   **Jika pengguna memiliki rekam medis:**
        *   Sebuah tabel atau daftar rekam medis akan ditampilkan.
        *   Kolom yang ada minimal: ID Rekam Medis, Tipe Rekam Medis, Tanggal Dibuat (terformat), Hash Data.
        *   Data yang ditampilkan harus sesuai dengan rekam medis milik pengguna yang login.
    *   **Jika pengguna tidak memiliki rekam medis:**
        *   Pesan seperti "Anda belum memiliki rekam medis" atau "Tidak ada data rekam medis" akan ditampilkan.
    *   **Jika data sedang dimuat (loading):**
        *   Indikator loading (misalnya, _spinner_ atau `CircularProgress`) akan terlihat sebelum data ditampilkan atau pesan "tidak ada data" muncul.
    *   Periksa _browser console_: tidak boleh ada error fatal.
    *   Periksa Developer Tools > Network: harus ada panggilan API yang berhasil ke endpoint `/api/v1/medical-records/patient/me` dengan status 200 OK.

### 5. Akses Rute Terproteksi (Dashboard)

*   **Tindakan (Ketika Belum Login):**
    1.  Pastikan Anda sudah logout atau buka _incognito window_ baru.
    2.  Coba akses langsung ke `http://localhost:5173/dashboard`.
*   **Hasil yang Diharapkan (Ketika Belum Login):**
    *   Anda akan secara otomatis diarahkan kembali ke halaman `/login`.

*   **Tindakan (Ketika Sudah Login):**
    1.  Login ke aplikasi sehingga Anda berada di halaman `/dashboard`.
    2.  Refresh halaman `/dashboard` (tekan F5 atau tombol refresh browser).
*   **Hasil yang Diharapkan (Ketika Sudah Login):**
    *   Anda tetap berada di halaman `/dashboard`.
    *   Data di dashboard (termasuk daftar rekam medis) akan dimuat ulang dengan benar. State Redux (jika dicek dengan Redux DevTools) akan terhidrasi kembali berdasarkan token yang ada di `localStorage`.

### 6. Fungsionalitas Logout

*   **Tindakan:**
    1.  Pastikan Anda sedang login dan berada di halaman `/dashboard`.
    2.  Klik tombol "Logout".
*   **Hasil yang Diharapkan:**
    *   Anda akan diarahkan kembali ke halaman `/login`.
    *   Buka Developer Tools > Application > Local Storage: item `access_token` harus sudah terhapus.
    *   (Opsional) Jika menggunakan Redux DevTools: _action_ `auth/logout` akan ter-dispatch. State `auth.isAuthenticated` menjadi `false`, dan `auth.token` menjadi `null`.
    *   Mencoba mengakses `http://localhost:5173/dashboard` secara langsung setelah logout akan mengarahkan Anda kembali ke `/login`.

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
