import uuid
from datetime import UTC, datetime

import pytest

from src.models import RequestLog, ResponseLog


@pytest.mark.asyncio
@pytest.mark.integration
class TestRequestLog:
    async def test_insert_with_timezone_aware_timestamp(self, async_session):
        log = RequestLog(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(UTC),
            method="GET",
            url="http://example.com/models",
            path="/models",
            query=None,
            headers={"host": "example.com"},
            body=None,
        )
        async_session.add(log)
        await async_session.commit()

        result = await async_session.get(RequestLog, log.id)
        assert result is not None
        assert result.method == "GET"
        assert result.timestamp is not None


@pytest.mark.asyncio
@pytest.mark.integration
class TestResponseLog:
    async def test_insert_with_timezone_aware_timestamp(self, async_session):
        req = RequestLog(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(UTC),
            method="POST",
            url="http://example.com/chat",
            path="/chat",
            query=None,
            headers={},
            body=None,
        )
        async_session.add(req)
        await async_session.flush()

        log = ResponseLog(
            id=str(uuid.uuid4()),
            request_id=req.id,
            timestamp=datetime.now(UTC),
            status_code=200,
            headers={},
            body=None,
        )
        async_session.add(log)
        await async_session.commit()

        result = await async_session.get(ResponseLog, log.id)
        assert result is not None
        assert result.status_code == 200
