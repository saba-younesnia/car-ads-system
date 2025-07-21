from flask import Flask, session, redirect, url_for, request, flash, abort  # abort را اضافه کردیم
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps  # برای دکوراتورها اضافه شد

app = Flask(__name__)

# --- پیکربندی Flask ---
# اصلاح نحوه پیکربندی: از دیکشنری برای تنظیمات استفاده کنید
app.config['SECRET_KEY'] = 'your_super_secret_and_long_key_here_replace_this_in_production'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # برای جلوگیری از هشدارها
# app.config['SESSION_PERMANENT'] = True # این خط برای فعال کردن جلسات دائمی است، اگر نیاز دارید فعال کنید

# پیکربندی اتصال به پایگاه داده PostgreSQL
# توجه: 'db' نام سرویس پایگاه داده در Docker Compose خواهد بود.
# برای تست اولیه بدون Docker، می توانید از 'localhost' استفاده کنید.
# این مقدار در فاز 6 برای Docker تغییر خواهد کرد.
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5432/car_ads_db'

# --- مقداردهی اولیه افزونه‌ها ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# --- تعریف مدل‌های پایگاه داده (به زودی در models.py منتقل می‌شود) ---
# این مدل‌ها موقتاً اینجا هستند و در مرحله بعد به models.py منتقل می‌شوند.
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
        # در Flask-Login، این ویژگی نشان می‌دهد که کاربر احراز هویت شده است.
        # در اینجا، ما آن را به فعال بودن کاربر مرتبط می‌کنیم.
        return self.active

    @property
    def is_active(self):
        # در Flask-Login، این ویژگی نشان می‌دهد که کاربر فعال است و می‌تواند وارد شود.
        return self.active

    @property
    def is_anonymous(self):
        # در Flask-Login، این ویژگی نشان می‌دهد که کاربر ناشناس است.
        return False

    def get_id(self):
        # در Flask-Login، این متد شناسه منحصر به فرد کاربر را برمی‌گرداند.
        return str(self.id)

    def has_roles(self, *requirements):
        user_roles = {role.name for role in self.roles}
        for requirement in requirements:
            if requirement in user_roles:
                return True
        return False


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id', name='_user_role_uc'),)


# --- توابع کمکی برای احراز هویت و مجوز (اصلاح شده) ---
def login_required(f):
    @wraps(f)  # برای حفظ متادیتای تابع اصلی
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to access this page.', 'error')
            return redirect(url_for('login_api'))  # یا یک صفحه ورود

        user = User.query.get(session['user_id'])
        if not user or not user.is_active:
            session.pop('user_id', None)
            flash('Your session has expired or account is inactive.', 'error')
            return redirect(url_for('login_api'))

        request.current_user = user  # کاربر فعلی را به شیء درخواست اضافه می‌کنیم
        return f(*args, **kwargs)

    return decorated_function


def roles_required(*roles):
    def wrapper(f):
        @wraps(f)  # برای حفظ متادیتای تابع اصلی
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('You need to be logged in to access this page.', 'error')
                return redirect(url_for('login_api'))

            user = User.query.get(session['user_id'])
            if not user or not user.is_active:
                session.pop('user_id', None)
                flash('Your session has expired or account is inactive.', 'error')
                return redirect(url_for('login_api'))

            request.current_user = user  # کاربر فعلی را به شیء درخواست اضافه می‌کنیم

            if not request.current_user.has_roles(*roles):
                flash('You do not have the required permissions.', 'error')
                return abort(403)  # Forbidden
            return f(*args, **kwargs)

        return decorated_function

    return wrapper


# --- مسیرهای Flask (برای تست اولیه) ---
# یک مسیر فرضی برای login_api اضافه می‌کنیم تا redirect کار کند
@app.route('/login_api')
def login_api():
    return 'This is the login API endpoint. Please implement your login logic here.'


@app.route('/')
def home_page():
    return 'Welcome to Car Ads System!'


@app.route('/admin_dashboard')
@login_required
@roles_required('Admin')  # مثال استفاده از دکوراتورها
def admin_dashboard():
    return f'Welcome, Admin {request.current_user.mobile_number}!'


# --- اجرای برنامه ---
if __name__ == '__main__':
    # این خطوط را برای ایجاد جداول در پایگاه داده در اولین اجرا اضافه کنید
    # توجه: در محیط واقعی از flask db upgrade استفاده می‌کنیم
    with app.app_context():
        db.create_all()  # این خط بعداً حذف می‌شود و با مهاجرت جایگزین می‌شود
        # ایجاد نقش‌های پیش‌فرض اگر وجود ندارند
        roles_to_create = ['Admin', 'User', 'Moderator']  # لیست نقش‌ها را اضافه کردیم
        for role_name in roles_to_create:
            if not Role.query.filter_by(name=role_name).first():
                db.session.add(Role(name=role_name))
        db.session.commit()

        # ایجاد یک کاربر ادمین اولیه برای تست
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
