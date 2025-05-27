Tentu, saya akan membantu Anda mereview dokumentasi di `./memory-bank` untuk mengidentifikasi potensi ketidakjelasan dan ambiguitas yang krusial. Memastikan dokumentasi selalu *up-to-date* dan jelas adalah praktik yang sangat baik.

Setelah melakukan peninjauan terhadap dokumen-dokumen yang Anda sediakan, berikut adalah beberapa area yang berpotensi menimbulkan ketidakjelasan atau ambiguitas, beserta analisisnya:

**Ambiguitas dan Potensi Ketidakjelasan Krusial:**

1.  **Konsistensi Istilah dan Detail Teknis antara Dokumen Perencanaan dan Implementasi:**
    * **Observasi:** Terdapat variasi dalam penyebutan beberapa komponen atau detail teknis antara dokumen perencanaan tingkat tinggi (seperti `product-design-document.md` atau `proposal-draft.md`) dengan dokumen yang lebih teknis (seperti `tech-stack.md`, `database-schema.md`, dan `implementation-plan.md`).
    * **Contoh Spesifik:**
        * **Penyimpanan Off-Chain:** `product-design-document.md` (Bagian 5) menyebutkan "Raw medical data stored off-chain (hospital servers/secure cloud)". `tech-stack.md` (Bagian 2.1) merekomendasikan "MinIO self-hosted" untuk MVP. Meskipun tidak bertentangan secara langsung, kejelasan apakah MinIO akan di-deploy di server rumah sakit atau cloud PIPL-compliant perlu ditegaskan sejak awal, terutama karena implikasi biaya dan infrastruktur.
        * **Blockchain untuk Produksi:** `tech-stack.md` (Bagian 2.1) menyebutkan "Hyperledger Fabric" untuk produksi, sedangkan `architecture.md` (Bagian Blockchain Architecture) juga menyebutkan "Hyperledger Fabric (Future)". `proposal-draft.md` (Bagian 4) menyebutkan "Likely a consortium or private permissioned blockchain". Meskipun Hyperledger Fabric adalah salah satu jenis permissioned blockchain, konsistensi penyebutan dan mungkin justifikasi lebih awal mengapa Fabric dipilih akan lebih baik.
        * **Peran `UserRegistry.sol` vs. Entitas Pengguna di Database:** `implementation-plan.md` (Step 1.2) menyebutkan `UserRegistry.sol` untuk "mendaftarkan entitas 'User' dengan DID unik, Peran, dan Timestamp registrasi". `database-schema.md` juga mendefinisikan tabel `users` dengan kolom `id`, `did`, `role`, dll.. Perlu diperjelas apakah `UserRegistry.sol` hanya mencatat *subset* informasi (misalnya, DID dan peran untuk validasi on-chain) sementara detail lengkap ada di database PostgreSQL, atau ada duplikasi data. Interaksi dan sumber kebenaran (source of truth) untuk setiap atribut pengguna (terutama peran) perlu sangat jelas.
    * **Potensi Masalah:** Ambiguitas ini dapat menyebabkan kebingungan selama implementasi, perbedaan interpretasi antar anggota tim (atau AI), dan potensi pengerjaan ulang.
    * **Rekomendasi:** Lakukan sinkronisasi istilah dan detail teknis. Pastikan dokumen perencanaan awal (seperti PRD) diperbarui atau merujuk secara eksplisit ke dokumen teknis untuk detail implementasi setelah keputusan teknis dibuat. Definisikan dengan jelas data apa yang ada *on-chain* vs. *off-chain* untuk setiap entitas.

