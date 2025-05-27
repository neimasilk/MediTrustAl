# Baby Step 3.3: Basic Frontend Shell (Patient Portal)

## Tujuan:

Membuat dasar aplikasi frontend (Patient Portal) yang memungkinkan pengguna untuk login dan melihat daftar metadata rekam medis mereka. Ini akan menjadi fondasi untuk fitur frontend yang lebih kompleks di masa depan.

## Konteks & Referensi:

* **Implementation Plan:** Step 3.3 [cite: neimasilk/meditrustal/MediTrustAl-89c6d316f7c5903d37d5ea9f11f6097be78f16d8/memory-bank/implementation-plan.md]
* **Tech Stack Document:** Frontend menggunakan React.js, UI Framework: Material-UI (MUI), State Management: Redux Toolkit. [cite: neimasilk/meditrustal/MediTrustAl-89c6d316f7c5903d37d5ea9f11f6097be78f16d8/memory-bank/tech-stack.md]
* **Coding Rules:** Patuhi aturan modularitas dan penamaan. [cite: neimasilk/meditrustal/MediTrustAl-89c6d316f7c5903d37d5ea9f11f6097be78f16d8/memory-bank/coding-rules.md]
* **Backend API Endpoints yang akan digunakan:**
    * `POST /api/v1/auth/login` (untuk login) [cite: neimasilk/meditrustal/MediTrustAl-89c6d316f7c5903d37d5ea9f11f6097be78f16d8/src/app/api/endpoints/auth.py]
    * `GET /api/v1/medical-records/patient/me` (untuk mengambil daftar rekam medis) [cite: neimasilk/meditrustal/MediTrustAl-89c6d316f7c5903d37d5ea9f11f6097be78f16d8/src/app/api/endpoints/medical_records.py]
    * (Opsional) `GET /api/v1/medical-records/{record_id}` (untuk detail rekam medis) [cite: neimasilk/meditrustal/MediTrustAl-89c6d316f7c5903d37d5ea9f11f6097be78f16d8/src/app/api/endpoints/medical_records.py]

## Instruksi Implementasi:

### 1. Setup Proyek Frontend

* **Tindakan:**
    1.  Buat direktori baru bernama `frontend` di root repositori proyek MediTrustAl.
    2.  Di dalam direktori `frontend`, inisialisasi proyek React.js baru menggunakan `create-react-app` atau Vite (Vite direkomendasikan untuk setup yang lebih cepat dan modern jika belum ada preferensi kuat).
        ```bash
        # Contoh dengan Vite:
        # Navigasi ke root direktori proyek Anda jika belum
        # cd /path/to/your/MediTrustAl
        mkdir frontend
        cd frontend
        npm create vite@latest . -- --template react # atau yarn create vite . --template react
        npm install # atau yarn install
        ```
    3.  Instal dependensi yang dibutuhkan:
        * `axios` (untuk HTTP requests)
        * `react-router-dom` (untuk routing)
        * `@mui/material @emotion/react @emotion/styled` (untuk Material-UI)
        * `@reduxjs/toolkit react-redux` (untuk Redux state management)
        ```bash
        npm install axios react-router-dom @mui/material @emotion/react @emotion/styled @reduxjs/toolkit react-redux
        # atau
        yarn add axios react-router-dom @mui/material @emotion/react @emotion/styled @reduxjs/toolkit react-redux
        ```
    4.  Konfigurasi dasar untuk ESLint dan Prettier (opsional, tapi direkomendasikan sesuai `development-environment-notes.md`). [cite: neimasilk/meditrustal/MediTrustAl-89c6d316f7c5903d37d5ea9f11f6097be78f16d8/memory-bank/development-environment-notes.md]
    5.  Struktur folder dasar dalam `frontend/src/`:
        ```
        frontend/
        ├── public/
        ├── src/
        │   ├── App.jsx                 # Komponen utama aplikasi (atau .js)
        │   ├── main.jsx               # Entry point React (atau index.js jika CRA)
        │   ├── components/            # Komponen UI yang dapat digunakan kembali
        │   │   ├── layout/            # Komponen layout (misal: Navbar, Sidebar)
        │   │   └── ui/                # Komponen UI atomik (misal: CustomButton, InputField)
        │   ├── pages/                 # Komponen halaman (LoginPage.jsx, DashboardPage.jsx)
        │   ├── services/              # Logika untuk interaksi API (misal: authService.js, medicalRecordService.js)
        │   ├── store/                 # Konfigurasi Redux
        │   │   ├── slices/            # Slice Redux (misal: authSlice.js)
        │   │   └── store.js           # Konfigurasi store Redux
        │   ├── utils/                 # Fungsi utilitas (misal: tokenManager.js, privateRoute.js)
        │   └── App.css / index.css    # Styling global
        └── package.json
        ```
