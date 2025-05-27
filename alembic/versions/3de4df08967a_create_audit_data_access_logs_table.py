"""create_audit_data_access_logs_table

Revision ID: 3de4df08967a
Revises: 9096078f2071
Create Date: 2025-05-27 10:01:21.688627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3de4df08967a'
down_revision: Union[str, None] = '9096078f2071'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'audit_data_access_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('actor_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('owner_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('record_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('medical_records.id'), nullable=True),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('target_address', sa.String(length=42), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.create_index(op.f('ix_audit_data_access_logs_actor_user_id'), 'audit_data_access_logs', ['actor_user_id'], unique=False)
    op.create_index(op.f('ix_audit_data_access_logs_owner_user_id'), 'audit_data_access_logs', ['owner_user_id'], unique=False)
    op.create_index(op.f('ix_audit_data_access_logs_record_id'), 'audit_data_access_logs', ['record_id'], unique=False)
    op.create_index(op.f('ix_audit_data_access_logs_timestamp'), 'audit_data_access_logs', ['timestamp'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_audit_data_access_logs_timestamp'), table_name='audit_data_access_logs')
    op.drop_index(op.f('ix_audit_data_access_logs_record_id'), table_name='audit_data_access_logs')
    op.drop_index(op.f('ix_audit_data_access_logs_owner_user_id'), table_name='audit_data_access_logs')
    op.drop_index(op.f('ix_audit_data_access_logs_actor_user_id'), table_name='audit_data_access_logs')
    op.drop_table('audit_data_access_logs')
