import uuid
from sqlalchemy.orm import Session
from sqlalchemy import desc # Added for ordering
from src.app.models.audit_log import AuditDataAccessLog
from src.app.models import audit_log as models_audit # For type hinting if needed, or use AuditDataAccessLog directly

def create_audit_log(
    db: Session,
    actor_user_id: uuid.UUID,
    owner_user_id: uuid.UUID,
    action_type: str,
    record_id: uuid.UUID = None,
    ip_address: str = None,
    target_address: str = None,
    details: dict = None,
) -> AuditDataAccessLog:
    """
    Create a new audit data access log entry.
    """
    db_log = AuditDataAccessLog(
        actor_user_id=actor_user_id,
        owner_user_id=owner_user_id,
        action_type=action_type,
        record_id=record_id,
        ip_address=ip_address,
        target_address=target_address,
        details=details,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_audit_logs_by_owner(
    db: Session, owner_user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[AuditDataAccessLog]:
    """
    Retrieve audit logs for a specific owner, ordered by timestamp descending.
    """
    return (
        db.query(AuditDataAccessLog)
        .filter(AuditDataAccessLog.owner_user_id == owner_user_id)
        .order_by(desc(AuditDataAccessLog.timestamp))
        .offset(skip)
        .limit(limit)
        .all()
    )
