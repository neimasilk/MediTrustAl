import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    actor_user_id: uuid.UUID
    owner_user_id: uuid.UUID
    record_id: Optional[uuid.UUID] = None
    action_type: str
    ip_address: Optional[str] = None
    target_address: Optional[str] = None
    details: Optional[dict[str, Any]] = None # Using dict[str, Any] for JSONB

    model_config = ConfigDict(from_attributes=True)
