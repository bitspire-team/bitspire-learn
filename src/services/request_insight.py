import logging
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse

import httpx
from fastapi import Depends

from src.models.attachment import Attachment
from src.models.prompt import Prompt
from src.models.request_log import RequestLog
from src.models.response_log import ResponseLog
from src.repositories.attachment import AttachmentRepository
from src.repositories.prompt import PromptRepository
from src.repositories.repository import RepositoryRepository
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
        repo_repo: RepositoryRepository = Depends(),
        attachment_repo: AttachmentRepository = Depends(),
    ):
        self.route_repo = route_repo
        self.user_repo = user_repo
        self.prompt_repo = prompt_repo
        self.repo_repo = repo_repo
        self.attachment_repo = attachment_repo

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
            method=method, path=path, created_on=datetime.now(UTC)
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
            created_on=datetime.now(UTC),
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
            hash=content_hash,
            role="system",
            content=content,
            created_on=datetime.now(UTC),
        )
        logger.info("Discovered new system prompt (hash %s).", content_hash[:12])

    async def resolve_repository(self, url: str) -> None:
        parsed = urlparse(url)
        nwo = parse_qs(parsed.query).get("repo_nwo", [None])[0]
        if not nwo:
            return
        existing = await self.repo_repo.get_by_nwo(nwo)
        if existing:
            return
        parts = nwo.split("/", 1)
        owner = parts[0] if len(parts) == 2 else ""
        name = parts[1] if len(parts) == 2 else nwo
        await self.repo_repo.create(
            owner=owner, name=name, nwo=nwo, created_on=datetime.now(UTC)
        )
        logger.info("Discovered new repository %s.", nwo)

    async def resolve_attachments(self, body) -> None:
        if not isinstance(body, dict):
            return
        for msg in body.get("messages", []):
            content = msg.get("content", "")
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                part_type = part.get("type", "")
                part_text = part.get("text", "")
                if not part_text:
                    continue
                content_hash = Attachment.compute_hash(part_text)
                existing = await self.attachment_repo.get_by_hash(content_hash)
                if existing:
                    continue
                await self.attachment_repo.create(
                    hash=content_hash,
                    type=part_type,
                    content=part_text,
                    created_on=datetime.now(UTC),
                )
                logger.info(
                    "Discovered new attachment of type %s (hash %s).",
                    part_type,
                    content_hash[:12],
                )

    async def extract_and_store(
        self, request_log: RequestLog, response_log: ResponseLog
    ) -> None:
        await self.resolve_route(request_log.method, request_log.path)
        await self.resolve_user(request_log.headers or {})
        await self.resolve_prompt(request_log.body)
        await self.resolve_repository(request_log.url)
        await self.resolve_attachments(request_log.body)
        logger.info(
            "Processed insights for %s %s (status: %d).",
            request_log.method,
            request_log.path,
            response_log.status_code,
        )
