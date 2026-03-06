# APOEZ Backend

Backend service for [apoez.org](https://apoez.org). It powers the campus lost and found (LAF) system, backtest listings, and loaner tech. The API is built with FastAPI and uses MongoDB and Valkey (Redis-compatible) for data and caching.

## Set up

Clone the repository and enter it:

```bash
git clone https://github.com/alpha-phi-omega-ez/backend.git
cd backend
```

Install and set up [UV](https://docs.astral.sh/uv/getting-started/installation/). Install dependencies with:

```bash
uv sync
```

Create a `.env` file (or export variables) with the required environment variables before running the service.

### MongoDB and Valkey

The backend expects a running MongoDB instance for backtests, LAF, and loaner tech data. Valkey is used for caching and session-related data. For local development you can start MongoDB with:

```bash
make start_db
```

For production, use your own MongoDB and Valkey deployment. An example [docker compose for MongoDB](https://github.com/alpha-phi-omega-ez/deployment/blob/main/main-website-docker-compose.yml) used with the APOEZ production system is in the deployment repo.

## Environment Variables

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| `SECRET_KEY` | (random) | Secret for JWT/session signing. In development a random key is used if unset. |
| `GOOGLE_CLIENT_ID` | None | Google OAuth client ID for login |
| `GOOGLE_CLIENT_SECRET` | None | Google OAuth client secret for login |
| `ORIGINS` | `http://localhost:3000` | Allowed CORS origins (comma-separated) |
| `MONGO_DETAILS` | `mongodb://localhost:27017` | MongoDB connection URI |
| `FRONTEND_URL` | `http://localhost:3000` | Frontend base URL for redirects/links |
| `BACKEND_URL` | `http://localhost:9000` | Backend base URL |
| `TESTING` | `false` | Set to `true` for test mode (e.g. disables Sentry) |
| `ROOT_PATH` | `""` | Root path when served behind a reverse proxy (e.g. `/api`) |
| `VALKEY_ADDRESS` | `127.0.0.1` | Valkey server address for caching |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `240` | JWT access token expiry in minutes |
| `SENTRY_DSN` | None | Sentry DSN for error tracking |
| `SENTRY_TRACE_RATE` | `1.0` | Sentry trace sample rate |
| `SENTRY_PROFILE_RATE` | `1.0` | Sentry profiling sample rate |

## Running

UV creates a virtual environment and installs packages there. Run the API with UV or the venv’s Python.

**Development** (auto-reload on file changes):

```bash
make develop
```

or:

```bash
uv run fastapi dev --port 9000
```

**One-off run** (e.g. production-like):

```bash
uv run python main.py
```

The server listens on port 9000. When running locally:

- API: <http://localhost:9000>
- Interactive API docs (Swagger): <http://localhost:9000/docs>
- ReDoc: <http://localhost:9000/redoc>

## Testing

Tests are run with pytest. UV’s environment is used automatically:

```bash
uv run pytest
```

Run with verbose output:

```bash
uv run pytest -v
```

Test paths and options are configured in `pyproject.toml` (`tests/` directory, `pythonpath = ["."]`).

## Linting and formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. CI runs Ruff on pull requests; run locally with:

**Lint:**

```bash
ruff check server
```

**Auto-fix lint issues:**

```bash
ruff check server --fix
```

**Format:**

```bash
ruff format server
```

Ruff is configured in `pyproject.toml` (line length, quote style, and selected rules).

## Deployment

The application is containerized and deployed as a Docker image. On push to `main`, GitHub Actions builds and pushes the image to:

- GitHub Container Registry: `ghcr.io/alpha-phi-omega-ez/backend`
- Docker Hub: `dhi.io/alpha-phi-omega-ez/backend`

The Dockerfile uses a multi-stage build, exposes port 9000, and includes a healthcheck against `http://127.0.0.1:9000/`. Run the container with the required environment variables (see [Environment Variables](#environment-variables)) and with MongoDB and Valkey available.

## Project structure

| Path | Description |
|------|-------------|
| `main.py` | Application entry point (uvicorn) |
| `server/app.py` | FastAPI app, CORS, Sentry, lifespan, route mounting |
| `server/config.py` | Settings (pydantic-settings) loaded from env and `.env` |
| `server/routes/` | API route modules: `auth`, `backtest`, `laf`, `loanertech` |
| `server/models/` | Pydantic/data models for API and DB |
| `server/database/` | DB access and setup (MongoDB, Valkey) |
| `server/helpers/` | Shared utilities (auth, sanitization, DB helpers) |
| `tests/` | Pytest tests |

Data model details for backtests (course codes, courses, backtest documents) are in `server/models/backtest.py` and are used by both this backend and the [backtest-compilation](https://github.com/alpha-phi-omega-ez/backtest-compilation) script.

## Documentation and contributing

- [Code of conduct](docs/CODE_OF_CONDUCT.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Pull request template](docs/pull_request_template.md)

## Authors

- [**Rafael Cenzano**](https://github.com/RafaelCenzano)

## License

This project is licensed under the GNU Affero General Public License - see the [LICENSE](LICENSE) file for details.
