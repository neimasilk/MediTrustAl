# Baby Steps untuk Implementasi Step 1.4: Medical Record Data Model and Storage

**Tujuan Utama:** Mengimplementasikan fungsionalitas dasar untuk membuat dan menyimpan rekam medis, dengan data dienkripsi di database off-chain (PostgreSQL) dan hash data dicatat di blockchain (Ganache).

## Bagian 1: Persiapan dan Model Data (Database & Pydantic)

1.  **Definisi Tipe ENUM untuk `RecordType`:**
    * Buat Enum Python di `src/app/models/medical_record.py` (file baru) untuk `RecordType` sesuai `database-schema.md` (DIAGNOSIS, LAB_RESULT, PRESCRIPTION, TREATMENT_PLAN, MEDICAL_HISTORY, VITAL_SIGNS, IMAGING, VACCINATION).

2.  **Model SQLAlchemy `MedicalRecord`:**
    * Buat file `src/app/models/medical_record.py`.
    * Definisikan kelas `MedicalRecord(Base)` dengan kolom-kolom berikut, merujuk pada `database-schema.md`:
        * `id`: `Column(PGUUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")`
        * `patient_id`: `Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)`
        * `blockchain_record_id`: `Column(String(66), unique=True, nullable=True)` (Hash transaksi Ethereum, bisa null saat awal pembuatan sebelum transaksi dikonfirmasi)
        * `record_type`: `Column(SQLEnum(RecordType), nullable=False)` (gunakan Enum Python yang dibuat di atas)
        * `metadata`: `Column(JSONB, nullable=True)` (Untuk data tambahan spesifik per `record_type`)
        * `encrypted_data`: `Column(BYTEA, nullable=False)`
        * `data_hash`: `Column(String(64), nullable=False)` (SHA-256 dari data asli sebelum enkripsi)
        * `created_at`: `Column(DateTime(timezone=True), default=datetime.utcnow)`
        * `updated_at`: `Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)`
    * Tambahkan relasi ke model `User` (jika diperlukan, misal `patient = relationship("User")`).
    * Pastikan `Base` diimpor dari `src.app.core.database`.

3.  **Skema Pydantic untuk `MedicalRecord`:**
    * Di `src/app/models/medical_record.py`, definisikan skema Pydantic:
        * `MedicalRecordBase(BaseModel)`: `record_type: RecordType`, `metadata: Optional[dict] = None`, `raw_data: str` (data mentah yang akan dienkripsi, atau bisa struktur yang lebih kompleks jika diperlukan).
        * `MedicalRecordCreate(MedicalRecordBase)`: Tambahkan validasi jika perlu.
        * `MedicalRecordResponse(MedicalRecordBase)`: `id: uuid.UUID`, `patient_id: uuid.UUID`, `blockchain_record_id: Optional[str] = None`, `data_hash: str`, `created_at: datetime`, `updated_at: datetime`. `raw_data` tidak disertakan di sini; `encrypted_data` juga tidak diekspos langsung.
        * `Config.from_attributes = True` untuk `MedicalRecordResponse`.

4.  **Migrasi Alembic:**
    * Tambahkan model `MedicalRecord` ke `target_metadata` di `alembic/env.py` (jika belum otomatis terdeteksi dari `Base.metadata`).
        ```python
        # In alembic/env.py, after importing User's Base
        from src.app.models.medical_record import Base as MedicalRecordBase # or however you name it
        # ...
        target_metadata = [UserBase.metadata, MedicalRecordBase.metadata] # if multiple Bases
        # or ensure MedicalRecord model uses the same Base as User model.
        # If User model and MedicalRecord model use the same 'Base' from core.database,
        # then target_metadata = Base.metadata should be sufficient.
        ```
        *Periksa `src/app/models/user.py` dan pastikan `MedicalRecord` menggunakan `Base` yang sama dari `src.app.core.database`.*
    * Jalankan `alembic revision -m "create_medical_records_table"`
    * Edit file migrasi yang dihasilkan untuk memastikan tabel `medical_records` dibuat dengan benar, termasuk ENUM, foreign key, dan constraint lainnya.
    * Jalankan `alembic upgrade head`.

