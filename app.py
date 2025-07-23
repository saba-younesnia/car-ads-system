from flask import Flask, session, redirect, url_for, request, flash, abort, jsonify, render_template
from werkzeug.security import check_password_hash
import os
from flask_cors import CORS

from extensions import db, migrate
from models import User
from routes import bp as api_bp
from utils import login_required, roles_required

app = Flask(__name__)

CORS(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_super_secret_and_long_key_here_replace_this_in_production')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
    'postgresql://user:password@localhost:5432/car_ads_db'
)

db.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(api_bp)

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/login_api', methods=['POST'])
def login_api():
    data = request.get_json()
    mobile_number = data.get('mobile_number')
    password = data.get('password')

    user = User.query.filter_by(mobile_number=mobile_number).first()
    if user and user.is_active and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['user_mobile'] = user.mobile_number
        return jsonify({'message': 'Login successful', 'user_id': user.id, 'mobile_number': user.mobile_number}), 200
    return jsonify({'message': 'Invalid credentials or inactive account'}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('user_mobile', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/admin_dashboard')
@login_required
@roles_required('Admin')
def admin_dashboard():
    return f'Welcome, Admin {request.current_user.mobile_number}!'

if __name__ == '__main__':
    app.run(debug=True)