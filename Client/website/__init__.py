from flask import Flask
from flask_login import LoginManager
import requests, json

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'kara2004'

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        try:
            res = requests.get('http://127.0.0.1:8001/load_user', json=json.dumps({"id":id}))
        except:
            return User(id,'','','','','')
                
        if res.status_code==200:
            res = res.json()
            return User(res.get('id'),res.get('email'),res.get('password'),res.get('is_authed'),res.get('auth_key'),res.get('mail_auth_key'),res.get('is_privilleged'))
        else: 
            return User(id,'','','','','','')

    return app