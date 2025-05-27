# MediTrustAI

Sistem manajemen rekam medis berbasis blockchain dengan integrasi AI untuk analisis data kesehatan.

## Persyaratan Sistem

- Python 3.11 atau lebih tinggi
- PostgreSQL 15.x
- Node.js 20.x LTS atau lebih tinggi (untuk smart contract development)
- Ganache (untuk blockchain development lokal)

## Setup Environment Development

### 1. Setup Database (PostgreSQL)

1. Download PostgreSQL 15.x dari [situs resmi](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
2. Jalankan installer dengan konfigurasi berikut:
   - Port: 5432 (default)
   - Password untuk user 'postgres': postgres
   - Locale: Default
   - Komponen yang diinstal: minimal PostgreSQL Server dan pgAdmin 4

3. Setelah instalasi, buat database baru:
   - Buka pgAdmin 4
   - Buat database baru dengan nama: `meditrustal`

### 2. Setup Python Environment

1. Clone repository:
   ```bash
   git clone https://github.com/yourusername/MediTrustAl.git
   cd MediTrustAl
   ```

2. Buat virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Untuk Linux/Mac
   # ATAU
   .\venv\Scripts\activate  # Untuk Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Setup Blockchain Development

1. Install Ganache:
   - Download dari [Truffle Suite](https://trufflesuite.com/ganache/)
   - Install dan jalankan
   - Buat workspace baru dengan port RPC SERVER: 7545

2. Setup smart contract:
   ```bash
   cd blockchain
   npm install
   npx hardhat compile
   npx hardhat run scripts/deploy.js --network ganache
   ```

### 4. Konfigurasi Environment

1. Buat file `.env` di root project:
   ```env
   GANACHE_RPC_URL=http://127.0.0.1:7545
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/meditrustal
   JWT_SECRET_KEY=your-secret-key-for-jwt
   ```

2. Jalankan migrasi database:
   ```bash
   python -m alembic upgrade head
   ```

### 5. Menjalankan Aplikasi

1. Jalankan backend:
   ```bash
   uvicorn src.app.main:app --reload
   ```

2. Akses API documentation:
   - http://localhost:8000/docs (Swagger UI)
   - http://localhost:8000/redoc (ReDoc)

## Status Implementasi

- [x] Implementasi manajemen rekam medis (MVP Core)
- [x] Integrasi blockchain (UserRegistry & MedicalRecordRegistry)
- [x] Sistem autentikasi dan registrasi pengguna
- [x] Integrasi AI/NLP (Placeholder implemented)
- [x] Unit & integration testing untuk fitur utama
- [ ] AI Predictive Service (Placeholder, next step)

## Testing

### Unit Testing
```bash
# Menjalankan semua test
pytest

# Menjalankan test dengan coverage report
pytest --cov=src

# Menjalankan test spesifik
pytest tests/test_specific_file.py
```

### Smart Contract Testing
```bash
# Di direktori blockchain/
npx hardhat test
```

### Catatan untuk Developer (Developer Notes)
- **Endpoint `/api/v1/medical-records/patient/me`**: Pengambilan rekam medis melalui endpoint ini bergantung pada `BlockchainService` yang mengembalikan hash rekam medis (data_hash) terkait DID pasien melalui metode `get_record_hashes_for_patient`. Perhatikan bahwa:
  - Fungsi `get_record_hashes_for_patient` mengembalikan array hash rekam medis (data_hash) dari blockchain, bukan transaction hash.
  - Kolom `blockchain_record_id` di database menyimpan transaction hash (tx_hash) yang dihasilkan saat mencatat data_hash ke blockchain, bukan data_hash itu sendiri.
  - Pencocokan antara hash dari blockchain dan rekam medis di database dilakukan menggunakan kolom `data_hash`, bukan `blockchain_record_id`.
  - Dalam pengembangan lokal dan pengujian integrasi, pastikan metode `get_record_hashes_for_patient` dari `BlockchainService` (yang di-mock dalam `tests/conftest.py`) dikonfigurasi untuk mengembalikan hash yang sesuai dengan kolom `data_hash` di database agar rekam medis muncul.

- **Nama Kolom Database vs Model ORM**: Perhatikan bahwa terdapat perbedaan penamaan antara kolom di database dan atribut di model ORM:
  - Kolom `record_metadata` di database (sebelumnya bernama `metadata` di file migrasi) dipetakan ke atribut `record_metadata` di model ORM dan Pydantic.
  - Jika Anda menggunakan SQL langsung atau alat database lain, pastikan untuk merujuk ke nama kolom yang benar (`record_metadata`).

## Troubleshooting

### Database Issues
1. **Error: Connection refused**
   - Pastikan PostgreSQL service berjalan
   - Verifikasi port 5432 tidak digunakan aplikasi lain
   - Cek kredensial di `.env` sesuai dengan setup PostgreSQL

2. **Error: Database meditrustal does not exist**
   - Buat database melalui pgAdmin 4
   - Atau gunakan command: `createdb meditrustal`

### Blockchain Issues
1. **Error: Cannot connect to Ganache**
   - Pastikan Ganache berjalan
   - Verifikasi RPC URL di `.env` sesuai dengan setting Ganache
   - Port default: 7545

2. **Error: Contract deployment failed**
   - Pastikan ada ETH di account Ganache
   - Cek network configuration di `hardhat.config.js`

### Python Environment Issues
1. **Error: Module not found**
   - Pastikan virtual environment aktif
   - Jalankan `pip install -r requirements.txt`
   - Cek `PYTHONPATH` includes project root

2. **Error: Import error src.app**
   - Jalankan aplikasi dari root directory
   - Tambahkan project root ke PYTHONPATH

## Struktur Project

```
MediTrustAl/
├── src/
│   └── app/
│       ├── core/          # Konfigurasi inti
│       ├── models/        # Model database
│       ├── schemas/       # Pydantic schemas
│       └── api/           # API endpoints
├── blockchain/            # Smart contracts
├── alembic/              # Database migrations
└── tests/                # Unit tests
```

## Status Implementasi

- [x] Setup dasar project
- [x] Implementasi smart contract UserRegistry
- [x] Integrasi blockchain dengan FastAPI
- [x] Setup database PostgreSQL
- [x] Implementasi autentikasi dasar
- [ ] Implementasi manajemen rekam medis
- [ ] Integrasi AI untuk analisis
- [ ] Frontend development

## Kontribusi

1. Fork repository
2. Buat branch baru (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## Lisensi

[MIT License](LICENSE)