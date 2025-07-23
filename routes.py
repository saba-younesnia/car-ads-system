from flask import jsonify, request, abort
# IMPORT app, db, login_required, roles_required from app.py
# This assumes app.py is imported first or app is globally available (which it is via the from routes import * in app.py)
from app import app, db, login_required, roles_required # ADD login_required, roles_required here
from models import User, Role, Car, Advertisement, PriceHistory, OwnershipHistory, CarImage, Transaction
from werkzeug.security import generate_password_hash # ADD THIS IMPORT (for register_user_api)
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_ # برای جستجوی پیشرفته

# --- توابع کمکی برای سریالایز کردن مدل‌ها به دیکشنری ---
def serialize_car(car):
    return {
        'id': car.id,
        'make': car.make,
        'model': car.model,
        'year': car.year,
        'color': car.color,
        'status': car.status
    }

def serialize_advertisement(ad):
    return {
        'id': ad.id,
        'title': ad.title,
        'description': ad.description,
        'price': str(ad.price),
        'status': ad.status,
        'created_at': ad.created_at.isoformat(),
        'car_id': ad.car_id,
        'user_id': ad.user_id,
        'car_details': serialize_car(ad.car_details) if ad.car_details else None,
        'publisher_mobile': ad.publisher.mobile_number if ad.publisher else None
    }

# --- نقاط پایانی API برای User (ثبت نام) ---
@app.route('/api/register', methods=['POST']) # Added method
def register_user_api():
    data = request.get_json()
    if not data or 'mobile_number' not in data or 'password' not in data:
        abort(400, description="Mobile number and password are required.")

    mobile_number = data['mobile_number']
    password = data['password']

    if User.query.filter_by(mobile_number=mobile_number).first():
        abort(409, description="Mobile number already registered.")

    try:
        new_user = User(mobile_number=mobile_number, password_hash=generate_password_hash(password)) # Fixed password_hash and used generate_password_hash
        db.session.add(new_user)
        db.session.commit() # Commit to get user ID before assigning roles

        # Assign 'User' role to new registrations
        user_role = Role.query.filter_by(name='User').first() # Changed from 'System' to 'User'
        if user_role:
            new_user.roles.append(user_role)
            db.session.commit()
        else:
            print("Warning: 'User' role not found. Please ensure roles are created.")

        return jsonify({'message': 'User registered successfully', 'user_id': new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Registration failed: {e}")

# --- نقاط پایانی API برای User (مدیریت توسط ادمین/ارشد) ---
@app.route('/api/users', methods=['GET']) # Added method
@login_required
@roles_required('Admin', 'Senior') # Specified roles
def get_all_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'mobile_number': u.mobile_number, 'active': u.active, 'roles': [r.name for r in u.roles]} for u in users])

@app.route('/api/users/<int:user_id>/deactivate', methods=['PUT']) # Added method
@login_required
@roles_required('Admin', 'Senior') # Specified roles
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == request.current_user.id: # Used request.current_user
        abort(400, description="You cannot deactivate your own account.")
    try:
        user.active = False
        db.session.commit()
        return jsonify({'message': f'User {user_id} deactivated successfully'})
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"An error occurred: {e}")

# --- نقاط پایانی API برای Car ---
@app.route('/api/cars', methods=['GET']) # Added method
def get_all_cars():
    cars = Car.query.all()
    return jsonify([serialize_car(car) for car in cars])

@app.route('/api/cars/<int:car_id>', methods=['GET']) # Added method
def get_car_by_id(car_id):
    car = Car.query.get_or_404(car_id)
    return jsonify(serialize_car(car))

# --- نقاط پایانی API برای Advertisement ---
@app.route('/api/advertisements', methods=['GET']) # Added method (for fetching all ads)
def get_all_advertisements():
    advertisements = Advertisement.query.all()
    return jsonify([serialize_advertisement(ad) for ad in advertisements])

@app.route('/api/advertisements/<int:ad_id>', methods=['GET']) # Added method (for fetching single ad)
def get_advertisement_by_id(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    return jsonify(serialize_advertisement(ad))

@app.route('/api/advertisements', methods=['POST']) # Added method (for creating ads)
@login_required
@roles_required('System', 'Admin', 'Senior') # Specified roles
def create_advertisement():
    data = request.get_json()
    if not data:
        abort(400, description="No JSON data provided")

    try:
        new_car = Car(
            make=data['car']['make'],
            model=data['car']['model'],
            year=data['car']['year'],
            color=data['car']['color'],
            status=data['car'].get('status', 'used')
        )
        db.session.add(new_car)
        db.session.flush() # Use flush to get car.id before commit

        new_ad = Advertisement(
            title=data['title'],
            description=data['description'],
            price=data['price'],
            car_id=new_car.id,
            user_id=request.current_user.id # Used request.current_user
        )
        db.session.add(new_ad)
        db.session.commit()
        return jsonify(serialize_advertisement(new_ad)), 201
    except IntegrityError:
        db.session.rollback()
        abort(409, description="Car or Advertisement already exists or invalid data.")
    except KeyError as e:
        db.session.rollback()
        abort(400, description=f"Missing data: {e}")
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"An error occurred: {e}")

