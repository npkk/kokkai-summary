FROM python:3.13

ENV PYTHONUNBUFFERED=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Set the working directory to the root of the application within the container
WORKDIR /app/

# Copy the api and db directories from the build context (project root)
COPY api/ ./api/
COPY db/ ./db/

# Set PYTHONPATH to include both api and db directories for module imports
ENV PYTHONPATH="/app/api:/app/db"

# Change to the api directory for dependency installation and running the app
WORKDIR /app/api/

# Place executables in the environment at the front of the path
ENV PATH="/app/api/.venv/bin:$PATH"

# Compile bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
ENV UV_LINK_MODE=copy

# Install dependencies
# uv.lock and pyproject.toml are now in /app/api/
# The `kokkai-db` dependency with `path = "../db"` will now correctly resolve
# because `db` is at `/app/db` (relative to /app/api, ../db points to /app/db)
RUN rm -rf .venv 
RUN rm -f uv.lock
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project

CMD ["uv", "run", "fastapi", "run", "--reload"]