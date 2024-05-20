from fastapi import FastAPI

from .database import SessionLocal
from .routers import chargers

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


get_db.create_all()

app.include_router(chargers.router)
