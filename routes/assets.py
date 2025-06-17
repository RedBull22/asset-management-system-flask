# routes/assets.py

"""
Asset Management System - Assets Blueprint

This blueprint handles routes related to managing assets (list, view, create, update, delete).
Includes pagination and sorting for the list view using a helper function.
Permissions are enforced based on user roles (Admin/Regular).
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
# Import necessary components from extensions and models
from extensions import db
from models import Asset, AssetType, Assignment
from flask_login import login_required, current_user
from flask_wtf import FlaskForm # Need FlaskForm for dummy form
# Import the pagination and sorting helper function from utils
from utils import paginate_and_sort_query


# Create a Blueprint named 'assets'
assets = Blueprint('assets', __name__)

# --- Asset CRUD Routes ---
@assets.route('/assets')
@login_required # Protect this route - requires login for any user
def list_assets():
    """
    Displays a paginated and sortable list of all assets.
    Accessible to all logged-in users.

    Query parameters:
        page (int): The page number to display (defaults to 1).
        sort_by (str): The column to sort by ('name', 'serial_number', 'asset_type_id'). Defaults to 'name'.
        sort_direction (str): The sort direction ('asc' or 'desc'). Defaults to 'asc'.

    Uses the paginate_and_sort_query helper function.

    Returns:
        str: Rendered HTML content for the assets list page.
    """
    # Define valid columns for sorting and their model attributes
    valid_sort_columns = {
        'name': Asset.name,
        'serial_number': Asset.serial_number,
        'asset_type_id': Asset.asset_type_id
    }

    # Use the helper function to get the paginated and sorted results and the final sort parameters
    pagination, sort_by, sort_direction = paginate_and_sort_query(
        Asset.query, # Pass the base query object
        Asset,       # Pass the model class
        valid_sort_columns, # Pass the valid sort columns dictionary
        'name',      # Default sort by name
        'asc'        # Default sort direction ascending
        # per_page defaults to 10 in the helper function
    )


    # Create a dummy form for CSRF token usage in the delete form within the template
    # This can also be simplified by just passing FlaskForm() directly
    # class EmptyForm(FlaskForm):
    #     pass
    # form = EmptyForm()
    form = FlaskForm() # Simpler way to get a form with just CSRF token

    # Render the template, passing the pagination object and current sort parameters
    return render_template('assets.html',
                           pagination=pagination, # Contains items for the current page and pagination info
                           form=form, # Dummy form for CSRF
                           sort_by=sort_by, # Current sort column name (string)
                           sort_direction=sort_direction) # Current sort direction (string)


# Route to view a single asset's details
# ... (rest of your assets.py routes - view_asset, create_asset, update_asset, delete_asset - remain the same) ...
@assets.route('/asset/<int:asset_id>')
@login_required
def view_asset(asset_id):
    """
    Displays details for a specific asset.
    Accessible to all logged-in users.
    """
    asset = Asset.query.get_or_404(asset_id)
    form = FlaskForm() # Dummy form for CSRF
    return render_template('asset_detail.html', title=f'Asset: {asset.name}', asset=asset, form=form)

@assets.route('/asset/new', methods=['GET', 'POST'])
@login_required
def create_asset():
    """Handles creation of a new asset. Accessible to Admin and Regular users."""
    if not current_user.is_admin and current_user.role != 'regular':
        flash('You do not have permission to create assets.', 'danger')
        return redirect(url_for('assets.list_assets'))
    from forms import AssetForm
    form = AssetForm(Asset=Asset)
    form.asset_type.choices = [(at.id, at.name) for at in AssetType.query.all()]
    if form.validate_on_submit():
        asset_type = AssetType.query.get(form.asset_type.data)
        if asset_type:
            asset = Asset(name=form.name.data, serial_number=form.serial_number.data, asset_type=asset_type)
            db.session.add(asset)
            db.session.commit()
            flash('Asset created successfully!', 'success')
            return redirect(url_for('assets.list_assets'))
        else:
             flash('Invalid asset type selected.', 'danger')
             return render_template('create_asset.html', title='New Asset', form=form)
    return render_template('create_asset.html', title='New Asset', form=form)

@assets.route('/asset/<int:asset_id>/update', methods=['GET', 'POST'])
@login_required
def update_asset(asset_id):
    """Handles updating an existing asset. Accessible to Admin and Regular users."""
    if not current_user.is_admin and current_user.role != 'regular':
         flash('You do not have permission to update assets.', 'danger')
         return redirect(url_for('assets.list_assets'))
    asset = Asset.query.get_or_404(asset_id)
    from forms import AssetForm
    form = AssetForm(Asset=Asset, current_asset=asset)
    form.asset_type.choices = [(at.id, at.name) for at in AssetType.query.all()]
    if form.validate_on_submit():
        asset.name = form.name.data
        asset.serial_number = form.serial_number.data
        asset_type = AssetType.query.get(form.asset_type.data)
        if asset_type:
             asset.asset_type = asset_type
        else:
             flash('Invalid asset type selected.', 'danger')
             return render_template('update_asset.html', title='Update Asset', form=form, asset=asset)
        db.session.commit()
        flash('Asset updated successfully!', 'success')
        return redirect(url_for('assets.list_assets'))
    elif request.method == 'GET':
        form.name.data = asset.name
        form.serial_number.data = asset.serial_number
        form.asset_type.data = asset.asset_type_id
    return render_template('update_asset.html', title='Update Asset', form=form, asset=asset)

@assets.route('/asset/<int:asset_id>/delete', methods=['POST'])
@login_required
def delete_asset(asset_id):
    """Handles deletion of an existing asset. Accessible only to Admin users."""
    if not current_user.is_admin:
        flash('You do not have permission to delete assets.', 'danger')
        return redirect(url_for('assets.list_assets'))
    asset = Asset.query.get_or_404(asset_id)
    if asset.assignments:
        flash(f'Cannot delete asset "{asset.name}" because it is linked to {len(asset.assignments)} assignments.', 'danger')
        return redirect(url_for('assets.list_assets'))
    db.session.delete(asset)
    db.session.commit()
    flash('Asset deleted successfully!', 'success')
    return redirect(url_for('assets.list_assets'))

# --- End Asset CRUD Routes ---
