from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
    #Initialize Flask App
    app = Flask(__name__)
    #Workaround disabling CORS so that dynamic requests from client's browser are working
    CORS(app)
    app.config['SECRET_KEY'] = 'kara2004'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app) #Integrate SQLAlchemy database

    #Import routes from views file
    from .views import views

    app.register_blueprint(views, url_prefix='/')

    #Define Database schema
    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database')
