from apo import app, db
from apo.models import Chargers

from datetime import datetime, timezone
from pytz import timezone as pytz_timezone

from flask import make_response

# Timezone constant
local = pytz_timezone("US/Eastern")

# String constants
FMT = "%y-%m-%d %H:%M:%S"
DESC = "desc"
IN_OFFICE = "in_office"
CHECKED_OUT = "checked_out"
PHONE_NUMBER = "phone_number"
ID = "id"
AREA_CODE = "area_code"
MIDDLE = "middle"
END = "end"
RESPONSE = "response"

# SQLAlchemy constants
CHARGERS_SELECT = db.select(Chargers)


def list_chargers(admin=False):
    chargers = db.session.execute(CHARGERS_SELECT).all()

    if chargers is None:
        app.logger.error("Failed to query and find chargers")
        abort(500)

    charger_dict = {}

    if admin:
        for charger in chargers:
            charger_dict[charger.Chargers.id] = {
                DESC: charger.Chargers.description,
                IN_OFFICE: charger.Chargers.in_office,
                CHECKED_OUT: local.localize(charger.Chargers.checked_out).strftime(FMT),
                PHONE_NUMBER: f"({charger.Chargers.phone_area_code}){charger.Chargers.phone_middle}-{charger.Chargers.phone_end}",
            }
    else:
        for charger in chargers:
            charger_dict[charger.Chargers.id] = {
                DESC: charger.Chargers.description,
                IN_OFFICE: charger.Chargers.in_office,
            }

    app.logger.debug(f"charger list data created {charger_dict}")
    return charger_dict


def edit_desc(request_data):
    if ID not in request_data:
        return make_response(
            {RESPONSE: f"charger {charger.id} not found in request"}, 400
        )

    charger = db.get_or_404(Chargers, request_data[ID])

    if DESC not in request_data:
        return make_response(
            {RESPONSE: f"charger desc {charger.id} not found in request"}, 400
        )

    charger.description = request_data[DESC]
    db.session.commit()

    app.logger.debug(f"charger {charger} description updated")

    return make_response({RESPONSE: f"updated charger {charger.id} description"}, 200)


def checkout(request_data):
    if ID not in request_data:
        return make_response(
            {RESPONSE: f"charger {charger.id} not found in request"}, 400
        )

    charger = db.get_or_404(Chargers, request_data[ID])

    if not charger.in_office:
        return make_response({RESPONSE: f"charger {charger.id} not checked in"}, 400)

    charger.in_office = False
    charger.checked_out = datetime.now(timezone.utc)

    if (
        AREA_CODE not in request_data
        or MIDDLE not in request_data
        or END not in request_data
    ):
        return make_response(
            {RESPONSE: f"phone number {charger.id} not found in request"}, 400
        )

    charger.phone_area_code = request_data[AREA_CODE]
    charger.phone_middle = request_data[MIDDLE]
    charger.phone_end = request_data[END]
    db.session.commit()

    app.logger.debug(f"charger {charger} checkedout")

    return make_response({RESPONSE: f"checked out charger {charger.id}"}, 200)


def checkin(request_data):
    if ID not in request_data:
        return make_response(
            {RESPONSE: f"charger {charger.id} not found in request"}, 400
        )

    charger = db.get_or_404(Chargers, request_data[ID])

    if charger.in_office:
        return make_response(
            {RESPONSE: f"charger {charger.id} already checked in"}, 400
        )

    charger.in_office = True
    db.session.commit()

    app.logger.debug(f"charger {charger} checkedin")

    return make_response({RESPONSE: f"checked in charger {charger.id}"}, 200)


def create(request_data):
    if DESC not in request_data:
        return make_response(
            {"response": f"charger {charger.id} desc not found in request"}, 400
        )
    desc = request_data[DESC]

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

    app.logger.debug(f"charger {new_charger} created")

    return make_response({RESPONSE: f"created charger {new_charger.id}"}, 200)


def delete(request_data):
    if ID not in request_data:
        return make_response(
            {RESPONSE: f"charger {charger.id} not found in request"}, 400
        )

    desc = request_data[ID]

    charger = db.get_or_404(Chargers, request_data[ID])

    db.session.delete(charger)
    db.session.commit()

    app.logger.debug(f"charger {charger} deleted")

    return make_response({RESPONSE: f"charger {charger.id} deleted"}, 200)
