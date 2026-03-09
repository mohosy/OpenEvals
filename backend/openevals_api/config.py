from __future__ import annotations

import base64
import hashlib
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPENEVALS_", extra="ignore")

    app_name: str = "OpenEvals"
    environment: str = "development"
    database_url: str = "sqlite:///./openevals.db"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str | None = None
    openai_judge_model: str = "gpt-4.1-mini"
    app_secret: str = "change-me"
    api_token: str | None = None
    frontend_origin: str = "http://localhost:5173"
    inline_runs: bool = False
    github_timeout_seconds: float = Field(default=15.0, ge=1.0, le=60.0)

    @property
    def fernet_key(self) -> bytes:
        digest = hashlib.sha256(self.app_secret.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)


@lru_cache
def get_settings() -> Settings:
    return Settings()

