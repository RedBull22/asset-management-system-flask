# Asset Management System

## Project Overview

The Asset Management System is a web-based application designed to provide **organizations** with a streamlined and secure solution for tracking their tangible assets. It aims to replace inefficient manual methods by offering a centralized platform for managing users, asset categories, individual assets, and their assignment to personnel. The system features robust authentication and role-based access control, ensuring data integrity and appropriate user permissions.

## Key Features

*   **User Management:** Secure registration, login, and logout functionalities.
*   **Role-Based Access Control (RBAC):** Differentiated permissions for 'Admin' and 'Regular' users.
    *   **Admin Users:** Full CRUD (Create, Read, Update, Delete) access to all entities (Users, Asset Types, Assets, Assignments).
    *   **Regular Users:** Read-only access to User and Asset Type lists, with CRUD access to Assets and Assignments.
*   **Asset Type Management:** **Categorize** assets (e.g., Laptops, Monitors).
*   **Asset Tracking:** Manage individual assets by name, serial number, and type.
*   **Assignment Management:** Assign assets to users and track assignment dates.
*   **Data Integrity:** Implemented checks to prevent deletion of linked records (e.g., cannot delete an Asset Type with associated Assets).
*   **Enhanced User Interface:** Includes pagination and dynamic sorting for efficient list view management.
*   **Robust Forms:** Utilizes Flask-WTF for form handling, validation, and CSRF protection.
*   **Secure Passwords:** User passwords are securely hashed using Bcrypt.

## Technologies Used

The application is built using the following core technologies:

*   **Backend:** Python 3.9+ with Flask web framework
*   **Database:** SQLAlchemy (ORM) with SQLite for local development (PostgreSQL for production deployment)
*   **Authentication:** Flask-Login, Flask-Bcrypt
*   **Forms:** Flask-WTF, WTForms, email-validator
*   **Web Server (Production):** Gunicorn
*   **Environment Variables:** python-dotenv

## Prerequisites

Before running the application, ensure you have the following installed on your system:

*   **Python 3.9+** (or a later version)
*   **Git** (for cloning the repository)

## Local Setup Instructions

Follow these steps to get the Asset Management System up and running on your local machine:

### 1. Clone the Repository

Open your terminal or command prompt and clone the project repository:

```bash
https://github.com/RedBull22/asset-management-system-flask.git
cd asset-management-system-flask

2. Virtual Environment Setup

python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

3. Install Dependencies
pip install -r requirements.txt

4. Confifigure Environment Variables 
touch .env
SECRET_KEY='your_strong_random_secret_key_here'
DEBUG='True'
DATABASE_URL='sqlite:///site.db' # Use SQLite for local development

5. Setup the database
python
>>> from app import app, db, create_sample_data
>>> with app.app_context():
...     db.create_all()
...     create_sample_data()
...
>>> exit()

The sample admin user credentials are:
Email: admin@example.com
Password: admin_password

6. Run the application 
flask run

7. Deployment
Live application url: RedBull25.pythonanywhere.com
