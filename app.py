# app.py
from flask import Flask, session, redirect, url_for, request, flash, abort, jsonify, render_template # Added jsonify, render_template
from werkzeug.security import check_password_hash # Only check_password_hash is needed here for login_api

# Import db and migrate from your new extensions file
from extensions import db, migrate

# Import your models *after* db is defined in extensions.py
from models import User # Only import User model here if needed for app.py specific routes (like login/logout)

# --- IMPORT YOUR BLUEPRINT HERE ---
from routes import bp as api_bp # Import the blueprint and give it an alias
# ----------------------------------

# --- Import your decorators from utils.py ---
from utils import login_required, roles_required # Import from the new utils file
# --------------------------------------------

app = Flask(__name__)

# --- Flask Configuration ---
app.config['SECRET_KEY'] = 'your_super_secret_and_long_key_here_replace_this_in_production'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5432/car_ads_db'

# --- Initialize Extensions with the app ---
db.init_app(app)
migrate.init_app(app, db)

# --- Register Blueprints ---
app.register_blueprint(api_bp) # Register the blueprint
# ---------------------------

# --- Flask Routes (for app.py specific routes, e.g., non-API or top-level) ---

@app.route('/')
def home_page():
    """
    Renders the main HTML page for the UI.
    """
    return render_template('index.html')

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

@app.route('/admin_dashboard')
@login_required
@roles_required('Admin')
def admin_dashboard():
    # Example usage of current_user and has_roles
    return f'Welcome, Admin {request.current_user.mobile_number}!'

# --- Run the application ---
if __name__ == '__main__':
    app.run(debug=True)