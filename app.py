# app.py
from flask import Flask, session, redirect, url_for, request, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Import db and migrate from your new extensions file
from extensions import db, migrate

# Import your models *after* db is defined in extensions.py
from models import * # Import all your models here

app = Flask(__name__)

# --- Flask Configuration ---
app.config['SECRET_KEY'] = 'your_super_secret_and_long_key_here_replace_this_in_production'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5432/car_ads_db'

# --- Initialize Extensions with the app ---
# Now initialize db and migrate with the app
db.init_app(app)
migrate.init_app(app, db)


# --- Helper functions for authentication and authorization ---
def login_required(f):
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

            request.current_user = user

            if not request.current_user.has_roles(*roles):
                flash('You do not have the required permissions.', 'error')
                return abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return wrapper


# --- Flask Routes ---
@app.route('/login_api')
def login_api():
    return 'This is the login API endpoint. Please implement your login logic here.'


@app.route('/')
def home_page():
    return 'Welcome to Car Ads System!'


@app.route('/admin_dashboard')
@login_required
@roles_required('Admin')
def admin_dashboard():
    return f'Welcome, Admin {request.current_user.mobile_number}!'


# --- Run the application ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        roles_to_create = ['Admin', 'User', 'Moderator']
        for role_name in roles_to_create:
            if not Role.query.filter_by(name=role_name).first():
                db.session.add(Role(name=role_name))
        db.session.commit()

        if not User.query.filter_by(mobile_number='09123456789').first():
            user = User(mobile_number='09123456789', password_hash=generate_password_hash('adminpass'))
            db.session.add(user)
            db.session.commit()
            admin_role = Role.query.filter_by(name='Admin').first()
            if admin_role:
                user.roles.append(admin_role)
                db.session.commit()
                print("Admin user created: 09123456789 / adminpass")

    app.run(debug=True)