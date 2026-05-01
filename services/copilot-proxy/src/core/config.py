from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    COPILOT_API_BASE_URL: str = "https://api.githubcopilot.com/"
    GITHUB_API_BASE_URL: str = "https://api.github.com/"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
