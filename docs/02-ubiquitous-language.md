# Ubiquitous Language

## Базовые Термины

### ReferralToken
Корневой агрегат реферального ключа со скидочной политикой и lifecycle.

### Channel
Источник привлечения, например `email | sms | in_app | ads | partner | other`.

### DiscountPolicy
Value object скидки: `percent` или `fixed` с ограничениями по границам и валюте.

### AttributionVisit
Неизменяемый факт клика при входе по токену.

### AttributionConversion
Неизменяемый бизнес-факт конверсии (`requested`, `paid`).

### ConversionStage
Enum: `requested | paid`.

### TokenStatus
Enum: `active | disabled | expired`.

### TokenTTL
Правило срока жизни токена; для курсовых кампаний TTL по умолчанию = `course.starts_at`.

## Запрещенные Термины

| Термин | Причина |
|---|---|
| mutable click overwrite | факты кликов должны быть append-only |
| discount without token validation | скидка всегда должна быть подтверждена политикой |
| hidden attribution rewrite | конверсии — неизменяемые факты |
