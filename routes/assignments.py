# routes/assignments.py

"""
Asset Management System - Assignments Blueprint

This blueprint handles routes related to managing assignments (list, view, create, update, delete).
Accessible to Admin and Regular users (with restrictions for Regular users).
Includes pagination and sorting for the list view using a helper function.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
# Import necessary components from extensions and models
from extensions import db
from models import Assignment, Asset, User
from flask_login import login_required, current_user
from flask_wtf import FlaskForm # Need FlaskForm for dummy form
from datetime import datetime
# Import the pagination and sorting helper function from utils
from utils import paginate_and_sort_query


# Create a Blueprint named 'assignments'
assignments = Blueprint('assignments', __name__, url_prefix='/assignments') # Use url_prefix /assignments

# --- Assignment CRUD Routes ---
@assignments.route('/')
@login_required # Accessible to all logged-in users
def list_assignments():
    """
    Displays a paginated and sortable list of all assignments.
    Accessible to all logged-in users.

    Query parameters:
        page (int): The page number to display (defaults to 1).
        sort_by (str): The column to sort by ('date', 'asset_id', 'user_id'). Defaults to 'date'.
        sort_direction (str): The sort direction ('asc' or 'desc'). Defaults to 'desc'.

    Uses the paginate_and_sort_query helper function.

    Returns:
        str: Rendered HTML content for the assignments list page.
    """
    # Define valid columns for sorting and their model attributes
    valid_sort_columns = {
        'date': Assignment.assignment_date,
        'asset_id': Assignment.asset_id, # Sorting by the foreign key ID
        'user_id': Assignment.user_id    # Sorting by the foreign key ID
    }

    # Use the helper function to get the paginated and sorted results and the final sort parameters
    pagination, sort_by, sort_direction = paginate_and_sort_query(
        Assignment.query, # Pass the base query object
        Assignment,       # Pass the model class
        valid_sort_columns, # Pass the valid sort columns dictionary
        'date',           # Default sort by assignment_date
        'desc'            # Default sort direction descending (newest first)
        # per_page defaults to 10 in the helper function
    )

    # Create a dummy form for CSRF token usage in the delete form
    form = FlaskForm() # Simpler way to get a form with just CSRF token

    # Pass pagination object AND current sort parameters to the template
    return render_template('assignments.html',
                           pagination=pagination, # Contains items for the current page and pagination info
                           form=form, # Dummy form for CSRF
                           sort_by=sort_by, # Current sort column name (string)
                           sort_direction=sort_direction) # Current sort direction (string)


# Route to view a single assignment's details
# ... (rest of your assignments.py routes - view_assignment, create_assignment, update_assignment, delete_assignment - remain the same) ...
@assignments.route('/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    """Displays details for a specific assignment. Accessible to all logged-in users."""
    assignment = Assignment.query.get_or_404(assignment_id)
    form = FlaskForm() # Dummy form for CSRF
    return render_template('assignment_detail.html', title=f'Assignment ID: {assignment.id}', assignment=assignment, form=form)

@assignments.route('/new', methods=['GET', 'POST'])
@login_required
def create_assignment():
    """Handles creation of a new assignment. Accessible to Admin and Regular users."""
    if not current_user.is_admin and current_user.role != 'regular':
        flash('You do not have permission to create assignments.', 'danger')
        return redirect(url_for('assignments.list_assignments'))
    from forms import AssignmentForm
    form = AssignmentForm(Asset=Asset, User=User)
    if form.validate_on_submit():
        asset = Asset.query.get(form.asset.data)
        user = User.query.get(form.user.data)
        if asset and user:
            assignment = Assignment(asset=asset, user=user, assignment_date=datetime.utcnow())
            db.session.add(assignment)
            db.session.commit()
            flash('Assignment created successfully!', 'success')
            return redirect(url_for('assignments.list_assignments'))
        else:
            flash('Invalid Asset or User selected.', 'danger')
            return render_template('create_assignment.html', title='New Assignment', form=form)
    return render_template('create_assignment.html', title='New Assignment', form=form)

@assignments.route('/<int:assignment_id>/update', methods=['GET', 'POST'])
@login_required
def update_assignment(assignment_id):
    """Handles updating an existing assignment. Accessible to Admin and Regular users."""
    if not current_user.is_admin and current_user.role != 'regular':
        flash('You do not have permission to update assignments.', 'danger')
        return redirect(url_for('assignments.list_assignments'))
    assignment = Assignment.query.get_or_404(assignment_id)
    from forms import AssignmentForm
    form = AssignmentForm(Asset=Asset, User=User, current_assignment=assignment)
    if form.validate_on_submit():
        asset = Asset.query.get(form.asset.data)
        user = User.query.get(form.user.data)
        if asset and user:
            assignment.asset = asset
            assignment.user = user
            db.session.commit()
            flash('Assignment updated successfully!', 'success')
            return redirect(url_for('assignments.list_assignments'))
        else:
            flash('Invalid Asset or User selected.', 'danger')
            return render_template('update_assignment.html', title='Update Assignment', form=form, assignment=assignment)
    elif request.method == 'GET':
        form.asset.data = assignment.asset_id
        form.user.data = assignment.user_id
    return render_template('update_assignment.html', title='Update Assignment', form=form, assignment=assignment)

@assignments.route('/<int:assignment_id>/delete', methods=['POST'])
@login_required
def delete_assignment(assignment_id):
    """Handles deletion of an existing assignment. Accessible only to Admin users."""
    if not current_user.is_admin:
        flash('You do not have permission to delete assignments.', 'danger')
        return redirect(url_for('assignments.list_assignments'))
    assignment = Assignment.query.get_or_404(assignment_id)
    db.session.delete(assignment)
    db.session.commit()
    flash('Assignment deleted successfully!', 'success')
    return redirect(url_for('assignments.list_assignments'))

# --- End Assignment CRUD Routes ---
