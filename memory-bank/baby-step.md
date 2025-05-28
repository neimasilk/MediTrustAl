# Baby Steps: Implementasi Frontend Mockup-01 (Login) & Mockup-02 (Registrasi)

Dokumen ini berisi panduan langkah demi langkah (baby steps) untuk mengimplementasikan fungsionalitas frontend berdasarkan Mockup-01 (Halaman Login) dan Mockup-02 (Halaman Registrasi). Tujuannya adalah untuk menghilangkan ambiguitas dan mempermudah developer (terutama junior) dalam proses pengembangan.

**Referensi Utama:**
*   `frontend/mockups/mockup-01-login.html`
*   `frontend/mockups/mockup-02-register.html`
*   `memory-bank/outline-mockup.md` (untuk spesifikasi detail jika ada)
*   `src/app/api/v1/endpoints/auth.py` (untuk detail endpoint API Login & Registrasi)
*   `frontend/src/services/api.js` (atau file serupa untuk interaksi API di frontend)
*   `frontend/src/store/authSlice.js` (atau file serupa untuk manajemen state autentikasi)

## A. Persiapan Umum Frontend

Sebelum memulai implementasi spesifik untuk Login dan Registrasi, pastikan hal berikut sudah ada atau dibuat jika belum:

1.  **Struktur Direktori Komponen & Halaman:**
    *   Pastikan ada direktori `frontend/src/pages` untuk komponen halaman (e.g., `LoginPage.jsx`, `RegisterPage.jsx`).
    *   Pastikan ada direktori `frontend/src/components` untuk komponen UI yang reusable (e.g., `InputField.jsx`, `Button.jsx`, `Notification.jsx`).

2.  **Routing:**
    *   Konfigurasi routing dasar menggunakan `react-router-dom`.
    *   Buat rute untuk `/login` yang mengarah ke `LoginPage`.
    *   Buat rute untuk `/register` yang mengarah ke `RegisterPage`.
    *   Implementasikan `PublicRoute` yang mengarahkan pengguna yang sudah login dari `/login` dan `/register` ke `/dashboard`.
    *   Implementasikan `PrivateRoute` yang mengarahkan pengguna yang belum login dari rute terproteksi (e.g., `/dashboard`) ke `/login`.

3.  **Layanan API (API Service):**
    *   Buat atau pastikan ada file `frontend/src/services/api.js` (atau nama serupa) yang berisi fungsi untuk melakukan request ke backend.
    *   Gunakan `axios` atau `fetch` API.
    *   Konfigurasi base URL untuk API backend (e.g., `http://localhost:8000/api/v1`).
    *   Implementasikan fungsi `loginUser(credentials)` yang melakukan `POST` request ke `/auth/token`.
    *   Implementasikan fungsi `registerUser(userData)` yang melakukan `POST` request ke `/auth/register`.
    *   Sertakan error handling yang baik untuk menangkap respons error dari API.

4.  **Manajemen State (State Management):**
    *   Gunakan Redux Toolkit (atau Context API jika proyek lebih kecil dan disepakati).
    *   Buat `authSlice` yang akan menangani state terkait autentikasi:
        *   `user`: null atau objek user jika login.
        *   `token`: null atau token JWT jika login.
        *   `isLoading`: boolean (untuk indikator loading saat proses login/register).
        *   `error`: null atau pesan error jika terjadi kesalahan.
    *   Buat _reducers_ dan _actions_ untuk:
        *   `loginStart`, `loginSuccess`, `loginFailure`
        *   `registerStart`, `registerSuccess`, `registerFailure`
        *   `logout`
    *   Implementasikan _thunks_ (jika menggunakan Redux Toolkit) untuk menghandle logika asynchronous login dan registrasi yang memanggil fungsi dari `api.js` dan men-dispatch actions yang sesuai.

5.  **Utilitas Token:**
    *   Buat file utilitas (misalnya `frontend/src/utils/tokenManager.js`) untuk menyimpan dan mengambil token JWT dari `localStorage`.
    *   Fungsi: `saveToken(token)`, `getToken()`, `removeToken()`.
    *   Pastikan `axios` (atau `fetch`) instance dikonfigurasi untuk menyertakan token JWT di header `Authorization` untuk request yang memerlukan autentikasi.

6.  **Komponen UI Dasar (Reusable Components):**
    *   Buat komponen dasar jika belum ada:
        *   `InputField.jsx`: Komponen input generik dengan props untuk `type`, `placeholder`, `value`, `onChange`, `label`, `error`.
        *   `Button.jsx`: Komponen tombol generik dengan props untuk `text`, `onClick`, `type` (`submit`, `button`), `disabled`, `variant` (primary, secondary, etc.).
        *   `Notification.jsx`: Komponen untuk menampilkan pesan notifikasi (sukses, error, warning). Bisa menggunakan library seperti `react-toastify` atau buat custom.
        *   `LoadingSpinner.jsx`: Komponen untuk indikator loading.

## B. Implementasi Mockup-01: Halaman Login (`LoginPage.jsx`)

