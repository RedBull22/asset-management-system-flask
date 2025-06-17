# app.py

"""
Asset Management System - Main Application File

This file initializes the Flask application, configures extensions,
registers blueprints, defines core routes like the index page,
sets up error handlers, includes sample data creation logic,
and includes production readiness configurations (environment variables, logging).
"""

from flask import Flask, render_template, url_for, redirect, request, flash, abort
# Import SQLAlchemy and Bcrypt classes here for initialization (though instances are in extensions.py)
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
# Import your models from models.py *before* forms if needed by user_loader or sample data
from models import User # Only need User model for user_loader and sample data check
# Import extension instances from extensions.py *before* models or forms
from extensions import db, bcrypt, login_manager # Import db, bcrypt, login_manager instances

import os # Import os to access environment variables
from datetime import datetime, timedelta # Import timedelta for sample data
import logging # Import the logging module


# Import blueprints *after* creating the app instance
from routes.auth import auth
from routes.assets import assets
from routes.asset_types import asset_types
from routes.users import users
from routes.assignments import assignments


# Create the Flask application instance
app = Flask(__name__)

# --- Configuration ---
# Use environment variables for sensitive or production-specific configuration
# Get SECRET_KEY from environment variable, default to hardcoded dev key if not set
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_super_secret_key_here_dev')

# Get DATABASE_URL from environment variable (e.g., provided by hosting platform)
# Default to SQLite for local development if DATABASE_URL is not set
# Using os.path.join is robust for different OS
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'site.db')
)
# Disable SQLAlchemy event system for performance, not needed for this project
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Determine debug mode based on environment variable, default to True for local dev
# In production, DEBUG environment variable will likely be 'False' or unset
app.config['DEBUG'] = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')

# --- End Configuration ---


# Extension instances are created in extensions.py
# Initialize extensions *after* configuring the app and importing other modules/blueprints
db.init_app(app) # Initialize SQLAlchemy with the Flask app
bcrypt.init_app(app) # Initialize Bcrypt with the Flask app
login_manager.init_app(app) # Initialize LoginManager with the Flask app


# Configure Flask-Login
login_manager.login_view = 'auth.login' # Set the endpoint for the login page (using blueprint name)
login_manager.login_message_category = 'info' # Set the category for flash messages shown for protected routes

# User loader function required by Flask-Login
# This function tells Flask-Login how to load a user from the database based on their ID
@login_manager.user_loader
def load_user(user_id):
    """
    Loads a user from the database based on the user ID.

    Args:
        user_id (int): The ID of the user to load.

    Returns:
        User or None: The User object if found, otherwise None.
    """
    # Use db.session.get() for SQLAlchemy 2.0+ style loading
    return db.session.get(User, int(user_id))

# --- Register Blueprints ---
# Register the blueprints defined in the routes/ directory
app.register_blueprint(auth)
app.register_blueprint(assets)
app.register_blueprint(asset_types)
app.register_blueprint(users)
app.register_blueprint(assignments)
# --- End Register Blueprints ---


# --- Main Routes (like index) can stay here ---
@app.route('/')
def index():
    """
    Renders the homepage of the application.

    Returns:
        str: Rendered HTML content for the index page.
    """
    # Renders index.html, which extends base.html
    return render_template('index.html')
# --- End Main Routes ---

# --- Error Handlers ---
# These functions handle specific HTTP error codes

# Handler for 404 Not Found errors
@app.errorhandler(404)
def page_not_found(e):
    """
    Handles 404 Not Found errors by rendering a custom 404 page.

    Args:
        e: The exception object (contains error details).

    Returns:
        tuple: Rendered HTML content for the 404 page and the 404 status code.
    """
    # 404s are common and often not critical, so we might log them at a lower level or not at all
    # app.logger.warning('Page Not Found: %s', request.url) # Optional: Log 404s as warnings
    return render_template('404.html'), 404

# Handler for 500 Internal Server errors
@app.errorhandler(500)
def internal_server_error(e):
    """
    Handles 500 Internal Server errors by rendering a custom 500 page and logging the error.

    Args:
        e: The exception object (contains error details).

    Returns:
        tuple: Rendered HTML content for the 500 page and the 500 status code.
    """
    # Log the exception details using the app.logger
    app.logger.error('Internal Server Error: %s', e)
    return render_template('500.html'), 500

# --- End Error Handlers ---


