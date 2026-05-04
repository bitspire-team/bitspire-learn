import pytest
from sqlalchemy import select
from src.models.user import User
from src.repositories.base import BaseRepository


@pytest.mark.asyncio
@pytest.mark.integration
class TestBaseRepository:
    async def test_create(self, async_session):
        repo = BaseRepository(User, async_session)
        user = await repo.create(github_id=123, login="testuser", name="Test User", email="test@example.com")

        assert user.id is not None
        assert user.login == "testuser"

        # Verify it's in the database


        result = await async_session.execute(select(User).where(User.login == "testuser"))
        db_user = result.scalar_one()
        assert db_user.github_id == 123

    async def test_update(self, async_session):
        repo = BaseRepository(User, async_session)
        user = await repo.create(github_id=456, login="updateuser", name="Original Name")

        updated_user = await repo.update(user, name="New Name")
        assert updated_user.name == "New Name"



        result = await async_session.execute(select(User).where(User.login == "updateuser"))
        db_user = result.scalar_one()
        assert db_user.name == "New Name"
