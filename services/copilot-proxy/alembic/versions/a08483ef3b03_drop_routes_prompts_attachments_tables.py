"""drop_routes_prompts_attachments_tables

Revision ID: a08483ef3b03
Revises: dc54357fb2b2
Create Date: 2026-05-05 00:06:16.725165

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a08483ef3b03'
down_revision: Union[str, Sequence[str], None] = 'dc54357fb2b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f('ix_routes_method'), table_name='routes')
    op.drop_index(op.f('ix_routes_path'), table_name='routes')
    op.drop_table('routes')
    op.drop_index(op.f('ix_attachments_hash'), table_name='attachments')
    op.drop_index(op.f('ix_attachments_type'), table_name='attachments')
    op.drop_table('attachments')
    op.drop_index(op.f('ix_prompts_hash'), table_name='prompts')
    op.drop_table('prompts')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table('prompts',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('hash', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('role', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_on', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('prompts_pkey'))
    )
    op.create_index(op.f('ix_prompts_hash'), 'prompts', ['hash'], unique=True)
    op.create_table('attachments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('hash', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('type', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_on', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('attachments_pkey'))
    )
    op.create_index(op.f('ix_attachments_type'), 'attachments', ['type'], unique=False)
    op.create_index(op.f('ix_attachments_hash'), 'attachments', ['hash'], unique=True)
    op.create_table('routes',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('method', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('path', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_on', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('routes_pkey'))
    )
    op.create_index(op.f('ix_routes_path'), 'routes', ['path'], unique=False)
    op.create_index(op.f('ix_routes_method'), 'routes', ['method'], unique=False)
