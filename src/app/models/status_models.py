from pydantic import BaseModel
import datetime

class StatusResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime.datetime
    service_version: str