from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, email, password, is_authed, auth_key, mail_auth_key):
        self.id = id
        self.email = email
        self.password = password
        self.is_authed = is_authed
        self.auth_key = auth_key
        self.mail_auth_key = mail_auth_key

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

