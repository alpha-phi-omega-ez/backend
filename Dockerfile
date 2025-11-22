# Python official 3.14.0 image on debian trixie (v13)
FROM python:3.14.0-slim-trixie

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

COPY . /app

# Install the dependencies
RUN uv sync --frozen --no-cache

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail --silent --show-error --output /dev/null http://0.0.0.0:9000 || exit 1

EXPOSE 9000

CMD ["/app/.venv/bin/fastapi", "run", "main.py", "--port", "9000", "--host", "0.0.0.0"]
