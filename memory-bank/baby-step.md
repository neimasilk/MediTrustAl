# Baby Step: Implementasi Placeholder AI Predictive Service (Step 3.2)

**Tanggal:** 2025-05-27
**Prioritas:** Tinggi
**Estimasi Waktu:** 2-3 Jam
**Referensi Dokumen:**
* `memory-bank/implementation-plan.md` (khususnya Step 3.2)
* `memory-bank/tech-stack.md` (untuk struktur layanan Python/FastAPI)
* `memory-bank/coding-rules.md`

## Tujuan:
Mengimplementasikan layanan AI placeholder yang sangat sederhana sebagai dasar untuk integrasi model AI prediktif yang lebih canggih di masa mendatang. Layanan ini akan memiliki satu endpoint API yang menerima data terstruktur dummy dan mengembalikan skor risiko dummy dalam format JSON.

## Detail Implementasi:

### 1. Buat Service AI Placeholder
* **File:** `src/app/services/ai_service.py`
* **Fungsi:** `predict_risk_placeholder(data: dict) -> dict`
    * **Input:** Sebuah dictionary `data` yang berisi data terstruktur dummy. Untuk MVP ini, fungsi akan mengabaikan konten `data` ini.
    * **Output:** Mengembalikan dictionary yang telah ditentukan sebelumnya yang merepresentasikan skor risiko dummy.
        ```python
        # Contoh implementasi di dalam src/app/services/ai_service.py
        def predict_risk_placeholder(data: dict) -> dict:
            """
            Placeholder function for AI risk prediction.
            Ignores the input data and returns a dummy risk score.
            """
            # Input 'data' is ignored for this placeholder
            return {
                "risk_level": "low", # Contoh: "low", "medium", "high"
                "score": 0.1,        # Contoh: float antara 0.0 dan 1.0
                "message": "This is a placeholder risk prediction."
            }
        ```

### 2. Definisikan Pydantic Models untuk API
* **File:** `src/app/models/ai_prediction.py` (atau bisa juga langsung di `src/app/api/endpoints/ai.py` jika hanya digunakan di sana). *Disarankan membuat file model terpisah untuk konsistensi.*
* **Model Request:** `AIPredictionRequest`
    ```python
    from pydantic import BaseModel, Field
    from typing import Optional, Dict, Any

    class AIPredictionRequest(BaseModel):
        # Sesuai implementation-plan.md: {"age": 50, "systolic_bp": 120}
        # Kita buat lebih generik untuk placeholder ini, agar bisa menerima berbagai struktur dummy
        # Atau bisa spesifik jika ingin meniru input model tertentu di masa depan.
        # Untuk placeholder, dictionary generik mungkin cukup.
        dummy_data: Dict[str, Any] = Field(..., description="Dummy structured data for AI prediction placeholder. Example: {'age': 50, 'systolic_bp': 120}")
        # Contoh lebih spesifik jika diinginkan:
        # age: Optional[int] = Field(None, example=50, description="Patient's age.")
        # systolic_bp: Optional[int] = Field(None, example=120, description="Patient's systolic blood pressure.")
        # other_features: Optional[Dict[str, Any]] = Field(None, description="Other dummy features.")
    ```
* **Model Response:** `AIPredictionResponse`
    ```python
    from pydantic import BaseModel, Field
    from typing import Optional

    class AIPredictionResponse(BaseModel):
        risk_level: str = Field(..., example="low", description="Predicted risk level (e.g., low, medium, high).")
        score: float = Field(..., example=0.1, description="Numerical risk score, typically between 0.0 and 1.0.")
        message: Optional[str] = Field(None, example="This is a placeholder risk prediction.", description="Additional information or message from the prediction service.")

    ```

### 3. Implementasi API Endpoint
* **File:** `src/app/api/endpoints/ai.py`
* **Router:** `APIRouter()`
* **Endpoint:** `POST /api/v1/ai/predict-risk`
    * Menggunakan `AIPredictionRequest` sebagai body request.
    * Menggunakan `AIPredictionResponse` sebagai model response.
    * Memanggil fungsi `predict_risk_placeholder` dari `ai_service.py`.
    ```python
    from fastapi import APIRouter
    # Jika model Pydantic dibuat di file terpisah:
    # from src.app.models.ai_prediction import AIPredictionRequest, AIPredictionResponse
    # Jika model Pydantic ada di file ini (kurang ideal):
    # from pydantic import BaseModel, Field ... (definisi model di sini)
    from src.app.services.ai_service import predict_risk_placeholder

    # Asumsikan model Pydantic ada di src/app/models/ai_prediction.py
    from src.app.models.ai_prediction import AIPredictionRequest, AIPredictionResponse


    router = APIRouter()

    @router.post(
        "/predict-risk",
        response_model=AIPredictionResponse,
        summary="Predicts Risk (Placeholder)",
        description="Receives dummy structured data and returns a *placeholder* risk prediction. This is a dummy implementation for MVP, intended to be replaced by a real AI model."
    )
    async def predict_risk_api(request_data: AIPredictionRequest):
        # request_data.dummy_data akan berisi dictionary dari body request
        # atau jika field spesifik (age, systolic_bp) didefinisikan, akses melalui request_data.age, dll.
        prediction_result = predict_risk_placeholder(request_data.dummy_data)
        return AIPredictionResponse(**prediction_result)
    ```