**Tujuan:** Membuat halaman login yang memungkinkan pengguna memasukkan username/email dan password, mengirimkannya ke backend, dan menangani respons.

**File Target:** `frontend/src/pages/LoginPage.jsx`

**Langkah-langkah:**

1.  **Struktur Komponen `LoginPage.jsx`:**
    *   Import React, `useState`, `useDispatch`, `useSelector` (dari `react-redux`), `Link` (dari `react-router-dom`), dan _thunk_ login dari `authSlice`.
    *   Import komponen UI yang dibutuhkan (`InputField`, `Button`, `Notification`, `LoadingSpinner`).
    *   Buat state lokal menggunakan `useState` untuk field input:
        *   `usernameOrEmail`
        *   `password`
    *   Gunakan `useDispatch` untuk mendapatkan fungsi `dispatch`.
    *   Gunakan `useSelector` untuk mendapatkan state `isLoading` dan `error` dari `authSlice`.

2.  **Layout dan Styling (JSX & CSS):**
    *   Replikasi tampilan dari `mockup-01-login.html`.
    *   Gunakan CSS Modules atau styled-components untuk styling (sesuai konvensi proyek).
    *   Pastikan halaman responsif.
    *   Struktur dasar JSX:
        ```jsx
        <div className="login-container">
          <h2>Login Akun</h2>
          <form onSubmit={handleSubmit}>
            <InputField
              label="Username atau Email"
              type="text" // atau email jika backend hanya menerima email untuk login
              value={usernameOrEmail}
              onChange={(e) => setUsernameOrEmail(e.target.value)}
              // Tambahkan error handling jika ada
            />
            <InputField
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              // Tambahkan error handling jika ada
            />
            {error && <Notification type="error" message={error} />}
            <Button type="submit" text="Login" disabled={isLoading} />
            {isLoading && <LoadingSpinner />}
          </form>
          <p>Belum punya akun? <Link to="/register">Daftar di sini</Link></p>
        </div>
        ```

3.  **Logika Handle Submit (`handleSubmit`):**
    *   Buat fungsi `handleSubmit` yang akan dipanggil saat form di-submit.
    *   Panggil `event.preventDefault()`.
    *   Lakukan validasi input dasar di sisi frontend (opsional, karena backend juga melakukan validasi, tapi baik untuk UX):
        *   Pastikan `usernameOrEmail` dan `password` tidak kosong.
        *   Jika ada error validasi, tampilkan pesan menggunakan komponen `Notification` atau state error lokal.
    *   Jika validasi lolos, dispatch _thunk_ login dengan `usernameOrEmail` dan `password` sebagai argumen:
        ```javascript
        dispatch(loginUserThunk({ username: usernameOrEmail, password })); 
        // Sesuaikan payload dengan yang diharapkan backend /auth/token (biasanya form data: username & password)
        ```

4.  **Menangani Hasil Login:**
    *   `authSlice` akan menangani respons dari API.
    *   Jika login sukses (`loginSuccess` di-dispatch):
        *   Token dan data user akan disimpan di Redux state.
        *   Token akan disimpan di `localStorage` (dilakukan di dalam _thunk_ atau _reducer_).
        *   Pengguna akan diarahkan ke `/dashboard`. Gunakan `useNavigate` dari `react-router-dom` atau lakukan ini di dalam _thunk_ setelah sukses.
    *   Jika login gagal (`loginFailure` di-dispatch):
        *   Pesan error dari backend akan disimpan di Redux state (`error`).
        *   Komponen `Notification` akan menampilkan pesan error tersebut.

5.  **Indikator Loading:**
    *   Tombol "Login" harus di-disable saat `isLoading` adalah `true`.
    *   Tampilkan komponen `LoadingSpinner` saat `isLoading` adalah `true`.

6.  **Link ke Halaman Registrasi:**
    *   Pastikan ada link yang mengarah ke `/register` untuk pengguna yang belum memiliki akun.

7.  **Pengujian Manual Awal:**
    *   Jalankan frontend dan backend.
    *   Coba login dengan kredensial salah, pastikan pesan error muncul.
    *   Coba login dengan kredensial benar, pastikan diarahkan ke dashboard (jika sudah ada) atau halaman lain yang sesuai.
    *   Periksa `localStorage` untuk token JWT setelah login berhasil.
    *   Periksa Redux DevTools untuk melihat perubahan state.

## C. Implementasi Mockup-02: Halaman Registrasi (`RegisterPage.jsx`)

**Tujuan:** Membuat halaman registrasi yang memungkinkan pengguna baru mendaftar dengan mengisi data yang diperlukan, mengirimkannya ke backend, dan menangani respons.

**File Target:** `frontend/src/pages/RegisterPage.jsx`

**Langkah-langkah:**

