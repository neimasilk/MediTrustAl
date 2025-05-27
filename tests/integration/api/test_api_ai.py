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
