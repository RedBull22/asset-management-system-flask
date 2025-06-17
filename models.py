# models.py

"""
Asset Management System - Database Models File

This file defines the SQLAlchemy ORM models for the application's database tables:
User, AssetType, Asset, and Assignment.
It also includes helper methods for user authentication (password hashing, checking).
"""

# Import the SQLAlchemy db instance from extensions.py
from extensions import db, bcrypt # Also need bcrypt for password hashing
from flask_login import UserMixin # UserMixin provides default implementations for Flask-Login properties
from datetime import datetime # Used for the assignment_date field

# --- User Model ---
# Inherits from db.Model (SQLAlchemy) and UserMixin (Flask-Login)
class User(db.Model, UserMixin):
    """
    Represents a user in the system.

    Attributes:
        id (int): Primary key, unique identifier for the user.
        username (str): Unique username for the user.
        email (str): Unique email address for the user.
        password_hash (str): Hashed password for secure storage.
        role (str): The role of the user ('admin' or 'regular').
        assignments (relationship): One-to-many relationship with Assignment model.
    """
    # Define table name explicitly (optional, defaults to lowercase class name)
    __tablename__ = 'user'

    # Define columns
    id = db.Column(db.Integer, primary_key=True) # Primary Key
    username = db.Column(db.String(20), unique=True, nullable=False) # Unique and required username
    email = db.Column(db.String(120), unique=True, nullable=False) # Unique and required email
    password_hash = db.Column(db.String(60), nullable=False) # Required password hash
    role = db.Column(db.String(20), nullable=False, default='regular') # User role, default is 'regular'

    # Define relationship with Assignment model
    # 'assignments' is a list of Assignment objects associated with this user
    # backref='user' creates a 'user' attribute on the Assignment model
    # lazy=True means the assignments are loaded when accessed (efficient)
    assignments = db.relationship('Assignment', backref='user', lazy=True)

    # Method to set the user's password (hashes it using bcrypt)
    def set_password(self, password):
        """Hashes the provided password and stores the hash."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Method to check a provided password against the stored hash
    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    # Property required by Flask-Login to check if the user is an admin
    @property
    def is_admin(self):
        """Checks if the user's role is 'admin'."""
        return self.role == 'admin'

    # String representation of the User object (useful for debugging)
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

# --- Asset Type Model ---
class AssetType(db.Model):
    """
    Represents a type of asset (e.g., Laptop, Monitor, Software).

    Attributes:
        id (int): Primary key, unique identifier for the asset type.
        name (str): Unique name for the asset type.
        assets (relationship): One-to-many relationship with Asset model.
    """
    __tablename__ = 'asset_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # Unique and required name

    # Define relationship with Asset model
    # 'assets' is a list of Asset objects associated with this asset type
    # backref='asset_type' creates an 'asset_type' attribute on the Asset model
    # lazy=True means assets are loaded when accessed
    assets = db.relationship('Asset', backref='asset_type', lazy=True)

    def __repr__(self):
        return f"AssetType('{self.name}')"

# --- Asset Model ---
class Asset(db.Model):
    """
    Represents an individual asset in the system.

    Attributes:
        id (int): Primary key, unique identifier for the asset.
        name (str): Name of the asset.
        serial_number (str): Unique serial number for the asset.
        asset_type_id (int): Foreign key referencing the AssetType model.
        asset_type (relationship): Many-to-one relationship with AssetType model.
        assignments (relationship): One-to-many relationship with Assignment model.
    """
    __tablename__ = 'asset'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # Required name
    serial_number = db.Column(db.String(50), unique=True, nullable=False) # Unique and required serial number

    # Foreign Key to AssetType
    # db.ForeignKey('asset_type.id') links to the 'id' column of the 'asset_type' table
    # nullable=False means every asset MUST have an asset type
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_type.id'), nullable=False)

    # Define relationship with Assignment model
    # 'assignments' is a list of Assignment objects associated with this asset
    # backref='asset' creates an 'asset' attribute on the Assignment model
    # lazy=True means assignments are loaded when accessed
    # cascade='all, delete-orphan' means deleting an Asset will delete associated Assignments (handle carefully!)
    # Let's explicitly NOT cascade delete assignments here, relying on the route logic to prevent deletion if assignments exist.
    assignments = db.relationship('Assignment', backref='asset', lazy=True)


    def __repr__(self):
        return f"Asset('{self.name}', '{self.serial_number}')"

# --- Assignment Model ---
class Assignment(db.Model):
    """
    Represents the assignment of an Asset to a User at a specific time.
    This is a many-to-many relationship with extra data (assignment_date).

    Attributes:
        id (int): Primary key, unique identifier for the assignment.
        asset_id (int): Foreign key referencing the Asset model.
        user_id (int): Foreign key referencing the User model.
        assignment_date (datetime): The date and time of the assignment.
        asset (relationship): Many-to-one relationship with Asset model.
        user (relationship): Many-to-one relationship with User model.
    """
    __tablename__ = 'assignment'

    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key to Asset
    # nullable=False means every assignment MUST be linked to an asset
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    # Foreign Key to User
    # nullable=False means every assignment MUST be linked to a user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Date of the assignment, defaults to the current UTC time if not provided
    assignment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships are defined on the User and Asset models via backref

    def __repr__(self):
        # Show related object names for better readability
        asset_name = self.asset.name if self.asset else 'N/A'
        user_name = self.user.username if self.user else 'N/A'
        return f"Assignment(Asset: '{asset_name}', User: '{user_name}', Date: '{self.assignment_date.strftime('%Y-%m-%d %H:%M')}')"

# --- End of models ---
