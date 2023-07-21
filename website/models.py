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
    availability = db.relationship("Availability")
    memberships = db.relationship("User_Band_Junction")
    active_band = db.Column(db.Integer, db.ForeignKey("bands.id"), default=1)

class Bands(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    band_name = db.Column(db.String(150), unique=True)
    members = db.relationship("User_Band_Junction")
    active_band = db.relationship("User")


class User_Band_Junction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    band_name = db.Column(db.String(150), db.ForeignKey("bands.band_name"))
    member_id = db.Column(db.Integer, db.ForeignKey("user.id"))