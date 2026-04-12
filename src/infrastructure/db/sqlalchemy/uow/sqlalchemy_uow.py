"""SQLAlchemy UnitOfWork attribution-service."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session, sessionmaker

from src.application.ports.repositories import RepositoryProvider
from src.infrastructure.db.sqlalchemy.repositories.conversion_repository_sqlalchemy import (
    SqlalchemyAttributionConversionRepository,
)
from src.infrastructure.db.sqlalchemy.repositories.referral_token_repository_sqlalchemy import (
    SqlalchemyReferralTokenRepository,
)
from src.infrastructure.db.sqlalchemy.repositories.visit_repository_sqlalchemy import (
    SqlalchemyAttributionVisitRepository,
)


@dataclass(frozen=True, slots=True)
class SqlalchemyRepositoryProvider(RepositoryProvider):
    """Провайдер SQLAlchemy-репозиториев."""

    referral_tokens: SqlalchemyReferralTokenRepository
    visits: SqlalchemyAttributionVisitRepository
    conversions: SqlalchemyAttributionConversionRepository


class SqlalchemyUnitOfWork:
    """Транзакционная обертка SQLAlchemy."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session = session_factory()
        self._repositories = SqlalchemyRepositoryProvider(
            referral_tokens=SqlalchemyReferralTokenRepository(self._session),
            visits=SqlalchemyAttributionVisitRepository(self._session),
            conversions=SqlalchemyAttributionConversionRepository(self._session),
        )

    @property
    def repositories(self) -> SqlalchemyRepositoryProvider:
        return self._repositories

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def close(self) -> None:
        self._session.close()
