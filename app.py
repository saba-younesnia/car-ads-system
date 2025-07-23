# app.py
from flask import Flask, session, redirect, url_for, request, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash # Changed from UserManager
from functools import wraps

# Import db and migrate from your new extensions file
from extensions import db, migrate

# Import your models *after* db is defined in extensions.py
from models import * # Import all your models here

# --- ADD THIS LINE ---
from routes import * # This imports all routes and registers them with 'app'
# ---------------------

app = Flask(__name__)

# --- Flask Configuration ---
app.config['SECRET_KEY'] = 'your_super_secret_and_long_key_here_replace_this_in_production'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5432/car_ads_db'

# --- Initialize Extensions with the app ---
db.init_app(app)
migrate.init_app(app, db)


# --- Helper functions for authentication and authorization (Keep these here for app.py specific routes) ---
# Note: For routes.py, we will assume these are either imported or
# that routes.py is processed in a way that 'app' is already available.
# The previous solution for routes.py relied on request.current_user which is set by these decorators.
# If you get NameErrors in routes.py, you might need to 'from app import login_required, roles_required' in routes.py
# but be careful with circular imports if routes.py also imports 'app'.
# A better long-term solution would be Flask Blueprints.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to access this page.', 'error')
            return redirect(url_for('login_api')) # Ensure 'login_api' route exists

        user = User.query.get(session.get('user_id'))
        if not user or not user.is_active:
            session.pop('user_id', None)
            flash('Your session has expired or account is inactive.', 'error')
            return redirect(url_for('login_api'))

        # Attach the current user to the request object for easy access in routes
        request.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('You need to be logged in to access this page.', 'error')
                return redirect(url_for('login_api'))

            user = User.query.get(session.get('user_id'))
            if not user or not user.is_active:
                session.pop('user_id', None)
                flash('Your session has expired or account is inactive.', 'error')
                return redirect(url_for('login_api'))

            request.current_user = user # Ensure current_user is set for role checking

            # Check if current_user has any of the required roles
            if not request.current_user.has_roles(*roles):
                flash('You do not have the required permissions.', 'error')
                return abort(403) # Return 403 Forbidden

            return f(*args, **kwargs)

        return decorated_function

    return wrapper


# --- Flask Routes (for app.py specific routes) ---
# Example: Basic login route to set session (you'll expand this for actual login logic)
@app.route('/login_api', methods=['POST'])
def login_api():
    data = request.get_json()
    mobile_number = data.get('mobile_number')
    password = data.get('password')

    user = User.query.filter_by(mobile_number=mobile_number).first()
    if user and user.is_active and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
    return jsonify({'message': 'Invalid credentials or inactive account'}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/')
def home_page():
    return 'Welcome to Car Ads System!'


@app.route('/admin_dashboard')
@login_required
@roles_required('Admin')
def admin_dashboard():
    # Example usage of current_user and has_roles
    return f'Welcome, Admin {request.current_user.mobile_number}!'


# --- Run the application ---
if __name__ == '__main__':
    # Removed db.create_all() and initial role/user creation
    # This logic is now in seed_db.py
    app.run(debug=True)