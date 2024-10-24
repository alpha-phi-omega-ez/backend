from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes.loanertech import router as LoanerTechRouter

app = FastAPI()

# Define the origins that are allowed to make requests to your FastAPI app
origins = [
    "http://localhost:3000",  # Frontend URL
    # Add other origins as needed
]

# Add CORS middleware to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers (authorization, etc.)
)

app.include_router(LoanerTechRouter, tags=["LoanerTech"], prefix="/loanertech")


@app.get("/", tags=["Root"])
async def read_root() -> dict[str, str]:
    return {"message": "Welcome to this fantastic app!"}
