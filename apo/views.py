from flask import (
    make_response,
    redirect,
    render_template,
    send_file,
    url_for,
    Response,
    request,
    abort
)
from flask_login import current_user, login_required, login_user, logout_user

from apo import app, login_manager, oauth, oauth_client
from apo.forms import LostReportForm
from apo.models import Users
import requests
import json


@login_manager.user_loader
def load_user(user_id):
    try:
        # update to proper query
        return Users.query.get(user_id)
    except:
        return None


def get_google_provider_cfg():
    try:
        return requests.get(app.config["GOOGLE_DISCOVERY_URL"]).json()
    except:
        return None


"""
Routes
"""


@app.route("/", methods=["GET"])
def index():
    return render_template("home.html")


@app.route("/login/")
def google():
  oauth.register(
    name="google",
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    server_metadata_url=app.config["GOOGLE_DISCOVERY_URL"],
    client_kwargs={"scope": "openid email profile"},
  )

  # Redirect to google_auth function
  redirect_uri = url_for("google_auth", _external=True)
  print(redirect_uri)
  return oauth.google.authorize_redirect(redirect_uri)


@app.route("/login/callback/")
def google_auth():
  token = oauth.google.authorize_access_token()
  user = oauth.google.parse_id_token(token)
  print(" Google User ", user)
  return redirect(index)


# Google OAuth Login following this guide:
# https://realpython.com/flask-google-login/
@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    if not google_provider_cfg:
        return abort(500)
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    print(request.base_url + "/callback")
    request_uri = oauth_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    if not google_provider_cfg:
        return abort(500)
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = oauth_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(app.config["GOOGLE_CLIENT_ID"], app.config["GOOGLE_CLIENT_SECRET"]),
    )
    if not token_response:
        return abort(500)

    # Parse the tokens!
    oauth_client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = oauth_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        # Replace with can't login page
        # redirect to index
        # flash fail to login
        return "User email not available or not verified by Google.", 400


    # Create a user in your db with the information provided
    # by Google
    if not Users.query.get(unique_id):
        user = User(
            id_=unique_id,
            name=users_name,
            email=users_email
        )
        db.session.add(user)
        db.session.commit()
    # Begin user session by logging the user in
    # Use remember?
    login_user(user, remember=True)

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# @app.route("/backtests", methods=["GET", "POST"])
# def backtests():
#     return render_template("backtest.html")


"""
SEO
"""


@app.route("/robots.txt", methods=["GET"])
def robots() -> Response:
    # Return static robots.txt file for any web crawlers that use it
    return send_file("templates/seo/robots.txt")


# @app.route('/favicon.ico', methods=['GET'])
# def favicon():

#     # Return static favicon.ico
#     return send_file('static/img/apo.ico')


@app.route("/sitemap.xml", methods=["GET"])
def sitemap() -> Response:
    # Return static sitemap XML file for SEO
    sitemap_xml = render_template("seo/sitemap.xml")
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


"""
Error Handlers
"""


@app.errorhandler(404)
def page_not_found(e) -> Response:
    # 404 error page
    return make_response(render_template("404.html"), 404)


@app.errorhandler(500)
def error_for_server(e) -> Response:
    # 500 error page
    return make_response(render_template("500.html"), 500)
