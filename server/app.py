from fastapi import FastAPI

from server.routes.loanertech import router as LoanerTechRouter

app = FastAPI()

app.include_router(LoanerTechRouter, tags=["LoanerTech"], prefix="/loanertech")


@app.get("/", tags=["Root"])
async def read_root() -> dict[str, str]:
    return {"message": "Welcome to this fantastic app!"}
