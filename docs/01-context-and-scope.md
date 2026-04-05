# Bounded Context И Границы

## Название Контекста

**Контекст Атрибуции И Промо**

## Назначение Контекста

Контекст управляет каналами, referral токенами, скидками и фактами конверсий.
Он валидирует входы атрибуции и возвращает детерминированные решения по скидке для потребляющих сервисов.

## Ответственность

1. создавать и управлять referral токенами
2. обеспечивать правила валидности токена и TTL
3. фиксировать факты кликов и конверсий
4. рассчитывать скидку по токену и политике
5. предоставлять отчетность по channel/token/campaign

## Структура Агрегатов

```shell
ReferralToken (Aggregate Root)
`- DiscountPolicy (Value Object)

AttributionConversion (Aggregate Root)
`- AttributionSnapshot (Value Object)
```

## Внешние Зависимости

Зависит от:
- `auth_service` для role context актора (admin/partner)
- `course_service` как producer/consumer фактов конверсии

Не зависит от:
- course/enrollment доменной логики
- прямого доступа к БД внешних сервисов

## Точки Интеграции

Входящие:
- CRUD-команды токенов
- команды трекинга кликов и конверсий
- запросы resolve discount

Исходящие:
- отчеты для admin dashboard
- опциональные события в analytics warehouse

## Явные Границы

Контекст не должен:
- принимать решения по course access/enrollment
- мутировать course/user агрегаты