2.  **Detail Interaksi Antar Layanan dan Alur Data Kritis:**
    * **Observasi:** `architecture.md` menyediakan diagram alur data tingkat tinggi (misalnya, Alur Otentikasi, Alur Rekam Medis). Namun, detail interaksi API antar layanan (misalnya, antara `Medical Records Service` dan `Blockchain Service`) dan format data yang dipertukarkan mungkin belum cukup terperinci untuk implementasi yang kompleks.
    * **Contoh Spesifik:**
        * Dalam `architecture.md` (Bagian Data Flow - Medical Record Flow), alurnya adalah "Client → API Gateway → Medical Records Service → Database (Encrypted Data) └→ Blockchain (Hash + Access Control)". Bagaimana `Medical Records Service` berinteraksi dengan `Blockchain Service` untuk mencatat hash dan mengelola kontrol akses? Apakah sinkron atau asinkron? Bagaimana kegagalan di salah satu langkah ditangani?
        * `implementation-plan.md` (Step 2.1) menyebutkan "placeholder 'Health Record' linked to a patient's DID" di blockchain, yang berisi "unique ID, a timestamp, and a field for a data hash". Di sisi lain, `database-schema.md` (Tabel medical\_records) memiliki `id` (UUID), `blockchain_record_id` (tx hash), dan `data_hash`. Bagaimana ID rekam medis di database berkorelasi dengan ID (jika ada) di struktur blockchain? Apakah `blockchain_record_id` di DB adalah ID unik dari entri blockchain, atau hash transaksi pencatatan? Dokumen `README.md` menyebutkan "Endpoint `/api/v1/medical-records/patient/me` ... bergantung pada `BlockchainService` yang mengembalikan hash rekam medis terkait DID pasien." Ini mengindikasikan blockchain menyimpan daftar hash per DID, yang sesuai dengan implementasi `MedicalRecordRegistry.sol` dan `getRecordHashesByPatient`. Kejelasan ini baik, namun perlu dipastikan konsisten di semua dokumen arsitektur.
    * **Potensi Masalah:** Kurangnya detail dapat menyebabkan kesulitan dalam merancang kontrak API internal, penanganan error yang tidak konsisten, dan masalah integrasi.
    * **Rekomendasi:** Pertimbangkan untuk membuat urutan diagram yang lebih detail atau spesifikasi API internal untuk alur data kritis. Ini bisa menjadi bagian dari `architecture.md` atau dokumen terpisah.

3.  **Strategi Pengelolaan Kunci Enkripsi:**
    * **Observasi:** `database-schema.md` menyebutkan "Encrypted FHIR R4 data (AES-256-GCM suggested)" dan `implementation-plan.md` (Step 2.2) juga menyebutkan AES-256-GCM. `src/app/api/endpoints/medical_records.py` memiliki fungsi `get_encryption_key` yang mengambil kunci dari `JWT_SECRET_KEY`.
    * **Ambiguitas/Potensi Masalah:**
        * Menggunakan `JWT_SECRET_KEY` untuk enkripsi data rekam medis adalah praktik yang **sangat tidak aman** untuk produksi dan bahkan berisiko untuk pengembangan jika tidak ditangani dengan hati-hati. JWT secret dimaksudkan untuk menandatangani token, bukan untuk enkripsi data simetris. Kompromi pada JWT secret akan mengkompromikan semua data terenkripsi.
        * Dokumen `status-todolist-suggestions.md` menyebutkan ini sebagai "[MITIGATED FOR MVP] Pengelolaan Kunci Enkripsi: Penggunaan JWT secret untuk kunci enkripsi (MVP)". Meskipun ditandai *mitigated for MVP*, ini adalah risiko keamanan yang signifikan dan perlu ada rencana yang jelas untuk solusi yang lebih aman sesegera mungkin, bahkan sebelum produksi penuh.
        * Strategi pengelolaan kunci (Key Management Strategy - KMS) yang sebenarnya (bagaimana kunci per pasien atau per rekam medis akan dibuat, disimpan, dirotasi, dan dicabut) belum terdefinisi dengan baik dalam dokumentasi arsitektur atau keamanan.
    * **Rekomendasi:**
        * **Segera (bahkan untuk MVP development lanjutan):** Hentikan penggunaan JWT secret untuk enkripsi data. Minimal, gunakan kunci enkripsi data (Data Encryption Key - DEK) yang terpisah dan disimpan secara aman di environment variable atau sistem konfigurasi.
        * **Jangka Panjang:** Definisikan strategi KMS yang kuat. Ini bisa melibatkan penggunaan *Key Derivation Function* (KDF) dari password pengguna (dengan salt yang tepat), penggunaan *Hardware Security Module* (HSM), atau layanan KMS cloud jika sesuai dengan batasan PIPL. Ini harus menjadi prioritas tinggi dalam `architecture.md` dan `tech-stack.md`.
        * Perjelas apakah enkripsi dilakukan per pasien, per rekam medis, atau menggunakan satu kunci sistem (yang terakhir kurang ideal).

