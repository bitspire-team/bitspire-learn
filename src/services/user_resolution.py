import logging
from datetime import datetime

import httpx
from fastapi import Depends, Request

from src.repositories.user import UserRepository

logger = logging.getLogger(__name__)

GITHUB_API_USER_URL = "https://api.github.com/user"

github_client = httpx.AsyncClient(timeout=10.0)


async def fetch_github_profile(auth_header: str) -> dict | None:
    response = await github_client.get(
        GITHUB_API_USER_URL,
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


class UserResolutionService:
    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo

    async def resolve_user(self, request: Request) -> int | None:
        headers = dict(request.headers)
        auth = headers.get("authorization", "")
        machine_id = headers.get("vscode-machineid")

        if not machine_id:
            return None

        existing = await self.user_repo.get_by_machine_id(machine_id)
        if existing:
            await self.user_repo.update(existing, last_seen_at=datetime.now())
            logger.info("Resolved known user %s from machine id.", existing.login)
            return existing.id

        if not auth.startswith("Bearer gho_"):
            return None

        github_profile = await fetch_github_profile(auth)
        if not github_profile:
            return None

        github_id = github_profile.get("id")

        existing_by_gh = await self.user_repo.get_by_github_id(github_id)
        if existing_by_gh:
            await self.user_repo.update(
                existing_by_gh,
                machine_id=machine_id,
                last_seen_at=datetime.now(),
            )
            logger.info("Linked machine id to existing user %s.", existing_by_gh.login)
            return existing_by_gh.id

        now = datetime.now()
        user = await self.user_repo.create(
            github_id=github_id,
            login=github_profile.get("login"),
            name=github_profile.get("name"),
            email=github_profile.get("email"),
            avatar_url=github_profile.get("avatar_url"),
            machine_id=machine_id,
            first_seen_at=now,
            last_seen_at=now,
        )
        logger.info(
            "Resolved and saved new user %s (GitHub ID %d) from the authorization token.",
            user.login,
            user.github_id,
        )
        return user.id
