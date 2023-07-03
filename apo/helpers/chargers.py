from apo import app, db
from apo.models import Chargers

from datetime import datetime, timezone
import pytz

from flask import make_response

local = pytz.timezone("US/Eastern")
fmt = "%y-%m-%d %H:%M:%S"


def list_chargers(admin=False):
    chargers = db.session.execute(db.select(Chargers)).all()
    charger_dict = {}
    if chargers is None:
        app.logger.error("Failed to query and find chargers")
        abort(500)

    for charger in chargers:
        if admin:
            charger_dict[charger.Chargers.id] = {
                "desc": charger.Chargers.description,
                "in_office": charger.Chargers.in_office,
                "checked_out": local.localize(charger.Chargers.checked_out).strftime(fmt),
                "phone_number": f"({charger.Chargers.phone_area_code}){charger.Chargers.phone_middle}-{charger.Chargers.phone_end}",
            }
        else:
            charger_dict[charger.Chargers.id] = {
                "desc": charger.Chargers.description,
                "in_office": charger.Chargers.in_office,
            }
    app.logger.debug(f"charger list data created {charger_dict}")
    return charger_dict


def edit_desc(request_data):
    if "id" not in request_data:
        return make_response(
            {"response": f"charger {charger.id} not found in request"}, 400
        )

    charger = db.get_or_404(Chargers, request_data["id"])

    if "desc" not in request_data:
        return make_response(
            {"response": f"charger desc {charger.id} not found in request"}, 400
        )
    charger.description = request_data["desc"]
    db.session.commit()

    app.logger.debug(f"charger {charger} description updated")

    return make_response(
        {"response": f"updated charger {charger.id} description"}, 200
    )


def checkout(request_data):
    if "id" not in request_data:
        return make_response(
            {"response": f"charger {charger.id} not found in request"}, 400
        )
    charger = db.get_or_404(Chargers, request_data["id"])

    if not charger.in_office:
        return make_response(
            {"response": f"charger {charger.id} not checked in"}, 400
        )
    charger.in_office = False
    charger.checked_out = datetime.now(timezone.utc)
    if (
        "area_code" not in request_data
        or "middle" not in request_data
        or "end" not in request_data
    ):
        return make_response(
            {"response": f"phone number {charger.id} not found in request"}, 400
        )
    charger.phone_area_code = request_data["area_code"]
    charger.phone_middle = request_data["middle"]
    charger.phone_end = request_data["end"]
    db.session.commit()

    app.logger.debug(f"charger {charger} checkedout")

    return make_response({"response": f"checked out charger {charger.id}"}, 200)


def checkin(request_data):
    if "id" not in request_data:
        return make_response(
            {"response": f"charger {charger.id} not found in request"}, 400
        )
    charger = db.get_or_404(Chargers, request_data["id"])

    if charger.in_office:
        return make_response(
            {"response": f"charger {charger.id} already checked in"}, 400
        )
    charger.in_office = True
    db.session.commit()

    app.logger.debug(f"charger {charger} checkedin")

    return make_response({"response": f"checked in charger {charger.id}"}, 200)


def create(request_data):
    if "desc" not in request_data:
        return make_response(
            {"response": f"charger {charger.id} desc not found in request"}, 400
        )
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

    app.logger.debug(f"charger {new_charger} created")

    return make_response({"response": f"created charger {new_charger.id}"}, 200)


def delete(request_data):
    if "id" not in request_data:
        return make_response(
            {"response": f"charger {charger.id} not found in request"}, 400
        )
    desc = request_data["id"]

    charger = db.get_or_404(Chargers, request_data["id"])

    db.session.delete(charger)
    db.session.commit()

    app.logger.debug(f"charger {charger} deleted")

    return make_response({"response": f"charger {charger.id} deleted"}, 200)
