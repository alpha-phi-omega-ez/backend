from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from . import crud
from .db_models import Chargers
from .database import SessionLocal, engine
from .main import get_db

router = APIRouter(
    prefix="/chargers",
    tags=["chargers"],
    responses={404: {"description": "Not found"}},
)


@router.get("/list/", tags=["chargers"])
async def read_users(db: Session = Depends(get_db)):
    chargers = crud.get_chargers(db)
    result = {"chargers": chargers}
    return result
