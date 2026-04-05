from enum import StrEnum


class AttributionChannel(StrEnum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    ADS = "ads"
    PARTNER = "partner"
    OTHER = "other"


class TokenStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    EXPIRED = "expired"


class DiscountType(StrEnum):
    PERCENT = "percent"
    FIXED = "fixed"


class ConversionStage(StrEnum):
    REQUESTED = "requested"
    PAID = "paid"
