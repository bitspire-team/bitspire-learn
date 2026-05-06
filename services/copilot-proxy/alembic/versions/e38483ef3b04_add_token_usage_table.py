"""add_token_usage_table

Revision ID: e38483ef3b04
Revises: a08483ef3b03
Create Date: 2026-05-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e38483ef3b04'
down_revision: Union[str, Sequence[str], None] = 'a08483ef3b03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('token_usages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('request_log_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('repository_id', sa.Integer(), nullable=True),
        sa.Column('interaction_id', sa.String(), nullable=True),
        sa.Column('model', sa.String(), nullable=True),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('completion_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ),
        sa.ForeignKeyConstraint(['request_log_id'], ['request_logs.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_token_usages_interaction_id'), 'token_usages', ['interaction_id'], unique=False)
    op.create_index(op.f('ix_token_usages_model'), 'token_usages', ['model'], unique=False)
    op.create_index(op.f('ix_token_usages_repository_id'), 'token_usages', ['repository_id'], unique=False)
    op.create_index(op.f('ix_token_usages_request_log_id'), 'token_usages', ['request_log_id'], unique=False)
    op.create_index(op.f('ix_token_usages_user_id'), 'token_usages', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_token_usages_user_id'), table_name='token_usages')
    op.drop_index(op.f('ix_token_usages_request_log_id'), table_name='token_usages')
    op.drop_index(op.f('ix_token_usages_repository_id'), table_name='token_usages')
    op.drop_index(op.f('ix_token_usages_model'), table_name='token_usages')
    op.drop_index(op.f('ix_token_usages_interaction_id'), table_name='token_usages')
    op.drop_table('token_usages')
