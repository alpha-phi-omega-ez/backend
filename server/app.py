from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.config import settings
from server.database import db_setup
from server.routes.auth import router as AuthRouter
from server.routes.backtest import router as BacktestRouter
from server.routes.laf import router as LAFRouter
from server.routes.loanertech import router as LoanerTechRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs during the startup phase
    await db_setup()
    yield  # Application runs here
    # This runs during the shutdown phase
    # Any cleanup logic can go here


app = FastAPI(lifespan=lifespan)

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