5.  **CRUD Operations untuk `MedicalRecord`:**
    * Buat file `src/app/crud/crud_medical_record.py`.
    * Implementasikan fungsi:
        * `create_medical_record(db: Session, *, medical_record_in: MedicalRecordCreate, patient_id: uuid.UUID, encrypted_data: bytes, data_hash: str) -> MedicalRecord`
        * `get_medical_record_by_id(db: Session, record_id: uuid.UUID) -> Optional[MedicalRecord]`
        * `get_medical_records_by_patient_id(db: Session, patient_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[MedicalRecord]`
        * `update_medical_record_blockchain_id(db: Session, record_id: uuid.UUID, blockchain_tx_hash: str) -> Optional[MedicalRecord]`

## Bagian 2: Utilitas Enkripsi dan Hashing

1.  **Buat Modul Utilitas `src/app/core/encryption.py`:**
    * Implementasikan fungsi `encrypt_data(data: str, key: bytes) -> bytes`:
        * Menggunakan AES-256-GCM.
        * Menghasilkan nonce, ciphertext, dan tag. Mengembalikan gabungan ketiganya atau struktur yang bisa disimpan dan diurai kembali.
        * *Catatan Kunci*: Untuk MVP, `key` bisa berasal dari konfigurasi atau konstanta. Pengelolaan kunci yang aman adalah topik besar dan akan disempurnakan nanti. Jangan hardcode kunci di kode. Pertimbangkan mengambil dari `.env` untuk development.
    * Implementasikan fungsi `decrypt_data(encrypted_data_with_nonce_tag: bytes, key: bytes) -> str`:
        * Mengurai nonce, ciphertext, tag dari input.
        * Melakukan dekripsi dan verifikasi tag.
    * Implementasikan fungsi `generate_encryption_key() -> bytes` (misalnya, 32 bytes acak, hanya untuk testing atau jika kunci per record/user dibutuhkan dan disimpan terpisah).
    * Implementasikan fungsi `hash_data(data: str) -> str`:
        * Menggunakan SHA-256.
        * Mengembalikan representasi hex dari hash.

## Bagian 3: Smart Contract `MedicalRecordRegistry`

1.  **Buat File `contracts/MedicalRecordRegistry.sol`:**
    * Versi Solidity (misalnya, `pragma solidity ^0.8.20;`).
    * Definisikan `struct RecordMetadata { string patientDid; string recordType; uint256 timestamp; address submitter; }`
    * Definisikan `mapping(bytes32 => RecordMetadata) public recordHashes;` (key adalah `data_hash`).
    * Definisikan `event RecordAdded(bytes32 indexed recordHash, string indexed patientDid, string recordType, uint256 timestamp, address submitter);`
    * Implementasikan fungsi `function addRecord(bytes32 _recordHash, string memory _patientDid, string memory _recordType) public`:
        * Cek apakah `_recordHash` sudah ada (revert jika iya untuk menghindari duplikasi).
        * Simpan metadata: `recordHashes[_recordHash] = RecordMetadata(_patientDid, _recordType, block.timestamp, msg.sender);`
        * Emit `RecordAdded(_recordHash, _patientDid, _recordType, block.timestamp, msg.sender);`
    * Implementasikan fungsi view `function getRecordMetadata(bytes32 _recordHash) public view returns (string memory patientDid, string memory recordType, uint256 timestamp, address submitter)` (jika diperlukan untuk verifikasi).

2.  **Kompilasi Smart Contract:**
    * Jalankan `npx hardhat compile` di direktori root proyek. Pastikan tidak ada error.

3.  **Buat Skrip Deployment `scripts/deployMedicalRecordRegistry.js`:**
    * Mirip dengan `deployUserRegistry.js`.
    * Deploy `MedicalRecordRegistry`.
    * Panggil `saveDeploymentInfo` untuk menyimpan ABI dan alamat kontrak ke `blockchain/build/deployments/MedicalRecordRegistry-address.json` dan `MedicalRecordRegistry-abi.json`.

4.  **Deploy ke Ganache:**
    * Pastikan Ganache berjalan.
    * Jalankan `npx hardhat run scripts/deployMedicalRecordRegistry.js --network ganache`.

5.  **Update Konfigurasi Aplikasi:**
    * Di `src/app/core/config.py`, tambahkan entri di `BLOCKCHAIN_CONFIG` untuk `medical_record_registry_address` dan `medical_record_registry_abi`.
    * Modifikasi fungsi `load_contract_info()` untuk memuat ABI dan alamat `MedicalRecordRegistry` juga.

