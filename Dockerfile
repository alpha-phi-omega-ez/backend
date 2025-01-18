# Use the latest uv image with python 3.13 and alpine
FROM ghcr.io/astral-sh/uv:python3.13-alpine

COPY . /app

WORKDIR /app

RUN uv sync --frozen --no-cache

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://0.0.0.0:9000 || exit 1

EXPOSE 9000

CMD ["/app/.venv/bin/fastapi", "run", "main.py", "--port", "9000", "--host", "0.0.0.0"]