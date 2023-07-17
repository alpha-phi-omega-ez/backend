from datetime import datetime, timezone

from flask import abort
from pytz import timezone as pytz_timezone

from apo import app, db
from apo.models import Chargers

# Constants
LOCAL = pytz_timezone(zone="US/Eastern")
CHARGERS_SELECT = db.select(Chargers)


def list_chargers(admin: bool) -> dict:
    chargers = db.session.execute(CHARGERS_SELECT).all()

    if chargers is None:
        app.logger.error("Failed to query and find chargers")
        abort(500)

    charger_dict = {}

    if admin:
        for charger in chargers:
            charger_dict[charger.Chargers.id] = {
                "desc": charger.Chargers.description,
                "in_office": charger.Chargers.in_office,
                "checked_out": LOCAL.localize(charger.Chargers.checked_out).strftime(
                    "%d-%m-%Y %H:%M:%S"
                ),
                "phone_number": f"({charger.Chargers.phone_area_code}){charger.Chargers.phone_middle}-{charger.Chargers.phone_end}",
            }
    else:
        for charger in chargers:
            charger_dict[charger.Chargers.id] = {
                "desc": charger.Chargers.description,
                "in_office": charger.Chargers.in_office,
            }

    app.logger.debug(f"Charger list data created {charger_dict}")
    return charger_dict


def edit_desc(request_data: dict) -> dict:
    if "id" not in request_data or "desc" not in request_data:
        app.logger.debug("Missing request data to complete request")
        abort(400)

    charger = db.get_or_404(Chargers, request_data["id"])

    desc = request_data["desc"]
    if not isinstance(desc, str):
        app.logger.error("Description is not a string")
        abort(400)

    charger.description = desc
    db.session.commit()

    app.logger.debug(f"Charger {charger} description updated")

    return {"response": f"Updated charger {charger.id} description"}


def checkout(request_data: dict) -> dict:
    if (
        "id" not in request_data
        or "area_code" not in request_data
        or "middle" not in request_data
        or "end" not in request_data
    ):
        app.logger.debug("Missing request data to complete request")
        abort(400)

    area_code = request_data["phone_area_code"]
    middle = request_data["middle"]
    end = request_data["end"]

    if (
        isinstance(area_code, int)
        and isinstance(middle, int)
        and isinstance(end, int)
        and (area_code > 999 or middle > 999 or end > 9999)
    ):
        app.logger.debug("Phone number input error")
        abort(400)
    elif area_code is not None or middle is not None or end is not None:
        app.logger.debug("Phone number input error")
        abort(400)

    charger = db.get_or_404(Chargers, request_data["id"])

    if not charger.in_office:
        app.logger.debug(f"Charger {charger} is not in office and can't be checked out")
        abort(400)

    charger.in_office = False
    charger.checked_out = datetime.now(timezone.utc)

    charger.phone_area_code = area_code
    charger.phone_middle = middle
    charger.phone_end = end
    db.session.commit()

    app.logger.debug(f"Charger {charger} checkedout")

    return {"response": f"Checked out charger {charger.id}"}


def checkin(request_data: dict) -> dict:
    if "id" not in request_data:
        app.logger.debug("Missing request data to complete request")
        abort(400)

    charger = db.get_or_404(Chargers, request_data["id"])

    if charger.in_office:
        app.logger.debug(f"Charger {charger} is in the office and can't be checked in")
        abort(400)

    charger.in_office = True
    db.session.commit()

    app.logger.debug(f"Charger {charger} checkedin")

    return {"response": f"Checked in charger {charger.id}"}


def create(request_data: dict) -> dict:
    if "desc" not in request_data:
        app.logger.debug("Missing request data to complete request")
        abort(400)

    desc = request_data["desc"]

    new_charger = Chargers(
        in_office=True,
        checked_out=datetime.now(timezone.utc),
        description=desc,
        phone_area_code=None,
        phone_middle=None,
        phone_end=None,
    )
    db.session.add(new_charger)
    db.session.commit()

    app.logger.debug(f"Charger {new_charger} created")

    return {"response": f"created charger {new_charger.id}"}


def delete(request_data: dict) -> dict:
    if "id" not in request_data:
        app.logger.debug("Missing request data to complete request")
        abort(400)

    desc = request_data["id"]

    charger = db.get_or_404(Chargers, request_data["id"])

    db.session.delete(charger)
    db.session.commit()

    app.logger.debug(f"Charger {charger} deleted")

    return {"response": f"Charger {charger.id} deleted"}
