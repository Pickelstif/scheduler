from . import db
from flask_login import UserMixin
from datetime import datetime


class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(20), nullable=False, default=datetime.now().year)
    month = db.Column(db.String(20), nullable=False, default=datetime.now().month)
    day = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    band = db.Column(db.String(150))
    availability = db.relationship("Availability")

    bandmates = {}