### 4. Registrasi Router AI di Aplikasi Utama
* **File:** `src/app/main.py`
* Tambahkan router AI ke aplikasi FastAPI.
    ```python
    # Di src/app/main.py
    from .api.endpoints import users, auth, medical_records, nlp as nlp_router, ai as ai_router # Tambahkan ai_router

    # ... (kode FastAPI app)

    app.include_router(ai_router.router, prefix="/api/v1/ai", tags=["AI Predictive Service"]) # Tambahkan ini
    ```

### 5. Buat Unit Tests
* **File:** `tests/unit/services/test_ai_service.py`
* Tes fungsi `predict_risk_placeholder` untuk memastikan ia mengembalikan output dummy yang diharapkan secara konsisten.
    ```python
    import pytest
    from src.app.services.ai_service import predict_risk_placeholder

    def test_predict_risk_placeholder_returns_dummy_data():
        expected_output = {
            "risk_level": "low",
            "score": 0.1,
            "message": "This is a placeholder risk prediction."
        }
        # Test dengan beberapa input dummy berbeda
        result1 = predict_risk_placeholder({"age": 50, "systolic_bp": 120})
        assert result1 == expected_output

        result2 = predict_risk_placeholder({"feature_x": "value_a", "feature_y": 123})
        assert result2 == expected_output

        result3 = predict_risk_placeholder({}) # Input kosong
        assert result3 == expected_output
    ```

### 6. Buat Integration Tests untuk API Endpoint
* **File:** `tests/integration/api/test_api_ai.py`
* Tes endpoint `POST /api/v1/ai/predict-risk`:
    * Valid request dengan body JSON yang sesuai.
    * Invalid request (misalnya, body JSON tidak sesuai dengan model `AIPredictionRequest`, jika ada validasi spesifik).
    ```python
    import pytest
    from fastapi.testclient import TestClient
    from src.app.main import app # Import your FastAPI app

    client = TestClient(app)

    def test_predict_risk_ai_api_valid_request():
        """
        Test the /api/v1/ai/predict-risk endpoint with a valid request.
        """
        request_payload = {
            "dummy_data": {"age": 50, "systolic_bp": 120, "cholesterol": 200}
        }
        response = client.post("/api/v1/ai/predict-risk", json=request_payload)
        assert response.status_code == 200
        expected_json = {
            "risk_level": "low",
            "score": 0.1,
            "message": "This is a placeholder risk prediction."
        }
        assert response.json() == expected_json

    def test_predict_risk_ai_api_another_valid_request():
        request_payload = {
            "dummy_data": {"location": "urban", "activity_level": "sedentary"}
        }
        response = client.post("/api/v1/ai/predict-risk", json=request_payload)
        assert response.status_code == 200
        expected_json = {
            "risk_level": "low",
            "score": 0.1,
            "message": "This is a placeholder risk prediction."
        }
        assert response.json() == expected_json

    def test_predict_risk_ai_api_invalid_request_missing_dummy_data():
        """
        Test with a request missing the 'dummy_data' field.
        Expects a 422 Unprocessable Entity response.
        """
        response = client.post("/api/v1/ai/predict-risk", json={}) # dummy_data is required
        assert response.status_code == 422
        # Pydantic v2 error format
        assert response.json()["detail"][0]["type"] == "missing"
        assert "dummy_data" in response.json()["detail"][0]["loc"]


    def test_predict_risk_ai_api_invalid_request_wrong_type_for_dummy_data():
        """
        Test with 'dummy_data' having an incorrect data type (e.g., string instead of dict).
        Expects a 422 Unprocessable Entity response.
        """
        response = client.post("/api/v1/ai/predict-risk", json={"dummy_data": "not a dictionary"})
        assert response.status_code == 422
        assert response.json()["detail"][0]["type"] == "dict_type" # Pydantic v2 error for wrong dict type
        assert "dummy_data" in response.json()["detail"][0]["loc"]
    ```

### 7. Dokumentasi
* Tambahkan komentar yang jelas di kode.
* Pastikan endpoint API dideskripsikan dengan baik di OpenAPI/Swagger, menjelaskan bahwa ini adalah *placeholder*. (FastAPI menangani ini secara otomatis berdasarkan `summary` dan `description` di decorator `@router.post`).

## Kriteria Keberhasilan:
* Semua file kode baru (`ai_service.py`, `models/ai_prediction.py`, `api/endpoints/ai.py`) berhasil dibuat dan diimplementasikan.
* Router AI berhasil didaftarkan di `main.py`.
* Semua unit test untuk `ai_service.py` lolos.
* Semua integration test untuk endpoint `/api/v1/ai/predict-risk` lolos.
* Endpoint API dapat diakses melalui Swagger UI dan menampilkan deskripsi placeholder.
* Tidak ada error linting (Flake8) atau formatting (Black) pada kode baru.

Dengan mengikuti langkah-langkah ini, implementasi placeholder AI predictive service akan jelas, terstruktur, dan mudah diverifikasi.