"""SQLAlchemy репозиторий конверсий."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.domain.conversions.conversion.entity import AttributionConversion
from src.domain.shared.statuses import AttributionChannel
from src.infrastructure.db.sqlalchemy.mappers.conversion_mapper import apply_to_model, to_domain
from src.infrastructure.db.sqlalchemy.models import AttributionConversionModel


class SqlalchemyAttributionConversionRepository:
    """SQLAlchemy реализация AttributionConversionRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, access_grant_id: str) -> AttributionConversion | None:
        model = self._session.get(AttributionConversionModel, access_grant_id)
        if model is None:
            return None
        return to_domain(model)

    def save(self, conversion: AttributionConversion) -> None:
        model = self._session.get(AttributionConversionModel, conversion.access_grant_id)
        if model is None:
            model = AttributionConversionModel(access_grant_id=conversion.access_grant_id)
            self._session.add(model)
        apply_to_model(conversion, model)

    def list(
        self,
        *,
        channel: AttributionChannel | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[AttributionConversion]:
        stmt = select(AttributionConversionModel)
        if channel is not None:
            stmt = stmt.where(AttributionConversionModel.channel == channel.value)
        if date_from is not None:
            stmt = stmt.where(func.date(AttributionConversionModel.created_at) >= date_from)
        if date_to is not None:
            stmt = stmt.where(func.date(AttributionConversionModel.created_at) <= date_to)
        stmt = stmt.order_by(AttributionConversionModel.created_at.asc())

        items = self._session.execute(stmt).scalars().all()
        return [to_domain(item) for item in items]
