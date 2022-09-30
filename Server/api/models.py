from . import db

#User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    auth_key = db.Column(db.String(64))
    mail_auth_key = db.Column(db.String(64))
    is_authed = db.Column(db.Boolean, default=False)
    is_privilleged = db.Column(db.Boolean, default=False)

#Text Log Table
class Text_Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auth_key = db.Column(db.String(64))
    parameters = db.Column(db.String(200))
    text = db.Column(db.String(1000))
    rest = db.Column(db.Boolean, default=False)
