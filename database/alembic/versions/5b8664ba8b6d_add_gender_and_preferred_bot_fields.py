"""Add gender and preferred_bot fields to users table

Revision ID: 5b8664ba8b6d
Revises: 4a8664ba8b6c
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5b8664ba8b6d'
down_revision = '4a8664ba8b6c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column('users', sa.Column('gender', sa.String(length=10), nullable=True))
    op.add_column('users', sa.Column('preferred_bot', sa.String(length=10), nullable=True))


def downgrade() -> None:
    # Remove columns
    op.drop_column('users', 'preferred_bot')
    op.drop_column('users', 'gender')
