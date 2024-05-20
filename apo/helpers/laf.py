from datetime import datetime, date

from flask import abort

from apo import app, db
from apo.models import LostItems


def verfiy_args(request_data) -> tuple[date, str, str, str]:
    if (
        "description" not in request_data
        or "item_type" not in request_data
        or "locations" not in request_data
        or "date_lost" not in request_data
    ):
        app.logger.debug("Missing request data to complete request")
        abort(400)

    try:
        date_lost = datetime.strptime(request_data["date_lost"], "%d-%m-%Y").date()
    except ValueError as e:
        app.logger.debug(f"Date value error {e}")
        abort(400)

    description = request_data["description"]
    item_type = request_data["item_type"]

    if not isinstance(item_type, str) or not isinstance(description, str):
        app.logger.debug("Issue with item_type or description")
        abort(400)

    try:
        locations = ",".join(request_data["locations"])
    except TypeError as e:
        app.logger.debug(f"Locations error {e}")
        abort(400)

    return date_lost, description, item_type, locations


def create(request_data: dict) -> dict:
    date_lost, description, item_type, locations = verfiy_args(request_data)

    new_laf = LostItems(
        description=description,
        lost_report_match=1,
        item_type=item_type,
        locations=locations,
        date_lost=date_lost,
    )

    db.session.add(new_laf)
    db.session.commit()

    return {"response": f"Succesfully created LAF item {new_laf}"}


def edit(request_data: dict) -> dict:
    if "id" not in request_data:
        app.logger.debug("Missing request data to complete request")
        abort(400)

    date_lost, description, item_type, locations = verfiy_args(request_data)

    laf_item = db.get_or_404(LostItems, request_data["id"])

    laf_item.date_lost = date_lost
    laf_item.description = description
    laf_item.item_type = item_type
    laf_item.locations = locations

    db.session.commit()

    return {"response": f"Sucessfully updated {laf_item}"}


def archive(request_data: dict) -> dict:
    if "id" not in request_data:
        app.logger.debug("Missing request data to complete request")
        abort(400)

    laf = db.get_or_404(LostItems, request_data["id"])

    laf.archived = True
    laf.archived_dt = datetime.now()

    db.session.commit()

    return {"response": f"Archived lost report: {laf}"}
