"""create_medical_records_table

Revision ID: 9096078f2071
Revises: 
Create Date: 2025-05-26 15:31:25.530567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9096078f2071'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define Enum values for direct use in SQL
record_type_enum_values = [
    "DIAGNOSIS", "LAB_RESULT", "PRESCRIPTION", "TREATMENT_PLAN",
    "MEDICAL_HISTORY", "VITAL_SIGNS", "IMAGING", "VACCINATION"
]
record_type_sql_enum = sa.Enum(*record_type_enum_values, name="recordtype")


def upgrade() -> None:
    """Upgrade schema."""
    # Create the ENUM type in PostgreSQL
    op.execute(f"CREATE TYPE recordtype AS ENUM ({', '.join([f'''\'{val}\'''' for val in record_type_enum_values])})")

    op.create_table(
        'medical_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('blockchain_record_id', sa.String(length=66), nullable=True),
        sa.Column('record_type', record_type_sql_enum, nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('encrypted_data', sa.LargeBinary(), nullable=False),
        sa.Column('data_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('blockchain_record_id')
    )
    op.create_index(op.f('ix_medical_records_patient_id'), 'medical_records', ['patient_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_medical_records_patient_id'), table_name='medical_records')
    op.drop_table('medical_records')

    # Drop the ENUM type in PostgreSQL
    op.execute("DROP TYPE recordtype")
