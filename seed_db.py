from app import app, db
from models import Role, User
from werkzeug.security import generate_password_hash

def seed_initial_data():
    with app.app_context():
        print("Starting database seeding...")

        db.create_all()
        print("Database tables checked/created.")

        roles_to_create = ['Admin', 'User', 'Moderator', 'System', 'Senior', 'Seller']

        for role_name in roles_to_create:
            if not Role.query.filter_by(name=role_name).first():
                db.session.add(Role(name=role_name))
                print(f"Role '{role_name}' created.")
            else:
                print(f"Role '{role_name}' already exists.")
        db.session.commit()

        admin_mobile = '09123456789'
        admin_password = 'adminpass'
        if not User.query.filter_by(mobile_number=admin_mobile).first():
            user = User(mobile_number=admin_mobile, password_hash=generate_password_hash(admin_password))
            db.session.add(user)
            db.session.commit()

            admin_role = Role.query.filter_by(name='Admin').first()
            if admin_role:
                user.roles.append(admin_role)
                db.session.commit()
                print(f"Admin user created: {admin_mobile} / {admin_password}")
            else:
                print("Warning: Admin role not found when trying to assign to user.")
        else:
            print(f"Admin user '{admin_mobile}' already exists.")

        print("Database seeding complete.")

if __name__ == '__main__':
    seed_initial_data()