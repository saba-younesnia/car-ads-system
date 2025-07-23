from flask import Blueprint, jsonify, request, abort
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from extensions import db
from models import User, Role, Car, Advertisement, PriceHistory, OwnershipHistory, CarImage, Transaction

from utils import login_required, roles_required

bp = Blueprint('api', __name__, url_prefix='/api')

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

@bp.route('/register', methods=['POST'])
def register_user_api():
    data = request.get_json()
    if not data or 'mobile_number' not in data or 'password' not in data:
        abort(400, description="Mobile number and password are required.")

    mobile_number = data['mobile_number']
    password = data['password']

    if User.query.filter_by(mobile_number=mobile_number).first():
        abort(409, description="Mobile number already registered.")

    try:
        new_user = User(mobile_number=mobile_number, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        user_role = Role.query.filter_by(name='User').first()
        if user_role:
            new_user.roles.append(user_role)
            db.session.commit()
        else:
            print("Warning: 'User' role not found. Please ensure roles are created.")

        return jsonify({'message': 'User registered successfully', 'user_id': new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Registration failed: {e}")

@bp.route('/users', methods=['GET'])
@login_required
@roles_required('Admin', 'Senior')
def get_all_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'mobile_number': u.mobile_number, 'active': u.active, 'roles': [r.name for r in u.roles]} for u in users])

@bp.route('/users/<int:user_id>/deactivate', methods=['PUT'])
@login_required
@roles_required('Admin', 'Senior')
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == request.current_user.id:
        abort(400, description="You cannot deactivate your own account.")
    try:
        user.active = False
        db.session.commit()
        return jsonify({'message': f'User {user_id} deactivated successfully'})
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"An error occurred: {e}")

@bp.route('/cars', methods=['GET'])
def get_all_cars():
    cars = Car.query.all()
    return jsonify([serialize_car(car) for car in cars])

@bp.route('/cars/<int:car_id>', methods=['GET'])
def get_car_by_id(car_id):
    car = Car.query.get_or_404(car_id)
    return jsonify(serialize_car(car))

@bp.route('/advertisements', methods=['GET'])
def get_all_advertisements():
    advertisements = Advertisement.query.all()
    return jsonify([serialize_advertisement(ad) for ad in advertisements])

@bp.route('/advertisements/<int:ad_id>', methods=['GET'])
def get_advertisement_by_id(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    return jsonify(serialize_advertisement(ad))

@bp.route('/advertisements', methods=['POST'])
@login_required
@roles_required('System', 'Admin', 'Senior', 'User')
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
        db.session.flush()

        new_ad = Advertisement(
            title=data['title'],
            description=data['description'],
            price=data['price'],
            car_id=new_car.id,
            user_id=request.current_user.id
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

@bp.route('/advertisements/<int:ad_id>', methods=['PUT'])
@login_required
@roles_required('System', 'Admin', 'Senior', 'User')
def update_advertisement(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    data = request.get_json()

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

@bp.route('/advertisements/<int:ad_id>', methods=['DELETE'])
@login_required
@roles_required('System', 'Admin', 'Senior', 'User')
def delete_advertisement(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)

    if not (request.current_user.has_roles('Admin', 'Senior') or request.current_user.id == ad.user_id):
        abort(403, description="You do not have permission to delete this advertisement.")

    try:
        db.session.delete(ad)
        db.session.commit()
        return jsonify({'message': 'Advertisement deleted successfully'}), 204
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"An error occurred: {e}")

@bp.route('/transactions', methods=['POST'])
@login_required
@roles_required('User')
def create_transaction():
    data = request.get_json()
    if not data or 'car_id' not in data or 'agreed_price' not in data:
        abort(400, description="Car ID and agreed price are required.")

    car = Car.query.get_or_404(data['car_id'])
    advertisement = Advertisement.query.filter_by(car_id=car.id).first()
    if not advertisement:
        abort(404, description="Advertisement for this car not found.")

    if request.current_user.id == advertisement.user_id:
        abort(400, description="You cannot buy your own advertisement.")

    if Transaction.query.filter_by(car_id=car.id, status='pending').first():
        abort(409, description="This car is already part of a pending transaction.")

    try:
        new_transaction = Transaction(
            car_id=car.id,
            buyer_id=request.current_user.id,
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

@bp.route('/transactions/<int:transaction_id>/status', methods=['PUT'])
@login_required
@roles_required('Seller', 'Admin', 'Senior')
def update_transaction_status(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['accepted', 'rejected', 'completed']:
        abort(400, description="Invalid status. Must be 'accepted', 'rejected', or 'completed'.")

    if not (request.current_user.has_roles('Admin', 'Senior') or request.current_user.id == transaction.seller_id):
        abort(403, description="You do not have permission to update this transaction's status.")

    try:
        transaction.status = new_status
        db.session.commit()
        return jsonify({'message': f'Transaction {transaction_id} status updated to {new_status}'})
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Failed to update transaction status: {e}")

@bp.route('/transactions', methods=['GET'])
@login_required
@roles_required('User', 'Admin', 'Senior', 'Seller')
def get_user_transactions():
    if request.current_user.has_roles('Admin', 'Senior'):
        transactions = Transaction.query.all()
    else:
        transactions = Transaction.query.filter(
            (Transaction.buyer_id == request.current_user.id) |
            (Transaction.seller_id == request.current_user.id)
        ).all()

    serialized_transactions = []
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

@bp.route('/cars/<int:car_id>/related', methods=['GET'])
def get_related_cars(car_id):
    main_car = Car.query.get_or_404(car_id)
    related_cars = Car.query.filter(
        Car.make == main_car.make,
        Car.id != main_car.id
    ).limit(5).all()

    return jsonify([serialize_car(car) for car in related_cars])

@bp.route('/search/cars', methods=['GET'])
def advanced_car_search():
    query = Car.query.join(Advertisement)

    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    brand = request.args.get('brand')
    color = request.args.get('color')
    status = request.args.get('status')

    filters = []

    if min_price is not None:
        filters.append(Advertisement.price >= min_price)
    if max_price is not None:
        filters.append(Advertisement.price <= max_price)
    if brand:
        filters.append(Car.make.ilike(f'%{brand}%'))
    if color:
        filters.append(Car.color.ilike(f'%{color}%'))
    if status:
        filters.append(Car.status == status)

    if filters:
        query = query.filter(and_(*filters))

    search_results = query.all()
    return jsonify([serialize_car(car) for car in search_results])