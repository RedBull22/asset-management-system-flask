# routes/users.py

"""
Asset Management System - Users Blueprint

This blueprint handles routes related to managing users (list, view, create, update, delete).
These routes are restricted to Admin users only.
Includes pagination and sorting for the list view using a helper function.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
# Import necessary components from extensions and models
from extensions import db, bcrypt
from models import User, Assignment
from flask_login import login_required, current_user
from flask_wtf import FlaskForm # Need FlaskForm for dummy form
# Import the pagination and sorting helper function from utils
from utils import paginate_and_sort_query


# Create a Blueprint named 'users'
users = Blueprint('users', __name__, url_prefix='/users') # Use url_prefix /users


# --- User CRUD Routes (Admin Only) ---
@users.route('/')
@login_required
def list_users():
    """
    Displays a paginated and sortable list of all users.
    Accessible only to Admin users.

    Query parameters:
        page (int): The page number to display (defaults to 1).
        sort_by (str): The column to sort by ('username', 'email', 'role'). Defaults to 'username'.
        sort_direction (str): The sort direction ('asc' or 'desc'). Defaults to 'asc'.

    Uses the paginate_and_sort_query helper function.

    Returns:
        str: Rendered HTML content for the users list page.
        Response: Redirect to index if unauthorized.
    """
    # Check if the current user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to view users.', 'danger')
        return redirect(url_for('index')) # Redirect to homepage if unauthorized

    # Define valid columns for sorting and their model attributes
    valid_sort_columns = {
        'username': User.username,
        'email': User.email,
        'role': User.role
    }

    # Use the helper function to get the paginated and sorted results and the final sort parameters
    pagination, sort_by, sort_direction = paginate_and_sort_query(
        User.query,     # Pass the base query object
        User,           # Pass the model class
        valid_sort_columns, # Pass the valid sort columns dictionary
        'username',     # Default sort by username
        'asc'           # Default sort direction ascending
        # per_page defaults to 10 in the helper function
    )

    # Create a dummy form for CSRF token usage in the delete form
    form = FlaskForm() # Simpler way to get a form with just CSRF token

    # Render the template, passing the pagination object and current sort parameters
    return render_template('users.html',
                           pagination=pagination, # Contains items for the current page and pagination info
                           form=form, # Dummy form for CSRF
                           sort_by=sort_by, # Current sort column name (string)
                           sort_direction=sort_direction) # Current sort direction (string)


# Route to view a single user's details
# ... (rest of your users.py routes - view_user, create_user, update_user, delete_user - remain the same) ...
@users.route('/<int:user_id>')
@login_required
def view_user(user_id):
    """Displays details for a specific user. Accessible only to Admin users."""
    if not current_user.is_admin:
        flash('You do not have permission to view user details.', 'danger')
        return redirect(url_for('index'))
    user_to_view = User.query.get_or_404(user_id)
    form = FlaskForm() # Dummy form for CSRF
    return render_template('user_detail.html', title=f'User: {user_to_view.username}', user=user_to_view, form=form)

@users.route('/new', methods=['GET', 'POST'])
@login_required
def create_user():
    """Handles creation of a new user. Accessible only to Admin users."""
    if not current_user.is_admin:
        flash('You do not have permission to create users.', 'danger')
        return redirect(url_for('users.list_users'))
    from forms import UserForm
    form = UserForm(User=User)
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User "{user.username}" created successfully!', 'success')
        return redirect(url_for('users.list_users'))
    return render_template('create_user.html', title='New User', form=form)

@users.route('/<int:user_id>/update', methods=['GET', 'POST'])
@login_required
def update_user(user_id):
    """Handles updating an existing user. Accessible only to Admin users."""
    if not current_user.is_admin:
        flash('You do not have permission to update users.', 'danger')
        return redirect(url_for('users.list_users'))
    user_to_update = User.query.get_or_404(user_id)
    from forms import UpdateUserForm
    form = UpdateUserForm(User=User, current_user_obj=user_to_update)
    original_role = user_to_update.role
    if form.validate_on_submit():
        admin_self_demotion_attempted = False
        if current_user.id == user_to_update.id and form.role.data != 'admin':
             flash('You cannot change your own role from admin.', 'warning')
             admin_self_demotion_attempted = True
        user_to_update.username = form.username.data
        user_to_update.email = form.email.data
        if not admin_self_demotion_attempted:
             user_to_update.role = form.role.data
        if form.password.data:
             user_to_update.set_password(form.password.data)
        db.session.commit()
        if not admin_self_demotion_attempted:
            flash(f'User "{user_to_update.username}" updated successfully!', 'success')
        return redirect(url_for('users.list_users'))
    elif request.method == 'GET':
        form.username.data = user_to_update.username
        form.email.data = user_to_update.email
        form.role.data = user_to_update.role
    return render_template('update_user.html', title='Update User', form=form, user=user_to_update)

@users.route('/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Handles deletion of an existing user. Accessible only to Admin users."""
    if not current_user.is_admin:
        flash('You do not have permission to delete users.', 'danger')
        return redirect(url_for('users.list_users'))
    user_to_delete = User.query.get_or_404(user_id)
    if current_user.id == user_to_delete.id:
        flash('You cannot delete your own account.', 'warning')
        return redirect(url_for('users.list_users'))
    if user_to_delete.assignments:
         flash(f'Cannot delete user "{user_to_delete.username}" because they are linked to {len(user_to_delete.assignments)} assignments.', 'danger')
         return redirect(url_for('users.list_users'))
    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f'User "{user_to_delete.username}" deleted successfully!', 'success')
    return redirect(url_for('users.list_users'))

# --- End User CRUD Routes ---