# --- Sample Data Creation ---
def create_sample_data():
    """
    Creates sample data in the database if no data or admin user exists.
    Includes AssetTypes, Users (Admin/Regular), Assets, and Assignments.
    This function is called when the application is run directly.
    """
    # Import models locally within the function to avoid circular import with db init
    from models import AssetType, User, Asset, Assignment
    from datetime import timedelta # Need timedelta for varying dates


    # Check if sample data already exists to avoid duplication
    # We check for any AssetType or the specific admin user as indicators
    if AssetType.query.first() or User.query.filter_by(username='admin').first():
        print("Sample data already exists, skipping creation.")
        return

    print("Database is empty or admin user not found, creating sample data...")

    # Create some asset types (more than before to hit 10 if needed)
    laptop_type = AssetType(name='Laptop')
    desktop_type = AssetType(name='Desktop')
    server_type = AssetType(name='Server')
    software_type = AssetType(name='Software License')
    monitor_type = AssetType(name='Monitor')
    keyboard_type = AssetType(name='Keyboard')
    mouse_type = AssetType(name='Mouse')
    printer_type = AssetType(name='Printer')
    scanner_type = AssetType(name='Scanner')
    router_type = AssetType(name='Router')
    switch_type = AssetType(name='Network Switch')
    phone_type = AssetType(name='Desk Phone') # 12 types now

    # Create some users (more than before)
    admin_user = User(username='admin', email='admin@example.com', role='admin')
    # Hash passwords before saving!
    admin_user.set_password('admin_password')
    regular_user1 = User(username='user1', email='user1@example.com', role='regular')
    regular_user1.set_password('user_password')
    regular_user2 = User(username='user2', email='user2@example.com', role='regular')
    regular_user2.set_password('user_password')
    regular_user3 = User(username='user3', email='user3@example.com', role='regular')
    regular_user3.set_password('user_password')
    regular_user4 = User(username='user4', email='user4@example.com', role='regular')
    regular_user4.set_password('user_password')
    regular_user5 = User(username='user5', email='user5@example.com', role='regular')
    regular_user5.set_password('user_password')
    regular_user6 = User(username='user6', email='user6@example.com', role='regular')
    regular_user6.set_password('user_password')
    regular_user7 = User(username='user7', email='user7@example.com', role='regular')
    regular_user7.set_password('user_password')
    regular_user8 = User(username='user8', email='user8@example.com', role='regular')
    regular_user8.set_password('user_password')
    regular_user9 = User(username='user9', email='user9@example.com', role='regular')
    regular_user9.set_password('user_password')
    regular_user10 = User(username='user10', email='user10@example.com', role='regular') # 11 users now
    regular_user10.set_password('user_password')


    # Create some assets (more than before)
    laptop1 = Asset(name='Dell XPS 13', serial_number='ABC12345', asset_type=laptop_type)
    laptop2 = Asset(name='HP Spectre x360', serial_number='DEF67890', asset_type=laptop_type)
    laptop3 = Asset(name='MacBook Pro 14', serial_number='GHI11223', asset_type=laptop_type)
    desktop1 = Asset(name='HP Envy Desktop', serial_number='JKL44556', asset_type=desktop_type)
    desktop2 = Asset(name='Dell OptiPlex 7000', serial_number='MNO77889', asset_type=desktop_type)
    server1 = Asset(name='Dell PowerEdge R740', serial_number='PQR00112', asset_type=server_type)
    server2 = Asset(name='HP ProLiant DL380', serial_number='STU33445', asset_type=server_type)
    software1 = Asset(name='Microsoft Office 365', serial_number='SW-1234', asset_type=software_type)
    software2 = Asset(name='Adobe Creative Suite', serial_number='SW-5678', asset_type=software_type)
    monitor1 = Asset(name='Dell Ultrasharp 27', serial_number='VWX66778', asset_type=monitor_type)
    monitor2 = Asset(name='HP Z27', serial_number='YZA99001', asset_type=monitor_type)
    keyboard1 = Asset(name='Logitech K120', serial_number='KB-1122', asset_type=keyboard_type)
    mouse1 = Asset(name='Logitech M185', serial_number='MS-3344', asset_type=mouse_type) # 13 assets now

    # Add basic data first to ensure relationships can be formed
    db.session.add_all([laptop_type, desktop_type, server_type, software_type, monitor_type, keyboard_type, mouse_type, printer_type, scanner_type, router_type, switch_type, phone_type,
                        admin_user, regular_user1, regular_user2, regular_user3, regular_user4, regular_user5, regular_user6, regular_user7, regular_user8, regular_user9, regular_user10,
                        laptop1, laptop2, laptop3, desktop1, desktop2, server1, server2, software1, software2, monitor1, monitor2, keyboard1, mouse1])
    db.session.commit()

    # Now create assignments using the objects (at least 10)
    assignment1 = Assignment(asset=laptop1, user=admin_user, assignment_date=datetime.utcnow() - timedelta(days=30))
    assignment2 = Assignment(asset=desktop1, user=regular_user1, assignment_date=datetime.utcnow() - timedelta(days=25))
    assignment3 = Assignment(asset=server1, user=regular_user2, assignment_date=datetime.utcnow() - timedelta(days=20))
    assignment4 = Assignment(asset=laptop2, user=regular_user3, assignment_date=datetime.utcnow() - timedelta(days=15))
    assignment5 = Assignment(asset=desktop2, user=regular_user4, assignment_date=datetime.utcnow() - timedelta(days=10))
    assignment6 = Assignment(asset=software1, user=regular_user5, assignment_date=datetime.utcnow() - timedelta(days=5))
    assignment7 = Assignment(asset=monitor1, user=regular_user6, assignment_date=datetime.utcnow() - timedelta(days=3))
    assignment8 = Assignment(asset=server2, user=regular_user7, assignment_date=datetime.utcnow() - timedelta(days=1))
    assignment9 = Assignment(asset=laptop3, user=regular_user8, assignment_date=datetime.utcnow())
    assignment10 = Assignment(asset=software2, user=regular_user9, assignment_date=datetime.utcnow())
    assignment11 = Assignment(asset=keyboard1, user=regular_user10, assignment_date=datetime.utcnow()) # 11 assignments

    db.session.add_all([assignment1, assignment2, assignment3, assignment4, assignment5, assignment6, assignment7, assignment8, assignment9, assignment10, assignment11])
    db.session.commit()

    print("Sample data created.")

