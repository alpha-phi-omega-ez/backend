from datetime import date, datetime

from flask import abort

from apo import app, db
from apo.models import LostReports

# Constants
LOST_REPORTS_SELECT = db.select(LostReports)


def lost_report_locations_output(locations: str) -> list:
    if locations is None:
        abort(500)
    return locations.split(",")


def lostreports() -> dict:
    lost_reports = db.session.execute(LOST_REPORTS_SELECT).all()

    if lost_reports is None:
        app.logger.error("Failed to query and find lost reports")
        abort(500)

    lost_report_dict = {}

    for report in lost_reports:
        lost_report_dict[report.LostReports.id] = {
            "first_name": report.LostReports.first_name,
            "last_name": report.LostReports.last_name,
            "email": report.LostReports.email,
            "description": report.LostReports.description,
            "item_type": report.LostReports.item_type,
            "locations": lost_report_locations_output(report.LostReports.locations),
            "date_lost": report.LostReports.date_lost.strftime("%d-%m-%Y"),
            "phone_number": f"({report.LostReports.phone_area_code}){report.LostReports.phone_middle}-{report.LostReports.phone_end}",
        }

    app.logger.debug(f"lost report dict created {lost_report_dict}")
    return lost_report_dict


def create_lostreport(request_data: dict) -> dict:
    if (
        "first_name" not in request_data
        or "last_name" not in request_data
        or "email" not in request_data
        or "description" not in request_data
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

    try:
        first_name = request_data["first_name"][:40]
        last_name = request_data["last_name"][:50]
        email = request_data["email"][:100]
    except TypeError as e:
        app.logger.debug(f"Date value error {e}")
        abort(400)

    area_code = request_data.get("area_code", None)
    middle = request_data.get("middle", None)
    end = request_data.get("end", None)

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

    description = request_data["description"]
    item_type = request_data["item_type"]

    if not isinstance(description, str) or not isinstance(item_type, str):
        app.logger.debug(
            f"Issue with description or item_type: {description} {item_type}"
        )
        abort(400)

    try:
        locations = ",".join(request_data["locations"])
    except TypeError as e:
        app.logger.debug(f"Locations error {e}")
        abort(400)

    new_lost_report = LostReports(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_area_code=area_code,
        phone_middle=middle,
        phone_end=end,
        description=description,
        item_type=item_type,
        locations=locations,
        date_lost=date_lost,
        date_added=date.today(),
    )

    db.session.add(new_lost_report)
    db.session.commit()

    return {"response": f"Successfully created {new_lost_report}"}


def edit_lostreport(request_data: dict) -> dict:
    if (
        "id" not in request_data
        or "first_name" not in request_data
        or "last_name" not in request_data
        or "email" not in request_data
        or "description" not in request_data
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

    try:
        first_name = request_data["first_name"][:40]
        last_name = request_data["last_name"][:50]
        email = request_data["email"][:100]
    except TypeError as e:
        app.logger.debug(f"Date value error {e}")
        abort(400)

    area_code = request_data.get("area_code", None)
    middle = request_data.get("middle", None)
    end = request_data.get("end", None)

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

    description = request_data["description"]
    item_type = request_data["item_type"]

    if not isinstance(description, str) or not isinstance(item_type, str):
        app.logger.debug(
            f"Issue with description or item_type: {description} {item_type}"
        )
        abort(400)

    try:
        locations = ",".join(request_data["locations"])
    except TypeError as e:
        app.logger.debug(f"Locations error {e}")
        abort(400)

    lost_report = db.get_or_404(LostReports, request_data["id"])

    lost_report.first_name = first_name
    lost_report.last_name = last_name
    lost_report.email = email
    lost_report.phone_area_code = area_code
    lost_report.phone_middle = middle
    lost_report.phone_end = end
    lost_report.description = description
    lost_report.item_type = item_type
    lost_report.locations = locations
    lost_report.date_lost = date_lost

    db.session.commit()

    return {"response": f"Successfully updated lost report id: {lost_report.id}"}


def archive_lostreport(request_data: dict) -> dict:
    if (
        "id" not in request_data
        or "found" not in request_data
        or not isinstance(request_data["found"], bool)
    ):
        app.logger.debug("Missing request data to complete request")
        abort(400)

    lost_report = db.get_or_404(LostReports, request_data["id"])

    lost_report.archived = True
    lost_report.archived_dt = datetime.now()
    db.session.commit()

    return {"response": f"Archived lost report: {lost_report}"}
