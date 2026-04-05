# Infrastructure Слой

## Назначение

Реализует persistence и reporting адаптеры за application-портами.

## Структура

```shell
src/infrastructure/
|- db/{session.py,models.py,repositories/,uow/}
|- messaging/{outbox_publisher.py,event_bus_kafka.py}
|- analytics/{report_queries.py}
`- di/providers.py
```
