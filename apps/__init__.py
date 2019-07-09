from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'

db = SQLAlchemy()
csrf = CSRFProtect()
# from .seckill.models import *
# from .user.models import *


def create_app(path, config):
    app = Flask(path)
    app.config.from_object(config)
    csrf.init_app(app)
    login_manager.init_app(app)


    db.init_app(app)
    # db.create_all(app=app)
    # redis_conn = Redis()

    return app