4.  **Detail Implementasi NLP dan AI untuk MVP:**
    * **Observasi:** `implementation-plan.md` (Step 3.1 dan 3.2) menjelaskan pembuatan *placeholder* untuk layanan NLP dan AI. `product-design-document.md` (Bagian 4.2) dan `proposal-draft.md` (Bagian 4) menguraikan kemampuan NLP/AI yang lebih canggih.
    * **Ambiguitas/Potensi Masalah:**
        * Meskipun `implementation-plan.md` jelas tentang *placeholder* untuk MVP, dokumen lain mungkin memberi kesan bahwa kemampuan NLP/AI yang lebih canggih akan ada di MVP awal. `tech-stack.md` (Bagian 2.2) mendaftar banyak model dan *tool* NLP/AI canggih (BERT-Chinese-Medical, ClinicalBERT, BioBERT, TensorFlow, PyTorch, dll.). Apakah ini untuk MVP atau visi jangka panjang? Jika untuk jangka panjang, `implementation-plan.md` perlu lebih eksplisit memetakan kapan teknologi ini akan diintegrasikan pasca-MVP.
        * Integrasi dengan DeepSeek API disebutkan sebagai tujuan jangka panjang untuk MVP di `implementation-plan.md` (Step 3.1), tetapi detail bagaimana *placeholder* saat ini akan bertransisi ke DeepSeek API (misalnya, kontrak API, penanganan error, biaya) belum ada.
    * **Rekomendasi:**
        * Pastikan `tech-stack.md` membedakan dengan jelas antara teknologi yang digunakan untuk *placeholder MVP* dan yang direncanakan untuk versi produksi atau iterasi berikutnya.
        * Buat rencana transisi yang lebih jelas dari layanan *placeholder* ke layanan NLP/AI yang sebenarnya (misalnya, DeepSeek API atau model internal) dalam `implementation-plan.md` atau dokumen arsitektur.
        * Update `progress.md` dan `status-todolist-suggestions.md` untuk secara akurat mencerminkan bahwa layanan NLP/AI saat ini adalah *placeholder*.

5.  **Konsistensi User Roles dan Permissions:**
    * **Observasi:** `UserRole` didefinisikan dalam `src/app/models/user.py` sebagai enum (PATIENT, DOCTOR, ADMIN). `product-design-document.md` menyebutkan "System Administrators" sebagai target pengguna dan "System Administrator Portal". `database-schema.md` juga memiliki `role VARCHAR(20) NOT NULL CHECK (role IN ('PATIENT', 'DOCTOR', 'ADMIN'))`.
    * **Ambiguitas/Potensi Masalah:**
        * Definisi peran sudah konsisten. Namun, detail mengenai *permissions* spesifik untuk setiap peran, terutama untuk ADMIN dan bagaimana ini akan berinteraksi dengan data pasien (bahkan metadata), belum terperinci. Misalnya, dapatkah ADMIN melihat log audit akses data pasien? Sejauh mana akses mereka?
        * Bagaimana *consent* pasien mempengaruhi kemampuan DOCTOR untuk mengakses data juga perlu detail lebih lanjut. `implementation-plan.md` (Step 4.1) menyentuh ini dengan "simple access list", tetapi ini perlu dielaborasi dalam arsitektur dan desain database (misalnya, tabel consent, bagaimana smart contract merefleksikan ini). `database-schema.md` memiliki tabel `data_processing_consents` dan `data_deletion_requests`, yang sangat baik, tetapi bagaimana ini terhubung ke *smart contract* dan alur akses data oleh dokter perlu diperjelas dalam `architecture.md`.
    * **Rekomendasi:**
        * Detailkan matriks *Role-Based Access Control* (RBAC) dalam `architecture.md` atau dokumen keamanan terpisah.
        * Elaborasikan alur kerja *consent management* dan bagaimana ini berinteraksi dengan *smart contract* dan akses data di `architecture.md`.
        * Pastikan `database-schema.md` (tabel `audit_logs`, `data_processing_consents`) selaras dengan alur ini.

