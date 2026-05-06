from unittest.mock import AsyncMock

import pytest
from src.models.token_usage import TokenUsage
from src.repositories.token_usage import TokenUsageRepository


class TestTokenUsageRepository:
    @pytest.fixture
    def mock_session(self):
        """Provide a dummy async session."""
        return AsyncMock()

    @pytest.fixture
    def repo(self, mock_session):
        """Provide TokenUsageRepository with a mock session."""
        return TokenUsageRepository(mock_session)

    def test_repository_initialization(self, repo, mock_session):
        """Repository initializes with correct model and session."""
        assert repo.model == TokenUsage
        assert repo.session == mock_session
