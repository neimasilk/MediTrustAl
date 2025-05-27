# In src/app/models/ai_prediction.py
from typing import Dict, Any, Optional
from pydantic import BaseModel

class AIPredictionRequest(BaseModel):
    dummy_data: Dict[str, Any]

class AIPredictionResponse(BaseModel):
    risk_level: str
    score: float
    message: Optional[str] = None
