import pytest
from fastapi.testclient import TestClient
from src.app.main import app  # Import your FastAPI app

client = TestClient(app)

def test_extract_entities_nlp_api_valid_request():
    """
    Test the /api/v1/nlp/extract-entities endpoint with a valid request.
    """
    response = client.post("/api/v1/nlp/extract-entities", json={"text": "Some medical text here"})
    assert response.status_code == 200
    expected_json = {
        "entities": [
            {"text": "Blood Pressure", "type": "VitalSign"},
            {"text": "120/80 mmHg", "type": "Measurement"}
        ]
    }
    assert response.json() == expected_json

def test_extract_entities_nlp_api_another_valid_request():
    """
    Test with different valid input to ensure consistency of the placeholder.
    """
    response = client.post("/api/v1/nlp/extract-entities", json={"text": "Patient reports headache and fever."})
    assert response.status_code == 200
    expected_json = {
        "entities": [
            {"text": "Blood Pressure", "type": "VitalSign"},
            {"text": "120/80 mmHg", "type": "Measurement"}
        ]
    }
    assert response.json() == expected_json

def test_extract_entities_nlp_api_invalid_request_missing_text():
    """
    Test the endpoint with a request missing the 'text' field.
    Expects a 422 Unprocessable Entity response.
    """
    response = client.post("/api/v1/nlp/extract-entities", json={})
    assert response.status_code == 422

def test_extract_entities_nlp_api_invalid_request_wrong_type():
    """
    Test the endpoint with a request where 'text' has an incorrect data type.
    Expects a 422 Unprocessable Entity response.
    """
    response = client.post("/api/v1/nlp/extract-entities", json={"text": 123})
    assert response.status_code == 422

def test_extract_entities_nlp_api_empty_text_field():
    """
    Test the endpoint with a request where 'text' is an empty string.
    This is still a valid request according to the Pydantic model (str),
    so it should return the placeholder's dummy data and a 200 OK.
    """
    response = client.post("/api/v1/nlp/extract-entities", json={"text": ""})
    assert response.status_code == 200
    expected_json = {
        "entities": [
            {"text": "Blood Pressure", "type": "VitalSign"},
            {"text": "120/80 mmHg", "type": "Measurement"}
        ]
    }
    assert response.json() == expected_json
