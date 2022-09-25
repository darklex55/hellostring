from email.policy import default
from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(150))
    auth_key = db.Column(db.String(100))
    mail_auth_key = db.Column(db.String(100))
    is_authed = db.Column(db.Boolean, default=False)


class Text_Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auth_key = db.Column(db.String(100))
    parameters = db.Column(db.String(200))
    text = db.Column(db.String(100))
    rest = db.Column(db.Boolean, default=False)