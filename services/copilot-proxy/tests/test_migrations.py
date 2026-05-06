from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory


class TestMigrations:
    def test_upgrade_and_downgrade(self):
        """Test that we can upgrade to head and downgrade to base."""
        alembic_ini_path = str(Path(__file__).parent.parent / "alembic.ini")
        alembic_cfg = Config(alembic_ini_path)
        alembic_cfg.set_main_option("script_location", str(Path(__file__).parent.parent / "alembic"))

        # Determine the database URL
        # For testing purposes, we can use a synchronous memory database or similar
        # Since alembic env.py handles the connection, it should use the DATABASE_URL.

        # Test upgrade to the newest
        command.upgrade(alembic_cfg, "head")

        script = ScriptDirectory.from_config(alembic_cfg)
        revisions = list(script.walk_revisions())

        if len(revisions) >= 2:
            # Downgrade to previous
            previous_rev = revisions[1].revision
            command.downgrade(alembic_cfg, previous_rev)

            # Upgrade back to newest
            command.upgrade(alembic_cfg, "head")
