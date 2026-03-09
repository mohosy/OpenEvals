from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from openevals_runner.suite_models import PromptTemplate


class SuiteImportRequest(BaseModel):
    yaml_content: Optional[str] = None
    github_url: Optional[str] = None
    slug: Optional[str] = None

    @field_validator("github_url")
    @classmethod
    def strip_url(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class SuiteUpdateRequest(BaseModel):
    yaml_content: str
    slug: Optional[str] = None


class RunCreateRequest(BaseModel):
    models: list[str] = Field(default_factory=list)
    prompt_override: Optional[PromptTemplate] = None
    api_key_override: Optional[str] = None
    case_ids: Optional[list[str]] = None


class CiRunUploadRequest(BaseModel):
    suite_name: str
    suite_yaml: str
    suite_hash: str
    models: list[str]
    result: dict[str, Any]
    git_ref: Optional[str] = None
    git_sha: Optional[str] = None