6.  **Perluas `BlockchainService` (`src/app/core/blockchain.py`):**
    * Tambahkan inisialisasi untuk kontrak `MedicalRecordRegistry` di `__init__`.
    * Implementasikan metode baru `async def add_medical_record_hash(self, record_hash_hex: str, patient_did: str, record_type: str) -> dict`:
        * Konversi `record_hash_hex` ke `bytes32`.
        * Bangun, tandatangani, dan kirim transaksi ke fungsi `addRecord` di smart contract `MedicalRecordRegistry`.
        * Tunggu receipt dan kembalikan `{'success': True, 'transaction_hash': tx_hash_hex}` atau `{'success': False, 'error': str(e)}`.

## Bagian 4: Backend API Endpoints untuk Rekam Medis

1.  **Buat File `src/app/api/endpoints/medical_records.py`:**
    * Buat `APIRouter`.
    * Impor dependensi yang diperlukan (Session, model, CRUD, `get_current_active_user`, `BlockchainService`, utilitas enkripsi/hashing).

2.  **Implementasi Endpoint `POST /medical-records`:**
    * `@router.post("/", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)`
    * `async def create_medical_record_endpoint(medical_record_in: MedicalRecordCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user), blockchain_service: BlockchainService = Depends(get_blockchain_service))`
    * Dapatkan `patient_id` dari `current_user.id` (asumsi pasien membuat rekam medisnya sendiri untuk MVP).
    * Dapatkan `patient_did` dari `current_user.did`.
    * Generate kunci enkripsi (untuk MVP, bisa sementara diambil dari config atau generate per record jika tidak ada strategi penyimpanan kunci yang lebih baik). **PENTING**: Ini adalah penyederhanaan besar untuk MVP. Kunci ini HARUS dikelola dengan aman di produksi.
        ```python
        # Contoh sangat sederhana, JANGAN GUNAKAN DI PRODUKSI TANPA STRATEGI KUNCI YANG BENAR
        from src.app.core.config import JWT_CONFIG # Menggunakan secret JWT sebagai contoh, TIDAK IDEAL
        encryption_key = JWT_CONFIG["secret_key"][:32].encode() # Pastikan 32 bytes untuk AES-256
        # ATAU, generate per record dan simpan terenkripsi (lebih kompleks)
        # encryption_key = generate_encryption_key()
        ```
    * Enkripsi `medical_record_in.raw_data` menggunakan `encrypt_data(medical_record_in.raw_data, encryption_key)`.
    * Hitung `data_hash` dari `medical_record_in.raw_data` (sebelum enkripsi) menggunakan `hash_data()`.
    * Simpan `MedicalRecord` ke database menggunakan `crud_medical_record.create_medical_record`, berikan `encrypted_data` dan `data_hash`. Dapatkan ID record yang baru dibuat.
    * Panggil `blockchain_service.add_medical_record_hash(record_hash_hex=new_db_record.data_hash, patient_did=current_user.did, record_type=new_db_record.record_type.value)`.
    * Jika sukses, update `blockchain_record_id` di database untuk record tersebut menggunakan `crud_medical_record.update_medical_record_blockchain_id`.
    * Kembalikan data record yang telah dibuat. Tangani error jika terjadi.

3.  **Implementasi Endpoint `GET /medical-records/patient/me`:**
    * `@router.get("/patient/me", response_model=List[MedicalRecordResponse])`
    * `async def get_my_medical_records(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user), skip: int = 0, limit: int = 100)`
    * Gunakan `crud_medical_record.get_medical_records_by_patient_id(db, patient_id=current_user.id, skip=skip, limit=limit)`.
    * Kembalikan list of `MedicalRecordResponse`. (Perhatikan: `raw_data` dan `encrypted_data` tidak ada di `MedicalRecordResponse` by default, ini bagus untuk listing).

