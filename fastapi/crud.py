from sqlalchemy.orm import Session

from .db_models import SubjectCodes, Chargers, ItemType


def get_subject_codes(db: Session):
    return db.execute(db.select(SubjectCodes)).all()


def get_chargers(db: Session):
    return db.execute(db.select(Chargers)).all()


def get_laf_types(db: Session):
    return db.execute(db.select(ItemType)).all()
