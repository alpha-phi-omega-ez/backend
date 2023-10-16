# Import os
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    # Configuration
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)  # Not used right now
    GOOGLE_CLIENT_SECRET = os.environ.get(
        "GOOGLE_CLIENT_SECRET", None
    )  # Not used right now
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )

    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32))

    TESTING = False
    DEBUG = False

    PREFERRED_URL_SCHEME = "https"


class TestingConfig(Config):
    TESTING = True
    DEBUG = True

    # Using SQLLITE locally
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'database.db')}"


class ProductionConfig(Config):
    # SQLALCHEMY_DATABASE_URI = ""
    SERVER_NAME = "apoez.org"
