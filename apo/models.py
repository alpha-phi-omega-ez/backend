from flask_login import UserMixin

from apo import app, db


# User table
# contains data about every user
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    firstname = db.Column(db.String(30), unique=False, nullable=False)
    lastname = db.Column(db.String(30), unique=False, nullable=False)
    nickname = db.Column(db.String(30), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
