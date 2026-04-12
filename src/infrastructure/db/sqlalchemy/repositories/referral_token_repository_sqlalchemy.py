"""SQLAlchemy репозиторий referral tokens."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.shared.statuses import AttributionChannel, TokenStatus
from src.domain.tokens.referral_token.entity import ReferralToken
from src.infrastructure.db.sqlalchemy.mappers.referral_token_mapper import apply_to_model, to_domain
from src.infrastructure.db.sqlalchemy.models import ReferralTokenModel


class SqlalchemyReferralTokenRepository:
    """SQLAlchemy реализация ReferralTokenRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, token: str) -> ReferralToken | None:
        model = self._session.get(ReferralTokenModel, token)
        if model is None:
            return None
        return to_domain(model)

    def save(self, referral_token: ReferralToken) -> None:
        model = self._session.get(ReferralTokenModel, referral_token.token)
        if model is None:
            model = ReferralTokenModel(token=referral_token.token)
            self._session.add(model)
        apply_to_model(referral_token, model)

    def list(
        self,
        *,
        channel: AttributionChannel | None = None,
        status: TokenStatus | None = None,
    ) -> list[ReferralToken]:
        stmt = select(ReferralTokenModel)
        if channel is not None:
            stmt = stmt.where(ReferralTokenModel.channel == channel.value)
        if status is not None:
            stmt = stmt.where(ReferralTokenModel.status == status.value)
        stmt = stmt.order_by(ReferralTokenModel.created_at.asc())

        items = self._session.execute(stmt).scalars().all()
        return [to_domain(item) for item in items]