* **Verifikasi:**
    * Proyek frontend berhasil dibuat dan dapat dijalankan (misalnya `npm run dev` atau `yarn dev` dari dalam direktori `frontend`). Aplikasi React default akan muncul di browser.
    * Dependensi berhasil diinstal tanpa error (cek `package.json` dan `node_modules`).
    * Struktur folder dasar telah dibuat di dalam `frontend/src/`.

### 2. Implementasi Halaman Login

* **Tindakan:**
    1.  Buat file `LoginPage.jsx` di `frontend/src/pages/`.
    2.  Gunakan komponen Material-UI (`Container`, `Box`, `Typography`, `TextField`, `Button`) untuk membuat form login.
        * Form harus memiliki input untuk "Username or Email" dan "Password".
        * Form harus memiliki tombol "Login".
    3.  Buat file `authService.js` di `frontend/src/services/`.
        * Implementasikan fungsi `loginUser(credentials)` yang menerima objek `credentials` (berisi `username_or_email` dan `password`).
        * Fungsi ini menggunakan `axios.post` untuk mengirim data ke endpoint backend `POST /api/v1/auth/login/json`.
        * Pastikan URL backend benar (misalnya, `http://localhost:8000/api/v1/auth/login/json`).
    4.  Di `LoginPage.jsx`:
        * Gunakan `useState` untuk mengelola state input form (`usernameOrEmail`, `password`) dan state untuk pesan error atau loading.
        * Ketika tombol "Login" ditekan:
            * Panggil `authService.loginUser()` dengan data dari form.
            * Jika login berhasil (respons 200 OK dan ada `access_token`):
                * Simpan `access_token` ke `localStorage` (buat fungsi helper di `frontend/src/utils/tokenManager.js` untuk `saveToken`, `getToken`, `removeToken`).
                * *Untuk Redux (akan diintegrasikan lebih lanjut di Langkah 3):* Dispatch action untuk menyimpan token dan status autentikasi.
                * Redirect pengguna ke halaman Dashboard (misalnya `/dashboard`) menggunakan `useNavigate` dari `react-router-dom`.
            * Jika login gagal:
                * Tampilkan pesan error yang diterima dari backend atau pesan generik (misalnya, "Login Gagal. Periksa kembali username/email dan password Anda.").
    5.  Buat file `AppRouter.jsx` (atau modifikasi `App.jsx`) untuk mengatur routing dasar menggunakan `react-router-dom`.
        * Definisikan rute untuk `/login` yang me-render `LoginPage`.
        * Definisikan rute untuk `/dashboard` (akan diproteksi nanti).
* **Verifikasi:**
    * Halaman login (`/login`) dapat diakses dan menampilkan form dengan benar.
    * Pengguna dapat mengetik di input fields.
    * Mengklik tombol "Login" dengan kredensial valid (setelah backend berjalan dan pengguna terdaftar) akan:
        * Mengirim request ke backend.
        * Menyimpan token di `localStorage`.
        * Mengarahkan pengguna ke rute `/dashboard`.
    * Mengklik tombol "Login" dengan kredensial tidak valid akan menampilkan pesan error.
    * Cek _network tab_ di _developer tools_ browser untuk memastikan API call ke backend benar.

