FROM python:3.13-slim-bookworm
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*
WORKDIR /app/summary

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/
COPY summary/pyproject.toml summary/uv.lock ./
COPY db/ ../db/
COPY summary/app/ ./app/
COPY summary/main.py ./
COPY summary/tmp/ ./tmp/
RUN uv sync
COPY summary/cronjob /etc/cron.d/summary-cron
RUN chmod 0644 /etc/cron.d/summary-cron
RUN crontab /etc/cron.d/summary-cron
CMD ["cron", "-f"]
