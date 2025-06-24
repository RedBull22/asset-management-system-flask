# utils.py

"""
Asset Management System - Utility Functions

This file contains helper functions used across the application,
such as the logic for handling pagination and sorting database queries.
"""

from flask import request
# Import db from extensions to access query object and its functions (like db.func.lower)
from extensions import db
# Import String type from SQLAlchemy to check column types for case-insensitive sorting
from sqlalchemy.types import String

# Import models to reference model attributes for sorting
# (These imports are already in your file, ensuring they are here for completeness)
from models import Asset, User, Assignment, AssetType


def paginate_and_sort_query(query, model, valid_sort_columns, default_sort_by, default_sort_direction, per_page=10):
    """
    Applies pagination and sorting logic to a SQLAlchemy query object.
    Includes case-insensitive sorting for string columns.

    Args:
        query: The base SQLAlchemy query object (e.g., User.query).
        model: The SQLAlchemy model class the query is for (e.g., User).
        valid_sort_columns (dict): A dictionary mapping URL parameter names (str)
                                   to SQLAlchemy model attributes (e.g., {'username': User.username}).
        default_sort_by (str): The default column name (key in valid_sort_columns) to sort by.
        default_sort_direction (str): The default sort direction ('asc' or 'desc').
        per_page (int): The number of items per page for pagination (defaults to 10).

    Returns:
        tuple: A tuple containing:
               - pagination object: The Flask-SQLAlchemy pagination object.
               - sort_by (str): The validated sort column name used.
               - sort_direction (str): The validated sort direction used.
    """
    # Get pagination parameters from the URL, default to page 1
    page = request.args.get('page', 1, type=int)

    # --- Sorting Logic ---
    # Get sorting parameters from the URL
    sort_by = request.args.get('sort_by', default_sort_by)
    sort_direction = request.args.get('sort_direction', default_sort_direction)

    # Validate the sort_by parameter
    # Ensure sort_by is a valid column
    if sort_by not in valid_sort_columns:
        sort_by = default_sort_by # Default to the specified default if invalid column
    # Ensure sort_direction is valid
    if sort_direction not in ['asc', 'desc']:
        sort_direction = default_sort_direction # Default to 'asc' if invalid

    # Get the SQLAlchemy model attribute to sort by
    sort_column_attribute = valid_sort_columns[sort_by]

    # Apply the sorting direction and handle case-insensitivity for string columns
    if isinstance(sort_column_attribute.type, String):
        # For string columns, use db.func.lower() for case-insensitive sorting
        if sort_direction == 'desc':
            query = query.order_by(db.func.lower(sort_column_attribute).desc())
        else: # Default to ascending for 'asc' or any other value
            query = query.order_by(db.func.lower(sort_column_attribute).asc())
    else:
        # For non-string columns (e.g., Integer, DateTime), sort directly
        if sort_direction == 'desc':
            query = query.order_by(sort_column_attribute.desc())
        else: # Default to ascending
            query = query.order_by(sort_column_attribute.asc())

    # --- End Sorting Logic ---

    # Apply pagination to the sorted query
    # error_out=False means if the page number is invalid, it returns an empty page
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return pagination, sort_by, sort_direction

# No other functions needed for now
