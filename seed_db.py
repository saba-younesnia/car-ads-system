# seed_db.py
# This file is for seeding initial data into the database.
# Run it using: python seed_db.py

from app import app, db # This import should now work without circular dependencies
from models import Role, User # Import your models
from werkzeug.security import generate_password_hash # For hashing passwords

def seed_initial_data():
    """
    Creates initial roles and an admin user in the database.
    """
    with app.app_context(): # Ensure we are within the Flask application context
        print("Starting database seeding...")

        # Create all tables if they don't exist
        db.create_all()
        print("Database tables checked/created.")

        # Define roles to be created
        roles_to_create = ['Admin', 'User', 'Moderator', 'System', 'Senior', 'Seller']

        for role_name in roles_to_create:
            if not Role.query.filter_by(name=role_name).first():
                db.session.add(Role(name=role_name))
                print(f"Role '{role_name}' created.")
            else:
                print(f"Role '{role_name}' already exists.")
        db.session.commit()

        # Create an admin user if it doesn't exist
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