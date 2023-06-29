from apo import db
from apo.models import Chargers

from datetime import datetime, timezone
import pytz

from flask import make_response

local = pytz.timezone("US/Eastern")
fmt = "%y-%m-%d %H:%M:%S"


def list_chargers(admin=False):
    chargers = Chargers.query.all()
    charger_dict = {}
    for charger in chargers:
        if admin:
            charger_dict[charger.id] = {
                "desc": charger.description,
                "in_office": charger.in_office,
                "checked_out": local.localize(charger.checked_out).strftime(fmt),
                "phone_number": f"({charger.phone_area_code}){charger.phone_middle}-{charger.phone_end}",
            }
        else:
            charger_dict[charger.id] = {
                "desc": charger.description,
                "in_office": charger.in_office,
            }
    return charger_dict


def edit_desc(request_data):
    charger = Chargers.query.get(request_data["id"])

    if charger:
        charger.description = request_data["desc"]
        db.session.commit()

        return make_response(
            {"response": f"updated charger {charger.id} description"}, 200
        )
    return make_response({"response": "charger not found"}, 404)


def checkout(request_data):
    charger = Chargers.query.get(request_data["id"])

    if charger:
        if not charger.in_office:
            return make_response({"response": f"charger {charger.id} not checked in"}, 400)
        charger.in_office = False
        charger.checked_out = datetime.now(timezone.utc)
        charger.phone_area_code = request_data["area_code"]
        charger.phone_middle = request_data["middle"]
        charger.phone_end = request_data["end"]
        db.session.commit()

        return make_response({"response": f"checked out charger {charger.id}"}, 200)

    return make_response({"response": "charger not found"}, 404)


def checkin(request_data):
    charger = Chargers.query.get(request_data["id"])

    if charger:
        if charger.in_office:
            return make_response({"response": f"charger {charger.id} already checked in"}, 400)
        charger.in_office = True
        db.session.commit()

        return make_response({"response": f"checked in charger {charger.id}"}, 200)

    return make_response({"response": "charger not found"}, 404)
