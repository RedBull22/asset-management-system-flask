# routes/asset_types.py

"""
Asset Management System - Asset Types Blueprint

This blueprint handles routes related to managing asset types (list, view, create, update, delete).
These routes are restricted to Admin users only.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
# Import necessary components from extensions and models
from extensions import db
from models import AssetType, Asset # Need AssetType and Asset models
from flask_login import login_required, current_user
from flask_wtf import FlaskForm # Need FlaskForm for dummy form


# Create a Blueprint named 'asset_types'
asset_types = Blueprint('asset_types', __name__, url_prefix='/asset_types') # Use url_prefix /asset_types


# --- Asset Type CRUD Routes (Admin Only) ---
@asset_types.route('/')
@login_required
def list_asset_types():
    """
    Displays a list of all asset types.
    Accessible only to Admin users.

    Returns:
        str: Rendered HTML content for the asset types list page.
        Response: Redirect to index if unauthorized.
    """
    # Check if the current user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to view asset types.', 'danger')
        return redirect(url_for('index')) # Redirect to homepage if unauthorized

    # Get all asset types from the database
    # Note: Pagination/Sorting not implemented here as lists are expected to be small
    asset_types = AssetType.query.all()

    # Create a dummy form for CSRF token usage in the delete form within the template
    class EmptyForm(FlaskForm):
        pass
    form = EmptyForm() # Pass form for delete confirmation CSRF

    # Render the template, passing the list of asset types and the form
    return render_template('asset_types.html', asset_types=asset_types, form=form)

# Route to view a single asset type's details (optional, not strictly needed for brief but good practice)
# @asset_types.route('/<int:asset_type_id>')
# @login_required
# def view_asset_type(asset_type_id):
#     """
#     Displays details for a specific asset type.
#     Accessible only to Admin users.
#
#     Args:
#         asset_type_id (int): The ID of the asset type to view.
#
#     Returns:
#         str: Rendered HTML content for the asset type detail page.
#         Response: Redirect to index if unauthorized.
#         404: If the asset type ID does not exist.
#     """
#     if not current_user.is_admin:
#         flash('You do not have permission to view asset type details.', 'danger')
#         return redirect(url_for('index'))
#
#     asset_type = AssetType.query.get_or_404(asset_type_id)
#     # Note: You might want to display assets linked to this type here
#     # assets_of_type = Asset.query.filter_by(asset_type=asset_type).all()
#
#     return render_template('asset_type_detail.html', title=f'Asset Type: {asset_type.name}', asset_type=asset_type)


@asset_types.route('/new', methods=['GET', 'POST'])
@login_required
def create_asset_type():
    """
    Handles creation of a new asset type.
    Accessible only to Admin users.

    GET: Displays the create asset type form.
    POST: Validates form data, creates a new asset type, and redirects to the list.

    Returns:
        str or Response: Rendered HTML content for the form or a redirect response.
    """
    # Check if the current user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to create asset types.', 'danger')
        return redirect(url_for('asset_types.list_asset_types')) # Redirect to list if unauthorized

    # Pass the AssetType model to the form for custom validation
    from forms import AssetTypeForm # Import form here
    form = AssetTypeForm(AssetType=AssetType) # Pass the AssetType model instance

    # Validate form data on POST request
    if form.validate_on_submit():
        # Create a new AssetType instance
        asset_type = AssetType(name=form.name.data)
        # Add the new asset type to the database session and commit
        db.session.add(asset_type)
        db.session.commit()
        # Flash a success message and redirect to the asset types list
        flash('Asset type created successfully!', 'success')
        return redirect(url_for('asset_types.list_asset_types'))

    # Render the create asset type template on GET request or if form validation fails
    return render_template('create_asset_type.html', title='New Asset Type', form=form)


@asset_types.route('/<int:asset_type_id>/update', methods=['GET', 'POST'])
@login_required
def update_asset_type(asset_type_id):
    """
    Handles updating an existing asset type.
    Accessible only to Admin users.

    Args:
        asset_type_id (int): The ID of the asset type to update.

    GET: Displays the update asset type form pre-populated with current data.
    POST: Validates form data, updates the asset type, and redirects to the list.

    Returns:
        str or Response: Rendered HTML content for the form or a redirect response.
        404: If the asset type ID does not exist.
    """
    # Check if the current user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to update asset types.', 'danger')
        return redirect(url_for('asset_types.list_asset_types')) # Redirect if unauthorized

    # Get the asset type by ID, using get_or_404
    asset_type = AssetType.query.get_or_404(asset_type_id)

    # Pass the AssetType model AND the current asset type object to the form for custom validation
    from forms import AssetTypeForm # Import form here
    form = AssetTypeForm(AssetType=AssetType, current_asset_type=asset_type) # Pass model and current object

    # Validate form data on POST request
    if form.validate_on_submit():
        # Update the asset type object with data from the form
        asset_type.name = form.name.data
        # Commit the changes to the database
        db.session.commit()
        # Flash a success message and redirect to the asset types list
        flash('Asset type updated successfully!', 'success')
        return redirect(url_for('asset_types.list_asset_types'))

    # On GET request, populate the form fields with the current asset type data
    elif request.method == 'GET':
        form.name.data = asset_type.name

    # Render the update asset type template on GET or if form validation fails on POST
    return render_template('update_asset_type.html', title='Update Asset Type', form=form, asset_type=asset_type)


@asset_types.route('/<int:asset_type_id>/delete', methods=['POST']) # Only accept POST requests for deletion
@login_required
def delete_asset_type(asset_type_id):
    """
    Handles deletion of an existing asset type.
    Accessible only to Admin users.

    Args:
        asset_type_id (int): The ID of the asset type to delete.

    Returns:
        Response: Redirect response.
        404: If the asset type ID does not exist.
    """
    # Check if the current user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to delete asset types.', 'danger')
        return redirect(url_for('asset_types.list_asset_types')) # Redirect if unauthorized

    # Get the asset type by ID, using get_or_404
    asset_type = AssetType.query.get_or_404(asset_type_id)

    # --- IMPORTANT: Handle related assets! ---
    # Prevent deletion if there are assets linked to this asset type due to foreign key constraint
    if asset_type.assets: # Check if the asset type has any related assets
         flash(f'Cannot delete asset type "{asset_type.name}" because it is linked to {len(asset_type.assets)} assets.', 'danger')
         return redirect(url_for('asset_types.list_asset_types')) # Redirect back with error message


    # If no related assets, proceed with deletion
    db.session.delete(asset_type)
    db.session.commit()
    flash('Asset type deleted successfully!', 'success')

    return redirect(url_for('asset_types.list_asset_types')) # Redirect to the asset types list after deletion

# --- End Asset Type CRUD Routes ---
