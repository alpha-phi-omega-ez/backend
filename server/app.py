from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk

from server.config import settings
from server.database.laf import laf_db_setup
from server.routes.auth import router as AuthRouter
from server.routes.backtest import router as BacktestRouter
from server.routes.laf import router as LAFRouter
from server.routes.loanertech import router as LoanerTechRouter


sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=settings.SENTRY_TRACE_RATE,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=settings.SENTRY_PROFILE_RATE,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs during the startup phase
    await laf_db_setup()
    yield  # Application runs here
    # This runs during the shutdown phase
    # Any cleanup logic can go here


app = FastAPI(lifespan=lifespan, root_path=settings.ROOT_PATH)

# Add CORS middleware to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers (authorization, etc.)
)


app.include_router(LoanerTechRouter, tags=["LoanerTech"], prefix="/loanertech")
app.include_router(BacktestRouter, tags=["Backtests"], prefix="")
app.include_router(LAFRouter, tags=["laf"], prefix="/laf")
app.include_router(AuthRouter, tags=["Auth"], prefix="")


@app.api_route("/", methods=["GET", "HEAD"], tags=["Root"])
async def read_root() -> dict[str, str]:
    return {"message": "Welcome to the apoez backend!"}
