import logging
from datetime import datetime

import httpx
from fastapi import Depends

from src.models.prompt import Prompt
from src.models.request_log import RequestLog
from src.models.response_log import ResponseLog
from src.repositories.prompt import PromptRepository
from src.repositories.route import RouteRepository
from src.repositories.user import UserRepository

logger = logging.getLogger(__name__)

github_client = httpx.AsyncClient(timeout=10.0)


class RequestInsightService:
    def __init__(
        self,
        route_repo: RouteRepository = Depends(),
        user_repo: UserRepository = Depends(),
        prompt_repo: PromptRepository = Depends(),
    ):
        self.route_repo = route_repo
        self.user_repo = user_repo
        self.prompt_repo = prompt_repo

    @staticmethod
    def extract_system_content(body) -> str | None:
        if not isinstance(body, dict):
            return None
        messages = body.get("messages", [])
        if not messages:
            return None
        content = messages[0].get("content", "")
        if isinstance(content, list):
            content = " ".join(
                p.get("text", "") for p in content if isinstance(p, dict)
            )
        return content if content else None

    async def resolve_route(self, method: str, path: str) -> None:
        existing = await self.route_repo.get_by_method_and_path(method, path)
        if existing:
            return
        await self.route_repo.create(
            method=method, path=path, created_on=datetime.now()
        )
        logger.info("Discovered new route %s %s.", method, path)

    @staticmethod
    async def fetch_github_profile(auth_header: str) -> dict | None:
        response = await github_client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": auth_header,
                "Accept": "application/vnd.github+json",
                "User-Agent": "copilot-proxy",
            },
        )
        if response.status_code != 200:
            logger.warning(
                "GitHub API returned status %d when resolving user profile.",
                response.status_code,
            )
            return None
        profile = response.json()
        logger.info("Fetched GitHub profile for user %s.", profile.get("login"))
        return profile

    async def resolve_user(self, headers: dict) -> None:
        auth = headers.get("authorization", "")
        if not auth.startswith("Bearer gho_"):
            return
        profile = await self.fetch_github_profile(auth)
        if not profile:
            return
        github_id = profile.get("id")
        existing = await self.user_repo.get_by_github_id(github_id)
        if existing:
            return
        user = await self.user_repo.create(
            github_id=github_id,
            login=profile.get("login"),
            name=profile.get("name"),
            email=profile.get("email"),
            avatar_url=profile.get("avatar_url"),
            created_on=datetime.now(),
        )
        logger.info(
            "Discovered new user %s (GitHub ID %d).", user.login, user.github_id
        )

    async def resolve_prompt(self, body) -> None:
        content = self.extract_system_content(body)
        if not content:
            return
        content_hash = Prompt.compute_hash(content)
        existing = await self.prompt_repo.get_by_hash(content_hash)
        if existing:
            return
        await self.prompt_repo.create(
            hash=content_hash, role="system", content=content, created_on=datetime.now()
        )
        logger.info("Discovered new system prompt (hash %s).", content_hash[:12])

    async def extract_and_store(
        self, request_log: RequestLog, response_log: ResponseLog
    ) -> None:
        await self.resolve_route(request_log.method, request_log.path)
        await self.resolve_user(request_log.headers or {})
        await self.resolve_prompt(request_log.body)
        logger.info(
            "Processed insights for %s %s (status: %d).",
            request_log.method,
            request_log.path,
            response_log.status_code,
        )
