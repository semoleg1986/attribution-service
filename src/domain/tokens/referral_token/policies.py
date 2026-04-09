"""Доменные политики доступа для referral token."""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.errors import AccessDeniedError


@dataclass(frozen=True, slots=True)
class ActorContext:
    """Контекст актора, извлеченный из access token claims."""

    actor_id: str
    roles: set[str]

    @classmethod
    def from_claims(cls, actor_id: str, roles: list[str]) -> "ActorContext":
        return cls(actor_id=actor_id, roles={item.strip().lower() for item in roles if item})


class AdminPolicy:
    """Политики доступа для admin-операций attribution."""

    @staticmethod
    def ensure_can_manage_tokens(actor: ActorContext) -> None:
        if "admin" not in actor.roles:
            raise AccessDeniedError("Операция доступна только роли admin.")

    @staticmethod
    def ensure_can_view_reports(actor: ActorContext) -> None:
        if "admin" not in actor.roles:
            raise AccessDeniedError("Отчет доступен только роли admin.")
