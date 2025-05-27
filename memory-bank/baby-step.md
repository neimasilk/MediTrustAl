# Baby Steps: Implementasi Step 3.1 - Placeholder NLP Service

**Tujuan Utama:** Membuat layanan NLP placeholder yang sangat sederhana, sesuai dengan rencana implementasi MVP. Layanan ini belum akan melakukan pemrosesan NLP sebenarnya, tetapi akan mengembalikan respons JSON dummy yang telah ditentukan.

**Prasyarat:**
* Step 2.3 (Basic Patient Data Retrieval) telah selesai dan diverifikasi.
* Lingkungan pengembangan backend (FastAPI) berfungsi dengan baik.

---

### **Baby Step 3.1.1: Penentuan Lokasi dan Struktur Placeholder NLP Service**

* **Tujuan:** Memutuskan apakah placeholder NLP service akan menjadi modul dalam backend FastAPI utama atau microservice terpisah (untuk MVP, modul dalam backend utama mungkin lebih sederhana).
* **Pertimbangan:**
    * **Modul dalam Backend Utama (Direkomendasikan untuk MVP):**
        * **Keuntungan:** Lebih cepat diimplementasikan, tidak perlu setup infrastruktur service baru (routing, deployment terpisah), lebih mudah dipanggil dari service lain di backend utama.
        * **Struktur Potensial:**
            ```
            src/app/
            ├── api/
            │   └── endpoints/
            │       ├── ...
            │       └── nlp.py  # Router untuk NLP
            ├── services/
            │   └── nlp_service.py # Logika placeholder NLP
            └── core/
                └── ...
            ```
    * **Microservice Terpisah (FastAPI/Flask):**
        * **Keuntungan:** Pemisahan yang lebih jelas, potensi skalabilitas independen di masa depan.
        * **Kerugian (untuk MVP):** Overhead setup lebih besar, perlu konfigurasi komunikasi antar-service.
* **Keputusan (Untuk AI Developer):** Untuk MVP ini, implementasikan sebagai **modul dalam backend FastAPI utama**. Buat file `src/app/services/nlp_service.py` untuk logika dan `src/app/api/endpoints/nlp.py` untuk routing API.
* **Instruksi:**
    1.  Buat file `src/app/services/nlp_service.py`.
    2.  Buat file `src/app/api/endpoints/nlp.py`.
    3.  Tambahkan router NLP ke `src/app/main.py`.
* **Kriteria Penerimaan:**
    * File-file baru telah dibuat di lokasi yang benar.
    * Router NLP telah ditambahkan ke instance FastAPI utama di `main.py` (misalnya, dengan prefix `/api/v1/nlp`).
* **Rollback (jika gagal):** Hapus file yang baru dibuat dan revert perubahan di `main.py`.

---

### **Baby Step 3.1.2: Implementasi Logika Placeholder NLP Service**

* **Tujuan:** Mengimplementasikan fungsi di `nlp_service.py` yang menerima teks dan mengembalikan respons JSON dummy.
* **Instruksi:**
    1.  Dalam `src/app/services/nlp_service.py`, buat sebuah fungsi, misalnya `extract_entities_placeholder`, yang:
        * Menerima satu argumen string (misalnya, `text_input: str`).
        * Mengabaikan `text_input` (karena ini adalah placeholder).
        * Mengembalikan dictionary Python yang identik dengan struktur JSON dummy yang ditentukan:
            ```python
            {
                "entities": [
                    {"text": "Blood Pressure", "type": "VitalSign"},
                    {"text": "120/80 mmHg", "type": "Measurement"}
                ]
            }
            ```
* **Kriteria Penerimaan:**
    * Fungsi `extract_entities_placeholder` ada di `src/app/services/nlp_service.py`.
    * Fungsi tersebut mengembalikan dictionary Python yang sesuai dengan struktur yang ditentukan, terlepas dari inputnya.
* **Rollback (jika gagal):** Perbaiki implementasi fungsi hingga sesuai.

---

### **Baby Step 3.1.3: Implementasi Endpoint API untuk Placeholder NLP Service**

