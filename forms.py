# forms.py

"""
Asset Management System - Forms File

This file defines Flask-WTF forms used for handling user input
for registration, login, and CRUD operations on models.
It includes basic validators and custom validation logic.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
# Import necessary validators
from wtforms.validators import DataRequired, Length, ValidationError, Email, EqualTo, Optional

# Import your models from models.py
# We import the model classes themselves, not db or bcrypt instances here
# This helps break the circular import chain by only needing the class definitions
from models import User, Asset, AssetType, Assignment # Import all necessary models

# Define a custom validator function for password strength
def validate_password_strength(form, field):
    """
    Custom validator to check the strength of a password field.

    Args:
        form: The Flask-WTF form object.
        field: The specific field being validated (the password field).

    Raises:
        ValidationError: If the password does not meet the strength criteria.
    """
    password = field.data
    # Basic strength check: minimum length and requiring at least one digit
    if len(password) < 6:
        raise ValidationError('Password must be at least 6 characters long.')
    if not any(char.isdigit() for char in password):
        raise ValidationError('Password must contain at least one digit.')
    # You could add checks for uppercase, lowercase, symbols, etc. here for stricter requirements:
    # if not any(char.isupper() for char in password):
    #     raise ValidationError('Password must contain at least one uppercase letter.')
    # if not any(char.islower() for char in password):
    #     raise ValidationError('Password must contain at least one lowercase letter.')
    # if not any(not char.isalnum() for char in password): # isalnum checks if char is alphanumeric
    #     raise ValidationError('Password must contain at least one symbol.')


# --- Form for creating/updating Assets ---
class AssetForm(FlaskForm):
    """Form for creating and updating assets."""
    # DataRequired ensures the field is not empty
    # Length sets minimum and maximum length constraints
    name = StringField('Asset Name', validators=[DataRequired(), Length(min=1, max=100)])
    serial_number = StringField('Serial Number', validators=[DataRequired(), Length(min=1, max=50)])
    # SelectField for Asset Type - choices will be populated dynamically in the route
    # coerce=int ensures the selected value is treated as an integer ID
    asset_type = SelectField('Asset Type', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Asset')

    # Modify __init__ to accept the Asset model for custom validation AND an optional current_asset object
    def __init__(self, *args, **kwargs):
        """
        Initializes the AssetForm.

        Args:
            Asset (Model): The SQLAlchemy Asset model class (passed for validation).
            current_asset (Asset, optional): The Asset object being updated (passed for unique validation).
        """
        # Asset model is now imported directly at the top
        self.Asset = kwargs.pop('Asset', Asset) # Default to imported model if not passed
        self.current_asset = kwargs.pop('current_asset', None) # Accept current_asset object for updates
        super(AssetForm, self).__init__(*args, **kwargs)

    # Custom validation method for the serial_number field
    # This method is automatically called by Flask-WTF because it's named validate_<fieldname>
    def validate_serial_number(self, serial_number):
        """
        Custom validator to check for unique serial number, excluding the current asset if updating.

        Args:
            serial_number: The serial_number field object.

        Raises:
            ValidationError: If another asset with the same serial number already exists.
        """
        # Only perform this check if the form is valid so far and the serial number field has data
        if serial_number.data:
            if self.Asset:
                 # Query for an asset with this serial number that IS NOT the current asset
                 query = self.Asset.query.filter_by(serial_number=serial_number.data)
                 if self.current_asset:
                     # Exclude the current asset when checking for uniqueness during an update
                     query = query.filter(self.Asset.id != self.current_asset.id)

                 asset = query.first() # Check if any *other* asset exists with that serial

                 if asset: # If another asset is found with that serial number...
                      raise ValidationError('An asset with this serial number already exists.')
            else:
                 # This print helps debug if the model isn't passed correctly during form creation
                 print("Warning: Asset model not available in AssetForm for validation.")


# --- Define the Registration form ---
class RegistrationForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    # Email() validator checks for basic email format
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Added custom strength validator to the password field
    password = PasswordField('Password', validators=[DataRequired(), validate_password_strength])
    # EqualTo checks if this field matches another field ('password')
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    # BooleanField doesn't typically need validators
    submit = SubmitField('Sign Up')

    # Add an __init__ method to accept the User model for custom validation
    def __init__(self, *args, **kwargs):
        """
        Initializes the RegistrationForm.

        Args:
            User (Model): The SQLAlchemy User model class (passed for validation).
        """
        # User model is now imported directly at the top
        self.User = kwargs.pop('User', User) # Default to imported model if not passed
        super(RegistrationForm, self).__init__(*args, **kwargs)

    # Custom validation methods to check if username or email already exists (for creation)
    # These validators are only called if the basic validators (DataRequired, Length, Email) pass
    def validate_username(self, username):
        """
        Custom validator to check if the username already exists.

        Args:
            username: The username field object.

        Raises:
            ValidationError: If the username is already taken.
        """
        # Only perform this check if the form is valid so far and the field has data
        if username.data:
            if self.User:
                 user = self.User.query.filter_by(username=username.data).first()
                 if user:
                     raise ValidationError('That username is taken. Please choose a different one.')
            else:
                 print("Warning: User model not available in RegistrationForm for username validation.")

    def validate_email(self, email):
        """
        Custom validator to check if the email already exists.

        Args:
            email: The email field object.

        Raises:
            ValidationError: If the email is already taken.
        """
        # Only perform this check if the form is valid so far and the field has data
        if email.data:
            if self.User:
                 user = self.User.query.filter_by(email=email.data).first()
                 if user:
                     raise ValidationError('That email is taken. Please choose a different one.')
            else:
                 print("Warning: User model not available in RegistrationForm for email validation.")


# --- Define the Login form ---
class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    # No strength check needed for login, only DataRequired
    password = PasswordField('Password', validators=[DataRequired()])
    # BooleanField doesn't typically need validators
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    # Add an __init__ method to accept the User model (optional for login, but kept for consistency)
    def __init__(self, *args, **kwargs):
         """Initializes the LoginForm (User model passed for potential future use)."""
         # User model is now imported directly at the top
         self.User = kwargs.pop('User', User) # Default to imported model if not passed
         super(LoginForm, self).__init__(*args, **kwargs)


# --- Form for creating/updating Asset Types (Admin only) ---
class AssetTypeForm(FlaskForm):
    """Form for creating and updating asset types."""
    name = StringField('Asset Type Name', validators=[DataRequired(), Length(min=1, max=50)])
    submit = SubmitField('Save Asset Type')

    # Add an __init__ method to accept the AssetType model and an optional current_asset_type object
    def __init__(self, *args, **kwargs):
        """
        Initializes the AssetTypeForm.

        Args:
            AssetType (Model): The SQLAlchemy AssetType model class (passed for validation).
            current_asset_type (AssetType, optional): The AssetType object being updated (passed for unique validation).
        """
        # AssetType model is now imported directly at the top
        self.AssetType = kwargs.pop('AssetType', AssetType) # Default to imported model if not passed
        self.current_asset_type = kwargs.pop('current_asset_type', None) # Accept current_asset_type for updates
        super(AssetTypeForm, self).__init__(*args, **kwargs)


    # Custom validation for unique asset type name (handles updates)
    def validate_name(self, name):
        """
        Custom validator to check for unique asset type name, excluding the current asset type if updating.

        Args:
            name: The name field object.

        Raises:
            ValidationError: If another asset type with the same name already exists.
        """
         # Only perform this check if the form is valid so far and the name field has data
        if name.data:
            if self.AssetType:
                # Query for an asset type with this name that IS NOT the current asset type
                query = self.AssetType.query.filter_by(name=name.data)
                if self.current_asset_type:
                    # Exclude the current asset type when checking for uniqueness during an update
                    query = query.filter(self.AssetType.id != self.current_asset_type.id)

                asset_type = query.first() # Check if any *other* asset type exists with this name

                if asset_type: # If another asset type is found with that name...
                     raise ValidationError('An asset type with this name already exists.')
            else:
                print("Warning: AssetType model not available in AssetTypeForm for validation.")

# --- Form for creating new Users (Admin only) ---
class UserForm(FlaskForm):
    """Form for creating new users (Admin only)."""
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Added custom strength validator to the password field
    password = PasswordField('Password', validators=[DataRequired(), validate_password_strength])
    # EqualTo checks if this field matches another field ('password')
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    # Role can be selected when creating
    # SelectField handles valid choices based on the 'choices' argument
    role = SelectField('Role', choices=[('regular', 'Regular User'), ('admin', 'Admin User')], validators=[DataRequired()])
    submit = SubmitField('Create User')

    # Add __init__ to accept User model for custom validation
    def __init__(self, *args, **kwargs):
        """
        Initializes the UserForm.

        Args:
            User (Model): The SQLAlchemy User model class (passed for validation).
        """
        # User model is now imported directly at the top
        self.User = kwargs.pop('User', User) # Default to imported model if not passed
        super(UserForm, self).__init__(*args, **kwargs)

    # Custom validation methods to check if username or email already exists (for creation)
    def validate_username(self, username):
        """
        Custom validator to check if the username already exists.

        Args:
            username: The username field object.

        Raises:
            ValidationError: If the username is already taken.
        """
         # Only perform this check if the form is valid so far and the field has data
        if username.data:
            if self.User:
                 user = self.User.query.filter_by(username=username.data).first()
                 if user:
                     raise ValidationError('That username is taken. Please choose a different one.')
            else:
                 print("Warning: User model not available in UserForm for username validation.")

    def validate_email(self, email):
        """
        Custom validator to check if the email already exists.

        Args:
            email: The email field object.

        Raises:
            ValidationError: If the email is already taken.
        """
         # Only perform this check if the form is valid so far and the field has data
        if email.data:
            if self.User:
                 user = self.User.query.filter_by(email=email.data).first()
                 if user:
                     raise ValidationError('That email is taken. Please choose a different one.')
            else:
                 print("Warning: User model not available in UserForm for email validation.")

# --- Form for updating existing Users (Admin only) ---
class UpdateUserForm(FlaskForm):
    """Form for updating existing users (Admin only)."""
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Password fields are optional for update, only required if changing
    # If password IS provided (Optional() passes), it must meet strength and EqualTo checks
    password = PasswordField('New Password', validators=[Optional(), validate_password_strength])
    confirm_password = PasswordField('Confirm New Password',
                                     validators=[Optional(), EqualTo('password', message='Passwords must match.')])
    # Role can be updated
    # SelectField handles valid choices based on the 'choices' argument
    role = SelectField('Role', choices=[('regular', 'Regular User'), ('admin', 'Admin User')], validators=[DataRequired()])
    submit = SubmitField('Update User')

    # Add __init__ to accept User model AND the current_user object being updated
    def __init__(self, *args, **kwargs):
        """
        Initializes the UpdateUserForm.

        Args:
            User (Model): The SQLAlchemy User model class (passed for validation).
            current_user_obj (User): The User object being updated (passed for unique validation).
        """
        # User model is now imported directly at the top
        self.User = kwargs.pop('User', User) # Default to imported model if not passed
        self.current_user_obj = kwargs.pop('current_user_obj', None) # Pass the user object being updated
        super(UpdateUserForm, self).__init__(*args, **kwargs)

    # Custom validation methods to check for unique username/email (for update)
    def validate_username(self, username):
        """
        Custom validator to check for unique username, excluding the current user being updated.

        Args:
            username: The username field object.

        Raises:
            ValidationError: If another user with the same username already exists.
        """
         # Only perform this check if the form is valid so far and the field has data
        if username.data:
            if self.User and self.current_user_obj:
                 # Query for a user with this username that IS NOT the current user being updated
                 user = self.User.query.filter_by(username=username.data).first()
                 if user and user.id != self.current_user_obj.id:
                     raise ValidationError('That username is taken. Please choose a different one.')
            else:
                print("Warning: User model or current_user_obj not available in UpdateUserForm for username validation.")


    def validate_email(self, email):
        """
        Custom validator to check for unique email, excluding the current user being updated.

        Args:
            email: The email field object.

        Raises:
            ValidationError: If another user with the same email already exists.
        """
         # Only perform this check if the form is valid so far and the field has data
        if email.data:
            if self.User and self.current_user_obj:
                 # Query for a user with this email that IS NOT the current user being updated
                 user = self.User.query.filter_by(email=email.data).first()
                 if user and user.id != self.current_user_obj.id:
                     raise ValidationError('That email is taken. Please choose a different one.')
            else:
                 print("Warning: User model or current_user_obj not available in UpdateUserForm for email validation.")

# --- Form for creating/updating Assignments ---
class AssignmentForm(FlaskForm):
    """Form for creating and updating assignments."""
    # SelectField for Asset - choices will be populated dynamically in the route's GET request
    # coerce=int ensures the selected value is treated as an integer ID
    asset = SelectField('Asset', coerce=int, validators=[DataRequired()])
    # SelectField for User - choices will be populated dynamically in the route's GET request
    # coerce=int ensures the selected value is treated as an integer ID
    user = SelectField('User', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Assignment')

    # Add __init__ to accept Asset and User models for populating choices
    # Also accept current_assignment object if updating
    def __init__(self, *args, **kwargs):
        """
        Initializes the AssignmentForm.

        Args:
            Asset (Model): The SQLAlchemy Asset model class (passed for populating choices).
            User (Model): The SQLAlchemy User model class (passed for populating choices).
            current_assignment (Assignment, optional): The Assignment object being updated.
        """
        # Asset and User models are now imported directly at the top
        self.Asset = kwargs.pop('Asset', Asset) # Default to imported model if not passed
        self.User = kwargs.pop('User', User) # Default to imported model if not passed
        # Pass the current assignment object if updating (optional, not used in validation currently)
        self.current_assignment = kwargs.pop('current_assignment', None)
        super(AssignmentForm, self).__init__(*args, **kwargs)

        # Populate choices here if models were passed
        # This happens on GET requests when the form is rendered
        if self.Asset:
             # Query all assets and create choices list (value, label)
             self.asset.choices = [(a.id, f'{a.name} (SN: {a.serial_number})') for a in self.Asset.query.all()]
        else:
             print("Warning: Asset model not available in AssignmentForm for asset choices.")

        if self.User:
             # Query all users and create choices list (value, label)
             self.user.choices = [(u.id, f'{u.username} ({u.email})') for u in self.User.query.all()]
        else:
             print("Warning: User model not available in AssignmentForm for user choices.")

    # Optional: Add custom validation to prevent assigning an asset already assigned
    # This is more complex validation and might be beyond "almost flawless" basic validation
    # It requires checking the Assignment table for existing assignments for the selected asset
    # def validate_asset(self, asset):
    #     """
    #     Optional custom validator to prevent assigning an asset that is already assigned.
    #     Note: This validator is commented out as it adds complexity beyond basic requirements.
    #     """
    #     if asset.data: # Only validate if an asset was selected
    #         # Query for any existing assignment with this asset ID
    #         # Import Assignment model locally if not imported at top (it is imported at top here)
    #         query = Assignment.query.filter_by(asset_id=asset.data)
    #         if self.current_assignment:
    #             # Exclude the current assignment if we're updating
    #             query = query.filter(Assignment.id != self.current_assignment.id)
    #         existing_assignment = query.first()
    #         if existing_assignment:
    #             raise ValidationError('This asset is already assigned.')


# --- End of forms ---
