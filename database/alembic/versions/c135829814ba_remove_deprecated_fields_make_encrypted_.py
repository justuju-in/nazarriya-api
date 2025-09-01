"""remove_deprecated_fields_make_encrypted_required

Revision ID: c135829814ba
Revises: 30b4eacfaccd
Create Date: 2025-09-01 13:04:19.632805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c135829814ba'
down_revision = '30b4eacfaccd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Since we're not in production, delete all existing data to avoid null constraint issues
    op.execute("DELETE FROM chat_messages")
    op.execute("DELETE FROM chat_sessions")
    
    # Remove deprecated content field from chat_messages
    op.drop_column('chat_messages', 'content')
    
    # Remove deprecated session_data field from chat_sessions
    op.drop_column('chat_sessions', 'session_data')
    
    # Make encrypted fields required (non-nullable)
    op.alter_column('chat_messages', 'encrypted_content', nullable=False)
    op.alter_column('chat_messages', 'encryption_metadata', nullable=False)
    op.alter_column('chat_messages', 'content_hash', nullable=False)


def downgrade() -> None:
    # Add back deprecated fields
    op.add_column('chat_messages', sa.Column('content', sa.Text(), nullable=True))
    op.add_column('chat_sessions', sa.Column('session_data', sa.JSON(), nullable=True))
    
    # Make encrypted fields nullable again
    op.alter_column('chat_messages', 'encrypted_content', nullable=True)
    op.alter_column('chat_messages', 'encryption_metadata', nullable=True)
    op.alter_column('chat_messages', 'content_hash', nullable=True)
