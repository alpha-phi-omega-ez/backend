from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.config import settings
from server.routes.auth import router as AuthRouter
from server.routes.loanertech import router as LoanerTechRouter
from server.routes.backtest import router as BacktestRouter

app = FastAPI()

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
app.include_router(AuthRouter, tags=["Auth"], prefix="")


@app.get("/", tags=["Root"])
async def read_root() -> dict[str, str]:
    return {"message": "Welcome to this fantastic app!"}
