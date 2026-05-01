import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import APIRouter, FastAPI

from src.api.routes.health import router as health_router
from src.api.routes.proxy import router as proxy_router
from src.api.routes.proxy import upstream_client
from src.core.db import init_db
from src.middleware import LoggingMiddleware

os.makedirs("outputs/logs", exist_ok=True)

log_file_path = os.path.join(
    "outputs/logs", f"proxy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file_path, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Application startup completed.")
    yield
    await upstream_client.aclose()
    logger.info("The proxy server is shutting down gracefully.")


def create_app() -> FastAPI:
    app = FastAPI(title="Copilot Proxy", lifespan=lifespan)

    app.add_middleware(LoggingMiddleware)

    api_router = APIRouter()
    api_router.include_router(health_router, tags=["health"])
    api_router.include_router(proxy_router, tags=["proxy"])
    app.include_router(api_router)
    return app


app = create_app()

if __name__ == "__main__":
    logger.info("The proxy server is starting up.")
    logger.info("The proxy server is writing logs to %s.", log_file_path)
    uvicorn.run(app)
