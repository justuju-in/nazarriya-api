"""Add phone_number field to users table

Revision ID: 6c8664ba8b6e
Revises: 5b8664ba8b6d
Create Date: 2025-01-27 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6c8664ba8b6e'
down_revision = '5b8664ba8b6d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add phone_number column as nullable initially
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))
    
    # Create unique index on phone_number
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)
    
    # Populate existing rows with dummy phone numbers
    # Format: 0000000000, 0000000001, 0000000002, etc.
    # Use a CTE approach that works with PostgreSQL
    op.execute("""
        WITH numbered_users AS (
            SELECT id, 
                   CONCAT('000000000', ROW_NUMBER() OVER (ORDER BY created_at) - 1) as new_phone
            FROM users 
            WHERE phone_number IS NULL
        )
        UPDATE users 
        SET phone_number = nu.new_phone
        FROM numbered_users nu
        WHERE users.id = nu.id
    """)
    
    # Make phone_number non-nullable after population
    op.alter_column('users', 'phone_number', nullable=False)


def downgrade() -> None:
    # Remove unique index
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    
    # Remove phone_number column
    op.drop_column('users', 'phone_number')
