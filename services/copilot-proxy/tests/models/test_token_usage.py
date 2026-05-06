from src.models.token_usage import TokenUsage


class TestTokenUsage:
    def test_token_usage_attributes(self):
        """TokenUsage model has expected attributes."""
        assert hasattr(TokenUsage, "id")
        assert hasattr(TokenUsage, "request_log_id")
        assert hasattr(TokenUsage, "user_id")
        assert hasattr(TokenUsage, "repository_id")
        assert hasattr(TokenUsage, "interaction_id")
        assert hasattr(TokenUsage, "model")
        assert hasattr(TokenUsage, "prompt_tokens")
        assert hasattr(TokenUsage, "completion_tokens")
        assert hasattr(TokenUsage, "total_tokens")
        assert hasattr(TokenUsage, "created_on")

    def test_tablename(self):
        """TokenUsage model uses correct table name."""
        assert TokenUsage.__tablename__ == "token_usages"