6.  **Keterkaitan antara `blockchain_record_id` di Database dan Transaksi Blockchain:**
    * **Observasi:** Tabel `medical_records` di `database-schema.md` memiliki kolom `blockchain_record_id VARCHAR(66) UNIQUE NOT NULL` yang diberi komentar "-- Ethereum tx hash format". `src/app/api/endpoints/medical_records.py` menyimpan `tx_hash` dari hasil pemanggilan `blockchain_service.add_medical_record_hash` ke kolom ini.
    * **Ambiguitas/Potensi Masalah:** Apakah `blockchain_record_id` ini *selalu* hash transaksi? Smart contract `MedicalRecordRegistry.sol` memiliki `event RecordAdded(bytes32 indexed recordHash, ...)` dan fungsi `addRecord(bytes32 recordHash, ...)`. Yang dicatat sebagai *identifier unik* di *smart contract* adalah `recordHash` (hash dari data medis), bukan `tx_hash`. Fungsi `getRecordHashesByPatient` juga mengembalikan `bytes32[]` yang merupakan `recordHash`.
    * Jika `blockchain_record_id` di DB adalah `tx_hash`, maka bagaimana kita menghubungkan `recordHash` yang ada di *event* dan struktur *smart contract* dengan entri di database? Jika `blockchain_record_id` seharusnya adalah `recordHash`, maka perlu penyesuaian.
    * `README.md` menyebutkan: "Endpoint `/api/v1/medical-records/patient/me`**: Pengambilan rekam medis melalui endpoint ini sekarang bergantung pada `BlockchainService` yang mengembalikan hash rekam medis terkait DID pasien." Ini mengacu pada `recordHash` (hash data), bukan `tx_hash`.
    * Namun, `MedicalRecord` ORM model memiliki `blockchain_record_id = Column(String(66), unique=True, nullable=True)`, dan `crud_medical_record.py` mengupdate field ini dengan `blockchain_tx_hash`. Ini konsisten dengan API endpoint yang juga menyimpan `tx_hash`.
    * **Ketidakselarasan yang perlu diatasi:**
        * *Smart contract* (`MedicalRecordRegistry`) menggunakan `recordHash` (hash data) sebagai *identifier* utama untuk rekam medis.
        * API (`medical_records.py`) dan CRUD (`crud_medical_record.py`) saat ini menyimpan `transaction_hash` ke `blockchain_record_id` di database.
        * Endpoint `GET /medical-records/patient/me` (sesuai `README.md` dan implementasi `MedicalRecordRegistry`) bergantung pada pengambilan `recordHash` (hash data) dari *blockchain service*, bukan `transaction_hash`.
    * **Rekomendasi:**
        * **Klarifikasi Tujuan `blockchain_record_id`:** Putuskan apakah kolom ini untuk menyimpan `transaction_hash` (sebagai bukti pencatatan) atau `recordHash` (sebagai *identifier* yang digunakan oleh *smart contract* untuk pengambilan).
        * **Jika untuk `recordHash`:** Ubah logika di API dan CRUD untuk menyimpan `recordHash` (yaitu `data_hash`) ke `blockchain_record_id`. Ini akan lebih selaras dengan cara *smart contract* di-query. Kolom `data_hash` dan `blockchain_record_id` mungkin menjadi redundan jika keduanya menyimpan hal yang sama (kecuali ada kasus di mana `data_hash` ada tetapi belum dicatat ke blockchain, sehingga `blockchain_record_id` null).
        * **Jika untuk `transaction_hash`:** Maka perlu ada cara untuk mengquery *smart contract* atau *event* menggunakan `transaction_hash` untuk mendapatkan `recordHash` terkait jika diperlukan, atau memastikan alur `GET /medical-records/patient/me` benar-benar hanya mengandalkan `recordHash` yang diambil dari `getRecordHashesByPatient` dan kemudian mencocokkannya dengan kolom `data_hash` di database (seperti yang tampaknya dilakukan oleh kode saat ini di `test_api_medical_records.py` dan `medical_records.py`).
        * **Paling Penting:** Pastikan konsistensi. Jika `BlockchainService.get_record_hashes_for_patient` mengembalikan `data_hash` (seperti yang dilakukan `MedicalRecordRegistry.sol`), maka *local database query* harus menggunakan `data_hash` untuk mencocokkan, bukan `blockchain_record_id` (kecuali `blockchain_record_id` juga diisi dengan `data_hash`). Kode saat ini di `medical_records.py` (fungsi `get_my_medical_records`) tampaknya sudah benar dengan mencocokkan `data_hash` dari blockchain dengan `MedicalRecordORM.data_hash` di DB. Jadi, ambiguitasnya lebih ke *penamaan kolom* `blockchain_record_id` yang mungkin menyesatkan jika isinya adalah `tx_hash` sementara query utama bergantung pada `data_hash`. Pertimbangkan mengganti nama `blockchain_record_id` menjadi `blockchain_transaction_hash` jika memang itu isinya, untuk menghindari kebingungan.

