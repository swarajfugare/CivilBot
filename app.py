import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from markupsafe import Markup
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import DeclarativeBase

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Create extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
bcrypt = Bcrypt()

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "civil-ai-default-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
bcrypt.init_app(app)

# Login manager configuration
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access CivilBot.'
login_manager.login_message_category = 'info'

# Add custom template filter for newline to br conversion
@app.template_filter('nl2br')
def nl2br_filter(text):
    """Convert newlines to HTML line breaks"""
    if text is None:
        return ''
    return Markup(str(text).replace('\n', '<br>\n'))

# User loader function
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    from models import User, ChatHistory
    db.create_all()
    logging.info("Database tables created")

# Import routes after app creation to avoid circular imports
from routes import *

# Log startup information
logging.info("CivilBot Assistant application started successfully")