1.  **Struktur Komponen `RegisterPage.jsx`:**
    *   Mirip dengan `LoginPage.jsx`: import React, hooks, actions, komponen UI.
    *   State lokal untuk field input registrasi (sesuaikan dengan `UserCreate` schema di backend `src/app/schemas/user.py` dan `mockup-02-register.html`):
        *   `email`
        *   `username`
        *   `full_name`
        *   `password`
        *   `confirmPassword` (untuk validasi di frontend)
        *   `role` (jika bisa dipilih pengguna, default ke 'patient')
        *   `blockchain_address` (opsional saat registrasi, atau auto-generate jika desainnya begitu)
    *   Gunakan `useSelector` untuk `isLoading` dan `error` dari `authSlice`.

2.  **Layout dan Styling (JSX & CSS):**
    *   Replikasi tampilan dari `mockup-02-register.html`.
    *   Pastikan halaman responsif.
    *   Struktur dasar JSX (contoh, sesuaikan fieldnya):
        ```jsx
        <div className="register-container">
          <h2>Buat Akun Baru</h2>
          <form onSubmit={handleSubmit}>
            <InputField label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <InputField label="Username" type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
            <InputField label="Nama Lengkap" type="text" value={full_name} onChange={(e) => setFullName(e.target.value)} />
            <InputField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <InputField label="Konfirmasi Password" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
            {/* Tambahkan field lain jika ada, misal Role, Blockchain Address */} 
            {error && <Notification type="error" message={error} />}
            <Button type="submit" text="Daftar" disabled={isLoading} />
            {isLoading && <LoadingSpinner />}
          </form>
          <p>Sudah punya akun? <Link to="/login">Login di sini</Link></p>
        </div>
        ```

3.  **Logika Handle Submit (`handleSubmit`):**
    *   Buat fungsi `handleSubmit`.
    *   Panggil `event.preventDefault()`.
    *   Lakukan validasi input di sisi frontend:
        *   Semua field wajib diisi (kecuali yang opsional).
        *   Format email valid.
        *   Password dan `confirmPassword` harus cocok.
        *   Panjang minimal password (jika ada aturan).
        *   Jika ada error validasi, tampilkan pesan.
    *   Jika validasi lolos, buat objek `userData` yang akan dikirim ke backend (sesuai schema `UserCreate`):
        ```javascript
        const userData = { email, username, full_name, password, role: 'patient' /*, blockchain_address */ };
        ```
    *   Dispatch _thunk_ registrasi:
        ```javascript
        dispatch(registerUserThunk(userData));
        ```

4.  **Menangani Hasil Registrasi:**
    *   `authSlice` akan menangani respons dari API.
    *   Jika registrasi sukses (`registerSuccess` di-dispatch):
        *   Tampilkan pesan sukses (misalnya, "Registrasi berhasil! Silakan login.").
        *   Arahkan pengguna ke halaman `/login` (atau otomatis login jika desainnya begitu, tapi umumnya ke login dulu).
    *   Jika registrasi gagal (`registerFailure` di-dispatch):
        *   Pesan error dari backend (misalnya, "Username sudah ada", "Email sudah terdaftar") akan disimpan di Redux state (`error`).
        *   Komponen `Notification` akan menampilkan pesan error tersebut.

5.  **Indikator Loading:**
    *   Sama seperti di `LoginPage.jsx`.

6.  **Link ke Halaman Login:**
    *   Pastikan ada link yang mengarah ke `/login` untuk pengguna yang sudah memiliki akun.

7.  **Pengujian Manual Awal:**
    *   Jalankan frontend dan backend.
    *   Coba registrasi dengan data valid. Pastikan sukses dan diarahkan ke login.
    *   Coba registrasi dengan username atau email yang sudah ada. Pastikan pesan error yang sesuai muncul.
    *   Coba registrasi dengan password dan konfirmasi password yang tidak cocok. Pastikan error validasi frontend muncul.
    *   Periksa database untuk memastikan user baru tersimpan dengan benar setelah registrasi sukses.
    *   Periksa Redux DevTools.

## D. Langkah Selanjutnya Setelah Implementasi Awal

1.  **Refinement & Styling Lanjutan:**
    *   Pastikan styling benar-benar sesuai dengan mockup HTML.
    *   Perhatikan detail UX seperti pesan error yang jelas, feedback saat interaksi.

2.  **Error Handling Lebih Detail:**
    *   Tangani berbagai jenis error dari backend (400, 401, 403, 409, 500) dengan pesan yang lebih spesifik jika memungkinkan.

3.  **Integrasi dengan Komponen Lain:**
    *   Pastikan alur navigasi setelah login/registrasi berjalan lancar ke halaman dashboard atau halaman lain yang relevan.

4.  **Penulisan Unit Test (jika sudah masuk tahap itu):**
    *   Tulis unit test untuk komponen `LoginPage` dan `RegisterPage`.
    *   Tulis unit test untuk `authSlice` (reducers, actions, thunks).

5.  **Review dan Iterasi:**
    *   Lakukan review kode.
    *   Uji kembali secara manual untuk memastikan semua skenario tertangani dengan baik.

Dengan mengikuti langkah-langkah ini, implementasi halaman Login dan Registrasi diharapkan menjadi lebih terstruktur dan minim ambiguitas.