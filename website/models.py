from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    #username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(150))
    auth_key = db.Column(db.String(100))
    mail_auth_key = db.Column(db.String(100))
    is_authed = db.Column(db.Boolean, default=False)