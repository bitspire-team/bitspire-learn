"""simplify_message_id_to_integer

Revision ID: dc54357fb2b2
Revises: 
Create Date: 2026-05-04 23:48:57.446546

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc54357fb2b2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Change messages.id from VARCHAR to INTEGER with auto-increment sequence
    op.execute("""
        DO $$ BEGIN
            -- Create sequence if it doesn't exist
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.sequences
                WHERE sequence_schema = 'public' AND sequence_name = 'messages_id_seq'
            ) THEN
                CREATE SEQUENCE public.messages_id_seq
                    START WITH 1
                    INCREMENT BY 1
                    NO MINVALUE
                    NO MAXVALUE
                    CACHE 1;
            END IF;
        END $$;
    """)
    op.execute("""
        ALTER TABLE messages
            ADD COLUMN id_new INTEGER NOT NULL DEFAULT nextval('messages_id_seq');
    """)
    op.execute("""
        ALTER TABLE messages
            OWNER TO pi;
    """)
    op.execute("""
        ALTER SEQUENCE messages_id_seq OWNED BY messages.id_new;
    """)
    op.execute("""
        ALTER TABLE messages DROP CONSTRAINT messages_pkey CASCADE;
    """)
    op.execute("""
        ALTER TABLE messages DROP COLUMN id;
    """)
    op.execute("""
        ALTER TABLE messages RENAME COLUMN id_new TO id;
    """)
    op.execute("""
        ALTER TABLE messages ADD PRIMARY KEY (id);
    """)
    # Drop the old index on the removed column (may already be gone)
    try:
        op.drop_index("ix_messages_id", table_name="messages")
    except Exception:
        pass
    # Recreate index on new integer column
    op.create_index(op.f("ix_messages_id"), "messages", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Reverse: go back to VARCHAR primary key
    op.drop_constraint(None, "messages", type_="primary")
    op.drop_index(op.f("ix_messages_id"), table_name="messages")
    op.execute("ALTER TABLE messages DROP COLUMN id")
    op.execute("""
        ALTER TABLE messages
            ADD COLUMN id_new VARCHAR NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
    """)
    op.execute("""
        ALTER TABLE messages RENAME COLUMN id_new TO id;
    """)
    op.execute("""
        ALTER TABLE messages ADD PRIMARY KEY (id);
    """)
    op.create_index(op.f("ix_messages_id"), "messages", ["id"], unique=False)
    op.execute("DROP SEQUENCE IF EXISTS messages_id_seq")
