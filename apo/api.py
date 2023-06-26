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

"""
API
"""


@app.route("/api/v1/chargers")
def list_chargers():
    chargers = Chargers.query.all()
    # charger_data = [{charger.id:{"desc":charger.description}} for charger in chargers]
    charger_dict = {}
    for charger in chargers:
        charger_dict[charger.id] = {
            "desc": charger.description,
            "in_office": charger.in_office,
        }
    return make_response(charger_dict), 200


# @login_required
@app.route("/api/v1/chargers/admin")
def list_chargers_admin():
    chargers = Chargers.query.all()
    charger_dict = {}
    # TODO: strftime for checkedout
    for charger in chargers:
        charger_dict[charger.id] = {
            "desc": charger.description,
            "in_office": charger.in_office,
            "checked_out": charger.checked_out,
            "phone_number": f"({charger.phone_area_code}){charger.phone_middle}-{charger.phone_end}",
        }
    return make_response(charger_dict), 200


# @login_required
@app.route("/api/v1/chargers/admin/edit/desc", methods=["POST"])
def update_charger_desc():

    request_data = request.get_json()

    charger = Chargers.query.get(request_data["id"])

    if charger:
        charger.description = request_data["desc"]
        db.session.commit()
        # correct http response
        return make_response({"response":f"updated charger {charger.id} description"}, 200)
    
    return make_response({"response":"charger not found"}), 404