### 3. Pengaturan State Management (Redux Toolkit) dan Protected Routes

* **Tindakan:**
    1.  Buat file `store.js` di `frontend/src/store/` untuk mengkonfigurasi Redux store menggunakan `configureStore` dari `@reduxjs/toolkit`.
    2.  Buat file `authSlice.js` di `frontend/src/store/slices/`.
        * Definisikan `initialState` dengan `isAuthenticated: false`, `token: null`, `user: null`, `error: null`, `isLoading: false`.
        * Buat _slice_ dengan `name: 'auth'`.
        * Definisikan _reducers_ untuk:
            * `loginStart`: set `isLoading` ke `true`, `error` ke `null`.
            * `loginSuccess`: set `isLoading` ke `false`, `isAuthenticated` ke `true`, `token` dari payload, `user` dari payload (jika ada, atau bisa di-fetch terpisah).
            * `loginFailure`: set `isLoading` ke `false`, `error` dari payload, `token` dan `user` ke `null`, `isAuthenticated` ke `false`.
            * `logout`: reset state ke `initialState` (atau set `isAuthenticated: false`, `token: null`, `user: null`).
        * Ekspor _actions_ dan _reducer_.
    3.  Update `frontend/src/main.jsx` (atau `index.js`) untuk membungkus komponen `<App />` dengan `<Provider store={store}>` dari `react-redux`.
    4.  Update `LoginPage.jsx`:
        * Gunakan `useDispatch` untuk dispatch actions `loginStart`, `loginSuccess`, `loginFailure`.
        * Gunakan `useSelector` untuk mendapatkan `isLoading` dan `error` dari state `auth` untuk menampilkan UI yang sesuai (misalnya, _loading spinner_, pesan error).
        * Pada login sukses, selain menyimpan token ke `localStorage`, dispatch `loginSuccess` dengan token.
    5.  Buat komponen `PrivateRoute.jsx` di `frontend/src/utils/` (atau `frontend/src/routes/`).
        * Komponen ini akan menerima `children` sebagai prop.
        * Gunakan `useSelector` untuk mendapatkan `isAuthenticated` dari `authSlice`.
        * Jika `isAuthenticated` true, render `{children}`.
        * Jika `isAuthenticated` false, redirect ke `/login` menggunakan `<Navigate to="/login" />` dari `react-router-dom`.
    6.  Update routing di `AppRouter.jsx` (atau `App.jsx`):
        * Bungkus rute `/dashboard` dengan `<PrivateRoute>`.
* **Verifikasi:**
    * Aplikasi berjalan tanpa error Redux.
    * State `auth` di Redux DevTools berubah sesuai dengan actions yang di-dispatch (login start, success, failure, logout).
    * Mencoba mengakses `/dashboard` secara langsung tanpa login akan dialihkan ke `/login`.
    * Setelah login berhasil, `/dashboard` dapat diakses.

### 4. Implementasi Halaman Dashboard Dasar

