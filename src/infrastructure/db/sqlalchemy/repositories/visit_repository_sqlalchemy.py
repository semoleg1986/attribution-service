"""SQLAlchemy репозиторий фактов переходов."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.domain.shared.statuses import AttributionChannel
from src.domain.visits.visit.entity import AttributionVisit
from src.infrastructure.db.sqlalchemy.mappers.visit_mapper import apply_to_model
from src.infrastructure.db.sqlalchemy.models import AttributionVisitModel


class SqlalchemyAttributionVisitRepository:
    """SQLAlchemy реализация AttributionVisitRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, visit: AttributionVisit) -> None:
        model = AttributionVisitModel(visit_id=visit.visit_id)
        apply_to_model(visit, model)
        self._session.add(model)

    def count(
        self,
        *,
        channel: AttributionChannel | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        stmt = select(func.count(AttributionVisitModel.visit_id))
        if channel is not None:
            stmt = stmt.where(AttributionVisitModel.channel == channel.value)
        if date_from is not None:
            stmt = stmt.where(func.date(AttributionVisitModel.clicked_at) >= date_from)
        if date_to is not None:
            stmt = stmt.where(func.date(AttributionVisitModel.clicked_at) <= date_to)

        return int(self._session.execute(stmt).scalar_one())
