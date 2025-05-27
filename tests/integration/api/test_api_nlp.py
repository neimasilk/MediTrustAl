import pytest
from fastapi.testclient import TestClient
import httpx # For simulating HTTP errors from the service

from src.app.main import app
from src.app.core.config import API_V1_STR
from src.app.schemas.nlp import NLPEntity # Import for mocking service response accurately

# client = TestClient(app) # This will be used from conftest.py

# Test cases for the /api/v1/nlp/extract-entities endpoint
# We will mock the nlp_service.extract_entities_from_text directly

@pytest.mark.asyncio # To allow mocking async function if client itself is async
async def test_extract_entities_endpoint_success_with_entities(client: TestClient, mocker):
    """Test endpoint success when service returns entities."""
    mock_service_return_value = {"entities": [NLPEntity(text="fever", type="Symptom")]}
    
    # Corrected patch target: where 'extract_entities_from_text' is imported by the nlp endpoint module
    mocker.patch('src.app.api.endpoints.nlp.extract_entities_from_text', 
                 return_value=mock_service_return_value)

    response = client.post(f"{API_V1_STR}/nlp/extract-entities", json={"text": "Patient has a fever."})
    assert response.status_code == 200
    assert response.json() == {"entities": [{"text": "fever", "type": "Symptom"}]}


@pytest.mark.asyncio
async def test_extract_entities_endpoint_success_no_entities(client: TestClient, mocker):
    """Test endpoint success when service returns no entities."""
    mock_service_return_value = {"entities": []}
    mocker.patch('src.app.api.endpoints.nlp.extract_entities_from_text', 
                 return_value=mock_service_return_value)

    response = client.post(f"{API_V1_STR}/nlp/extract-entities", json={"text": "No relevant info."})
    assert response.status_code == 200
    assert response.json() == mock_service_return_value

@pytest.mark.asyncio
async def test_extract_entities_endpoint_service_raises_value_error(client: TestClient, mocker):
    """Test endpoint when service raises ValueError (e.g., API key missing)."""
    mocker.patch('src.app.api.endpoints.nlp.extract_entities_from_text', 
                 side_effect=ValueError("DEEPSEEK_API_KEY not configured."))

    response = client.post(f"{API_V1_STR}/nlp/extract-entities", json={"text": "Test API key error."})
    assert response.status_code == 503
    # The endpoint constructs a detailed message, check for its core part
    assert "Error communicating with NLP service (DeepSeek API): 500" in response.json()["detail"]


@pytest.mark.asyncio
async def test_extract_entities_endpoint_service_raises_http_status_error(client: TestClient, mocker):
    """Test endpoint when service raises HTTPStatusError (e.g., DeepSeek API down)."""
    # Simulate an HTTPStatusError from httpx
    mock_request = httpx.Request("POST", "https://api.deepseek.com/chat/completions")
    mock_response = httpx.Response(500, request=mock_request, content=b"DeepSeek API Error")
    
    mocker.patch('src.app.api.endpoints.nlp.extract_entities_from_text', 
                 side_effect=httpx.HTTPStatusError("DeepSeek API Error", request=mock_request, response=mock_response))

    response = client.post(f"{API_V1_STR}/nlp/extract-entities", json={"text": "Test DeepSeek API error."})
    assert response.status_code == 503 # Service Unavailable
    assert "Service unavailable" in response.json()["detail"]
    assert "Error communicating with NLP service" in response.json()["detail"]


@pytest.mark.asyncio
async def test_extract_entities_endpoint_service_raises_request_error(client: TestClient, mocker):
    """Test endpoint when service raises RequestError (e.g., network issue)."""
    mock_request = httpx.Request("POST", "https://api.deepseek.com/chat/completions")
    mocker.patch('src.app.api.endpoints.nlp.extract_entities_from_text', 
                 side_effect=httpx.RequestError("Network error", request=mock_request))

    response = client.post(f"{API_V1_STR}/nlp/extract-entities", json={"text": "Test network error."})
    assert response.status_code == 503 # Service Unavailable
    assert "Service unavailable" in response.json()["detail"]
    assert "Network error communicating with NLP service" in response.json()["detail"]


def test_extract_entities_nlp_api_invalid_request_missing_text(client: TestClient): # client fixture was already here
    """
    Test the endpoint with a request missing the 'text' field.
    Expects a 422 Unprocessable Entity response.
    """
    response = client.post("/api/v1/nlp/extract-entities", json={})
    assert response.status_code == 422

def test_extract_entities_nlp_api_invalid_request_wrong_type(client: TestClient): # Added client fixture
    """
    Test the endpoint with a request where 'text' has an incorrect data type.
    Expects a 422 Unprocessable Entity response.
    """
    response = client.post(f"{API_V1_STR}/nlp/extract-entities", json={"text": 123})
    assert response.status_code == 422

def test_extract_entities_nlp_api_empty_text_field(client: TestClient): # Changed to sync, no mocker
    """
    Test the endpoint with a request where 'text' is an empty string.
    The NLPExtractionRequest schema in src/app/api/endpoints/nlp.py has:
    text: str = Field(..., min_length=1, description="...")
    So an empty string should result in a 422 from FastAPI validation before service call.
    """
    response = client.post(f"{API_V1_STR}/nlp/extract-entities", json={"text": ""})
    assert response.status_code == 422