* **Tindakan:**
    1.  Buat file `DashboardPage.jsx` di `frontend/src/pages/`.
    2.  Di `DashboardPage.jsx`:
        * Tampilkan pesan selamat datang, misalnya "Selamat Datang, [Username Pengguna]!" (Username bisa diambil dari state Redux jika sudah disimpan saat login, atau dari `/users/me` nanti).
        * Tambahkan tombol "Logout" (Material-UI `Button`).
            * `onClick` tombol ini akan:
                * Dispatch action `logout()` dari `authSlice`.
                * Panggil fungsi dari `tokenManager.js` untuk menghapus token dari `localStorage`.
                * Redirect ke `/login` menggunakan `useNavigate`.
    3.  Buat file `medicalRecordService.js` di `frontend/src/services/`.
        * Implementasikan fungsi `getMyMedicalRecords()`:
            * Ambil token dari `localStorage` (menggunakan `tokenManager.js`) atau dari Redux state.
            * Kirim permintaan `GET` ke `/api/v1/medical-records/patient/me` menggunakan `axios`.
            * Sertakan token dalam header `Authorization: Bearer {token}`.
            * Kembalikan data rekam medis jika sukses, atau tangani error.
    4.  Di `DashboardPage.jsx`:
        * Gunakan `useEffect` untuk memanggil `medicalRecordService.getMyMedicalRecords()` ketika komponen dimuat.
        * Simpan daftar rekam medis yang diterima ke dalam state lokal komponen (`useState([])`) atau buat `medicalRecordsSlice.js` dan kelola di Redux.
        * Tampilkan daftar rekam medis menggunakan komponen Material-UI seperti `Table`, `TableBody`, `TableCell`, `TableContainer`, `TableHead`, `TableRow`, `Paper`.
        * Kolom yang ditampilkan minimal: `id` (Record ID), `record_type`, `created_at` (format tanggal agar mudah dibaca), `data_hash`.
        * Jika tidak ada rekam medis, tampilkan pesan seperti "Anda belum memiliki rekam medis."
* **Verifikasi:**
    * Halaman Dashboard (`/dashboard`) dapat diakses setelah login.
    * Pesan selamat datang (statis untuk saat ini) ditampilkan.
    * Tombol "Logout" berfungsi: menghapus token, mereset state auth di Redux, dan mengarahkan ke halaman login.
    * Saat Dashboard dimuat, API call ke `/api/v1/medical-records/patient/me` dilakukan dengan token yang benar.
    * Data rekam medis (atau pesan "tidak ada rekam medis") ditampilkan dengan benar dalam format tabel/daftar.
    * Pastikan backend FastAPI memiliki CORS yang dikonfigurasi untuk memperbolehkan request dari origin frontend (misalnya, `http://localhost:5173` jika menggunakan Vite default).
        * Contoh di `src/app/main.py`:
          ```python
          from fastapi.middleware.cors import CORSMiddleware

          origins = [
              "http://localhost:3000", # Jika frontend React default CRA
              "http://localhost:5173", # Jika frontend Vite default
              # Tambahkan origin lain jika perlu
          ]

          app.add_middleware(
              CORSMiddleware,
              allow_origins=origins,
              allow_credentials=True,
              allow_methods=["*"],
              allow_headers=["*"],
          )
          ```

### 5. (Opsional untuk MVP Awal) Menampilkan Detail Rekam Medis

* **Tindakan:**
    1.  Pada setiap baris tabel rekam medis di `DashboardPage.jsx`, tambahkan `Button` atau `IconButton` (misalnya, dengan ikon "View" atau "Details") dari Material-UI.
    2.  Ketika tombol ini diklik:
        * Navigasikan ke rute baru, misalnya `/records/:recordId` (menggunakan `useNavigate` dan meneruskan `record.id`).
    3.  Buat komponen `MedicalRecordDetailPage.jsx` di `frontend/src/pages/`.
        * Ambil `recordId` dari parameter URL menggunakan `useParams` dari `react-router-dom`.
    4.  Di `medicalRecordService.js`, tambahkan fungsi `getMedicalRecordDetail(recordId)`:
        * Ambil token.
        * Kirim permintaan `GET` ke `/api/v1/medical-records/{recordId}`.
        * Sertakan token di header.
    5.  Di `MedicalRecordDetailPage.jsx`:
        * Gunakan `useEffect` untuk memanggil `medicalRecordService.getMedicalRecordDetail(recordId)` saat komponen dimuat.
        * Simpan detail rekam medis (termasuk `raw_data`) ke state lokal.
        * Tampilkan informasi detail rekam medis, termasuk `raw_data` (misalnya, dalam `<pre>` tag atau `Typography`).
    6.  Tambahkan rute untuk `/records/:recordId` di `AppRouter.jsx` (atau `App.jsx`), pastikan juga diproteksi oleh `PrivateRoute`.
