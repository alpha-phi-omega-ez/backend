import os

from dotenv import load_dotenv

# Import Flask modules
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from oauthlib.oauth2 import WebApplicationClient
# from authlib.integrations.flask_client import OAuth
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))

environment = os.environ.get("CONFIG", "config.TestingConfig")
print(os.environ.get("CONFIG"))
print(os.environ.get("SENTRY_URL"))

if environment == "config.ProductionConfig":

    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_URL"),
        integrations=[
            FlaskIntegration(),
        ],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0
    )


# Create flask app object
app = Flask(__name__)
app.config.from_object(environment)

# Create Database object
db = SQLAlchemy(app, session_options={"expire_on_commit": False})

# Create Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"
login_manager.session_protection = "strong"

# Create OAuth Client
oauth_client = WebApplicationClient(app.config["GOOGLE_CLIENT_ID"])
# oauth = OAuth(app)

# Import all api endpoints
import apo.api

# Import all views
import apo.views
