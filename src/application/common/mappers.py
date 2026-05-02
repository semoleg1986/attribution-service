"""Мапперы application DTO <-> domain entities."""

from __future__ import annotations

from src.application.common.dto import MoneyResult, ReferralTokenResult
from src.domain.shared.value_objects import Money
from src.domain.tokens.referral_token.entity import ReferralToken


def to_money_result(value: Money) -> MoneyResult:
    return MoneyResult(amount=value.amount, currency=value.currency)


def to_referral_token_result(token: ReferralToken) -> ReferralTokenResult:
    return ReferralTokenResult(
        token=token.token,
        status=token.status.value,
        channel=token.channel.value,
        campaign=token.campaign,
        source=token.source,
        medium=token.medium,
        course_id=token.course_id,
        discount_type=token.discount_type.value,
        discount_value=token.discount_value,
        expires_at=token.expires_at,
    )