* **Tujuan:** Membuat endpoint API `POST /api/v1/nlp/extract-entities` yang menggunakan logika dari `nlp_service.py`.
* **Instruksi:**
    1.  Dalam `src/app/api/endpoints/nlp.py`:
        * Impor `APIRouter` dan fungsi `extract_entities_placeholder` dari `nlp_service.py`.
        * Buat Pydantic model untuk request body, misalnya `NLPExtractionRequest`, yang memiliki satu field `text: str`.
        * Buat Pydantic model untuk response body, misalnya `NLPExtractionResponse`, yang mencerminkan struktur JSON dummy (misalnya, field `entities: List[Dict[str, str]]`).
        * Definisikan endpoint `POST /extract-entities` yang:
            * Menerima request body yang sesuai dengan `NLPExtractionRequest`.
            * Memanggil fungsi `extract_entities_placeholder` (input teks dari request bisa diabaikan oleh fungsi placeholder).
            * Mengembalikan respons yang sesuai dengan `NLPExtractionResponse`.
    2.  Pastikan router ini ditambahkan ke aplikasi FastAPI utama di `src/app/main.py` dengan prefix `/api/v1/nlp`.
* **Kriteria Penerimaan:**
    * Endpoint `POST /api/v1/nlp/extract-entities` dapat diakses.
    * Endpoint menerima JSON dengan field `text`.
    * Endpoint mengembalikan JSON response dengan struktur `{"entities": [{"text": "Blood Pressure", "type": "VitalSign"}, {"text": "120/80 mmHg", "type": "Measurement"}]}`.
* **Rollback (jika gagal):** Periksa Pydantic model, routing, dan pemanggilan service. Pastikan router sudah benar ditambahkan di `main.py`.

---

### **Baby Step 3.1.4: Penulisan Tes Unit untuk Placeholder NLP Service**

* **Tujuan:** Membuat tes unit untuk memverifikasi fungsionalitas placeholder NLP service dan endpoint API-nya.
* **Instruksi:**
    1.  Buat file tes baru, misalnya `tests/unit/services/test_nlp_service.py`.
        * Tes fungsi `extract_entities_placeholder` untuk memastikan ia selalu mengembalikan struktur dummy yang benar, apa pun inputnya.
    2.  Buat file tes baru, misalnya `tests/integration/api/test_api_nlp.py`.
        * Tes endpoint `POST /api/v1/nlp/extract-entities`:
            * Kirim request valid dengan data teks.
            * Verifikasi status code adalah 200 OK.
            * Verifikasi body respons adalah JSON dummy yang diharapkan.
            * Tes dengan request body yang tidak valid (misalnya, field `text` hilang atau tipe salah) untuk memastikan validasi Pydantic bekerja (status code 422).
* **Kriteria Penerimaan:**
    * Semua tes unit dan integrasi untuk placeholder NLP service lolos.
    * Tes mencakup skenario *happy path* dan *error/invalid input*.
* **Rollback (jika gagal):** Perbaiki kode service, endpoint, atau tes hingga semua tes lolos.

---

### **Baby Step 3.1.5: Pembaruan Dokumentasi API (Swagger/OpenAPI)**

* **Tujuan:** Memastikan endpoint baru untuk NLP terdokumentasi secara otomatis dalam dokumentasi Swagger UI / OpenAPI.
* **Instruksi:**
    1.  Jalankan server FastAPI (`uvicorn src.app.main:app --reload`).
    2.  Akses dokumentasi API interaktif (biasanya di `http://localhost:8000/docs`).
    3.  Verifikasi bahwa endpoint `POST /api/v1/nlp/extract-entities` muncul dengan benar, termasuk deskripsi, model request, dan model respons.
    4.  Jika perlu, tambahkan deskripsi yang lebih baik atau ringkasan pada definisi router atau endpoint di `src/app/api/endpoints/nlp.py` menggunakan parameter `summary` dan `description` di decorator FastAPI.
* **Kriteria Penerimaan:**
    * Endpoint NLP baru terdokumentasi dengan benar di Swagger UI.
    * Model request dan response terlihat jelas.
* **Rollback (jika gagal):** Periksa tipe Pydantic model, decorator FastAPI, dan pastikan server berjalan dengan kode terbaru.

---

Setelah semua baby steps ini berhasil diselesaikan, Step 3.1 dari `implementation-plan.md` dapat dianggap sepenuhnya selesai.