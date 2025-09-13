# Utility to create default admin user if not present
from backend.models.table_models import User, db

def create_admin(app):
    with app.app_context():
        admin_email = "admin@gmail.com"
        admin_password = "admin123"

        # Check if admin already exists
        existing_admin = User.query.filter_by(email = admin_email).first()

        if not existing_admin:
            # Create new admin user
            admin = User(
                email = admin_email,
                full_name = "Admin",
                address = "Admin Office",
                pincode = "123123",
                role = "admin"
            )

            # Hash and store admin password
            admin.hash_password(admin_password)

            # Add admin to database
            db.session.add(admin)
            db.session.commit()
            print("Admin created")
        else:
            print("Admin already exists")