# --- End Sample Data Creation ---


if __name__ == '__main__':
    """
    Main entry point for running the Flask development server.
    Sets up database, creates sample data if needed, configures logging,
    and runs the app in debug mode.
    This block ONLY runs when you execute app.py directly (e.g., python app.py).
    It is NOT used by production WSGI servers like Gunicorn.
    """
    # Ensure the application context is pushed before interacting with Flask/SQLAlchemy
    with app.app_context():
        # Create database tables if they don't exist
        # Note: In production, you'd typically use Flask-Migrate for schema changes
        db.create_all()
        # Create sample data if the database is empty (only runs if conditions met)
        create_sample_data()

    # --- Logging Configuration (for development server) ---
    # In production, logging is often handled by the WSGI server and platform
    # Set up logging to a file named 'error.log' in the project root for local dev
    file_handler = logging.FileHandler('error.log')
    # Set the logging level for this handler to ERROR, meaning only errors and critical messages will be written to the file
    file_handler.setLevel(logging.ERROR)
    # Define the format of the log messages (timestamp, level, message, file path, line number)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    file_handler.setFormatter(formatter)
    # Add the file handler to the Flask application's logger
    app.logger.addHandler(file_handler)
    # Set the overall logging level for the application's logger
    # This should be at least ERROR to allow the file_handler to log errors
    app.logger.setLevel(logging.ERROR)

    # Optional: Add a handler to also print errors to the console (useful during development)
    # If you want errors to show in your terminal *and* the file when debug=False
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.ERROR)
    # console_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    # console_handler.setFormatter(console_formatter)
    # app.logger.addHandler(console_handler)

    # Optional: Log an informational message when the server starts (requires app.logger.setLevel to be INFO or lower)
    # If app.logger.setLevel is ERROR, this line won't actually log anything.
    # app.logger.info('Asset Management System starting up...')
    # --- End Logging Configuration ---

    # Run the Flask development server
    # debug=True provides helpful error pages and auto-reloading during development
    # This uses the DEBUG config value now
    app.run(debug=app.config['DEBUG'])

# Note: Production WSGI servers (like Gunicorn) will import the 'app' instance directly
# from this file and run it, they do NOT execute the code inside the if __name__ == '__main__': block.
