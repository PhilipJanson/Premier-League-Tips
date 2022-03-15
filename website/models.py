from . import db
from flask_login import UserMixin


class Tip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fixture_id = db.Column(db.Integer)
    tip = db.Column(db.String(1))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean)
    tips = db.relationship('Tip')