4.  **Implementasi Endpoint `GET /medical-records/{record_id}`:**
    * `@router.get("/{record_id}", response_model=MedicalRecordResponse)` (atau model baru yang menyertakan `raw_data` setelah dekripsi).
    * `async def get_medical_record_detail(record_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user))`
    * Ambil record dari DB menggunakan `crud_medical_record.get_medical_record_by_id(db, record_id=record_id)`.
    * **Otorisasi**: Pastikan `current_user.id == db_record.patient_id`. Jika tidak, `HTTPException(status.HTTP_403_FORBIDDEN)`.
    * Jika endpoint ini harus mengembalikan data yang didekripsi:
        * Dapatkan kunci enkripsi (mekanisme yang sama seperti saat enkripsi).
        * Dekripsi `db_record.encrypted_data` menggunakan `decrypt_data()`.
        * Buat Pydantic model baru `MedicalRecordDetailResponse(MedicalRecordResponse)` yang menyertakan field `raw_data: str`.
        * Return `MedicalRecordDetailResponse` dengan `raw_data` yang telah didekripsi.
    * Jika hanya metadata: return `MedicalRecordResponse`.

5.  **Tambahkan Router ke `src/app/main.py`:**
    * `app.include_router(medical_records.router, prefix="/api/v1/medical-records", tags=["medical_records"])`

## Bagian 5: Pengujian

1.  **Unit Tests untuk Utilitas Enkripsi & Hashing (`tests/test_encryption.py`):**
    * Test `encrypt_data` dan `decrypt_data` (pastikan data bisa dienkripsi dan didekripsi kembali ke bentuk semula).
    * Test `hash_data` (pastikan output konsisten untuk input yang sama).

2.  **Unit Tests untuk CRUD Medical Record (`tests/unit/crud/test_crud_medical_record.py`):**
    * Test `create_medical_record`.
    * Test `get_medical_record_by_id`.
    * Test `get_medical_records_by_patient_id`.
    * Test `update_medical_record_blockchain_id`.
    * Gunakan session database testing dari `conftest.py`.

3.  **Unit Tests untuk `BlockchainService` (Metode Medical Record):**
    * Di `tests/unit/core/test_blockchain_service.py` (atau file serupa).
    * Test `add_medical_record_hash` dengan mock `Web3` dan objek kontrak. Pastikan parameter yang benar diteruskan ke fungsi smart contract.

4.  **Integration Tests untuk API Endpoints Medical Record (`tests/integration/api/test_api_medical_records.py`):**
    * Setup test user dan login untuk mendapatkan token.
    * Test `POST /medical-records`:
        * Verifikasi status code 201.
        * Verifikasi data tersimpan di DB dengan benar (`encrypted_data` tidak kosong, `data_hash` benar).
        * Verifikasi `BlockchainService.add_medical_record_hash` dipanggil dengan argumen yang benar (menggunakan mock).
        * Verifikasi `blockchain_record_id` di DB diupdate.
    * Test `GET /medical-records/patient/me`:
        * Verifikasi status code 200 dan data yang dikembalikan sesuai.
        * Verifikasi hanya record milik user yang login yang kembali.
    * Test `GET /medical-records/{record_id}`:
        * Verifikasi status code 200.
        * Verifikasi otorisasi (user hanya bisa akses record miliknya).
        * Jika mengembalikan data terdekripsi, verifikasi dekripsi berhasil.
    * Test kasus error (misalnya, record tidak ditemukan, tidak terotorisasi).

5.  **Smart Contract Tests (`blockchain/test/MedicalRecordRegistry.test.js` atau `.sol`):**
    * Gunakan Hardhat/Chai/Mocha.
    * Test fungsi `addRecord`:
        * Pastikan record ditambahkan dengan benar.
        * Pastikan event `RecordAdded` di-emit dengan parameter yang benar.
        * Test revert jika record hash sudah ada.
    * Test fungsi view `getRecordMetadata` (jika ada).

**Catatan Penting Selama Implementasi:**
* **Keamanan Kunci Enkripsi:** Strategi kunci yang digunakan di baby steps ini (mengambil dari config atau generate on-the-fly tanpa penyimpanan aman) adalah **HANYA UNTUK MVP DAN DEVELOPMENT**. Ini harus menjadi prioritas utama untuk ditingkatkan sebelum produksi.
* **Error Handling:** Implementasikan error handling yang baik di semua lapisan.
* **Logging:** Tambahkan logging yang informatif.
* **Commit Secara Berkala:** Setelah setiap baby step kecil selesai dan diuji, commit perubahan.