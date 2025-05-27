import uuid
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.app.core.database import get_db
from src.app.models.user import User
from src.app.api.endpoints.auth import get_current_active_user
from src.app.crud import crud_audit_log
from src.app.schemas.audit_log import AuditLogResponse

router = APIRouter()

@router.get(
    "/my-record-access-history",
    response_model=List[AuditLogResponse],
    summary="Get access history for the current user's records",
    description="Retrieves a list of audit log entries where the current user is the owner of the data/record.",
)
def get_my_record_access_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"),
):
    """
    Fetches the audit log entries related to records owned by the currently authenticated user.
    This allows users to see who has accessed their data.
    """
    logs = crud_audit_log.get_audit_logs_by_owner(
        db=db, owner_user_id=current_user.id, skip=skip, limit=limit
    )
    return logs
