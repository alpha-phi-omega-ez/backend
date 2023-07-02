import os

# Import Flask modules
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# from oauthlib.oauth2 import WebApplicationClient
from authlib.integrations.flask_client import OAuth

# Create flask app object
app = Flask(__name__)
app.config.from_object(os.environ.get("CONFIG", "config.TestingConfig"))

# Create Database object
db = SQLAlchemy(app, session_options={"expire_on_commit": False})

# Create Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"
login_manager.session_protection = "strong"

# Create OAuth Client
# oauth_client = WebApplicationClient(app.config["GOOGLE_CLIENT_ID"])
oauth = OAuth(app)

# Import all api endpoints
import apo.api

# Import all views
import apo.views