* **Verifikasi:**
    * Tombol/link "Lihat Detail" muncul untuk setiap rekam medis di dashboard.
    * Mengklik tombol tersebut mengarahkan ke halaman detail dengan URL yang benar (misalnya, `/records/uuid-rekam-medis`).
    * Halaman detail melakukan API call ke `/api/v1/medical-records/{recordId}`.
    * Detail rekam medis, terutama `raw_data`, ditampilkan dengan benar.

## Struktur Direktori Frontend yang Diharapkan (Contoh Akhir):



frontend/
├── node_modules/
├── public/
│ └── index.html
├── src/
│ ├── App.jsx
│ ├── App.css
│ ├── main.jsx
│ ├── index.css
│ ├── components/
│ │ ├── layout/
│ │ │ └── Navbar.jsx // (Opsional untuk MVP ini, bisa ditambahkan nanti)
│ │ └── ui/
│ │ ├── CustomButton.jsx // (Jika membuat komponen tombol kustom)
│ │ └── LoadingSpinner.jsx // (Komponen loading spinner)
│ ├── pages/
│ │ ├── LoginPage.jsx
│ │ ├── DashboardPage.jsx
│ │ └── MedicalRecordDetailPage.jsx // (Jika opsional diimplementasikan)
│ ├── services/
│ │ ├── authService.js
│ │ └── medicalRecordService.js
│ ├── store/
│ │ ├── slices/
│ │ │ └── authSlice.js
│ │ └── store.js
│ ├── utils/
│ │ ├── tokenManager.js
│ │ └── PrivateRoute.jsx
│ └── routes/ // (Atau routing bisa langsung di App.jsx)
│ └── AppRouter.jsx
├── .gitignore
├── package.json
└── vite.config.js // (Jika menggunakan Vite)
## Catatan Tambahan untuk Junior Developer:

* **Backend Berjalan:** Pastikan backend FastAPI MediTrustAl sudah berjalan dan dapat diakses dari browser atau Postman sebelum memulai frontend. Endpoint yang dibutuhkan adalah `/api/v1/auth/login/json` dan `/api/v1/medical-records/patient/me`.
* **CORS:** Pastikan backend FastAPI telah dikonfigurasi untuk mengizinkan permintaan dari origin tempat aplikasi frontend Anda berjalan (misalnya, `http://localhost:5173` untuk Vite default, atau `http://localhost:3000` untuk Create React App default).
* **Iterasi Kecil:** Kerjakan setiap sub-langkah satu per satu. Tes sering untuk memastikan setiap bagian berfungsi sebelum melanjutkan.
* **React DevTools & Redux DevTools:** Instal ekstensi browser ini untuk membantu debugging state React dan Redux.
* **Dokumentasi Material-UI:** Lihat dokumentasi resmi Material-UI ([https://mui.com/](https://mui.com/)) untuk contoh penggunaan komponen.
* **Error Handling:** Implementasikan penanganan error dasar untuk panggilan API (misalnya, menampilkan pesan error jika API gagal).
* **Styling:** Fokus pada fungsionalitas terlebih dahulu. Styling mendetail bisa dilakukan kemudian. Gunakan komponen Material-UI untuk tampilan awal yang rapi.
* **Modularitas:** Buat komponen sekecil mungkin dengan tanggung jawab tunggal.
* **Token Management:** `localStorage` cukup untuk MVP. Jika menggunakan Redux untuk token, pastikan sinkronisasi dengan `localStorage` jika ingin token tetap ada setelah refresh halaman (misalnya dengan `redux-persist` atau memuat dari `localStorage` saat aplikasi pertama kali dimuat).

Dengan mengikuti langkah-langkah ini, shell frontend dasar untuk Patient Portal dapat dibuat secara bertahap dan teruji.