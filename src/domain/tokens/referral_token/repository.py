from __future__ import annotations

from typing import Protocol

from src.domain.shared.statuses import AttributionChannel, TokenStatus

from .entity import ReferralToken


class ReferralTokenRepository(Protocol):
    """Репозиторий агрегата ReferralToken."""

    def get(self, token: str) -> ReferralToken | None:
        """Получить токен по строковому значению."""

    def save(self, referral_token: ReferralToken) -> None:
        """Сохранить агрегат ReferralToken."""

    def list(
        self,
        *,
        channel: AttributionChannel | None = None,
        status: TokenStatus | None = None,
    ) -> list[ReferralToken]:
        """Вернуть список токенов по фильтрам."""
