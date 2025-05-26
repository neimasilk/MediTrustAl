from fastapi import APIRouter
import datetime
# Jika Anda membuat status_models.py:
from app.models.status_models import StatusResponse

router = APIRouter()

SERVICE_VERSION = "0.1.0"

@router.get("/status", response_model=StatusResponse) # Aktifkan response_model jika menggunakan Pydantic model
async def get_status():
    return {
        "status": "success",
        "message": "API is running and healthy.",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(), # ISO 8601 format
        "service_version": SERVICE_VERSION
    }