import json
import logging
import re
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse

import httpx
from fastapi import Depends

from src.models.request_log import RequestLog
from src.models.response_log import ResponseLog
from src.repositories.message import MessageRepository
from src.repositories.repository import RepositoryRepository
from src.repositories.user import UserRepository

logger = logging.getLogger(__name__)

github_client = httpx.AsyncClient(timeout=10.0)


class RequestInsightService:
    def __init__(
        self,
        user_repo: UserRepository = Depends(),
        repo_repo: RepositoryRepository = Depends(),
        message_repo: MessageRepository = Depends(),
    ):
        self.user_repo = user_repo
        self.repo_repo = repo_repo
        self.message_repo = message_repo

    @staticmethod
    def parse_content_payload(content) -> str:
        if isinstance(content, list):
            texts = [p.get("text", "") for p in content if isinstance(p, dict)]
            return "\n".join(texts)
        if isinstance(content, dict) and "text" in content:
            return str(content["text"])
        return str(content) if content is not None else ""

    @staticmethod
    def extract_xml_metadata(text: str) -> tuple[str, dict]:
        if not text:
            return "", {}

        parts = re.split(r"(?si)(<([a-z0-9_\-]+)[^>]*>.*?</\2>)", text)
        plain_text_parts = []
        meta_data = {}

        i = 0
        while i < len(parts):
            text_part = parts[i]
            tag_match = parts[i + 1] if i + 1 < len(parts) else None
            tag_name = parts[i + 2] if i + 2 < len(parts) else None

            if text_part and text_part.strip():
                plain_text_parts.append(text_part.strip())

            if tag_match and tag_name:
                meta_data.setdefault(tag_name, []).append(tag_match)

            i += 3

        plain_text = "\n\n".join(plain_text_parts)
        return plain_text, meta_data

    @staticmethod
    async def fetch_github_profile(auth_header: str) -> dict:
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
            msg = "The GitHub profile could not be fetched."
            raise ValueError(msg)
        profile = response.json()
        if not isinstance(profile.get("id"), int):
            msg = "The GitHub profile is missing a valid user ID."
            raise ValueError(msg)
        logger.info("Fetched GitHub profile for user %s.", profile.get("login"))
        return profile

    async def resolve_user(self, headers: dict) -> None:
        auth = headers.get("authorization", "")
        if not auth.startswith("Bearer gho_"):
            return
        profile = await self.fetch_github_profile(auth)
        github_id = profile["id"]
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
        logger.info("Discovered new user %s (GitHub ID %d).", user.login, user.github_id)

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
        await self.repo_repo.create(owner=owner, name=name, nwo=nwo, created_on=datetime.now(UTC))
        logger.info("Discovered new repository %s.", nwo)

    def extract_generated_messages(self, response_body) -> list[dict]:
        if isinstance(response_body, str):
            try:
                response_body = json.loads(response_body)
            except Exception:
                return []
        if not isinstance(response_body, dict):
            return []

        generated_messages = []

        for choice in response_body.get("choices") or []:
            msg = choice.get("message") or {}
            if msg.get("content"):
                generated_messages.append({"role": msg.get("role") or "assistant", "content": str(msg["content"])})

        chunks, roles = {}, {}
        for event in response_body.get("sse_events") or []:
            for choice in event.get("choices") or []:
                idx = choice.get("index", 0)
                delta = choice.get("delta") or {}
                if delta.get("role"):
                    roles[idx] = delta["role"]
                if delta.get("content"):
                    chunks.setdefault(idx, []).append(str(delta["content"]))

        for idx, content_chunks in sorted(chunks.items()):
            content = "".join(content_chunks).strip()
            if content:
                generated_messages.append({"role": roles.get(idx, "assistant"), "content": content})

        return generated_messages

    async def resolve_messages(self, request_body: dict, request_log_id: str, model_name: str | None = None) -> None:
        for msg in request_body.get("messages", []):
            role = msg.get("role")
            content = msg.get("content")
            if not role or content is None:
                continue

            raw_text = self.parse_content_payload(content)
            plain_text, meta_data = self.extract_xml_metadata(raw_text)

            await self.message_repo.create(
                request_log_id=request_log_id,
                role=role,
                content=content,
                text=plain_text,
                meta_data=meta_data,
                model=model_name,
                created_on=datetime.now(UTC),
            )
            logger.info("Stored request message with role %s for request %s.", role, request_log_id)

    async def resolve_generated_messages(
        self, response_body: dict, request_log_id: str, model_name: str | None = None
    ) -> None:
        generated = self.extract_generated_messages(response_body)
        for msg in generated:
            role = msg.get("role", "assistant")
            raw_text = msg.get("content", "")
            plain_text, meta_data = self.extract_xml_metadata(raw_text)

            await self.message_repo.create(
                request_log_id=request_log_id,
                role=role,
                content={"text": raw_text},
                text=plain_text,
                meta_data=meta_data,
                model=model_name,
                created_on=datetime.now(UTC),
            )
            logger.info("Stored generated message with role %s for request %s.", role, request_log_id)

    async def extract_and_store(self, request_log: RequestLog, response_log: ResponseLog) -> None:
        body = request_log.body if isinstance(request_log.body, dict) else {}
        resp_body = response_log.body if isinstance(response_log.body, dict) else {}

        await self.resolve_user(request_log.headers or {})  # type: ignore
        await self.resolve_repository(request_log.url)  # type: ignore

        model_name = body.get("model")

        await self.resolve_messages(body, request_log.id, model_name=model_name)  # type: ignore
        await self.resolve_generated_messages(resp_body, request_log.id, model_name=model_name)  # type: ignore
        logger.info(
            "Processed insights for %s %s (status: %d).",
            request_log.method,
            request_log.path,
            response_log.status_code,
        )
