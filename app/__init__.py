from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_socketio import SocketIO
from config import Config
from threading import Thread,Lock
from flask_migrate import Migrate
import sys
import time
import cv2

bcrypt = Bcrypt()
db = SQLAlchemy()
login = LoginManager()
login.login_view = 'main.login'
login.login_message = 'Please log in to access this page.'
mail = Mail()
bootstrap = Bootstrap()
migrate = Migrate()
socketio = SocketIO(async_mode=None)

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    bcrypt.init_app(app)
    login.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    socketio.init_app(app)
    migrate.init_app(app,db,render_as_batch=True)
    from app.main.routes import main
    from app.main import chat_events
    app.register_blueprint(main)

    return app