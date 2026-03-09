from __future__ import annotations

from cryptography.fernet import Fernet
from fastapi import Header, HTTPException, status

from openevals_api.config import get_settings


def _fernet() -> Fernet:
    return Fernet(get_settings().fernet_key)


def encrypt_secret(value: str | None) -> str | None:
    if not value:
        return None
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str | None) -> str | None:
    if not value:
        return None
    return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")


def require_api_token(x_api_token: str | None = Header(default=None)) -> None:
    expected = get_settings().api_token
    if expected and x_api_token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token.",
        )

