"""Контракты агрегированного доступа к репозиториям."""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.conversions.conversion.repository import AttributionConversionRepository
from src.domain.tokens.referral_token.repository import ReferralTokenRepository
from src.domain.visits.visit.repository import AttributionVisitRepository


@dataclass(frozen=True, slots=True)
class RepositoryProvider:
    """Набор репозиториев attribution-service."""

    referral_tokens: ReferralTokenRepository
    visits: AttributionVisitRepository
    conversions: AttributionConversionRepository
