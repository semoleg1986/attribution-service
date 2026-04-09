FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.in ./
RUN pip install --no-cache-dir -r requirements.in

COPY . .

# В сервисе пока нет HTTP entrypoint, поэтому image публикуем как base-runtime.
CMD ["python", "-m", "pytest", "-q"]
