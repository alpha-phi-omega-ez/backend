from flask import make_response, request, Response

# from flask_login import current_user, login_required

from apo import app  # , login_manager
from apo.forms import LostReportForm
from apo.helpers import backtests, chargers, lostreports


"""
API
"""


@app.route("/api/v1/chargers", methods=["GET"])
def list_chargers_api() -> Response:
    app.logger.info("/api/v1/chargers called")
    # replace by passing is is_anonmous
    return make_response(chargers.list_chargers(True), 200)


# @login_required
@app.route("/api/v1/chargers/edit", methods=["PUT"])
def update_charger_desc_api() -> Response:
    app.logger.info("/api/v1/chargers/edit called")
    app.logger.debug(f"request data: {request.get_json()}")
    return make_response(chargers.edit_desc(request_data=request.get_json()), 200)


# @login_required
@app.route("/api/v1/chargers/checkout", methods=["PUT"])
def checkout_charger_api() -> Response:
    app.logger.debug("/api/v1/chargers/admin/checkout")
    app.logger.debug(f"request data: {request.get_json()}")
    return make_response(chargers.checkout(request_data=request.get_json()), 200)


# @login_required
@app.route("/api/v1/chargers/checkin", methods=["PUT"])
def checkin_charger_api() -> Response:
    app.logger.debug("/api/v1/chargers/admin/checkin")
    app.logger.debug(f"request data: {request.get_json()}")
    return make_response(chargers.checkin(request_data=request.get_json()), 200)


# @login_required
@app.route("/api/v1/chargers/create", methods=["POST"])
def create_charger_api() -> Response:
    app.logger.debug("/api/v1/chargers/admin/create")
    app.logger.debug(f"request data: {request.get_json()}")
    return make_response(chargers.create(request_data=request.get_json()), 200)


# @login_required
@app.route("/api/v1/chargers/delete", methods=["DELETE"])
def delete_charger_api() -> Response:
    app.logger.debug("/api/v1/chargers/admin/delete")
    app.logger.debug(f"request data: {request.get_json()}")
    return make_response(chargers.delete(request_data=request.get_json()), 200)


@app.route("/api/v1/subject_codes", methods=["GET"])
def list_backtest_subject_codes_api() -> Response:
    app.logger.info(f"/api/v1/subject_codes called")
    return make_response(backtests.list_subject_codes(), 200)


@app.route("/api/v1/classes", methods=["GET"])
def list_backtest_classes_api() -> Response:
    app.logger.info("/api/v1/classes called")
    app.logger.debug(f"request data: {request.get_json()}")
    return make_response(backtests.list_classes(request_data=request.get_json()), 200)


@app.route("/api/v1/backtests", methods=["GET"])
def list_backtest_in_class_api() -> Response:
    app.logger.info("/api/v1/backtests called")
    app.logger.debug(f"request data: {request.get_json()}")
    return make_response(backtests.backtests(request.get_json()), 200)


# @login_required
@app.route("/api/v1/lostreports", methods=["GET"])
def list_lost_reports() -> Response:
    app.logger.info("/api/v1/backtests called")
    return make_response(lostreports.lostreports(), 200)


@app.route("/api/v1/lostreports/create", methods=["POST"])
def create_lost_report() -> Response:
    app.logger.info("/api/v1/lostreports/create called")
    app.logger.debug(f"request data: {request.get_json()}")
    return make_response(lostreports.create_lostreport(request_data=request.get_json()), 200)


@app.route("/api/v1/lostreports/edit", methods=["PUT"])
def edit_lost_report() -> Response:
    app.logger.info("/api/v1/lostreports/edit called")
    app.logger.debug(f"request data: {request.get_json()}")
    return make_response(lostreports.edit_lostreport(request_data=request.get_json()), 200)


@app.route("/api/v1/lostreports/archive", methods=["PUT"])
def archive_lost_report() -> Response:
    app.logger.info("/api/v1/lostreports/archive called")
    app.logger.debug(f"request data: {request.get_json()}")
    return make_response(lostreports.archive_lostreport(request_data=request.get_json()), 200)