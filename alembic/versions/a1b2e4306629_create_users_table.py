"""Create users table

Revision ID: a1b2e4306629
Revises: 
Create Date: <Tanggal Pembuatan Awal Anda>

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from src.app.models.user import UserRole

# revision identifiers, used by Alembic.
revision = 'a1b2e4306629'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Explicitly create the ENUM type in PostgreSQL before creating the table
    postgresql.ENUM(UserRole, name='userrole').create(op.get_bind())
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('username', sa.String(length=50), nullable=False, unique=True),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('blockchain_address', sa.String(length=42), nullable=True, unique=True),
        sa.Column('did', sa.String(length=100), nullable=False, unique=True),
        sa.Column('role', postgresql.ENUM(UserRole, name='userrole', create_type=False), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.execute("DROP TYPE userrole;")
