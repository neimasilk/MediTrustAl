import pytest
import httpx
import json
from respx import MockRouter  # Correct import for respx.mock

from src.app.services.nlp_service import extract_entities_from_text, DEEPSEEK_API_URL
from src.app.core.config import settings
from src.app.schemas.nlp import NLPEntity # For asserting the type of entities

@pytest.mark.asyncio
async def test_extract_entities_success_with_entities(respx_mock: MockRouter):
    """Test successful entity extraction with valid entities returned."""
    mock_response_content = json.dumps([
        {"text": "demam", "type": "Symptom"},
        {"text": "parasetamol", "type": "Medication"}
    ])
    mock_deepseek_response = {
        "choices": [{"message": {"content": mock_response_content}}]
    }
    respx_mock.post(DEEPSEEK_API_URL).mock(return_value=httpx.Response(200, json=mock_deepseek_response))

    result = await extract_entities_from_text("Pasien mengalami demam dan diberi parasetamol.")
    
    assert "entities" in result
    assert len(result["entities"]) == 2
    # Check if the items are dicts that can be validated by NLPEntity, or actual NLPEntity instances
    # Based on nlp_service.py, it directly creates NLPEntity instances if parsing is successful.
    for entity in result["entities"]:
        assert isinstance(entity, NLPEntity)
    
    assert result["entities"][0].text == "demam"
    assert result["entities"][0].type == "Symptom"
    assert result["entities"][1].text == "parasetamol"
    assert result["entities"][1].type == "Medication"

@pytest.mark.asyncio
async def test_extract_entities_success_no_entities(respx_mock: MockRouter):
    """Test successful API call but no entities found by DeepSeek."""
    mock_response_content = json.dumps([]) # Empty list of entities
    mock_deepseek_response = {
        "choices": [{"message": {"content": mock_response_content}}]
    }
    respx_mock.post(DEEPSEEK_API_URL).mock(return_value=httpx.Response(200, json=mock_deepseek_response))

    result = await extract_entities_from_text("Tidak ada informasi medis yang relevan.")
    
    assert "entities" in result
    assert len(result["entities"]) == 0

@pytest.mark.asyncio
async def test_extract_entities_deepseek_invalid_json_content(respx_mock: MockRouter):
    """Test DeepSeek returning 200 OK but content is not valid JSON."""
    mock_response_content = "Ini bukan JSON, tapi teks biasa."
    mock_deepseek_response = {
        "choices": [{"message": {"content": mock_response_content}}]
    }
    respx_mock.post(DEEPSEEK_API_URL).mock(return_value=httpx.Response(200, json=mock_deepseek_response))

    result = await extract_entities_from_text("Input teks acak.")
    
    assert "entities" in result
    assert len(result["entities"]) == 0 # Expect empty list due to parsing error

@pytest.mark.asyncio
async def test_extract_entities_deepseek_malformed_entities_list(respx_mock: MockRouter):
    """Test DeepSeek returns JSON, but not a list of valid entity dicts."""
    mock_response_content = json.dumps({"entities": "bukan list"}) # Not a list
    mock_deepseek_response = {
        "choices": [{"message": {"content": mock_response_content}}]
    }
    respx_mock.post(DEEPSEEK_API_URL).mock(return_value=httpx.Response(200, json=mock_deepseek_response))

    result = await extract_entities_from_text("Input teks lain.")
    assert "entities" in result
    assert len(result["entities"]) == 0

@pytest.mark.asyncio
async def test_extract_entities_deepseek_malformed_entity_item(respx_mock: MockRouter):
    """Test DeepSeek returns a list, but items are not valid entity dicts."""
    mock_response_content = json.dumps([
        {"text": "demam"}, # Missing 'type'
        {"type": "Medication"} # Missing 'text'
    ])
    mock_deepseek_response = {
        "choices": [{"message": {"content": mock_response_content}}]
    }
    respx_mock.post(DEEPSEEK_API_URL).mock(return_value=httpx.Response(200, json=mock_deepseek_response))

    result = await extract_entities_from_text("Input teks lagi.")
    assert "entities" in result
    assert len(result["entities"]) == 0 # Items are skipped

@pytest.mark.asyncio
async def test_extract_entities_deepseek_api_http_error(respx_mock: MockRouter):
    """Test handling of HTTP error (e.g., 500) from DeepSeek API."""
    respx_mock.post(DEEPSEEK_API_URL).mock(return_value=httpx.Response(500, text="Internal Server Error"))

    with pytest.raises(httpx.HTTPStatusError):
        await extract_entities_from_text("Tes error API.")

@pytest.mark.asyncio
async def test_extract_entities_deepseek_api_request_error(respx_mock: MockRouter):
    """Test handling of network request error when calling DeepSeek API."""
    respx_mock.post(DEEPSEEK_API_URL).mock(side_effect=httpx.RequestError("Simulated network error"))

    with pytest.raises(httpx.RequestError):
        await extract_entities_from_text("Tes error request.")

@pytest.mark.asyncio
async def test_extract_entities_no_api_key(mocker): # mocker fixture from pytest-mock
    """Test behavior when DEEPSEEK_API_KEY is not configured."""
    # Temporarily mock settings.DEEPSEEK_API_KEY to be None or empty
    mocker.patch.object(settings, 'DEEPSEEK_API_KEY', None)
    
    with pytest.raises(ValueError, match="DEEPSEEK_API_KEY not configured."):
        await extract_entities_from_text("Tes tanpa API key.")

@pytest.mark.asyncio
async def test_extract_entities_deepseek_empty_choices(respx_mock: MockRouter):
    """Test DeepSeek returning 200 OK but 'choices' is empty or malformed."""
    mock_deepseek_response = {"choices": []} # Empty choices
    respx_mock.post(DEEPSEEK_API_URL).mock(return_value=httpx.Response(200, json=mock_deepseek_response))

    result = await extract_entities_from_text("Input.")
    assert "entities" in result
    assert len(result["entities"]) == 0

@pytest.mark.asyncio
async def test_extract_entities_deepseek_no_message_in_choice(respx_mock: MockRouter):
    """Test DeepSeek returning 200 OK but a choice has no 'message'."""
    mock_deepseek_response = {"choices": [{}]} # Choice without message
    respx_mock.post(DEEPSEEK_API_URL).mock(return_value=httpx.Response(200, json=mock_deepseek_response))

    result = await extract_entities_from_text("Input..")
    assert "entities" in result
    assert len(result["entities"]) == 0

@pytest.mark.asyncio
async def test_extract_entities_deepseek_no_content_in_message(respx_mock: MockRouter):
    """Test DeepSeek returning 200 OK but message has no 'content'."""
    mock_deepseek_response = {"choices": [{"message": {}}]} # Message without content
    respx_mock.post(DEEPSEEK_API_URL).mock(return_value=httpx.Response(200, json=mock_deepseek_response))

    result = await extract_entities_from_text("Input...")
    assert "entities" in result
    assert len(result["entities"]) == 0
