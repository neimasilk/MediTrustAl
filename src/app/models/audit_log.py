import uuid
from datetime import datetime, timezone # Added for default timestamp
from sqlalchemy import Column, ForeignKey, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from ..core.database import Base # Corrected import path

class AuditDataAccessLog(Base):
    __tablename__ = "audit_data_access_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # Changed for SQLite compatibility
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)) # Changed for SQLite compatibility
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=True)
    action_type = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=True)
    target_address = Column(String(42), nullable=True)
    details = Column(JSONB, nullable=True)

    actor_user = relationship("User", foreign_keys=[actor_user_id])
    owner_user = relationship("User", foreign_keys=[owner_user_id])
    medical_record = relationship("MedicalRecord", foreign_keys=[record_id])
