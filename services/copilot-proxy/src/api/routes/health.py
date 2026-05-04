import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Response

from src.repositories import HealthRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/live")
async def is_alive() -> dict:
    logger.info("Received a liveness probe request.")
    return {"status": "alive"}


@router.get("/healthy")
async def is_healthy(repo: Annotated[HealthRepository, Depends(HealthRepository)]) -> Response:
    logger.info("Received a health check request.")
    try:
        await repo.check()
        return Response(
            status_code=200,
            content=json.dumps({"status": "healthy"}),
            media_type="application/json",
        )
    except Exception as e:
        logger.exception("Database health check failed: %s", e)
        return Response(
            status_code=503,
            content=json.dumps({"status": "unhealthy", "error": "Database connection failed"}),
            media_type="application/json",
        )
