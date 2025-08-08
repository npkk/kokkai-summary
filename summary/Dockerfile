FROM python:3.13-slim-bookworm

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

COPY summary/pyproject.toml summary/uv.lock ./

# local dependency
COPY db/ /db/

RUN uv sync --frozen

COPY summary/ ./

COPY summary/cronjob /etc/cron.d/summary-cron

RUN chmod 0644 /etc/cron.d/summary-cron

RUN crontab /etc/cron.d/summary-cron

CMD ["cron", "-f"]
