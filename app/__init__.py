from flask_migrate import Migrate
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
socketio = SocketIO()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    socketio.init_app(app, cors_allowed_origins="*")
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Blueprint name used

    # Register Blueprints
    from app.routes import main
    app.register_blueprint(main)

    # Import socket events to register handlers
    from app import socket_events

    return app

# User loader must be placed outside the create_app function
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