7.  **Versi Node.js dan Ganache:**
    * **Observasi:**
        * `README.md` (Persyaratan Sistem): Node.js 16.x+, Ganache (tanpa versi spesifik).
        * `development-environment-notes.md` (Required Software): Node.js 20.x LTS, Ganache 7.x.
        * `implementation-plan.md` (Step 1.2): `npm install -g ganache` (menginstal versi terbaru), `ganache --deterministic --chain.chainId 1337 --database.dbPath ./.ganache-db`.
        * `hardhat.config.js`: Menggunakan `ganache: { url: "http://127.0.0.1:7545" }`.
    * **Potensi Masalah:** Perbedaan versi Node.js antara `README.md` (16.x+) dan `development-environment-notes.md` (20.x LTS) bisa menyebabkan masalah kompatibilitas jika pengembang menggunakan versi yang berbeda. Versi Ganache yang tidak spesifik di `README.md` juga bisa menjadi masalah. Perintah instalasi Ganache di `implementation-plan.md` (`npm install -g ganache`) akan menginstal versi terbaru yang mungkin berbeda dengan 7.x yang direkomendasikan di `development-environment-notes.md`.
    * **Rekomendasi:** Standarisasi versi Node.js dan Ganache di semua dokumen. `development-environment-notes.md` tampaknya memiliki versi yang lebih spesifik dan baru (Node.js 20.x, Ganache 7.x), yang mungkin lebih baik. Perbarui `README.md` dan pastikan `implementation-plan.md` merujuk pada instalasi versi spesifik jika perlu (misalnya, `npm install -g ganache@7.x.x`).

8.  **Status Implementasi di `README.md` vs. `status-todolist-suggestions.md`:**
    * **Observasi:**
        * `README.md` (Status Implementasi): Mencantumkan beberapa item sebagai selesai ([x]) dan beberapa belum ([ ]).
        * `status-todolist-suggestions.md`: Memberikan status yang lebih detail dan tanggal terakhir pembaruan.
    * **Potensi Masalah:** `README.md` mungkin tidak selalu se-aktual `status-todolist-suggestions.md` atau `progress.md`. Ini bisa membingungkan bagi seseorang yang pertama kali melihat proyek.
    * **Rekomendasi:** Pertimbangkan untuk membuat `README.md` merujuk ke `status-todolist-suggestions.md` atau `progress.md` untuk status implementasi terbaru, atau pastikan `README.md` selalu disinkronkan setelah setiap pembaruan signifikan. Mengingat Anda menekankan keterbaruan dokumentasi, proses sinkronisasi ini penting.

