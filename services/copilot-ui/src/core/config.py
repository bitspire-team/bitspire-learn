from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Must use a sync driver (postgresql+psycopg2 or sqlite) — async drivers cause MissingGreenlet in Streamlit.
    DATABASE_URL: str

    # Pricing models for cost estimation board (dollars per 1 million tokens)
    PRICE_PER_1M_PROMPT_TOKENS: float = 2.0
    PRICE_PER_1M_COMPLETION_TOKENS: float = 12.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()
