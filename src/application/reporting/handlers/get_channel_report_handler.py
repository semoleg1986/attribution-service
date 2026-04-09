"""Handler отчета по каналам атрибуции."""

from __future__ import annotations

from src.application.common.dto import ChannelReportItemResult, MoneyResult
from src.application.ports.unit_of_work import UnitOfWork
from src.application.reporting.queries.dto import GetChannelReportQuery
from src.domain.shared.statuses import AttributionChannel
from src.domain.tokens.referral_token.policies import ActorContext, AdminPolicy


class GetChannelReportHandler:
    """Собирает агрегированный отчет по воронке каналов."""

    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def __call__(self, query: GetChannelReportQuery) -> list[ChannelReportItemResult]:
        actor = ActorContext.from_claims(query.actor_id, query.actor_roles)
        AdminPolicy.ensure_can_view_reports(actor)

        result: list[ChannelReportItemResult] = []
        for channel in AttributionChannel:
            clicks = self._uow.repositories.visits.count(
                channel=channel,
                date_from=query.date_from,
                date_to=query.date_to,
            )
            conversions = self._uow.repositories.conversions.list(
                channel=channel,
                date_from=query.date_from,
                date_to=query.date_to,
            )
            requested = sum(1 for item in conversions if item.requested_recorded)
            paid = sum(1 for item in conversions if item.paid_recorded)
            paid_revenue = sum(
                item.paid_amount.amount
                for item in conversions
                if item.paid_recorded and item.paid_amount is not None
            )
            result.append(
                ChannelReportItemResult(
                    channel=channel.value,
                    clicks=clicks,
                    requested=requested,
                    paid=paid,
                    paid_revenue=MoneyResult(amount=paid_revenue, currency="USD"),
                )
            )
        return result
