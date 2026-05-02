"""Handler отчета по кампаниям атрибуции."""

from __future__ import annotations

from collections import defaultdict

from src.application.common.dto import (
    CampaignReportItemResult,
    MoneyResult,
    PaginatedCampaignReportResult,
)
from src.application.ports.unit_of_work import UnitOfWork
from src.application.reporting.queries.dto import GetCampaignReportQuery
from src.domain.shared.statuses import AttributionChannel
from src.domain.tokens.referral_token.policies import ActorContext, AdminPolicy


class GetCampaignReportHandler:
    """Собирает агрегированный отчет по кампаниям."""

    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def __call__(self, query: GetCampaignReportQuery) -> PaginatedCampaignReportResult:
        actor = ActorContext.from_claims(query.actor_id, query.actor_roles)
        AdminPolicy.ensure_can_view_reports(actor)

        channel_filter = (
            AttributionChannel(query.channel) if query.channel is not None else None
        )

        tokens = self._uow.repositories.referral_tokens.list(channel=channel_filter)
        token_to_campaign = {item.token: item.campaign for item in tokens}
        token_to_channel = {item.token: item.channel.value for item in tokens}

        aggregates: dict[
            tuple[str, str | None], dict[str, float | int | str | None]
        ] = defaultdict(
            lambda: {
                "clicks": 0,
                "requested": 0,
                "paid": 0,
                "gross_revenue": 0.0,
                "discount_total": 0.0,
            }
        )

        visits = self._uow.repositories.visits.list(
            channel=channel_filter,
            date_from=query.date_from,
            date_to=query.date_to,
        )
        for item in visits:
            campaign = token_to_campaign.get(item.token)
            channel = token_to_channel.get(item.token, item.channel.value)
            key = (channel, campaign)
            aggregates[key]["clicks"] += 1

        conversions = self._uow.repositories.conversions.list(
            channel=channel_filter,
            date_from=query.date_from,
            date_to=query.date_to,
        )
        for item in conversions:
            campaign = token_to_campaign.get(item.token or "")
            key = (item.channel.value, campaign)
            if item.requested_recorded:
                aggregates[key]["requested"] += 1
                if item.requested_discount is not None:
                    aggregates[key]["discount_total"] += item.requested_discount.amount
            if item.paid_recorded:
                aggregates[key]["paid"] += 1
                if item.paid_amount is not None:
                    aggregates[key]["gross_revenue"] += item.paid_amount.amount

        items = [
            CampaignReportItemResult(
                channel=channel,
                campaign=campaign,
                clicks=int(values["clicks"]),
                requested=int(values["requested"]),
                paid=int(values["paid"]),
                gross_revenue=MoneyResult(
                    amount=float(values["gross_revenue"]), currency="USD"
                ),
                discount_total=MoneyResult(
                    amount=float(values["discount_total"]), currency="USD"
                ),
            )
            for (channel, campaign), values in aggregates.items()
        ]
        items.sort(
            key=lambda item: (
                -item.gross_revenue.amount,
                item.channel,
                item.campaign or "",
            )
        )

        total = len(items)
        paginated = items[query.offset : query.offset + query.limit]
        return PaginatedCampaignReportResult(
            items=paginated,
            limit=query.limit,
            offset=query.offset,
            total=total,
        )
