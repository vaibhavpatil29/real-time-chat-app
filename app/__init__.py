from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_login import LoginManager, current_user
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
from config import config
import os
from datetime import datetime

db = SQLAlchemy()
socketio = SocketIO()
login_manager = LoginManager()
mail = Mail()
oauth = OAuth()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    socketio.init_app(app, cors_allowed_origins="*")
    login_manager.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Security headers middleware
    @app.after_request
    def add_security_headers(response):
        for header, value in app.config.get('SECURITY_HEADERS', {}).items():
            response.headers[header] = value
        return response
    
    # User activity tracking
    @app.before_request
    def before_request():
        from flask_login import current_user
        if current_user.is_authenticated:
            current_user.update_last_seen()
            db.session.commit()
    
    # Register Blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Import socket events to register handlers
    from app import socket_events
    
    # Create upload folder if it doesn't exist
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder and not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    return app

# User loader must be placed outside the create_app function
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
