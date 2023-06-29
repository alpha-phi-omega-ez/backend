from flask import (
    flash,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required

from apo import app, db, login_manager
from apo.forms import LostReportForm
from apo.models import (
    User,
    BacktestClasses,
    Backtest,
    Chargers,
)  # , LostReport, LostItem

from apo.helpers import chargers

"""
API
"""


@app.route("/api/v1/chargers", methods=["GET"])
def list_chargers_api():
    return make_response(chargers.list_chargers(), 200)


# @login_required
@app.route("/api/v1/chargers/admin", methods=["GET"])
def list_chargers_admin_api():
    return make_response(chargers.list_chargers(True), 200)


# @login_required
@app.route("/api/v1/chargers/admin/edit/desc", methods=["POST"])
def update_charger_desc_api():
    return chargers.edit_desc(request.get_json())


# @login_required
@app.route("/api/v1/chargers/admin/checkout", methods=["POST"])
def checkout_charger_api():
    return chargers.checkout(request.get_json())


# @login_required
@app.route("/api/v1/chargers/admin/checkin", methods=["POST"])
def checkin_charger_api():
    return chargers.checkin(request.get_json())


# @login_required
@app.route("/api/v1/chargers/admin/create", methods=["POST"])
def create_charger_api():
    return chargers.create(request.get_json())


# @login_required
@app.route("/api/v1/chargers/admin/delete", methods=["POST"])
def delete_charger_api():
    return chargers.delete(request.get_json())