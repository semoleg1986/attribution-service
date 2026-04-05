# Доменная Модель

## Структура Домена

```shell
src/domain/
|- tokens/
|  `- referral_token/
|     |- entity.py
|     |- repository.py
|     |- events.py
|     `- policies.py
|- visits/
|  `- visit/
|     |- entity.py
|     |- repository.py
|     `- events.py
|- conversions/
|  `- conversion/
|     |- entity.py
|     |- repository.py
|     |- events.py
|     `- policies.py
|- shared/
|  |- entity.py
|  |- statuses.py
|  `- value_objects.py
`- errors.py
```

## Корневые Агрегаты

- `ReferralToken`
- `AttributionConversion`

## Value Objects

- `DiscountPolicy`, `TokenTTL`, `AttributionSnapshot`, `Money`

## Репозиторные Порты

- `ReferralTokenRepository`
- `AttributionVisitRepository`
- `AttributionConversionRepository`

## Доменные События

- `ReferralTokenCreated`
- `ReferralTokenExpired`
- `AttributionVisitTracked`
- `AttributionConversionRecorded`
