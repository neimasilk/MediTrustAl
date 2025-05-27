import httpx
import logging
import json # Added for parsing JSON string from DeepSeek response
from typing import List, Dict, Any # For type hinting

from src.app.core.config import settings # For DEEPSEEK_API_KEY
from src.app.schemas.nlp import NLPEntity, NLPExtractionResponse # Import Pydantic schemas

# Setup logger if you want specific logging for this service
logger = logging.getLogger(__name__)

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

async def extract_entities_from_text(text_input: str) -> Dict[str, List[NLPEntity]]:
    """
    Extracts medical entities from the input text using the DeepSeek API.
    """
    api_key = settings.DEEPSEEK_API_KEY
    if not api_key:
        logger.error("DEEPSEEK_API_KEY not configured.")
        # Depending on desired behavior, could raise an error or return empty/error dict
        raise ValueError("DEEPSEEK_API_KEY not configured.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Payload for DeepSeek API - designed for medical entity extraction
    # The system prompt instructs the model on its role and desired output format.
    # For actual production, testing different prompts and possibly fine-tuning a model would yield better results.
    payload = {
        "model": "deepseek-chat", # Using the general chat model
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert medical entity extractor. Your task is to identify and classify "
                    "medical entities from the provided text. The entities should be classified into "
                    "the following types: 'Symptom', 'Diagnosis', 'Medication', 'Procedure', "
                    "'AnatomicalSite', 'Observation', 'Condition', 'TestName', 'TestResult', 'Dosage', 'Frequency'. "
                    "For each recognized entity, provide its exact text from the input and its classified type. "
                    "If possible, try to return the output in a structured format, like a list of objects, "
                    "where each object has a 'text' and 'type' field. For example: "
                    "[{\"text\": \"fever\", \"type\": \"Symptom\"}, {\"text\": \"headache\", \"type\": \"Symptom\"}, {\"text\": \"amoxicillin\", \"type\": \"Medication\"}]"
                    # Adding instruction for JSON output might be beneficial if the model supports it well.
                    # "Please provide the output as a JSON list of objects, each with a 'text' and 'type' key."
                )
            },
            {
                "role": "user",
                "content": text_input
            }
        ],
        # temperature can be set low (e.g., 0.2) for more deterministic output in extraction tasks
        "temperature": 0.3, 
        # max_tokens might need adjustment based on expected input/output length
        # "max_tokens": 1024, 
    }

    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Sending request to DeepSeek API for entity extraction. Input text length: {len(text_input)}")
            response = await client.post(
                DEEPSEEK_API_URL,
                headers=headers,
                json=payload,
                timeout=30.0  # 30 seconds timeout
            )
            response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
            deepseek_response_data = response.json()
            logger.info("Successfully received response from DeepSeek API.")

            # Process the response to extract entities
            entities: List[NLPEntity] = []
            try:
                # Skenario 1: DeepSeek returns a JSON string in content
                content_string = deepseek_response_data.get('choices', [{}])[0].get('message', {}).get('content')
                if not content_string:
                    logger.warning("DeepSeek response content is empty or not found.")
                    return {"entities": []}

                # Attempt to parse the content string as JSON
                # The prompt guides the model to produce a list of {"text": ..., "type": ...}
                parsed_content = json.loads(content_string)
                
                if isinstance(parsed_content, list):
                    for item in parsed_content:
                        if isinstance(item, dict) and 'text' in item and 'type' in item:
                            entities.append(NLPEntity(text=item['text'], type=item['type']))
                        else:
                            logger.warning(f"Skipping invalid entity item: {item}")
                else:
                    logger.warning(f"Parsed content is not a list as expected: {parsed_content}")
                
                logger.info(f"Successfully extracted {len(entities)} entities.")
                return {"entities": entities}

            except json.JSONDecodeError as json_err:
                logger.error(f"Failed to parse JSON from DeepSeek response content: {json_err}")
                logger.error(f"Raw content from DeepSeek: {content_string}")
                # Fallback or error: If content is not JSON, or not the expected format.
                # For now, returning empty list. Could implement Skenario 2 (regex/string parsing) here if needed.
                return {"entities": []}
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"Unexpected structure in DeepSeek response: {e}. Response: {deepseek_response_data}")
                return {"entities": []}

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred while calling DeepSeek API: {e.response.status_code} - {e.response.text}")
        # Re-raise the error to be handled by the caller or a global error handler
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error occurred while calling DeepSeek API: {e}")
        # Re-raise or handle as a specific service error
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred in extract_entities_from_text: {e}")
        # Re-raise or handle
        raise
