from __future__ import annotations

from typing import Protocol

from .entity import ReferralToken


class ReferralTokenRepository(Protocol):
    """Репозиторий агрегата ReferralToken."""

    def get(self, token: str) -> ReferralToken | None:
        """Получить токен по строковому значению."""

    def save(self, referral_token: ReferralToken) -> None:
        """Сохранить агрегат ReferralToken."""
