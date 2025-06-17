# routes/auth.py

"""
Asset Management System - Authentication Blueprint

This blueprint handles user authentication routes: registration, login, and logout.
It uses Flask-Login for session management and Flask-Bcrypt for password hashing.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
# Import bcrypt and db instances from extensions.py
from extensions import bcrypt, db # Need bcrypt for hashing, db for adding new users
# Import forms and models
from forms import RegistrationForm, LoginForm # Import forms
from models import User # Import User model

# Create the authentication blueprint
auth = Blueprint('auth', __name__, url_prefix='/auth') # Use url_prefix to prepend /auth to all routes


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration.

    GET: Displays the registration form.
    POST: Validates form data, creates a new user, and redirects to login.
    """
    # If user is already logged in, redirect to homepage
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Pass the User model to the form for custom validation (__init__ method)
    form = RegistrationForm(User=User)

    # Validate form data on POST request
    if form.validate_on_submit():
        # Hash the password before creating the user object
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Create a new User instance
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        # Add the new user to the database session and commit
        db.session.add(user)
        db.session.commit()
        # Flash a success message to be displayed on the next page
        flash('Your account has been created! You are now able to log in.', 'success')
        # Redirect the user to the login page
        return redirect(url_for('auth.login'))

    # Render the registration template on GET request or if form validation fails
    return render_template('register.html', title='Register', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.

    GET: Displays the login form.
    POST: Validates form data, authenticates user, and logs them in.
    """
    # If user is already logged in, redirect to homepage
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Pass the User model to the form (optional for login, but good for consistency)
    form = LoginForm(User=User)

    # Validate form data on POST request
    if form.validate_on_submit():
        # Find the user by email
        # Use db.session.execute() for SQLAlchemy 2.0+ style querying
        user = db.session.execute(db.select(User).filter_by(email=form.email.data)).scalar_one_or_none()

        # Check if user exists and the password is correct
        if user and user.check_password(form.password.data):
            # Log the user in using Flask-Login
            login_user(user, remember=form.remember.data)
            # Redirect to the page the user tried to access before logging in (if any),
            # otherwise redirect to the index page.
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            # Redirect to next_page if it exists and is safe, otherwise redirect to index
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            # Flash an error message for invalid login attempt
            flash('Login Unsuccessful. Please check email and password', 'danger')

    # Render the login template on GET request or if form validation fails
    return render_template('login.html', title='Login', form=form)


@auth.route('/logout')
@login_required # User must be logged in to log out
def logout():
    """
    Logs out the current user.

    Redirects to the homepage after logging out.
    """
    logout_user() # Use Flask-Login's logout_user function
    flash('You have been logged out.', 'info')
    # Redirect to the index page after logout
    return redirect(url_for('index'))

# --- End of Authentication Routes ---
