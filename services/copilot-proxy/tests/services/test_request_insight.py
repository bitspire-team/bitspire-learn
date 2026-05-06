from unittest.mock import AsyncMock

from src.services.request_insight import RequestInsightService


class TestRequestInsightService:
    def test_extract_usage_statistics_valid_json(self):
        service = RequestInsightService(AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock())
        response_body = {"usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}}
        result = service.extract_usage_statistics(response_body)
        assert result == {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}

    def test_extract_usage_statistics_sse(self):
        service = RequestInsightService(AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock())
        response_body = {
            "sse_events": [
                {"usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10}},
                {"usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}},
            ]
        }
        result = service.extract_usage_statistics(response_body)
        assert result == {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}

    def test_extract_usage_statistics_no_usage(self):
        service = RequestInsightService(AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock())
        result = service.extract_usage_statistics({"foo": "bar"})
        assert result == {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
