# Import os
import os
basedir = os.path.abspath(os.path.dirname(__file__))

from pathlib import Path
import json

class Config():

    # This file should not be in the repository; don't want to check it in
    maybe_path = Path.home()/"Documents"/"google-secret.json"
    if maybe_path.exists():
      with open(maybe_path) as f:
        loaded = json.load(f)
      GOOGLE_CLIENT_ID = loaded["web"]["client_id"]
      GOOGLE_CLIENT_SECRET = loaded["web"]["client_secret"]
    else:
      # Configuration
      GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None) # Not used right now
      GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None) # Not used right now
      
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32))

    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )  # Not used right now

    TESTING = False
    DEBUG = False

    PREFERRED_URL_SCHEME = "https"

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

    # Using SQLLITE locally
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'database.db')}"
    

class ProductionConfig(Config):
    #SQLALCHEMY_DATABASE_URI = ""
    SERVER_NAME = "apoez.org"