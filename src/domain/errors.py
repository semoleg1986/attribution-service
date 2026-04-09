class DomainError(Exception):
    """Базовая ошибка доменного слоя."""


class InvariantViolationError(DomainError):
    """Ошибка нарушения доменного инварианта."""


class AccessDeniedError(DomainError):
    """Ошибка нарушения политики доступа."""


class NotFoundError(DomainError):
    """Ошибка отсутствия доменной сущности."""