@app.route('/api/advertisements/<int:ad_id>', methods=['PUT']) # Added method (for updating ads)
@login_required
@roles_required('System', 'Admin', 'Senior') # Specified roles
def update_advertisement(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    data = request.get_json()

    # Object-level permission check: only owner or Admin/Senior user can edit
    if not (request.current_user.has_roles('Admin', 'Senior') or request.current_user.id == ad.user_id):
        abort(403, description="You do not have permission to update this advertisement.")

    try:
        ad.title = data.get('title', ad.title)
        ad.description = data.get('description', ad.description)
        ad.price = data.get('price', ad.price)
        ad.status = data.get('status', ad.status)

        if 'car' in data and ad.car_details:
            car_data = data['car']
            ad.car_details.make = car_data.get('make', ad.car_details.make)
            ad.car_details.model = car_data.get('model', ad.car_details.model)
            ad.car_details.year = car_data.get('year', ad.car_details.year)
            ad.car_details.color = car_data.get('color', ad.car_details.color)
            ad.car_details.status = car_data.get('status', ad.car_details.status)

        db.session.commit()
        return jsonify(serialize_advertisement(ad))
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"An error occurred: {e}")

@app.route('/api/advertisements/<int:ad_id>', methods=['DELETE']) # Added method (for deleting ads)
@login_required
@roles_required('System', 'Admin', 'Senior') # Specified roles
def delete_advertisement(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)

    # Object-level permission check: only owner or Admin/Senior user can delete
    if not (request.current_user.has_roles('Admin', 'Senior') or request.current_user.id == ad.user_id):
        abort(403, description="You do not have permission to delete this advertisement.")

    try:
        db.session.delete(ad)
        db.session.commit()
        return jsonify({'message': 'Advertisement deleted successfully'}), 204
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"An error occurred: {e}")

# --- نقاط پایانی API برای Transaction (شروع معامله) ---
@app.route('/api/transactions', methods=['POST']) # Added method
@login_required
@roles_required('User') # Specify roles: User can initiate transactions
def create_transaction():
    data = request.get_json()
    if not data or 'car_id' not in data or 'agreed_price' not in data:
        abort(400, description="Car ID and agreed price are required.")

    car = Car.query.get_or_404(data['car_id'])
    advertisement = Advertisement.query.filter_by(car_id=car.id).first()
    if not advertisement:
        abort(404, description="Advertisement for this car not found.")

    if request.current_user.id == advertisement.user_id: # Used request.current_user
        abort(400, description="You cannot buy your own advertisement.")

    # بررسی اینکه آیا این خودرو قبلاً در یک معامله فعال است
    if Transaction.query.filter_by(car_id=car.id, status='pending').first():
        abort(409, description="This car is already part of a pending transaction.")

    try:
        new_transaction = Transaction(
            car_id=car.id,
            buyer_id=request.current_user.id, # Used request.current_user
            seller_id=advertisement.user_id,
            agreed_price=data['agreed_price'],
            status='pending'
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({'message': 'Transaction initiated successfully', 'transaction_id': new_transaction.id}), 201
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Failed to initiate transaction: {e}")

# --- نقاط پایانی API برای Transaction (به‌روزرسانی وضعیت معامله) ---
@app.route('/api/transactions/<int:transaction_id>/status', methods=['PUT']) # Added method
@login_required
@roles_required('Seller', 'Admin', 'Senior') # Specify roles: Seller, Admin, Senior
def update_transaction_status(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['accepted', 'rejected', 'completed']:
        abort(400, description="Invalid status. Must be 'accepted', 'rejected', or 'completed'.")

    # فقط فروشنده، ادمین یا کاربر ارشد می‌تواند وضعیت معامله را تغییر دهد
    if not (request.current_user.has_roles('Admin', 'Senior') or request.current_user.id == transaction.seller_id): # Used request.current_user
        abort(403, description="You do not have permission to update this transaction's status.")

    try:
        transaction.status = new_status
        db.session.commit()
        return jsonify({'message': f'Transaction {transaction_id} status updated to {new_status}'})
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Failed to update transaction status: {e}")

# --- نقاط پایانی API برای Transaction (مشاهده معاملات) ---
@app.route('/api/transactions', methods=['GET']) # Added method
@login_required
@roles_required('User', 'Admin', 'Senior') # Specified roles: All can view their own, Admin/Senior all
def get_user_transactions():
    # کاربران سیستم فقط معاملات خودشان را می‌بینند، ادمین/ارشد همه را
    if request.current_user.has_roles('Admin', 'Senior'): # Used request.current_user
        transactions = Transaction.query.all()
    else: # User
        transactions = Transaction.query.filter(
            (Transaction.buyer_id == request.current_user.id) | # Used request.current_user
            (Transaction.seller_id == request.current_user.id) # Used request.current_user
        ).all()

    serialized_transactions = [] # FIXED: Initialize as empty list
    for t in transactions:
        serialized_transactions.append({
            'id': t.id,
            'car_id': t.car_id,
            'buyer_id': t.buyer_id,
            'seller_id': t.seller_id,
            'status': t.status,
            'agreed_price': str(t.agreed_price),
            'transaction_date': t.transaction_date.isoformat(),
            'car_make': t.car_transaction.make if t.car_transaction else None,
            'buyer_mobile': t.buyer.mobile_number if t.buyer else None,
            'seller_mobile': t.seller.mobile_number if t.seller else None,
        })
    return jsonify(serialized_transactions)