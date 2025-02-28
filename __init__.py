from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager
import os
import logging

logger = logging.getLogger(__name__)
SECRET_KEY = os.urandom(32)

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pi-camera.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    return app