9.  **Deskripsi `UserLogin` Pydantic Model:**
    * **Observasi:** Dalam `src/app/api/endpoints/auth.py`, fungsi `login_for_access_token_json` menggunakan `UserLogin` sebagai tipe data untuk `user_credentials`. Ada komentar `# UserLogin is not defined in the file, but I will keep it as is.`.
    * **Fakta:** Model `UserLogin` sebenarnya *didefinisikan* di `src/app/models/user.py`.
    * **Potensi Masalah:** Komentar yang usang dapat menyesatkan pengembang (atau AI) yang membaca kode tersebut, membuatnya berpikir model tersebut hilang atau perlu dibuat.
    * **Rekomendasi:** Hapus komentar yang sudah tidak relevan tersebut dari `src/app/api/endpoints/auth.py`.

10. **Nama Kolom `metadata` vs. `record_metadata`:**
    * **Observasi:**
        * `database-schema.md` untuk tabel `medical_records` mendefinisikan `metadata JSONB`.
        * Model SQLAlchemy `MedicalRecord` di `src/app/models/medical_record.py` memiliki `record_metadata = Column(JSONB, nullable=True)`.
        * Model Pydantic `MedicalRecordBase` dan `MedicalRecordResponse` di `src/app/models/medical_record.py` menggunakan `record_metadata: Optional[dict] = None`.
        * File migrasi Alembic `9096078f2071_create_medical_records_table.py` membuat kolom `metadata postgresql.JSONB(astext_type=sa.Text())`.
    * **Potensi Masalah:** Ada ketidakkonsistenan nama antara skema database aktual yang dibuat oleh migrasi (`metadata`) dan nama atribut yang digunakan dalam model ORM SQLAlchemy serta model Pydantic (`record_metadata`). Ini bisa menyebabkan error saat mapping data antara ORM dan database, atau kebingungan.
    * **Rekomendasi:**
        * Standarisasi nama. Mengingat model ORM dan Pydantic sudah menggunakan `record_metadata`, akan lebih baik jika kolom di database dan file migrasi juga dinamai `record_metadata`.
        * Jika migrasi sudah dijalankan dan mengubah nama kolom di database memerlukan migrasi baru, pastikan model SQLAlchemy menggunakan `Column('metadata', JSONB, key='record_metadata')` atau sejenisnya untuk memetakan nama kolom database `metadata` ke atribut ORM `record_metadata`. Namun, menyamakan nama adalah solusi yang lebih bersih.
        * Perbarui `database-schema.md` untuk mencerminkan nama yang benar (`record_metadata`).

**Area Lain untuk Diperhatikan (Mungkin Bukan Krusial, Tapi Perlu Klarifikasi Lanjutan):**

* **Detail Skema Respons API:** `implementation-plan.md` (Bagian "API Standards & Error Handling") mendefinisikan format error respons. Pastikan ini diimplementasikan secara konsisten di semua endpoint. `status_routes.py` menggunakan `StatusResponse` dari `status_models.py`, yang baik.
* **Strategi CI/CD:** `architecture.md` (Bagian CI/CD Architecture) menyebutkan Kubernetes dan Helm untuk deploy. `testing-strategy.md` (Bagian Continuous Integration) menunjukkan workflow GitHub Actions dasar. Perlu dipastikan ada rencana detail untuk build Docker image dan proses deployment ke Kubernetes.
* **Ketergantungan Versi di `requirements.txt` vs. `tech-stack.md`:**
    * `requirements.txt` memiliki versi spesifik untuk beberapa pustaka (misalnya, `fastapi==0.110.0`).
    * `tech-stack.md` juga menyebutkan versi untuk beberapa pustaka (misalnya, `fastapi==0.110.0`, `uvicorn[standard]==0.27.1`).
    * Penting untuk menjaga kedua file ini sinkron. `requirements.txt` harus menjadi *source of truth* untuk versi yang diinstal. `tech-stack.md` harus mencerminkan keputusan versi ini atau memberikan justifikasi jika ada perbedaan (misalnya, versi minimal yang didukung).

Dengan menangani poin-poin di atas, terutama yang bersifat krusial, Anda dapat meningkatkan kejelasan, konsistensi, dan mengurangi risiko ambiguitas dalam dokumentasi proyek MediTrustAl. Ini akan sangat membantu dalam pengembangan yang efisien dan kolaborasi tim (termasuk dengan AI).