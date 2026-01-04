# Use the 3.14 official docker hardened python dev image with debian trixie (v13)
FROM dhi.io/python:3.14-debian13-dev AS builder

# Copy uv binary
COPY --from=dhi.io/uv:0 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1

# Set the working directory
WORKDIR /app

# Copy the required files
COPY uv.lock pyproject.toml /app/

# Install the required packages
RUN uv sync --frozen --no-cache --no-install-project

# Use the 3.14 official docker hardened python image with debian trixie (v13)
FROM dhi.io/python:3.14-debian13

WORKDIR /app

# Add httpcheck binary (+~75KB)
COPY --from=ghcr.io/tarampampam/microcheck:1 /bin/httpcheck /bin/httpcheck

COPY main.py /app/
COPY server/ /app/server/

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Set environment to use the installed packages
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["httpcheck", "http://127.0.0.1:9000/"]

EXPOSE 9000

CMD ["/app/.venv/bin/fastapi", "run", "main.py", "--port", "9000", "--host", "0.0.0.0"]
