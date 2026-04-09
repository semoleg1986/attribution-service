"""Порт верификации Bearer access token."""

from __future__ import annotations

from typing import Protocol


class AccessTokenVerifier(Protocol):
    """Контракт декодирования и проверки access token."""

    def decode_access(self, access_token: str) -> dict[str, str | list[str]]:
        """Вернуть claims `sub` и `roles` из access token."""
