from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
import httpx # For error handling from NLP service

# Use centralized schemas
from src.app.schemas.nlp import NLPEntity, NLPExtractionResponse
from src.app.services.nlp_service import extract_entities_from_text

router = APIRouter()

class NLPExtractionRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The input text from which to extract entities.")

# NLPEntity and NLPExtractionResponse are now imported from src.app.schemas.nlp

@router.post(
    "/extract-entities",
    response_model=NLPExtractionResponse,
    summary="Extracts Named Entities using DeepSeek API",
    description="Receives text input and returns a list of extracted medical entities by calling the DeepSeek API."
)
async def extract_entities(request: NLPExtractionRequest):
    try:
        # Call the actual NLP service function
        # The service function is expected to return a dict like {"entities": [...]}
        # where each item in the list is already an NLPEntity-like dict or Pydantic model.
        extraction_result_dict = await extract_entities_from_text(request.text)
        
        # Ensure the result from the service is in the correct format before passing to Pydantic model
        # The service already formats it as {"entities": [NLPEntity(...)]}
        # So, we can directly validate it with the response_model.
        return extraction_result_dict # FastAPI will validate this against NLPExtractionResponse
    
    except ValueError as ve:
        # This could be from API key not configured in nlp_service
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"NLP service configuration error: {str(ve)}"
        )
    except httpx.HTTPStatusError as hse:
        # Error from DeepSeek API itself (e.g., 4xx, 5xx)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error communicating with NLP service (DeepSeek API): {hse.response.status_code} - {hse.response.text}"
        )
    except httpx.RequestError as re:
        # Network error connecting to DeepSeek
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Network error communicating with NLP service: {str(re)}"
        )
    except Exception as e:
        # Any other unexpected error from the service or during processing
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during entity extraction: {str(e)}"
        )
