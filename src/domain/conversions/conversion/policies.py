"""Политики доступа для conversion use-cases."""

from __future__ import annotations

from src.domain.errors import AccessDeniedError
from src.domain.tokens.referral_token.policies import ActorContext


class InternalPolicy:
    """Политики внутренних операций (межсервисные endpoints)."""

    @staticmethod
    def ensure_can_call_internal(actor: ActorContext) -> None:
        allowed = {"admin", "service", "course_service"}
        if not (actor.roles & allowed):
            raise AccessDeniedError("Внутренняя операция недоступна для текущей роли.")
