# Application Слой

## Назначение

Оркестрирует use cases токенов, трекинга и отчетности через порты и `ApplicationFacade`.

## Структура Application

```shell
src/application/
|- tokens/{commands,queries,handlers}/
|- tracking/{commands,queries,handlers}/
|- reporting/{queries,handlers}/
|- facade/application_facade.py
`- ports/
   |- repositories.py
   |- unit_of_work.py
   |- clock.py
   |- id_generator.py
   `- analytics_sink.py
```

## Command Side

- `CreateReferralToken`, `DisableReferralToken`
- `TrackVisit`
- `RecordConversionRequested`
- `RecordConversionPaid`

## Query Side

- `ResolveDiscount`
- `GetTokenStats`
- `GetChannelReport`

## Порты

- репозитории токенов, визитов и конверсий
- `UnitOfWork`
- опционально analytics sink/event bus
