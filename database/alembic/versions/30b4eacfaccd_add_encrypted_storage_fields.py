"""add_encrypted_storage_fields

Revision ID: 30b4eacfaccd
Revises: 6c8664ba8b6e
Create Date: 2025-09-01 12:55:25.896128

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '30b4eacfaccd'
down_revision = '6c8664ba8b6e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add encrypted storage fields to chat_messages table
    op.add_column('chat_messages', sa.Column('encrypted_content', sa.LargeBinary(), nullable=True))
    op.add_column('chat_messages', sa.Column('encryption_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('chat_messages', sa.Column('content_hash', sa.String(length=64), nullable=True))
    
    # Add index on content_hash for integrity verification
    op.create_index(op.f('ix_chat_messages_content_hash'), 'chat_messages', ['content_hash'], unique=False)
    
    # Add encrypted storage fields to chat_sessions table for session data
    op.add_column('chat_sessions', sa.Column('encrypted_session_data', sa.LargeBinary(), nullable=True))
    op.add_column('chat_sessions', sa.Column('session_encryption_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    # Remove indexes
    op.drop_index(op.f('ix_chat_messages_content_hash'), table_name='chat_messages')
    
    # Remove encrypted storage fields from chat_messages table
    op.drop_column('chat_messages', 'content_hash')
    op.drop_column('chat_messages', 'encryption_metadata')
    op.drop_column('chat_messages', 'encrypted_content')
    
    # Remove encrypted storage fields from chat_sessions table
    op.drop_column('chat_sessions', 'session_encryption_metadata')
    op.drop_column('chat_sessions', 'encrypted_session_data')
