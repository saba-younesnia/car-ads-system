from extensions import db
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    mobile_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), nullable=False, default=True)
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))

    @property
    def is_authenticated(self):
        return self.active

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def has_roles(self, *requirements):
        user_roles = {role.name for role in self.roles}
        for requirement in requirements:
            if requirement in user_roles:
                return True
        return False

    transactions_as_buyer = relationship('Transaction', foreign_keys='[Transaction.buyer_id]', backref='buyer', lazy=True)
    transactions_as_seller = relationship('Transaction', foreign_keys='[Transaction.seller_id]', backref='seller', lazy=True)

    advertisements = relationship('Advertisement', backref='publisher', lazy=True, cascade="all, delete-orphan")
    ownership_records = relationship('OwnershipHistory', backref='owner', lazy=True, cascade="all, delete-orphan")


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))
    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='_user_role_uc'),)

class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(100), nullable=False, index=True)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(50), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default='used', index=True)

    advertisement = relationship('Advertisement', backref='car_details', uselist=False, cascade="all, delete-orphan")
    price_history = relationship('PriceHistory', backref='car', lazy=True, cascade="all, delete-orphan")
    ownership_history = relationship('OwnershipHistory', backref='car', lazy=True, cascade="all, delete-orphan")
    images = relationship('CarImage', backref='car', lazy=True, cascade="all, delete-orphan")
    transaction = relationship('Transaction', backref='car_transaction', uselist=False)

class Advertisement(db.Model):
    __tablename__ = 'advertisements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(15, 2), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    car_id = db.Column(db.Integer, db.ForeignKey('cars.id', ondelete='CASCADE'), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))

class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Numeric(15, 2), nullable=False)
    change_date = db.Column(db.DateTime, default=datetime.utcnow)

class OwnershipHistory(db.Model):
    __tablename__ = 'ownership_history'
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id', ondelete='CASCADE'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)

class CarImage(db.Model):
    __tablename__ = 'car_images'
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id', ondelete='RESTRICT'), unique=True, nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    agreed_price = db.Column(db.Numeric(15, 2), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)