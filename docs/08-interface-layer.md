# Interface Слой

## Назначение

Публикует admin/public/internal HTTP-контракты атрибуции и маппит транспортные ошибки.

## Структура

```shell
src/interface/http/
|- app.py
|- main.py
|- health.py
|- errors.py
|- problem_types.py
|- wiring.py
`- v1/
   |- admin/router.py
   |- public/router.py
   |- internal/router.py
   `- schemas/
      |- tokens.py
      |- tracking.py
      `- reporting.py
```
