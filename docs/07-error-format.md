# Формат Ошибок (RFC 7807)

`attribution-service` возвращает ошибки как `application/problem+json`.

## Типы Проблем

- `/problems/validation` -> `422`
- `/problems/not-found` -> `404`
- `/problems/access-denied` -> `403`
- `/problems/conflict` -> `409`
- `/problems/unauthorized` -> `401`
