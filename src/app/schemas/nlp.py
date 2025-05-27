from pydantic import BaseModel
from typing import List

class NLPEntity(BaseModel):
    text: str
    type: str

class NLPExtractionResponse(BaseModel):
    entities: List[NLPEntity]
