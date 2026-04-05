from __future__ import annotations

from dataclasses import dataclass

from src.domain.errors import InvariantViolationError


@dataclass(frozen=True, slots=True)
class Money:
    """
    Денежное значение.

    :param amount: Сумма.
    :type amount: float
    :param currency: Валюта в формате ISO-4217.
    :type currency: str
    """

    amount: float
    currency: str

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvariantViolationError("Сумма не может быть отрицательной")
        if len(self.currency) != 3:
            raise InvariantViolationError("Валюта должна быть в формате ISO-4217")
