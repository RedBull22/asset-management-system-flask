# extensions.py

"""
Asset Management System - Flask Extensions File

This file creates instances of Flask extensions (SQLAlchemy, Bcrypt, LoginManager)
without initializing them with the Flask application instance.
This helps resolve circular dependencies when importing these instances
in models and other modules before the app instance is fully created.
The instances are initialized later in app.py using app.init_app().
"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Create instances of the extensions
# They are NOT initialized with the app yet (no app=... argument)
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# No functions or classes defined here, just instances created.
